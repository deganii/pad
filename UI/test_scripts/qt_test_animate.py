import sys
import time

import numpy as np

from matplotlib.backends.qt_compat import QtCore, QtWidgets, QtGui
from matplotlib.backends.backend_qt5agg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from PyQt5 import uic
from PyQt5.QtWidgets import QGridLayout

from matplotlib.figure import Figure


class PadMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(PadMainWindow, self).__init__()
        uic.loadUi('c:/dev/pad/ui/designer/mainwindow.ui', self)

        # self._main = QtWidgets.QWidget()
        # self.setCentralWidget(self._main)
        # layout = QtWidgets.QVBoxLayout(self._main)

        # get the gridlayout
        layout = self.findChild(QGridLayout, "gridGraphs")

        static_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(static_canvas)
        # self.addToolBar(NavigationToolbar(static_canvas, self))

        dynamic_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(dynamic_canvas)
        # self.addToolBar(QtCore.Qt.BottomToolBarArea,
        #                 NavigationToolbar(dynamic_canvas, self))

        self._static_ax = static_canvas.figure.subplots()
        t = np.linspace(0, 10, 501)
        self._static_ax.plot(t, np.tan(t), ".")

        self._dynamic_ax = dynamic_canvas.figure.subplots()
        self._timer = dynamic_canvas.new_timer(
            100, [(self._update_canvas, (), {})])
        self._timer.start()

    def _update_canvas(self):
        self._dynamic_ax.clear()
        t = np.linspace(0, 10, 101)
        # Shift the sinusoid as a function of time.
        self._dynamic_ax.plot(t, np.sin(t + time.time()))
        self._dynamic_ax.figure.canvas.draw()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = PadMainWindow()
    window.show()
    app.exec_()