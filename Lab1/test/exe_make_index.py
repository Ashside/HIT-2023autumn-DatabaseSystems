import sys
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView

from ui_make_index import Ui_MainWindow

import pymysql
import DatabaseConnect


class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MyMainWindow, self).__init__()
        self.setupUi(self)
        # 读取功能
        self.pushButton.clicked.connect(self.makeindex)

    # 读取按钮功能
    def makeindex(self):
        # 数据库连接对象
        conn = DatabaseConnect.GetConn()
        cur = conn.cursor()
        # 获取name,gender,classnum,subject,domitory这五个checkbox的值
        check_res = {'stu_name': self.name.isChecked(),
                     'stu_gender': self.gender.isChecked(),
                     'stu_class': self.classnum.isChecked(),
                     'stu_subject': self.subject.isChecked(),
                     'stu_domitory': self.domitory.isChecked()}
        # 为student表设置索引
        for key in check_res.keys():
            if check_res[key]:
                try:
                    sql = "create index " + key + "_index on student(" + key + ")"
                    cur.execute(sql)
                    conn.commit()
                    print("为student表的" + key + "属性设置索引成功")
                except:
                    print("student表的" + key + "索引已存在")

        # 将设置的索引输出到表格
        try:
            sql = "show index from student"
            cur.execute(sql)
            conn.commit()
            res = cur.fetchall()
            self.tableWidget.setRowCount(len(res))
            self.tableWidget.setColumnCount(5)
            self.tableWidget.setHorizontalHeaderLabels(['Table', 'Non_unique', 'Key_name', 'Seq_in_index', 'Column_name'])
            for i in range(len(res)):
                for j in range(5):
                    self.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(res[i][j])))
        except:
            print("获取student表索引失败")


        DatabaseConnect.CloseConn(cur, conn)


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    win = MyMainWindow()
    win.show()
    sys.exit(app.exec())
