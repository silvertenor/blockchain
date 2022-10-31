from PyQt6.QtCore import Qt, QAbstractTableModel
from PyQt6.QtGui import QScreen
from PyQt6.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QMainWindow,
    QTableView,
    QApplication,
)

import modules.history as hist

# Our table - based on pandas DF
class TableModel(QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Orientation.Vertical:
                return str(self._data.index[section])


# Our window
class MainWindow(QMainWindow):
    def __init__(self):
        # initialize parent model
        super().__init__()

        # set title
        self.setWindowTitle("GEthereum")

        layout = QVBoxLayout()
        widgets = [QLabel]  # our widgets
        # initialize our variables
        self.table = QTableView()
        button = QPushButton("Query Chain")
        # Gather our blockchain data
        # data = self.getData()

        # set up our display
        for w in widgets:
            layout.addWidget(w())
        layout.addWidget(self.table)
        layout.addWidget(button)
        widget = QWidget()
        widget.setLayout(layout)
        # Force screen to maximize
        self.showMaximized()
        # Equally space out the columns in our table
        button.setCheckable = True
        button.clicked.connect(lambda: self.getData())

        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        self.setCentralWidget(widget)

    # Function to get data
    def getData(self):
        # Update table
        data = hist.getHistory()
        self.model = TableModel(data)
        self.table.setModel(self.model)
        width = self.frameGeometry().width()
        for i in range(0, data.shape[1]):
            self.table.setColumnWidth(i, width // data.shape[1])


app = QApplication([])
window = MainWindow()
window.show()

app.exec()
