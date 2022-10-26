import sys
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt


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

        data = [('2022-07-04 17:49:11',
  '0xfcf9b277a29ca61e5661ff86a2ce053748b0ca0abf7c887a98c78ec84094a149',
  'DESKTOP-V8GI6RV',
  '0x2d390a10bb93c044a71734c1e87dfe7569f27cb539e42b16bc02e09087671636'),
 ('2022-07-04 17:49:11',
  '0xfcf9b277a29ca61e5661ff86a2ce053748b0ca0abf7c887a98c78ec84094a149',
  'DESKTOP-V8GI6RV',
  '0xb7795ef98a132a90f90748a47d5c65e52d8d987f52d85edf1a1601f3a4dd354f'),
 ('2022-07-04 17:49:11',
  '0xfcf9b277a29ca61e5661ff86a2ce053748b0ca0abf7c887a98c78ec84094a149',
  'DESKTOP-V8GI6RV',
  '0xcf8f64f944e563c500048fded6d131edb8aa137d6d9280c8b858615985f1a3d2'),
 ('2022-07-04 17:49:11',
  '0xfcf9b277a29ca61e5661ff86a2ce053748b0ca0abf7c887a98c78ec84094a149',
  'DESKTOP-V8GI6RV',
  '0x14627426ba68b49c8c0a9bb409c566dda85773e487178d3b45f43609cd969f1a')]

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