import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import pyqtgraph.parametertree as paramtree

import gui_scatter
from core import *
from gui_util import *
from ui.gui import Ui_MainWindow

class Worker(QtCore.QObject):
    finished = pyqtSignal()
    update_data = pyqtSignal(np.ndarray)
    update_fitness = pyqtSignal(np.ndarray)
    update_gencount = pyqtSignal(int)
    core = None

    def work(self):
        for i in range(self.core.config.trajanje_svijeta):
            result = self.core.cycle()
            self.update_data.emit(result.colormap)
            self.update_fitness.emit(result.fitnessmap)
            self.update_gencount.emit(i)
        self.finished.emit()

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(QMainWindow, self).__init__(parent)
        self.isPlotShowing = False
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        p = self.initParams()
        self.ui.graphicsView.setParameters(p, showTop=False)
        p.sigTreeStateChanged.connect(self.change_params)

        self.config = Config(self.activeParams)

        self.plot = gui_scatter.ScatterPlot(self.config.dataset.data)

        self.axestable = AxesTable(self, self.ui.table_axes)
        self.histogram = HistoPlot(self.ui.histogram_widget)

        self.ui.button_start.clicked.connect(self.start)
        self.ui.checkBox_plotShowing.stateChanged.connect(self.show_plot)

    def show_plot(self, state):
        self.plot.show(state)

    def fitprint(self, fitmap):
        print fitmap

    def change_params(self, param, changes):
        for param, change, data in changes:
            self.activeParams[param.name()] = data
        self.config = Config(self.activeParams)
        self.plot.setData(self.config.dataset.data)

    def start(self):
        self.thread = QtCore.QThread()
        self.worker = Worker()
        self.worker.core = Core(self.config)
        self.worker.update_gencount.connect(self.plot.w.setGenerationCount)
        self.worker.update_data.connect(self.plot.w.groupItems)
        self.worker.update_data.connect(self.histogram.update)
        self.worker.update_fitness.connect(self.fitprint)
        self.worker.moveToThread(self.thread)
        self.worker.finished.connect(self.thread.quit)
        self.thread.started.connect(self.worker.work)
        self.thread.start()

    def initParams(self):
        self.activeParams = {
            'Dataset' : 'Iris',
            'Number of generations' : 100,
            'Population size': 20,
            'Max clusters' : 5,
            'Fitness method': 'db',
            'q' : 2,
            't' : 2,
            'Distance measure': 'Mahalanobis'
        }
        params = [
            {'name': 'Algorithm properties', 'type': 'group', 'children': [
                {'name': 'Dataset', 'type': 'list', 'values': {"Iris": "Iris", "Wine": "Wine", "Glass": "Glass", "Naive": "Naive"}, 'value': self.activeParams['Dataset']},
                {'name': 'Number of generations', 'type': 'int', 'value': self.activeParams['Number of generations']},
                {'name': 'Max clusters', 'type': 'int', 'value': self.activeParams['Max clusters']},
                {'name': 'Population size', 'type': 'int', 'value': self.activeParams['Population size']},
                {'name': 'Fitness method', 'type': 'list', 'values': {"db": "db", "cs": "cs"}, 'value': self.activeParams['Fitness method']},
                {'name': 'q', 'type': 'int', 'value': self.activeParams['q']},
                {'name': 't', 'type': 'int', 'value': self.activeParams['t']},
                {'name': 'Distance measure', 'type': 'list', 'values': {"Cosine": "Cosine", "Mahalanobis": "Mahalanobis", "Minkowski_2": "Minkowski_2"}}]
            },
            {'name': 'Dataset stats', 'type': 'group', 'children': [
                {'name': 'Size', 'type': 'int', 'value': 150, 'readonly': True},
                {'name': 'Features', 'type': 'int', 'value': 4, 'readonly': True}]
            }]

        return paramtree.Parameter.create(name='', type='group', children=params)

def main():
    app = QApplication(sys.argv)
    main = MainWindow(parent=None)
    main.show()
    app.exec_()

if __name__ == "__main__":
    main()