from elasticsearch_dsl import Search, MultiSearch, A

class AbstractSearch:
    def __init__(self, es_client=None, index=None):
        self.es_client = es_client
        self.index = index
        self.search = None
        self.multi_search = None

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
        # print(self.search.to_dict())
        self.__exclude(exclude)
        self.__query(query)
        self.__aggregations(aggregations)
        try:
            return AbstractSearch.es2api(
                self.search.sort('-publish_date')[start:start+limit].execute().to_dict(),
                start, limit
            )
        except Exception as err:
            print(err)

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



class AbstractMultiSearch:
    def __init__(self, es_client=None, index=None, multi_search=None):
        self.es_client = es_client
        self.index = index
        self.multi_search = multi_search

    @staticmethod
    def es2api(response, start, limit, column=None):
        return {
            'total': response['hits']['total']['value'],
            'results': response['hits']['hits'],
            'aggregations': {key: value['buckets'] for key, value \
                in response.get('aggregations', {}).items()},
            'start': start,
            'limit': limit,
            'column': column
        }

    async def multisearch(self, searches):
        for search in searches:
            search_object = self.__get(
                query=search['query'],
                filters=search['filters'],
                start=search['start'],
                limit=search['limit'],
                from_date=search['from_date'],
                to_date=search['to_date'],
                aggregations=search['aggregations'],
                exclude=search['exclude']
            )
            self.multi_search = self.multi_search.add(search_object)
        try:
            responses = [
                AbstractMultiSearch.es2api(
                    response.to_dict(),
                    searches[index]['start'],
                    searches[index]['limit'],
                    column=searches[index]['column']) for \
                    (index, response) in enumerate(self.multi_search.execute())
                ]
            return responses

        except Exception as err:
            print(err)

    def __get(self, query='*', filters=None, aggregations=None, exclude=None, 
        to_date=None, from_date=None, start=0, limit=30):
        single_search = Search(using=self.es_client, index=self.index)
        single_search = self.__filters(single_search, filters, to_date, from_date)
        single_search = self.__exclude(single_search, exclude)
        single_search = self.__query(single_search, query)
        single_search = self.__aggregations(single_search, aggregations)
        single_search = single_search.sort('-publish_date')[start:start+limit]
        return single_search
  
    def __aggregations(self, search, aggregations):
        for key, value in aggregations.items():
            try:
                aggregation = A(value['type'], field=f'{key}.keyword')
                search.aggs.bucket(key, aggregation)
            except Exception as err:
                print(err)
        return search
    
    def __filters(self, search, filters, to_date, from_date):
        search = search.filter('range', **{f'publish_date': {'gte':from_date ,'lte':to_date}})
        for key, value in filters.items():
           search = search.filter(value['type'], **{f'{key}.keyword': value[value['type']]})
        return search

    def __exclude(self, search, exclude):
        for value in exclude:
            search = search.exclude(value['type'], **{f'{value["field"]}.keyword': value[value['type']]})
        return search

    def __query(self, search, query):
        search = search.query('simple_query_string', query=query)
        return search
    
    async def __aenter__(self):
        self.multi_search = MultiSearch(using=self.es_client, index=self.index)
        return self

    async def __aexit__(self, *args, **kwargs):
        return self

