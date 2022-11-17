from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineQuick import *
import logging
import os, json, sys, signal
from importlib import reload
import shutil, multiprocessing

basedir = os.path.dirname(__file__)
os.environ["basedir"] = basedir
# Import custom module
import source.modules.history as hist
import source.modules.configPush as conf
import source.modules.deployContract as dc
import source.modules.environmentSetup as es
import source.modules.environmentUpdate as eu
import source.modules.updateChain as uc
import source.modules.autoCheck as ac
import source.modules.diffMachine as dm

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
    logging.info("Could not load contract... Consider deploying a new one.")

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


# Diff Window
class DiffWindow(QWidget):
    def __init__(self):
        super().__init__()
        # Parent layout of entire window
        layout = QVBoxLayout()
        self.label = QLabel("Difference window")  # Title
        # Layout of selection cbox and submit button
        layoutSelect = QHBoxLayout()
        comboBox = QComboBox()
        # Get list of html and times with each diff change
        self.html, timeChoices = dm.diffDisplay()
        comboBox.addItems(timeChoices)  # add to cbox
        layoutSelect.addWidget(comboBox)
        comboBox.activated.connect(self.test)
        # print(dict(zip(timeChoices, html)))
        # exit()
        self.view = QWebEngineView()
        layout.addWidget(self.label)
        layout.addLayout(layoutSelect)
        layout.addWidget(self.view)
        self.view.setHtml("<hr>This is a test</hr>")
        self.setLayout(layout)
        # self.view.show()

    def test(self, index):
        self.view.setHtml(self.html[index])
        # print('activated index', index)


# Admin control panel
class AdminWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 SpreadSheet")
        self.resize(400, 250)
        self.show()

        self.table = QTableWidget(3, 3)
        self.table.setHorizontalHeaderLabels(["Name", "User", "Role"])

        self.table.setItem(0, 0, QTableWidgetItem("Molly"))
        self.table.setItem(0, 1, QTableWidgetItem("mollyward"))
        self.table.setItem(0, 2, QTableWidgetItem("admin"))
        self.table.setColumnWidth(0, 150)

        self.table.setItem(1, 0, QTableWidgetItem("Paul"))
        self.table.setItem(1, 1, QTableWidgetItem("paulcunningham"))
        self.table.setItem(1, 2, QTableWidgetItem("admin"))

        self.table.setItem(2, 0, QTableWidgetItem("Devin"))
        self.table.setItem(2, 1, QTableWidgetItem("devinlane"))
        self.table.setItem(2, 2, QTableWidgetItem("user"))

        self.vBox = QGridLayout()
        self.vBox.addWidget(QLabel("Name:"), 0, 0)
        self.vBox.addWidget(QLineEdit(""), 0, 1)
        self.vBox.addWidget(QLabel("User:"), 1, 0)
        self.vBox.addWidget(QLineEdit(""), 1, 1)
        self.vBox.addWidget(QLabel("Role:"), 2, 0)
        self.vBox.addWidget(QLineEdit(""), 2, 1)
        self.vBox.addWidget(QPushButton("Add User"), 3, 0, 2, 2)
        self.vBox.addWidget(self.table, 5, 0, 2, 2)
        self.setLayout(self.vBox)


class CredentialWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
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
        saveCredentialButton = QPushButton("Save Changes")
        self.credButtonLayout = QHBoxLayout()
        self.credButtonLayout.addWidget(saveCredentialButton)
        saveCredentialButton.setCheckable = True
        saveCredentialButton.clicked.connect(lambda: self.updateCredentials())
        self.layout.addWidget(self.formGroupBox)
        self.layout.addWidget(saveCredentialButton)
        self.setLayout(self.layout)
        # self.setCentralWidget(widget)

    def updateCredentials(self):
        updateDict = {}
        formList = self.formGroupBox.children()
        for key, nextVal in enumerate(formList):
            if isinstance(nextVal, QLabel):
                if formList[key + 1].text():
                    updateDict[nextVal.text()] = formList[key + 1].text()

        if updateDict:
            # Update environment variables
            eu.updateEnv(updateDict)
            # Quit app
            QCoreApplication.quit()
            # Start new instance of application

            # Reload .env file
            reload(es)
            status = QProcess.startDetached(sys.executable, sys.argv)
            # Terminate current app
            signal.signal(signal.SIGQUIT, sigquit_handler)


