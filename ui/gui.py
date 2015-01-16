# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui.ui'
#
# Created: Fri Jan 16 04:25:31 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

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
        MainWindow.resize(673, 548)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 681, 511))
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setEnabled(True)
        self.tab.setObjectName(_fromUtf8("tab"))
        self.gridLayoutWidget = QtGui.QWidget(self.tab)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(-1, -1, 681, 371))
        self.gridLayoutWidget.setObjectName(_fromUtf8("gridLayoutWidget"))
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.widget = QtGui.QWidget(self.gridLayoutWidget)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.gridLayout.addWidget(self.widget, 0, 0, 1, 1)
        self.comboBox = QtGui.QComboBox(self.tab)
        self.comboBox.setGeometry(QtCore.QRect(80, 380, 131, 31))
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.label = QtGui.QLabel(self.tab)
        self.label.setGeometry(QtCore.QRect(0, 380, 71, 21))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(self.tab)
        self.label_2.setGeometry(QtCore.QRect(0, 420, 91, 21))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.dimensionLabel = QtGui.QLabel(self.tab)
        self.dimensionLabel.setGeometry(QtCore.QRect(90, 420, 111, 21))
        self.dimensionLabel.setObjectName(_fromUtf8("dimensionLabel"))
        self.startButton = QtGui.QPushButton(self.tab)
        self.startButton.setGeometry(QtCore.QRect(280, 380, 96, 33))
        self.startButton.setObjectName(_fromUtf8("startButton"))
        self.label_3 = QtGui.QLabel(self.tab)
        self.label_3.setGeometry(QtCore.QRect(280, 420, 131, 21))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.label_4 = QtGui.QLabel(self.tab)
        self.label_4.setGeometry(QtCore.QRect(280, 440, 65, 21))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.generationLabel = QtGui.QLabel(self.tab)
        self.generationLabel.setGeometry(QtCore.QRect(420, 420, 65, 21))
        self.generationLabel.setObjectName(_fromUtf8("generationLabel"))
        self.clusterNumLabel = QtGui.QLabel(self.tab)
        self.clusterNumLabel.setGeometry(QtCore.QRect(420, 440, 65, 21))
        self.clusterNumLabel.setObjectName(_fromUtf8("clusterNumLabel"))
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Evo-clustering", None))
        self.label.setText(_translate("MainWindow", "Dataset:", None))
        self.label_2.setText(_translate("MainWindow", "Dimensions:", None))
        self.dimensionLabel.setText(_translate("MainWindow", "None loaded", None))
        self.startButton.setText(_translate("MainWindow", "Start", None))
        self.label_3.setText(_translate("MainWindow", "Current generation:", None))
        self.label_4.setText(_translate("MainWindow", "Clusters:", None))
        self.generationLabel.setText(_translate("MainWindow", "0", None))
        self.clusterNumLabel.setText(_translate("MainWindow", "0", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Core", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Stats", None))


