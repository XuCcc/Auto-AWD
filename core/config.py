#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/04/12 17:12
# @Author  : Xu
# @Site    : https://xuccc.github.io/

from typing import List
import yaml
import re
import os
import time

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
        self.start = TimeParser.format_time(data.get('start', '00:00'))
        self.end = TimeParser.format_time(data.get('end', '23:59'))
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
        elif time.strftime('%H:%M', localtime) >= self.end:
            return -1
        else:
            h, m = map(lambda x: int(x), self.start.split(':'))
            return ((localtime.tm_hour - h) * 60 + (localtime.tm_min - m)) // self.interval

    @property
    def next_round_time(self):
        r = self.round
        if r <= 0:
            return self.end

        seconds = ((r + 1) * self.interval) * 60
        start = time.mktime(time.strptime(self.start, '%H:%M'))
        return time.strftime('%H:%M', time.localtime(start + seconds))


class PlatformParser(BaseParser):
    def __init__(self, data):
        super(PlatformParser, self).__init__(data)
        self.url: str = data['url']
        if not self.url.startswith(('http://', 'https://')):
            raise ConfigSyntaxError("platform.url should start with 'http://' or 'https://'")
        self.curl: str = data['curl']
        if '{flag}' not in self.curl:
            raise ConfigSyntaxError("platform.curl missing formatter: {flag}")

        self.timeout: int = data.get('timeout', 3)
        self.success_text = data.get('success_text', '')


class TeamParser(BaseParser):
    def __init__(self, data):
        super(TeamParser, self).__init__(data)
        self.ips = ParserUtil.ip(data['ips'], data.get('include', ''), data.get('exclude', ''))

    def __iter__(self):
        return iter(self.ips)

    def __len__(self):
        return len(self.ips)


class AttackParser(BaseParser):
    def __init__(self, data):
        super(AttackParser, self).__init__(data)
        self.dir = data.get('dir', 'payloads')
        if not os.path.exists(self.dir):
            raise ConfigFileError(f'payload dir:{self.dir} not find')
        self.thread: int = data.get('thread', 8)
        self.regx = data['regx']


class ChallengeParser(BaseParser):
    def __init__(self, data):
        super(ChallengeParser, self).__init__(data)
        self._challenges = data or {0: 'default'}

    def __iter__(self):
        return iter(self._challenges.items())

    def __contains__(self, item):
        return item in self._challenges

    def __len__(self):
        return len(self._challenges)

    def get(self, port: int):
        return self._challenges.get(port, 'default')


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

        self.time = TimeParser(self.data.get('time'))
        self.platform = PlatformParser(self.data.get('platform'))
        self.team = TeamParser(self.data.get('team'))
        self.challenge = ChallengeParser(self.data.get('challenge', {}))
        self.plugins = PluginParser(self.data.get('plugin', {}))
        self.attack = AttackParser(self.data.get('attack', {}))
