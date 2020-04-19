#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/04/14 21:37
# @Author  : Xu
# @Site    : https://xuccc.github.io/

import sys
from loguru import logger


class Log(object):
    app = logger.bind(name='app')
    plugin = logger.bind(name='plugin')

    @classmethod
    def config(cls, debug):
        level = 'DEBUG' if debug else 'INFO'
        logger.remove(0)
        logger.add(sys.stdout,
                   level=level)
        logger.add('app.log',
                   filter=lambda record: record['extra'].get('name') == 'app',
                   level=level)
        logger.add('plugin.log',
                   filter=lambda record: record['extra'].get('name') == 'plugin',
                   level=level)
