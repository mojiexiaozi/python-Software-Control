# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     recording
   Description :
   Author :       Lyl
   date：          2019/7/30
-------------------------------------------------
   Change Activity:
                   2019/7/30:
-------------------------------------------------
"""
__author__ = 'Lyl'

import yaml
from queue import Queue
from time import time
from threading import Thread
from pyautogui import getActiveWindow, onScreen
from win32gui import GetClassName
from pynput import mouse
from pynput import keyboard


class Monitoring(Thread):
    def __init__(self, queue):
        super().__init__()

        assert isinstance(queue, Queue)
        self._queue = queue

    @property
    def queue(self):
        return self._queue

    def run(self):
        pass

    @staticmethod
    def add_window_to_event(event):
        assert isinstance(event, dict)
        window = getActiveWindow()
        if window:
            event["window"] = {
                "title": window.title,
                "class_name": GetClassName(window._hWnd),
                "top": window.top,
                "left": window.left,
                "width": window.width,
                "height": window.height}
        else:
            event["window"] = None
        return event


class KeyBoardMonitoring(Monitoring):
    @staticmethod
    def key_to_string(key):
        try:
            key = key.char

        except AttributeError:
            key = str(key)
        return key

    def _on_press(self, key):
        if key == keyboard.Key.f8:
            self.queue.put("keyboard_monitor_quit")
            return False

        key = self.key_to_string(key)
        event = {"event_type": "keyboard_press",
                 "event_key": key,
                 "event_time": time()}
        event = self.add_window_to_event(event)   # 添加窗口
        self.queue.put(event)

    def _on_release(self, key):
        key = self.key_to_string(key)
        event = {"event_type": "keyboard_release",
                 "event_key": key,
                 "event_time": time()}
        event = self.add_window_to_event(event)   # 添加窗口
        self.queue.put(event)

    def run(self):
        with keyboard.Listener(on_press=self._on_press, on_release=self._on_release) as listener:
            listener.join()


class MouseMonitoring(Monitoring):
    def _on_move(self, x, y):
        event = {"event_type": "mouse_move",
                 "position_x": x,
                 "position_y": y,
                 "event_time": time()}
        event = self.add_window_to_event(event)   # 添加窗口
        self._queue.put(event)

    def _on_click(self, x, y, button, pressed):
        if button == mouse.Button.middle:
            # Stop listener
            self._queue.put("mouse_monitor_quit")
            return False

        event = {
            "event_type": "mouse_{0}".format(
                {
                    True: "press",
                    False: "release"}[pressed]),
            "position_x": x,
            "position_y": y,
            "event_key": str(button),
            "event_time": time()}
        event = self.add_window_to_event(event)   # 添加窗口
        self._queue.put(event)

    def _on_scroll(self, x, y, dx, dy):
        event = {"event_type": "mouse_scroll",
                 "dx": dx,
                 "dy": dy,
                 "event_time": time()}
        event = self.add_window_to_event(event)   # 添加窗口
        self._queue.put(event)

    def run(self):
        # Collect events until released
        with mouse.Listener(on_move=self._on_move, on_click=self._on_click, on_scroll=self._on_scroll) as listener:
            # listener.start()
            listener.join()


class Recording(object):
    def __init__(self):
        self.event_type = ""

    def do(self, event):
        assert event["event_type"] == self.event_type
        assert isinstance(event["event_time"], time)
        assert not KeyError(event["window"])


class MouseMoveRecording(Recording):
    def __init__(self):
        super().__init__()
        self.event_type = "mouse_move"

    def do(self, event):
        super().do(event)
        assert onScreen(event["position_x"], event["position_y"])
        return event


class MouseClickPressRecording(Recording):
    def __init__(self):
        super().__init__()
        self.event_type = "mouse_click_press"

    def do(self, event):
        super().do(event)
        assert isinstance(event["event_key"], mouse.Button)
        assert onScreen(event["position_x"], event["position_y"])
        return event


class MouseClickReleaseRecording(Recording):
    def __init__(self):
        super().__init__()
        self.event_type = "mouse_click_release"

    def do(self, event):
        super().do(event)
        assert isinstance(event["event_key"], mouse.Button)
        assert onScreen(event["position_x"], event["position_y"])
        return event


class MouseScrollRecording(Recording):
    def __init__(self):
        super().__init__()
        self.event_type = "mouse_scroll"

    def do(self, event):
        super().do(event)
        assert isinstance(event["position_x"], int)
        assert isinstance(event["position_y"], int)
        return event


class KeyboardReleaseRecording(Recording):
    def __init__(self):
        super().__init__()
        self.event_type = "key_release"

    def do(self, event):
        super().do(event)
        assert isinstance(event["event_key"], keyboard.Key)
        return event


class KeyboardPressRecording(Recording):
    def __init__(self):
        super().__init__()
        self.event_type = "key_press"

    def do(self, event):
        super().do(event)
        assert event["event_type"] in ["key_press", "key_release"]
        assert isinstance(event["event_key"], keyboard.Key)
        return event


class RecordingProduct(object):
    @staticmethod
    def create(event_type):
        assert event_type in [
            "mouse_move",
            "mouse_press",
            "mouse_release",
            "mouse_scroll",
            "keyboard_press",
            "keyboard_release"]
        if event_type == "mouse_move":
            return MouseMoveRecording()
        elif event_type == "mouse_press":
            return MouseClickPressRecording()
        elif event_type == "mouse_release":
            return MouseClickReleaseRecording()
        elif event_type == "mouse_scroll":
            return MouseScrollRecording()
        elif event_type == "keyboard_press":
            return KeyboardPressRecording()
        elif event_type == "keyboard_release":
            return KeyboardReleaseRecording()


class Recorder(Thread):
    def __init__(self):
        super().__init__()
        self._queue = Queue()
        self._mouse_monitor_quit = False
        self._keyboard_monitor_quit = False
        self._events = []
        self._last_time = 0.0

    @property
    def queue(self):
        return self._queue

    def quit_monitor(self, event):
        if event == "keyboard_monitor_quit":
            self._mouse_monitor_quit = True
            mouse.Controller().click(mouse.Button.middle)
            # print(event)
        elif event == "mouse_monitor_quit":
            self._keyboard_monitor_quit = True
            keyboard.Controller().press(keyboard.Key.f8)
            keyboard.Controller().release(keyboard.Key.f8)
            # print(event)

        if self._keyboard_monitor_quit and self._mouse_monitor_quit:
            print('quit')
            return True
        else:
            return False

    def set_event_time(self, events):
        assert isinstance(events, list)

        event_time = events[-1]["event_time"] - self._last_time
        self._last_time = events[-1]["event_time"]
        events[-1]["event_time"] = event_time
        return events

    def run(self):
        while True:
            event = self._queue.get()
            assert isinstance(event, str) or isinstance(event, dict)
            print(event)
            if self.quit_monitor(event):
                break

            if isinstance(event, dict):
                RecordingProduct().create(event["event_type"])
                self._events.append(event)
                events = self.set_event_time(self._events)
                # print(events[-1])
        self._events[0]["event_time"] = 1.0  # 延时1秒开始脚本
        SaveEvents().do(self._events)


class SaveEvents(object):
    @staticmethod
    def do(events):
        with open('events.yaml', 'w') as f:
            yaml.safe_dump(events, f, encoding='utf-8', allow_unicode=True)


if __name__ == '__main__':
    recorder = Recorder()

    mouse_monitor = MouseMonitoring(recorder.queue)
    keyboard_monitor = KeyBoardMonitoring(recorder.queue)

    recorder.start()
    mouse_monitor.start()
    keyboard_monitor.start()

    recorder.join()
    mouse_monitor.join()
    keyboard_monitor.join()
