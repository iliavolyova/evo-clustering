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
    update_gencount = pyqtSignal(int)
    core = None

    def work(self):
        for i in range(self.core.config.trajanje_svijeta):
            self.update_data.emit(self.core.cycle())
            self.update_gencount.emit(i)
        self.finished.emit()

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(QMainWindow, self).__init__(parent)
        self.isPlotShowing = False
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        p = self.initParams()
        self.ui.graphicsView.setParameters(p)
        p.sigTreeStateChanged.connect(self.change_params)

        self.core = Core(Config(self.activeParams))

        self.plot = gui_scatter.ScatterPlot(self.core.config.dataset.data)
        self.axestable = AxesTable(self, self.ui.table_axes)

        self.histogram = HistoPlot(self.ui.histogram_widget)

        self.ui.button_start.clicked.connect(self.start)
        self.ui.checkBox_plotShowing.stateChanged.connect(self.show_plot)

    def show_plot(self, state):
        self.plot.show(state)

    def change_params(self, param, changes):
        for param, change, data in changes:
            self.activeParams[param.name()] = data
        self.core = Core(Config(self.activeParams))
        self.plot.setData(self.core.config.dataset.data)

    def start(self):
        self.thread = QtCore.QThread()
        self.worker = Worker()
        self.worker.core = self.core
        self.worker.update_gencount.connect(self.plot.w.setGenerationCount)
        self.worker.update_data.connect(self.plot.w.groupItems)
        self.worker.update_data.connect(self.histogram.update)
        self.worker.moveToThread(self.thread)
        self.worker.finished.connect(self.thread.quit)
        self.thread.started.connect(self.worker.work)
        self.thread.start()

    def initParams(self):
        self.activeParams = {
            'Dataset' : 'Iris',
            'Number of generations' : 100
        }
        params = [ {'name': 'General', 'type': 'group', 'children': [
            {'name': 'Dataset', 'type': 'list', 'values': {"Iris": "Iris", "Wine": "Wine", "Glass": "Glass"}, 'value': self.activeParams['Dataset']},
            {'name': 'Number of generations', 'type': 'int', 'value': self.activeParams['Number of generations']}]}]
        return paramtree.Parameter.create(name='', type='group', children=params)

def main():
    app = QApplication(sys.argv)
    main = MainWindow(parent=None)
    main.show()
    app.exec_()

if __name__ == "__main__":
    main()