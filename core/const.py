#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/04/12 18:16
# @Author  : Xu
# @Site    : https://xuccc.github.io/

import os
import importlib.util
from enum import IntEnum


class Status(IntEnum):
    SUCCESS = 1
    FAIL = 2
    ERROR = 9
    TBD = 0


class PayloadData(object):
    def __init__(self, filename, cls):
        self.name = filename
        self.port = cls.port
        self.func = cls.run
        self.once = cls.once

    @staticmethod
    def load(path):
        filename = os.path.basename(path)
        spec = importlib.util.spec_from_file_location('awd.core.payload', path)
        payload = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(payload)
        return PayloadData(filename, payload.Payload)

    def __str__(self):
        return f'{self.name} {self.port}'
