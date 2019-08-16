# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     recording_interface
   Description :
   Author :
   date：          2019/8/7
-------------------------------------------------
   Change Activity:
                   2019/8/7:
-------------------------------------------------
"""
__author__ = 'Lyl'


import PySimpleGUI as Gui
from gui import Controls, Layouts

from queue import Queue
from threading import Thread

from pynput_record import LaunchRecord


class RecordingInterface(object):
    def __init__(self):
        super().__init__()
        self._layouts = Layouts()
        self._window = None

    @property
    def layouts(self):
        return self._layouts

    @property
    def window(self):
        assert isinstance(self._window, Gui.Window)
        return self._window

    def _design_window(self):
        controls = Controls()
        controls.pack(Gui.Text('', key='__MESSAGE__', size=[40, 1], font=("Helvetica", 18)))
        self._layouts.pack(controls)

        controls = Controls()
        controls.pack(Gui.T(' ' * 20))
        controls.pack(Gui.Button('start record', key='__START_STOP__', font=("Helvetica", 18), size=(12, 1)))
        controls.pack(Gui.Button('quit', key="__QUIT__", font=("Helvetica", 18), size=(12, 1)))
        self._layouts.pack(controls)

    def load_window(self):
        self._design_window()
        self._window = Gui.Window('Record', self._layouts.layout, alpha_channel=0.8)
        self._window.DisableClose = True


class WarningDialog(object):
    def __init__(self, warning_message):
        self._layout = Layouts()
        self.interface_design(warning_message)
        self._window = Gui.Window(title="Warning", layout=self._layout.layout)
        # self.handle_event()

    def interface_design(self, warning_message):
        controls = Controls()
        controls.pack(Gui.Text(warning_message, key="__WARNING_MESSAGE__"))
        self._layout.pack(controls)

        controls = Controls()
        controls.pack(Gui.OK(key="__OK__"))
        self._layout.pack(controls)

    def handle_event(self):
        event, _ = self._window.Read(3000)
        print("warning dialog close")
        self._window.Close()


class InterfaceProduct(object):
    @staticmethod
    def product():
        return RecordingInterface()


class WindowEventMonitor(object):
    def __init__(self, window_instance, window_event_queue, monitor_queue):
        super().__init__()
        assert isinstance(window_event_queue, Queue)
        assert isinstance(monitor_queue, Queue)
        self._window_event_queue = window_event_queue
        self._monitor_queue = monitor_queue

        assert isinstance(window_instance, Window)
        self.window_instance = window_instance

    @property
    def monitor_queue(self):
        return self._monitor_queue

    @property
    def window_event_queue(self):
        return self._window_event_queue

    def run(self):
        self.monitor_queue.put("__CONTINUE__")
        while True:
            message = self.monitor_queue.get()
            print(message)
            if message == "__CONTINUE__":
                event, event_message = self.window_instance.window.Read()  # 读取事件
                print(event, event_message)
                self._window_event_queue.put((event, event_message))
            elif message == "__QUIT__":
                break
            self.monitor_queue.put("__CONTINUE__")
        print("window event monitor quit...")


class WindowEventHandle(Thread):
    def __init__(self, window_event_queue, window_instance, monitor_queue):
        super().__init__()
        assert isinstance(window_event_queue, Queue)
        self._window_event_queue = window_event_queue

        assert isinstance(monitor_queue, Queue)
        self._monitor_queue = monitor_queue

        assert isinstance(window_instance, Window)
        self._window_instance = window_instance

    def start_record(self, record_queue):
        assert isinstance(record_queue, Queue)

        self._window_instance.move_to(1300, 910)
        self._window_instance.set_alpha(0.3)

        LaunchRecord(self._window_event_queue, record_queue).start()

    def stop_record(self):
        self._window_instance.move_to(800, 500)
        self._window_instance.set_alpha(0.8)

    def run(self):
        recording = False
        record_button_dict = {True: "stop record", False: "start record"}
        record_queue = None
        while True:
            # print(1)
            event, event_message = self._window_event_queue.get()
            print(event, event_message)
            if event is None or event == "__QUIT__":
                if recording:
                    # WarningDialog("recording, do not exit")
                    print("ignore")
                else:
                    self._monitor_queue.put("__QUIT__")
                    break
            elif event == "__START_STOP__":
                recording = not recording
                self._window_instance.update_element("__START_STOP__", record_button_dict[recording])
                if recording:
                    record_queue = Queue()
                    self.start_record(record_queue)

                else:
                    self.stop_record()
                    record_queue.put("__QUIT__")
            elif event == "__RECORD_QUIT__":
                self.stop_record()
                recording = False
                self._window_instance.update_element("__START_STOP__", record_button_dict[recording])

        self._window_instance.close()
        print("window event handle quit...")


class Window(object):
    def __init__(self, interface_product):
        assert isinstance(interface_product, InterfaceProduct)
        interface = interface_product.product()
        interface.load_window()

        self._window = interface.window
        assert isinstance(self._window, Gui.Window)

    @property
    def window(self):
        return self._window

    def set_alpha(self, alpha):
        self._window.SetAlpha(alpha)

    def move_to(self, x, y):
        self._window.Move(x, y)

    def close(self):
        self._window.Close()

    def update_element(self, element, message):
        assert isinstance(element, str)
        assert isinstance(message, str)
        self._window.Element(element).Update(message)

    def set_title(self, title):
        self._window.Title = title


class LaunchWindow(object):
    def __init__(self):
        window = Window(InterfaceProduct())
        monitor_queue = Queue()
        window_event_queue = Queue()
        window_event_monitor = WindowEventMonitor(window_instance=window,
                                                  monitor_queue=monitor_queue,
                                                  window_event_queue=window_event_queue)
        window_event_handle = WindowEventHandle(window_event_queue=window_event_queue,
                                                monitor_queue=monitor_queue,
                                                window_instance=window)
        window_event_handle.setDaemon(True)
        window_event_handle.start()
        print("window event handle start")
        window_event_monitor.run()

        # window_event_handle.join()
        # window_event_monitor.join()

        # print("interface closed")


if __name__ == '__main__':
    LaunchWindow()



