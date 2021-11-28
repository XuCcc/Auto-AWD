#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/04/14 22:10
# @Author  : Xu
# @Site    : https://xuccc.github.io/

import queue
import time
from concurrent.futures import ThreadPoolExecutor, Future
from threading import Thread
from typing import Dict

from core.config import AppConfig
from core.item import ItemStream
from core.piper import *


class Pipeline(object):
    name = 'PipelineListener'
    queue = queue.Queue()
    _pipers: Dict[str, Piper] = {}
    _tasks: Dict[ItemStream, Future] = {}

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
            LogPiper(self._config.debug)
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
        for item in list(cls._tasks.keys()):
            if cls._tasks.get(item).cancel() or cls._tasks.get(item).done():
                cls._tasks.pop(item)
        while not cls.queue.empty():
            cls.queue.get_nowait()

    @classmethod
    def cancel(cls, payload: str):
        c = 0
        for item in list(cls._tasks.keys()):
            if item.payload.name == payload:
                if cls._tasks.get(item).cancel():
                    cls._tasks.pop(item)
                    c += 1
        return c

    def do(self, item: ItemStream) -> ItemStream:
        for piper in self._pipers.values():
            piper.process(item)
        return item

    def run(self):
        while True:
            try:
                item: ItemStream = self.queue.get(False, timeout=3)
            except queue.Empty:
                continue
            future = self._pool.submit(self.do, item)
            self._tasks[item] = future

            if self._config.platform.interval:
                time.sleep(self._config.platform.interval / 1000)

    def start(self):
        thread = Thread(
            target=self.run,
            name=self.name,
            daemon=True
        )
        thread.start()

    @property
    def progress(self):
        r = 0
        d = 0
        a = 0
        for i in self._tasks.values():
            a += 1
            if i.running():
                r += 1
            elif i.done():
                d += 1
        return r, d, a
