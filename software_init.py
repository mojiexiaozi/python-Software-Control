# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     software_init
   Description :
   Author :
   date：          2019/8/13
-------------------------------------------------
   Change Activity:
                   2019/8/13:
-------------------------------------------------
"""
__author__ = 'Lyl'

import yaml
import os


SOFTWARE_DIR = os.path.split(__file__)[0]
CONFIG_FILE = "software_config.yaml"
os.chdir(SOFTWARE_DIR)


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
    def __init__(self):
        self._software_config = SoftwareConfig()
        self.load_config()
        print("system init done")
        # ----------------------------------------

    @property
    def software_config(self):
        return self._software_config

    def create_dir(self):
        assert self._logging_config is not None
        if not os.path.exists(self._log_dir):
            os.mkdir(self._log_dir)

        if not os.path.exists(self._scripts_dir):
            os.mkdir(self._scripts_dir)

    @staticmethod`
    def _load_config():
        try:
            with open(CONFIG_FILE, 'r') as config_file_ref:
                config = yaml.safe_load(config_file_ref)
        except (FileExistsError or FileNotFoundError) as e:
            print(e)
            raise UserWarning("system init failed: software_config.yaml missing")
        return config

    def load_config(self):
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
            raise UserWarning(
                "system init failed: software_config.yaml missing")

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
        config_dict = {"software dir": self.software_dir,
                       "logging config": self.logging_config,
                       "log dir": self.log_dir,
                       "scripts dir": self.scripts_dir,
                       "using script": self.using_script}
        print(config_dict)

        with open(CONFIG_FILE, 'w') as config_file_ref:
            yaml.safe_dump(config_dict, config_file_ref, encoding='utf-8', allow_unicode=True)


if __name__ == '__main__':
    software_config = Init().software_config
    print("using_script:{0}".format(software_config.using_script))
    print("scripts_dir:{0}".format(software_config.scripts_dir))
    print("log_dir:{0}".format(software_config.log_dir))
    print("logging_config:{0}".format(software_config.logging_config))
    print("software_dir:{0}".format(software_config.software_dir))
