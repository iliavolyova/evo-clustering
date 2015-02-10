from PyQt4 import QtCore, QtGui
import re
import pyqtgraph.parametertree as paramtree

class AxesTable():
    def __init__(self, main_window, table_axes):
        self.table = table_axes
        self.main = main_window
        columns = table_axes.columnCount()
        rows = table_axes.rowCount()
        for row in range(rows):
            for column in range(columns):
                item = QtGui.QTableWidgetItem('')
                if column in [1, 2, 3]:
                    item.setCheckState(QtCore.Qt.Unchecked)
                    flags = ~QtCore.Qt.ItemIsEnabled
                    flags |= QtCore.Qt.ItemIsUserCheckable
                    item.setFlags(flags)
                table_axes.setItem(row, column, item)
        self.table.cellChanged.connect(self.check_input)
        self.addItem(0,0, '0 1 2')

    def check_input(self, row, col):
        item = self.table.item(row, col)
        max_dimension = self.main.config.n_dims-1
        regex = re.compile(r'^([0-9]+)\D+([0-9]+)\D+([0-9]+)$')
        match = regex.search(self.table.item(row, 0).text())
        if match:
            axes = [int(num) for num in match.groups()]
            for axis in axes:
                if axis > max_dimension:
                    item.setText('')
                    return

            if col == 0 and axes:
                self.main.plot.editViews(row, axes)
                checkbox = self.table.item(row, 1)
                checkbox.setCheckState(QtCore.Qt.Checked)
                checkbox.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                checkbox_centroids = self.table.item(row, 2)
                checkbox_centroids.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                checkbox_results = self.table.item(row, 3)
                checkbox_results.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                self.main.plot.w.groupItems(self.main.config.dataset.params['ClusterMap'])
            elif col == 1 and axes:
                self.main.plot.setVisible(row, item.checkState(), axes)
                checkbox_centroids = self.table.item(row, 2)
                if item.checkState():
                    checkbox_centroids.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                else:
                    flags = ~QtCore.Qt.ItemIsEnabled
                    flags |= QtCore.Qt.ItemIsUserCheckable
                    checkbox_centroids.setFlags(flags)
            elif col == 2 and axes and self.table.item(row, 1):
                self.main.plot.setVisibleCentroid(row, item.checkState())
            elif col == 3 and axes:
                view = [int(i) for i in self.table.item(row, 0).text().split(' ')]
                self.main.set_visible_results_plot(row, view, item.checkState())
        else:
            item.setText('')

    def addItem(self, row, col, text):
        if col == 0:
            item = QtGui.QTableWidgetItem(text)
            checkbox = self.table.item(row, 1)
            checkbox2 = self.table.item(row, 2)
            checkbox.setCheckState(QtCore.Qt.Checked)
            checkbox.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            checkbox2.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            self.table.setItem(row, col, item)

    def untick_result(self, row):
        checkbox_result = self.table.item(row, 3)
        checkbox_result.setCheckState(QtCore.Qt.Unchecked)

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
            'Distance measure': 'Minkowski_2',
            'Feature significance': True
        }
        self.datasetParams = {
            'Size' : 150,
            'Features': 4,
            'Classes': 3,
            'Iris-setosa' : 50,
            'Iris-versicolor': 50,
            'Iris-virginica': 50,
            'Feature weights': [0.7826, -0.4194, 0.9490, 0.9565]
        }
        self.params = [
            {'name': 'Algorithm properties', 'type': 'group', 'children': [
                {'name': 'Dataset', 'type': 'list', 'values': {"Iris": "Iris", "Wine": "Wine", "Glass": "Glass", "Naive" : "Naive"}, 'value': self.activeParams['Dataset']},
                {'name': 'Number of generations', 'type': 'int', 'value': self.activeParams['Number of generations']},
                {'name': 'Max clusters', 'type': 'int', 'value': self.activeParams['Max clusters']},
                {'name': 'Population size', 'type': 'int', 'value': self.activeParams['Population size']},
                {'name': 'Fitness method', 'type': 'list', 'values': {"db": "db", "cs": "cs"}, 'value': self.activeParams['Fitness method']},
                {'name': 'q', 'type': 'int', 'value': self.activeParams['q']},
                {'name': 't', 'type': 'int', 'value': self.activeParams['t']},
                {'name': 'Distance measure', 'type': 'list', 'values': {"Cosine": "Cosine", "Mahalanobis": "Mahalanobis", "Minkowski_2": "Minkowski_2"}, 'value': self.activeParams['Distance measure']},
                {'name': 'Feature significance', 'type': 'bool', 'value': self.activeParams['Feature significance']}]
            },
            {'name': 'Dataset stats', 'type': 'group', 'children': [
                {'name': 'Size', 'type': 'int', 'value': self.datasetParams['Size'], 'readonly': True},
                {'name': 'Features', 'type': 'int', 'value': self.datasetParams['Features'], 'readonly': True},
                {'name': 'Classes', 'type': 'int', 'value': self.datasetParams['Classes'], 'readonly': True},
                {'name': 'Class clusters', 'type': 'group', 'children': [
                    {'name': 'Iris-setosa', 'type': 'int', 'value': self.datasetParams['Iris-setosa'], 'readonly': True},
                    {'name': 'Iris-versicolor', 'type': 'int', 'value': self.datasetParams['Iris-versicolor'], 'readonly': True},
                    {'name': 'Iris-virginica', 'type': 'int', 'value': self.datasetParams['Iris-virginica'], 'readonly': True},
                ]},
                {'name': 'Feature significance', 'type': 'group', 'children': [
                    {'name': '1', 'type': 'float', 'value': self.datasetParams['Feature weights'][0], 'readonly': True},
                    {'name': '2', 'type': 'float', 'value': self.datasetParams['Feature weights'][1], 'readonly': True},
                    {'name': '3', 'type': 'float', 'value': self.datasetParams['Feature weights'][2], 'readonly': True},
                    {'name': '4', 'type': 'float', 'value': self.datasetParams['Feature weights'][3], 'readonly': True}
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
