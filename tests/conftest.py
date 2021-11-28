#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/04/12 17:23
# @Author  : Xu
# @Site    : https://xuccc.github.io/

import pytest

from core.config import AppConfig
from core.data import Payload

YAML = """
# db: awd.db
time:
  start: '8:00'
  interval: 5
platform:
 curl: curl  http://127.0.0.1:8000/submit?flag={flag}&token=fc067281e151a0b929f5056f22298490
  # python: submit.py
#  timeout: 3
#  success_text: ''
attack:
  regx: \w{32}
  dir: %s
#  thread: 8
challenge:
  raw:
    easyWeb:
      - 172.18.0.1
      - 172.18.0.2
    hardWeb:
      - 172.18.1.1
      - 172.18.1.2
"""

FIND_FLAG_PAYLOAD = """
import uuid
import random
import time


class Payload(object):
    challenge = 'easyWeb'
    flag = True

    @staticmethod
    def run(ip):
        time.sleep(random.randint(1, 3))
        return True, 'flag is here: ' + uuid.uuid4().hex
"""

ONLY_RUN_PAYLOAD = """
import uuid
import random
import time


class Payload(object):
    challenge = 'hardWeb'
    flag = False

    @staticmethod
    def run(ip):
        time.sleep(random.randint(1, 3))
        return True, 'attack success'


"""


@pytest.fixture()
def config(tmpdir):
    c = tmpdir.join('config.yml')
    c.write(YAML % tmpdir)
    AppConfig().load(c)
    return AppConfig()


@pytest.fixture()
def find_flag_payload(tmpdir, config):
    p = tmpdir.join('find_flag.py')
    p.write(FIND_FLAG_PAYLOAD)
    return Payload.load(p)


@pytest.fixture()
def only_run_payload(tmpdir, config):
    p = tmpdir.join('only_run.py')
    p.write(ONLY_RUN_PAYLOAD)
    return Payload.load(p)
