import sys
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView

from ui_main_window import Ui_MainWindow
import os
import pymysql
import DatabaseConnect


class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MyMainWindow, self).__init__()
        self.setupUi(self)


        # 读取功能
        self.makeViewBut.clicked.connect(self.makeView)
        self.makeIndexBut.clicked.connect(self.makeIndex)
        self.insertBut.clicked.connect(self.insertStudent)
        self.deleteBut.clicked.connect(self.deleteStudent)
        self.queryBut.clicked.connect(self.queryStudent)

    def makeView(self):
        sysstr = os.system('python exe_make_view.py')

    def makeIndex(self):
        sysstr = os.system('python exe_make_index.py')

    def insertStudent(self):
        sysstr = os.system('python exe_insert_student.py')

    def deleteStudent(self):
        sysstr = os.system('python exe_delete_student.py')

    def queryStudent(self):
        sysstr = os.system('python exe_query_student.py')







if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    win = MyMainWindow()
    win.show()
    sys.exit(app.exec())
