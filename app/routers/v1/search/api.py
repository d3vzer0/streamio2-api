from fastapi import APIRouter
from elasticsearch import Elasticsearch
from app.environment import config
from .schema import SearchOut, SearchIn
from .utils import AbstractSearch

es_client = Elasticsearch([config['es_hosts']])
router = APIRouter()


@router.post('/search', response_model=SearchOut)
async def search_es(search: SearchIn):
    search_object = search.dict(exclude_none=True)
    async with AbstractSearch(es_client=es_client, index=config['index_pattern']) as abstract_search:
        results = await abstract_search.get(query=search_object['query'],
            filters=search_object['filters'],
            aggregations=search_object['aggregations']
        )
        return results
    