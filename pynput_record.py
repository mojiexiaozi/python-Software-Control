#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   pynput_record.py
@Time    :   2019/08/28 09:33:07
@Author  :   MasterLin
@Version :   1.0
@Contact :   15651838825@163.com
@License :   (C)Copyright 2018-2019, CASI
@Desc    :   None
"""

from queue import Queue
from threading import Thread
from time import time

import win32gui
import win32api
from pynput import keyboard, mouse

from script_save import SaveEvent
from software_init import Init

software_config = Init().software_config


class Event(object):
    """ Base event """
    def __init__(self):
        """
        @self.event_type : event type
        @self._window    : window message
        @self._events    : events
        @self._time =    : time
        """
        self._event_type = "event"
        self._window = None
        self._events = {}
        self._time = time()

    @property
    def event_type(self):
        return self._event_type

    @event_type.setter
    def event_type(self, event_type):
        self._event_type = event_type

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, now_time):
        self._time = now_time

    @property
    def events(self):
        self.dumps()
        return self._events

    def add_event_value(self, key_word, value):
        assert key_word is not None
        assert isinstance(key_word, str)
        self._events[key_word] = value

    @property
    def window(self):
        return self._window

    @window.setter
    def window(self, window):
        self._window = window

    def dumps(self):
        self._events["window"] = self._window
        self.add_event_value("event type", self.event_type)
        self.add_event_value("time", self.time)


class MouseEvent(Event):
    def __init__(self):
        super().__init__()
        self.event_type = "mouse event"
        self._x = 0
        self._y = 0

    @property
    def position(self):
        return self._x, self._y

    @position.setter
    def position(self, position):
        self._x = position[0]
        self._y = position[1]

    def dumps(self):
        super().dumps()
        self.add_event_value("x", self._x)
        self.add_event_value("y", self._y)


class KeyboardEvent(Event):
    def __init__(self):
        super().__init__()
        self.event_type = "keyboard event"
        self._key = None
        self._caps_lk = False

    @property
    def caps_lk(self):
        return self._caps_lk

    @caps_lk.setter
    def caps_lk(self, caps_lk):
        self._caps_lk = caps_lk

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, key):
        self._key = key

    def dumps(self):
        super().dumps()
        # print(self._key, type(self._key))
        try:
            key = self._key.char
        except AttributeError:
            key = str(self._key)
        self.add_event_value("key", key)
        self.add_event_value("caps lk", self._caps_lk)


class MouseMove(MouseEvent):
    def __init__(self):
        super().__init__()
        self.event_type = "mouse move"


class MouseClick(MouseEvent):
    def __init__(self):
        super().__init__()
        self.event_type = "mouse click"
        self._button = None

    @property
    def button(self):
        return self._button

    @button.setter
    def button(self, button):
        assert isinstance(button, mouse.Button)
        self._button = button

    def dumps(self):
        super().dumps()
        self.add_event_value("button", str(self._button))


class MouseClickPress(MouseClick):
    def __init__(self):
        super().__init__()
        self.event_type = "mouse click press"


class MouseClickRelease(MouseClick):
    def __init__(self):
        super().__init__()
        self.event_type = "mouse click release"


class MouseScroll(MouseEvent):
    def __init__(self):
        super().__init__()
        self.event_type = "mouse scroll"
        self._dx = 0
        self._dy = 0

    @property
    def wheel(self):
        return self._dx, self._dy

    @wheel.setter
    def wheel(self, wheel):
        self._dx = wheel[0]
        self._dy = wheel[1]

    def dumps(self):
        super().dumps()
        self.add_event_value("dx", self._dx)
        self.add_event_value("dy", self._dy)


class KeyboardPress(KeyboardEvent):
    def __init__(self):
        super().__init__()
        self.event_type = "keyboard press"


class KeyboardRelease(KeyboardEvent):
    def __init__(self):
        super().__init__()
        self.event_type = "keyboard release"


class UserInputEvent(Event):
    def __init__(self):
        super().__init__()
        self.event_type = "user input"
        self._message = ""
        self.time = 1.0

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, message):
        self._message = message

    def dumps(self):
        super().dumps()
        self.add_event_value("message", self._message)


class Product(object):
    def product(self):
        pass


class UserInputEventProduct(Product):
    def product(self):
        return UserInputEvent()


class MouseMoveProduct(Product):
    def product(self):
        return MouseMove()


class MouseClickPressProduct(Product):
    def product(self):
        return MouseClickPress()


class MouseClickReleaseProduct(Product):
    def product(self):
        return MouseClickRelease()


class MouseScrollProduct(Product):
    def product(self):
        return MouseScroll()


class KeyboardPressProduct(Product):
    def product(self):
        return KeyboardPress()


class KeyboardReleaseProduct(Product):
    def product(self):
        return KeyboardRelease()


class EventProduct(object):
    @staticmethod
    def product(event_type):
        assert event_type in [
            "mouse move", "mouse click press", "mouse click release",
            "mouse scroll", "keyboard press", "keyboard release", "user input"
        ]
        if event_type == "mouse move":
            return MouseMoveProduct().product()
        elif event_type == "mouse click press":
            return MouseClickPressProduct().product()
        elif event_type == "mouse click release":
            return MouseClickReleaseProduct().product()
        elif event_type == "mouse scroll":
            return MouseScrollProduct().product()
        elif event_type == "keyboard press":
            return KeyboardPressProduct().product()
        elif event_type == "keyboard release":
            return KeyboardReleaseProduct().product()
        elif event_type == "user input":
            return UserInputEventProduct().product()


class Window(object):
    @property
    def window(self):
        window = get_window()
        return window


def get_window():
    handle = win32gui.GetForegroundWindow()
    # print(handle)
    if handle:
        left, top, right, bottom = (0, 0, 0, 0)
        title = ""
        class_name = ""
        try:
            title = win32gui.GetWindowText(handle)
            class_name = win32gui.GetClassName(handle)

            left, top, right, bottom = win32gui.GetWindowRect(handle)
        except BaseException as e:
            print(e)

        width = right - left
        height = bottom - top

        window_message = {
            "title": title,
            "class name": class_name,
            "left": left,
            "top": top,
            "width": width,
            "height": height
        }
        return window_message

    else:
        return None


class Listener(Thread):
    def __init__(self, record_queue):
        # assert isinstance(record_queue, Queue)
        super().__init__()
        self._record_queue = record_queue

    @property
    def record_queue(self):
        return self._record_queue

    def listener(self):
        raise UserWarning("this method is write to child class")


class MouseListener(Listener):
    def on_move(self, x, y):
        mouse_move = MouseMoveProduct().product()

        mouse_move.window = Window().window
        mouse_move.position = (x, y)
        self.record_queue.put(mouse_move)

    def on_click(self, x, y, button, pressed):
        if pressed:
            mouse_click = MouseClickPressProduct().product()
        else:
            mouse_click = MouseClickReleaseProduct().product()

        mouse_click.window = Window().window
        mouse_click.position = x, y
        mouse_click.button = button
        self.record_queue.put(mouse_click)

    def on_scroll(self, x, y, dx, dy):
        mouse_scroll = MouseScrollProduct().product()

        mouse_scroll.window = Window().window
        mouse_scroll.position = x, y
        mouse_scroll.wheel = (dx, dy)
        self.record_queue.put(mouse_scroll)

    def run(self):
        listener = mouse.Listener(on_click=self.on_click,
                                  on_move=self.on_move,
                                  on_scroll=self.on_scroll)
        listener.setDaemon(True)
        listener.start()


class KeyboardListener(Listener):
    def on_press(self, key):
        keyboard_press = KeyboardPressProduct().product()

        keyboard_press.window = Window().window
        keyboard_press.key = key
        keyboard_press.caps_lk = bool(win32api.GetAsyncKeyState(20))
        # print("debug...")
        self.record_queue.put(keyboard_press)

    def on_release(self, key):
        keyboard_release = KeyboardReleaseProduct().product()

        keyboard_release.window = Window().window
        keyboard_release.key = key
        keyboard_release.caps_lk = bool(win32api.GetAsyncKeyState(20))
        self.record_queue.put(keyboard_release)

    def run(self):
        listener = keyboard.Listener(on_press=self.on_press,
                                     on_release=self.on_release)
        listener.setDaemon(True)
        listener.start()


class ListenerProduct(object):
    @staticmethod
    def product(monitor_name="mouse", record_queue=Queue()):
        # assert isinstance(record_queue, Queue)
        if monitor_name == 'mouse':
            return MouseListener(record_queue)
        elif monitor_name == "keyboard":
            return KeyboardListener(record_queue)


class Record(Thread):
    def __init__(self, record_queue):
        super().__init__()
        # assert isinstance(record_queue, Queue)
        self._record_queue = record_queue
        # self._event_handle_queue = event_handle_queue

        self._last_time = -1

    def run(self):
        mouse_listener = MouseListener(self._record_queue)
        keyboard_listener = KeyboardListener(self._record_queue)

        mouse_listener.setDaemon(True)
        keyboard_listener.setDaemon(True)

        mouse_listener.start()
        keyboard_listener.start()
        event_dict_list = []
        while True:
            event = self._record_queue.get()

            if isinstance(event, KeyboardPress):
                if event.key == keyboard.Key.f12:
                    break

            if isinstance(event, Event):
                print("debug-{0}".format(event.event_type))
                event_dict = event.events
                # print(event.event_type)
                # self._event_handle_queue.put(
                #     ("__RECORD_EVENT__", event.event_type))
                event_dict_list.append(event_dict)
        print("quit...")
        event_dict_list = TimeDelay.get_time(event_dict_list)
        SaveEvent().save_to_yaml_file(event_dict_list)


class TimeDelay(object):
    @staticmethod
    def get_time(event_dict_list):
        if not event_dict_list:
            return event_dict_list

        last_time = event_dict_list[0]['time'] - 0.1
        for i in range(len(event_dict_list)):
            delay_time = event_dict_list[i]['time'] - last_time
            last_time = event_dict_list[i]['time']
            event_dict_list[i]['time'] = delay_time
        return event_dict_list


# class RecordProduct(object):
#     @staticmethod
#     def product(record_queue=Queue(), event_handle_queue=Queue()):
#         return Record(record_queue=record_queue,
#                       event_handle_queue=event_handle_queue)
#
#
# class LaunchRecord(Thread):
#     def __init__(self, event_handle_queue, record_queue):
#         super().__init__()
#         # assert isinstance(window_event_queue, Queue)
#         # assert isinstance(record_queue, Queue)
#         self._event_handle_queue = event_handle_queue
#         self._record_queue = record_queue
#
#     def run(self):
#         mouse_listener = ListenerProduct.product(
#             monitor_name="mouse", record_queue=self._record_queue)
#         keyboard_listener = ListenerProduct.product(
#             monitor_name="keyboard", record_queue=self._record_queue)
#         recorder = RecordProduct.product(
#             record_queue=self._record_queue,
#             event_handle_queue=self._event_handle_queue)
#
#         mouse_listener.listener()
#         print("mouse listener...")
#         keyboard_listener.listener()
#         print("keyboard listener...")
#
#         recorder.start()
#         print("recording...")
#         recorder.join()
#         print("record done")
#         self._event_handle_queue.put(("__RECORD_QUIT__", None))


if __name__ == '__main__':
    pass
    # launcher = LaunchRecord(Queue(), Queue())
    # launcher.start()
    # launcher.join()
