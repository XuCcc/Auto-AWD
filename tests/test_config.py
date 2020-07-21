#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/04/12 17:29
# @Author  : Xu
# @Site    : https://xuccc.github.io/

import pytest
from unittest import mock
from core.config import ParserUtil, ChallengeParser


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


def test_ip_port_parse():
    c = ChallengeParser({
        'ips': '172.18.0.1~5',
        'include': '172.18.0.8',
        'exclude': '172.18.0.4',
        'port': [
            8080,
            9099
        ]
    })
    assert c.ports == [8080, 9099]
    assert c.ips == ['172.18.0.1', '172.18.0.2', '172.18.0.3', '172.18.0.5', '172.18.0.8']


def test_ip_parse(config):
    assert config.challenges.ips == ['172.18.0.1',
                                     '172.18.0.2',
                                     '172.18.0.3',
                                     ]


def test_challenge_parse(config):
    assert config.challenges.ports == [8080, 8081, 9099]


def test_next_round_time_calc(config):
    with mock.patch('core.config.TimeParser.round', new_callable=mock.PropertyMock) as m:
        m.return_value = 3
        assert config.time.next_round_time == '08:20'