class File:
    def __init__(self, user, id, name, title, date, size, url=None):
        self.user = user
        self.id = id
        self.name = name
        self.url = url
        self.title = title.strip()
        self.date = date
        self.size = size
