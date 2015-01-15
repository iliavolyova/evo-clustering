import sys, os, random
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from __builtin__ import enumerate

import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from core import *

class Worker(QThread):
    updated = pyqtSignal(tuple)
    update_status_bar = pyqtSignal(int)
    core = None

    def run(self):
        for i in range(self.core.config.trajanje_svijeta):
            grupiranje, centri = self.core.cycle()
            if i % 3 is 0:
                self.updated.emit((grupiranje, centri))
            self.update_status_bar.emit(i)

class AppForm(QMainWindow):
    def __init__(self, parent=None):
        self.core = Core(Config(Wine()))
        self.colors = []

        QMainWindow.__init__(self, parent)
        self.setWindowTitle('Evolucijski clustering')

        self._thread = Worker(self)
        self._thread.core = self.core
        self._thread.updated.connect(self.on_draw)
        self._thread.update_status_bar.connect(self.update_status_bar)

        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()

        self.on_draw_initial(self.core.config.dataset.data)

    def getColor(self, klasa):
        if klasa > len(self.colors) - 1:
            color = (random.random(), random.random(), random.random())
            self.colors.append(color)
            return color
        else:
            return self.colors[klasa]

    def save_plot(self):
        file_choices = "PNG (*.png)|*.png"

        path = unicode(QFileDialog.getSaveFileName(self,
                        'Save file', '',
                        file_choices))
        if path:
            self.canvas.print_figure(path, dpi=self.dpi)
            self.statusBar().showMessage('Saved to %s' % path, 2000)

    def on_about(self):
        msg = """ A demo of using PyQt with matplotlib:

         * Use the matplotlib navigation bar
         * Add values to the text box and press Enter (or click "Draw")
         * Show or hide the grid
         * Drag the slider to modify the width of the bars
         * Save the plot to a file using the File menu
         * Click on a bar to receive an informative message
        """
        QMessageBox.about(self, "About the demo", msg.strip())

    def setup_axes(self):
        self.axes.clear()
        self.axes.grid(self.grid_cb.isChecked())
        self.axes.set_xlim(-50, 150)
        self.axes.set_ylim(-50, 150)


    def on_draw(self, data):

        # clear the axes and redraw the plot anew
        self.setup_axes()

        self.axes.grid(self.grid_cb.isChecked())

        for iklasa, klasa in enumerate(data[0]):
            self.axes.plot([t[0] * 100 for t in klasa],
                           [t[1] * 100 for t in klasa],
                           'o',
                           markersize=10 ,
                           color=(self.getColor(data[0].index(klasa))))
            self.axes.plot([data[1][iklasa][0] * 100 ],
                           [data[1][iklasa][1] * 100 ],
                           'x',
                           markersize=12 ,
                           color=(self.getColor(data[0].index(klasa))))

        self.canvas.draw()

    def on_draw_initial(self, data):
        # clear the axes and redraw the plot anew
        self.setup_axes()

        self.axes.plot([t[0] * 100 for t in data], [t[1] * 100 for t in data], 'o', markersize=12 , color=(random.random(), random.random(), random.random()))

        self.canvas.draw()

    def create_main_frame(self):
        self.main_frame = QWidget()

        # Create the mpl Figure and FigCanvas objects.
        # 5x4 inches, 100 dots-per-inch
        #
        self.dpi = 100
        self.fig = Figure((5.0, 4.0), dpi=self.dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)

        # Since we have only one plot, we can use add_axes
        # instead of add_subplot, but then the subplot
        # configuration tool in the navigation toolbar wouldn't
        # work.
        #
        self.axes = self.fig.add_subplot(111)

        # Bind the 'pick' event for clicking on one of the bars
        #
        # LLL self.canvas.mpl_connect('pick_event', self.on_pick)

        # Create the navigation toolbar, tied to the canvas
        #
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)

        # Other GUI controls
        #
        self.draw_button = QPushButton("&Start")
        self.connect(self.draw_button, SIGNAL('clicked()'), self._thread.start)

        self.grid_cb = QCheckBox("Show &Grid")
        self.grid_cb.setChecked(False)
        self.connect(self.grid_cb, SIGNAL('stateChanged(int)'), self.on_draw)

        #
        # Layout with box sizers
        #
        hbox = QHBoxLayout()

        for w in [  self.draw_button, self.grid_cb,]:
            hbox.addWidget(w)
            hbox.setAlignment(w, Qt.AlignVCenter)

        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        vbox.addLayout(hbox)

        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)

    def create_status_bar(self):
        self.status_text = QLabel("Generacija 0")
        self.statusBar().addWidget(self.status_text, 1)

    def update_status_bar(self, i):
        self.status_text.setText('Generacija ' + str(i))

    def create_menu(self):
        self.file_menu = self.menuBar().addMenu("&File")

        load_file_action = self.create_action("&Save plot",
            shortcut="Ctrl+S", slot=self.save_plot,
            tip="Save the plot")
        quit_action = self.create_action("&Quit", slot=self.close,
            shortcut="Ctrl+Q", tip="Close the application")

        self.add_actions(self.file_menu,
            (load_file_action, None, quit_action))

        self.help_menu = self.menuBar().addMenu("&Help")
        about_action = self.create_action("&About",
            shortcut='F1', slot=self.on_about,
            tip='About the demo')

        self.add_actions(self.help_menu, (about_action,))

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(  self, text, slot=None, shortcut=None,
                        icon=None, tip=None, checkable=False,
                        signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action


def main():
    app = QApplication(sys.argv)
    form = AppForm()
    form.show()
    app.exec_()

if __name__ == "__main__":
    main()