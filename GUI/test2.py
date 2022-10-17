import sys
import os
import time
from PyQt6.QtWidgets import QApplication, QLineEdit, QWidget, QGridLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtSql import QSqlDatabase, QSqlQuery

class Window(QWidget):
    def __init__(self):
        super().__init__()
        layout = QGridLayout() 
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        self.setWindowTitle("GEthereum")

        self.setLayout(layout)

        title = QLabel("Login:")
        layout.addWidget(title, 0 ,1)

        user = QLabel("Username:")
        layout.addWidget(user, 1, 0)

        pwd = QLabel("Password:")
        layout.addWidget(pwd, 2, 0)

        self.input1 = QLineEdit()
        layout.addWidget(self.input1, 1, 1, 1, 2)

        self.input2 = QLineEdit()
        self.input2.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.input2, 2, 1, 1, 2)

        button1 = QPushButton("Cancel")
        button1.clicked.connect(self.close)
        layout.addWidget(button1, 3, 1)

        button2 = QPushButton("Login")
        button2.clicked.connect(self.login)
        layout.addWidget(button2, 3, 2)

    def login(self):
        if self.input1.text() == "Molly" and self.input2.text() == "Ward":
            print("Login Successful")
        else:
            print("Login Failed")


app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())