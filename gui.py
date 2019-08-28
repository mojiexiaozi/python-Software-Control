#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   gui.py
@Time    :   2019/08/27 22:33:11
@Author  :   MasterLin
@Version :   1.0
@Contact :   15651838825@163.com
@License :   (C)Copyright 2018-2019, CASIA
@Desc    :   None
'''

# here put the import lib

__author__ = 'Lyl'


class Controls(object):
    def __init__(self):
        self._controls = []

    @property
    def controls(self):
        assert self._controls.__len__() >= 1
        return self._controls

    def pack(self, control):
        assert control is not None
        self._controls.append(control)

    def empty(self):
        self._controls = []


class Layouts(object):
    def __init__(self):
        self._layouts = []

    @property
    def layout(self):
        assert self._layouts.__len__() >= 1  # 必须非空
        return self._layouts

    def pack(self, controls):
        assert isinstance(controls, Controls)
        self._layouts.append(controls.controls)
