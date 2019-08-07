# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     playback
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
from threading import Thread

from pynput.mouse import Button
from pynput.keyboard import Key
from pynput import mouse
from pynput import keyboard

from win32gui import FindWindow
import pyautogui

from time import sleep


class WindowFinder(object):
    @staticmethod
    def get_window(class_name, title):
        assert isinstance(class_name, str)
        assert isinstance(title, str)
        hwnd = FindWindow(None, title)

        if not isinstance(hwnd, pyautogui.Window):  # 标题查不到句柄，使用类名查找，类名查找不到需要打开
            hwnd = FindWindow(class_name, None)

        if hwnd:
            return pyautogui.Window(hwnd)


class WindowEvent(object):
    @staticmethod
    def set_window(event):
        assert isinstance(event, dict)

        window_dict = event["window"]
        win_class_name = window_dict["class_name"]
        win_title = window_dict["title"]
        win_height = window_dict["height"]
        win_width = window_dict["width"]
        win_top = window_dict["top"]
        win_left = window_dict["left"]

        win = WindowFinder.get_window(win_class_name, win_title)
        if win:
            if (not win.isActive) or not (event["event_type"] == "mouse_move"):
                win.restore()
                win.activate()
            if not (win.height == win_height) or not (win.width == win_height):
                win.resizeTo(win_width, win_height)

            if win.height != win_height or win.width != win_height:
                win.moveTo(win_left, win_top)


class Event(object):
    def __init__(self):
        self.event_controller=None

    def do(self, event):
        assert isinstance(event, dict)


class PressEvent(Event):
    def do(self, event):
        print("{0}-press".format(event["event_key"]))
        self.event_controller.press(event["event_key"])


class ReleaseEvent(Event):
    def do(self, event):
        print("{0}-release".format(event["event_key"]))
        self.event_controller.release(event["event_key"])


class ClickEvent(Event):
    def do(self, event):
        print("{0}-click".format(event["event_key"]))
        assert isinstance(self.event_controller, mouse.Controller)
        self.event_controller.click(event["event_key"])


class MoveEvent(Event):
    def do(self, event):
        print(
            "move to ({0}, {1})".format(
                event["position_x"],
                event["position_y"]))
        assert isinstance(self.event_controller, mouse.Controller)
        self.event_controller.position=(
    event["position_x"], event["position_y"])


class ScrollEvent(Event):
    def do(self, event):
        assert isinstance(self.event_controller, mouse.Controller)
        assert event["event_type"] == "mouse_scroll"
        assert isinstance(event["position_y"], int)

        dx=event["position_x"] * 120
        dy=event["position_y"] * 120

        self.event_controller.scroll(dx, dy)
        print(
            "{0}-scroll to ({1}, {2})".format(
                event["event_key"],
                event["position_x"],
                event["position_y"]))


class MousePress(PressEvent):
    def __init__(self):
        super().__init__()
        self.event_controller=mouse.Controller()

    def do(self, event):
        MouseMove().do(event)

        super().do(event)


class MouseRelease(ReleaseEvent):
    def __init__(self):
        super().__init__()
        self.event_controller=mouse.Controller()

    def do(self, event):
        MouseMove().do(event)

        super().do(event)


class MouseClick(ClickEvent):

    def __init__(self):
        super().__init__()
        self.event_controller=mouse.Controller()

    def do(self, event):
        MouseMove().do(event)

        super().do(event)


class MouseMove(MoveEvent):
    def __init__(self):
        super().__init__()
        self.event_controller=mouse.Controller()


class MouseScroll(ScrollEvent):
    def __init__(self):
        super().__init__()
        self.event_controller=mouse.Controller()


class KeyboardPress(PressEvent):
    def __init__(self):
        super().__init__()
        self.event_controller=keyboard.Controller()


class KeyboardRelease(ReleaseEvent):
    def __init__(self):
        super().__init__()
        self.event_controller=keyboard.Controller()


