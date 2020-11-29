#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/04/17 21:15
# @Author  : Xu
# @Site    : https://xuccc.github.io/

import os
from pony.orm import *

from core import ROOT_PATH
from core.log import Log

db = Database()


class FuncInfo(db.Entity):
    id = PrimaryKey(int, auto=True)
    round = Optional(int)
    message = Optional(str, nullable=True)
    status = Optional(bool)
    name = Required(str)
    ip = Required(str)
    flag = Optional('FlagInfo')


class FlagInfo(db.Entity):
    id = PrimaryKey(int, auto=True)
    round = Required(int)
    value = Required(str, unique=True)
    status = Optional(bool)
    message = Optional(str)
    func = Optional(FuncInfo)


def init_database(path):
    dbPath = os.path.join(ROOT_PATH, path)
    if os.path.exists(path):
        db.bind(provider='sqlite', filename=dbPath)
        db.generate_mapping()
        Log.app.success('load database: ' + dbPath)
    else:
        db.bind(provider='sqlite', filename=dbPath, create_db=True)
        db.generate_mapping(create_tables=True)
        Log.app.info('create database: ' + dbPath)
