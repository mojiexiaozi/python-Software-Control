#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   script_save.py
@Time    :   2019/08/28 09:30:48
@Author  :   MsterLin
@Version :   1.0
@Contact :   15651838825@163.com
@License :   (C)Copyright 2018-2019, CASIA
@Desc    :   None
'''

# here put the import lib


from software_init import Init
import yaml
import os
from datetime import datetime
from log import Logger

software_config = Init().software_config
logger = Logger().get_logger(__name__)


class SaveEvent(object):
    """ Save script """
    @staticmethod
    def save_to_yaml_file(event_dict_list, file_name=None):
        assert isinstance(event_dict_list, list)

        if event_dict_list:
            assert isinstance(event_dict_list[0], dict)

            script_dir = software_config.scripts_dir
            os.chdir(software_config.software_dir)

            logger.info("software dir:%s" % software_config.software_dir)
            os.chdir(script_dir)

            if file_name is None:
                file_name = "{0}.yaml".format(
                    datetime.now().strftime("%Y%m%d_%H%M%S"))

            with open(file_name, 'w') as file_ref:
                script = {"script": event_dict_list}
                yaml.safe_dump(script,
                               file_ref,
                               encoding='utf-8',
                               allow_unicode=True)
                print("save...")
