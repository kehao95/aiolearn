
import asyncio
from context import aiolearn
import getpass

async def main():
    user = aiolearn.User(username='keh13',
                         password=getpass.getpass("input password:"))
    semester = aiolearn.Semester(user, current=False)
    courses = await semester.courses
    course = courses[0]
    print(course.name)
    works = await course.works
    messages = await course.messages
    files = await course.files
    print('\n>>works')
    for work in works:
        print(work.title)
    print('\n>>messages')
    for message in messages:
        print(message.title)
    print('\n>>files')
    for file in files:
        print(file.name)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
