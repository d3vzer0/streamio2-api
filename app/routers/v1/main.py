from fastapi import APIRouter, Depends, Security
from app.routers.v1.search import api as SearchAPI
from app.routers.v1.unsplash import api as UnsplashAPI

api_v1 = APIRouter()

api_v1.include_router(SearchAPI.router,
    tags=['search']
)
api_v1.include_router(UnsplashAPI.router,
    tags=['unsplash']
)