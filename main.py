from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import uvicorn
from pipelines.video_pipeline import video_pipeline
from pipelines.text_pipeline import text_pipeline
from db.milvus import MilvusHelper
from config.config import DEFAULT_TABLE, SEARCH_SERVICE_ADDRESS, RABBITMQ_QUEUE, INDEX_SERVICE_ADDRESS
from messaging.rmq import RabbitMQHelper, process_message
import threading

app = FastAPI()
milvus_client = MilvusHelper()
rabbitmq_helper = RabbitMQHelper()

class TagMessage(BaseModel):
    id: str
    url: str
    description: str

class SearchRequest(BaseModel):
    query: str

@app.post("/video/process", summary="Process Video", description="Processes a video by extracting vectors and words, storing them in Milvus, and updating search and index services.")
def process_video(tag: TagMessage):
    try:
        vectors, words = video_pipeline(tag.id, tag.url, tag.description)
        if not milvus_client.has_collection(DEFAULT_TABLE):
            milvus_client.create_collection(DEFAULT_TABLE)
        milvus_client.create_index(DEFAULT_TABLE)
        results = milvus_client.insert(DEFAULT_TABLE, vectors)
        vector_ids = [str(x) for x in results]
        search_response = httpx.post(f"{SEARCH_SERVICE_ADDRESS}/word/add", json={"words": words}, timeout=10.0)
        index_response = httpx.put(f"{INDEX_SERVICE_ADDRESS}/index/{tag.id}", json={"vectors": vector_ids}, timeout=10.0)
        return {"Milvus IDs": vector_ids, "Search Service Response Code": search_response.status_code, "Index Service Response Code": index_response.status_code }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/video/search", summary="Search Videos", description="Searches for videos based on a text query, returning the IDs of the most relevant video vectors.")
async def search_videos(request: SearchRequest, top_k: int = 10):
    try:
        query_vector = text_pipeline(request.query)
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
    uvicorn.run(app, host="0.0.0.0", port=8842)
