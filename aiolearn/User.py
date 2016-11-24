import aiohttp
import getpass
import logging
import asyncio
import json
from bs4 import BeautifulSoup
from .config import _URL_LOGIN, _GET_TICKET, _URL_BASE_NEW
logging.basicConfig(level=logging.DEBUG)
_logger = logging.getLogger(__name__)
loop = asyncio.get_event_loop()


class User:
    def __init__(self, username, password):
        if username is None or password is None:
            username = input("TsinghuaId:")
            password = getpass.getpass("Password:")
        self.username = username
        self.password = password
        self.session = None
        self.session_new = None

    def __del__(self):
        if self.session is not None:
            self.session.close()
            self.session_new.close()

    async def wrapped_get(self, url):
        if self.session is None: await self.login()
        _logger.debug("%s sending GET request %s" % (self.username, url))
        if not url.startswith(_URL_BASE_NEW):
            r = await self.session.get(url)
        else:
            r = await self.session_new.get(url)
        text = await r.text()
        return text

    async def session_post(self, url, body):
        if self.session is None: await self.login()
        pass

    async def make_soup(self, url):
        html_text = await self.wrapped_get(url)
        return BeautifulSoup(html_text, "html.parser")

    async def cook_json(self, url):
        json_text = await self.wrapped_get(url) # TODO: response.json()
        return json.loads(json_text)

    async def login(self):
        _logger.debug("%s: login()" % self.username)
        data = dict(
            userid=self.username,
            userpass=self.password,
        )
        self.session = aiohttp.ClientSession(loop=loop)
        self.session_new = aiohttp.ClientSession(loop=loop)
        r = await self.session.post(_URL_LOGIN, data=data)
        content = await r.text()
        if len(content) > 120:
            raise RuntimeError(r)

        # New WebLearning
        # TODO: duplicate requests
        soup = await self.make_soup(_GET_TICKET)
        url_ticket = soup.iframe['src']
        await self.wrapped_get(url_ticket)
