import aiohttp

async def get_unsplash(query, client_id, count=10):
    endpoint = 'https://api.unsplash.com/photos/random'
    headers = {
        'Accept-Version': 'v1',
        'Authorization': f'Client-ID {client_id}'
    }
    params = {
        'orientation': 'portrait',
        'query': query,
        'count': count
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint, headers=headers, params=params) as response:
            return await response.json()
