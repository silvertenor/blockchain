import sys
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QLabel, QApplication


class BasicForm(QWidget):
     def __init__(self):
         super().__init__()
         self.setupGUI()

     def setupGUI(self):
         self.resize(300,300)
         self.label = QLabel("HELLO WORLD !!")
         self.label.setParent(self)

if __name__ == "__main__":
     app = QApplication(sys.argv)

     form = BasicForm()
     form.show()

     app.exec()

app = QApplication(sys.argv)
window = QWidget()
window.show()
sys.exit(app.exec())
