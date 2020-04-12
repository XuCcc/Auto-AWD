#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/04/12 17:29
# @Author  : Xu
# @Site    : https://xuccc.github.io/

import pytest

from core.config import ParserUtil


@pytest.mark.parametrize('ips,include,exclude,result',
                         [
                             ('127.0.0.1~3', '127.0.0.128', '127.0.0.2',
                              ['127.0.0.1', '127.0.0.3', '127.0.0.128']),
                             ('127.0.0.1~3', '127.0.0.128', '',
                              ['127.0.0.1', '127.0.0.2', '127.0.0.3', '127.0.0.128']),
                             ('127.0.0.1~3', '', '127.0.0.2',
                              ['127.0.0.1', '127.0.0.3']),
                             ('127.0.0.1~3', '', '',
                              ['127.0.0.1', '127.0.0.2', '127.0.0.3'])
                         ])
def test_ip(ips, include, exclude, result):
    assert ParserUtil.ip(ips, include, exclude) == result


def test_ip_parse(config):
    assert config.team.ips == ['172.18.0.1',
                               '172.18.0.2',
                               '172.18.0.3',
                               '172.18.0.4',
                               '172.18.0.5',
                               '172.18.0.6',
                               '172.18.0.7',
                               '172.18.0.8',
                               '172.18.0.9',
                               '172.18.0.10']


def test_challenge_parse(config):
    assert 8080 in config.challenge
    assert 9999 not in config.challenge


def test_challenge_get(config):
    assert config.challenge.get(8080) == 'web'
