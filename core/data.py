#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/04/12 18:16
# @Author  : Xu
# @Site    : https://xuccc.github.io/

import os
from enum import IntEnum

from core.utils import load_py_script


class Status(IntEnum):
    SUCCESS = 1
    FAIL = 2
    ERROR = 9
    TBD = 0


class Payload(object):
    def __init__(self, filename, cls):
        self.name = filename
        self.challenge = cls.challenge
        self.func = cls.run
        self.flag = cls.flag

    @staticmethod
    def load(path):
        filename = os.path.basename(path)
        payload = load_py_script('awd.core.payload', path)
        return Payload(filename, payload.Payload)

    def __str__(self):
        return f'{self.name} {self.challenge}'
