#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/04/14 21:35
# @Author  : Xu
# @Site    : https://xuccc.github.io/

from colorama import Fore

from core.log import Log
from core.item import ItemStream
from core.piper.basePiper import Piper


class LogPiper(Piper):
    name = 'logPiper'

    def __init__(self):
        self._log = Log.app

    def process(self, item: ItemStream):
        msg = ''
        if (item.payload is not None) & hasattr(item, 'func'):
            if item.func.status:
                msg = f'{item.payload.name}@{item.ip}:{item.payload.port} run {Fore.GREEN}success, {Fore.RESET}'
            else:
                msg = f'{item.payload.name}@{item.ip}:{item.payload.port} run {Fore.RED}fail, {Fore.RESET}{item.func.message}'

        if hasattr(item, 'flag'):
            if item.flag.status:
                msg += f'submit success {Fore.GREEN}{item.flag.value}'
            else:
                msg += f'submit fail {Fore.RED}{item.flag.value}, {Fore.RESET}{item.flag.message}'
        self._log.info(msg)
