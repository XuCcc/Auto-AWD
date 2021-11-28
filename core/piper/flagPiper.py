#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/04/12 22:44
# @Author  : Xu
# @Site    : https://xuccc.github.io/

import requests
import subprocess
import traceback

from core.data import Status
from core.item import ItemStream
from core.piper.basePiper import Piper
from core.config import PlatformParser


class FlagPiper(Piper):
    name = 'flagPiper'

    def __init__(self, config: PlatformParser):
        self._config = config

    # TODO: retry when timeout/50x
    def submit_flag(self, flag) -> (bool, str):
        if self._config.isCurl:
            r, msg = self._parse_shell_output(self._config.curl.format(flag=flag))
        else:
            r, msg = self._parse_request_output(flag)
        if not r:
            return False, msg

        if not self._config.success_text:
            return True, msg
        for text in self._config.success_text:
            if text in msg:
                return True, msg
        return False, msg

    def _parse_shell_output(self, cmd: str) -> (bool, str):
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

    def _parse_request_output(self, flag) -> (bool, str):
        try:
            rep: requests.Response = self._config.py(flag)
        except:
            return False, traceback.format_exc()
        else:
            if not isinstance(rep, requests.Response):
                return False, \
                       f"[platform.python] {self._config.data.get('python')} return value is not requests.Response"
            if rep.status_code != 200:
                return False, rep.reason
            return True, rep.text

    def process(self, item: ItemStream):
        if not item.has_flag():
            return

        try:
            r, msg = self.submit_flag(item.flag.value)
        except:
            item.flag.result = (Status.ERROR, traceback.format_exc())
        else:
            item.flag.result = (Status.FAIL, msg) if not r else (Status.SUCCESS, msg)
