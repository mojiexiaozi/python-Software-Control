# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     Application
   Description :
   Author :       Lyl
   date：          2019/8/1
-------------------------------------------------
   Change Activity:
                   2019/8/1:
-------------------------------------------------
"""
__author__ = 'Lyl'

import PySimpleGUI as Gui
from gui import Controls, Layouts


class LoginInterface(object):
    def __init__(self):
        self._layouts = Layouts()
        self._window = None

    @property
    def layouts(self):
        return self._layouts

    @property
    def window(self):
        return self._window

    def design_window(self):
        controls = Controls()
        controls.pack(Gui.Text('username'))
        controls.pack(Gui.Input('', size=(15, 1), key='username'))
        self._layouts.pack(controls)

        controls = Controls()
        controls.pack(Gui.Text('password'))
        controls.pack(Gui.Input('', size=(15, 1), key='password', password_char="*"))
        self._layouts.pack(controls)

        controls = Controls()
        controls.pack(Gui.Button('login'))
        controls.pack(Gui.Button('cancel'))
        self._layouts.pack(controls)

        self._window = Gui.Window('logging', self._layouts.layout)

    def run(self):
        while True:
            event, values = self._window.Read()  # 读取事件
            # print(event)
            # print(values)
            if event is None or event == 'Exit' or event == "cancel":
                self._window.Close()
                return None
            elif event == "login":
                self._window.Close()
                return values