# Our window
class MainWindow(QMainWindow):
    def closeEvent(self, *args, **kwargs):
        super(QMainWindow, self).closeEvent(*args, **kwargs)
        try:
            for file in os.scandir(basedir + "/source/tmp"):
                # os.remove(file)
                pass
            # print("terminating process{}".format(proc2))
            # proc2.terminate()
            # proc2.join()
            # # p.wait()
            # print("Process terminated.")
            # print("Process{}".format(proc2))
        except:
            print("Could not terminate python process")

    def __init__(self):
        # initialize parent model
        super().__init__()
        self.layout = QVBoxLayout(self)
        # set up our UI
        self.setWindowTitle("GEthereum")
        self.title = QLabel("GEthereum Main Window")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Initialize all buttons
        self.buttonInitialize()
        # Initialize logbox
        self.logInitialize()
        # Initialize tabs
        self.tabInitialize()

        # set our view of the page
        widget = QWidget()
        self.layout.addWidget(self.tabs)
        widget.setLayout(self.layout)  # apply layout to our widget
        # Force screen to maximize
        self.showMaximized()

        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        self.setCentralWidget(widget)

    # Function to show admin window
    def showAdminWindow(self):
        self.adminWindow = AdminWindow()
        self.adminWindow.show()

    # Function to display file differences
    def showDiffs(self, checked):
        self.diffWindow = DiffWindow()
        self.diffWindow.show()

    def showCredentialWindow(self):
        self.credWindow = CredentialWindow()
        self.credWindow.show()

    def buttonInitialize(self):
        # initialize our labels/buttons/tables
        queryButton = QPushButton("Query Chain")
        configPushButton = QPushButton("Publish New Configuration")
        deployButton = QPushButton("Deploy Contract")
        fileDiffButton = QPushButton("See File History")
        adminWindowButton = QPushButton("User Management")
        openCredentialButton = QPushButton("Update Credentials")
        # Individual layout of buttons (tab 1)
        self.mainButtonLayout = QHBoxLayout()
        self.mainButtonLayout.addWidget(fileDiffButton)
        self.mainButtonLayout.addWidget(configPushButton)
        self.mainButtonLayout.addWidget(queryButton)
        self.mainButtonLayout.addWidget(deployButton)
        # Layout of tab 2
        self.configButtonLayout = QVBoxLayout()
        self.configButtonLayout.addWidget(adminWindowButton)
        self.configButtonLayout.addWidget(openCredentialButton)
        # Layout of buttons (tab 2)
        # Define backend functions for our buttons when pushed
        queryButton.setCheckable = True
        queryButton.clicked.connect(lambda: self.getData())
        configPushButton.setCheckable = True
        configPushButton.clicked.connect(lambda: self.pushConfig())
        deployButton.setCheckable = True
        deployButton.clicked.connect(lambda: self.updateContract())
        fileDiffButton.clicked.connect(self.showDiffs)
        adminWindowButton.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        adminWindowButton.clicked.connect(self.showAdminWindow)
        openCredentialButton.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        openCredentialButton.clicked.connect(self.showCredentialWindow)

    # Set up logging box
    def logInitialize(self):
        # Log view
        self.logBox = QTextEditLogger(self)
        self.logBox.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        logging.getLogger().addHandler(self.logBox)
        logging.getLogger().setLevel(logging.DEBUG)

    # Set up tabs and layout
    def tabInitialize(self):
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tabs.addTab(self.tab1, "Main View")
        self.tabs.addTab(self.tab2, "Configuration")
        # Total layout of pages
        self.tab1.layout = QVBoxLayout()
        self.tab2.layout = QVBoxLayout()
        tab2Title = QLabel("Configuration Message")
        tab2Title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tab2.layout.addWidget(tab2Title)
        self.tab2.layout.addLayout(self.configButtonLayout)
        # add our widgets to each layout
        self.tab1.layout.addWidget(self.title)
        self.tab1.layout.addLayout(self.mainButtonLayout)
        # Table view
        self.table = QTableView()
        self.tab1.layout.addWidget(self.table)
        self.tab1.layout.addWidget(self.logBox.widget)
        self.tab1.setLayout(self.tab1.layout)
        self.tab2.setLayout(self.tab2.layout)

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
        except Exception as e:
            logging.error(e)
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
        dc.main()
        try:
            # dc.main()
            # Update table
            self.getData()
            logging.info("Contract deployed and table updated!")
        except:
            logging.error(
                (
                    "An error occured when deploying the contract or querying the chain. Please make sure you have a valid connection to the server and that your .env file is up to date."
                )
            )


def sigquit_handler(signum, frame):
    sys.exit(app.exec_())


# p = subprocess.Popen(["python", "process.py"])


def backgroun():
    ac.main()


if __name__ == "__main__":
    # multiprocessing.freeze_support()
    # proc2 = multiprocessing.Process(target=backgroun)
    # proc2.daemon = True
    # proc2.start()

    app = QApplication([])
    window = MainWindow()
    window.show()

    app.exec()

# app.aboutToQuit.connect(exitHandler())
