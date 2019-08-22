# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     process_learn
   Description :
   Author :
   date：          2019/8/22
-------------------------------------------------
   Change Activity:
                   2019/8/22:
-------------------------------------------------
"""
__author__ = 'Lyl'

from multiprocessing import Process
from time import sleep


class Task(Process):
    def __init__(self, name):
        super().__init__()
        self._name = name

    def run(self):
        while True:
            print("{0} is running".format(self._name))
            sleep(1)


if __name__ == "__main__":
    task1 = Task("thread1")
    task2 = Task("thread2")
    task1.start()
    sleep(0.5)
    task2.start()
    task1.join()
    task2.join()
