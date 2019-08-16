# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     events_interface
   Description :
   Author :
   date：          2019/8/9
-------------------------------------------------
   Change Activity:
                   2019/8/9:
-------------------------------------------------
"""
__author__ = 'Lyl'


import PySimpleGUI as Gui

from gui import Controls, Layouts

from extract_input_message import LaunchExtractor


class EventsInterface(object):
    def __init__(self):
        self._gui = None
        self.design_gui()

    def design_gui(self):
        layouts = Layouts()

        controls = Controls()
        font = ("Helvetica", 18)
        controls.pack(Gui.Text('events', size=(40, 1), key="__EVENTS__", font=font))
        layouts.pack(controls)

        controls = Controls()
        controls.pack(Gui.Multiline(size=(88, 20), key="__EVENTS_MESSAGE__", font=font))
        layouts.pack(controls)

        controls.empty()
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
                file_name = Gui.filedialog.askopenfilename(initialdir="./",
                                                           title="please choose a events file",
                                                           defaultextension="yaml",
                                                           filetypes=[("default", ".yaml"), ("events txt", ".txt")])
                # with open(file_name, 'r') as file_ref:
                #     events = yaml.safe_load(file_ref)
                #     # print(events)
                #     self._gui.Element("__EVENTS_MESSAGE__").Update(events)
                user_input_message = LaunchExtractor().do()
                print(user_input_message)
                self._gui.Element("__EVENTS_MESSAGE__").Update(user_input_message)
            else:
                print("event: {0} value: {1}".format(event, value))


if __name__ == '__main__':
    gui = EventsInterface()
    gui.run()
