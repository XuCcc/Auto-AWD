#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/04/19 21:32
# @Author  : Xu
# @Site    : https://xuccc.github.io/

import abc
from threading import Thread

from core.log import Log
from core.utils import SingletonType


class BaseService(Thread, metaclass=SingletonType):
    serviceName = 'BaseService'
    log = Log.app

    @property
    @abc.abstractmethod
    def status(self):
        return ''
