#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   extract_input_message.py
@Time    :   2019/08/28 17:59:29
@Author  :   MasterLin
@Version :   1.0
@Contact :   15651838825@163.com
@License :   (C)Copyright 2018-2019, CASI
@Desc    :   None
"""
from pynput.keyboard import Key

from string import ascii_lowercase
from pynput_playback import LoadFromYaml, Unpack
from pynput_record import (KeyboardEvent, KeyboardPress, MouseEvent,
                           UserInputEvent, UserInputEventProduct)
from log import Logger

logger = Logger().get_logger(__name__)


class KeyConstant(object):
    def __init__(self):
        self._MESSAGE_KEY = [
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c',
            'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p',
            'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C',
            'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
            'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '!', '"', '#',
            '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', ':',
            ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{',
            '|', '}', '~', ' ', '\t', '\n', '\r', '\x0b', '\x0c'
        ]
        self._CTRL_KEY = [Key.ctrl, Key.ctrl_l, Key.ctrl_r]
        self._ALT_KEY = [Key.alt, Key.alt_gr, Key.alt_l, Key.alt_r]
        self._WIN_KEY = [Key.cmd, Key.cmd_l, Key.cmd_r]
        self._SHIFT_KEY = [Key.shift, Key.shift_l, Key.shift_r]
        self._SHIFT_KEY_CHANGE = {
            '0': ')',
            '1': '!',
            '2': '@',
            '3': '#',
            '4': '$',
            '5': '%',
            '6': '^',
            '7': '&',
            '8': '*',
            '9': '(',
            '`': '~',
            '[': '{',
            ']': '}',
            '\\': '|',
            ';': ':',
            "'": '"',
            ',': '<',
            '.': '>',
            '/': '?'
        }

    @property
    def shift_key_change(self):
        return self._SHIFT_KEY_CHANGE

    @property
    def message_key(self):
        return self._MESSAGE_KEY

    @property
    def ctrl_key(self):
        return self._CTRL_KEY

    @property
    def alt_key(self):
        return self._ALT_KEY

    @property
    def shift_key(self):
        return self._SHIFT_KEY

    @property
    def win_key(self):
        return self._WIN_KEY


class ExtractInputMessage(object):
    def __init__(self):
        self._events_cls = None
        self._user_input_message = []
        self._ctrl_pressed = False
        self._alt_pressed = False
        self._win_pressed = False
        self._shift_pressed = False
        self._KEY_CONSTANT = KeyConstant()

        # Using for extract
        self._message_recording = False
        self._message = ""
        self._first_event_cls = None
        self._last_event_cls = None

    @property
    def events_cls(self):
        return self._events_cls

    @property
    def user_input_message(self):
        return self._user_input_message

    @events_cls.setter
    def events_cls(self, events_cls):
        assert isinstance(events_cls, list)
        assert isinstance(events_cls[0], KeyboardEvent) or isinstance(
            events_cls[0], MouseEvent)

        self._events_cls = events_cls

    def get_shift_key(self, event):
        """ change to shift key if shift is pressed """
        assert isinstance(event, KeyboardEvent)
        if str(event.key) in ascii_lowercase:
            if self._shift_pressed ^ event.caps_lk:
                event.key.lower()

        if self._shift_pressed:
            if event.key in self._KEY_CONSTANT.shift_key_change:
                event.key = self._KEY_CONSTANT.shift_key_change[event.key]
        return event.key

    def message_recorded_init(self):
        self._message_recording = False
        self._message = ""
        self._first_event_cls = None
        self._last_event_cls = None

    def pressed_verify(self, event):
        assert isinstance(event, KeyboardEvent)
        if event.key in self._KEY_CONSTANT.ctrl_key:
            self._ctrl_pressed = isinstance(event, KeyboardPress)

        elif event.key in self._KEY_CONSTANT.alt_key:
            self._alt_pressed = isinstance(event, KeyboardPress)

        elif event.key in self._KEY_CONSTANT.win_key:
            self._win_pressed = isinstance(event, KeyboardPress)

        elif event.key in self._KEY_CONSTANT.shift_key:
            self._shift_pressed = isinstance(event, KeyboardPress)

    def recording_verify(self, event):
        if self._ctrl_pressed or self._alt_pressed or self._win_pressed:
            self._message_recording = False
        elif event.key in [Key.enter, Key.esc]:
            self._message_recording = False
        elif (isinstance(event, KeyboardPress) and event.window is not None
              and not self._message_recording):

            if event.key in self._KEY_CONSTANT.message_key:
                self._message_recording = True
            elif event.key in self._KEY_CONSTANT.shift_key:
                self._message_recording = True

        elif self._message_recording:
            assert isinstance(self._first_event_cls, KeyboardPress)
            if event.window is None:
                self._message_recording = False
            elif event.window["class name"] != self._first_event_cls.window[
                    "class name"]:
                self._message_recording = False
            # print(event.window, self._first_event_cls.window)
        # print(self._message_recording)
        # print(event.window, event.key)

    def update_first_event_cls(self, event):
        if self._first_event_cls is None:
            self._first_event_cls = event

    def record_message(self, event):
        if isinstance(event, KeyboardPress):
            event.key = self.get_shift_key(event)
            if event.key == Key.backspace:
                self._message = self._message[:-1]
            elif event.key == Key.space:
                self._message += ' '
            elif event.key in self._KEY_CONSTANT.message_key:
                self._message += event.key

    def extract(self):
        assert isinstance(self.events_cls, list)

        self.message_recorded_init()

        for event in self.events_cls:
            if isinstance(event, KeyboardEvent):

                self.pressed_verify(event)
                self.recording_verify(event)
                # print(self._message_recording, event.key)

                if self._message_recording:
                    self.update_first_event_cls(event)
                    self.record_message(event)
                else:
                    if self._message:
                        self._user_input_message.append(
                            (self._message, self._first_event_cls,
                             self._last_event_cls))
                    self.message_recorded_init()

                self._last_event_cls = event
        if self._message:
            self._user_input_message.append(
                (self._message, self._first_event_cls, self._last_event_cls))


class LaunchExtractor(object):
    @staticmethod
    def do(script_path):
        unpack_method = Unpack().unpack
        script = LoadFromYaml().save_load(script_path=script_path)
        if script is None:
            logger.warning("events is empty")
            return None
        events = script["script"]
        event_cls_list = [unpack_method(event) for event in events]
        # logger.info(event_cls_list)

        extractor = ExtractInputMessage()
        extractor.events_cls = event_cls_list
        extractor.extract()

        # logger.info(extractor.user_input_message)
        logger.info(extractor.user_input_message)
        for user_input in extractor.user_input_message:
            logger.info(user_input)
            input_message = user_input[0]
            start_event = user_input[1]
            last_event = user_input[2]

            # logger.info(input_message)
            start_index = event_cls_list.index(start_event)
            stop_index = event_cls_list.index(last_event)

            user_input_event = UserInputEventProduct().product()
            user_input_event.window = start_event.window
            user_input_event.message = input_message

            user_input_event = [user_input_event]
            event_cls_list = (event_cls_list[:start_index] + user_input_event +
                              event_cls_list[stop_index + 1:])

        message = ""
        user_input_event_list = []
        for event in event_cls_list:
            # logger.info(event.event_type)
            if isinstance(event, UserInputEvent):
                user_input_event_list.append(event)
                user_message = "input@{0} >> {1}".format(
                    event.window["class name"], event.message)
                logger.info(user_message)
                message += user_message
                message += '\n'

        return message, event_cls_list, user_input_event_list


if __name__ == '__main__':
    user_input_message = LaunchExtractor().do()
    print(user_input_message)
