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

from core.utils import loadPy
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
                self.py: Callable[[str], requests.Response] = loadPy('awd.core.submit', data.get('python')).submit
            except AttributeError:
                raise ConfigFileError(f'[platform.python] miss function: submit(flag)')
            except SyntaxError as e:
                raise ConfigSyntaxError(f'[platform.python] file syntax error: {e}')

        self.timeout: int = data.get('timeout', 3)
        self.success_text = data.get('success_text', '')


class ChallengeParser(BaseParser):
    def __init__(self, data):
        super(ChallengeParser, self).__init__(data)
        self.raw: Dict[str, str] = data.get('raw')

        if not self.raw:
            self.ips = ParserUtil.ip(data['ips'], data.get('include', ''), data.get('exclude', ''))
            self.ports = data['port']
            self.challenges: Dict[str, List[int]] = self.parse_ip_port()
        else:
            self.challenges = self.parse_raw()
            self.ips = list(self.challenges.keys())
            ports = set()
            for ps in self.challenges.values():
                for p in ps:
                    ports.add(p)
            self.ports = list(ports)

    def parse_raw(self):
        mapping = {}
        for ip in self.raw.keys():
            if isinstance(self.raw.get(ip), str):
                mapping[ip] = [int(port) for port in self.raw.get(ip).split(',')]
            elif isinstance(self.raw.get(ip), int):
                mapping[ip] = [self.raw.get(ip)]
        return mapping

    def parse_ip_port(self):
        mapping = {}
        for ip in self.ips:
            mapping[ip] = self.ports
        return mapping

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


class AppConfig(BaseParser):
    def __init__(self, config: str):
        if not os.path.exists(config):
            raise ConfigFileError(f'config file {config} not find')
        with open(config, 'r') as f:
            super(AppConfig, self).__init__(yaml.safe_load(f.read()))

        self.db = self.data.get('db', 'awd.db')
        self.debug = self.data.get('debug', False)
        self.time = TimeParser(self.data.get('time'))
        self.platform = PlatformParser(self.data.get('platform'))
        self.challenges = ChallengeParser(self.data.get('challenge'))
        self.plugins = PluginParser(self.data.get('plugin', {}))
        self.attack = AttackParser(self.data.get('attack', {}))
