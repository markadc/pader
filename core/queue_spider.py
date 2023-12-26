# -*- coding: utf-8 -*-

import time
from concurrent.futures import ThreadPoolExecutor
from copy import copy
from queue import PriorityQueue
from typing import Iterable

from loguru import logger

from pader.core.request import Request
from pader.core.response import Response
from pader.core.spider import Spider


def safe(func):
    def _safe(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error('{}  ==>  {}'.format(func.__name__, e))

    return _safe


class QueueSpider(Spider):
    def __init__(self, qsize=10, speed=2):
        self.request_queue = RequestQueue(qsize=qsize)
        self.speed = speed
        self.__pool1 = ThreadPoolExecutor(max_workers=speed)
        self.__pool2 = ThreadPoolExecutor(max_workers=speed)
        self.__fs = []

    def ready(self):
        result = self.start_requests()
        self.join_queue(result)

    def run(self):
        # 爬虫开始
        self.when_spider_start()

        # 爬虫流程
        self.__pool1.submit(self.ready)
        for _ in range(self.speed):
            self.__pool1.submit(self.start_tasks)
        self.__pool1.shutdown()

        # 爬虫结束
        self.when_spider_end()

    def get_result(self, request: Request):
        """请求 ==> 中间件 ==> 响应 ==>  校验 ==> 回调"""
        request.middleware(request)
        _response = request.send()
        response = Response(_response)
        if self.validate(request, response) is False:
            return
        result = request.callback(request, response)
        return result

    def job(self, request: Request):
        """结果 ==> 队列"""
        result = self.get_result(request)
        self.join_queue(result)

    def job_is_done(self):
        for f in copy(self.__fs):
            if not f.done():
                return False
            try:
                self.__fs.remove(f)
            except:
                pass

        # 方式1
        # if len(self.__fs) == 0:
        #     return True

        # 方式2
        for i in range(3):
            time.sleep(1)
            if len(self.__fs) != 0:
                return False
        else:
            return True

    @safe
    def start_tasks(self):
        while True:
            if self.request_queue.is_empty() and self.job_is_done():
                break

            request = self.request_queue.get()
            if request:
                f = self.__pool2.submit(self.job, request)
                self.__fs.append(f)

    def join_queue(self, result):
        if result is None:
            return
        if not isinstance(result, Iterable):
            return
        for the in result:
            if isinstance(the, Request):
                self.set_safe_request(the)
                self.request_queue.add(the)


class RequestQueue:
    def __init__(self, qsize):
        self.pqueue = PriorityQueue(maxsize=qsize)

    def add(self, req: Request, force=True):
        req.priority = req.priority or time.time()
        item = req.priority, req
        if force:
            self.pqueue.queue.append(item)
        else:
            self.pqueue.put(item)

    def get(self) -> Request | None:
        try:
            priority, req = self.pqueue.get(timeout=1)
            return req
        except:
            return

    def is_empty(self):
        return self.pqueue.empty()

    def is_full(self):
        return self.pqueue.full()

    def qsize(self):
        return self.pqueue.qsize()

    def __str__(self):
        return "<qsize={}>".format(self.qsize())
