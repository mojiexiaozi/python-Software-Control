# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     main.py
   Description :
   Author :
   date：          2019/8/20
-------------------------------------------------
   Change Activity:
                   2019/8/20:
-------------------------------------------------
"""
__author__ = 'Lyl'


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

