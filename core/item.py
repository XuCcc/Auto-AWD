#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/04/12 18:19
# @Author  : Xu
# @Site    : https://xuccc.github.io/

from typing import Callable, Tuple

from core.data import Status, Payload


class Item(object):
    def __init__(self, ):
        self._status = Status.TBD
        self.message = ''

    @property
    def status(self) -> bool:
        return Status.SUCCESS == self._status

    @property
    def result(self):
        return self._status, self.message

    @result.setter
    def result(self, result: Tuple):
        self._status, self.message = result


class FuncItem(Item):
    def __init__(self, func: Callable[[str], str]):
        super(FuncItem, self).__init__()
        self.func = func

    def run(self, ip) -> (bool, str):
        return self.func(ip)


class FlagItem(Item):
    def __init__(self, value):
        super(FlagItem, self).__init__()
        self.value = value


class ItemStream(Item):
    flag: FlagItem
    func: FuncItem

    def __init__(self, r: int, ip='127.0.0.1', payload: Payload = None, challenge: str = None):
        super(ItemStream, self).__init__()
        self.round = r
        self.ip = ip
        self.payload = payload
        if payload is not None:
            self.set_func(payload.func)
            self.challenge = payload.challenge
        else:
            self.challenge = challenge or ''

    def set_flag(self, value):
        self.flag = FlagItem(value)

    def set_func(self, func: Callable[[str], str]):
        self.func = FuncItem(func)

    def has_flag(self):
        return hasattr(self, 'flag')

    def has_func(self):
        return hasattr(self, 'func')
