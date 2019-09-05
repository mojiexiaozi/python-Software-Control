#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
----------------------------------------------------
@Project      :    CASI003
@File         :   main_interface.py
@Time         :   2019/9/2 9:09
@Author       :   kimi
@Version      :   1.0
@Contact      :   15651838825@163.com
@License      :   (C)Copyright 2018-2019, CASI
@Desc         :   None
-----------------------------------------------------
"""

# ---------------------------------------------------
# module import
import re

# ----------------------------------------------------
# script variable
script_delay = 1000
script_list = range(10)
script_index = 0
script_var1 = 0
script_var2 = 0
script_var3 = 0
script_var4 = 0
script_var5 = 0
script_var6 = 0
script_var7 = 0
script_var8 = 0
script_var9 = 0
script_var10 = 0

delay = 1000

SCRIPT_VAR = {
    'script_delay': "",
    'script_list': "",
    'script_index': "",
    'script_var1': "",
    'script_var2': "",
    'script_var3': "",
    'script_var4': "",
    'script_var5': "",
    'script_var6': "",
    'script_var7': "",
    'script_var8': "",
    'script_var9': "",
    'script_var10': "",
    'delay': ""
}


def get_pattern_from_name(name: str):
    pattern = r'<{0}>(.*?)</{0}>'.format(name)
    return re.compile(pattern, re.S)


def get_head(script: str):
    head = get_pattern_from_name("head").findall(script)[0]
    pattern = r"{0}[\s]*=[\s]*(.*)"
    # print(head)
    for var in SCRIPT_VAR:
        SCRIPT_VAR[var] = re.findall(pattern.format(var), head)

    for var in SCRIPT_VAR:
        if SCRIPT_VAR[var]:
            try:
                value = eval(SCRIPT_VAR[var][0])
                SCRIPT_VAR[var] = value
            except NameError as e:
                print(e)
    # print(SCRIPT_VAR)


def update_script_value():
    global script_delay
    global script_list
    global script_index
    global script_var1
    global script_var2
    global script_var3
    global script_var4
    global script_var5
    global script_var6
    global script_var7
    global script_var8
    global script_var9
    global script_var10
    global delay

    script_delay = SCRIPT_VAR['script_delay']
    script_list = SCRIPT_VAR['script_list']
    script_index = SCRIPT_VAR["script_index"]
    delay = SCRIPT_VAR["delay"]

    script_var1 = SCRIPT_VAR["script_var1"]
    script_var2 = SCRIPT_VAR["script_var2"]
    script_var3 = SCRIPT_VAR["script_var3"]
    script_var4 = SCRIPT_VAR["script_var4"]
    script_var5 = SCRIPT_VAR["script_var5"]
    script_var6 = SCRIPT_VAR["script_var6"]
    script_var7 = SCRIPT_VAR["script_var7"]
    script_var8 = SCRIPT_VAR["script_var8"]
    script_var9 = SCRIPT_VAR["script_var9"]
    script_var10 = SCRIPT_VAR["script_var10"]


if __name__ == '__main__':
    with open('guideline.txt', 'r') as f:
        test = f.read()
    get_head(test)
    update_script_value()

    print("script val 1: {0}".format(script_var1))
    print("script val 2: {0}".format(script_var2))
    print("script val 3: {0}".format(script_var3))
    print("script val 4: {0}".format(script_var4))
    print("script val 5: {0}".format(script_var5))
    print("script val 6: {0}".format(script_var6))
    print("script val 7: {0}".format(script_var7))
    print("script val 8: {0}".format(script_var8))
    print("script val 9: {0}".format(script_var9))
    print("script val 10: {0}".format(script_var10))
    print("delay : {0}".format(delay))
    print("script : {0}".format(script_delay))
    print("script list : {0}".format(script_list))
    print("script index : {0}".format(script_index))
