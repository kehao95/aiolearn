class Work:
    def __init__(self, user, id, course_id, title, start_time, end_time, completion, url=None, detail_new=None):
        self.id = id
        self.course_id = course_id
        self.title = title.strip()
        self.start_time = start_time
        self.end_time = end_time
        self.completion = completion  # 0 for 尚未提交, 1 for 已经提交, 2 for 已经批改
        self.user = user
        self.url = url
        self.detail_new = detail_new

    @property
    async def grading(self):
        return ""  # TODO

    @property
    async def detail(self):
        if(not self.detail_new is None):
            return self.detail_new
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
