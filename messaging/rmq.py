import json
import sys
import pika
from pika.exceptions import AMQPConnectionError
from logs.multiprocess import LOGGER
from config.config import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PASSWORD, DLQ_ENABLED, DLQ_QUEUE, DEFAULT_TABLE, RABBITMQ_QUEUE, SEACH_SERVICE_ADDRESS
from pipelines.video_pipeline import video_pipeline
from db.milvus import MilvusHelper
import httpx

class RabbitMQHelper:
    def __init__(self):
        try:
            self.connection_params = pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
                credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
            )
            self.connection = pika.BlockingConnection(self.connection_params)
            self.channel = self.connection.channel()
            LOGGER.debug(f"Successfully connected to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT}")
        except AMQPConnectionError as e:
            LOGGER.error(f"Failed to connect to RabbitMQ: {e}")
            sys.exit(1)

    def declare_queue(self, queue_name):
        self.channel.queue_declare(queue=queue_name)
        LOGGER.debug(f"Declared RabbitMQ queue: {queue_name}")

    def consume_messages(self, queue_name, callback):
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=self._wrap_callback(callback),
            auto_ack=False
        )
        LOGGER.debug(f"Started consuming messages from queue: {queue_name}")
        self.channel.start_consuming()

    def _wrap_callback(self, callback):
        def wrapped_callback(ch, method, properties, body):
            try:
                callback(body)
                ch.basic_ack(delivery_tag=method.delivery_tag)
                LOGGER.debug(f"Successfully processed message: {body}")
            except Exception as e:
                LOGGER.error(f"Failed to process message: {e}")
                self._handle_failure(ch, method, body)
        return wrapped_callback

    def _handle_failure(self, ch, method, body):
        if DLQ_ENABLED:
            self.channel.basic_publish(exchange='', routing_key=DLQ_QUEUE, body=body)
            LOGGER.debug(f"Message sent to DLQ: {body}")
        else:
            LOGGER.debug(f"Message discarded: {body}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def close_connection(self):
        if self.connection.is_open:
            self.connection.close()
            LOGGER.debug("Closed RabbitMQ connection")

def process_message(message):
    try:
        tag_message = json.loads(message)
        vectors, words = video_pipeline(tag_message["ID"], tag_message["Url"], tag_message["Description"])

        milvus_client = MilvusHelper()
        if not milvus_client.has_collection(DEFAULT_TABLE):
            milvus_client.create_collection(DEFAULT_TABLE)
            milvus_client.create_index(DEFAULT_TABLE)
        
        ids = milvus_client.insert(DEFAULT_TABLE, vectors)
        search_response = response.json()
        response = httpx.post(SEACH_SERVICE_ADDRESS, json={"words": words})
        LOGGER.info(f"Processed message, Milvus IDs: {ids}, Search Service Response: {search_response}")
    except Exception as e:
        LOGGER.error(f"Error processing message: {e}")


if __name__ == "__main__":
    rabbitmq_helper = RabbitMQHelper()
    rabbitmq_helper.declare_queue(RABBITMQ_QUEUE)
    rabbitmq_helper.consume_messages(RABBITMQ_QUEUE, process_message)