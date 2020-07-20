#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/04/21 22:28
# @Author  : Xu
# @Site    : https://xuccc.github.io/

from core.engine import AwdEngine

if __name__ == '__main__':
    c = AwdEngine('config.yml', True)
    c.init()
    c.load()
    c.run()
