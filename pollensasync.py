"""asyncio-friendly python API for RNSA (https://pollens.fr)."""
import asyncio
import aiohttp
import async_timeout

BASE_URL = 'https://pollens.fr/risks/thea/counties/{}'

class PollensClient(object):
    """Pollens client implementation."""

    def __init__(self, session=None,
                 timeout=aiohttp.client.DEFAULT_TIMEOUT):
        """Constructor.
        session: aiohttp.ClientSession or None to create a new session.
        """
        self._params = {}
        self._timeout = timeout
        if session is not None:
            self._session = session
        else:
            self._session = aiohttp.ClientSession()

    async def Get(self, number):
        """Get data by station number."""
        return (await self._get(BASE_URL.format(number)))

    
    async def _get(self, path, **kwargs):
        with async_timeout.timeout(self._timeout):
            resp = await self._session.get(
                path, params=dict(self._params, **kwargs))
            print(type(resp.headers['Content-Type']))
            return (await resp.text(encoding='utf-8'))