# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     script_save
   Description :
   Author :       
   date：          2019/8/23
-------------------------------------------------
   Change Activity:
                   2019/8/23:
-------------------------------------------------
"""
__author__ = 'Lyl'

from software_init import Init
import yaml
import os
from datetime import datetime

software_config = Init().software_config
os.chdir(software_config.software_dir)


class SaveEvent(object):
    @staticmethod
    def save_to_yaml_file(event_dict_list):
        assert isinstance(event_dict_list, list)
        if event_dict_list:
            assert isinstance(event_dict_list[0], dict)

            script_dir = software_config.scripts_dir
            os.chdir(script_dir)
            script_name = "{0}.yaml".format(datetime.now().strftime("%Y%m%d_%H%M%S"))

            with open(script_name, 'w') as file_ref:
                yaml.safe_dump(event_dict_list, file_ref, encoding='utf-8', allow_unicode=True)
                print("save...")
