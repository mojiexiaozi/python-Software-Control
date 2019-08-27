# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     test_software_init
   Description :
   Author :       
   date：          2019/8/16
-------------------------------------------------
   Change Activity:
                   2019/8/16:
-------------------------------------------------
"""
__author__ = 'Lyl'
import pytest
from software_init import Init, SoftwareConfig


software_config = Init().software_config


def test_load(self):
    assert isinstance(software_config, SoftwareConfig)
    print("using_script:{0}".format(software_config.using_script))
    print("scripts_dir:{0}".format(software_config.scripts_dir))
    print("log_dir:{0}".format(software_config.log_dir))
    print("logging_config:{0}".format(software_config.logging_config))
    print("software_dir:{0}".format(software_config.software_dir))


def test_dumps(self):
    software_config.dumps()


if __name__ == '__main__':
    pytest.main()
