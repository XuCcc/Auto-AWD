#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/04/12 18:16
# @Author  : Xu
# @Site    : https://xuccc.github.io/

import os
from enum import IntEnum

from core.utils import loadPy


class Status(IntEnum):
    SUCCESS = 1
    FAIL = 2
    ERROR = 9
    TBD = 0


class PayloadData(object):
    def __init__(self, filename, cls):
        self.name = filename
        self.challenge = cls.challenge
        self.func = cls.run
        self.once = cls.once

    @staticmethod
    def load(path):
        filename = os.path.basename(path)
        payload = loadPy('awd.core.payload', path)
        return PayloadData(filename, payload.Payload)

    def __str__(self):
        return f'{self.name} {self.challenge}'
