from PyQt5 import uic
from PyQt5.QtGui import QPainter, QColor, QIcon, QFont
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit
from PyQt5.QtCore import Qt, QTimer, QRect, QSize, QPropertyAnimation, pyqtProperty
import sqlite3


class SaveForm(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('saveform.ui', self)
        self.con = sqlite3.connect('saves.sqlite')
        self.cursor = self.con.cursor()
        self.cursor.execute(""" CREATE TABLE IF NOT EXISTS tsaves (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL,
                                        path text NOT NULL); """)
        self.initUI()

    def initUI(self):
        qty = self.cursor.execute('select * from tsaves').fetchall()
        for i in range(len(qty)):
            layout = QHBoxLayout
            idlbl = QLabel()
            idlbl.setText(qty[i][0])
            le = QLineEdit()
            le.setText(qty[i][1])
            le.placeholderText('Name')
            


    def closeEvent(self, event):
        self.con.close()
