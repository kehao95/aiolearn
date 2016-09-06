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
