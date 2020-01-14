import sys,os
import time
import signal
import traceback
import logging

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from matplotlib.backends.qt_compat import QtCore, QtWidgets, QtGui
from matplotlib.backends.backend_qt5agg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from PyQt5 import uic
from PyQt5.QtWidgets import QGridLayout, QPushButton, QLineEdit, QSpinBox, QMessageBox, QAction
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from matplotlib.figure import Figure


from matplotlib.colors import ListedColormap
import seaborn as sns

# http://www.futurile.net/2016/03/14/partial-colouring-text-in-matplotlib-with-latex/
# matplotlib.rc('text',usetex=True)
# matplotlib.rc('text.latex', preamble=r'\usepackage{color}')
from experiments import DiscreteExperiment
from serial_conn import SerialModule

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception


class PadMainWindow(QtWidgets.QMainWindow):
    def __init__(self, serialConnection):
        super(PadMainWindow, self).__init__()
        self.experiment_running = False
        self.prompting = False
        self.serialConnection = serialConnection
        uic.loadUi('c:/dev/pad/ui/designer/mainwindow.ui', self)

        # get the gridlayout for the plots
        layout = self.findChild(QGridLayout, "gridGraphs")

        raw_canvas = FigureCanvas(Figure(figsize=(5,3)))
        layout.addWidget(raw_canvas, 0, 0)

        raw_ax = raw_canvas.figure.subplots()
        t = [np.nan] * 100
        self.i_x, = raw_ax.plot(t, [np.nan] * len(t), label='$I_x = I_{\parallel }$')
        self.i_y, = raw_ax.plot(t, [np.nan] * len(t), label='$I_y = I_{\perp }$')
        raw_ax.set_title('Raw Intensities $(I_x, I_y) = (I_{\parallel }, I_{\perp })$')
        raw_ax.set_xlabel("Time (s)")
        raw_ax.relim()
        raw_ax.autoscale_view(True, True, True)
        raw_ax.set_xlim(0, 15)
        raw_ax.set_ylabel("Fluorescence (a.u.)")
        raw_ax.legend()
        self._raw_ax = raw_ax

        temp_canvas = FigureCanvas(Figure(figsize=(5,3)))
        layout.addWidget(temp_canvas, 0, 2)
        temp_ax = temp_canvas.figure.subplots()
        pid_ax = temp_ax.twinx()
        self.hls_cmp = ListedColormap(sns.hls_palette(8).as_hex())
        self.default_cmp = plt.get_cmap("tab10")
        self.temp = temp_ax.plot(t, [np.nan] * len(t), label='Temp °C', color=self.hls_cmp(0))[0]
        self.pid_ctrl = pid_ax.plot(t, [np.nan] * len(t), label='PID Control', color=self.hls_cmp(1))[0]
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

        pa_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(pa_canvas, 1, 0)

        pa_ax = pa_canvas.figure.subplots()
        self.pa_r0, = pa_ax.plot(t, [np.nan] * len(t), label='$r_0$', linestyle='--')
        self.pa_r, = pa_ax.plot(t, [np.nan] * len(t), label='$r$')
        self.pa_delta_r, = pa_ax.plot(t, [np.nan] * len(t), label='$\Delta r$')
        pa_ax.set_title('Anisotropy (\Delta r$ = {1})')
        pa_ax.set_xlabel("Time (s)")
        pa_ax.relim()
        pa_ax.autoscale_view(True, True, True)
        pa_ax.set_xlim(0, 15)
        pa_ax.set_ylabel("$r, r_o, \Delta r$")
        pa_ax.legend()
        self._pa_ax = pa_ax

        buttonAutoReference = self.findChild(QPushButton, "buttonAutoReference")
        buttonAutoReference.clicked.connect(self.on_auto_reference)

        actionHeatingOn = self.findChild(QAction, "actionHeatingOn")
        actionHeatingOn.triggered.connect(self.on_heating_on)
        actionHeatingOff = self.findChild(QAction, "actionHeatingOff")
        actionHeatingOff.triggered.connect(self.on_heating_off)
        actionLEDOn = self.findChild(QAction, "actionLEDOn")
        actionLEDOn.triggered.connect(self.on_led_on)
        actionLEDOff = self.findChild(QAction, "actionLEDOff")
        actionLEDOff.triggered.connect(self.on_led_off)

        self.buttonStartDiscrete = self.findChild(QPushButton, "buttonStartDiscrete")
        self.buttonStartDiscrete.clicked.connect(self.on_start_discrete)

        self.textRefX = self.findChild(QSpinBox, "textRefX")
        self.textRefY = self.findChild(QSpinBox, "textRefY")

        self.textExpName = self.findChild(QLineEdit, "textExpName")

        noise_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(noise_canvas, 0, 1)

        noise_ax = noise_canvas.figure.subplots()
        # noise_ax2 = noise_ax.twinx()
        self.x_noise = sns.distplot([], vertical=True, ax=noise_ax, color=self.hls_cmp(0), bins=50, axlabel=False)
        self.y_noise = sns.distplot([], vertical=True, ax=noise_ax, color=self.hls_cmp(1), bins=50, axlabel=False)
        self._noise_ax = noise_ax
        noise_ax.set_title('Noise $(\mu, \sigma)$')

        pa_noise_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(pa_noise_canvas, 1, 1)

        pa_noise_ax = pa_noise_canvas.figure.subplots()
        self.pa_noise = sns.distplot([], vertical=True, ax=pa_noise_ax, color=self.hls_cmp(2), bins=50, axlabel=False)
        self._pa_noise_ax = pa_noise_ax
        pa_noise_ax.set_title('Noise $(\sigma_{\Delta r})$')


        pa_ax.set_ylabel("$r, r_o, \Delta r$")

        exp_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(exp_canvas, 1, 2)
        exp_ax = exp_canvas.figure.subplots()
        placehldr_exp = np.asarray([15,7,3.2,1.1,0.4,0.1])
        placehldr_err = np.asarray([3.4, 1.5, 0.5,0.5,0.2,0.1])
        sns.barplot(x=list(range(placehldr_exp.shape[0])),
                         y=placehldr_exp, color='lightsteelblue',
                         ax=exp_ax, yerr=placehldr_err, capsize=0.2)
        exp_ax.set_title('PA Experiment Placeholder')
        exp_ax.set_xlabel("Measurement ID (n)")
        exp_ax.set_ylabel("$\Delta r$")
        bbox_props = dict(boxstyle="round", fc="w", ec="0.5", alpha=0.6)
        # with matplotlib.rc_context({"lines.linewidth": 0.5}):
        exp_ax.text(2.5, 8, "Placeholder", ha="center", va="center", size=20,
                    bbox=bbox_props, color='steelblue')
        self._exp_ax = exp_ax

        offsets = {'bottom':0.2, 'left':0.17, 'right':0.87}
        offsets_t = {'bottom': 0.2, 'left': 0.17, 'right': 1.0}
        temp_canvas.figure.subplots_adjust(**offsets)
        raw_canvas.figure.subplots_adjust(**offsets_t)
        pa_canvas.figure.subplots_adjust(**offsets_t)
        exp_canvas.figure.subplots_adjust(**offsets_t)
        noise_canvas.figure.subplots_adjust(bottom=0.2, left=0)
        pa_noise_canvas.figure.subplots_adjust(bottom=0.2, left=0)

        layout.setColumnStretch(0, 3)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 3)

        self._timer = temp_canvas.new_timer(
            100, [(self._update_canvas, (), {})])
        self._timer.start()

    def _redraw(self, ax, partial, scale_y=True):
        ax.relim()
        if partial:  # avoid autoscaling the X-axis if we don't have enough datapoints
            ax.autoscale_view(True, False, True)
        else:
            ax.set_xlim(auto=True)
            ax.autoscale_view(True, True, scale_y)
        ax.figure.canvas.draw()


    def _update_canvas(self):
        try:
            dataPartial = self.serialConnection.updatePlotData(
                self._raw_ax, self.i_x, self.i_y,
                self._temp_ax, self.temp, self.pid_ctrl)

            t = self.i_x.get_xdata()
            raw_ix = np.asarray(self.i_x.get_ydata())
            raw_iy = np.asarray(self.i_y.get_ydata())
            raw_pa = np.asarray(self.pa_delta_r.get_ydata())

            r = (raw_ix - raw_iy) / (raw_ix + 2 * raw_iy)
            if self.textRefX.value() != 0 and self.textRefY.value() != 0:
                ref_x,ref_y = float(self.textRefX.value()), float(self.textRefY.value())
                r0 = (ref_x - ref_y) /(ref_x + 2* ref_y)
            else:
                r0 = 0
            delta_r = r - r0

            self.pa_r0.set_data(t, [r0]*len(t))
            self.pa_r.set_data(t, r)
            self.pa_delta_r.set_data(t, delta_r)
            self._pa_ax.set_title('Anisotropy ($\Delta r = {0:0.4f}$)'.format(delta_r[-1]))

            # self.x_noise.set_data(raw_ix[~np.isnan(raw_ix)])
            # self.y_noise.set_data(raw_iy[~np.isnan(raw_iy)])
            # print(raw_ix[~np.isnan(raw_ix)])

            self.x_noise.clear()
            self.y_noise.clear()
            self.pa_noise.clear()

            # sns.distplot(raw_ix[~np.isnan(raw_ix)], vertical=True, ax=self.x_noise, color=self.hls_cmp(0), bins=50)
            # sns.distplot(raw_iy[~np.isnan(raw_iy)], vertical=True, ax=self.y_noise, color=self.hls_cmp(1), bins=50)

            dist_x = raw_ix[~np.isnan(raw_ix)]
            dist_y = raw_iy[~np.isnan(raw_iy)]
            dist_pa =raw_pa[~np.isnan(raw_pa)]

            # shift the x noise distribution above the y
            mean_x = np.mean(dist_x)
            mean_y = np.mean(dist_y)
            mean_pa = np.mean(dist_pa)
            dist_x = dist_x - mean_x
            dist_y = dist_y - mean_y + 5*np.std(dist_x)
            dist_pa = dist_pa - mean_pa

            if dist_x.shape[0] > 0 and not np.all(dist_x[0] == dist_x): # don't plot if there is no deviance
                sns.kdeplot(dist_x, vertical=True, ax=self.x_noise,
                    color=self.default_cmp(0), shade = True)
            if dist_y.shape[0] > 0 and not np.all(dist_y[0] == dist_y):
                sns.kdeplot(dist_y, vertical=True, ax=self.x_noise,
                    color=self.default_cmp(1), shade = True)
            if dist_pa.shape[0] > 0 and not np.all(dist_pa[0] == dist_pa):
                sns.kdeplot(dist_pa, vertical=True, ax=self.pa_noise,
                    color=self.default_cmp(2), shade = True)
            self.x_noise.set_title(r'Noise $(\sigma_x, \sigma_y)$')
            self.x_noise.set_yticks([])
            self.x_noise.set_yticklabels([])
            self.x_noise.set_xticks([])
            self.x_noise.set_xticklabels([])
            self.x_noise.set_xlabel("$({0:.2f}, {1:.2f})$".format(np.std(dist_x), np.std(dist_y)))

            self.pa_noise.set_title(r'Noise $(\sigma_{\Delta r})$')
            self.pa_noise.set_yticks([])
            self.pa_noise.set_yticklabels([])
            self.pa_noise.set_xticks([])
            self.pa_noise.set_xticklabels([])

            # Don't show ticks above 100%
            # pid_yticks = ax.yaxis.get_major_ticks()
            # pid_yticks[-1].set_visible(False)

            # TODO: add logic to only redraw when data changes...
            if self.experiment_running:
                self.experiment.draw_plot(self._exp_ax)
                if self.experiment.is_complete():
                    self.stop_experiment()
                    # self.experiment_running = False
                    # self.experiment = None
                    # QMessageBox.information(self, 'Successful','Experiment Completed')
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setText('Experiment Completed')
                    msg.setWindowTitle('Successful')
                    msg.setStandardButtons(QMessageBox.Ok)
                    self.completed_msg = msg
                    msg.buttonClicked.connect(self.on_finished_discrete)
                    msg.show()
                elif self.experiment.waiting_new_sample() and not self.prompting:
                    self.prompt_next_measurement()
            self._redraw(self._pa_ax, partial=dataPartial)
            self._redraw(self._temp_ax, partial=dataPartial, scale_y=False)
            self._redraw(self._raw_ax, partial=dataPartial)
            self._redraw(self._noise_ax, partial=dataPartial)
            self._redraw(self._pa_noise_ax, partial=dataPartial)
            self._redraw(self._exp_ax, partial=True)

            # TODO: initiate next measurement here
            

        except Exception as e:
            print(e)
            traceback.print_exc()

    @pyqtSlot()
    def on_auto_reference(self):
        # get latest
        (x,y) = self.serialConnection.get_raw_intensity()
        self.textRefX.setValue(x)
        self.textRefY.setValue(y)

    @pyqtSlot()
    def on_led_on(self):
        self.serialConnection.set_led(isIlluminating=True)

    @pyqtSlot()
    def on_led_off(self):
        self.serialConnection.set_led(isIlluminating=False)

    @pyqtSlot()
    def on_heating_on(self):
        self.serialConnection.set_heating(isHeating=True)

    @pyqtSlot()
    def on_heating_off(self):
        self.serialConnection.set_heating(isHeating=False)



    @pyqtSlot()
    def on_start_discrete(self):
        if self.experiment_running:
            self.stop_experiment()
        else:
            # TODO: get latest experimental parameters
            self.serialConnection.reset_mcu_clock()
            self.serialConnection.set_led(isIlluminating=False)
            timestr = time.strftime("%Y%m%d-%H%M%S")
            exp_name = self.textExpName.text()
            if not exp_name:
                exp_name = 'Experiment'
            exp_dir = '../Experiments/{0}_{1}/'.format(exp_name, timestr)
            os.makedirs(exp_dir, exist_ok=True)
            #self.experiment = DiscreteExperiment(exp_name, exp_dir)
            self.experiment = DiscreteExperiment(exp_name, exp_dir,
                self.textRefX.value(), self.textRefY.value())
            self.serialConnection.start_logging(
                exp_dir + 'raw.csv', self.experiment.on_new_data)
            self.experiment_running = True
            self.buttonStartDiscrete.setText(
                self.buttonStartDiscrete.text().replace('Start', 'Stop'))
            self.prompt_next_measurement()



    @pyqtSlot()
    def on_finished_discrete(self):
        pass
        # self.stop_experiment()

    def stop_experiment(self):
        self.serialConnection.stop_logging()
        self.experiment.stop_measurement()
        self.buttonStartDiscrete.setText(
            self.buttonStartDiscrete.text().replace('Stop', 'Start'))
        self.experiment_running = False
        self.experiment = None

    def prompt_next_measurement(self):
        self.prompting = True
        # turn off the led
        self.serialConnection.set_led(isIlluminating=False)

        msgBox = QMessageBox()
        msgBox.setWindowTitle("Experiment")
        msgBox.setText('Please load the next sample for measurement #{0}'.format(
            self.experiment.measurements_completed + 1))
        self.continue_button = QPushButton('Continue...')
        msgBox.addButton(self.continue_button, QMessageBox.YesRole)
        msgBox.addButton(QPushButton('End Experiment'), QMessageBox.RejectRole)
        self.prompt_box = msgBox
        msgBox.buttonClicked.connect(self.prompt_handler)
        msgBox.show()

    @pyqtSlot()
    def prompt_handler(self):
        if self.prompt_box.clickedButton() == self.continue_button:
            self.serialConnection.set_led(isIlluminating=True)
            self.experiment.start_measurement()
        else:
            self.serialConnection.set_led(isIlluminating=False)
            self.stop_experiment()
        self.prompting = False


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
        sns.set(style="darkgrid", font_scale=0.87)
        # matplotlib.rcParams.update({'font.size': 12})

        s = SerialModule()
        s.readSerialStart()

        if s.isConnected:
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