class Unpack(object):
    def unpack(self, event):
        window_dict=event["window"]
        if window_dict:
            assert isinstance(window_dict["left"], int)
            assert isinstance(window_dict["top"], int)
            assert isinstance(window_dict["left"], int)
            assert isinstance(window_dict["width"], int)
            assert isinstance(window_dict["title"], str)
            assert isinstance(window_dict["class_name"], str)

            assert isinstance(event["event_time"], float)
            print(window_dict["title"])
            WindowEvent().set_window(event)

        return event


class MouseMoveUnpack(Unpack):
    def unpack(self, event):
        super().unpack(event)
        assert pyautogui.onScreen(event["position_x"], event["position_y"])
        return event


class MousePressUnpack(Unpack):
    def unpack(self, event):
        super().unpack(event)
        try:
            event["event_key"]=eval(event["event_key"])
        except NameError:
            event["event_key"]=event["event_key"]
        assert isinstance(event["event_key"], Button)

        assert pyautogui.onScreen(event["position_x"], event["position_y"])
        return event


class MouseReleaseUnpack(MousePressUnpack):
    def unpack(self, event):
        return super().unpack(event)


class MouseScrollUnpack(Unpack):
    def unpack(self, event):
        super().unpack(event)
        assert isinstance(event["dx"], int)
        assert isinstance(event["dy"], int)
        return event


class KeyboardPressUnpack(Unpack):
    def unpack(self, event):
        super().unpack(event)
        try:
            event["event_key"]=eval(event["event_key"])
        except NameError:
            event["event_key"] = event["event_key"]
        assert isinstance(event["event_key"], Key) or isinstance(event["event_key"], str)

        return event


class KeyboardReleaseUnpack(KeyboardPressUnpack):
    def unpack(self, event):
        return super().unpack(event)


class UnpackProduct(object):
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
            return MouseMoveUnpack()
        elif event_type == "mouse_press":
            return MousePressUnpack()
        elif event_type == "mouse_release":
            return MouseReleaseUnpack()
        elif event_type == "mouse_scroll":
            return MouseScrollUnpack()
        elif event_type == "keyboard_press":
            return KeyboardPressUnpack()
        elif event_type == "keyboard_release":
            return KeyboardReleaseUnpack()


class Unpacking(object):
    def __init__(self):
        self._unpack_product_create_method= UnpackProduct().create

    def unpacking(self, event):
        assert isinstance(event, dict)
        print(event)
        event= self._unpack_product_create_method(event["event_type"]).unpack(event)
        return event


class EventProduct(object):
    @staticmethod
    def create(event_type):
        """
        :param event_type in [
            "mouse_move",
            "mouse_press",
            "mouse_release",
            "mouse_scroll",
            "keyboard_press",
            "keyboard_release"]
        :return:
        """
        assert event_type in [
            "mouse_move",
            "mouse_press",
            "mouse_release",
            "mouse_scroll",
            "keyboard_press",
            "keyboard_release"]
        if event_type == "mouse_move":
            return MouseMove()
        elif event_type == "mouse_press":
            return MousePress()
        elif event_type == "mouse_release":
            return MouseRelease()
        elif event_type == "mouse_scroll":
            return MouseScroll()
        elif event_type == "keyboard_press":
            return KeyboardPress()
        elif event_type == "keyboard_release":
            return KeyboardRelease()


class PlayBack(Thread):
    def __init__(self):
        super().__init__()

    @staticmethod
    def open_event():
        with open("events.yaml", 'r') as f:
            events= yaml.safe_load(f)
            # assert isinstance(events, list)
        return events

    def run(self):
        events= self.open_event()
        for event in events:
            # print(event)
            now_event= Unpacking().unpacking(event)
            # print(now_event)
            EventProduct().create(now_event["event_type"]).do(now_event)
            sleep(now_event["event_time"])


if __name__ == '__main__':
    PlayBack().start()
