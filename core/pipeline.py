#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/04/14 22:10
# @Author  : Xu
# @Site    : https://xuccc.github.io/

import queue
from concurrent.futures import ThreadPoolExecutor, Future
from typing import List, Dict
from threading import Thread

from core.config import AppConfig
from core.item import ItemStream
from core.piper import *


class Pipeline(object):
    queue = queue.Queue()
    pipers: Dict[str, Piper] = {}
    tasks: List[Future] = []

    def __init__(self, config: AppConfig):
        self.ips = config.team.ips
        self.challenges = config.challenge

        self._config = config
        self._pool = ThreadPoolExecutor(config.attack.thread)

    def build(self):
        self.add(
            FuncHandler(self._config.attack)
        ).add(
            FlagPiper(self._config.platform)
        ).add(
            LogPiper(self._config.challenge)
        ).add(
            DbPiper()
        )

    @classmethod
    def add(cls, piper: Piper):
        cls.pipers.update({
            piper.name: piper
        })
        return cls

    @classmethod
    def get(cls, name):
        return cls.pipers.get(name)

    @classmethod
    def send(cls, item: ItemStream):
        cls.queue.put(item)

    @classmethod
    def clear(cls):
        cls.tasks.clear()
        while not cls.queue.empty():
            cls.queue.get_nowait()

    def do(self, item: ItemStream) -> ItemStream:
        for piper in self.pipers.values():
            piper.process(item)
        return item

    def run(self):
        while True:
            item: ItemStream = self.queue.get()
            f = self._pool.submit(self.do, item)
            self.tasks.append(f)

    def start(self):
        thread = Thread(
            target=self.run,
            name='PipelineListener',
            daemon=True
        )
        thread.start()
        return thread
