# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     unit_test
   Description :
   Author :       kimi
   date：          2019/7/31
-------------------------------------------------
   Change Activity:
                   2019/7/31:
-------------------------------------------------
"""
__author__ = 'kimi'

import unittest
import playback


class TestPlayBack(unittest.TestCase):

    def test_motion(self):
        motions = playback.PlayBack().open_motion()
        self.assertIsInstance(motions, list)


if __name__ == '__main__':
    unittest.main()
