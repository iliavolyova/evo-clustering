from __future__ import division
import pyqtgraph.opengl as gl
import numpy as np
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class ScatterPlot():

    def __init__(self, data):
        self.data = data
        self.w = MyGLView()
        self.w.opts['distance'] = 35
        self.w.show()
        self.w.setWindowTitle("3D Scatter Plot")

        self.initGrids()

    def editViews(self, decViewNum, dimensions):
        viewTrans, viewRepr = self.toBinDigitList(decViewNum)
        if viewRepr in self.w.views:
            self.w.views[viewRepr] = dimensions
        else:
            self.addView(viewTrans, dimensions)

    def addView(self, viewnum, dimensions):
        positions = np.array([np.array([
            (point[dimensions[0]] + 0.05) * viewnum[0],
            (point[dimensions[1]] + 0.05) * viewnum[1],
            (point[dimensions[2]] + 0.05) * viewnum[2]])
                              * 10 for point in self.data])

        item = gl.GLScatterPlotItem(pos=positions, color=(1,1,1,1), size=0.5, pxMode=False)
        viewrepr = " ".join(str(v) for v in viewnum)
        self.w.views[viewrepr] = dimensions
        self.w.dataItems[viewrepr] = item
        self.w.addItem(item)

    def setVisible(self, row, show, dimensions):
        viewTrans, viewRepr = self.toBinDigitList(row)
        if viewRepr in self.w.views and not show:
            del self.w.views[viewRepr]
            self.w.removeItem(self.w.dataItems[viewRepr])
            del self.w.dataItems[viewRepr]
        elif viewRepr not in self.w.views and show:
            self.editViews(row, dimensions)

    def show(self, state):
        if state == Qt.Checked:
            self.w.show()
        else:
            self.w.hide()

    def showGrid(self, flag):
        if flag:
            self.initGrids()
        else:
            for i in self.w.gridItems:
                 self.w.removeItem(i)
            self.w.gridItems = []

    def setSampleSize(self, size):
        scaledSize = size / 10
        for key, item in self.w.dataItems.iteritems():
            item.setData(size=scaledSize)

    def setData(self, data):
        self.data = data
        self.w.clearData()
        self.editViews(0, [0, 1, 2])

    def initGrids(self):
        x = gl.GLGridItem()
        x.translate(5, 0, 0)
        x.scale(0.5, 1, 1)
        y = gl.GLGridItem()
        y.rotate(90, 0 , 1 ,0)
        z = gl.GLGridItem()
        z.rotate(90, 1, 0, 0)
        z.translate(5, 0, 0)
        z.scale(0.5, 1, 1)
        self.w.addItem(x)
        self.w.addItem(y)
        self.w.addItem(z)
        self.w.gridItems.append(x)
        self.w.gridItems.append(y)
        self.w.gridItems.append(z)

    def toBinDigitList(self, row):
        binstring = self.tobin(row).zfill(3)
        view = [int(x) for x in list(binstring)]
        viewTrans = [num+1 if num == 0 else num-2 for num in view]
        viewRepr = " ".join(str(v) for v in viewTrans)
        return (viewTrans, viewRepr)

    def tobin(self,i):
        if i == 0:
            return "0"
        s = ''
        while i:
            if i & 1 == 1:
                s = "1" + s
            else:
                s = "0" + s
            i >>= 1
        return s


class MyGLView(gl.GLViewWidget):
    die = pyqtSignal()

    def __init__(self):
        super(MyGLView, self).__init__()
        self.centerOnScreen()
        self.views = {}
        self.dataItems = {}
        self.gridItems = []
        self.generations = 0
        self.colors = {
            0: np.array([255, 0, 0]),
            1: np.array([0, 255, 0]),
            2: np.array([0, 0, 255]),
            3: np.array([0, 125, 125]),
            4: np.array([125, 125, 0]),
            5: np.array([125, 0, 125]),
            6: np.array([255, 0 , 255]),
            7: np.array([0, 255, 255])
        }

    def setGenerationCount(self, gencount):
        self.generations = gencount
        self.update()

    def groupItems(self, groups):
        colormap = np.array([self.colors[i] for i in groups])
        for key, item in self.dataItems.iteritems():
            item.setData(color=colormap)

    def clearData(self):
        for key, data in self.dataItems.iteritems():
            if self.dataItems[key] in self.items:
                self.removeItem(data)
        self.views = {}

    def paintGL(self, *args, **kwds):
        gl.GLViewWidget.paintGL(self, *args, **kwds)
        for v in self.views:
            vi = v.split(" ")
            self.renderText(int(vi[0])*5, int(vi[1])*5, int(vi[2]) * 11, str(self.views[v]))
        self.renderText(0, 0, 13, "Generation: " + str(self.generations))

    def centerOnScreen (self):
        resolution = QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))

    def closeEvent(self, QCloseEvent):
        self.die.emit()
        QCloseEvent.accept()
