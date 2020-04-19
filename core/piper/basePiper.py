#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/04/12 20:16
# @Author  : Xu
# @Site    : https://xuccc.github.io/

import abc
from core.item import ItemStream


class Piper(object):
    name = 'basePiper'

    @abc.abstractmethod
    def process(self, item: ItemStream):
        pass
