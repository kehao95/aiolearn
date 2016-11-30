import aiohttp
import getpass
import logging
import asyncio
import json
from bs4 import BeautifulSoup
from .config import _URL_LOGIN, _URL_CURRENT_SEMESTER, _URL_BASE_NEW
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
        self.cache = None

    def __del__(self):
        if self.session is not None:
            self.session.close()
            self.session_new.close()

    async def wrapped_get(self, url):
        if self.session is None: await self.login()
        _logger.debug("%s GET %s" % (self.username, url))

        if url == _URL_CURRENT_SEMESTER:
            cache = self.cache
            if not (cache is None):
                self.cache = None
                _logger.debug("%s cache hit" % self.username)
                return cache
            _logger.debug("%s cache unavailable" % self.username)



        if not url.startswith(_URL_BASE_NEW):
            r = await self.session.get(url)
        else:
            r = await self.session_new.get(url)
        text = await r.text()

        if url == _URL_CURRENT_SEMESTER:
            self.cache = text
            _logger.debug("%s writing cache" % self.username)

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
        soup = await self.make_soup(_URL_CURRENT_SEMESTER) # cache in play
        url_ticket = soup.iframe['src']
        await self.wrapped_get(url_ticket)
