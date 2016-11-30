import asyncio
import re
from .Course import Course
from .config import _URL_CURRENT_SEMESTER, _URL_PAST_SEMESTER, _URL_BASE


class Semester:
    def __init__(self, user, current=True):
        if current is True: # TODO: three possible values when summer semester is comming
            self.url = _URL_CURRENT_SEMESTER
        else:
            self.url = _URL_PAST_SEMESTER
        self.user = user

    @property
    async def courses(self):
        async def get_course_one(item):
            i = item.find('a')
            url = i['href']

            name = i.contents[0].strip()

            # remove trailing `(2016-2017秋季学期)`
            name = re.sub(r'\(\d+-\d+\w+\)$', '', name)
            # remove trailing `(1)`
            name = re.sub(r'\(\d+\)$', '', name)

            if url.startswith('/Mult'):
                # Old WebLearning
                url = _URL_BASE + url
                id = url[-6:] # TODO: magic number
                return Course(
                    user  = user,
                    id    = id,
                    name  = name,
                    is_new= False
                )
            else:
                # New WebLearning
                # substring starting from past the last `/`
                id = re.search(r'/([^/]+)$', url).group(1)
                return Course(
                    user   = user,
                    id     = id,
                    name   = name,
                    is_new = True
                )


        user = self.user
        soup = await self.user.make_soup(self.url)
        tasks = [get_course_one(i) for i
                 in soup.find_all('tr', class_=['info_tr', 'info_tr2'])]
        courses = [c for c in await asyncio.gather(*tasks) if c is not None]
        return courses
