
from elasticsearch_dsl.query import Range
from pydantic import BaseModel, validator, root_validator
from typing import List, Dict, Optional

VALID_AGGREGATIONS = ['term', 'range']


class TermBucket(BaseModel):
    key: str
    doc_count: int


class AggregationOptions(BaseModel):
    type: str = 'term'
    size: int = 20

    @validator('type')
    def must_be_of_type(cls, v):
        if v not in VALID_AGGREGATIONS:
            raise ValueError(f'Type must be one of: {", ".join(VALID_AGGREGATIONS)}')
        return v


class RangeFilter(BaseModel):
    gte: int
    lte: int


class SearchFilter(BaseModel):
    term: Optional[str] = None
    range: Optional[RangeFilter] = None

    @root_validator
    def validate_options(cls, values):
        if not values['range'] and not values['term']:
            raise ValueError(f'Filter must contain filter value of type term or range')
        values['type'] = 'term' if values['term'] else 'range'
        return values


class SearchIn(BaseModel):
    query: str = '*'
    start: int = 1
    limit: int = 20
    filters: Optional[Dict[str, SearchFilter]] = []
    aggregations: Optional[Dict[str, AggregationOptions]] = {}


class TermAggregation(BaseModel):
    key: str
    doc_count: int


class SearchOut(BaseModel):
    total: int
    start: int
    limit: int
    results: List[Dict]
    aggregations: Optional[Dict[str, TermAggregation]]
