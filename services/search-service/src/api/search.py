from fastapi import APIRouter
from src.indexers.es_client import async_es_client

router = APIRouter()

@router.get("/")
async def search_all(q: str):
    """Full-text search across issues and comments."""
    response = await async_es_client.search(
        index="issues,comments",
        query={
            "multi_match": {
                "query": q,
                "fields": ["title", "description", "content"]
            }
        }
    )
    hits = response["hits"]["hits"]
    results = []
    for hit in hits:
        source = hit["_source"]
        source["_index"] = hit["_index"]
        results.append(source)
    return results
