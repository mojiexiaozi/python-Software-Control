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

from software_init import Init, SoftwareConfig
import yaml
from pynput.mouse import Button
from pynput.keyboard import KeyCode, Key

from pynput import mouse, keyboard
from threading import Thread
from queue import Queue

from pynput_record import EventProduct, Event, UserInputEvent
from time import sleep
from log import Logger
import os

from script_setup import *

software_config = Init().software_config
logger = Logger().get_logger(__name__)
assert isinstance(software_config, SoftwareConfig)


class Action(object):
    def __init__(self):
        self._controller = None

    @property
    def controller(self):
        return self._controller

    @controller.setter
    def controller(self, controller):
        self._controller = controller

    def action(self, event):
        assert isinstance(event, Event)


class UserInputAction(Action):
    def __init__(self):
        super().__init__()
        self.controller = keyboard.Controller()

    def action(self, event):
        assert isinstance(event, UserInputEvent)
        self.controller.type(event.message)


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
        except NameError as e:
            print(e)
            print("{0}-press-error".format(event.key))


class KeyboardReleaseAction(KeyboardAction):
    def action(self, event):
        print(event.key)
        assert isinstance(self.controller, keyboard.Controller)
        try:
            self.controller.release(event.key)
        except NameError as e:
            print(e)
            print("{0}-release-error".format(event.key))


class ActionProduct(object):
    @staticmethod
    def product(event_type):
        assert event_type in [
            "mouse move", "mouse click press", "mouse click release",
            "mouse scroll", "keyboard press", "keyboard release", "user input"
        ]
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
        elif event_type == "user input":
            return UserInputAction()


class Unpack(object):
    @staticmethod
    def unpack(event):
        event_type = event["event type"]
        event_cls = EventProduct().product(event_type)
        if event_type == "mouse move":
            event_cls.time = event["time"]
            event_cls.window = event["window"]

            event_cls.position = (event["x"], event["y"])

        elif event_type in ["mouse click press", "mouse click release"]:
            event_cls.time = event["time"]
            event_cls.window = event["window"]

            event_cls.position = (event["x"], event["y"])

            button = eval(event["button"])
            assert isinstance(button, Button)
            event_cls.button = button

        elif event_type == "mouse click scroll":
            event_cls.time = event["time"]
            event_cls.window = event["window"]

            event_cls.position = event["x"], event["y"]
            event_cls.wheel = (event["dx"], event["dy"])

        elif event_type in ["keyboard press", "keyboard release"]:
            event_cls.time = event["time"]
            event_cls.window = event["window"]

            try:
                key = eval(event["key"])
            except (NameError, SyntaxError):
                key = str(event["key"])
            if isinstance(key, int):
                key = str(key)

            assert isinstance(key, KeyCode) or isinstance(
                key, Key) or isinstance(key, str)
            event_cls.key = key

        elif event_type == "user input":
            event_cls.time = event["time"]
            event_cls.message = event["message"]
            event_cls.window = event["window"]

        return event_cls


class LoadFromYaml(object):
    @staticmethod
    def save_load(script_path=software_config.using_script):
        os.chdir(software_config.software_dir)
        os.chdir(software_config.scripts_dir)
        if not os.path.exists(script_path):
            logger.warning("{0} does not exists".format(script_path))
            return None

        with open(script_path, 'r') as events_file_ref:
            # print(events_file_ref)
            print("event loading...")
            return yaml.safe_load(events_file_ref)


class Playback(Thread):
    def __init__(self, this_queue: Queue):
        super().__init__()
        self._this_queue = this_queue

    @property
    def this_queue(self):
        return self._this_queue

    def run(self) -> None:
        keyboard_listener = KeyboardListener(playback_queue=self.this_queue)
        keyboard_listener.setDaemon(True)
        keyboard_listener.start()

        unpack_method = Unpack().unpack
        action_product_method = ActionProduct().product
        script = LoadFromYaml().save_load(software_config.using_script)
        events = script["script"]

        self.this_queue.put("__CONTINUE__")

        # event_cls = None
        for event in events:
            command = self.this_queue.get()
            if command == "__PLAYBACK_QUIT__":
                break
            elif command == "__CONTINUE__":
                event_cls = unpack_method(event)
                print(event_cls.event_type)
                action = action_product_method(event_cls.event_type)
                action.action(event_cls)

                self._this_queue.put("__CONTINUE__")
            # print("delay time:{0}".format(delay_time))
            sleep(event["time"] + 0.005)
        print("playback done")


class KeyboardListener(Thread):
    def __init__(self, playback_queue):
        super().__init__()
        # assert isinstance(playback_queue, Queue)
        self._playback_queue = playback_queue

    def on_press(self, key):
        if key == keyboard.Key.f11:
            self._playback_queue.put("__PLAYBACK_QUIT__")
            print("user quit playback")
            return False

    def run(self):
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()


# class LaunchPlayback(Thread):
#     def __init__(self, playback_queue, interface_queue=None):
#         super().__init__()
#         self._playback_queue = playback_queue
#         self._interface_queue = interface_queue
#
#     def run(self):
#         Playback().run(playback_queue=self._playback_queue,
#                        interface_queue=self._interface_queue)
#         self._interface_queue.put(("__PLAYBACK_QUIT__", None))


if __name__ == '__main__':
    pass
    # launcher = LaunchPlayback(Queue(), Queue())
    # launcher.start()
    # launcher.join()
