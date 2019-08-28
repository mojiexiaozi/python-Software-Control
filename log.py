#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   log.py
@Time    :   2019/08/28 09:11:34
@Author  :   MsterLin
@Version :   1.0
@Contact :   15651838825@163.com
@License :   (C)Copyright 2018-2019, CASIA
@Desc    :   setting logging by yaml config file
'''

# here put the import lib
import logging
import logging.config

from software_init import Init
import os

software_config = Init().software_config


def singleton(cls):
    instances = {}

    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper


@singleton
class Logger(object):
    """ Init logging through yaml setting """
    def __init__(self, default_level=logging.DEBUG):
        os.chdir(software_config.software_dir)
        os.chdir(software_config.log_dir)
        try:
            self._logger = logging.config.dictConfig(
                software_config.logging_config)
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
