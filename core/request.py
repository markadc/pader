# -*- coding: utf-8 -*-

from typing import Callable

import requests
from fake_useragent import UserAgent
from loguru import logger

from pader.core.exceptions import RequestMethodError, ResponseCodeError, ResponseTextError


def retry(func):
    def _retry(*args, **kwargs):
        url = args[0].url
        for _ in range(3):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    '''
                    URL         {}
                    ERROR       {}
                    '''.format(url, e)
                )
        logger.critical('Failed  ==>  {}'.format(url))

    return _retry


class Request:
    def __init__(
            self, url, headers=None, cookies=None, proxies=None,
            params=None, data=None, json=None,
            timeout=5, method='GET',
            callback: Callable = None, middleware: Callable = None, priority=None,
            codes=None, checker: Callable = None,
            **kwargs
    ):
        self.url = url
        self.headers = headers
        self.cookies = cookies
        self.proxies = proxies
        self.params = params
        self.data = data
        self.json = json
        self.timeout = timeout
        self.method = method

        self.callback = callback
        self.middleware = middleware
        self.priority = priority
        self.codes = codes
        self.checker = checker

        self.ua = UserAgent()

        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        return '<Request {}>'.format(self.url)

    def get_headers(self) -> dict:
        headers = {'User-Agent': self.ua.random}
        return headers

    @retry
    def send(self):
        self.headers = self.headers or self.get_headers()

        match self.method:
            case 'GET':
                response = requests.get(
                    self.url, headers=self.headers, proxies=self.proxies,
                    params=self.params,
                    timeout=self.timeout
                )
            case 'POST':
                response = requests.post(
                    self.url, headers=self.headers, proxies=self.proxies,
                    data=self.data, json=self.json,
                    timeout=self.timeout
                )
            case _:
                raise RequestMethodError('unsupported {}'.format(self.method))

        if self.codes and response.status_code not in self.codes:
            raise ResponseCodeError('{} not in {}'.format(response.status_code, self.codes))

        if self.checker and self.checker(self.url, response.text) is False:
            raise ResponseTextError('not ideal text')

        return response
