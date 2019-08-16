# -*- coding:utf-8 -*-
"""
author:Lyl
date:2019-07-18
description: setting logging by yaml config file
"""

import logging
import logging.config

from software_init import Init

software_config = Init()


def singleton(cls):
    instances = {}

    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return wrapper


@singleton
class Logger(object):
    def __init__(self, default_level=logging.DEBUG):
        try:
            self._logger = logging.config.dictConfig(software_config.logging_config)
            logging.info("logging init done")
        except ValueError as e:
            print(e)
            self._logger = logging.basicConfig(level=default_level)
            logging.warning('logging init Failed')

    @staticmethod
    def get_logger(name=__name__):
        return logging.getLogger(name)


if __name__ == '__main__':
    logger = Logger().get_logger()
    logger.info("hello")
    logger = Logger().get_logger()
    logger.warning("warn")
