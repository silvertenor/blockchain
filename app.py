from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import logging
import os, json

basedir = os.path.dirname(__file__)
os.environ["basedir"] = basedir
# Import custom module
import source.modules.history as hist
import source.modules.configPush as conf
import source.modules.deployContract as dc
import source.modules.environmentSetup as es

# Set up
with open(os.path.join(basedir, "source", "compiled_code.json"), "r") as file:
    contractInfo = json.load(file)

# Deploy file Prereqs
# Get bytecode
bytecode = contractInfo["contracts"]["DataTracker.sol"]["DataTracker"]["evm"][
    "bytecode"
]["object"]

# get abi and load contract into memory
abi = contractInfo["contracts"]["DataTracker.sol"]["DataTracker"]["abi"]
os.environ["abi"] = json.dumps(abi)
try:
    dtContract = es.w3.eth.contract(
        address=os.environ["contract_address"], abi=abi
    )  # our contract
except Exception as e:
    print("Could not load contract.")


# Class for logging
class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QPlainTextEdit(parent)
        self.widget.setReadOnly(True)
        self.widget.setMaximumSize(
            self.widget.maximumSize().width(), parent.frameSize().height() // 6
        )

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


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
        self.layout = QVBoxLayout(self)
        # set up our UI
        self.setWindowTitle("GEthereum")
        title = QLabel("GEthereum Main Window")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tabs.addTab(self.tab1, "Tab 1")
        self.tabs.addTab(self.tab2, "Tab 2")
        # Total layout of pages
        self.tab1.layout = QVBoxLayout()
        self.tab2.layout = QVBoxLayout()
        # Individual layout of buttons (tab 1)
        buttonLayout = QHBoxLayout()

        self.createForm()
        tab2Title = QLabel("Credential Management")
        tab2Title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tab2.layout.addWidget(tab2Title)
        self.tab2.layout.addWidget(self.formGroupBox)
        # initialize our labels/buttons/tables
        queryButton = QPushButton("Query Chain")
        configPushButton = QPushButton("Publish New Configuration")
        deployButton = QPushButton("Deploy Contract")

        # add our widgets to each layout
        self.tab1.layout.addWidget(title)
        self.tab1.layout.addLayout(buttonLayout)
        buttonLayout.addWidget(configPushButton)
        buttonLayout.addWidget(queryButton)
        buttonLayout.addWidget(deployButton)

        # Table view
        self.table = QTableView()
        self.tab1.layout.addWidget(self.table)

        # Log view
        logBox = QTextEditLogger(self)
        logBox.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        logging.getLogger().addHandler(logBox)
        logging.getLogger().setLevel(logging.DEBUG)
        # self.tab1.pageLayout.addWidget(self.formGroupBox)
        self.tab1.layout.addWidget(logBox.widget)
        # set our view of the page
        widget = QWidget()
        self.layout.addWidget(self.tabs)
        self.tab1.setLayout(self.tab1.layout)
        self.tab2.setLayout(self.tab2.layout)
        widget.setLayout(self.layout)  # apply layout to our widget
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

    # Function to create form
    def createForm(self):
        # Form to update environment file
        self.formGroupBox = QGroupBox()
        self.accountAddress = QLineEdit()
        self.privateKey = QLineEdit()
        self.web3Provider = QLineEdit()
        self.chainID = QLineEdit()
        self.contractAddress = QLineEdit()
        layout = QFormLayout()
        rows = {
            "Account Address": self.accountAddress,
            "Private Key": self.privateKey,
            "Web3 Provider": self.web3Provider,
            "Chain ID": self.chainID,
            "Contract Address": self.contractAddress,
        }
        for row in rows:
            layout.addRow(QLabel(row), rows[row])
        self.formGroupBox.setLayout(layout)

    # Function to push config
    def pushConfig(self):
        try:
            logging.info(
                "Publishing new IPs to {}".format(
                    os.path.join(basedir, "/source/logfiles", "Device.xml")
                )
            )
            # Call function to place random garbage IP's in XML File
            conf.changeFile()
            # Update the blockchain
            conf.updateChain()
            # Update the table
            self.getData()
        except:
            logging.error("Error publishing new configuration.")

    # Function to get data
    def getData(self):
        # Update table data
        try:
            logging.info("Querying initial state of system...")
            data = hist.getHistory()
            # Refresh table view
            self.model = TableModel(data)
            self.table.setModel(self.model)
            width = self.frameGeometry().width()
            for i in range(0, data.shape[1]):
                self.table.setColumnWidth(i, width // data.shape[1])
            logging.info("Table Updated!")
        except:
            logging.error("Error querying blockchain or updating table.")

    # Function to update contract
    def updateContract(self):
        logging.info("Deploying contract...")
        # self.pageLayout.addWidget(prog_bar)
        # call function to deploy new contract
        try:
            dc.main()
            # Update table
            self.getData()
            logging.info("Contract deployed and table updated!")
        except:
            logging.error(
                (
                    "An error occured when deploying the contract or querying the chain. Please make sure you have a valid connection to the server and that your .env file is up to date."
                )
            )


app = QApplication([])
window = MainWindow()
window.show()

app.exec()
