#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
----------------------------------------------------
@Project      :    CASI003
@File         :   main_interface.py
@Time         :   2019/9/2 9:09
@Author       :   kimi
@Version      :   1.0
@Contact      :   15651838825@163.com
@License      :   (C)Copyright 2018-2019, CASI
@Desc         :   None
-----------------------------------------------------
"""

# ---------------------------------------------------
# module import
import sys
import os
import re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QDesktopWidget,
                             QMessageBox, QAction, QTextEdit, QFileDialog,
                             QMenuBar, QToolBar)
from PyQt5.QtGui import QIcon, QFont
from PyQt5 import QtGui
from PyQt5.QtCore import QDir
from queue import Queue

from extract_input_message import LaunchExtractor
from pynput_record import Record
from pynput_playback import Playback
from script_save import SaveEvent
from software_init import Init
from log import Logger

logger = Logger().get_logger(__name__)


class ExitAction(QAction):
    def __init__(self, parent):
        super().__init__(parent)
        assert isinstance(parent, QMainWindow)
        self.setIcon(QIcon('icon/exit.svg'))
        self.setText('Exit')

        self.setShortcut('Ctrl+Q')
        self.setStatusTip('Exit application.')
        self.triggered.connect(parent.close)


class OpenAction(QAction):
    def __init__(self, parent):
        super().__init__(parent)
        assert isinstance(parent, QMainWindow)
        self.setIcon(QIcon('icon/open.svg'))
        self.setText('Open')

        self.setShortcut('Ctrl+O')
        self.setStatusTip('Open script file.')
        # self.triggered.connect(parent.close)


class SaveAction(QAction):
    def __init__(self, parent):
        super().__init__(parent)
        assert isinstance(parent, QMainWindow)
        self.setIcon(QIcon('icon/save.svg'))
        self.setText('Save')

        self.setShortcut('Ctrl+S')
        self.setStatusTip('Save script file.')
        # self.triggered.connect(parent.close)


class SaveAsAction(QAction):
    def __init__(self, parent):
        super().__init__(parent)
        assert isinstance(parent, QMainWindow)
        self.setIcon(QIcon('icon/save_as.svg'))
        self.setText('Save As')

        self.setShortcut('Ctrl+Shift+S')
        self.setStatusTip('Save As Script File.')
        # self.triggered.connect(parent.close)


class StartRecordAction(QAction):
    def __init__(self, parent):
        super().__init__(parent)
        assert isinstance(parent, QMainWindow)
        self.setIcon(QIcon('icon/record.svg'))
        self.setText('Start Record')

        self.setShortcut('Ctrl+R')
        self.setStatusTip('Start record a script.')
        # self.triggered.connect(parent.close)


class StopRecordAction(QAction):
    def __init__(self, parent):
        super().__init__(parent)
        assert isinstance(parent, QMainWindow)
        self.setIcon(QIcon('icon/stop.svg'))
        self.setText('Stop Record')

        self.setShortcut('F12')
        self.setStatusTip('Stop record script.')
        # self.triggered.connect(parent.close)


class StartPlayAction(QAction):
    def __init__(self, parent):
        super().__init__(parent)
        assert isinstance(parent, QMainWindow)
        self.setIcon(QIcon('icon/playback.svg'))
        self.setText('Start Play')

        self.setShortcut('Ctrl+P')
        self.setStatusTip('Start play a script.')
        # self.triggered.connect(parent.close)


class StopPlayAction(QAction):
    def __init__(self, parent):
        super().__init__(parent)
        assert isinstance(parent, QMainWindow)
        self.setIcon(QIcon('icon/stop.svg'))
        self.setText('Stop Play')

        self.setShortcut('F11')
        self.setStatusTip('Stop Play Script.')
        # self.triggered.connect(parent.close)


class MenuBar(QMenuBar):
    def __init__(self, parent):
        super().__init__(parent)
        self.file_menu = self.addMenu('File')
        self.file_menu.addActions(
            (parent.open_action, parent.save_action, parent.save_as_action))
        self.file_menu.setStatusTip("Script")

        # ------------------------------------------------------------------------------
        # motion menu
        self.record_menu = self.addMenu('Record')
        self.record_menu.addActions(
            (parent.start_record_action, parent.stop_record_action))

        self.playback_menu = self.addMenu('Playback')
        self.playback_menu.addActions(
            (parent.start_playback_action, parent.stop_playback_action))

        # -----------------------------------------------------------------
        # Exit menu bar
        self.exit_menu = self.addMenu('&Exit')
        self.exit_menu.addAction(parent.exit_action)


class ToolBar(QToolBar):
    def __init__(self, parent):
        super().__init__(parent)
        self.file_tool_bar = parent.addToolBar('File')
        self.file_tool_bar.addActions(
            (parent.open_action, parent.save_action, parent.save_as_action))

        self.motion_tool_bar = parent.addToolBar('Motion')
        self.motion_tool_bar.addActions(
            (parent.start_record_action, parent.start_playback_action))

        self.exit_tool_bar = parent.addToolBar('Exit')
        self.exit_tool_bar.addAction(parent.exit_action)


class TextEdit(QTextEdit):
    def __init__(self, parent):
        super().__init__(parent)
        assert isinstance(parent, QMainWindow)
        self.parent = parent
        self.setStatusTip('Script views')
        self.resize(980, 700)
        self.move(10, 66)
        self.textChanged.connect(self.text_change)

        self.text_change("")

    def text_change(self, tip_symbol='*'):
        tip = "{0}{1}".format(tip_symbol,
                              self.parent.software_config.using_script)
        self.setStatusTip(tip)
        logger.info(tip)


class TimesNewRomanFont(QFont):
    def __init__(self):
        super().__init__()
        self.setFamily('Times New Roman')
        self.setPointSize(14)


class Recorder(object):
    def __init__(self, parent: QMainWindow):
        self._parent = parent

    def start_record(self):
        record = Record(Queue())
        record.start()
        self._parent.setHidden(True)
        record.join()
        self._parent.setHidden(False)
        self._parent.info_box.info("Record Done!")


class Player(object):
    def __init__(self, parent: QMainWindow):
        self._this_queue = Queue()
        self._parent = parent

    @property
    def this_queue(self):
        return self._this_queue

    def start_play(self):
        player = Playback(this_queue=self.this_queue)
        player.start()
        self._parent.setHidden(True)
        player.join()
        self._parent.setHidden(False)
        self._parent.info_box.info("Play Done!")


class InfoBox(QMessageBox):
    def __init__(self, parent: QMainWindow):
        super().__init__(parent)
        self.setWindowTitle("Info")
        self.addButton(self.Ok)

    def info(self, message: str):
        self.setText(message)
        self.show()


class FileDialog(QFileDialog):
    def __init__(self, parent):
        super().__init__(parent)
        assert isinstance(parent, MainInterface)
        self.parent = parent
        self.setWindowTitle("Open Script")
        self.setWindowIcon(QIcon('icon/open.svg'))
        self.setDirectory(QDir(parent.software_config.scripts_dir))

    def load(self, file_name=""):
        assert isinstance(self.parent, MainInterface)
        file_name = self.getOpenFileName(caption="Open Script",
                                         filter='*.yaml')
        if file_name:
            file_name = os.path.split(file_name[0])[1]
            if file_name:
                self.parent.software_config.using_script = file_name
                self.parent.text_edit.setStatusTip(file_name)
                self.parent.software_config.dumps()
                logger.info(file_name)
                self.extractor(file_name)
            else:
                logger.warning("open cancel")

    def extractor(self, file_name):
        extractor_message = LaunchExtractor().do(file_name)
        if extractor_message:
            user_input_message = extractor_message[0]
            user_input_message = "<script>\nscript@{0}\n{1}</script>".format(
                file_name, user_input_message)
            logger.info(user_input_message)
            # self.parent.text_edit.setText(user_input_message)
            self.parent.text_edit.setPlainText(user_input_message)
        else:
            self.parent.text_edit.setText(
                "{0} script file is missing or illegal!".format(file_name))
        self.parent.extractor_message = extractor_message


class SaveScript(object):
    def __init__(self, parent):
        assert isinstance(parent, MainInterface)
        self.parent = parent

    def save(self, filename=None):
        logger.info(filename)
        if not self.parent.extractor_message:
            logger.warning("Empty Script")

        self.parent.text_edit.text_change("")
        message = self.parent.text_edit.toPlainText()
        logger.info(message)
        pattern = re.compile(r'>>(.*)')
        message_list = re.findall(pattern=pattern, string=message)
        logger.info(message_list)

        # user_input_message = self.parent.extractor_message[0]
        event_cls_list = self.parent.extractor_message[1]
        user_input_event_list = self.parent.extractor_message[2]

        if message_list:
            message_list = [temp.strip() for temp in message_list]

        for i in range(len(user_input_event_list)):
            try:
                user_input_event_list[i].message = message_list[i]
            except IndexError:
                pass

        for user_input_event in user_input_event_list:
            event_cls_list[event_cls_list.index(
                user_input_event)] = user_input_event

        if event_cls_list:
            # pattern = re.compile(r'[\S]*.yaml')
            # result = pattern.findall(filename)
            logger.info(filename)
            if not filename:
                filename = self.parent.software_config.using_script

            logger.info("filename{0}".format(filename))
            event_dict_list = [event.events for event in event_cls_list]
            SaveEvent.save_to_yaml_file(event_dict_list=event_dict_list,
                                        file_name=filename)


class SaveAsDialog(QFileDialog):
    def __init__(self, parent):
        super().__init__(parent)
        assert isinstance(parent, MainInterface)
        self.parent = parent
        self.setWindowTitle("Save As Script")
        self.setWindowIcon(QIcon('icon/save.svg'))
        self.setDirectory(QDir(parent.software_config.scripts_dir))

    def save_as(self):
        file_name = self.getSaveFileName(caption="Save As", filter="*.yaml")[0]
        logger.info(file_name)
        if file_name:
            self.parent.save_event.save(file_name)
            logger.info("save done")
        else:
            logger.info("save as cancel")


class MainInterface(QMainWindow):
    def __init__(self):
        super().__init__()

        self.software_config = Init().software_config
        os.chdir(self.software_config.software_dir)
        # ---------------------------------------
        # actions
        self.open_action = OpenAction(self)
        self.save_action = SaveAction(self)
        self.save_as_action = SaveAsAction(self)
        self.exit_action = ExitAction(self)
        self.start_record_action = StartRecordAction(self)
        self.stop_record_action = StopRecordAction(self)
        self.start_playback_action = StartPlayAction(self)
        self.stop_playback_action = StopPlayAction(self)

        self._recorder = Recorder(self)
        self._player = Player(self)
        self.info_box = InfoBox(self)
        self.file_dialog = FileDialog(self)
        self.save_as_dialog = SaveAsDialog(self)

        self.extractor_message = None
        self.save_event = SaveScript(self)
        # --------------------------------------------------
        # text edit
        self.text_edit = TextEdit(self)

        # --------------------------------------------
        # load ui
        self.ui_init()
        self._connect_action()
        self.file_dialog.extractor(self.software_config.using_script)

    def ui_init(self):
        # -----------------------------------
        # set menus
        self.setMenuBar(MenuBar(self))
        # -------------------------------
        # set tool bars
        self.addToolBar(ToolBar(self))
        # ------------------------------------------
        # set icon
        self.setWindowIcon(QIcon('icon/main.svg'))
        # ----------------------------------------------
        # set status tip
        self.setStatusTip("Main")
        self.statusBar().setStatusTip("Status Tip")
        # -----------------------------------------------
        # set font
        self.setFont(TimesNewRomanFont())
        # -----------------------------------------------
        # show main interface
        self.setWindowTitle("Main")
        self.setGeometry(100, 100, 1000, 800)
        self.setFixedHeight(800)
        self.setFixedWidth(1000)
        self.move_to_center()
        self.show()

    def _connect_action(self):
        self.start_record_action.triggered.connect(self._recorder.start_record)
        self.start_playback_action.triggered.connect(self._player.start_play)
        self.open_action.triggered.connect(self.file_dialog.load)
        self.save_action.triggered.connect(self.save_event.save)
        self.save_as_action.triggered.connect(self.save_as_dialog.save_as)

    def move_to_center(self):
        frame = self.frameGeometry()
        desktop = QDesktopWidget().availableGeometry().center()
        frame.moveCenter(desktop)
        self.move(frame.topLeft())

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        reply = QMessageBox().question(self, "Quit?", "Are you sure to quit?",
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


class MainInterfaceLoad(object):
    def __init__(self):
        app = QApplication(sys.argv)
        main_interface = MainInterface()
        sys.exit(app.exec_())


if __name__ == '__main__':
    MainInterfaceLoad()
