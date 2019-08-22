# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     asc_learn
   Description :
   Author :       
   date：          2019/8/22
-------------------------------------------------
   Change Activity:
                   2019/8/22:
-------------------------------------------------
"""
__author__ = 'Lyl'

import asyncio


count = 0


async def task(delay=0.1, name="task1"):
    global count
    while True:
        if count == 100:
            print()
            print("{0} is running, count:{1}".format(name, count))
            break

        count += 1
        print("#", end='')
        await asyncio.sleep(delay)
        await asyncio.sleep(delay)


async def main():
    task1 = asyncio.create_task(task(0.005))
    task2 = asyncio.create_task(task(0.005, "task2"))

    await task1
    await task2

if __name__ == '__main__':
    asyncio.run(main())
