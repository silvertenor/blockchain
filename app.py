from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineQuick import *
import logging
import pandas as pd
import os, json, sys, signal
from importlib import reload
import shutil, multiprocessing

# Set our base directory:
basedir = os.path.dirname(__file__)
os.environ["basedir"] = basedir
# Import custom modules
import source.modules.history as hist
import source.modules.configPush as conf
import source.modules.deployContract as dc
import source.modules.environmentSetup as es
import source.modules.environmentUpdate as eu
import source.modules.autoCheck as ac
import source.modules.diffMachine as dm
import source.modules.userManagement as um

# Read in compiled contract code
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
            self.widget.maximumSize().width(), parent.frameSize().height() // 5
        )

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


# Main table that shows all fields in blockchain:
class TableModel(QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

    def rowCount(self, index):
        try:
            return self._data.shape[0]
        except Exception as e:
            logging.error(e)
            return 0

    def columnCount(self, index):
        try:
            return self._data.shape[1]
        except Exception as e:
            logging.error(e)
            return 0

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
        self.label = QLabel("File History")  # Title
        # Layout of selection cbox and submit button
        layoutSelect = QHBoxLayout()
        comboBox = QComboBox()
        # Get list of html and labels (time + username) with each change
        self.html, labels = dm.diffDisplay()
        comboBox.addItems(labels)  # add to cbox
        layoutSelect.addWidget(comboBox)
        comboBox.activated.connect(self.updatePrettyDiff)
        # Initialize view - must be web engine for html
        self.view = QWebEngineView()
        layout.addWidget(self.label)
        layout.addLayout(layoutSelect)
        layout.addWidget(self.view)
        # Initial message:
        self.view.setHtml("<hr>Please make a selection to update this view.</hr>")
        self.setLayout(layout)

    # Function to update displayed HTML
    def updatePrettyDiff(self, index):
        self.view.setHtml(self.html[index])


# Admin control panel
class AdminWindow(QWidget):
    def __init__(self):
        super().__init__()
        # housekeeping
        self.setWindowTitle("Account Management")
        self.resize(400, 400)
        self.show()
        # Set up form
        self.setUpForm()
        # Button to save new user:
        self.saveButton = QPushButton("Commit")
        self.saveButton.setCheckable = True
        self.saveButton.clicked.connect(lambda: self.addAccount())
        # Set up table
        self.table = QTableView()
        self.updateTable()
        # Configure layout
        self.vBox = QVBoxLayout()
        self.vBox.addWidget(self.formGroupBox)
        self.vBox.addWidget(self.saveButton)
        self.vBox.addWidget(self.table)
        self.setLayout(self.vBox)

    # Function to set up form inside admin panel - fields to fill out!
    def setUpForm(self):
        self.formGroupBox = QGroupBox()
        # User's name, account address, and role (admin/user)
        self.name = QLineEdit()
        self.account = QLineEdit()
        self.role = QComboBox()
        layout = QFormLayout()
        rows = {"User": self.name, "Account Address": self.account, "Role": self.role}
        for row in rows:
            layout.addRow(QLabel(row), rows[row])
        choices = ["User", "Admin"]
        self.role.addItems(choices)
        self.formGroupBox.setLayout(layout)

    # If 'commit' button clicked, run this to add user/admin to SC library:
    def addAccount(self):
        try:
            name = self.name.text()
            account = self.account.text()
            role = self.role.currentText()
            um.add(name, account, role)
            self.updateTable()
        except Exception as e:
            logging.error(e)

    # Update the table with admin/user records
    def updateTable(self):
        try:
            admins = um.query()
            self.model = TableModel(admins)
            self.table.setModel(self.model)
            width = self.frameGeometry().width()
            for i in range(0, admins.shape[1]):
                self.table.setColumnWidth(i, width // admins.shape[1])
            logging.info("Table Updated!")
        except Exception as e:
            self.model = TableModel(pd.DataFrame())
            self.table.setModel(self.model)
            width = self.frameGeometry().width()
            logging.error(e)


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
            pass
            print("terminating process{}".format(proc2))
            proc2.terminate()
            proc2.join()
            # p.wait()
            print("Process terminated.")
            print("Process{}".format(proc2))
        except:
            print("Could not terminate python process")

    def __init__(self):
        # initialize parent model
        super().__init__()
        self.layout = QVBoxLayout()
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
        self.logBox1 = QTextEditLogger(self)
        self.logBox1.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        logging.getLogger().addHandler(self.logBox1)
        logging.getLogger().setLevel(logging.DEBUG)
        self.logBox2 = QTextEditLogger(self)
        self.logBox2.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        logging.getLogger().addHandler(self.logBox2)

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
        self.tab2.layout.addWidget(self.logBox2.widget)

        # add our widgets to each layout
        self.tab1.layout.addWidget(self.title)
        self.tab1.layout.addLayout(self.mainButtonLayout)
        # Table view
        self.table = QTableView()
        self.tab1.layout.addWidget(self.table)
        self.tab1.layout.addWidget(self.logBox1.widget)
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

        try:
            dc.main()
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

    # Function to display file differences
    def showDiffs(self, checked):
        try:
            self.diffWindow = DiffWindow()
            self.diffWindow.show()
        except Exception as e:
            logging.error(e)

    # Function to show admin window
    def showAdminWindow(self):
        try:
            self.adminWindow = AdminWindow()
            self.adminWindow.show()
        except Exception as e:
            logging.error(e)

    def showCredentialWindow(self):
        self.credWindow = CredentialWindow()
        self.credWindow.show()


def sigquit_handler(signum, frame):
    sys.exit(app.exec_())


def background():
    ac.main()


# Entrypoint:
if __name__ == "__main__":
    # multiprocessing.freeze_support()
    # proc2 = multiprocessing.Process(target=background)
    # proc2.daemon = True
    # proc2.start()

    app = QApplication([])
    window = MainWindow()
    window.show()

    app.exec()

# app.aboutToQuit.connect(exitHandler())
