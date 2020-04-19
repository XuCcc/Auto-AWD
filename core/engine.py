#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/04/15 22:55
# @Author  : Xu
# @Site    : https://xuccc.github.io/

import time
import sys
import schedule
from threading import Thread

from core.log import Log
from core.db import init_database
from core.const import PayloadData
from core.item import ItemStream
from core.config import AppConfig
from core.piper import FlagPiper
from core.pipeline import Pipeline
from core.service.monitor import PayloadMonitor


def schedule_run():
    while True:
        schedule.run_pending()
        time.sleep(1)


class AwdEngine(object):
    def __init__(self, path, debug=False):
        Log.config(debug)
        self._log = Log.app
        self._config = AppConfig(path)

        self.pipeline = Pipeline(self._config)
        self.services = {}

    @property
    def isBegin(self) -> bool:
        return True if self._config.time.round > 0 else False

    @property
    def pmonitor(self) -> PayloadMonitor:
        return self.services.get(PayloadMonitor.serviceName)

    def init(self):
        init_database(self._config.db)
        PayloadData.load_challenge_mapping(self._config.challenge)
        self.pipeline.build()

        self.services.update({
            PayloadMonitor.serviceName: PayloadMonitor(self._config.attack)
        })
        self.pmonitor.loads()

    def check(self):
        # check flag submit piper
        piper: FlagPiper = self.pipeline.get(FlagPiper.name)
        r, msg = piper.submit_flag('flag')
        if not r:
            self._log.error('submit test flag error: ' + msg)
        elif r and not self._config.platform.success_text:
            self._log.warning('[platform.success_text] is empty when submit flag successful')

    def refresh(self):
        # do some jobs every round
        self._log.debug('clear queue in pipeline')
        self.pipeline.clear()
        for name, service in self.services.items():
            service.clear()
            self._log.debug(f'clear {name} cache')

    def start(self):
        self.pipeline.start()
        self._log.info(f'{self.pipeline.name} is running')
        for name, service in self.services.items():
            service.start()
            self._log.info(f'{name} is running')

        schedule.every(self._config.time.interval).minutes.do(self.refresh).tag('refresh')
        Thread(target=schedule_run, daemon=True).start()

    def _run(self):
        while True:
            payload = self.pmonitor.get()
            r = self._config.time.round
            for ip in self._config.team:
                self.pipeline.send(ItemStream(r, ip, payload))

    def run(self):
        try:
            self._run()
        except KeyboardInterrupt:
            self._log.critical('exit')
            sys.exit(0)