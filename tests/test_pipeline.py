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


def test_item_process_good_func_find_flag_submit_fail(pipeline, find_flag_payload):
    item = pipeline.do(ItemStream(1, payload=find_flag_payload))
    assert item.has_func()
    assert item.has_flag()
    assert item.func.status
    assert not item.flag.status


def test_item_process_good_func_find_no_flag(pipeline, find_flag_payload):
    find_flag_payload.func = MagicMock(return_value=(True, 'not flag'))
    item = pipeline.do(ItemStream(1, payload=find_flag_payload))
    assert item.has_func()
    assert not item.func.status
    assert item.func._status == Status.FAIL
    assert item.func.message == 'not flag'
    assert not item.has_flag()


def test_item_process_bad_func(pipeline, find_flag_payload):
    find_flag_payload.func = MagicMock(side_effect=KeyError)
    item = pipeline.do(ItemStream(1, payload=find_flag_payload))
    assert item.has_func()
    assert item.func._status == Status.ERROR
    assert not item.func.status
    assert not item.has_flag()


def test_item_process_good_func_submit_success(config, pipeline, find_flag_payload):
    config.platform.success_text = ['submit ok']
    FlagPiper._parse_shell_output = MagicMock(return_value=(True, "{'result':'submit ok'}"))
    item = pipeline.do(ItemStream(1, payload=find_flag_payload))
    assert item.has_flag()
    assert item.flag.status


def test_item_process_only_run(pipeline, only_run_payload):
    item = pipeline.do(ItemStream(1, payload=only_run_payload))
    assert item.has_func()
    assert item.func.status
    assert not hasattr(item, 'flag')
