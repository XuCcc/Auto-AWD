#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/04/12 17:12
# @Author  : Xu
# @Site    : https://xuccc.github.io/


class AwdError(Exception):
    pass


class ConfigSyntaxError(AwdError):
    pass


class ConfigFileError(AwdError):
    pass


class ServiceInitError(AwdError):
    pass
