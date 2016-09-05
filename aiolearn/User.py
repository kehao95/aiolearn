import aiohttp
import getpass
import logging
import asyncio
from bs4 import BeautifulSoup
from .config import _URL_LOGIN
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

    def __del__(self):
        if self.session is not None:
            self.session.close()

    async def make_soup(self, url):
        _logger.debug("%s make_soup start %s" % (self.username, url))
        if self.session is None:
            _logger.debug("%s: login()" % self.username)
            await self.login()
        try:
            r = await self.session.get(url)
        except aiohttp.errors.ServerDisconnectedError:
            print(url)
            raise Exception("error in makesoup")
        soup = BeautifulSoup(await r.text(), "html.parser")
        _logger.debug("make_soup done")
        return soup

    async def login(self):
        data = dict(
            userid=self.username,
            userpass=self.password,
        )
        self.session = aiohttp.ClientSession(loop=loop)
        r = await self.session.post(_URL_LOGIN, data=data)
        content = await r.text()
        if len(content) > 120:
            raise RuntimeError(r)
