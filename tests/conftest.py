#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/04/12 17:23
# @Author  : Xu
# @Site    : https://xuccc.github.io/

import pytest

from core.config import AppConfig


@pytest.fixture()
def config(tmpdir):
    c = tmpdir.join('config.yml')
    with open('config.template.yml') as f:
        c.write(f.read().format(dir=tmpdir,flag='{flag}'))
    return AppConfig(c)
