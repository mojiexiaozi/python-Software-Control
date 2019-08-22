# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test_interface
   Description :
   Author :       
   date：          2019/8/21
-------------------------------------------------
   Change Activity:
                   2019/8/21:
-------------------------------------------------
"""
__author__ = 'Lyl'

import unittest

from interface import MainInterface, PlaybackInterface, RecordingInterface, ReviewInterface


class TestInterface(unittest.TestCase):
    def test_main_interface(self):
        main_interface = MainInterface()
        main_interface.load_window()
        win = main_interface.window

        event, event_message = win.Read()
        print(event, event_message)
        win.Close()

    def test_playback_interface(self):
        playback_interface = PlaybackInterface()
        playback_interface.load_window()
        win = playback_interface.window

        event, event_message = win.Read()
        print(event, event_message)
        win.Close()

    def test_record_interface(self):
        record_interface = RecordingInterface()
        record_interface.load_window()
        win = record_interface.window

        event, event_message = win.Read()
        print(event, event_message)
        win.Close()

    def test_review_interface(self):
        interface = ReviewInterface()
        interface.load_window()
        win = interface.window

        event, event_message = win.Read()
        print(event, event_message)
        win.Close()


if __name__ == '__main__':
    unittest.main()
