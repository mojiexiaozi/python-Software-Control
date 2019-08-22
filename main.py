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

from queue import Queue

from interface_event import LaunchMainInterface


class Main(object):
    def __init__(self):
        pass

    @staticmethod
    def run():
        LaunchMainInterface().start()


if __name__ == '__main__':
    Main().run()

