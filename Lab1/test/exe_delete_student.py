import sys
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView

from ui_delete_student import Ui_MainWindow

import pymysql
import DatabaseConnect


class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MyMainWindow, self).__init__()
        self.setupUi(self)
        # 读取功能
        self.deleteSel.clicked.connect(self.delete_sel)
        self.deleteStudent.clicked.connect(self.delete_student)

    # 读取按钮功能
    def delete_student(self):
        # 数据库连接对象
        conn = DatabaseConnect.GetConn()
        cur = conn.cursor()
        # 获取输入的学号
        stu_id = self.idnumForStudent.text()
        # 查询是否存在该学号
        sql = "select * from student where stu_id = %s"
        cur.execute(sql, stu_id)
        result = cur.fetchall()
        if len(result) == 0:
            QtWidgets.QMessageBox.warning(self, '警告', '该学号不存在！', QtWidgets.QMessageBox.Yes)
        else:
            try:
                # 删除该学号
                sql = "delete from student where stu_id = %s"
                cur.execute(sql, stu_id)
                conn.commit()
                QtWidgets.QMessageBox.information(self, '提示', '删除学生信息成功！', QtWidgets.QMessageBox.Yes)
                # 继续删除selcourse表中的信息
                sql = "delete from university.selcouse where stu_id = %s"
                cur.execute(sql, stu_id)
                conn.commit()
                QtWidgets.QMessageBox.information(self, '提示', '删除选课信息成功！', QtWidgets.QMessageBox.Yes)
            except Exception as e:
                print(e)
                QtWidgets.QMessageBox.warning(self, '警告', '删除失败！', QtWidgets.QMessageBox.Yes)
                conn.rollback()
        cur.close()
        conn.close()

    def delete_sel(self):
        # 数据库连接对象
        conn = DatabaseConnect.GetConn()
        cur = conn.cursor()
        # 获取输入的学号和课程名
        stu_id = self.idnumForCourse.text()
        course_name = self.courseName.currentText()
        # 查询是否存在该学号
        sql = "select * from student where stu_id = %s"
        cur.execute(sql, stu_id)
        result = cur.fetchall()
        isIdExist = len(result)
        # 查询该学号是否选了该课程
        sql = "select * from selcouse where stu_id = %s and course_name = %s"
        cur.execute(sql, (stu_id, course_name))
        result = cur.fetchall()
        isSelExist = len(result)
        if isIdExist == 0:
            QtWidgets.QMessageBox.warning(self, '警告', '该学号不存在！', QtWidgets.QMessageBox.Yes)
        elif isSelExist == 0:
            QtWidgets.QMessageBox.warning(self, '警告', '该学生未选该课程！', QtWidgets.QMessageBox.Yes)
        else:
            try:

                # 删除该学号选的该课程
                sql = "delete from selcouse where stu_id = %s and course_name = %s"
                cur.execute(sql, (stu_id, course_name))
                conn.commit()
                QtWidgets.QMessageBox.information(self, '提示', '删除选课信息成功！', QtWidgets.QMessageBox.Yes)
            except:
                QtWidgets.QMessageBox.warning(self, '警告', '删除失败！', QtWidgets.QMessageBox.Yes)


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    win = MyMainWindow()
    win.show()
    sys.exit(app.exec())
