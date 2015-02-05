import pyqtgraph as pg
import numpy as np
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class GraphsWrapper:
    def __init__(self, config):
        self.w = Graphs(config)

    def show_graphs(self, state):
        if state == Qt.Checked:
            self.w.show()
        else:
            self.w.hide()

class Graphs(pg.GraphicsWindow):
    graphsdying = pyqtSignal()

    def __init__(self, config):
        super(Graphs, self).__init__()

        self.config = config
        layout = pg.GraphicsLayout(border=(100,100,100))
        self.setCentralItem(layout)
        self.resize(650, 250)
        self.setWindowTitle('Graphs')
        self.show()
        self.histoWidget = layout.addPlot(title="Cluster histogram")
        self.fitnessWidget = layout.addPlot(title="Fitness graph")

    def reinit_graphs(self, parameters):
        optimalFitness = self.config.dataset.getOptimalFitness(self.config)
        self.fitness_plot = FitnessPlot(self.fitnessWidget, optimalFitness, parameters.activeParams['Number of generations'])
        self.histogram = HistoPlot(self.histoWidget, 5)
        self.histogram.add_optimal(self.config.dataset.params)

    def centerOnScreen (self):
        resolution = QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))

    def closeEvent(self, QCloseEvent):
        self.graphsdying.emit()
        QCloseEvent.accept()

class FitnessPlot():
    def __init__(self, widget, optimalFitness, initial_generations):
        self.widget = widget
        self.widget.clear()
        self.widget.setLabel('left', 'Fitness value')
        self.widget.setLabel('bottom', 'Generation')
        self.optfit = optimalFitness
        self.optimal = self.widget.plot()
        self.redraw_optimal(initial_generations)
        self.max_data = []
        self.min_data = []
        self.max_curve = self.widget.plot()
        self.min_curve = self.widget.plot()
        fill = pg.FillBetweenItem(self.min_curve, self.max_curve, (100, 100, 255))
        self.widget.addItem(fill)

    def redraw_optimal(self, generations):
        self.x = np.linspace(0, generations, num=generations)
        y = np.empty(generations)
        y.fill(self.optfit)
        self.optimal.setData(x=self.x, y=y, pen=(255,0,0))

    def add_fitness(self, data):
        max = np.amax(data)
        min = np.amin(data)
        self.max_data.append(max)
        self.min_data.append(min)
        self.max_curve.setData(x=self.x[:len(self.max_data)], y=self.max_data, pen='b')
        self.min_curve.setData(x=self.x[:len(self.min_data)], y=self.min_data, pen='k')

class HistoPlot():
    def __init__(self, plot_widget, max_clusters):
        self.widget = plot_widget
        self.widget.clear()
        self.widget.addLegend(offset=(-1,1))
        self.widget.setLabel('left', 'Samples in cluster')
        self.widget.setLabel('bottom', 'Cluster')
        self.max_clusters = max_clusters

    def add_optimal(self, dataset_params):
        self.dataset_params = dataset_params
        self.bins = np.arange(1, dataset_params['Classes'] + 1)
        data = dataset_params['ClusterMap']
        y = [data.count(i) for i in self.bins]
        self.optimal = pg.BarGraphItem(x=self.bins, height=sorted(y, reverse=True), width=1, brush='r')
        self.widget.addItem(self.optimal)
        mockplotdata = pg.PlotDataItem(pen='r')
        self.widget.legend.addItem(mockplotdata, 'optimal')

    def add_current(self):
        if len(self.bins) < self.max_clusters:
            self.bins = np.arange(1, self.max_clusters + 1)
            y = [self.dataset_params['ClusterMap'].count(i) for i in self.bins]
            self.optimal.setOpts(height=y)
        self.optimal.setOpts(x=self.bins-0.25, width=0.5)
        self.current = pg.BarGraphItem(x=self.bins+0.25, height=np.zeros(len(self.bins)), width=0.5, brush='b', name='current clusters')
        self.widget.addItem(self.current)
        mockplotdata = pg.PlotDataItem(pen='b')
        self.widget.legend.addItem(mockplotdata, 'current')

    def update(self, vals):
        scaledvals = vals + 1
        y = [scaledvals.tolist().count(i) for i in self.bins]
        self.current.setOpts(height=sorted(y, reverse=True))