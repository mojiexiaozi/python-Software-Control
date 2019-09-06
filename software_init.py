#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   software_init.py
@Time    :   2019/09/05 18:11:29
@Author  :   MasterLin
@Version :   1.0
@Contact :   15651838825@163.com
@License :   (C)Copyright 2018-2019, CASI
@Desc    :   None
"""

# here put the import lib
import yaml
import os
import sys

SOFTWARE_DIR = os.path.split(sys.argv[0])[0]
print(SOFTWARE_DIR)
CONFIG_FILE = "software_config.yaml"


# 实现单例模式
def singleton(cls):
    instances = {}

    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper


@singleton
class Init(object):
    """ Loading software setting from
        software_config.yaml type setting file
    """
    def __init__(self):
        self._software_config = SoftwareConfig()
        self.load_config()
        self.create_dir()
        print("system init done")  # ----------------------------------------

    @property
    def software_config(self):
        return self._software_config

    @staticmethod
    def _load_config():
        """ loading config from setting file """
        os.chdir(SOFTWARE_DIR)
        try:
            with open(CONFIG_FILE, 'r') as config_file_ref:
                config = yaml.safe_load(config_file_ref)
        except FileNotFoundError as e:
            print(e)
            raise FileExistsError("文件不存在")
        return config

    def create_dir(self):
        """ Create log and scripts dir if there are not found."""
        assert self.software_config is not None
        if not os.path.exists(self.software_config.log_dir):
            os.mkdir(self.software_config.log_dir)

        if not os.path.exists(self.software_config.scripts_dir):
            os.mkdir(self.software_config.scripts_dir)

    def load_config(self):
        """ Loading config from config dictionary """
        config = self._load_config()
        # --------------------------------------------------------
        # 配置文件解析
        try:
            self.software_config.using_script = config["using script"]
            self.software_config.scripts_dir = config["scripts dir"]
            self.software_config.log_dir = config["log dir"]
            self.software_config.logging_config = config["logging config"]
        except KeyError as e:
            print(e)
            raise UserWarning("setting file illegal")

        print("software config load done")


class SoftwareConfig(object):
    def __init__(self):
        """
        self._software_dir: 软件运行目录
        self._using_script: 使用中的脚本
        self._scripts_dir: 脚本目录
        self._logging_config：日志配置
        self._log_dir: 日志保存路径
        """
        self._software_dir = SOFTWARE_DIR
        self._using_script = None
        self._scripts_dir = None
        self._logging_config = None
        self._log_dir = None

    @property
    def software_dir(self):
        return self._software_dir

    @software_dir.setter
    def software_dir(self, software_dir):
        self._software_dir = software_dir

    @property
    def using_script(self):
        return self._using_script

    @using_script.setter
    def using_script(self, using_script):
        self._using_script = using_script

    @property
    def scripts_dir(self):
        return self._scripts_dir

    @scripts_dir.setter
    def scripts_dir(self, scripts_dir):
        self._scripts_dir = scripts_dir

    @property
    def logging_config(self):
        return self._logging_config

    @logging_config.setter
    def logging_config(self, logging_config):
        self._logging_config = logging_config

    @property
    def log_dir(self):
        return self._log_dir

    @log_dir.setter
    def log_dir(self, log_dir):
        self._log_dir = log_dir

    def dumps(self):
        config_dict = {
            "software dir": self.software_dir,
            "logging config": self.logging_config,
            "log dir": self.log_dir,
            "scripts dir": self.scripts_dir,
            "using script": self.using_script
        }
        # print(config_dict)
        os.chdir(SOFTWARE_DIR)
        with open(CONFIG_FILE, 'w') as config_file_ref:
            yaml.safe_dump(config_dict,
                           config_file_ref,
                           encoding='utf-8',
                           allow_unicode=True)


if __name__ == '__main__':
    software_config = Init().software_config
    print("using_script:{0}".format(software_config.using_script))
    print("scripts_dir:{0}".format(software_config.scripts_dir))
    print("log_dir:{0}".format(software_config.log_dir))
    print("logging_config:{0}".format(software_config.logging_config))
    print("software_dir:{0}".format(software_config.software_dir))
