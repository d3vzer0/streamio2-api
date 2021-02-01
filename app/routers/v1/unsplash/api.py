from fastapi import APIRouter
from app.environment import config
from typing import List
from .schema import UnsplashOut
from .utils import get_unsplash


router = APIRouter()

@router.get('/unsplash', response_model=List[UnsplashOut])
async def get_random(query: str = 'nature', count: int = 10):
    images = await get_unsplash('nature', config['unsplash_key'])
    return images
