import sys
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from backend.loadContract import *


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.table = QtWidgets.QTableView()
        # backend code here
        # Query the hash stored on the blockchain
        on_chain_hash = hash_storage.functions.retrieve().call()[0]
        print('On-chain hash: {}'.format(on_chain_hash))
        # Generate the hash of the log file
        device_hash = '0x' + hashGenerator(DEVICE_XML_PATH).hexdigest()
        print('Local hash: {}'.format(device_hash))
        # compare the two - if different, update the blockchain!
        if on_chain_hash != device_hash:
            # Gather metadata:
            computer_id, date_changed = fileParser(LOG_TXT_PATH)
            # Get previous tx hash
            previousTxHash = w3.eth.get_block('latest')['transactions'][0].hex()
            # Encrypt the metadata before updating the chain
            computer_id, date_changed = encrypt(computer_id), encrypt(date_changed)
            # Update blockchain
            updateBlockChain(date_changed, device_hash, computer_id, previousTxHash)
        else:
            print('No change detected. Exiting program.')
        pvsTx = hash_storage.functions.retrieve().call()[3]
        history = []
        while pvsTx:
            tx = w3.eth.get_transaction(pvsTx)
            try:
                obj, params = hash_storage.decode_function_input(tx['input'])
                params['_time'] = decrypt(params['_time'])
                params['_userID'] = decrypt(params['_userID'])
                pvsTx = params['_previousTx']
                print(params)
                history.append(params)
            except:
                pvsTx = False     
        import pandas as pd
        df = pd.DataFrame(history)
        df = df[['_time', '_userID', '_hashNumber', '_previousTx']]
        df.rename(columns={'_time': 'Date', '_userID': 'User ID', '_hashNumber': 'Hash', '_previousTx': 'Previous Transaction'}, inplace=True)
        # df.set_index('_time', inplace=True)
        headers = []
        data = []
        for item in history:
            row = ()
            for key in item:
                row += item[key],
            data.append(row)
        for item in df.columns:
            headers.append(item)
#         data = [('2022-07-04 17:49:11',
#   '0xfcf9b277a29ca61e5661ff86a2ce053748b0ca0abf7c887a98c78ec84094a149',
#   'DESKTOP-V8GI6RV',
#   '0x2d390a10bb93c044a71734c1e87dfe7569f27cb539e42b16bc02e09087671636'),
#  ('2022-07-04 17:49:11',
#   '0xfcf9b277a29ca61e5661ff86a2ce053748b0ca0abf7c887a98c78ec84094a149',
#   'DESKTOP-V8GI6RV',
#   '0xb7795ef98a132a90f90748a47d5c65e52d8d987f52d85edf1a1601f3a4dd354f'),
#  ('2022-07-04 17:49:11',
#   '0xfcf9b277a29ca61e5661ff86a2ce053748b0ca0abf7c887a98c78ec84094a149',
#   'DESKTOP-V8GI6RV',
#   '0xcf8f64f944e563c500048fded6d131edb8aa137d6d9280c8b858615985f1a3d2'),
#  ('2022-07-04 17:49:11',
#   '0xfcf9b277a29ca61e5661ff86a2ce053748b0ca0abf7c887a98c78ec84094a149',
#   'DESKTOP-V8GI6RV',
#   '0x14627426ba68b49c8c0a9bb409c566dda85773e487178d3b45f43609cd969f1a')]

        self.model = TableModel(data)
        self.table.setModel(self.model)

        self.setCentralWidget(self.table)

if __name__ == "__main__":
    import sys
    app=QtWidgets.QApplication(sys.argv)
    window2 = QtWidgets.QMainWindow
    ui =MainWindow()
    # ui.__init__(app)
    ui.show()
    sys.exit(app.exec())