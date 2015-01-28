from PyQt4 import QtCore, QtGui
import re
import numpy as np


class AxesTable():
    def __init__(self, main_window, table_axes):
        self.table = table_axes
        self.main = main_window
        columns = table_axes.columnCount()
        rows = table_axes.rowCount()
        for row in range(rows):
            for column in range(columns):
                item = QtGui.QTableWidgetItem('')
                if column == 1:
                    item.setCheckState(QtCore.Qt.Unchecked)
                    flags = ~QtCore.Qt.ItemIsEnabled
                    flags |= QtCore.Qt.ItemIsUserCheckable
                    item.setFlags(flags)
                table_axes.setItem(row, column, item)
        self.table.cellChanged.connect(self.check_input)
        self.addItem(0,0, '0 1 2')

    def check_input(self, row, col):
        item = self.table.item(row, col)
        regex = re.compile(r'^([0-9]+)\D+([0-9]+)\D+([0-9]+)$')
        match = regex.search(self.table.item(row, 0).text())
        if match:
            axes = [int(num) for num in match.groups()]
            if col == 1 and axes:
                self.main.plot.setVisible(row, item.checkState(), axes)
            if col == 0 and axes:
                self.main.plot.editViews(row, axes)
                checkbox = self.table.item(row, 1)
                checkbox.setCheckState(QtCore.Qt.Checked)
                checkbox.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        else:
            item.setText('')

    def addItem(self, row, col, text):
        if col == 0:
            item = QtGui.QTableWidgetItem(text)
            checkbox = self.table.item(row, 1)
            checkbox.setCheckState(QtCore.Qt.Checked)
            checkbox.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            self.table.setItem(row, col, item)


class HistoPlot():
    def __init__(self, plot_widget):
        self.widget = plot_widget
        y,x = np.histogram([], bins=range(5))
        self.plot = self.widget.plot(x, y, stepMode=True, fillLevel=0, brush=(0,0,255,150))

    def update(self, vals):
        y,x = np.histogram(vals, bins=range(5))
        self.plot.setData(x=x, y=y)