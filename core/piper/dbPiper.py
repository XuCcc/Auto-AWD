#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/04/13 22:45
# @Author  : Xu
# @Site    : https://xuccc.github.io/

from core.db import db_session, FuncInfo, FlagInfo
from core.item import ItemStream
from core.piper.basePiper import Piper


class DbPiper(Piper):
    def process(self, item: ItemStream):
        with db_session:
            if item.has_func():
                funcinfo = FuncInfo(
                    round=item.round,
                    message='' if item.func.status else item.func.message,
                    status=item.func.status,
                    name=item.payload.name,
                    port=item.payload.port,
                )
            if item.has_flag():
                flaginfo = FlagInfo(
                    round=item.round,
                    value=item.flag.value,
                    status=item.flag.status,
                    message='' if item.flag.status else item.flag.message
                )
            if item.has_func() & item.has_flag():
                funcinfo.flag = flaginfo
