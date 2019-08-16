# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test_software_init
   Description :
   Author :       
   date：          2019/8/16
-------------------------------------------------
   Change Activity:
                   2019/8/16:
-------------------------------------------------
"""
__author__ = 'Lyl'
import unittest
from software_init import Init


class TestSoftwareInit(unittest.TestCase):
    def test_load(self):
        software_config = Init()

        self.assertEqual(software_config.default_record_file, "pynput_events.yaml")
        self.assertNotEqual(software_config.default_record_file, "pynput_events")
        self.assertIsInstance(software_config.logging_config, dict)

    def test_init_reload(self):
        software_config = Init()
        software_config.load_config()

        self.assertEqual(software_config.default_record_file, "pynput_events.yaml")
        self.assertIsInstance(software_config.logging_config, dict)

    def test_singleton(self):
        config_one = Init()
        config_other = Init()
        self.assertEqual(config_one, config_other)


if __name__ == '__main__':
    unittest.main(verbosity=2)
