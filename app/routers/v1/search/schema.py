
from elasticsearch_dsl.query import Range
from pydantic import BaseModel, validator, root_validator
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import dateparser

VALID_AGGREGATIONS = ['terms', 'range', 'date_histogram']

def default_from():
    return datetime.today() - timedelta(days=7) 
    
def default_to():
    return datetime.today()


class TermBucket(BaseModel):
    key: str
    doc_count: int


class AggregationOptions(BaseModel):
    type: str = 'terms'
    size: int = 20
    args: Optional[Dict] = {}

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


class SearchExclude(BaseModel):
    term: Optional[str] = None
    field: str
    range: Optional[RangeFilter] = None

    @root_validator
    def validate_options(cls, values):
        if not values['range'] and not values['term']:
            raise ValueError(f'Filter must contain filter value of type term or range')
        values['type'] = 'term' if values['term'] else 'range'
        return values


class SearchIn(BaseModel):
    query: str = '*'
    column: str
    start: int = 1
    limit: int = 20
    from_date: datetime = default_from()
    to_date: datetime = default_to()
    filters: Optional[Dict[str, List[SearchFilter]]] = {}
    exclude: Optional[List[SearchExclude]] = []
    aggregations: Optional[Dict[str, AggregationOptions]] = {}

    @validator('from_date', pre=True)
    def valid_from_date(cls, v):
        return dateparser.parse(v)

    @validator('to_date', pre=True)
    def valid_to_date(cls, v):
        return dateparser.parse(v)

class HistogramIn(BaseModel):
    query: str = '*'
    start: int = 1
    limit: int = 20
    from_date: datetime = default_from()
    to_date: datetime = default_to()
    field: str
    interval: str = 'day'
    filters: Optional[Dict[str, SearchFilter]] = {}
    exclude: Optional[List[SearchExclude]] = []

    @validator('from_date', pre=True)
    def valid_from_date(cls, v):
        return dateparser.parse(v)

    @validator('to_date', pre=True)
    def valid_to_date(cls, v):
        return dateparser.parse(v)

class TermAggregation(BaseModel):
    key: str
    doc_count: int


class SearchOut(BaseModel):
    total: int
    start: int
    column: str
    limit: int
    results: List[Dict]
    aggregations: Optional[Dict]
