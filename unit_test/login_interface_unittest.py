# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     login_interface_unittest
   Description :
   Author :       
   date：          2019/8/7
-------------------------------------------------
   Change Activity:
                   2019/8/7:
-------------------------------------------------
"""
__author__ = 'Lyl'

from not_use.login_interface import LoginInterface
from PySimpleGUI import Window
import unittest


class LoginInterfaceUnittest(unittest.TestCase):
    def test_interface(self):
        login_interface = LoginInterface()
        login_interface.design_window()
        self.assertIsInstance(login_interface.window, Window)

        print(login_interface.run())


if __name__ == '__main__':
    unittest.main()
