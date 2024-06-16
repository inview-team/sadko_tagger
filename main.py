from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import uvicorn
from pipelines.video_pipeline import video_pipeline
from pipelines.text_pipeline import text_pipeline
from db.milvus import MilvusHelper
from config.config import DEFAULT_TABLE, SEACH_SERVICE_ADDRESS, RABBITMQ_QUEUE
from messaging.rmq import RabbitMQHelper, process_message
import threading

app = FastAPI()
milvus_client = MilvusHelper()
rabbitmq_helper = RabbitMQHelper()

class TagMessage(BaseModel):
    ID: str
    Url: str
    Description: str

class SearchRequest(BaseModel):
    search_text: str

@app.post("/video/process")
async def process_video(tag: TagMessage):
    try:
        vectors, words = video_pipeline(tag.ID, tag.Url, tag.Description)
        if not milvus_client.has_collection(DEFAULT_TABLE):
            milvus_client.create_collection(DEFAULT_TABLE)
            milvus_client.create_index(DEFAULT_TABLE)
        results = milvus_client.insert(DEFAULT_TABLE, vectors)
        vector_ids = [str(x) for x in results]
        async with httpx.AsyncClient() as client:
            response = await client.post(SEACH_SERVICE_ADDRESS, json={"words": words})
            search_response = response.json()

        return {"Milvus IDs": vector_ids, "Search Service Response": search_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/video/search")
async def search_videos(request: SearchRequest, top_k: int = 10):
    try:
        query_vector = text_pipeline(request.search_text)
        results = milvus_client.search_vectors(DEFAULT_TABLE, [query_vector], top_k)
        vector_ids = [str(x.id) for x in results[0]]
        return {"vector_ids": vector_ids}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def start_rabbitmq_consumer():
    rabbitmq_helper.declare_queue(RABBITMQ_QUEUE)
    rabbitmq_helper.consume_messages(RABBITMQ_QUEUE, process_message)

if __name__ == "__main__":
    threading.Thread(target=start_rabbitmq_consumer, daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=8841)
 