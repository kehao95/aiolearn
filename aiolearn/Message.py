import re


class Message:
    def __init__(self, user, id, course_id, title, date, detail_new=None, url=None):
        self.title = title.strip()
        self.url = url
        self.date = date
        self.user = user
        self.id = id
        self.course_id = course_id
        self.detail_new = detail_new

    @property
    async def detail(self):
        if(not self.detail_new is None):
            return self.detail_new
        soup = await self.user.make_soup(self.url)
        detail = soup.find_all('td', class_='tr_l2')[1]
        detail = detail.text.replace('\xa0', ' ')
        detail = re.sub('(\\xa0)+', ' ', detail)
        detail = re.sub('\n+', '\n', detail)
        return detail

    @property
    async def dict(self):
        d = self.__dict__.copy()
        d["detail"] = await self.detail
        del d['user']
        return d
