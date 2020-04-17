#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/04/12 22:44
# @Author  : Xu
# @Site    : https://xuccc.github.io/


import subprocess

from core.const import Status
from core.item import ItemStream
from core.piper.basePiper import Piper
from core.config import PlatformParser


class FlagPiper(Piper):
    def __init__(self, config: PlatformParser):
        self._config = config

    def submit_flag(self, flag) -> (bool, str):
        r, msg = self._get_shell_result(self._config.curl.format(flag=flag))
        if not r:
            return r, msg
        return self._config.success_text in msg, msg

    def _get_shell_result(self, cmd: str) -> (bool, str):
        with subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE) as p:
            try:
                exitcode = p.wait(self._config.timeout)
                stdout, stderr = p.communicate()
            except:
                p.kill()
                return False, f'Timeout: {cmd}'
            else:
                if exitcode != 0:
                    return False, stderr.decode('utf-8')
                return True, stdout.decode('utf-8')

    def process(self, item: ItemStream):
        if not item.has_flag():
            return

        try:
            r, msg = self.submit_flag(item.flag.value)
        except Exception as e:
            item.flag.result = (Status.ERROR, e)
        else:
            item.flag.result = (Status.FAIL, msg) if not r else (Status.SUCCESS, msg)
