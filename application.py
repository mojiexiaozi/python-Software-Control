# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     Application
   Description :
   Author :       Lyl
   date：          2019/8/1
-------------------------------------------------
   Change Activity:
                   2019/8/1:
-------------------------------------------------
"""
__author__ = 'Lyl'

import tkinter as tk


class App(tk.Frame):
    def __init__(self, master):
        assert isinstance(master, tk.Tk)
        super().__init__(master)
        self.master = master
        self.set_app_title("hello tk")

    def set_app_title(self, title):
        assert isinstance(title, str) and bool(title)
        self.master.wm_title(title)
        self.set_app_size(240, 240)

    def set_app_size(self, x, y):
        assert isinstance(x, int) and isinstance(y, int)
        assert x > 0 and y > 0
        self.master.geometry("{0}x{1}".format(x, y))


class Button(object):
    def __init__(self, master=None):
        assert isinstance(master, tk.Tk)
        self._button = tk.Button(app.master)

    def set_button_title(self, title):
        assert isinstance(title, str) and bool(title)
        self._button['text'] = title

    def pack(self):
        self._button.pack()


if __name__ == '__main__':
    app = App(tk.Tk())
    label = tk.Label(app.master)
    label["text"] = "ok"
    label.pack()
    button = Button(app.master)
    button.set_button_title("ok")
    button.pack()
    app.mainloop()
