import os

############### Milvus Configuration ###############
MILVUS_HOST = os.getenv("MILVUS_HOST", "127.0.0.1")
MILVUS_PORT = int(os.getenv("MILVUS_PORT", "19530"))
VECTOR_DIMENSION = int(os.getenv("VECTOR_DIMENSION", "384"))
INDEX_FILE_SIZE = int(os.getenv("INDEX_FILE_SIZE", "1024"))
METRIC_TYPE = os.getenv("METRIC_TYPE", "L2")
DEFAULT_TABLE = os.getenv("DEFAULT_TABLE", "milvus_video_search")
TOP_K = int(os.getenv("TOP_K", "10"))

############### Data Path ###############
OUTPUT_PATH = os.getenv("OUTPUT_PATH", "/home/dilaks/lct/output")

############### RabbitMQ Configuration ###############
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "127.0.0.1")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "video_queue")
DLQ_ENABLED = bool(int(os.getenv("DLQ_ENABLED", "0")))
DLQ_QUEUE = os.getenv("DLQ_QUEUE", "dlq_queue")

############### Logging Configuration ###############
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "/var/log/myapp.log")

############### Number of log files ###############
LOGS_NUM = int(os.getenv("logs_num", "0"))

############### Service addresses ###############
SEARCH_SERVICE_ADDRESS = os.getenv("SEARCH_SERVICE_ADDRESS", "http://localhost:8076/")
INDEX_SERVICE_ADDRESS = os.getenv("INDEX_SERVICE_ADDRESS", "http://localhost:8076/")