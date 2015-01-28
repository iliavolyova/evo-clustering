# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui.ui'
#
# Created: Wed Jan 28 01:44:31 2015
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from pyqtgraph.parametertree import ParameterTree
from pyqtgraph import PlotWidget

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(763, 572)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 781, 551))
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab_current = QtGui.QWidget()
        self.tab_current.setObjectName(_fromUtf8("tab_current"))
        self.button_start = QtGui.QPushButton(self.tab_current)
        self.button_start.setGeometry(QtCore.QRect(10, 450, 96, 33))
        self.button_start.setObjectName(_fromUtf8("button_start"))
        self.checkBox_plotShowing = QtGui.QCheckBox(self.tab_current)
        self.checkBox_plotShowing.setGeometry(QtCore.QRect(120, 440, 101, 41))
        self.checkBox_plotShowing.setChecked(True)
        self.checkBox_plotShowing.setObjectName(_fromUtf8("checkBox_plotShowing"))
        self.horizontalLayoutWidget = QtGui.QWidget(self.tab_current)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(9, -1, 741, 441))
        self.horizontalLayoutWidget.setObjectName(_fromUtf8("horizontalLayoutWidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.graphicsView = ParameterTree(self.horizontalLayoutWidget)
        self.graphicsView.setObjectName(_fromUtf8("graphicsView"))
        self.verticalLayout_3.addWidget(self.graphicsView)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label = QtGui.QLabel(self.horizontalLayoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout_2.addWidget(self.label)
        self.table_axes = QtGui.QTableWidget(self.horizontalLayoutWidget)
        self.table_axes.setMaximumSize(QtCore.QSize(364, 16777215))
        self.table_axes.setRowCount(8)
        self.table_axes.setColumnCount(2)
        self.table_axes.setObjectName(_fromUtf8("table_axes"))
        item = QtGui.QTableWidgetItem()
        self.table_axes.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.table_axes.setHorizontalHeaderItem(1, item)
        self.table_axes.horizontalHeader().setVisible(True)
        self.table_axes.horizontalHeader().setCascadingSectionResizes(False)
        self.table_axes.horizontalHeader().setDefaultSectionSize(100)
        self.verticalLayout_2.addWidget(self.table_axes)
        self.histogram_widget = PlotWidget(self.horizontalLayoutWidget)
        self.histogram_widget.setObjectName(_fromUtf8("histogram_widget"))
        self.verticalLayout_2.addWidget(self.histogram_widget)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.tabWidget.addTab(self.tab_current, _fromUtf8(""))
        self.tab_stats = QtGui.QWidget()
        self.tab_stats.setObjectName(_fromUtf8("tab_stats"))
        self.tabWidget.addTab(self.tab_stats, _fromUtf8(""))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 763, 27))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Evolutional clustering", None))
        self.button_start.setText(_translate("MainWindow", "Start", None))
        self.checkBox_plotShowing.setText(_translate("MainWindow", "Show plot", None))
        self.label.setText(_translate("MainWindow", "Current run stats", None))
        item = self.table_axes.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Axes", None))
        item = self.table_axes.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "showing", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_current), _translate("MainWindow", "Current Run", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_stats), _translate("MainWindow", "Stats", None))
