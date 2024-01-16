# -*- coding: utf-8 -*-

from typing import Iterable

from pader.core.request import Request
from pader.core.response import Response
from pader.core.spiders.base_spider import BaseSpider


class WeakSpider(BaseSpider):
    def run(self):
        self.when_spider_start()
        result = self.start_requests()
        self.deal_result(result)
        self.when_spider_close()

    def deal_result(self, result):
        if result is None:
            return
        if not isinstance(result, Iterable):
            return

        for request in result:
            if isinstance(request, Request):
                self.ensure_request(request)

                request.middleware(request)
                response = Response(request.send())
                if self.validate(request, response) is False:
                    continue

                result = request.callback(request, response)
                self.deal_result(result)
