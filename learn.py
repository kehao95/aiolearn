#! /usr/bin/python
# -*- coding: utf-8 -*-
import aiohttp
from bs4 import BeautifulSoup, Comment
import re
import getpass
import asyncio
import logging
import time
from itertools import *

__author__ = 'kehao'

# global vars
_URL_BASE = 'https://learn.tsinghua.edu.cn'
_URL_LOGIN = _URL_BASE + '/MultiLanguage/lesson/teacher/loginteacher.jsp'

# 学期
_URL_CURRENT_SEMESTER = 'http://learn.tsinghua.edu.cn/MultiLanguage/' \
                        'lesson/student/MyCourse.jsp?typepage=1'
_URL_PAST_SEMESTER = 'http://learn.tsinghua.edu.cn/MultiLanguage/' \
                     'lesson/student/MyCourse.jsp?typepage=2'
# 个人信息
_URL_PERSONAL_INFO = 'http://learn.tsinghua.edu.cn/MultiLanguage/' \
                     'vspace/vspace_userinfo1.jsp'

# 课程不同板块前缀
_PREF_MSG = 'http://learn.tsinghua.edu.cn/MultiLanguage/' \
            'public/bbs/getnoteid_student.jsp?course_id='
_PREF_INFO = 'http://learn.tsinghua.edu.cn/MultiLanguage/' \
             'lesson/student/course_info.jsp?course_id='
_PREF_FILES = 'http://learn.tsinghua.edu.cn/MultiLanguage/' \
              'lesson/student/download.jsp?course_id='
_PREF_LIST = 'http://learn.tsinghua.edu.cn/MultiLanguage/' \
             'lesson/student/ware_list.jsp?course_id='
_PREF_WORK = 'http://learn.tsinghua.edu.cn/MultiLanguage/' \
             'lesson/student/hom_wk_brw.jsp?course_id='

loop = asyncio.get_event_loop()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def timing(f):
    """function timing wrapper"""

    def wrapper(*arg, **kw):
        t1 = time.time()
        ret = f(*arg, **kw)
        t2 = time.time()
        print('func:%r args:[%r, %r] took: %2.4f sec' % \
              (f.__name__, arg, kw, t2 - t1))
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
            # 一个异步地请求一个课程
            i = item.find('a')
            url = i['href']
            if url.startswith('/Mult'):
                url = _URL_BASE + url
            else:  # !!important!! ignore the new WebLearning Courses At This moment
                return None
            name = re.sub(r'\([^\(\)]+\)$', '', re.sub(r'[\n\r\t ]', '', i.contents[0]))
            id = url[-6:]
            return Course(user=user, id=id, name=name, url=url)

        user = self.user
        soup = await self.user.make_soup(self.url)
        tasks = [get_course_one(i) for i in soup.find_all('tr', class_=['info_tr', 'info_tr2'])]
        courses = [c for c in await asyncio.gather(*tasks) if c is not None]
        return courses


class Course:
    def __init__(self, user, id, name, url):
        self.id = id
        self.name = name
        self.url = url
        self.user = user

    @property
    async def works(self):
        async def get_work(item):
            tds = item.find_all('td')
            url = 'http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/' \
                  + item.find('a')['href']
            id = re.search(r'(\d+)', url).group(0)
            title = item.find('a').contents[0]
            start_time = tds[1].contents[0]
            end_time = tds[2].contents[0]
            submitted = ("已经提交" in tds[3].contents[0])
            return Work(user=user, id=id, title=title, url=url
                        , start_time=start_time, end_time=end_time,
                        submitted=submitted)

        user = self.user
        works_url = _PREF_WORK + self.id
        works_soup = await self.user.make_soup(works_url)
        tasks = [get_work(i) for i in works_soup.find_all('tr', class_=['tr1', 'tr2'])]
        works = await asyncio.gather(*tasks)
        return works

    @property
    async def messages(self):
        async def get_message(item):
            tds = item.find_all('td')
            title = tds[1].contents[1].text
            url = 'http://learn.tsinghua.edu.cn/MultiLanguage/public/bbs/' + tds[1].contents[1]['href']
            id = re.findall(r'id=(\d+)', url)[0]
            date = tds[3].text
            return Message(user=user, id=id, title=title, url=url, date=date)

        user = self.user
        msg_url = _PREF_MSG + self.id
        msg_soup = await self.user.make_soup(msg_url)
        tasks = [get_message(i) for i in msg_soup.find_all('tr', class_=['tr1', 'tr2'])]
        messages = await asyncio.gather(*tasks)
        return messages

    @property
    async def files(self):
        return []


class Work:
    def __init__(self, user, id, title, url, start_time, end_time, submitted):
        self.id = id
        self.title = title
        self.url = url
        self.start_time = start_time
        self.end_time = end_time
        self.submitted = submitted
        self.user = user

    @property
    async def details(self):
        soup = await self.user.make_soup(self.url)
        try:
            details = soup.find_all('td', class_='tr_2')[1].textarea.contents[0]
        except IndexError:
            details = ""
        return details


class Message:
    def __init__(self, user, id, title, url, date):
        self.title = title
        self.url = url
        self.date = date
        self.user = user
        self.id = id

    @property
    async def details(self):
        soup = await self.user.make_soup(self.url)
        details = soup.find_all('td', class_='tr_l2')[1].text.replace('\xa0', ' ')
        details = re.sub('(\\xa0)+', ' ', details)
        details = re.sub('\n+', '\n', details)
        return details


class User:
    def __init__(self, userid, password):
        if userid is None or password is None:
            userid = input("TsinghuaId:")
            password = getpass.getpass("Password:")
        self.userid = userid
        self.password = password
        self.session = None

    def __del__(self):
        if self.session is not None:
            self.session.close()

    async def make_soup(self, url):
        logger.debug("%s make_soup start %s" % (self.userid, url))
        if self.session is None:
            await self.login()
        try:
            r = await self.session.get(url)
        except aiohttp.errors.ServerDisconnectedError:
            print(url)
            raise Exception("error in makesoup")
        soup = BeautifulSoup(await r.text(), "html.parser")
        logger.debug("make_soup done")
        return soup

    async def login(self):
        data = dict(
            userid=self.userid,
            userpass=self.password,
        )
        self.session = aiohttp.ClientSession(loop=loop)
        r = await self.session.post(_URL_LOGIN, data=data)
        content = await r.text()
        if len(content) > 120:
            raise RuntimeError(r)


@timing
async def main():
    import json
    with open("secret.json", "r") as f:
        secrets = json.loads(f.read())
    users = []
    for user in secrets['users']:
        users.append(User(userid=user['username'], password=user['password']))

    semesters = [Semester(user) for user in users]
    courses = list(chain(*await asyncio.gather(*[semester.courses for semester in semesters])))
    works = chain(*await asyncio.gather(*[course.works for course in courses]))
    for work in works:
        print(work.title)
    messages = chain(*await asyncio.gather(*[course.messages for course in courses]))
    for message in messages:
        print(message.title)



if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
