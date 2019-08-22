# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test_gui
   Description :
   Author :       
   date：          2019/8/20
-------------------------------------------------
   Change Activity:
                   2019/8/20:
-------------------------------------------------
"""
__author__ = 'Lyl'

import unittest
from gui import Controls, Layouts
import PySimpleGUI as Gui


class TestGui(unittest.TestCase):
    def setUp(self) -> None:
        print("test...")

    def tearDown(self) -> None:
        print("test done")

    def test_controls_empty(self):
        controls_instance = Controls()
        with self.assertRaises(AssertionError):
            controls = controls_instance.controls

    def test_layout_empty(self):
        layouts_instance = Layouts()
        with self.assertRaises(AssertionError):
            layouts = layouts_instance.layout

    def test_controls(self):
        controls_instance = Controls()
        with self.assertRaises(AssertionError):
            controls_instance.pack(None)
        controls_instance.pack(Gui.Text("hi"))

    def test_layout(self):
        layouts_instance = Layouts()
        with self.assertRaises(AssertionError):
            layouts_instance.pack(None)

        with self.assertRaises(AssertionError):
            layouts_instance.pack("hi")

        with self.assertRaises(AssertionError):
            layouts = layouts_instance.layout

        controls_instance = Controls()
        controls_instance.pack(Gui.Text("hi"))
        layouts_instance.pack(controls_instance)

        self.assertIsNotNone(layouts_instance.layout)

    def test_window(self):
        controls_isinstance = Controls()
        layouts_instance = Layouts()
        controls_isinstance.pack(Gui.Text("hi"))
        layouts_instance.pack(controls_isinstance)
        window = Gui.Window("test", layouts_instance.layout)
        event = window.Read()
        print(event)
        window.Close()


if __name__ == '__main__':
    unittest.main(verbosity=2)
