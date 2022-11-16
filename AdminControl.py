from PyQt6.QtWidgets import (
    QApplication, QWidget, QTableWidget, 
    QTableWidgetItem, QVBoxLayout, QHeaderView, QFormLayout, QLineEdit, QLabel, QPushButton, QGridLayout
)
import sys
 
class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 SpreadSheet")
        self.resize(400, 250)
        self.show()
 
        self.table = QTableWidget(3, 3)
        self.table.setHorizontalHeaderLabels(["Name", "User", "Role"])
 
        self.table.setItem(0,0, QTableWidgetItem("Molly"))
        self.table.setItem(0,1, QTableWidgetItem("mollyward"))
        self.table.setItem(0, 2 , QTableWidgetItem("admin"))
        self.table.setColumnWidth(0, 150)
  
        self.table.setItem(1,0, QTableWidgetItem("Paul"))
        self.table.setItem(1,1, QTableWidgetItem("paulcunningham"))
        self.table.setItem(1,2, QTableWidgetItem("admin"))
  
        self.table.setItem(2, 0, QTableWidgetItem("Devin"))
        self.table.setItem(2, 1, QTableWidgetItem("devinlane"))
        self.table.setItem(2, 2, QTableWidgetItem("user"))
        
        
        self.vBox = QGridLayout()
        self.vBox.addWidget(QLabel("Name:"),0,0)
        self.vBox.addWidget(QLineEdit(''),0,1)
        self.vBox.addWidget(QLabel("User:"),1,0)
        self.vBox.addWidget(QLineEdit(''),1,1)
        self.vBox.addWidget(QLabel("Role:"),2,0)  
        self.vBox.addWidget(QLineEdit(''),2,1)      
        self.vBox.addWidget(QPushButton("Add User"),3,0,2,2)
        self.vBox.addWidget(self.table,5,0,2,2)
        self.setLayout(self.vBox)
         
 
app = QApplication(sys.argv)
window = Window()
sys.exit(app.exec())
