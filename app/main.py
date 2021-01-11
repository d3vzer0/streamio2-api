from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from .environment import config
from .routers.v1.main import api_v1

app = FastAPI(
    title='StreamIO2',
    description='StreamIO2 Search API',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[config['allow_origin']],
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'DELETE', 'OPTIONS'],
    allow_headers=["*"],
)

# Include v1 endpoints
app.include_router(api_v1, prefix=config['api_path'])
