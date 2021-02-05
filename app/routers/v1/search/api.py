from fastapi import APIRouter
from elasticsearch import Elasticsearch
from app.environment import config
from .schema import SearchOut, SearchIn, HistogramIn
from .utils import AbstractSearch
from typing import List
from ssl import create_default_context
import ssl

context = create_default_context(cafile=config['es_ca_path'])
es_client = Elasticsearch([config['es_hosts']], ssl_context=context)
router = APIRouter()

@router.post('/search', response_model=List[SearchOut])
async def search_es(searches: List[SearchIn]):
    search_objects = [search.dict(exclude_none=True) for search in searches]
    async with AbstractSearch(es_client=es_client, index=config['index_pattern']) as abstract_search:
        results = [
            {
                **await abstract_search.get(query=search['query'],
                    filters=search['filters'],
                    start=search['start'],
                    limit=search['limit'],
                    from_date=search['from_date'],
                    to_date=search['to_date'],
                    aggregations=search['aggregations'],
                    exclude=search['exclude']),
                'column':search['column']
            }
            for search in search_objects
        ]
        return results

@router.post('/histogram')
async def histogram_es(search: HistogramIn):
    search_object = search.dict(exclude_none=True)
    async with AbstractSearch(es_client=es_client, index=config['index_pattern']) as abstract_search:
        results = await abstract_search.get_hist(query=search_object['query'],
            filters=search_object['filters'],
            field=search_object['field'],
            from_date=search_object['from_date'],
            to_date=search_object['to_date'],
            interval=search_object['interval'],
            exclude=search_object['exclude']
        )
        return results
    