import os

config = {
    'api_path': os.getenv('ST_API_PATH', '/api/v1'),
    'allow_origin': os.getenv('ST_CORS_ALLOW_ORIGIN', '*'),
    'es_hosts': os.getenv('ST_ES_HOSTS', 'https://ingest_user:ingest_user@localhost:9200/'),
    'es_ca_path': os.getenv('ST_ES_CA_PATH', '/etc/ssl/es.crt'),
    'index_pattern': os.getenv('ST_INDEX_PATTERN', 'applications-streamio*'),
    'unsplash_key': os.getenv('ST_UNSPLASH_KEY')
}