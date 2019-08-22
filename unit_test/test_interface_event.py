# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test_interface_event
   Description :
   Author :
   date：          2019/8/21
-------------------------------------------------
   Change Activity:
                   2019/8/21:
-------------------------------------------------
"""
__author__ = 'Lyl'

from interface_event import LaunchRecordInterface, LaunchPlaybackInterface, LaunchMainInterface

import unittest


class TestInterfaceEvent(unittest.TestCase):
    # def test_record(self):
    #     LaunchRecordInterface().start()
    #
    # def test_playback(self):
    #     LaunchPlaybackInterface().start()

    def test_main(self):
        LaunchMainInterface().start()


if __name__ == '__main__':
    unittest.main()
