import sys
import os
import time
from PyQt6.QtWidgets import QComboBox, QMainWindow, QApplication, QLineEdit, QWidget, QGridLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtSql import QSqlDatabase, QSqlQuery


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("GEthereum")
        title = QLabel("Select Changes to View: ")

        layout = QGridLayout()

        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        layout.addWidget(title, 0, 1)

        widget = QComboBox()
        layout.addWidget(widget, 1, 1)
        widget.addItems(["TCW File","LOG File", "XML File"])

        widget.currentIndexChanged.connect( self.index_changed )

        # widget.textChanged.connect( self.text_changed )

        self.setCentralWidget(widget)

    def index_changed(self, i): # i is an int
        print(i)

    def text_changed(self, s): # s is a str
        print(s)

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()