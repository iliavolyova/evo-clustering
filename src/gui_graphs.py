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
        self.moveToPosition()
        self.show()
        self.histoWidget = layout.addPlot(title="Cluster histogram")
        self.fitnessWidget = layout.addPlot(title="Fitness graph")

    def reinit_graphs(self, config, parameters):
        if config.dataset.params['ClusterMap'] is not None:
            optimalFitness = config.dataset.getOptimalFitness(config)
        else:
            optimalFitness = 0
        self.fitness_plot = FitnessPlot(self.fitnessWidget, optimalFitness, parameters.activeParams['Number of generations'])
        self.histogram = HistoPlot(self.histoWidget, parameters.activeParams['Max clusters'])
        self.histogram.add_optimal(self.config.dataset.params)

    def moveToPosition(self):
        resolution = QDesktopWidget().screenGeometry()
        self.move(resolution.width() - self.frameSize().width(),
                  resolution.height() - self.frameSize().height())

    def closeEvent(self, QCloseEvent):
        self.graphsdying.emit()
        QCloseEvent.accept()

class FitnessPlot():
    def __init__(self, widget, optimalFitness, initial_generations):
        self.widget = widget
        self.widget.clear()
        self.widget.setLabel('left', 'Fitness value')
        self.widget.setLabel('bottom', 'Generation')
        if self.widget.legend is None:
            self.legendIsSet = False
            self.widget.addLegend(offset=(-1,1))
        else:
            self.legendIsSet = True
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

        if not self.legendIsSet:
            mockplotdataopt = pg.PlotDataItem(pen='r')
            self.widget.legend.addItem(mockplotdataopt, 'optimal')
            mockplotdata = pg.PlotDataItem(pen='b')
            self.widget.legend.addItem(mockplotdata, 'best')
            mockfilldata = pg.PlotDataItem(pen=(100, 100, 255))
            self.widget.legend.addItem(mockfilldata, 'all')
        self.legendIsSet = True

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
        if self.widget.legend is None:
            self.legendIsSet = False
            self.widget.addLegend(offset=(-1,1))
        else:
            self.legendIsSet = True
        self.widget.setLabel('left', 'Samples in cluster')
        self.widget.setLabel('bottom', 'Cluster')
        self.max_clusters = max_clusters

    def add_optimal(self, dataset_params):
        self.dataset_params = dataset_params

        self.bins = np.arange(1, dataset_params['Classes'] + 1)
        data = dataset_params['ClusterMap']
        y = [data.count(i) for i in self.bins]
        self.optimal = pg.BarGraphItem(x=self.bins, height=sorted(y, reverse=True), width=0.8, brush='r')
        self.widget.addItem(self.optimal)
        if not self.legendIsSet:
            mockplotdata = pg.PlotDataItem(pen='r')
            self.widget.legend.addItem(mockplotdata, 'optimal')

    def add_current(self):
        if len(self.bins) < self.max_clusters:
            self.bins = np.arange(1, self.max_clusters + 1)
            y = [self.dataset_params['ClusterMap'].count(i) for i in self.bins]
            self.optimal.setOpts(height=y)
        self.optimal.setOpts(x=self.bins-0.2, width=0.4)
        self.current = pg.BarGraphItem(x=self.bins+0.2, height=np.zeros(len(self.bins)), width=0.4, brush='b', name='current clusters')
        self.widget.addItem(self.current)

        if not self.legendIsSet:
            mockplotdata = pg.PlotDataItem(pen='b')
            self.widget.legend.addItem(mockplotdata, 'current')
        self.legendIsSet = True

    def update(self, vals):
        scaledvals = vals + 1
        y = [scaledvals.tolist().count(i) for i in self.bins]
        self.current.setOpts(height=sorted(y, reverse=True))