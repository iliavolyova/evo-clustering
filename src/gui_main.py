from __future__ import division
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import gui_scatter
from core import *
from gui_util import *
from ui.gui import Ui_MainWindow

import Tkinter # zbog pyinstallera
import FileDialog # zbog pyinstallera
from Tkinter import *
from tkFileDialog import *

class Worker(QtCore.QObject):
    log = pyqtSignal(str)
    finished = pyqtSignal()
    update_data = pyqtSignal(np.ndarray)
    update_fitness = pyqtSignal(np.ndarray)
    update_gencount = pyqtSignal(int)
    core = None
    isLogging = False
    running = False

    def work(self):

        text = 'Iteracija:;' + ';'.join([str(s) for s in range(self.core.config.trajanje_svijeta)])
        text += '\nVrijednost fitness funkcije:'

        for i in range(self.core.config.trajanje_svijeta):
            if self.running:
                result = self.core.cycle()
                self.update_data.emit(result.colormap)
                self.update_fitness.emit(result.fitnessmap)
                self.update_gencount.emit(i)
                text += str(max(result.fitnessmap)).replace('.', ',') + ';'

        # racunamo fitness optimalne particije
        tocke = self.core.config.dataset.data
        klasteri = self.core.config.dataset.params['ClusterMap']
        particija = [[] for x in range(len(set(klasteri)))]
        for i, t in enumerate(tocke):
           particija[klasteri[i] - 1].append(t)

        testni = Kromosom(self.core.config, [], True)
        text += '\nFitness sluzbenog rjesenja:;' + str(testni.fitness(particija)).replace('.', ',')
        text += '\n(Vise je bolje)'

        if self.isLogging:
            self.log.emit()

        self.finished.emit()

    def __del__(self):
        self.running = False
        self.wait()

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(QMainWindow, self).__init__(parent)
        self.isPlotShowing = False
        self.isLogging = False
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.parameters = ParamTree()
        self.ui.graphicsView.setParameters(self.parameters.tree, showTop=False)
        self.parameters.tree.sigTreeStateChanged.connect(self.change_params)

        self.config = Config(self.parameters.activeParams)

        self.plot = gui_scatter.ScatterPlot(self.config.dataset.data)
        self.plot.w.die.connect(self.untick_show_plot)

        self.reinit_graphs()

        self.axestable = AxesTable(self, self.ui.table_axes)

        self.ui.button_start.clicked.connect(self.start)
        self.ui.checkBox_plotShowing.stateChanged.connect(self.plot.show)
        self.ui.checkBox_logging.stateChanged.connect(self.is_logging)
        self.ui.show_grid_checkbox.stateChanged.connect(self.plot.showGrid)
        self.ui.sample_size_slider.valueChanged.connect(self.plot.setSampleSize)

    def is_logging(self, state):
        self.isLogging = state

    def change_params(self, param, changes):
        for param, change, data in changes:
            if param.name() in self.parameters.activeParams:
                self.parameters.activeParams[param.name()] = data
        self.config = Config(self.parameters.activeParams)
        if param.opts['name'] == 'Dataset':
            self.histogram = HistoPlot(self.ui.histogram_widget, self.config.k_max)
            self.plot.setData(self.config.dataset.data)
            if 'ClusterMap' in self.config.dataset.params:
                self.plot.w.groupItems(self.config.dataset.params['ClusterMap'])
                self.histogram.add_optimal(self.config.dataset.params)
            for key, value in self.config.dataset.params.iteritems():
                children = self.parameters.tree.child('Dataset stats').children()
                for c in children:
                    if c.name() == key:
                        c.setValue(value)
                if key == 'Clusters':
                    self.parameters.addClusters(value)
        elif param.opts['name'] == 'Number of generations':
            self.fitness_plot.redraw_optimal(param.opts['value'])
            self.ui.evolutions_label.setText('0 of ' + str(self.parameters.activeParams['Number of generations']))

    def start(self):
        self.thread = QtCore.QThread(self)

        if hasattr(self, 'worker') and self.worker.running:
            self.worker.running = False
            self.ui.button_start.setText("Start")
            return

        self.reinit_graphs()
        self.ui.button_start.setText("Stop")
        self.histogram.add_current()
        self.worker = Worker()
        self.worker.isLogging = self.isLogging
        self.worker.core = Core(self.config)
        self.worker.update_gencount.connect(self.plot.w.setGenerationCount)
        self.worker.update_gencount.connect(self.update_progress_bar)
        self.worker.update_data.connect(self.plot.w.groupItems)
        self.worker.update_data.connect(self.histogram.update)
        self.worker.update_fitness.connect(self.fitness_plot.add_fitness)
        self.worker.log.connect(self.write_log)
        self.worker.moveToThread(self.thread)
        self.worker.finished.connect(self.thread.quit)
        self.thread.started.connect(self.worker.work)
        self.worker.running = True
        self.thread.start()
    
    def closeEvent(self, QCloseEvent):
        self.plot.w.close()
        QCloseEvent.accept()
    
    def untick_show_plot(self):
        self.ui.checkBox_plotShowing.setCheckState(Qt.Unchecked)

    def update_progress_bar(self, progress):
        generations = self.parameters.activeParams['Number of generations']
        scaled = (progress / generations) * 100
        self.ui.progressBar.setValue(scaled)
        self.ui.evolutions_label.setText(str(progress) + ' of ' + str(generations))

    def write_log(self, text):
        if self.isLogging:
            root = Tkinter.Tk()
            root.withdraw()
            f = asksaveasfile(parent=root, mode='w', filetypes=[('CSV', '*.csv')], defaultextension=".csv")
            f.write(text)
            f.close()

    def reinit_graphs(self):
        optimalFitness = self.config.dataset.getOptimalFitness(self.config)
        self.fitness_plot = FitnessPlot(self.ui.fitnes_widget, optimalFitness, self.parameters.activeParams['Number of generations'])
        self.histogram = HistoPlot(self.ui.histogram_widget, 5)
        self.histogram.add_optimal(self.config.dataset.params)

def main():
    app = QApplication(sys.argv)
    main = MainWindow(parent=None)
    main.show()
    app.exec_()

if __name__ == "__main__":
    main()