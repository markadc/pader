# -*- coding: utf-8 -*-

from pader.core.request import Request


class BaseSpider:
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

    def ensure_request(self, request: Request):
        """为请求设置默认属性"""
        request.middleware = request.middleware or self.middleware
        request.callback = request.callback or self.parse
