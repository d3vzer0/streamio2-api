from elasticsearch_dsl import Search, A

class AbstractSearch:
    def __init__(self, es_client=None, index=None):
        self.es_client = es_client
        self.index = index
        self.search = None

    @staticmethod
    def es2api(response, start, limit):
        return {
            'total': response['hits']['total']['value'],
            'results': response['hits']['hits'],
            'aggregations': {key: value['buckets'] for key, value \
                in response.get('aggregations', {}).items()},
            'start': start,
            'limit': limit
        }

    async def get(self, query='*', filters=None, aggregations=None, start=0, limit=30):
        self.__filters(filters)
        self.__query(query)
        self.__aggregations(aggregations)
        return AbstractSearch.es2api(
            self.search[start:limit].execute().to_dict(),
            start, limit
        )
   
    def __aggregations(self, aggregations):
        for key, value in aggregations.items():
            self.search = self.search.aggs.bucket(key, value['type'], field=f'{key}.keyword')
    
    def __filters(self, filters):
        for key, value in filters.items():
            self.search = self.search.filter(value['type'], **{f'{key}.keyword': value[value['type']]})

    def __query(self, query):
        self.search = self.search.query('simple_query_string', query=query)
    
    async def __aenter__(self):
        self.search = Search(using=self.es_client, index=self.index)
        return self

    async def __aexit__(self, *args, **kwargs):
        return self
