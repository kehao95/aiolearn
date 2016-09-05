#! /usr/bin/python
# -*- coding: utf-8 -*-
import aiohttp
from bs4 import BeautifulSoup, Comment
import re
import getpass
import asyncio
import logging
import time
from itertools import chain

__author__ = 'kehao'
# global vars
_URL_BASE = 'https://learn.tsinghua.edu.cn/MultiLanguage/'
_URL_LOGIN = _URL_BASE + 'lesson/teacher/loginteacher.jsp'
_URL_PREF = 'http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/'
# Semesters
_URL_CURRENT_SEMESTER = _URL_PREF + 'MyCourse.jsp?typepage=1'
_URL_PAST_SEMESTER = _URL_PREF + 'MyCourse.jsp?typepage=2'
_URL_PERSONAL_INFO = _URL_BASE + 'vspace/vspace_userinfo1.jsp'
# Courses
_ID_COURSE_URL = _URL_PREF + 'course_locate.jsp?course_id=%s'
# Differet Sections of Course
_COURSE_MSG = _URL_BASE + 'public/bbs/getnoteid_student.jsp?course_id=%s'
_COURSE_INFO = _URL_PREF + 'course_info.jsp?course_id=%s'
_COURSE_FILES = _URL_PREF + 'download.jsp?course_id=%s'
_COURSE_LIST = _URL_PREF + 'ware_list.jsp?course_id=%s'
_COURSE_WORK = _URL_PREF + 'hom_wk_brw.jsp?course_id=%s'
# Object Detail Page
_PAGE_MSG = _URL_BASE + 'public/bbs/%s'
_PAGE_FILE = 'http://learn.tsinghua.edu.cn/kejian/data/%s/download/%s'

loop = asyncio.get_event_loop()
logging.basicConfig(level=logging.DEBUG)
_logger = logging.getLogger(__name__)

def timing(f):
    """function timing wrapper"""

    def wrapper(*arg, **kw):
        t1 = time.time()
        ret = f(*arg, **kw)
        t2 = time.time()
        print('func:%r args:[%r, %r] took: %2.4f sec'
              % (f.__name__, arg, kw, t2 - t1))
        return ret

    return wrapper


def run(coroutine):
    r = loop.run_until_complete(coroutine)
    return r


class Semester:
    def __init__(self, user, current=True):
        if current is True:
            self.url = _URL_CURRENT_SEMESTER
        else:
            self.url = _URL_PAST_SEMESTER
        self.user = user

    @property
    async def courses(self):
        async def get_course_one(item):
            i = item.find('a')
            url = i['href']
            if url.startswith('/Mult'):
                url = _URL_BASE + url
            else:
                # !!important!!
                # ignore the new WebLearning Courses at this moment
                return None
            name = re.sub(r'\([^\(\)]+\)$', '', re.sub(r'[\n\r\t ]', '',
                          i.contents[0]))
            id = url[-6:]
            return Course(user=user, id=id, name=name)

        user = self.user
        soup = await self.user.make_soup(self.url)
        tasks = [get_course_one(i) for i
                 in soup.find_all('tr', class_=['info_tr', 'info_tr2'])]
        courses = [c for c in await asyncio.gather(*tasks) if c is not None]
        return courses


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


class Work:
    def __init__(self, user, id, course_id, title, start_time, end_time, completion, url):
        self.id = id
        self.course_id = course_id
        self.title = title
        self.start_time = start_time
        self.end_time = end_time
        self.completion = completion
        self.user = user
        self.url = url

    @property
    async def detail(self):
        soup = await self.user.make_soup(self.url)
        try:
            detail = soup.find_all('td', class_='tr_2')[1].textarea.contents[0]
        except IndexError:
            detail = ""
        return detail

    @property
    async def dict(self):
        d = self.__dict__.copy()
        d["detail"] = await self.detail
        del d['user']
        return d


class Message:
    def __init__(self, user, id, course_id, title, url, date):
        self.title = title
        self.url = url
        self.date = date
        self.user = user
        self.id = id
        self.course_id = course_id

    @property
    async def detail(self):
        soup = await self.user.make_soup(self.url)
        detail = soup.find_all('td', class_='tr_l2')[1].text.replace('\xa0', ' ')
        detail = re.sub('(\\xa0)+', ' ', detail)
        detail = re.sub('\n+', '\n', detail)
        return detail

    @property
    async def dict(self):
        d = self.__dict__.copy()
        d["detail"] = await self.detail
        del d['user']
        return d


class File:
    def __init__(self, user, id, name, url, title):
        self.user = user
        self.id = id
        self.name = name
        self.url = url
        self.title = title


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

async def main():
    import json
    with open("secret.json", "r") as f:
        secrets = json.loads(f.read())
    users = []
    for user in secrets['users']:
        users.append(User(username=user['username'], password=user['password']))
    semesters = [Semester(user) for user in users]
    courses = list(chain(*await asyncio.gather(*[semester.courses for semester in semesters])))
    files = asyncio.gather(*[course.files for course in courses])
    messages = asyncio.gather(*[course.messages for course in courses])
    works = asyncio.gather(*[course.works for course in courses])
    files, messages, works = map(lambda x: list(chain(*x)), await asyncio.gather(files, messages, works))
    works_details = await asyncio.gather(*[work.detail for work in works])
    for detail in works_details:
        print(detail)
    messages_details = await asyncio.gather(*[message.detail for message in messages])
    for detail in messages_details:
        print(detail)


if __name__ == '__main__':
    start = time.time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    end = time.time()
    print("using time %r" % (end - start))
