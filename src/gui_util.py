from PyQt4 import QtCore, QtGui
import re
import numpy as np
import pyqtgraph.parametertree as paramtree

from core import Config

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
        self.plot = self.widget.plot(x=x, y=y, stepMode=True, fillLevel=0, brush=(0,0,255,150))

    def update(self, vals):
        y,x = np.histogram(vals, bins=range(5))
        self.plot.setData(x=x, y=y)

class ParamTree():
    def __init__(self):
        self.activeParams = {
            'Dataset' : 'Iris',
            'Number of generations' : 100,
            'Population size': 20,
            'Max clusters' : 5,
            'Fitness method': 'db',
            'q' : 2,
            't' : 2,
        }
        self.datasetParams = {
            'Size' : 150,
            'Features': 4,
            'Classes': 3,
            'Iris-setosa' : 50,
            'Iris-versicolor': 50,
            'Iris-virginica': 50
        }
        self.params = [
            {'name': 'Algorithm properties', 'type': 'group', 'children': [
                {'name': 'Dataset', 'type': 'list', 'values': {"Iris": "Iris", "Wine": "Wine", "Glass": "Glass"}, 'value': self.activeParams['Dataset']},
                {'name': 'Number of generations', 'type': 'int', 'value': self.activeParams['Number of generations']},
                {'name': 'Max clusters', 'type': 'int', 'value': self.activeParams['Max clusters']},
                {'name': 'Population size', 'type': 'int', 'value': self.activeParams['Population size']},
                {'name': 'Fitness method', 'type': 'list', 'values': {"db": "db", "cs": "cs"}, 'value': self.activeParams['Fitness method']},
                {'name': 'q', 'type': 'int', 'value': self.activeParams['q']},
                {'name': 't', 'type': 'int', 'value': self.activeParams['t']}]
            },
            {'name': 'Dataset stats', 'type': 'group', 'children': [
                {'name': 'Size', 'type': 'int', 'value': self.datasetParams['Size'], 'readonly': True},
                {'name': 'Features', 'type': 'int', 'value': self.datasetParams['Features'], 'readonly': True},
                {'name': 'Classes', 'type': 'int', 'value': self.datasetParams['Classes'], 'readonly': True},
                {'name': 'Class clusters', 'type': 'group', 'children': [
                    {'name': 'Iris-setosa', 'type': 'int', 'value': self.datasetParams['Iris-setosa'], 'readonly': True},
                    {'name': 'Iris-versicolor', 'type': 'int', 'value': self.datasetParams['Iris-versicolor'], 'readonly': True},
                    {'name': 'Iris-virginica', 'type': 'int', 'value': self.datasetParams['Iris-virginica'], 'readonly': True},
                ]}]
            }]

        self.tree = paramtree.Parameter.create(name='', type='group', children=self.params)

    def addClusters(self, clusters):
        clustersGroup = self.tree.child('Dataset stats').child('Class clusters')
        clustersGroup.clearChildren()
        children = []

        for k, v in clusters.iteritems():
            children.append({'name': k, 'value': v, 'type': 'int', 'readonly': True})

        clustersGroup.addChildren(children)
