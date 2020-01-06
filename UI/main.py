import sys
import time
import signal
import traceback

import numpy as np
import matplotlib
from matplotlib.backends.qt_compat import QtCore, QtWidgets, QtGui
from matplotlib.backends.backend_qt5agg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from PyQt5 import uic
from PyQt5.QtWidgets import QGridLayout, QPushButton, QLineEdit, QSpinBox
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from matplotlib.figure import Figure

from SerialModule import SerialModule
from matplotlib.colors import ListedColormap
import seaborn as sns

class PadMainWindow(QtWidgets.QMainWindow):
    def __init__(self, serialConnection):
        super(PadMainWindow, self).__init__()
        self.serialConnection = serialConnection
        uic.loadUi('c:/dev/pad/ui/designer/mainwindow.ui', self)

        # get the gridlayout for the plots
        layout = self.findChild(QGridLayout, "gridGraphs")

        raw_canvas = FigureCanvas(Figure(figsize=(5,3)))
        layout.addWidget(raw_canvas)

        raw_ax = raw_canvas.figure.subplots()
        t = [np.nan] * 100
        self.i_x, = raw_ax.plot(t, [np.nan] * len(t), label='$I_x$')
        self.i_y, = raw_ax.plot(t, [np.nan] * len(t), label='$I_y$')
        raw_ax.set_title('Raw Intensities $(I_x, I_y)$')
        raw_ax.set_xlabel("Time (s)")
        raw_ax.relim()
        raw_ax.autoscale_view(True, True, True)
        raw_ax.set_xlim(0, 15)
        raw_ax.set_ylabel("Fluorescence (a.u.)")
        raw_ax.legend()
        self._raw_ax = raw_ax

        temp_canvas = FigureCanvas(Figure(figsize=(5,3)))
        layout.addWidget(temp_canvas)
        temp_ax = temp_canvas.figure.subplots()
        pid_ax = temp_ax.twinx()
        hls_cmp = ListedColormap(sns.hls_palette(8).as_hex())
        self.temp = temp_ax.plot(t, [np.nan] * len(t), label='Temp °C', color=hls_cmp(0))[0]
        self.pid_ctrl = pid_ax.plot(t, [np.nan] * len(t), label='PID Control', color=hls_cmp(1))[0]
        temp_ax.set_xlabel('Time(s)')
        temp_ax.set_ylabel('Temp (°C)')
        pid_ax.set_ylabel('PID Control')
        pid_ax.grid(False)
        temp_ax.set_title('Temperature Monitor (°C)')
        temp_ax.set_xlim(0, 15)
        temp_ax.set_ylim(10,85)
        pid_ax.set_ylim(-20,350)
        temp_ax.legend(loc='upper left')
        pid_ax.legend(loc='upper right')
        self._temp_ax = temp_ax

        temp_canvas.figure.subplots_adjust(bottom=0.2)
        raw_canvas.figure.subplots_adjust(bottom=0.2)

        buttonAutoReference = self.findChild(QPushButton, "buttonAutoReference")
        buttonAutoReference.clicked.connect(self.on_auto_reference)
        self.textRefX = self.findChild(QSpinBox, "textRefX")
        self.textRefY = self.findChild(QSpinBox, "textRefY")

        self._timer = temp_canvas.new_timer(
            100, [(self._update_canvas, (), {})])
        self._timer.start()

    def _update_canvas(self):
        dataPartial = self.serialConnection.updatePlotData(
            self._raw_ax, self.i_x, self.i_y,
            self._temp_ax, self.temp, self.pid_ctrl)
        self._raw_ax.relim()
        self._temp_ax.relim()
        if dataPartial: # avoid autoscaling the X-axis if we don't have enough datapoints
            self._raw_ax.autoscale_view(True, False, True)
            self._temp_ax.autoscale_view(True, False, True)
        else:
            self._raw_ax.set_xlim(auto=True)
            self._raw_ax.autoscale_view(True, True, True)
            self._temp_ax.set_xlim(auto=True)
            self._temp_ax.autoscale_view(True, True, False)
        self._temp_ax.figure.canvas.draw()
        self._raw_ax.figure.canvas.draw()


    @pyqtSlot()
    def on_auto_reference(self):
        # get latest
        (x,y) = self.serialConnection.get_raw_intensity()
        self.textRefX.setValue(x)
        self.textRefY.setValue(y)

if __name__ == "__main__":
    s = None
    try:
        def exit_gracefully(self, signum, frame):
            print("Graceful exit triggered")
            if s is not None:
                s.close()
        signal.signal(signal.SIGINT, exit_gracefully)
        signal.signal(signal.SIGTERM, exit_gracefully)

        # matplotlib.rcParams['toolbar'] = 'None'
        sns.set(style="darkgrid", font_scale=0.85)
        # matplotlib.rcParams.update({'font.size': 12})

        s = SerialModule()
        s.readSerialStart()



        app = QtWidgets.QApplication(sys.argv)
        window = PadMainWindow(s)
        window.show()
        app.exec_()

    except Exception as e:
        print(e)
        traceback.print_exc()
    finally:
        if s is not None:
            s.close()



