import sys
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView

from ui_make_view import Ui_MainWindow

import pymysql
import DatabaseConnect


class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MyMainWindow, self).__init__()
        self.setupUi(self)
        # 读取功能
        self.pushButton.clicked.connect(self.makeview)

    # 读取按钮功能
    def makeview(self):
        # 数据库连接对象
        conn = DatabaseConnect.GetConn()
        cur = conn.cursor()

        try:
            # 获取数据
            subject = self.comboBox.currentText()
            dict = {'人工智能': 'ai_stu', '大数据': 'bigdata_stu', '计科': 'cs_stu'}
            sql = "drop view if exists " + dict[subject]
            cur.execute(sql)
            sql = "create view " + dict[subject] + " as select * from student where stu_subject = '" + subject + "'"
            cur.execute(sql)
            conn.commit()
            print("创建视图成功")

            # 读取视图，输出到表格
            cur.execute("select * from " + dict[subject])
            # 获取数据
            data = cur.fetchall()
            # 设置表格行数
            self.tableWidget.setRowCount(len(data))
            # 设置表格列数
            self.tableWidget.setColumnCount(len(data[0]))
            # 设置表格头
            self.tableWidget.setHorizontalHeaderLabels(['学号', '姓名', '性别', '班级号', '专业', '寝室号'])
            # 设置表格内容
            for i in range(len(data)):
                for j in range(len(data[i])):
                    self.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(data[i][j])))
            # 设置表格自适应大小
            self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        except Exception as e:
            print(e)

        DatabaseConnect.CloseConn(cur, conn)


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    win = MyMainWindow()
    win.show()
    sys.exit(app.exec())
