#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/04/12 20:33
# @Author  : Xu
# @Site    : https://xuccc.github.io/

import re

from core.config import AttackParser
from core.const import Status
from core.item import ItemStream
from core.piper.basePiper import Piper


class FuncHandler(Piper):
    name = 'funcPiper'

    def __init__(self, config: AttackParser):
        self._config = config
        self.regx = re.compile(config.regx)

    def find_flag(self, string):
        m = self.regx.search(string)
        if not m:
            return False, ''
        return True, m.group(0)

    def process(self, item: ItemStream):
        if not item.has_func():
            return
        try:
            result, msg = item.func.run(item.ip)
        except Exception as e:
            item.func.result = (Status.ERROR, str(e))
        else:
            if not item.payload.flag:
                item.func.result = (Status.SUCCESS, msg) if result else (Status.FAIL, msg)
                return
            result, flag = self.find_flag(msg)
            if not result:
                item.func.result = (Status.FAIL, msg)
                return
            item.func.result = (Status.SUCCESS, msg)
            item.set_flag(flag)
