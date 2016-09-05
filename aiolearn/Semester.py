import asyncio
import re
from .Course import Course
from .config import _URL_CURRENT_SEMESTER, _URL_PAST_SEMESTER, _URL_BASE


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
