# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     interface
   Description :
   Author :
   date：          2019/8/20
-------------------------------------------------
   Change Activity:
                   2019/8/20:
-------------------------------------------------
"""
__author__ = 'Lyl'
from gui import Controls, Layouts
import PySimpleGUI as Gui
from software_init import Init

Gui.ChangeLookAndFeel('GreenTan')


# -------------------------------------------------- #
#                         界面虚类                    #
# -------------------------------------------------- #
class Interface(object):
    def __init__(self, interface_title="Demo"):
        super().__init__()
        self._layouts = Layouts()
        self._window = None
        self.window_title = interface_title

    @property
    def window(self):
        assert isinstance(self._window, Gui.Window)
        return self._window

    def set_window(self, window):
        assert isinstance(window, Gui.Window)
        self._window = window

    def design_window(self):
        pass

    def load_window(self):
        self.design_window()
        self._window = Gui.Window(self.window_title,
                                  self._layouts.layout,
                                  alpha_channel=0.8)
        self._window.DisableClose = False

    @property
    def layouts(self):
        return self._layouts

    def set_layouts(self, layouts):
        assert isinstance(layouts, Layouts)
        self._layouts = layouts


# -------------------------------------------------- #
#                         主界面                      #
# -------------------------------------------------- #
class MainInterface(Interface):
    def design_window(self):
        controls = Controls()

        menu_def = [['File', ['Open', 'Save', 'Exit', 'Properties']],
                    ['Edit', ['Paste', 'Undo']],
                    ['Help', 'About...']]

        controls.pack(Gui.Menu(menu_definition=menu_def, tearoff=False, key="__MENU__"))

        self.layouts.pack(controls)

        controls.empty()
        controls.pack(
            Gui.Text(text="using script:{0}".format(Init().software_config.using_script),
                     key='__MESSAGE__',
                     size=[40, 1],
                     font=("Helvetica", 18)))
        self.layouts.pack(controls)

        controls.empty()
        # controls.pack(Gui.T(' ' * 20))
        controls.pack(
            Gui.Button('record',
                       key='__RECORD__',
                       font=("Helvetica", 18),
                       size=(12, 1)))
        controls.pack(
            Gui.Button('playback',
                       key="__PLAYBACK__",
                       font=("Helvetica", 18),
                       size=(12, 1)))
        controls.pack(
            Gui.Button('review',
                       key="__REVIEW__",
                       font=("Helvetica", 18),
                       size=(12, 1)))
        controls.pack(
            Gui.Button('quit',
                       key="__QUIT__",
                       font=("Helvetica", 18),
                       size=(12, 1)))
        self.layouts.pack(controls)


# -------------------------------------------------- #
#                       脚本回放界面                   #
# -------------------------------------------------- #
class PlaybackInterface(Interface):
    def design_window(self):
        controls = Controls()
        controls.pack(
            Gui.Text(text="using script:{0}".format(Init().software_config.using_script),
                     key='__MESSAGE__',
                     size=[40, 1],
                     font=("Helvetica", 18)))
        self.layouts.pack(controls)

        controls = Controls()
        controls.pack(Gui.T(' ' * 20))
        controls.pack(
            Gui.Button('start play',
                       key='__START_STOP__',
                       font=("Helvetica", 18),
                       size=(12, 1)))
        controls.pack(
            Gui.Button('quit',
                       key="__QUIT__",
                       font=("Helvetica", 18),
                       size=(12, 1)))
        self.layouts.pack(controls)


# -------------------------------------------------- #
#                       脚本记录界面                   #
# -------------------------------------------------- #
class RecordingInterface(Interface):
    def design_window(self):
        controls = Controls()
        controls.pack(
            Gui.Text(text='Click start button to start record.',
                     key='__MESSAGE__',
                     size=[40, 1],
                     font=("Helvetica", 18)))
        self.layouts.pack(controls)

        controls = Controls()
        controls.pack(Gui.T(' ' * 20))
        controls.pack(
            Gui.Button(button_text='start record',
                       key='__START_STOP__',
                       font=("Helvetica", 18),
                       size=(12, 1)))
        controls.pack(
            Gui.Button(button_text='quit',
                       disabled=False,
                       key="__QUIT__",
                       font=("Helvetica", 18),
                       size=(12, 1)))
        self.layouts.pack(controls)


# -------------------------------------------------- #
#                       脚本查看界面                   #
# -------------------------------------------------- #
class ReviewInterface(Interface):
    def design_window(self):
        controls = Controls()
        font = ("Helvetica", 18)
        controls.pack(
            Gui.Text(text="script",
                     size=(80, 1),
                     key="__EVENTS__",
                     font=font))
        self.layouts.pack(controls)

        controls = Controls()
        controls.pack(
            Gui.Multiline(size=(88, 20), key="__EVENTS_MESSAGE__", font=font))
        self.layouts.pack(controls)

        controls.empty()
        button_size = (5, 1)
        controls.pack(
            Gui.Button("Load", key="__LOAD_EVENTS__", size=button_size))
        controls.pack(Gui.Button('Save', key="__SAVE__", size=button_size))
        controls.pack(Gui.Button("Quit", key="__QUIT__", size=button_size))

        self.layouts.pack(controls)
