# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 10:54:53 2019

@author: Lyl
"""

import yaml
from queue import Queue
from threading import Thread
from software_init import Init
from pynput import mouse, keyboard
import win32gui
from time import time
from log import Logger


software_config = Init()


class Event(object):
    def __init__(self):
        self.event_type = "event"
        self._window = None
        self._event_dict = {}
        self._time = time()

    def set_time(self, now_time):
        self._time = now_time

    @property
    def time(self):
        return self._time

    def set_event_dict(self, key_word, value):
        assert key_word is not None
        assert isinstance(key_word, str)
        self._event_dict[key_word] = value

    def set_window(self, window):
        self._window = window

    @property
    def window(self):
        return self._window

    def dumps(self):
        self._event_dict["window"] = self._window
        self.set_event_dict("event type", self.event_type)
        self.set_event_dict("time", self.time)

    @property
    def event_dict(self):
        self.dumps()
        return self._event_dict


class MouseEvent(Event):
    def __init__(self):
        super().__init__()
        self.event_type = "mouse event"
        self._x = 0
        self._y = 0

    @property
    def position(self):
        return self._x, self._y

    def set_position(self, x, y):
        assert isinstance(x, int) and isinstance(y, int)
        self._x = x
        self._y = y

    def dumps(self):
        super().dumps()
        self.set_event_dict("x", self._x)
        self.set_event_dict("y", self._y)


class KeyboardEvent(Event):
    def __init__(self):
        super().__init__()
        self.event_type = "keyboard event"
        self._key = None

    def set_key(self, key):
        # assert isinstance(key, keyboard.Key) or isinstance(key, keyboard.KeyCode)
        self._key = key

    @property
    def key(self):
        return self._key

    def dumps(self):
        super().dumps()
        assert isinstance(
            self._key,
            keyboard.Key) or isinstance(
            self._key,
            keyboard.KeyCode)
        try:
            key = self._key.char
        except AttributeError:
            key = str(self._key)
        self.set_event_dict("key", key)


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

    def set_button(self, button):
        assert isinstance(button, mouse.Button)
        self._button = button

    def dumps(self):
        super().dumps()
        self.set_event_dict("button", str(self._button))


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

    def set_wheel(self, dx, dy):
        assert isinstance(dx, int)
        assert isinstance(dy, int)
        self._dx = dx
        self._dy = dy

    @property
    def wheel(self):
        return self._dx, self._dy

    def dumps(self):
        super().dumps()
        self.set_event_dict("dx", self._dx)
        self.set_event_dict("dy", self._dy)


class KeyboardPress(KeyboardEvent):
    def __init__(self):
        super().__init__()
        self.event_type = "keyboard press"


class KeyboardRelease(KeyboardEvent):
    def __init__(self):
        super().__init__()
        self.event_type = "keyboard release"


class Product(object):
    def product(self):
        pass


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
        assert event_type in ["mouse move",
                              "mouse click press",
                              "mouse click release",
                              "mouse scroll",
                              "keyboard press",
                              "keyboard release"]
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


class Window(object):
    def __init__(self):
        self._window = self.get_window()

    @property
    def window(self):
        return self._window

    @staticmethod
    def get_window():
        handle = win32gui.GetForegroundWindow()
        if handle:
            try:
                title = win32gui.GetWindowText(handle)
                class_name = win32gui.GetClassName(handle)

                left, top, right, bottom = win32gui.GetWindowRect(handle)
                width = right - left
                height = bottom - top

                window_message = {"title": title,
                                  "class name": class_name,
                                  "left": left,
                                  "top": top,
                                  "width": width,
                                  "height": height}
                return window_message

            except BaseException as e:
                print(e)
        else:
            return None


class Listener(object):
    def __init__(self, record_queue):
        # assert isinstance(record_queue, Queue)
        self._record_queue = record_queue

    @property
    def record_queue(self):
        return self._record_queue

    def listener(self):
        raise UserWarning("this method is write to child class")


class MouseListener(Listener):
    def on_move(self, x, y):
        mouse_move = MouseMoveProduct().product()
        mouse_move.set_window(Window().window)
        mouse_move.set_position(x, y)
        self.record_queue.put(mouse_move)

    def on_click(self, x, y, button, pressed):
        if pressed:
            mouse_click = MouseClickPressProduct().product()
        else:
            mouse_click = MouseClickReleaseProduct().product()

        mouse_click.set_window(Window().window)
        mouse_click.set_position(x, y)
        mouse_click.set_button(button)
        self.record_queue.put(mouse_click)

    def on_scroll(self, x, y, dx, dy):
        mouse_scroll = MouseScrollProduct().product()

        mouse_scroll.set_window(Window().window)
        mouse_scroll.set_position(x, y)
        mouse_scroll.set_wheel(dx, dy)
        self.record_queue.put(mouse_scroll)

    def listener(self):
        listener = mouse.Listener(on_click=self.on_click,
                                  on_move=self.on_move,
                                  on_scroll=self.on_scroll)
        listener.start()


class KeyboardListener(Listener):
    def on_press(self, key):
        keyboard_press = KeyboardPressProduct().product()
        keyboard_press.set_window(Window().window)
        keyboard_press.set_key(key)
        self.record_queue.put(keyboard_press)

    def on_release(self, key):
        keyboard_release = KeyboardReleaseProduct().product()
        keyboard_release.set_window(Window().window)
        keyboard_release.set_key(key)
        self.record_queue.put(keyboard_release)

    def listener(self):
        listener = keyboard.Listener(on_press=self.on_press,
                                     on_release=self.on_release)
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
    def __init__(self, record_queue, event_handle_queue):
        super().__init__()
        # assert isinstance(record_queue, Queue)
        self._record_queue = record_queue
        # print(event_handle_queue, Queue)
        # assert isinstance(event_handle_queue, Queue)
        self._event_handle_queue = event_handle_queue

        self._last_time = -1

    @staticmethod
    def dump_to_yaml(events):
        assert isinstance(events, list)
        with open(software_config.default_record_file, 'w') as f:
            yaml.safe_dump(events, f, encoding='utf-8', allow_unicode=True)

    def run(self):
        event_dict_list = []
        while True:
            event = self._record_queue.get()

            if isinstance(event, KeyboardPress):
                if event.key == keyboard.Key.f12:
                    break
            elif event == "__QUIT__":
                break

            if isinstance(event, Event):
                event_dict = event.event_dict

                print(event.event_type)
                self._event_handle_queue.put(("__RECORD_EVENT__", event.event_type))
                event_dict_list.append(event_dict)
        print("quit...")
        SaveEvent().save_to_yaml_file(event_dict_list)


class SaveEvent(object):
    @staticmethod
    def save_to_yaml_file(event_dict_list):
        assert isinstance(event_dict_list, list)
        if event_dict_list:
            assert isinstance(event_dict_list[0], dict)

            with open(software_config.default_record_file, 'w') as file_ref:
                yaml.safe_dump(
                    event_dict_list,
                    file_ref,
                    encoding='utf-8',
                    allow_unicode=True)
                print("save...")


class RecordProduct(object):
    @staticmethod
    def product(record_queue=Queue(), event_handle_queue=Queue()):
        return Record(record_queue=record_queue, event_handle_queue=event_handle_queue)


class LaunchRecord(Thread):
    def __init__(self, event_handle_queue, record_queue):
        super().__init__()
        # assert isinstance(window_event_queue, Queue)
        # assert isinstance(record_queue, Queue)
        self._event_handle_queue = event_handle_queue
        self._record_queue = record_queue

    def run(self):
        mouse_listener = ListenerProduct.product(monitor_name="mouse", record_queue=self._record_queue)
        keyboard_listener = ListenerProduct.product(monitor_name="keyboard", record_queue=self._record_queue)
        recorder = RecordProduct.product(record_queue=self._record_queue,
                                         event_handle_queue=self._event_handle_queue)

        mouse_listener.listener()
        print("mouse listener...")
        keyboard_listener.listener()
        print("keyboard listener...")

        recorder.start()
        print("recording...")
        recorder.join()
        print("record done")
        self._event_handle_queue.put(("__RECORD_QUIT__", None))


if __name__ == '__main__':
    launcher = LaunchRecord(Queue(), Queue())
    launcher.start()
    launcher.join()
