#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/04/15 22:18
# @Author  : Xu
# @Site    : https://xuccc.github.io/

import pytest
from unittest.mock import MagicMock

from core.item import ItemStream
from core.const import Status
from core.piper.pipeline import Pipeline
from core.piper import FlagPiper, DbPiper


@pytest.fixture()
def pipeline(config):
    p = Pipeline(config)
    p.build()
    p.delete(DbPiper.name)
    return p


def test_item_process_good_func_find_flag_submit_fail(pipeline, payload):
    item = pipeline.do(ItemStream(1, payload=payload))
    assert item.has_func()
    assert item.has_flag()
    assert item.func.status
    assert not item.flag.status


def test_item_process_good_func_find_no_flag(pipeline, payload):
    payload.func = MagicMock(return_value='1')
    item = pipeline.do(ItemStream(1, payload=payload))
    assert item.has_func()
    assert not item.func.status
    assert item.func._status == Status.FAIL
    assert item.func.message == '1'
    assert not item.has_flag()


def test_item_process_bad_func(pipeline, payload):
    payload.func = MagicMock(side_effect=KeyError)
    item = pipeline.do(ItemStream(1, payload=payload))
    assert item.has_func()
    assert item.func._status == Status.ERROR
    assert not item.func.status
    assert not item.has_flag()


def test_item_process_good_func_submit_success(config, pipeline, payload):
    config.platform.success_text = ['submit ok']
    FlagPiper._parse_shell_output = MagicMock(return_value=(True, "{'result':'submit ok'}"))
    item = pipeline.do(ItemStream(1, payload=payload))
    assert item.has_flag()
    assert item.flag.status
