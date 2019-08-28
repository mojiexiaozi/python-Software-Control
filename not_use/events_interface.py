#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   events_interface.py
@Time    :   2019/08/28 09:13:53
@Author  :   MsterLin
@Version :   1.0
@Contact :   15651838825@163.com
@License :   (C)Copyright 2018-2019, CASIA
@Desc    :   Interface of events extrator
'''

# here put the import lib

__author__ = 'Lyl'

import PySimpleGUI as Gui
from gui import Controls, Layouts
from extract_input_message import LaunchExtractor
import os
from software_init import Init

software_config = Init().software_config


class EventsInterface(object):
    def __init__(self):
        self._gui = None
        self.design_gui()

    def design_gui(self):
        layouts = Layouts()

        controls = Controls()
        font = ("Helvetica", 18)
        controls.pack(
            Gui.Text('events', size=(40, 1), key="__EVENTS__", font=font))
        layouts.pack(controls)

        controls = Controls()
        controls.pack(
            Gui.Multiline(size=(88, 20), key="__EVENTS_MESSAGE__", font=font))
        layouts.pack(controls)

        controls.empty()
        button_size = (5, 1)
        controls.pack(Gui.Button('OK', key="__OK__", size=button_size))
        controls.pack(Gui.Button("Cancel", key="__CANCEL__", size=button_size))
        controls.pack(
            Gui.Button("Load", key="__LOAD_EVENTS__", size=button_size))
        layouts.pack(controls)

        self._gui = Gui.Window("Events Review", layouts.layout)

    def run(self):
        assert isinstance(self._gui, Gui.Window)
        while True:
            event, value = self._gui.Read()
            if event is None or event == "__CANCEL__":
                break
            elif event == "__LOAD_EVENTS__":
                initialdir = os.path.join(software_config.software_dir,
                                          software_config.scripts_dir)
                print(initialdir)
                file_name = Gui.filedialog.askopenfilename(
                    initialdir=initialdir,
                    title="please choose a events file",
                    defaultextension="yaml",
                    filetypes=[("default", ".yaml"), ("events txt", ".txt")])
                # with open(file_name, 'r') as file_ref:
                #     events = yaml.safe_load(file_ref)
                #     # print(events)
                #     self._gui.Element("__EVENTS_MESSAGE__").Update(events)
                user_input_message = LaunchExtractor().do()
                print(user_input_message)
                self._gui.Element("__EVENTS_MESSAGE__").Update(
                    user_input_message)
            else:
                print("event: {0} value: {1}".format(event, value))


if __name__ == '__main__':
    gui = EventsInterface()
    gui.run()
