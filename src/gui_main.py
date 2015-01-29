import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *


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
            #self.update_fitness.emit(result.fitnessmap)
            self.update_gencount.emit(i)
        self.finished.emit()

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(QMainWindow, self).__init__(parent)
        self.isPlotShowing = False
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.parameters = ParamTree()
        self.ui.graphicsView.setParameters(self.parameters.tree, showTop=False)
        self.parameters.tree.sigTreeStateChanged.connect(self.change_params)

        self.config = Config(self.parameters.activeParams)

        self.plot = gui_scatter.ScatterPlot(self.config.dataset.data)
        self.plot.w.die.connect(self.untick_show_plot)

        self.axestable = AxesTable(self, self.ui.table_axes)
        self.histogram = HistoPlot(self.ui.histogram_widget, 5)
        self.histogram.add_optimal(self.config.dataset.params)

        self.ui.button_start.clicked.connect(self.start)
        self.ui.checkBox_plotShowing.stateChanged.connect(self.show_plot)

    def show_plot(self, state):
        self.plot.show(state)

    def fitprint(self, fitmap):
        print fitmap

    def change_params(self, param, changes):
        for param, change, data in changes:
            if param.name() in self.parameters.activeParams:
                self.parameters.activeParams[param.name()] = data
        self.config = Config(self.parameters.activeParams)
        if param.opts['name'] == 'Dataset':
            self.histogram = HistoPlot(self.ui.histogram_widget, self.config.k_max)
            self.histogram.add_optimal(self.config.dataset.params)
            self.plot.setData(self.config.dataset.data)
            for key, value in self.config.dataset.params.iteritems():
                children = self.parameters.tree.child('Dataset stats').children()
                for c in children:
                    if c.name() == key:
                        c.setValue(value)
                if key == 'Clusters':
                    self.parameters.addClusters(value)

    def start(self):
        self.histogram.add_current()
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
    
    def closeEvent(self, QCloseEvent):
        self.plot.w.close()
        QCloseEvent.accept()
    
    def untick_show_plot(self):
        self.ui.checkBox_plotShowing.setCheckState(Qt.Unchecked)

def main():
    app = QApplication(sys.argv)
    main = MainWindow(parent=None)
    main.show()
    app.exec_()

if __name__ == "__main__":
    main()