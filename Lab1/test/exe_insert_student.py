import sys
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView

from ui_insert_student import Ui_MainWindow

import pymysql
import DatabaseConnect


class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MyMainWindow, self).__init__()
        self.setupUi(self)
        # 读取功能
        self.pushButton.clicked.connect(self.insert_student)

    # 读取按钮功能
    def insert_student(self):
        # 数据库连接对象
        conn = DatabaseConnect.GetConn()
        cur = conn.cursor()
        # 获取输入框内容
        stu_id = self.idnum.text()
        stu_name = self.name.text()
        stu_gender = self.gender.text()
        stu_class = self.classnum.text()
        stu_subject = self.subject.text()
        stu_dom = self.domitory.text()
        # 查询stu_id是否存在
        sql = "select * from student where stu_id = %s"
        cur.execute(sql, stu_id)
        isIdExist = cur.fetchall()
        # 查询stu_subject是否存在
        sql = "select * from subject where subject_id = %s"
        cur.execute(sql, stu_subject)
        isSubjectExist = cur.fetchall()
        # 查询stu_dom是否存在
        sql = "select * from domitory where dom_id = %s"
        cur.execute(sql, stu_dom)
        isDomExist = cur.fetchall()
        # 查询班级是否存在
        sql = "select * from classes where class_num = %s"
        cur.execute(sql, stu_class)
        isClassExist = cur.fetchall()

        # 检查输入框是否为空
        if not stu_id or not stu_name or not stu_gender or not stu_class or not stu_subject or not stu_dom:
            QtWidgets.QMessageBox.warning(self, "警告", "请填写完整信息！")
        elif len(stu_id) != 4:
            QtWidgets.QMessageBox.warning(self, "警告", "学号长度应为4位！")
        elif len(stu_name) > 20:
            QtWidgets.QMessageBox.warning(self, "警告", "姓名长度应小于20位！")
        # 检查性别是否为男或女
        elif stu_gender != "男" and stu_gender != "女":
            QtWidgets.QMessageBox.warning(self, "警告", "正确输入性别！")
        elif isIdExist:
            QtWidgets.QMessageBox.warning(self, "警告", "学号已存在！")
        elif not isSubjectExist:
            QtWidgets.QMessageBox.warning(self, "警告", "专业不存在！")
        elif not isDomExist:
            QtWidgets.QMessageBox.warning(self, "警告", "宿舍不存在！")
        elif not isClassExist:
            QtWidgets.QMessageBox.warning(self, "警告", "班级不存在！")
        else:
            try:
                # 插入学生信息
                sql = "insert into student values(%s,%s,%s,%s,%s,%s)"
                cur.execute(sql, [stu_id, stu_name, stu_gender, stu_class, stu_subject, stu_dom])
                conn.commit()
                QtWidgets.QMessageBox.information(self, "提示", "添加成功！")
                # 清空输入框
                self.idnum.setText("")
                self.name.setText("")
                self.gender.setText("")
                self.classnum.setText("")
                self.subject.setText("")
                self.domitory.setText("")
            except Exception as e:
                print(e)
                QtWidgets.QMessageBox.warning(self, "警告", "添加失败！")
                conn.rollback()
        cur.close()
        conn.close()


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    win = MyMainWindow()
    win.show()
    sys.exit(app.exec())
