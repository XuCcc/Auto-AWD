#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/04/21 22:28
# @Author  : Xu
# @Site    : https://xuccc.github.io/

from colorama import Fore
from core.engine import AwdEngine

__version__ = '0.1.0'
__banner__ = f'''
********************************************************
*     _         _             ___        ______  
*    / \  _   _| |_ ___      / \ \      / /  _ \ 
*   / _ \| | | | __/ _ \    / _ \ \ /\ / /| | | |
*  / ___ \ |_| | || (_) |  / ___ \ V  V / | |_| |
* /_/   \_\__,_|\__\___/  /_/   \_\_/\_/  |____/ 
*
*                                Version: {Fore.YELLOW}{__version__}{Fore.RESET} by Xu
*                                {Fore.LIGHTGREEN_EX}~~~~~~Good Luck~~~~~~{Fore.RESET}
********************************************************
'''

if __name__ == '__main__':
    print(__banner__)
    c = AwdEngine('config.template')
    c.init()
    c.load()
    c.run()
