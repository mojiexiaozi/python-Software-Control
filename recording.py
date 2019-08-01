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

from pynput import mouse
import yaml
from queue import Queue
from time import time
from threading import Thread


from pynput import keyboard


class KeyBoardMonitoring(Thread):
    def __init__(self, queue_loc, mouse_control):
        super().__init__()
        self._queue = queue_loc
        self._mouse_control = mouse_control
        self._is_ctrl_pressed = False
        self._is_shift_pressed = False
        self._is_alt_pressed = False
        self._is_recording = True

    def recording(self, key, press):
        if key == keyboard.Key.shift:
            if self._is_shift_pressed:
                self._is_recording = False
            else:
                self._is_recording = True
                self._is_shift_pressed = press
        elif key in [keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt_gr]:
            if self._is_alt_pressed:
                self._is_recording = False
            else:
                self._is_recording = True
                self._is_alt_pressed = press
        elif key in [keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r]:
            if self._is_ctrl_pressed:
                self._is_recording = False
            else:
                self._is_recording = True
                self._is_ctrl_pressed = press
        else:
            self._is_recording = True

        if self._is_recording:
            now_time = time()
            try:
                key_value = key.char
            except AttributeError:
                # print(e)s
                key_value = str(key)

            keyboard_info = {
                "device": "keyboard",
                "motion": key_value,
                "position_x": 0,
                "position_y": 0,
                "motion time": now_time,
                "pressed": press}
            self._queue.put(keyboard_info)
            print(keyboard_info)

    def on_press(self, key):
        self.recording(key, True)

    def on_release(self, key):
        if key in [
                keyboard.Key.ctrl,
                keyboard.Key.ctrl_l,
                keyboard.Key.ctrl_r]:
            self._is_ctrl_pressed = False
        elif key == keyboard.Key.shift:
            self._is_shift_pressed = False
        elif key in [keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt_gr]:
            self._is_alt_pressed = False
        elif key == keyboard.Key.f8:
            # Stop listener
            self._mouse_control.click(mouse.Button.middle, 1)
            return False

        self.recording(key, False)

    # Collect events until released
    def run(self):
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()


class MouseMonitoring(Thread):
    def __init__(self, queue_loc, keyboard_control):
        super().__init__()
        # self._button_pressed = False
        self._queue = queue_loc
        self._keyboard_control = keyboard_control

    def recoding(self, x, y, button, pressed, device):

        assert (device in ["mouse", "mouse_move", "mouse_scroll"])
        now_time = time()
        mouse_info = {
            "device": device,
            "motion": str(button),
            "position_x": x,
            "position_y": y,
            "motion time": now_time,
            "pressed": pressed}

        self._queue.put(mouse_info)
        print(mouse_info)

    def on_move(self, x, y):
        # if self._button_pressed:
        self.recoding(x, y, mouse.Button.left, False, "mouse_move")

    def on_click(self, x, y, button, pressed):
        # self._button_pressed = pressed
        if button == mouse.Button.middle:
            # Stop listener
            self._queue.put(None)
            self._keyboard_control.press(keyboard.Key.f8)
            self._keyboard_control.release(keyboard.Key.f8)

            return False
        self.recoding(x, y, button, pressed, "mouse")

    def on_scroll(self, x, y, dx, dy):
        print(x, y)
        self.recoding(dx, dy, mouse.Button.left, False, "mouse_scroll")

    def run(self):
        # Collect events until released
        with mouse.Listener(on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll) as listener:
            # listener.start()
            listener.join()


class Recording(Thread):
    def __init__(self):
        super().__init__()
        self._queue = Queue()
        self._keyboard_control = keyboard.Controller()
        self._mouse_control = mouse.Controller()

    def run(self):
        mouse_listener = MouseMonitoring(self._queue, self._keyboard_control)
        keyboard_listener = KeyBoardMonitoring(
            self._queue, self._mouse_control)

        mouse_listener.start()
        keyboard_listener.start()

        with open('mouse.yaml', 'w') as f:
            info_list = []
            while True:
                info = self._queue.get()
                # print(info)
                if not info:
                    break
                else:
                    info_list.append(info)

            list_len = len(info_list)

            for i in range(1, list_len):
                motion_time = (info_list[list_len - i]["motion time"] -
                               info_list[list_len - i - 1]["motion time"])
                info_list[list_len - i]["motion time"] = motion_time

            if info_list:
                info_list[0]["motion time"] = 0.1
                yaml.safe_dump(info_list, f)


if __name__ == '__main__':
    recording = Recording()
    recording.start()
    recording.join()
