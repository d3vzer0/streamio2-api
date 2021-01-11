from fastapi import APIRouter, Depends, Security
from app.routers.v1.search import api as SearchAPI

api_v1 = APIRouter()

api_v1.include_router(SearchAPI.router,
    tags=['search']
)