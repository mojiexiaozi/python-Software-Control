# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test_log
   Description :
   Author :
   date：          2019/8/16
-------------------------------------------------
   Change Activity:
                   2019/8/16:
-------------------------------------------------
"""
__author__ = 'Lyl'

from log import Logger
import unittest


class TestLog(unittest.TestCase):
    def test_logger_create(self):
        logger = Logger().get_logger(__name__)
        self.assertEqual(logger.name, __name__)
        self.assertLogs(logger)

    def test_warning(self):
        logger = Logger().get_logger(__name__)
        logger.warning("test-warning")

    def test_debug(self):
        logger = Logger().get_logger(__name__)
        logger.debug("test-debug")

    def test_error(self):
        logger = Logger().get_logger(__name__)
        logger.error("test-error")

    def test_info(self):
        logger = Logger().get_logger(__name__)
        logger.info("test-info")


if __name__ == '__main__':
    unittest.main(verbosity=2)
