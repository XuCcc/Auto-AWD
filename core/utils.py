#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/04/21 22:06
# @Author  : Xu
# @Site    : https://xuccc.github.io/

import os
import importlib.util


def loadPy(module: str, path):
    if not os.path.exists(path):
        raise ValueError(f'{path} is not exists')
    spec = importlib.util.spec_from_file_location(module, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m
