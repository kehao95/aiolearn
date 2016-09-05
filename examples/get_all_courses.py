
import asyncio
from context import aiolearn
import getpass

async def main():
    user = aiolearn.User(username='keh13', password=getpass.getpass("input password:"))
    semester = aiolearn.Semester(user, current=False)
    courses = await semester.courses
    for course in courses:
        print(course.name)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
