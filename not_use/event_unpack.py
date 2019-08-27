# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     event_unpack
   Description :
   Author :       
   date：          2019/8/14
-------------------------------------------------
   Change Activity:
                   2019/8/14:
-------------------------------------------------
"""
__author__ = 'Lyl'

from software_init import Init
import yaml

software_init = Init()


class LoadFromYaml(object):
    @staticmethod
    def save_load():
        with open(software_init.default_record_file, 'r') as events_file_ref:
            print("events loading...")
            events = yaml.safe_load(events_file_ref)
            print("events load done")
            return events


class Unpack(object):
    def __init__(self):
        self._events = LoadFromYaml().save_load()

    @property
    def events(self):
        return self._events

    def unpack(self, event_dict_list):
        assert isinstance(event_dict_list, list) and isinstance(event_dict_list[0], dict)
        self._events = event_dict_list


if __name__ == '__main__':
    Unpack()
