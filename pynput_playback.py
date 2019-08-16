# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     hook_playback
   Description :
   Author :
   date：          2019/8/13
-------------------------------------------------
   Change Activity:
                   2019/8/13:
-------------------------------------------------
"""
__author__ = 'Lyl'

from software_init import Init
import yaml
from pynput.mouse import Button
from pynput.keyboard import KeyCode, Key

from pynput import mouse, keyboard
from threading import Thread
from queue import Queue

from pynput_record import EventProduct, Event
from time import sleep

software_init = Init()


class Action(object):
    def __init__(self):
        self.controller = None

    def action(self, event):
        assert isinstance(event, Event)


class MouseAction(Action):
    def __init__(self):
        super().__init__()
        self.controller = mouse.Controller()


class MouseClickAction(MouseAction):
    pass


class MouseClickPressAction(MouseClickAction):
    def action(self, event):
        assert isinstance(self.controller, mouse.Controller)
        MouseMoveAction().action(event)
        sleep(0.01)
        self.controller.press(event.button)


class MouseClickReleaseAction(MouseClickAction):
    def action(self, event):
        assert isinstance(self.controller, mouse.Controller)
        MouseMoveAction().action(event)
        sleep(0.01)
        self.controller.release(event.button)


class MouseMoveAction(MouseAction):
    def action(self, event):
        assert isinstance(self.controller, mouse.Controller)
        self.controller.position = event.position


class MouseScrollAction(MouseAction):
    def action(self, event):
        assert isinstance(self.controller, mouse.Controller)
        MouseMoveAction().action(event)
        sleep(0.01)
        dx, dy = event.wheel
        self.controller.scroll(dx * 100, dy * 100)


class KeyboardAction(Action):
    def __init__(self):
        super().__init__()
        self.controller = keyboard.Controller()


class KeyboardPressAction(KeyboardAction):
    def action(self, event):
        print(event.key)
        assert isinstance(self.controller, keyboard.Controller)
        try:
            self.controller.press(event.key)
        except BaseException as e:
            print(e)


class KeyboardReleaseAction(KeyboardAction):
    def action(self, event):
        print(event.key)
        assert isinstance(self.controller, keyboard.Controller)
        try:
            self.controller.release(event.key)
        except BaseException as e:
            print(e)


class ActionProduct(object):
    @staticmethod
    def product(event_type):
        assert event_type in ["mouse move",
                              "mouse click press",
                              "mouse click release",
                              "mouse scroll",
                              "keyboard press",
                              "keyboard release"]
        if event_type == "mouse move":
            return MouseMoveAction()
        elif event_type == "mouse click press":
            return MouseClickPressAction()
        elif event_type == "mouse click release":
            return MouseClickReleaseAction()
        elif event_type == "mouse scroll":
            return MouseScrollAction()
        elif event_type == "keyboard press":
            return KeyboardPressAction()
        elif event_type == "keyboard release":
            return KeyboardReleaseAction()


class Unpack(object):
    @staticmethod
    def unpack(event):
        event_type = event["event type"]
        event_cls = EventProduct().product(event_type)
        if event_type == "mouse move":
            event_cls.set_time(event["time"])
            event_cls.set_window(event["window"])

            event_cls.set_position(event["x"], event["y"])

        elif event_type == "mouse click press":
            event_cls.set_time(event["time"])
            event_cls.set_window(event["window"])

            event_cls.set_position(event["x"], event["y"])
            event_cls.set_button(eval(event["button"]))

        elif event_type == "mouse click release":
            event_cls.set_time(event["time"])
            event_cls.set_window(event["window"])

            event_cls.set_position(event["x"], event["y"])

            button = eval(event["button"])
            event_cls.set_button(button)

        elif event_type == "mouse click scroll":
            event_cls.set_time(event["time"])
            event_cls.set_window(event["window"])

            event_cls.set_position(event["x"], event["y"])
            event_cls.set_wheel(event["dx"], event["dy"])

        elif event_type == "keyboard press":
            event_cls.set_time(event["time"])
            event_cls.set_window(event["window"])

            try:
                key = eval(event["key"])
            except BaseException as e:
                print(e)
                key = event["key"]
            if isinstance(key, int):
                key = str(key)
            event_cls.set_key(key)

        elif event_type == "keyboard release":
            event_cls.set_time(event["time"])
            event_cls.set_window(event["window"])

            try:
                key = eval(event["key"])
            except BaseException as e:
                print(e)
                key = str(event["key"])
            if isinstance(key, int):
                key = str(key)
            event_cls.set_key(key)
        return event_cls


class LoadFromYaml(object):
    @staticmethod
    def save_load():
        with open(software_init.default_record_file, 'r') as events_file_ref:
            print("event loading...")
            return yaml.safe_load(events_file_ref)


class Playback(object):
    @staticmethod
    def run(playback_queue, interface_queue):
        assert isinstance(playback_queue, Queue)
        assert isinstance(interface_queue, Queue)

        KeyboardListener(playback_queue=playback_queue).start()

        unpack_method = Unpack().unpack
        action_product_method = ActionProduct().product
        events = LoadFromYaml().save_load()
        last_time = events[0]["time"]
        playback_queue.put("__CONTINUE__")
        for event in events:
            command = playback_queue.get()
            if command == "__PLAYBACK_QUIT__":
                break
            elif command == "__CONTINUE__":
                event_cls = unpack_method(event)
                print(event_cls.event_type)
                action = action_product_method(event_cls.event_type)
                action.action(event_cls)

                delay_time = (event["time"] - last_time)
                last_time = event["time"]
                sleep(delay_time)
            # print("delay time:{0}".format(delay_time))
            playback_queue.put("__CONTINUE__")
            sleep(0.01)
        print("playback done")


class KeyboardListener(Thread):
    def __init__(self, playback_queue):
        super().__init__()
        assert isinstance(playback_queue, Queue)
        self._playback_queue = playback_queue

    def on_press(self, key):
        if key == keyboard.Key.f12:
            self._playback_queue.put("__PLAYBACK_QUIT__")
            print("user quit playback")
            return False

    def run(self):
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()


class LaunchPlayback(Thread):
    def __init__(self, playback_queue, interface_queue=None):
        super().__init__()
        assert isinstance(
            playback_queue,
            Queue) and isinstance(
            interface_queue,
            Queue)
        self._playback_queue = playback_queue
        self._interface_queue = interface_queue

    def run(self):
        Playback().run(playback_queue=self._playback_queue,
                       interface_queue=self._interface_queue)
        self._interface_queue.put(("__PLAYBACK_QUIT__", None))


if __name__ == '__main__':
    Playback().run(playback_queue=Queue(),
                   interface_queue=Queue())
