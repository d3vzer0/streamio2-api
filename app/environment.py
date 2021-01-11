import os

config = {
    'api_path': os.getenv('ST_API_PATH', '/api/v1'),
    'allow_origin': os.getenv('ST_CORS_ALLOW_ORIGIN', '*'),
    'es_hosts': os.getenv('ST_ES_HOSTS', 'http://localhost:9200/'),
    'index_pattern': os.getenv('ST_INDEX_PATTERN', 'sec-streaming-*')
}
