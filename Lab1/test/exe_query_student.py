import sys
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView

from ui_query_student import Ui_MainWindow

import pymysql
import DatabaseConnect


class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MyMainWindow, self).__init__()
        self.setupUi(self)
        # 读取功能
        self.joinQuery.clicked.connect(self.joinQueryStudent)
        self.groupQuery.clicked.connect(self.groupQueryStudent)
        self.whereQuery.clicked.connect(self.whereQueryStudent)

    def joinQueryStudent(self):
        # 查询选课数大于输入的学生，结果写入表格
        conn = DatabaseConnect.GetConn()
        cur = conn.cursor()
        try:

            # 获取输入
            cno = self.joinText.text()
            # 执行查询
            sql = ("select student.stu_name from student natural join selcouse group by selcouse.stu_id having count("
                   "*) > %s")
            cur.execute(sql, cno)
            result = cur.fetchall()
            QtWidgets.QMessageBox.information(self, '提示', '查询成功！')
            # 设置表格行数
            self.tableWidget.setRowCount(len(result))
            # 设置表格列数
            self.tableWidget.setColumnCount(len(result[0]))
            # 设置表格头
            self.tableWidget.setHorizontalHeaderLabels(['学生姓名'])
            # 设置表格内容
            for i in range(len(result)):
                for j in range(len(result[i])):
                    self.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(result[i][j])))
            # 设置表格自适应大小
            self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        except Exception as e:
            print(e)
            conn.rollback()

        cur.close()
        conn.close()

    def whereQueryStudent(self):
        # 查找选择了某门课程的学生
        conn = DatabaseConnect.GetConn()
        cur = conn.cursor()
        try:
            # 获取输入
            cno = self.whereText.currentText()
            # 执行查询
            sql = "select stu_name from student where stu_id in (select stu_id from selcouse where course_name = %s)"
            cur.execute(sql, cno)
            result = cur.fetchall()
            QtWidgets.QMessageBox.information(self, '提示', '查询选择{}课程的学生成功！'.format(cno))
            # 设置表格行数
            self.tableWidget.setRowCount(len(result))
            # 设置表格列数
            self.tableWidget.setColumnCount(len(result[0]))
            # 设置表格头
            self.tableWidget.setHorizontalHeaderLabels(['学生姓名'])
            # 设置表格内容
            for i in range(len(result)):
                for j in range(len(result[i])):
                    self.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(result[i][j])))
            # 设置表格自适应大小
            self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        except Exception as e:
            print(e)
            conn.rollback()
    def groupQueryStudent(self):
        # 查询某门课程的平均分
        conn = DatabaseConnect.GetConn()
        cur = conn.cursor()
        course_name = self.groupText.currentText()
        try:
            # 查找是否存在该课程的成绩
            sql = "select course_name from selcouse group by course_name having course_name = %s"
            cur.execute(sql, course_name)
            result = cur.fetchall()
            if len(result) == 0:
                QtWidgets.QMessageBox.information(self, '提示', '该课程不存在！')
                return
            # 执行查询
            sql = ("select avg(course_score) from selcouse group by course_name "
                   ""
                   ""
                   ""
                   "")
            cur.execute(sql, course_name)
            result = cur.fetchall()
            QtWidgets.QMessageBox.information(self, '提示', '查询{}的平均分成功！'.format(course_name))
            # 设置表格行数
            self.tableWidget.setRowCount(len(result))
            # 设置表格列数
            self.tableWidget.setColumnCount(len(result[0]))
            # 设置表格头
            self.tableWidget.setHorizontalHeaderLabels(['平均分'])
            # 设置表格内容
            for i in range(len(result)):
                for j in range(len(result[i])):
                    self.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(result[i][j])))
            # 设置表格自适应大小
            self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        except Exception as e:
            print(e)
            conn.rollback()




if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    win = MyMainWindow()
    win.show()
    sys.exit(app.exec())
