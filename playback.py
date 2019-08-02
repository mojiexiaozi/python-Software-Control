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


from time import sleep


class Event(object):
    def __init__(self):
        self.event_type = None

    def do(self, event):
        assert isinstance(event, dict)


class PressEvent(Event):
    def do(self, event):
        print("{0}-press".format(event["event"]))
        self.event_type.press(event["event"])


class ReleaseEvent(Event):
    def do(self, event):
        print("{0}-release".format(event["event"]))
        self.event_type.release(event["event"])


class ClickEvent(Event):
    def do(self, event):
        print("{0}-click".format(event["event"]))
        assert isinstance(self.event_type, mouse.Controller)
        self.event_type.click(event["event"])


class MoveEvent(Event):
    def do(self, event):
        print(
            "{0}-move to ({1}, {2})".format(
                event["event"],
                event["position_x"],
                event["position_y"]))
        assert isinstance(self.event_type, mouse.Controller)
        self.event_type.position = (event["position_x"], event["position_y"])


class ScrollEvent(Event):
    def do(self, event):
        assert isinstance(self.event_type, mouse.Controller)
        assert event["event_type"] == "mouse_scroll"
        assert isinstance(event["position_y"], int)

        dx = event["position_x"] * 120
        dy = event["position_y"] * 120

        self.event_type.scroll(dx, dy)
        print(
            "{0}-scroll to ({1}, {2})".format(
                event["event"],
                event["position_x"],
                event["position_y"]))


class MousePress(PressEvent):
    def __init__(self):
        super().__init__()
        self.event_type = mouse.Controller()

    def do(self, event):
        MouseMove().do(event)

        super().do(event)


class MouseRelease(ReleaseEvent):
    def __init__(self):
        super().__init__()
        self.event_type = mouse.Controller()

    def do(self, event):
        MouseMove().do(event)

        super().do(event)


class MouseClick(ClickEvent):

    def __init__(self):
        super().__init__()
        self.event_type = mouse.Controller()

    def do(self, event):
        MouseMove().do(event)

        super().do(event)


class MouseMove(MoveEvent):
    def __init__(self):
        super().__init__()
        self.event_type = mouse.Controller()


class MouseScroll(ScrollEvent):
    def __init__(self):
        super().__init__()
        self.event_type = mouse.Controller()


class KeyboardPress(PressEvent):
    def __init__(self):
        super().__init__()
        self.event_type = keyboard.Controller()


class KeyboardRelease(ReleaseEvent):
    def __init__(self):
        super().__init__()
        self.event_type = keyboard.Controller()


class Unpacking(object):
    @staticmethod
    def unpacking(event):
        """
        :param {
                "event_type": "mouse",
                "event": str(button),
                "position_x": x,
                "position_y": y,
                "event_time": now_time,
                "pressed": pressed}
        :return: unpacking event
        """
        assert isinstance(event, dict)
        try:
            assert event["event_type"] in [
                "mouse", "keyboard", "mouse_move", "mouse_scroll"]
            assert isinstance(event["event_time"], float)
            assert isinstance(event["position_x"], int)
            assert isinstance(event["position_y"], int)
            assert isinstance(event["pressed"], bool)

            try:
                event["event"] = eval(event["event"])
            except NameError:
                event["event"] = event["event"]

            if isinstance(event["event"], int):
                event["event"] = str(event["event"])
            print(event)

            assert (isinstance(event["event"], Key) or
                    isinstance(event["event"], Button) or
                    isinstance(event["event"], str))
            return event

        except KeyError:
            raise KeyError


class EventProduct(object):
    @staticmethod
    def create(event):
        """
        :param event: {
                "event_type": "mouse",
                "event": Key,
                "position_x": 0,
                "position_y": 0,
                "event_time": 0.1,
                "pressed": true}
        :return:
        """
        assert isinstance(event, dict)
        if event["event_type"] == "mouse":
            if event["pressed"]:
                return MousePress()
            else:
                return MouseRelease()
        elif event["event_type"] == "keyboard":
            if event["pressed"]:
                return KeyboardPress()
            else:
                return KeyboardRelease()
        elif event["event_type"] == "mouse_move":
            return MouseMove()
        elif event["event_type"] == "mouse_scroll":
            return MouseScroll()


class PlayBack(Thread):
    def __init__(self):
        super().__init__()

    @staticmethod
    def open_event():
        with open("mouse.yaml", 'r') as f:
            events = yaml.safe_load(f)
            # assert isinstance(events, list)
        return events

    def run(self):
        events = self.open_event()
        for event in events:
            now_event = Unpacking().unpacking(event)
            EventProduct().create(now_event).do(now_event)
            sleep(now_event["event_time"])


if __name__ == '__main__':
    PlayBack().start()
