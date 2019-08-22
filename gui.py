# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     gui
   Description :
   Author :       
   date：          2019/8/7
-------------------------------------------------
   Change Activity:
                   2019/8/7:
-------------------------------------------------
"""
__author__ = 'Lyl'

import PySimpleGUI as Gui


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
