# 持续更新中...

#### 更新日志

- 2023-12-25 爬虫支持并发
- 2023-12-26 优化代码，修复BUG
- 2024-01-05 解析数据改为使用parsel库
- 2024-01-16 更新spiders包

# 项目说明

- 轻量框架，支持中间件、检验等功能。用法与Scrapy、Feapder类似。

# Python解释器

- python3.10+

# 如何使用pader？

#### 使用WeakSpider

```python
from loguru import logger

import pader


class TestSpider(pader.WeakSpider):
    start_urls = ['https://www.baidu.com']

    def when_spider_start(self):
        print('爬虫开始了...')

    def when_spider_close(self):
        print('...爬虫结束了')

    def parse(self, request, response):
        lis = response.xpath('//ul[@id="hotsearch-content-wrapper"]/li')
        for li in lis:
            url = li.xpath('./a/@href').get()
            title = li.xpath('./a/span[last()]/text()').get()
            logger.success(title)
            logger.success(url)
            logger.info('\r')
            yield pader.Request(url, callback=self.parse_detail)

    def parse_detail(self, request, response):
        nodes = response.xpath('//div[@class="c-container"]//h3')
        for node in nodes:
            some = node.xpath('./a//text()').getall()
            title = ''.join(some)
            url = node.xpath('./a/@href').get()
            logger.success(title)
            logger.success(url)

    def middleware(self, request):
        request.mark = '百度首页' if request.callback.__name__ == 'parse' else '百度搜索页'
        logger.info('进入了中间件，已设置记号为{}'.format(request.mark))

    def validate(self, request, response):
        logger.warning('进入了校验，记号={}'.format(request.mark))


if __name__ == '__main__':
    TestSpider().run()

```

#### 使用QueueSpider

```python
import threading
import time

from loguru import logger

import pader


def t_name():
    return threading.current_thread().name


def show(request):
    logger.success("回调: {}  =>  线程: {}".format(request.callback.__name__, t_name()))


URL = "https://www.baidu.com/s?&wd=python3"


class TestSpider(pader.QueueSpider):
    def start_requests(self):
        for i in range(5):
            yield pader.Request(URL)

    def when_spider_start(self):
        logger.info('爬虫开始了...')

    def when_spider_close(self):
        logger.info('...爬虫结束了')

    def parse(self, request, response):
        show(request)
        for i in range(2):
            mark = 'parse-{}'.format(i + 1)
            yield pader.Request(URL, mark=mark, callback=self.parse_list)

    def parse_list(self, request, response):
        show(request)
        for i in range(3):
            mark = 'parse_list-{}'.format(i + 1)
            yield pader.Request(URL, mark=mark, callback=self.parse_detail)

    def parse_detail(self, request, response):
        show(request)

    def middleware(self, request):
        time.sleep(1)  # 睡眠1S方便看出并发效果


if __name__ == '__main__':
    TestSpider(speed=5, qsize=10).run()

```
