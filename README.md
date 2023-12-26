# 轻量框架，支持中间件、检验等功能。用法与Scrapy、Feapder类似。

# 持续更新中...

- 爬虫支持并发（QueueSpider）2023-12-25

# python解释器

python3+

# 使用pader的示例

## 使用Spider

```python
from loguru import logger

import pader


class TestSpider(pader.Spider):
    start_urls = ['https://www.baidu.com']

    def when_spider_start(self):
        print('爬虫开始了...')

    def when_spider_end(self):
        print('...爬虫结束了')

    def parse(self, request, response):
        lis = response.xpath('//ul[@id="hotsearch-content-wrapper"]/li')
        for li in lis:
            url = li.xpath('./a/@href')[0]
            title = li.xpath('./a/span[last()]/text()')[0]
            logger.success(title)
            logger.success(url)
            logger.info('\r')
            yield pader.Request(url, callback=self.parse_detail)

    def parse_detail(self, request, response):
        nodes = response.xpath('//div[@class="c-container"]//h3')
        for node in nodes:
            some = node.xpath('./a//text()')
            title = ''.join(some)
            url = node.xpath('./a/@href')[0]
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
## 使用QueueSpider

```python
import threading
import time

from loguru import logger

import pader
from pader import Request
from pader.core.queue_spider import QueueSpider


def t_name():
    return threading.current_thread().name


def show(request: Request):
    logger.success("回调: {}  =>  线程: {}".format(request.callback.__name__, t_name()))


URL = "https://www.baidu.com/s?&wd=python3"


class TestSpider(QueueSpider):
    def start_requests(self):
        for i in range(5):
            yield pader.Request(URL)

    def when_spider_start(self):
        logger.info('爬虫开始了...')

    def when_spider_end(self):
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