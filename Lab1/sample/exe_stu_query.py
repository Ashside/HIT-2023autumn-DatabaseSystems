import sys
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView

from ui_stu_table import Ui_MainWindow

import pymysql


class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MyMainWindow, self).__init__()
        self.setupUi(self)
        # 读取功能
        self.button_read.clicked.connect(self.read)

    # 读取按钮功能
    def read(self):
        # 数据库连接对象
        conn = pymysql.connect(host='localhost', port=3306, user='root', password="z499096", database='university')
        cur = conn.cursor()

        try:
            # 执行SQL语句
            cur.execute("select * from student")
            # 获取数据
            data = cur.fetchall()
            # 设置表格行数
            self.tableWidget.setRowCount(len(data))
            # 设置表格列数
            self.tableWidget.setColumnCount(len(data[0]))
            # 设置表格头
            self.tableWidget.setHorizontalHeaderLabels(['学号', '姓名', '性别', '班级号', '专业','寝室号'])
            # 设置表格内容
            for i in range(len(data)):
                for j in range(len(data[i])):
                    self.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(data[i][j])))
            # 设置表格自适应大小
            self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        except Exception as e:
            print(e)

        cur.close()
        conn.close()


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    win = MyMainWindow()
    win.show()
    sys.exit(app.exec())
