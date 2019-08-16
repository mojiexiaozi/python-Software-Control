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
from os.path import split, join
# from os import mkdir


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
        self._default_record_file = None
        self._logging_config = None
        self._software_config = None

        self.load_config()

    @property
    def software_config(self):
        assert self._software_config is not None
        return self._software_config

    @property
    def logging_config(self):
        assert self._logging_config is not None
        return self._logging_config

    @property
    def default_record_file(self):
        assert self._default_record_file is not None
        return self._default_record_file

    # def create_log_dir(self):
    #     assert self._logging_config is not None
    #     log_dir = join(split(__file__)[0], 'log')
    #     if not exists(log_dir):
    #         mkdir(log_dir)

    def _load_config(self):
        try:
            config_file_dir, _ = split(__file__)
            config_file = join(config_file_dir, "software_config.yaml")
            with open(config_file, 'r') as config_file_ref:
                self._software_config = yaml.safe_load(config_file_ref)
        except FileExistsError or FileNotFoundError as e:
            print(e)
            raise UserWarning("system init failed: software_config.yaml missing")

    def load_config(self):
        self._load_config()
        self._load_default_record_file()
        self._load_logging_config_file()
        print("system init done")

    def _load_default_record_file(self):
        try:
            self._default_record_file = self._software_config["default record file"]
        except KeyError as e:
            print(e)
            raise UserWarning("system init failed:  type error of config file")

    def _load_logging_config_file(self):
        try:
            self._logging_config = self._software_config["logging config"]
        except KeyError as e:
            print(e)
            raise UserWarning("system init failed:  type error of config file")
