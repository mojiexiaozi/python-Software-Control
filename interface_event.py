# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     interface_event
   Description :
   Author :
   date：          2019/8/21
-------------------------------------------------
   Change Activity:
                   2019/8/21:
-------------------------------------------------
"""
__author__ = 'Lyl'

import os
import re
from multiprocessing import Process
from queue import Queue
from threading import Thread

import PySimpleGUI as Gui

from extract_input_message import LaunchExtractor
from interface import (MainInterface, PlaybackInterface, RecordingInterface,
                       ReviewInterface)
from pynput_playback import LaunchPlayback
from pynput_record import LaunchRecord, SaveEvent

from software_init import Init

software_config = Init().software_config


# -------------------------------------------------- #
#                       界面事件虚类                   #
# -------------------------------------------------- #
class InterfaceEvent(object):
    """
    界面事件虚类
    """

    def __init__(self, window, event_handle_queue):
        """
        :param window: PySimpleGui 窗口类实例
        :param event_handle_queue: 事件处理队列
        """
        super().__init__()

        # assert isinstance(event_handle_queue, Queue)
        self._event_handle_queue = event_handle_queue

        assert isinstance(window, Gui.Window)
        self._window = window

    @property
    def event_handle_queue(self):
        return self._event_handle_queue

    @property
    def window(self):
        return self._window


# -------------------------------------------------- #
#                     界面事件监控类                   #
# -------------------------------------------------- #
class InterfaceEventMonitor(InterfaceEvent):
    """
    界面事件监控类
    """

    def run(self):
        """
        界面事件监控线程
        :return: None
        """
        print("window event monitor thread start")
        while True:
            event, event_message = self._window.Read()  # 读取事件
            # print(event, event_message)
            self._event_handle_queue.put((event, event_message))

            if event in (None, "__QUIT__"):
                break
        print("interface event monitor run done")

    def __del__(self):
        print("interface event monitor class release")


# -------------------------------------------------- #
#                    界面事件处理虚类                  #
# -------------------------------------------------- #
class InterfaceEventHandle(InterfaceEvent, Thread):
    """界面事件处理类"""

    def __del__(self):
        print("interface event handle class release")

    def run(self) -> None:
        """
        在子类中重写该方法
        :return:
        """
        pass


# -------------------------------------------------- #
#                     界面事件处理类                   #
# -------------------------------------------------- #
class MainInterfaceEventHandle(InterfaceEventHandle):
    """
    主界面事件处理
    """

    def run(self) -> None:
        print("MainInterfaceEventHandle thread start")
        while True:
            event, event_message = self.event_handle_queue.get()
            print(event, event_message)
            if event in ["__QUIT__", None]:
                break  # stop running
            elif event == "__RECORD__":
                self.window.Hide()
                record_launcher = LaunchRecordInterface()
                record_launcher.start()
                record_launcher.join()
                self.window.UnHide()
            elif event == "__PLAYBACK__":
                self.window.Hide()
                playback_launcher = LaunchPlaybackInterface()
                playback_launcher.start()
                playback_launcher.join()
                self.window.UnHide()

            elif event == "__REVIEW__":
                self.window.Hide()
                launcher = LaunchReviewInterface()
                launcher.start()
                launcher.join()
                self.window.UnHide()
        print("main interface event handle run done")
        self.window.Close()


# -------------------------------------------------- #
#                 脚本处理界面事件处理类                #
# -------------------------------------------------- #
class ReviewInterfaceEventHandle(InterfaceEventHandle):
    """
    脚本查看界面事件处理
    """

    def run(self) -> None:
        print("ReviewInterfaceEventHandle thread start")
        event_cls_list = None
        choose_script_file_name = ""
        user_input_event_list = None
        while True:
            event, event_message = self.event_handle_queue.get()
            print(event, event_message)

            if event in (None, "__QUIT__"):
                break
            elif event == "__LOAD_EVENTS__":
                initial_dir = os.path.join(software_config.software_dir,
                                           software_config.scripts_dir)
                choose_script_path = Gui.filedialog.askopenfilename(
                    initialdir=initial_dir,
                    initialfile=software_config.using_script,
                    title="please choose a events file",
                    defaultextension="yaml",
                    filetypes=[("default", ".yaml"), ("events txt", ".txt")])

                if os.path.exists(choose_script_path):
                    choose_script_file_name = os.path.split(choose_script_path)[1]
                    self.window.Element("__EVENTS__").Update("choose script >> {0}".format(choose_script_file_name))
                    extractor_message = LaunchExtractor().do(choose_script_path)

                    if extractor_message:
                        user_input_message = extractor_message[0]
                        event_cls_list = extractor_message[1]
                        user_input_event_list = extractor_message[2]
                        # print(user_input_message)
                        self.window.Element("__EVENTS_MESSAGE__").Update(
                            user_input_message)

            elif event == "__SAVE__":
                message = event_message["__EVENTS_MESSAGE__"]
                pattern = re.compile(r'>>(.*)')
                message_list = re.findall(pattern=pattern, string=message)
                if message_list:
                    message_list = [temp.strip() for temp in message_list]

                for i in range(len(user_input_event_list)):
                    try:
                        user_input_event_list[i].message = message_list[i]
                    except IndexError:
                        pass

                for user_input_event in user_input_event_list:
                    event_cls_list[event_cls_list.index(
                        user_input_event)] = user_input_event

                if event_cls_list:
                    event_dict_list = [
                        event.events for event in event_cls_list]
                    SaveEvent.save_to_yaml_file(event_dict_list=event_dict_list,
                                                file_name=choose_script_file_name)

            # print("event: {0} value: {1}".format(event, event_message))

        self.window.Close()


# -------------------------------------------------- #
#                  回放界面事件处理类                   #
# -------------------------------------------------- #
class PlaybackInterfaceEventHandle(InterfaceEventHandle):
    """记录界面事件处理"""

    def start_play(self, playback_queue):
        # assert isinstance(playback_queue, Queue)

        self.window.Move(1300, 910)
        self.window.SetAlpha(0.3)

        launcher = LaunchPlayback(playback_queue=playback_queue,
                                  interface_queue=self.event_handle_queue)
        launcher.setDaemon(True)
        launcher.start()

    def stop_play(self):
        self.window.Move(800, 500)
        self.window.SetAlpha(0.8)

    def run(self) -> None:
        playing = False
        play_button_dict = {True: "stop play", False: "start play"}
        play_queue = None
        while True:
            event, event_message = self.event_handle_queue.get()
            # print(event, event_message)
            if event in (None, "__QUIT__"):
                break
            elif event == "__START_STOP__":
                playing = not playing
                self.window.Element("__START_STOP__").Update(
                    play_button_dict[playing])

                if playing:
                    self.window.Element("__MESSAGE__").Update("playing...")
                    play_queue = Queue()
                    self.start_play(play_queue)
                else:
                    self.window.Element("__MESSAGE__").Update("play done")
                    self.stop_play()
                    play_queue.put_nowait("__PLAYBACK_QUIT__")

                self.window.FindElement("__QUIT__").Update(disabled=playing)
            elif event == "__PLAYBACK_QUIT__":
                self.window.Element("__MESSAGE__").Update("play done")
                self.stop_play()
                playing = False
                self.window.Element("__START_STOP__").Update(
                    play_button_dict[playing])
                self.window.FindElement("__QUIT__").Update(disabled=False)

            elif event == "__PLAYBACK_MOTION__":
                self.window.Element("__MESSAGE__").Update(event_message)

        # self.window.Close()
        self.window.AutoClose = True
        print("playback event handle quit...")


# -------------------------------------------------- #
#                  记录界面事件处理类                   #
# -------------------------------------------------- #
class RecordInterfaceEventHandle(InterfaceEventHandle):
    """回放界面事件处理"""

    def start_record(self, record_queue):
        # assert isinstance(record_queue, Queue)

        self.window.Move(1300, 910)
        print(self.window)
        self.window.SetAlpha(0.3)

        LaunchRecord(event_handle_queue=self.event_handle_queue,
                     record_queue=record_queue).start()
        print("launcher done")

    def stop_record(self):
        self.window.Move(800, 500)
        self.window.SetAlpha(0.8)

    def run(self) -> None:
        recording = False
        record_button_dict = {True: "stop record", False: "start record"}
        record_queue = None
        while True:
            # print(1)
            event, event_message = self.event_handle_queue.get()
            # print(event, event_message)
            if event in [None, "__QUIT__"]:
                break
            elif event == "__START_STOP__":
                recording = not recording
                print("recording:{0}".format(recording))
                self.window.Element("__START_STOP__").Update(
                    record_button_dict[recording])

                if recording:
                    self.window.Element("__MESSAGE__").Update("recording...")
                    record_queue = Queue()
                    self.start_record(record_queue)
                    self.window.Element("__QUIT__").Update(disabled=True)
                else:
                    self.window.Element("__MESSAGE__").Update("record done")
                    self.stop_record()
                    record_queue.put_nowait("__QUIT__")
                    self.window.FindElement("__QUIT__").Update(disabled=False)
            elif event == "__RECORD_QUIT__":
                self.window.Element("__MESSAGE__").Update("record done")
                self.stop_record()
                recording = False
                self.window.FindElement("__START_STOP__").Update(
                    record_button_dict[recording])
                self.window.FindElement("__QUIT__").Update(disabled=False)

            elif event == "__RECORD_EVENT__":
                self.window.Element("__MESSAGE__").Update(event_message)

        self.window.Close()
        print("window event handle quit...")


# -------------------------------------------------- #
#                     主界面启动类                     #
# -------------------------------------------------- #
class LaunchMainInterface(Process):
    def run(self):
        main_interface = MainInterface(interface_title='Main')
        main_interface.load_window()
        win = main_interface.window

        event_handle_queue = Queue()
        monitor = InterfaceEventMonitor(
            window=win, event_handle_queue=event_handle_queue)
        handle = MainInterfaceEventHandle(
            window=win, event_handle_queue=event_handle_queue)

        handle.start()
        monitor.run()


# -------------------------------------------------- #
#                脚本查看界面启动类                     #
# -------------------------------------------------- #
class LaunchReviewInterface(Process):
    def run(self):
        interface = ReviewInterface(interface_title='Review')
        interface.load_window()
        win = interface.window

        event_handle_queue = Queue()
        monitor = InterfaceEventMonitor(window=win,
                                        event_handle_queue=event_handle_queue)
        handle = ReviewInterfaceEventHandle(
            window=win, event_handle_queue=event_handle_queue)

        handle.start()
        monitor.run()


# -------------------------------------------------- #
#                   记录界面启动类                     #
# -------------------------------------------------- #
class LaunchRecordInterface(Process):
    def run(self):
        interface = RecordingInterface(interface_title="Record")
        interface.load_window()
        win = interface.window

        event_handle_queue = Queue()
        monitor = InterfaceEventMonitor(window=win,
                                        event_handle_queue=event_handle_queue)
        handle = RecordInterfaceEventHandle(
            window=win, event_handle_queue=event_handle_queue)

        handle.start()
        monitor.run()


# -------------------------------------------------- #
#                   回放界面启动类                     #
# -------------------------------------------------- #
class LaunchPlaybackInterface(Process):
    def run(self):
        interface = PlaybackInterface(interface_title="Playback")
        interface.load_window()
        win = interface.window

        event_handle_queue = Queue()
        monitor = InterfaceEventMonitor(window=win,
                                        event_handle_queue=event_handle_queue)
        handle = PlaybackInterfaceEventHandle(
            window=win, event_handle_queue=event_handle_queue)

        handle.start()
        monitor.run()
