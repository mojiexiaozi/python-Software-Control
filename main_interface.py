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
from PyQt5.QtWidgets import (QApplication, QMainWindow, QDesktopWidget, QMessageBox, QAction, QTextEdit, QFileDialog,
                             QMenuBar, QToolBar, QInputDialog)
from PyQt5.QtGui import QIcon, QFont
from PyQt5 import QtGui
from PyQt5.QtCore import QDir
from queue import Queue

from extract_input_message import GetEventMessage
from pynput_record import Record
from pynput_playback import Playback
from script_save import SaveEvent
from software_init import Init
from log import Logger
from pynput_playback import LoadFromYaml
import functools
import shutil

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
        self.setStatusTip('Open script file.')  # self.triggered.connect(parent.close)


class AddAction(QAction):
    def __init__(self, parent):
        super().__init__(parent)
        assert isinstance(parent, QMainWindow)
        self.setIcon(QIcon('icon/add.svg'))
        self.setText('Add')

        self.setShortcut('Ctrl+=')
        self.setStatusTip('add script file.')  # self.triggered.connect(parent.close)


class SaveAction(QAction):
    def __init__(self, parent):
        super().__init__(parent)
        assert isinstance(parent, QMainWindow)
        self.setIcon(QIcon('icon/save.svg'))
        self.setText('Save')

        self.setShortcut('Ctrl+S')
        self.setStatusTip('Save script file.')  # self.triggered.connect(parent.close)


class SaveAsAction(QAction):
    def __init__(self, parent):
        super().__init__(parent)
        assert isinstance(parent, QMainWindow)
        self.setIcon(QIcon('icon/save_as.svg'))
        self.setText('Save As')

        self.setShortcut('Ctrl+Shift+S')
        self.setStatusTip('Save As Script File.')  # self.triggered.connect(parent.close)


class StartRecordAction(QAction):
    def __init__(self, parent):
        super().__init__(parent)
        assert isinstance(parent, QMainWindow)
        self.setIcon(QIcon('icon/record.svg'))
        self.setText('Start Record')

        self.setShortcut('Ctrl+R')
        self.setStatusTip('Start record a script.')  # self.triggered.connect(parent.close)


class StopRecordAction(QAction):
    def __init__(self, parent):
        super().__init__(parent)
        assert isinstance(parent, QMainWindow)
        self.setIcon(QIcon('icon/stop.svg'))
        self.setText('Stop Record')

        self.setShortcut('F12')
        self.setStatusTip('Stop record script.')  # self.triggered.connect(parent.close)


class StartPlayAction(QAction):
    def __init__(self, parent):
        super().__init__(parent)
        assert isinstance(parent, QMainWindow)
        self.setIcon(QIcon('icon/playback.svg'))
        self.setText('Start Play')

        self.setShortcut('Ctrl+P')
        self.setStatusTip('Start play a script.')  # self.triggered.connect(parent.close)


class StopPlayAction(QAction):
    def __init__(self, parent):
        super().__init__(parent)
        assert isinstance(parent, QMainWindow)
        self.setIcon(QIcon('icon/stop.svg'))
        self.setText('Stop Play')

        self.setShortcut('F12')
        self.setStatusTip('Stop Play Script.')  # self.triggered.connect(parent.close)


class AddValue(QAction):
    def __init__(self, parent):
        assert isinstance(parent, QMainWindow)
        super().__init__(parent)
        self.setIcon(QIcon('icon/add_value.svg'))
        self.setText('Add Value')
        self.setShortcut('Ctrl+.')
        self.setStatusTip('Add New Variable')


class MenuBar(QMenuBar):
    def __init__(self, parent):
        super().__init__(parent)
        self.file_menu = self.addMenu('File')
        self.file_menu.addActions((parent.open_action, parent.add_action, parent.save_action, parent.save_as_action))
        self.file_menu.setStatusTip("Script")

        # ------------------------------------------------------------------------------
        # motion menu
        self.record_menu = self.addMenu('Record')
        self.record_menu.addActions((parent.start_record_action, parent.stop_record_action))

        self.playback_menu = self.addMenu('Playback')
        self.playback_menu.addActions((parent.start_playback_action, parent.stop_playback_action))

        self.add_variable_menu = self.addMenu('Add Variable')
        self.add_variable_menu.addAction(parent.add_variable_action)

        # -----------------------------------------------------------------
        # Exit menu bar
        self.exit_menu = self.addMenu('&Exit')
        self.exit_menu.addAction(parent.exit_action)


