from __future__ import division
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import numpy as np
from scipy import spatial
from sklearn.cluster import *

import gui_graphs
import gui_scatter
from core import *
import log
import stats
from gui_util import *
from ui.gui import Ui_MainWindow

import Tkinter # zbog pyinstallera
import FileDialog # zbog pyinstallera
from Tkinter import *
from tkFileDialog import *

import random
from functools import partial

from sklearn import metrics

class Worker(QtCore.QObject):
    log = pyqtSignal(str)
    finished = pyqtSignal()
    update_data = pyqtSignal(np.ndarray)
    update_centroids = pyqtSignal(list)
    update_fitness = pyqtSignal(np.ndarray)
    update_gencount = pyqtSignal(int)
    core = None
    isLogging = False
    running = False

    def work(self):
        logger = log.Log()

        if self.isLogging:
            root = Tkinter.Tk()
            root.withdraw()
            f = asksaveasfilename(parent=root, filetypes=[('CSV', '*.csv')], defaultextension=".csv")
            logger.set_file(f)
            logger.set_header(self.core.config)
            optklasteri =  self.core.config.dataset.params['ClusterMap']


        for i in range(self.core.config.trajanje_svijeta):
            if self.running:
                result = self.core.cycle()
                self.update_data.emit(result.colormap)
                self.update_fitness.emit(result.fitnessmap)
                self.update_centroids.emit(result.centroids)
                self.update_gencount.emit(i)
                if self.isLogging:
                    logger.push_colormap(result.colormap)
                    logger.push_measures([
                        metrics.adjusted_rand_score(result.colormap, optklasteri),
                        metrics.adjusted_mutual_info_score(result.colormap, optklasteri),
                        metrics.homogeneity_score(result.colormap, optklasteri),
                        metrics.completeness_score(result.colormap, optklasteri),
                        metrics.v_measure_score(result.colormap, optklasteri),
                        max(result.fitnessmap)
                    ])
            if i == self.core.config.trajanje_svijeta - 1 and self.core.config.fitness_metoda == 'db' and not self.core.config.weights_on and self.isLogging:
                for algoritam in ["km", "dbs"]:
                    if algoritam == "km":
                        km_klas = KMeans(n_clusters = self.core.config.k_max, init = 'random', n_init=self.core.config.velicina_populacije, max_iter = self.core.config.trajanje_svijeta)
                        km_klas.fit(self.core.config.dataset.data)
                        rez = km_klas.predict(self.core.config.dataset.data)
                    else:
                        npa = np.array(self.core.config.dataset.data) # bug, ne ide bez
                        dbs_klas = DBSCAN().fit(npa)
                        rez = dbs_klas.fit_predict(npa)

                    min_boja = min(rez)
                    rez = [x - min_boja for x in rez]

                    max_boja = max(rez)
                    vr = set(rez)
                    if len(vr) != max_boja + 1:
                        offset = 0
                        for i in range(max_boja + 1):
                            if i in vr:
                                rez = [i - offset if rez[j] == i else rez[j] for j in range(len(rez))]
                            else:
                                offset += 1

                    logger.measures[i][6:9] = [0, 0, 0]
                    if algoritam == 'km':
                        try:
                            logger.measures[i][6] = self.core.config.dataset.getFitnessOf(self.core.config, rez) if len(vr) > 1 else 0.0001
                        except:
                            pass
                    else:
                        try:
                            logger.measures[i][7] = len(vr)
                            logger.measures[i][8] = self.core.config.dataset.getFitnessOf(self.core.config, rez) if len(vr) > 1 else 0.0001
                        except:
                            pass



        self.update_gencount.emit(self.core.config.trajanje_svijeta)

        if self.isLogging:
            logger.flush()

        self.finished.emit()

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(QMainWindow, self).__init__(parent)
        self.isLogging = False
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.parameters = ParamTree()
        self.ui.graphicsView.setParameters(self.parameters.tree, showTop=False)
        self.parameters.tree.sigTreeStateChanged.connect(self.change_params)

        self.config = Config(self.parameters.activeParams)
        self.resultPlots = {}

        self.plot = gui_scatter.ScatterPlot(self.config.dataset.data)
        self.plot.w.die.connect(self.untick_show_plot)

        self.graphs = gui_graphs.GraphsWrapper(self.config)
        self.graphs.w.reinit_graphs(self.config, self.parameters)
        self.graphs.w.graphsdying.connect(self.untick_show_graphs)

        self.axestable = AxesTable(self, self.ui.table_axes)

        self.stats_tab = stats.Stats(self.ui)

        self.ui.button_start.clicked.connect(self.start)
        self.ui.checkBox_plotShowing.stateChanged.connect(self.plot.show)
        self.ui.checkbox_graphs.stateChanged.connect(self.graphs.show_graphs)
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
        self.plot.reinitPlot(self.config.dataset.data)
        if param.opts['name'] == 'Dataset':
            for key, value in self.config.dataset.params.iteritems():
                children = self.parameters.tree.child('Dataset stats').children()
                for c in children:
                    if c.name() == key:
                        c.setValue(value)
                if key == 'Clusters':
                    self.parameters.addClusters(value)
                if key == 'Feature weights':
                    self.parameters.addFeatureSignificance(value)
        elif param.opts['name'] == 'Number of generations':
            self.graphs.w.fitness_plot.redraw_optimal(param.opts['value'])
            self.ui.evolutions_label.setText('0 of ' + str(self.parameters.activeParams['Number of generations']))

        self.graphs.w.reinit_graphs(self.config, self.parameters)
        self.plot.setData(self.config.dataset.data)
        if 'ClusterMap' in self.config.dataset.params:
            self.plot.w.groupItems(self.config.dataset.params['ClusterMap'])
            self.graphs.w.histogram.add_optimal(self.config.dataset.params)

    def start(self):
        self.thread = QtCore.QThread(self)

        if hasattr(self, 'worker') and self.worker.running:
            self.worker.running = False
            self.ui.button_start.setText("Start")
            return

        self.graphs.w.reinit_graphs(self.config, self.parameters)
        self.ui.button_start.setText("Stop")
        self.graphs.w.histogram.add_current()
        self.worker = Worker()
        self.worker.isLogging = self.isLogging
        self.worker.core = Core(self.config)
        self.worker.update_gencount.connect(self.plot.w.setGenerationCount)
        self.worker.update_gencount.connect(self.update_progress_bar)
        self.worker.update_data.connect(self.plot.w.groupItems)
        self.worker.update_centroids.connect(self.plot.w.update_centroids)
        self.worker.update_data.connect(self.graphs.w.histogram.update)
        self.worker.update_fitness.connect(self.graphs.w.fitness_plot.add_fitness)
        #self.worker.log.connect(self.write_log)
        self.worker.moveToThread(self.thread)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.finished_job)
        self.thread.started.connect(self.worker.work)
        self.worker.running = True
        self.thread.start()
    
    def closeEvent(self, QCloseEvent):
        self.plot.w.close()
        self.graphs.w.close()
        del self.graphs
        for k, v in self.resultPlots.iteritems():
            v.w.close()
        for k,v in self.stats_tab.plots.iteritems():
            v.close()
        del self.stats_tab
        del self.resultPlots
        QCloseEvent.accept()
    
    def untick_show_plot(self):
        self.ui.checkBox_plotShowing.setCheckState(Qt.Unchecked)

    def untick_show_graphs(self):
        self.ui.checkbox_graphs.setCheckState(Qt.Unchecked)

    def update_progress_bar(self, progress):
        generations = self.parameters.activeParams['Number of generations']
        scaled = (progress / generations) * 100
        self.ui.progressBar.setValue(scaled)
        self.ui.evolutions_label.setText(str(progress) + ' of ' + str(generations))

    #def write_log(self, text):
    #    if self.isLogging:
    #        root = Tkinter.Tk()
    #        root.withdraw()
    #        f = asksaveasfile(parent=root, mode='w', filetypes=[('CSV', '*.csv')], defaultextension=".csv")
    #        f.write(text)
    #        f.close()

    def set_visible_results_plot(self, row, view, state):
        if state:
            data = self.config.dataset.data
            self.resultPlots[row] = gui_scatter.ScatterPlot(data, title="Optimal clusters for " + str(view), labels=False)
            self.resultPlots[row].setData(data, row, view)
            if 'ClusterMap' in self.config.dataset.params:
                self.resultPlots[row].w.groupItems(self.config.dataset.params['ClusterMap'])
            self.resultPlots[row].w.die.connect(partial(self.axestable.untick_result, row))
        elif not state and row in self.resultPlots:
            self.resultPlots[row].w.close()
            del self.resultPlots[row]

    def finished_job(self):
        self.worker.running = False
        self.ui.button_start.setText("Start")

def main():
    app = QApplication(sys.argv)
    main = MainWindow(parent=None)
    main.show()
    app.exec_()

if __name__ == "__main__":
    random.seed(100)
    main()