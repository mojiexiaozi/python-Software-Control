from time import sleep
from multiprocessing import Process
import asyncio
import time
from queue import Queue

name = "界面事件虚类"
length = 50

print('# ' + '-' * length + ' #')
name_len = len(name)
length_left = int(length / 2) - int(name_len / 2)
length_right = length - length_left - name_len
print('# ' + ' ' * length_left + name + ' ' * length_right + ' #')
print('# ' + '-' * length + ' #')


class ProcessTest(Process):
    def run(self):
        for i in range(100):
            print("hello-{0}".format(i))
            sleep(1)


async def say_after(delay, what):
    await asyncio.sleep(delay)
    print(what)


async def main():
    task1 = asyncio.create_task(say_after(1, 'hello'))
    task2 = asyncio.create_task(say_after(1, 'world'))

    print(f"started at {time.strftime('%X')}")

    await task1
    await task2


class Consumer(object):
    def __init__(self, q):
        assert isinstance(q, Queue)
        self.q = q

    def task(self):
        while True:
            self.q.put("hello")
            time.sleep(1)


class Producer(object):
    def __init__(self, q):
        assert isinstance(q, Queue)
        self.q = q

    def task(self):
        while True:
            print(self.q.get())


async def consumer(q):
    c = Consumer(q)
    c.task()


async def producer(q):
    p = Producer(q)
    p.task()


async def test():
    q = Queue()
    task1 = asyncio.create_task(consumer(q))
    task2 = asyncio.create_task(producer(q))

    await task1
    await task2


