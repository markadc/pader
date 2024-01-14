# -*- coding: utf-8 -*-

from typing import Iterable

from pader.core.request import Request
from pader.core.response import Response


class Spider:
    start_urls = []

    def start_requests(self):
        """爬虫入口"""
        for url in self.start_urls:
            yield Request(url)

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

    def when_spider_close(self):
        """爬虫结束"""
        pass

    def run(self):
        self.when_spider_start()
        result = self.start_requests()
        self.deal_result(result)
        self.when_spider_close()

    def set_safe_request(self, request: Request):
        request.middleware = request.middleware or self.middleware
        request.callback = request.callback or self.parse

    def deal_result(self, result):
        if result is None:
            return
        if not isinstance(result, Iterable):
            return

        for request in result:
            if isinstance(request, Request):
                self.set_safe_request(request)

                request.middleware(request)
                response = Response(request.send())
                if self.validate(request, response) is False:
                    continue

                result = request.callback(request, response)
                self.deal_result(result)
