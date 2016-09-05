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
