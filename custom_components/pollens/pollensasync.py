"""asyncio-friendly python API for RNSA (https://pollens.fr)."""
import asyncio
import aiohttp
from aiohttp.client import ClientError, ClientTimeout
import json

import async_timeout

DEFAULT_TIMEOUT = 240

CLIENT_TIMEOUT = ClientTimeout(total=DEFAULT_TIMEOUT)

BASE_URL = "https://pollens.fr/risks/thea/counties/{}"


class PollensClient:
    """Pollens client implementation."""

    def __init__(self, session: aiohttp.ClientSession = None, timeout=CLIENT_TIMEOUT):
        """Constructor.
        session: aiohttp.ClientSession or None to create a new session.
        """
        self._county_name = None
        self._params = {}
        self._risk_level = None
        self._risks = {}
        self._timeout = timeout
        if session is not None:
            self._session = session
        else:
            self._session = aiohttp.ClientSession()

    async def Get(self, number):
        """Get data by station number."""
        try:
            request = await self._session.get(
                BASE_URL.format(number), timeout=CLIENT_TIMEOUT
            )
            if "application/json" in request.headers["content-type"]:
                request_json = await request.json()
            else:
                request_json = await request.text()
                request_json = json.loads(request_json)

            self._county_name = request_json["countyName"]
            for risk in request_json["risks"]:
                self._risks[risk["pollenName"]] = risk["level"]
            self._risk_level = request_json["riskLevel"]
            return request_json
        except (ClientError, asyncio.TimeoutError, ConnectionRefusedError) as err:
            return None

    @property
    def county_name(self):
        return self._county_name

    @property
    def risks(self):
        return self._risks

    @property
    def risk_level(self):
        return self._risk_level

    # async def _get(self, path, **kwargs):
    #     with async_timeout.timeout(self._timeout):
    #         resp = await self._session.get(path, params=dict(self._params, **kwargs))
    #         print(type(resp.headers["Content-Type"]))
    #         return await resp.text(encoding="utf-8")
