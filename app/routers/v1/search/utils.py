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

    async def get(self, query='*', filters=None, aggregations=None, exclude=None, 
        to_date=None, from_date=None, start=0, limit=30):
        self.search = Search(using=self.es_client, index=self.index)
        self.__filters(filters, to_date, from_date)
        self.__exclude(exclude)
        self.__query(query)
        self.__aggregations(aggregations)
        return AbstractSearch.es2api(
            self.search[start:start+limit].execute().to_dict(),
            start, limit
        )

    async def get_hist(self, query='*', filters=None, field=None, interval=None, exclude=None,
        to_date=None, from_date=None, start=0, limit=30):
        self.__filters(filters, to_date, from_date)
        self.__exclude(exclude)
        self.__query(query)
        self.__histogram(field, interval)
        return AbstractSearch.es2api(
            self.search[start:limit].execute().to_dict(),
            start, limit
        )

    def __histogram(self, field, interval):
        try:
            ah = A('terms', field='tags.keyword', size=5)
            aggregation = A('date_histogram', field='publish_date', interval=interval)
            self.search.aggs.bucket('histogram_data', aggregation).bucket('tags', ah)
        except Exception as err:
            print(err)


    def __aggregations(self, aggregations):
        for key, value in aggregations.items():
            print(key, value)
            try:
                aggregation = A(value['type'], field=f'{key}.keyword')
                self.search.aggs.bucket(key, aggregation)
            except Exception as err:
                print(err)
                pass
    
    def __filters(self, filters, to_date, from_date):
        self.search = self.search.filter('range', **{f'publish_date': {'gte':from_date ,'lte':to_date}})
        for key, value in filters.items():
            self.search = self.search.filter(value['type'], **{f'{key}.keyword': value[value['type']]})

    def __exclude(self, exclude):
        for value in exclude:
            self.search = self.search.exclude(value['type'], **{f'{value["field"]}.keyword': value[value['type']]})

    def __query(self, query):
        self.search = self.search.query('simple_query_string', query=query)
    
    async def __aenter__(self):
        self.search = Search(using=self.es_client, index=self.index)
        return self

    async def __aexit__(self, *args, **kwargs):
        return self

