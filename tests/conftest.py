#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/04/12 17:23
# @Author  : Xu
# @Site    : https://xuccc.github.io/

import pytest

from core.config import AppConfig
from core.const import PayloadData

YAML = """
time:
  start: '8:00'
  end: '23:00'
  interval: 5
platform:
  url: http://127.0.0.1:8000/submit
  curl: curl http://127.0.0.1:8000/submit?flag={flag}&token=fc067281e151a0b929f5056f22298490
team:
  ips: 172.18.0.1~10
#  include: 172.18.0.64
#  exclude: 172.18.0.4
attack:
  regx: \w{32}
  dir: %s
#  thread: 8
challenge:
  8080: web
  9099: pwn"""

GOOD_PAYLOAD = """
import uuid


class Payload(object):
    port = 8080
    once = True

    @staticmethod
    def run(ip):
        return 'flag is here: ' + uuid.uuid4().hex
"""


@pytest.fixture()
def config(tmpdir):
    c = tmpdir.join('config.yml')
    c.write(YAML % tmpdir)
    return AppConfig(c)


@pytest.fixture()
def payload(tmpdir, config):
    PayloadData.load_config(config.challenge)
    p = tmpdir.join('good.py')
    p.write(GOOD_PAYLOAD)
    return PayloadData.load(p)
