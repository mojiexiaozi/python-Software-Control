#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   main.py
@Time    :   2019/08/29 09:32:02
@Author  :   MasterLin
@Version :   1.0
@Contact :   15651838825@163.com
@License :   (C)Copyright 2018-2019, CASI
@Desc    :   None
"""

# here put the import lib


from interface_event import LaunchMainInterface
from log import Logger


class Main(object):
    def __init__(self):
        self._logger = Logger().get_logger()
        self._logger.info("Main class create")

    def __del__(self):
        self._logger.info("Main class release")

    def run(self):
        self._logger.info("Main thread running")

        main_launcher = LaunchMainInterface()
        main_launcher.start()
        main_launcher.join()

        self._logger.info("Main thread run done")


if __name__ == '__main__':
    Main().run()
