# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     recording
   Description :
   Author :       Lyl
   date：          2019/7/30
------------------      -------------------------------
   Change Activity:
                   2019/7/30:
-------------------------------------------------
"""
__author__ = 'Lyl'

import yaml
from queue import Queue
from time import time, sleep
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

            # print(window.title)
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
        sleep(3)
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
        sleep(3)
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


class EventNotify(object):
    def __init__(self, notify_queue):
        assert isinstance(notify_queue, Queue)
        self._queue = notify_queue
        self._event = None
        self.notify_message = ""

    def notify(self, event):
        assert isinstance(event, dict)
        self._event = event
        self.get_notify_message()
        print(self.notify_message)
        self._queue.put(self.notify_message)

    @property
    def queue(self):
        return self._queue

    @property
    def event(self):
        return self._event

    def get_notify_message(self):
        pass


class KeyboardNotify(EventNotify):
    def get_notify_message(self):
        event = self.event
        assert isinstance(event, dict)
        event_key = event["event_key"]
        event_type = {"keyboard_press": "pressed", "keyboard_release": "released"}[event["event_type"]]
        self.notify_message = "recorded keyboard.key:{0} {1}".format(event_key, event_type)


class MouseMoveNotify(EventNotify):
    def get_notify_message(self):
        event = self.event
        assert isinstance(event, dict)
        x = event["position_x"]
        y = event["position_y"]
        self.notify_message = "recorded mouse move to:({0}, {1})".format(x, y)


class MouseClickNotify(EventNotify):
    def get_notify_message(self):
        event = self.event
        assert isinstance(event, dict)
        event_key = event["event_key"]
        x = event["position_x"]
        y = event["position_y"]
        event_type = {"mouse_press": "pressed", "mouse_release": "release"}[event["event_type"]]
        self.notify_message = "recorded mouse.{0} {1} in:({2}, {3})".format(event_key, event_type, x, y)


class MouseScrollNotify(EventNotify):
    def get_notify_message(self):
        event = self.event
        assert isinstance(event, dict)
        dy = event["dy"]
        scroll_direction = {True: "up", False: "down"}[dy > 0]
        self.notify_message = "recorded mouse scroll {0}".format(scroll_direction)


class NotifyProduct(object):
    @staticmethod
    def create(event_type, notify_queue):
        if event_type in ["mouse_press", "mouse_release"]:
            return MouseClickNotify(notify_queue)
        elif event_type in ["keyboard_press", "keyboard_release"]:
            return KeyboardNotify(notify_queue)
        elif event_type == "mouse_scroll":
            return MouseScrollNotify(notify_queue)
        elif event_type == "mouse_move":
            return MouseMoveNotify(notify_queue)


class Recorder(Thread):
    def __init__(self, queue, notify_queue):
        super().__init__()
        assert isinstance(queue, Queue) and isinstance(notify_queue, Queue)
        self._queue = queue
        self._notify_queue = notify_queue
        self._notify_product_method = NotifyProduct().create

        self._mouse_monitor_quit = False
        self._keyboard_monitor_quit = False
        self._events = []
        self._last_time = 0.0

    @property
    def queue(self):
        return self._queue

    @property
    def notify_queue(self):
        return self._notify_queue

    def quit_monitor(self, event):
        if event == "keyboard_monitor_quit":
            self._mouse_monitor_quit = True
            mouse.Controller().click(mouse.Button.middle)
            print(event)
        elif event == "mouse_monitor_quit":
            self._keyboard_monitor_quit = True
            keyboard.Controller().press(keyboard.Key.f8)
            keyboard.Controller().release(keyboard.Key.f8)

            print(event)

        elif event == "monitor_quit":
            self._keyboard_monitor_quit = True
            self._mouse_monitor_quit = True
            mouse.Controller().click(mouse.Button.middle)
            sleep(0.1)
            keyboard.Controller().press(keyboard.Key.f8)
            sleep(0.1)
            keyboard.Controller().release(keyboard.Key.f8)

        if self._keyboard_monitor_quit and self._mouse_monitor_quit:
            print('monitor quit')
            return True
        else:
            return False

    def set_event_time(self, events):
        assert isinstance(events, list)

        event_time = events[-1]["event_time"] - self._last_time
        self._last_time = events[-1]["event_time"]
        events[-1]["event_time"] = abs(event_time)
        return events

    def run(self):
        while True:
            event = self._queue.get()
            assert isinstance(event, str) or isinstance(event, dict)
            if self.quit_monitor(event):
                break

            if isinstance(event, dict):
                # try:   # 忽略录制窗口   将会在后处理中实现，以满足单一原则（假装满足）
                #     if event["window"]["title"] == "Recording" and event["event_type"] == "mouse_press":
                #         print("ignore-{0}".format(event))
                #         continue
                # except KeyError:
                #     pass
                RecordingProduct().create(event["event_type"])
                self._events.append(event)
                events = self.set_event_time(self._events)

                notify = self._notify_product_method(event["event_type"], self._notify_queue)
                notify.notify(event)

                # print("recorded: {0}".format(event["event_type"]))
                # print(events[-1])
        if self._events:
            self._events[0]["event_time"] = 3.0   # 延时1秒开始脚本
        SaveEvents().do(self._events)


class SaveEvents(object):
    @staticmethod
    def do(events):
        with open('events.yaml', 'w') as f:
            yaml.safe_dump(events, f, encoding='utf-8', allow_unicode=True)


class StartRecord(object):
    def __init__(self, queue, notify_queue):
        assert isinstance(queue, Queue) and isinstance(notify_queue, Queue)
        self._notify_queue = notify_queue
        self._queue = queue

        self.recorder = None
        self.mouse_monitor = None
        self.keyboard_monitor = None

    def start(self):
        self.recorder = Recorder(self._queue, self._notify_queue)
        self.mouse_monitor = MouseMonitoring(self._queue)
        self.keyboard_monitor = KeyBoardMonitoring(self._queue)

        self.recorder.start()
        self.mouse_monitor.start()
        self.keyboard_monitor.start()
        print("recording start")

    def join(self):
        assert isinstance(self.recorder, Recorder)
        assert isinstance(self.mouse_monitor, MouseMonitoring)
        assert isinstance(self.keyboard_monitor, KeyBoardMonitoring)
        if self.recorder.is_alive():
            self.recorder.join()

        if self.mouse_monitor.is_alive():
            self.mouse_monitor.join()

        if self.keyboard_monitor.is_alive():
            self.keyboard_monitor.join()


if __name__ == '__main__':
    _queue = Queue()
    _notify_queue = Queue()
    StartRecord(_queue, _notify_queue).start()
