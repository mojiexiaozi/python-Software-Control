#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@File    :   test_window.py
@Time    :   2019/08/28 18:33:54
@Author  :   MasterLin
@Version :   1.0
@Contact :   15651838825@163.com
@License :   (C)Copyright 2018-2019, CASI
@Desc    :   None
"""

# here put the import lib

from pynput_record import Window


class TestWindow(object):
    def test_window(self):
        window = Window()
        print(window.window)


if __name__ == "__main__":
    TestWindow().test_window()
