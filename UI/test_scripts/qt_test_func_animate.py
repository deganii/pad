import sys
import time

import numpy as np

from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5

from matplotlib.backends.backend_qt5agg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)

from matplotlib.figure import Figure
import matplotlib.animation as animation

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)

        static_canvas = FigureCanvas(Figure(figsize=(1, 1)))
        layout.addWidget(static_canvas)
        self.addToolBar(NavigationToolbar(static_canvas, self))

        dynamic_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(dynamic_canvas)
        self.addToolBar(QtCore.Qt.BottomToolBarArea,
                        NavigationToolbar(dynamic_canvas, self))
        self._static_ax = static_canvas.figure.subplots()
        t = np.linspace(0, 10, 501)
        s_t = np.linspace(0, 10, 101)
        self._static_ax.plot(t, np.tan(t), ".")

        self._dynamic_ax = dynamic_canvas.figure.subplots()
        sin_t = self._dynamic_ax.plot(s_t, np.sin(s_t + time.time()))
        anim = animation.FuncAnimation(dynamic_canvas.figure,
                        self._update_canvas, fargs=(sin_t),
                        blit=False, interval=60)

    def _update_canvas(self, frame, sin_t):
        # self._dynamic_ax.clear()
        # Shift the sinusoid as a function of time.
        # self._dynamic_ax.plot(t, np.sin(t + time.time()))
        # self._dynamic_ax.figure.canvas.draw()
        s_t = np.linspace(0, 10, 101)
        sin_t.set_data(s_t, np.sin(s_t + time.time()))
        return [sin_t]

if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    app = ApplicationWindow()
    app.show()
    qapp.exec_()