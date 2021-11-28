#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/04/12 17:12
# @Author  : Xu
# @Site    : https://xuccc.github.io/

import requests
from typing import List, Dict, Callable
import yaml
import re
import os
import time

from core.utils import load_py_script, SingletonType
from core.exception import ConfigSyntaxError, ConfigFileError


class ParserUtil(object):
    @staticmethod
    def ip(ips: str, include: str = '', exclude: str = '') -> List[str]:
        a, b, c, start, end = re.split(r'[.~]', ips)
        result = ['.'.join((a, b, c, str(i))) for i in range(int(start), int(end) + 1)]
        result += [i for i in include.split(',') if i]
        result = [i for i in result if i not in exclude.split(',')]
        return result


class BaseParser(object):
    def __init__(self, data: dict):
        self.data = data


class TimeParser(BaseParser):
    def __init__(self, data):
        super(TimeParser, self).__init__(data)
        self.date = time.strftime('%Y-%m-%d', time.localtime())
        self.start = TimeParser.format_time(data.get('start', '00:00'))
        self.interval: int = data['interval']

    @staticmethod
    def format_time(t) -> str:
        try:
            return time.strftime('%H:%M', time.strptime(t, '%H:%M'))
        except ValueError as e:
            raise ConfigSyntaxError(f'time format error: {e}')

    @property
    def round(self):
        localtime = time.localtime()
        if time.strftime('%H:%M', localtime) < self.start:
            return 0
        else:
            h, m = map(lambda x: int(x), self.start.split(':'))
            return ((localtime.tm_hour - h) * 60 + (localtime.tm_min - m)) // self.interval

    @property
    def next_round_time(self):
        r = self.round
        seconds = ((r + 1) * self.interval) * 60
        start = time.mktime(time.strptime(f'{self.date} {self.start}', '%Y-%m-%d %H:%M'))
        return time.strftime('%H:%M', time.localtime(start + seconds))


class PlatformParser(BaseParser):
    def __init__(self, data):
        super(PlatformParser, self).__init__(data)
        self.isCurl = True
        if 'curl' in data and 'python' in data:
            raise ConfigSyntaxError('[platform.curl] or [platform.python] not both')

        if 'curl' in data:
            self.curl: str = data.get('curl')
            if '{flag}' not in self.curl:
                raise ConfigSyntaxError("[platform.curl] missing formatter: {flag}")
        elif 'python' in data:
            self.isCurl = False
            try:
                self.py: Callable[[str], requests.Response] = load_py_script('awd.core.submit',
                                                                             data.get('python')).submit
            except AttributeError:
                raise ConfigFileError(f'[platform.python] miss function: submit(flag)')
            except SyntaxError as e:
                raise ConfigSyntaxError(f'[platform.python] file syntax error: {e}')

        self.timeout: int = data.get('timeout', 3)
        self.success_text = data.get('success_text', [])
        self.interval: int = data.get('interval', 0)


class ChallengeParser(BaseParser):
    def __init__(self, data):
        super(ChallengeParser, self).__init__(data)
        self.challenges: Dict[str, List[str]] = {}
        self.ips = set()

        if (raw := data.get('raw')) is not None:
            self.challenges = raw
        else:
            for challenge, ip_data in data.items():
                self.challenges[challenge] = ParserUtil.ip(ip_data['ips'],
                                                           ip_data.get('include', ''), ip_data.get('exclude', ''))

        for ips in self.challenges.values():
            for ip in ips:
                self.ips.add(ip)

    def __iter__(self):
        return iter(self.challenges.items())


class AttackParser(BaseParser):
    def __init__(self, data):
        super(AttackParser, self).__init__(data)
        self.dir = data.get('dir', 'payloads')
        if not os.path.exists(self.dir):
            raise ConfigFileError(f'payload dir:{self.dir} not find')
        self.thread: int = data.get('thread', 8)
        self.regx = data['regx']


class PluginParser(BaseParser):
    def __init__(self, data):
        super(PluginParser, self).__init__(data)
        self.plugins = data


class AppConfig(metaclass=SingletonType):
    data: dict
    db: str
    debug: bool
    time: TimeParser
    platform: PlatformParser
    challenges: ChallengeParser
    plugins: PluginParser
    attack: AttackParser

    def load(self, config: str):
        if not os.path.exists(config):
            raise ConfigFileError(f'config file {config} not find')
        with open(config, 'r') as f:
            self.data = yaml.safe_load(f.read())

        self.db = self.data.get('db', 'awd.db')
        self.debug = self.data.get('debug', False)
        self.time = TimeParser(self.data.get('time'))
        self.platform = PlatformParser(self.data.get('platform'))
        self.challenges = ChallengeParser(self.data.get('challenge'))
        self.plugins = PluginParser(self.data.get('plugin', {}))
        self.attack = AttackParser(self.data.get('attack', {}))
