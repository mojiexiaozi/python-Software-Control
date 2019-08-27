# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test_message_split
   Description :
   Auth or :
   date：          2019/8/23
-------------------------------------------------
   Change Activity:
                   2019/8/23:
-------------------------------------------------
"""
__author__ = 'Lyl'
import re
import os

message = 'test1\ntest2\ntest3\ndone.\n\n'

print(re.split(pattern="\n", string=message))
print(os.getcwd())
print(os.path.isdir('log'))
