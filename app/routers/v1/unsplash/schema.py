
from pydantic import BaseModel
from typing import List, Dict, Optional


class UserLinks(BaseModel):
    html: str


class UserData(BaseModel):
    id: str
    username: str
    name: str
    links: UserLinks


class UrlData(BaseModel):
    full: str
    regular: str


class UnsplashOut(BaseModel):
    id: str
    width: int
    height: int
    description: Optional[str]
    user: UserData
    urls: UrlData
