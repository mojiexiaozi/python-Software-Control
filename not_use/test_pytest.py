# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     pytest_learn
   Description :
   Author :
   date：          2019/8/23
-------------------------------------------------
   Change Activity:
                   2019/8/23:
-------------------------------------------------
"""
__author__ = 'Lyl'

import pytest


def func(x):
    return x + 1


def test_answer():
    assert func(3) == 5


def f():
    raise SystemExit(1)


def test_raise():
    with pytest.raises(SystemExit):
        f()


if __name__ == '__main__':
    pytest.main()
