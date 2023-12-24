# -*- coding: utf-8 -*-

from typing import Iterable

from pader.core.request import Request
from pader.core.response import Response


class Spider:
    start_urls = []

    def ready(self):
        """爬虫入口"""
        for url in self.start_urls:
            yield Request(url, callback=self.parse, middleware=self.middleware)

    def parse(self, request, response):
        """回调函数"""
        pass

    def middleware(self, request):
        """中间件，可以设置代理等"""
        pass

    def validate(self, request, response):
        """校验，返回False则放弃这个请求"""
        pass

    def when_spider_start(self):
        """爬虫开始"""
        pass

    def when_spider_end(self):
        """爬虫结束"""
        pass

    def run(self):
        self.when_spider_start()
        result = self.ready()
        self.deal_result(result)
        self.when_spider_end()

    def deal_result(self, result):
        if result is None:
            return
        if not isinstance(result, Iterable):
            return

        for request in result:
            if isinstance(request, Request):
                request.middleware = request.middleware or self.middleware
                request.middleware(request)

                _response = request.send()
                if not _response:
                    continue

                response = Response(_response)
                if self.validate(request, response) is False:
                    continue

                request.callback = request.callback or self.parse
                result = request.callback(request, response)
                self.deal_result(result)
