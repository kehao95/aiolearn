[![license](https://img.shields.io/github/license/mashape/apistatus.svg?maxAge=2592000)]()
[![Build Status](https://travis-ci.org/kehao95/aiolearn.svg?branch=master)](https://travis-ci.org/kehao95/aiolearn)
# aiolearn
Thu Learn Spider for asyncio (PEP-3156)
## 关于这个项目
之前我完成了thu_learn项目作为清华大学的网络爬虫，但是效率一直是一个问题。
在那个项目中我使用的是requests作为网络库，请求效率虽然不慢，但是由于是阻塞的，会浪费大量的时间在网络等待上。
在这个项目中，我使用了python3.5的asyncio语法换用了异步的aiohttp库作为网络请求，使得爬虫的大部分行为变为异步的。
同时更改了类的结构，将用户及其session作为了类的一部分，使之可以同时处理多用户连接。
由于异步地重构使得库的使用方法大大改变，必须使用异步的方法进行调用，因此有了这个全新的项目。

![性能对比图](http://ww4.sinaimg.cn/large/bc2a20f8jw1eyfgutzss8j20kn0ctmxp.jpg)


## 简单理解 asynico：
通过 `async def` 来声明的函数为协程函数。协程函数的执行非同步，而是在异步执行，当遇见IO block的时候，如在本项目的网络请求，可以近乎并行执行。
协程需要使用asynico的event.loop来包裹执行。

## 示例使用
```python
import asyncio
import aiolearn
import getpass

async def main():
    user = aiolearn.User(username=input('input username'), password=getpass.getpass("input password:"))
    semester = aiolearn.Semester(user, current=False)
    courses = await semester.courses
    for course in courses:
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
    
```

semester.courses即协程对象，需要使用await代表获得其值。

