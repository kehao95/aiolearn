import re
import asyncio
from .Message import Message
from .File import File
from .Work import Work
from .config import (_COURSE_WORK, _COURSE_MSG, _COURSE_FILES, _URL_PREF,
                     _ID_COURSE_URL, _PAGE_FILE, _PAGE_MSG)
from bs4 import Comment


class Course:
    def __init__(self, user, id, name=None, url=None):
        self.id = id
        self.name = name
        self.user = user
        if url is None:
            self.url = _ID_COURSE_URL % id
        else:
            self.url = url

    @property
    async def works(self):
        async def get_work(item):
            tds = item.find_all('td')
            url = _URL_PREF + item.find('a')['href']
            ids = re.findall(r'id=(\d+)', url)
            id = ids[0]
            course_id = ids[1]
            title = item.find('a').contents[0]
            start_time = tds[1].contents[0]
            end_time = tds[2].contents[0]
            submitted = ("已经提交" in tds[3].contents[0])
            return Work(user=user, id=id, course_id=course_id, title=title,
                        url=url, start_time=start_time, end_time=end_time,
                        completion=submitted)

        user = self.user
        works_url = _COURSE_WORK % self.id
        works_soup = await self.user.make_soup(works_url)
        tasks = [get_work(i) for i
                 in works_soup.find_all('tr', class_=['tr1', 'tr2'])]
        works = await asyncio.gather(*tasks)
        return works

    @property
    async def messages(self):
        async def get_message(item):
            tds = item.find_all('td')
            title = tds[1].contents[1].text
            url = _PAGE_MSG % tds[1].contents[1]['href']
            ids = re.findall(r'id=(\d+)', url)
            id = ids[0]
            course_id = ids[1]
            date = tds[3].text
            return Message(user=user, id=id, course_id=course_id,
                           title=title, url=url, date=date)

        user = self.user
        msg_url = _COURSE_MSG % self.id
        msg_soup = await self.user.make_soup(msg_url)
        tasks = [get_message(i) for i in msg_soup.find_all('tr', class_=['tr1', 'tr2'])]
        messages = await asyncio.gather(*tasks)
        return messages

    @property
    async def files(self):
        async def get_file(item):
            name, id = re.search(r'getfilelink=([^&]+)&id=(\d+)', str(item.find(text=lambda text: isinstance(text, Comment)))).groups()
            a = item.find('a')
            url = _PAGE_FILE % (self.id, name)
            title = re.sub(r'[\n\r\t ]', '', a.contents[0])
            name = re.sub(r'_[^_]+\.', '.', name)
            return File(user=user, id=id, name=name, url=url, title=title)

        user = self.user
        file_url = _COURSE_FILES % self.id
        files_soup = await self.user.make_soup(file_url)
        tasks = [get_file(item) for item in files_soup.find_all('tr', class_=['tr1', 'tr2'])]
        files = await asyncio.gather(*tasks)
        return files

    @property
    def dict(self):
        d = self.__dict__.copy()
        user = self.user.__dict__.copy()
        del user['session']
        d['user'] = user
        return d
