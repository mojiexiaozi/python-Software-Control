# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     extract_input_message
   Description :
   Author :       
   date：          2019/8/15
-------------------------------------------------
   Change Activity:
                   2019/8/15:
-------------------------------------------------
"""
__author__ = 'Lyl'

from pynput.keyboard import Key
from pynput_record import KeyboardPress, UserInputEvent, KeyboardEvent, MouseEvent, UserInputEventProduct
from pynput_playback import Unpack, LoadFromYaml
from log import Logger


class ExtractInputMessage(object):
    def __init__(self):
        self._events_cls = None
        self._user_input_message = []
        self._ctrl_pressed = False
        self._alt_pressed = False
        self._win_pressed = False
        self._ctrl_key = [Key.ctrl, Key.ctrl_l, Key.ctrl_r]
        self._alt_key = [Key.alt, Key.alt_gr, Key.alt_l, Key.alt_r]
        self._win_key = [Key.cmd, Key.cmd_l, Key.cmd_r]
        self._message_key = [Key.space, '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
                             'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a', 's',
                             'd', 'f', 'g', 'h', 'j', 'k', 'l', 'z', 'x', 'c', 'v', 'b',
                             'n', 'm', '`', '-', '=', ';', "'", ',', '.', '/', '[', ']', '\\']
        self._message_window = ""

    def set_events(self, events_cls):
        assert isinstance(events_cls, list)
        assert isinstance(events_cls[0], KeyboardEvent) or isinstance(events_cls[0], MouseEvent)
        self._events_cls = events_cls

    @property
    def events_cls(self):
        return self._events_cls

    @property
    def user_input_message(self):
        return self._user_input_message

    def extract(self):
        assert isinstance(self.events_cls, list)
        message_start = False
        message = ""
        first_event_cls = None
        last_event_cls = None

        for event in self.events_cls:
            if isinstance(event, KeyboardEvent):
                # print(event.key)
                if event.key in self._ctrl_key:
                    self._ctrl_pressed = isinstance(event, KeyboardPress)

                elif event.key in self._alt_key:
                    self._alt_pressed = isinstance(event, KeyboardPress)

                elif event.key in self._win_key:
                    self._win_pressed = isinstance(event, KeyboardPress)

                if self._ctrl_pressed or self._alt_pressed or self._win_pressed or event.key == Key.enter:
                    if message:
                        try:
                            print("start:{0}, stop:{1}".format(first_event_cls.event_type, last_event_cls.event_type))
                            print("start:{0}, stop:{1}".format(first_event_cls.key, last_event_cls.key))
                        except AttributeError:
                            pass

                        self._user_input_message.append((message, first_event_cls, last_event_cls))
                        message = ""
                        last_event_cls = None
                    message_start = False
                elif event.key in self._message_key and not message_start:  # 抬起按下都有效
                    if event.window:
                        self._message_window = event.window
                        first_event_cls = None
                        last_event_cls = None
                        message_start = True
                    else:
                        self._message_window = None
                        message_start = False

                if message_start:
                    if not message:
                        first_event_cls = event
                    last_event_cls = event

                if event.key == Key.backspace and message_start and isinstance(event, KeyboardPress):  # 实现退格删除
                    message = message[:-1]

                if (event.key in self._message_key) and message_start and isinstance(event, KeyboardPress):
                    key = event.key
                    if key == Key.space:
                        key = " "

                    message += key
                    # print(key)
        if message:
            self._user_input_message.append((message, first_event_cls, last_event_cls))


class LaunchExtractor(object):
    @staticmethod
    def do():
        unpack_method = Unpack().unpack
        events = LoadFromYaml().save_load()
        event_cls_list = [unpack_method(event) for event in events]

        extractor = ExtractInputMessage()
        extractor.set_events(event_cls_list)
        extractor.extract()

        user_message = ""
        logger = Logger().get_logger()

        for message in extractor.user_input_message:
            logger.info(message[0])
            start = event_cls_list.index(message[1])
            stop = event_cls_list.index(message[2])

            user_input_event = UserInputEventProduct().product()
            user_input_event.set_window(message[1].window)
            user_input_event.set_message(message[0])
            user_input_event.set_time(message[1].time)

            event_cls_list = event_cls_list[:start] + [user_input_event] + event_cls_list[stop+1:]
            user_message += message[0]
            user_message += "\n"

        message = ""
        user_input_event_list = []
        for event in event_cls_list:
            logger.info(event.event_type)
            if isinstance(event, UserInputEvent):
                user_input_event_list.append(event)
                logger.info(event.message)
                message += event.message
                message += '\n'

        return message, event_cls_list, user_input_event_list


if __name__ == '__main__':
    user_input_message = LaunchExtractor().do()
    print(user_input_message)
