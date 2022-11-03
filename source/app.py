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

# Import custom module
import modules.history as hist
import modules.configPush as conf
import modules.deployContract as dc

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

        # set up our UI
        self.setWindowTitle("GEthereum")
        title = QLabel("GEthereum Main Window")
        layout = QVBoxLayout()
        widgets = [QLabel]  # our widgets
        # initialize our labels/buttons/tables
        self.table = QTableView()
        queryButton = QPushButton("Query Chain")
        configPushButton = QPushButton("Publish New Configuration")
        deployButton = QPushButton("Deploy Contract")

        # set up our display's layout
        for w in widgets:
            layout.addWidget(w())
        layout.addWidget(title)
        layout.addWidget(configPushButton)
        layout.addWidget(queryButton)
        layout.addWidget(deployButton)
        layout.addWidget(self.table)
        widget = QWidget()
        widget.setLayout(layout)  # apply layout to our widget
        # Force screen to maximize
        self.showMaximized()
        # Define backend functions for our buttons when pushed
        queryButton.setCheckable = True
        queryButton.clicked.connect(lambda: self.getData())
        configPushButton.setCheckable = True
        configPushButton.clicked.connect(lambda: self.pushConfig())
        deployButton.setCheckable = True
        deployButton.clicked.connect(lambda: self.updateContract())

        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        self.setCentralWidget(widget)

    # Function to push config
    def pushConfig(self):
        # Call function to place random garbage IP's in XML File
        conf.changeFile()
        # Update the blockchain
        conf.updateChain()
        # Update the table
        self.getData()

    # Function to get data
    def getData(self):
        # Update table data
        data = hist.getHistory()
        # Refresh table view
        self.model = TableModel(data)
        self.table.setModel(self.model)
        width = self.frameGeometry().width()
        for i in range(0, data.shape[1]):
            self.table.setColumnWidth(i, width // data.shape[1])

    # Function to update contract
    def updateContract(self):
        # call function to deploy new contract
        dc.main()
        # Update table
        self.getData()


app = QApplication([])
window = MainWindow()
window.show()

app.exec()
