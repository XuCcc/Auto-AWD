#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/04/14 21:35
# @Author  : Xu
# @Site    : https://xuccc.github.io/

from colorama import Fore, Style

from core.log import Log
from core.item import ItemStream
from core.piper.basePiper import Piper


class LogPiper(Piper):
    name = 'logPiper'

    def __init__(self, debug: bool):
        self._log = Log.app
        self._debug = debug

    def process(self, item: ItemStream):
        msg = ''
        if (item.payload is not None) & hasattr(item, 'func'):
            if item.func.status:
                msg = f'{item.payload.challenge} {item.payload.name}@{Fore.GREEN}{item.ip}{Fore.RESET} run success, '
            else:
                reason = item.func.message if self._debug else item.func.message[:255]
                msg = f'{item.payload.challenge} {item.payload.name}@{Fore.RED}{item.ip}{Fore.RESET} run fail, ' \
                      f'{Style.DIM}{reason}'

        if hasattr(item, 'flag'):
            if item.flag.status:
                msg += f'submit success {Fore.GREEN}{item.flag.value}'
            else:
                reason = item.flag.message if self._debug else item.flag.message[:64]
                msg += f'submit fail {Fore.RED}{item.flag.value}, {Fore.RESET} {Style.DIM}{reason}'

        self._log.info(msg)
