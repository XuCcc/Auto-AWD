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
    name = 'PipelineListener'
    queue = queue.Queue()
    _pipers: Dict[str, Piper] = {}
    _tasks: List[Future] = []

    def __init__(self, config: AppConfig):
        self.ips = config.challenges.ips
        self.challenges = config.challenges

        self._config = config
        self._pool = ThreadPoolExecutor(config.attack.thread)

    def build(self):
        self.add(
            FuncHandler(self._config.attack)
        ).add(
            FlagPiper(self._config.platform)
        ).add(
            LogPiper()
        ).add(
            DbPiper()
        )

    @classmethod
    def add(cls, piper: Piper):
        cls._pipers.update({
            piper.name: piper
        })
        return cls

    @classmethod
    def delete(cls, name):
        cls._pipers.pop(name)

    @classmethod
    def get(cls, name):
        return cls._pipers.get(name)

    @classmethod
    def send(cls, item: ItemStream):
        cls.queue.put(item)

    @classmethod
    def clear(cls):
        cls._tasks.clear()
        while not cls.queue.empty():
            cls.queue.get_nowait()

    def do(self, item: ItemStream) -> ItemStream:
        for piper in self._pipers.values():
            piper.process(item)
        return item

    def run(self):
        while True:
            item: ItemStream = self.queue.get()
            f = self._pool.submit(self.do, item)
            self._tasks.append(f)

    def start(self):
        thread = Thread(
            target=self.run,
            name=self.name,
            daemon=True
        )
        thread.start()

    @property
    def progress(self):
        done = [i for i in self._tasks if i.done()]
        return len(done), len(self._tasks)
