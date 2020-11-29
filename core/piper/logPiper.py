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
        debug_infos = ''
        if (item.payload is not None) & hasattr(item, 'func'):
            if item.func.status:
                msg = f'{item.payload.challenge} {item.payload.name}@{Fore.GREEN}{item.ip}{Fore.RESET} run success, '
            else:
                msg = f'{item.payload.challenge} {item.payload.name}@{Fore.RED}{item.ip}{Fore.RESET} run fail'
                debug_infos += item.func.message

        if hasattr(item, 'flag'):
            if item.flag.status:
                msg += f'submit success {Fore.GREEN}{item.flag.value}'
            else:
                msg += f'submit fail {Fore.RED}{item.flag.value}'

        self._log.info(msg)
        self._log.debug(debug_infos)
