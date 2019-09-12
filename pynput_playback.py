#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   pynput_playback.py
@Time    :   2019/09/06 17:00:10
@Author  :   MasterLin
@Version :   1.0
@Contact :   15651838825@163.com
@License :   (C)Copyright 2018-2019, CASI
@Desc    :   None
"""

# here put the import lib

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

from script_setup import get_script_setting

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
        try:
            with open(script_path, 'r', encoding='utf-8') as events_file_ref:
                # print(events_file_ref)
                print("event loading...")
                return yaml.safe_load(events_file_ref)
        except Exception as e:
            logger.error(e)


class Playback(Thread):
    def __init__(self, this_queue: Queue):
        super().__init__()
        self._this_queue = this_queue
        script = LoadFromYaml().save_load(software_config.using_script)
        try:
            script_conf = script["script config"]
            self._script_conf = get_script_setting(script_conf)
        except (TypeError, KeyError) as e:
            logger.warning('script config is illegal')
            logger.warning(type(e))
            self._script_conf = None
        logger.info(self._script_conf)
        self._unpack_method = Unpack().unpack
        self._action_product_method = ActionProduct().product
        # ------------------------------------------------------
        # script setting
        self.script_delay = 1
        self.script_index = 0
        self.script_list = range(1)
        self.script_val1 = '0'
        self.script_val2 = '0'
        self.script_val3 = '0'
        self.script_val4 = '0'
        self.script_val5 = '0'
        self.script_val6 = '0'
        self.script_val7 = '0'
        self.script_val8 = '0'
        self.script_val9 = '0'
        self.script_val10 = '0'

        self.update_script_setting()

    def update_script_setting(self):
        if not self._script_conf:
            return None
        head = self._script_conf['head']
        # ---------------------------------------------------------
        # get setting string
        try:
            self.script_delay = head['script_delay']
        except KeyError:
            logger.error("script delay must be defined.")
            raise UserWarning("script delay must be defined.")

        try:
            self.script_list = head['script_list']
        except KeyError:
            logger.error("script list list be defined.")
            raise UserWarning("script list must be defined.")

        try:
            self.script_val1 = head['script_val1']
        except KeyError:
            pass

        try:
            self.script_val2 = head['script_val2']
        except KeyError:
            pass

        try:
            self.script_val3 = head['script_val3']
        except KeyError:
            pass

        try:
            self.script_val4 = head['script_val4']
        except KeyError:
            pass

        try:
            self.script_val5 = head['script_val5']
        except KeyError:
            pass

        try:
            self.script_val6 = head['script_val6']
        except KeyError:
            pass

        try:
            self.script_val7 = head['script_val7']
        except KeyError:
            pass

        try:
            self.script_val8 = head['script_val8']
        except KeyError:
            pass

        try:
            self.script_val9 = head['script_val9']
        except KeyError:
            pass

        try:
            self.script_val10 = head['script_val10']
        except KeyError:
            pass

        # -----------------------------------------------------
        # try get value from string
        try:
            self.script_delay = eval(self.script_delay)
        except (NameError, TypeError):
            pass
        logger.info(self.script_delay)
        try:
            self.script_list = eval(self.script_list)
        except (NameError, TypeError):
            pass

        try:
            self.script_val1 = eval(self.script_val1)
        except (NameError, TypeError):
            pass

        try:
            self.script_val2 = eval(self.script_val2)
        except (NameError, TypeError):
            pass

        try:
            self.script_val3 = eval(self.script_val3)
        except (NameError, TypeError):
            pass

        try:
            self.script_val4 = eval(self.script_val4)
        except (NameError, TypeError):
            pass

        try:
            self.script_val5 = eval(self.script_val5)
        except (NameError, TypeError):
            pass

        try:
            self.script_val6 = eval(self.script_val6)
        except (NameError, TypeError):
            pass

        try:
            self.script_val7 = eval(self.script_val7)
        except (NameError, TypeError):
            pass

        try:
            self.script_val8 = eval(self.script_val8)
        except (NameError, TypeError):
            pass

        try:
            self.script_val9 = eval(self.script_val9)
        except (NameError, TypeError):
            pass

        try:
            self.script_val10 = eval(self.script_val10)
        except (NameError, TypeError):
            pass

    @property
    def this_queue(self):
        return self._this_queue

    def run_core(self, script_path, script_dict: dict):
        logger.info("script dict{0}".format(script_dict))
        script = LoadFromYaml().save_load(script_path)
        # get events
        events = []
        user_inputs = []
        if script:
            events = script["script"]

        if script_dict:
            logger.info(self._script_conf)
            logger.info(self._script_conf)
            user_inputs = script_dict["script_inputs"]
            logger.error(user_inputs)
            # 用于eval 强迫症写这个勉强让自己接受下==
            script_list = self.script_list
            script_delay = self.script_delay
            script_index = self.script_index
            script_val1 = self.script_val1
            script_val2 = self.script_val2
            script_val3 = self.script_val3
            script_val4 = self.script_val4
            script_val5 = self.script_val5
            script_val6 = self.script_val6
            script_val7 = self.script_val7
            script_val8 = self.script_val8
            script_val9 = self.script_val9
            script_val10 = self.script_val10
            # 打印下，去掉warning... 你够了
            logger.info(script_val1)
            logger.info(script_val2)
            logger.info(script_val3)
            logger.info(script_val4)
            logger.info(script_val5)
            logger.info(script_val6)
            logger.info(script_val7)
            logger.info(script_val8)
            logger.info(script_val9)
            logger.info(script_val10)
            logger.info(script_list)
            logger.info(script_index)
            logger.info(script_delay)
            logger.info('start play')

        self.this_queue.put("__CONTINUE__")
        # event_cls = None
        i = 0
        for event in events:
            command = self.this_queue.get()
            if command == "__PLAYBACK_QUIT__":
                self.this_queue.put("__CONTINUE__")
                return True
            elif command == "__CONTINUE__":
                event_cls = self._unpack_method(event)
                logger.info(type(event_cls))
                action = self._action_product_method(event_cls.event_type)
                # logger.error(isinstance(event_cls, UserInputEvent))
                if isinstance(event_cls, UserInputEvent) and script_dict:
                    logger.info("message-{0}".format(event_cls.message))
                    user_input = ''
                    try:
                        user_input = user_inputs[i]
                        i += 1
                    except Exception as e:
                        logger.error(e)

                    try:
                        user_input = eval(user_input)
                    except Exception as e:
                        logger.error(e)
                    if user_input:
                        logger.error(user_input)
                        event_cls.message = str(user_input)
                    logger.info("message-{0}".format(event_cls.message))
                action.action(event_cls)

            self._this_queue.put("__CONTINUE__")
            # print("delay time:{0}".format(delay_time))
            sleep(event["time"] + 0.005)
        return False

    def run(self) -> None:
        keyboard_listener = KeyboardListener(playback_queue=self.this_queue)
        keyboard_listener.setDaemon(True)
        keyboard_listener.start()

        if not self._script_conf:
            self.run_core(software_config.using_script, {})
        else:
            res = False
            logger.info(self.script_list)
            for i in self.script_list:
                self.script_index = i
                logger.info(self.script_index)
                for script_dict in self._script_conf["scripts"]:
                    res = self.run_core(script_dict["script_name"],
                                        script_dict)
                    if res:
                        return None
                    sleep(eval(script_dict["delay"]))

                sleep(self.script_delay)
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
