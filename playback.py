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


class Motion(object):
    def __init__(self):
        self.device = None

    def do(self, motion):
        assert isinstance(motion, dict)


class PressMotion(Motion):
    def do(self, motion):
        print("{0}-press".format(motion["motion"]))
        self.device.press(motion["motion"])


class ReleaseMotion(Motion):
    def do(self, motion):
        print("{0}-release".format(motion["motion"]))
        self.device.release(motion["motion"])


class ClickMotion(Motion):
    def do(self, motion):
        print("{0}-click".format(motion["motion"]))
        assert isinstance(self.device, mouse.Controller)
        self.device.click(motion["motion"])


class MoveMotion(Motion):
    def do(self, motion):
        print(
            "{0}-move to ({1}, {2})".format(
                motion["motion"],
                motion["position_x"],
                motion["position_y"]))
        assert isinstance(self.device, mouse.Controller)
        self.device.position = (motion["position_x"], motion["position_y"])


class ScrollMotion(Motion):
    def do(self, motion):
        assert isinstance(self.device, mouse.Controller)
        assert motion["device"] == "mouse_scroll"
        assert isinstance(motion["position_y"], int)

        dx = motion["position_x"] * 120
        dy = motion["position_y"] * 120

        self.device.scroll(dx, dy)
        print(
            "{0}-scroll to ({1}, {2})".format(
                motion["motion"],
                motion["position_x"],
                motion["position_y"]))


class MousePress(PressMotion):
    def __init__(self):
        super().__init__()
        self.device = mouse.Controller()

    def do(self, motion):
        MouseMove().do(motion)

        super().do(motion)


class MouseRelease(ReleaseMotion):
    def __init__(self):
        super().__init__()
        self.device = mouse.Controller()

    def do(self, motion):
        MouseMove().do(motion)

        super().do(motion)


class MouseClick(ClickMotion):

    def __init__(self):
        super().__init__()
        self.device = mouse.Controller()

    def do(self, motion):
        MouseMove().do(motion)

        super().do(motion)


class MouseMove(MoveMotion):
    def __init__(self):
        super().__init__()
        self.device = mouse.Controller()


class MouseScroll(ScrollMotion):
    def __init__(self):
        super().__init__()
        self.device = mouse.Controller()


class KeyboardPress(PressMotion):
    def __init__(self):
        super().__init__()
        self.device = keyboard.Controller()


class KeyboardRelease(ReleaseMotion):
    def __init__(self):
        super().__init__()
        self.device = keyboard.Controller()


class Unpacking(object):
    @staticmethod
    def unpacking(motion):
        """
        :param {
                "device": "mouse",
                "motion": str(button),
                "position_x": x,
                "position_y": y,
                "motion time": now_time,
                "pressed": pressed}
        :return: unpacking motion
        """
        assert isinstance(motion, dict)
        try:
            assert motion["device"] in [
                "mouse", "keyboard", "mouse_move", "mouse_scroll"]
            assert isinstance(motion["motion time"], float)
            assert isinstance(motion["position_x"], int)
            assert isinstance(motion["position_y"], int)
            assert isinstance(motion["pressed"], bool)

            try:
                motion["motion"] = eval(motion["motion"])
            except NameError:
                motion["motion"] = motion["motion"]

            if isinstance(motion["motion"], int):
                motion["motion"] = str(motion["motion"])
            print(motion)

            assert (isinstance(motion["motion"], Key) or
                    isinstance(motion["motion"], Button) or
                    isinstance(motion["motion"], str))
            return motion

        except KeyError:
            raise KeyError


class MotionProduct(object):
    @staticmethod
    def create(motion):
        """
        :param motion: {
                "device": "mouse",
                "motion": Key,
                "position_x": 0,
                "position_y": 0,
                "motion time": 0.1,
                "pressed": true}
        :return:
        """
        assert isinstance(motion, dict)
        if motion["device"] == "mouse":
            if motion["pressed"]:
                return MousePress()
            else:
                return MouseRelease()
        elif motion["device"] == "keyboard":
            if motion["pressed"]:
                return KeyboardPress()
            else:
                return KeyboardRelease()
        elif motion["device"] == "mouse_move":
            return MouseMove()
        elif motion["device"] == "mouse_scroll":
            return MouseScroll()


class PlayBack(Thread):
    def __init__(self):
        super().__init__()

    @staticmethod
    def open_motion():
        with open("mouse.yaml", 'r') as f:
            motions = yaml.safe_load(f)
            # assert isinstance(motions, list)
        return motions

    def run(self):
        motions = self.open_motion()
        for motion in motions:
            now_motion = Unpacking().unpacking(motion)
            MotionProduct().create(now_motion).do(now_motion)
            sleep(now_motion["motion time"])


if __name__ == '__main__':
    PlayBack().start()
