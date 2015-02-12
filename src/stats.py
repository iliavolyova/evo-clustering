from  __future__ import division
import os
from functools import partial

import log as logger
import core
import gui_graphs

from PyQt4.QtGui import *

defaultParams = {
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

class Stats():
    def __init__(self, window):
        self.window = window
        self.plots = {}
        self.setup_ui()

    def setup_ui(self):
        self.setup_table()
        self.populate_combo()

    def populate_combo(self):
        self.resfolder = os.path.join('..', 'res')
        self.run_groups = []
        for dirname, dirnames, filenames in os.walk(self.resfolder):
            for subdirname in dirnames:
                self.run_groups.append(subdirname)

        for r in self.run_groups:
            self.window.datasetComboBox.addItem(r)

        self.window.datasetComboBox.activated.connect(self.run_group_changed)

    def run_group_changed(self, rg_index):
        run_paths = []
        self.runs = []

        if rg_index != 0:
            basepath = os.path.join(self.resfolder, self.run_groups[rg_index-1])
            for dirname, dirnames, filenames in os.walk(basepath):
                for f in filenames:
                    run_paths.append(os.path.join(basepath, f))
        else:
            self.table.clearContents()
            self.clearLabels()
            return

        log = logger.Log()
        for path in run_paths:
            run = {}
            log.load(path)
            run['params'] = log.head_as_array
            run['colormaps'] = log.colormaps
            run['measures'] = log.measures
            dirs, filename = os.path.split(path)
            run['dataset'] = filename.split('_')[2]
            run['name'] = filename
            self.runs.append(run)

        params = self.get_params(self.runs[0])
        self.window.label_dataset.setText(params['Dataset'])
        opt_config = core.Config(params)
        self.window.label_classes.setText(str(opt_config.dataset.params['Classes']))

        distribution = []
        for k, v in opt_config.dataset.params['Clusters'].iteritems():
            distribution.append(v)

        self.window.label_distribution.setText(str(distribution))

        self.populate_table()

    def populate_table(self):
        self.table.clearContents()
        self.table.setRowCount(len(self.runs)+1)
        cls_sum=0
        dist_sum=[]
        dist_cnt=[]
        for row, run in enumerate(self.runs):

            colormap = run['colormaps'][-1]
            l_counts = [colormap.count(x) for x in set(colormap)]
            l_counts.sort(reverse=True)

            for index, val in enumerate(l_counts):
                if index >= len(dist_sum):
                    dist_sum.append(val)
                    dist_cnt.append(1)
                else:
                    dist_sum[index] += val
                    dist_cnt[index] += 1
            cls_sum += len(l_counts)

            params = self.get_params(run)
            conf = core.Config(params)

            for col in range(6):
                item = QTableWidgetItem('')

                if col == 0:
                    item = QTableWidgetItem(run['name'][14:])
                elif col == 1:
                    item = QTableWidgetItem(str(len(l_counts)))
                elif col == 2:
                    item = QTableWidgetItem(str(l_counts))
                elif col == 3:
                    item = QTableWidgetItem('%.4f' % conf.dataset.getOptimalFitness(conf))
                elif col == 4:
                    item = QTableWidgetItem('%.4f' % run['measures'][-1][5])
                elif col == 5:
                    btn = QPushButton(self.table)
                    btn.setText('Show')
                    btn.clicked.connect(partial(self.show_details, row - 1))
                    self.table.setCellWidget(row+1, col, btn)

                if col != 5:
                    self.table.setItem(row+1, col, item)

        avg_clsnum = '%.3f' % (cls_sum / len(self.runs))
        avg_dist = []
        for index, val in enumerate(dist_sum):
            avg_dist.append(dist_sum[index] / dist_cnt[index])
        avg_dist_str = ["%.1f" % t for t in avg_dist]

        for index, val in enumerate(['Average', avg_clsnum, '[' + ", ".join(avg_dist_str) + ']']):
            item = QTableWidgetItem(val)
            self.table.setItem(0, index, item)

    def show_details(self, row):
        self.plots[row] = gui_graphs.DetailsPlot(self.runs[row])

    def get_params(self, run):
        defaultParams['Dataset'] = run['dataset']
        defaultParams['Number of generations'] = int(run['params'][2])
        defaultParams['Population size'] = int(run['params'][1])
        defaultParams['Max clusters'] = int(run['params'][0])
        defaultParams['Fitness method'] = run['params'][3]
        defaultParams['Distance measure'] = run['params'][4]
        defaultParams['q'] = int(run['params'][5])
        defaultParams['t'] = int(run['params'][6])
        return defaultParams

    def setup_table(self):
        self.table = self.window.table_results
        self.table.setColumnWidth(0, 235)
        self.table.setColumnWidth(1, 50)
        self.table.setColumnWidth(2, 180)
        self.table.setColumnWidth(3, 65)
        self.table.setColumnWidth(4, 65)
        self.table.setColumnWidth(5, 60)

    def clearLabels(self):
        self.window.label_classes.setText('')
        self.window.label_dataset.setText('')
        self.window.label_distribution.setText('')