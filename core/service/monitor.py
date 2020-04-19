#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/04/15 21:39
# @Author  : Xu
# @Site    : https://xuccc.github.io/

import os
import glob
import queue
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from core.service import BaseService
from core.config import AttackParser
from core.const import PayloadData


class PayloadMonitor(BaseService, Observer):
    serviceName = 'PayloadFileMonitor'
    payloadQueue = queue.Queue()
    payloadDict = {}

    @classmethod
    def load_payload(cls, path) -> PayloadData:
        try:
            pd = PayloadData.load(path)
        except AttributeError as e:
            PayloadMonitor.log.warning(f'{path} missing attribute: {str(e).split(" ")[-1]}')
        except Exception as e:
            PayloadMonitor.log.warning(f'load {path} error: {e}')
        else:
            PayloadMonitor.payloadDict.update({pd.name: pd})
            PayloadMonitor.payloadQueue.put(pd)
            return pd
        return None

    @property
    def status(self):
        return ';'.join([str(p) for p in self.payloadDict.values()])

    class PayloadEventHandler(FileSystemEventHandler):
        # save file modify time to avoid run modify event twice: https://github.com/gorakhargosh/watchdog/issues/93
        mtime_cache = set()

        def on_created(self, event: FileSystemEvent):
            if event.is_directory or not event.src_path.endswith('py'):
                return
            PayloadMonitor.log.info(f'find new payload: {event.src_path}')

        def on_modified(self, event: FileSystemEvent):
            if event.is_directory or not event.src_path.endswith('py'):
                return

            mtime = os.stat(event.src_path).st_mtime
            if mtime in self.mtime_cache:
                return
            self.mtime_cache.add(mtime)
            if PayloadMonitor.load_payload(event.src_path):
                PayloadMonitor.log.info('update payload: ' + event.src_path)

        def on_deleted(self, event: FileSystemEvent):
            if event.is_directory or not event.src_path.endswith('py'):
                return
            filename = os.path.basename(event.src_path)
            if filename in PayloadMonitor.payloadDict:
                PayloadMonitor.payloadDict.pop(filename)
                PayloadMonitor.log.debug(f'remove payload: {event.src_path}')

    def __init__(self, config: AttackParser):
        self.dir = config.dir
        self.log.info('payload file monitor dir: ' + self.dir)
        super(PayloadMonitor, self).__init__(1)

        self.schedule(PayloadMonitor.PayloadEventHandler(), self.dir, True)

    @classmethod
    def get(cls) -> PayloadData:
        return cls.payloadQueue.get()

    @classmethod
    def clear(cls):
        PayloadMonitor.PayloadEventHandler.mtime_cache.clear()
        while not cls.payloadQueue.empty():
            cls.payloadQueue.get_nowait()
        for _, p in cls.payloadDict.items():
            cls.payloadQueue.put(p)

    def loads(self):
        for abs_path in glob.glob(f'{self.dir}/*.py'):
            if self.load_payload(abs_path):
                self.log.success('find payload: ' + abs_path)

    def __str__(self):
        return f'{self.serviceName} payload dir: {self.dir}'