class ToolBar(QToolBar):
    def __init__(self, parent):
        super().__init__(parent)
        self.file_tool_bar = parent.addToolBar('File')
        self.file_tool_bar.addActions(
            (parent.open_action, parent.add_action, parent.save_action, parent.save_as_action))

        self.motion_tool_bar = parent.addToolBar('Motion')
        self.motion_tool_bar.addActions((parent.start_record_action, parent.start_playback_action))

        self.ad_variable_tool_bar = parent.addToolBar('Add Variable')
        self.ad_variable_tool_bar.addAction(parent.add_variable_action)

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
        tip = "{0}{1}".format(tip_symbol, self.parent.software_config.using_script)
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
        file_name = self.getOpenFileName(caption="Open Script", filter='*.yaml')
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

    def add_script(self, file_name=''):
        file_name = self.getOpenFileName(caption="add Script", filter='*.yaml')
        if file_name:
            file_name = os.path.split(file_name[0])[1]
            # logger.info(file_name, self.parent.software_config.using_script)
            # if file_name == self.parent.software_config.using_script:
            #     return None
            current_message = self.parent.text_edit.toPlainText()
            add_message = GetEventMessage().get_event_message(file_name)
            logger.info(add_message)
            if add_message:
                pattern = re.compile(r'<{0}>.*</{0}>'.format('script'), re.S)
                script_message = pattern.findall(add_message)
                logger.info(script_message)
                if script_message:
                    add_message = '*'*20 + 'Script' + '*'*20 + '\n' + script_message[0]
                current_message = "{0}{1}".format(current_message, add_message)
                self.parent.text_edit.setPlainText(current_message)

    def extractor(self, file_name):
        extractor_message = GetEventMessage().get_event_message(file_name)
        if extractor_message:
            # user_input_message = extractor_message[0]
            # format_string = "<script>\n{0}\nscript@{1}\n{2}<script>"
            # user_input_message = format_string.format("delay=1000",
            #                                           file_name,
            #                                           user_input_message)
            # user_input_message = self.parent.s cript_head+user_input_message
            # logger.info(user_input_message)
            # self.parent.text_edit.setText(user_input_message)
            # logger.error(extractor_message)
            self.parent.text_edit.setPlainText(extractor_message)
        else:
            self.parent.text_edit.setText("{0} script file is missing or illegal!".format(file_name))
        self.parent.extractor_message = extractor_message


class SaveScript(object):
    def __init__(self, parent):
        assert isinstance(parent, MainInterface)
        self.parent = parent

    def save(self, filename=None):
        logger.info(filename)
        if not filename:
            filename = self.parent.software_config.using_script

        if not self.parent.extractor_message:
            logger.warning("Empty Script")

        self.parent.text_edit.text_change("")  # 添加脚本已保存提示
        message = self.parent.text_edit.toPlainText()
        # logger.info(message)
        # ----------------------------------------------------------------
        # save script config
        script = LoadFromYaml().save_load(script_path=filename)
        if script:
            script["script config"] = message
            SaveEvent().save_to_yaml_file(file_name=filename, script=script)
        else:
            logger.error("save failed")


class SaveAsDialog(QFileDialog):
    def __init__(self, parent):
        super().__init__(parent)
        assert isinstance(parent, MainInterface)
        self.parent = parent
        self.setWindowTitle("Save As Script")
        self.setWindowIcon(QIcon('icon/save.svg'))
        self.setDirectory(QDir(parent.software_config.scripts_dir))

    def save_as(self):
        new_file_name = self.getSaveFileName(caption="Save As", filter="*.yaml")[0]
        logger.info(new_file_name)
        if new_file_name:
            shutil.copyfile(self.parent.software_config.using_script, new_file_name)
            self.parent.save_event.save(new_file_name)
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
        self.add_action = AddAction(self)
        self.add_variable_action = AddValue(self)

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
        self.script_head = ""

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
        self.add_action.triggered.connect(self.file_dialog.add_script)
        self.add_variable_action.triggered.connect(self.add_variable)

    def add_variable(self):
        scripts = re.split(r'\n', self.text_edit.toPlainText())
        text_cursor_number = self.text_edit.textCursor().blockNumber()
        try:
            head_end = scripts.index('</head>')
        except ValueError:
            head_end = -1
        if text_cursor_number < head_end:
            item = self.get_item()
            if item:
                scripts.insert(text_cursor_number + 1, '{0} = [1, 2, 3]'.format(item))
        elif text_cursor_number > head_end:
            if re.findall(r"input@(.*)", scripts[text_cursor_number]):
                item = self.get_item()
                if item:
                    head, variable = re.split('[ ]*>>[ ]*', scripts[text_cursor_number])
                    scripts[text_cursor_number] = head + ' >> ' + '{0}[script_index]'.format(item)

        script_temp = r""
        for i in scripts:
            script_temp = script_temp + i + '\n'

        if script_temp:
            self.text_edit.setPlainText(script_temp)
        # logger.info(script_temp)

    def get_item(self):
        items = ['script_val1', 'script_val2',
                 'script_val3', 'script_val4',
                 'script_val5', 'script_val6',
                 'script_val7', 'script_val8',
                 'script_val9', 'script_val10']
        item, ok = QInputDialog.getItem(self, 'Choose Script Variable',
                                        'script variable items', items, 0, False)
        if ok and item:
            return item
        else:
            return None

    def move_to_center(self):
        frame = self.frameGeometry()
        desktop = QDesktopWidget().availableGeometry().center()
        frame.moveCenter(desktop)
        self.move(frame.topLeft())

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        event.accept()
        """
        reply = QMessageBox().question(self, "Quit?", "Are you sure to quit?", QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
        """


class MainInterfaceLoad(object):
    def __init__(self):
        app = QApplication(sys.argv)
        main_interface = MainInterface()
        sys.exit(app.exec_())


def just_one_instance(func):
    """
    装饰器
    如果有实例在跑则退出
    :return
    """

    @functools.wraps(func)
    def f(*args, **kwargs):
        import socket
        try:
            s = socket.socket()
            host = socket.gethostname()
            logger.info(host)
            s.bind((host, 9527))
        except Exception as e:
            logger.error(e)
            logger.error("already has an instance")
            return None
        return func(*args, **kwargs)

    return f


@just_one_instance
def main():
    MainInterfaceLoad()


if __name__ == '__main__':
    main()
