#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
----------------------------------------------------
@Project      :    CASI003
@File         :   create_exe.py
@Time         :   2019/9/11 11:53
@Author       :   kimi
@Version      :   1.0
@Contact      :   15651838825@163.com
@License      :   (C)Copyright 2018-2019, CASI
@Desc         :   None
-----------------------------------------------------
"""


# ---------------------------------------------------
# module import
import cairo
import rsvg

with open('../icon/main.svg', 'rb') as f:
    print(f.read())
    svg_image = Image.open(fp=f)
