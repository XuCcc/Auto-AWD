#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/04/21 22:06
# @Author  : Xu
# @Site    : https://xuccc.github.io/

import os
import threading
import importlib.util


def load_py_script(module: str, path):
    if not os.path.exists(path):
        raise ValueError(f'{path} is not exists')
    spec = importlib.util.spec_from_file_location(module, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class SingletonType(type):
    _instance_lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            with SingletonType._instance_lock:
                if not hasattr(cls, "_instance"):
                    cls._instance = super(SingletonType, cls).__call__(*args, **kwargs)
        return cls._instance
