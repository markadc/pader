# -*- coding: utf-8 -*-

class ResponseError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return '{}: {}'.format(self.__class__.__name__, self.msg)


class ResponseCodeError(ResponseError):
    pass


class ResponseTextError(ResponseError):
    pass


class RequestMethodError(ResponseError):
    pass
