import os
from elasticsearch import AsyncElasticsearch, Elasticsearch

ES_URL = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")

# Async client for FastAPI
async_es_client = AsyncElasticsearch(ES_URL)

# Sync client for Pika Consumer thread
sync_es_client = Elasticsearch(ES_URL)

async def init_indices():
    if not await async_es_client.indices.exists(index="issues"):
        await async_es_client.indices.create(
            index="issues",
            mappings={
                "properties": {
                    "id": {"type": "keyword"},
                    "title": {"type": "text"},
                    "description": {"type": "text"},
                    "project_id": {"type": "keyword"}
                }
            }
        )
    if not await async_es_client.indices.exists(index="comments"):
        await async_es_client.indices.create(
            index="comments",
            mappings={
                "properties": {
                    "id": {"type": "keyword"},
                    "issue_id": {"type": "keyword"},
                    "content": {"type": "text"}
                }
            }
        )
