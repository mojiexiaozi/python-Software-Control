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
from log import Logger
import os
from software_init import Init

logger = Logger().get_logger(__name__)
software_config = Init().software_config


# ----------------------------------------------------
def get_pattern_from_name(name: str):
    pattern = r'<{0}>(.*?)</{0}>'.format(name)
    return re.compile(pattern, re.S)


def get_head_val_string(script_string: str):
    SCRIPT_HEAD_VAR_STRING = {
        'script_delay': "",
        'script_list': "",
        'script_index': "",
        'script_val1': "",
        'script_val2': "",
        'script_val3': "",
        'script_val4': "",
        'script_val5': "",
        'script_val6': "",
        'script_val7': "",
        'script_val8': "",
        'script_val9': "",
        'script_val10': ""
    }
    head = get_pattern_from_name("head").findall(script_string)[0]
    pattern = r"{0}[\s]*=[\s]*(.*)"

    get_dict = {}
    for var_string in SCRIPT_HEAD_VAR_STRING:
        find = re.findall(pattern.format(var_string), head)
        if find:
            get_dict[var_string] = find[0]
    # logger.info(get_dict)
    return get_dict


def get_script_string(script_string: str):
    script_strings = get_pattern_from_name("script").findall(script_string)
    # logger.info(script_strings)
    run_scripts = []
    for script_string in script_strings:
        # find all setting of script
        delay = re.findall(r"delay[\s]*=[\s]*([0-9]*)", script_string)
        if delay:
            delay = delay[0]
        else:
            delay = '1000'

        script_name = re.findall(r"script@(.*)", script_string)
        if script_name:
            script_name = script_name[0]
        else:
            logger.error("script name must be define")

        script_input_strings = re.findall(r"input@(.*)", script_string)
        script_inputs = []
        for script_input_string in script_input_strings:
            script_input = re.findall(r"[.]*>>[\s]*(.*)", script_input_string)
            if script_input:
                script_inputs.append(script_input[0])
            else:
                script_inputs.append("")

        run_script = {
            "delay": delay,
            "script_name": script_name,
            "script_inputs": script_inputs
        }
        run_scripts.append(run_script)
    # logger.info(run_scripts)
    return run_scripts


def get_script_setting(script_string: str):
    head = get_head_val_string(script_string)
    scripts = get_script_string(script_string)
    script_setting = {'head': head, 'scripts': scripts}
    logger.info(script_setting)
    return script_setting


if __name__ == '__main__':
    file_path = os.path.join(software_config.software_dir, "guideline.txt")
    print(file_path)
    with open(file_path, 'r') as f:
        test = f.read()
    get_script_setting(test)
    pattern = re.compile(r'<{0}>.*</{0}>'.format('script'), re.S)
    print(test)
    print(pattern.findall(test))
