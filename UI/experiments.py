import csv
import traceback, os

# take discrete measurements, create a bar graph
from collections import deque
from threading import Lock
import seaborn as sns
import numpy as np

class DiscreteExperiment:
    def __init__(self, name, root, ref_x, ref_y, num_measurements=10,
                 samples_per_measurement=100):
        self.name = name
        self.root = root
        self.num_measurements = num_measurements
        self.samples_per_measurement = samples_per_measurement
        self.ref_x = ref_x
        self.ref_y = ref_y
        self.data_lock = Lock()
        self.current_measurement = None
        self.measurements_completed = -1
        try:
            self.init_data()
        except Exception as e:
            print(e)
            traceback.print_exc()
            print("Failed to start experiment")

    def init_data(self):
        self.data = []
        for i in range(self.num_measurements):
            self.data[i] = {'i_x': deque(self.samples_per_measurement),
                            'i_y': deque(self.samples_per_measurement),
                            'pid_ctrl': deque(self.samples_per_measurement),
                            'temp': deque(self.samples_per_measurement),
                            't': deque(self.samples_per_measurement),
                            'ref_x': deque(self.samples_per_measurement),
                            'ref_y': deque(self.samples_per_measurement),
                            'ref_pa_r0': deque(self.samples_per_measurement),
                            'raw_pa_r': deque(self.samples_per_measurement),
                            'pa_delta_r': deque(self.samples_per_measurement),
            }

    # called by UI timer thread when the UI wants an updated plot
    def draw_plot(self, ax):
        if self.measurements_completed > 0:
            with self.data_lock:
                msmt_avgs = np.empty(self.measurements_completed)
                msmt_stds = np.empty(self.measurements_completed)
                # compute statistics for each available measurements
                for i in range(self.measurements_completed):
                    msmt_avgs[i] = np.mean(self.data[i]['pa_delta_r'])
                    msmt_stds[i] = np.std(self.data[i]['pa_delta_r'])
                sns.barplot(x=list(range(self.measurements_completed)),
                            y=msmt_avgs, palette="Blues_d",
                            ax=ax, yerr=msmt_stds)
                ax.set_title(self.name)

    def start_measurement(self):
        with self.data_lock:
            self.current_measurement = self.measurements_completed+1
            filename = self.root + 'measurement_{0:03d}.csv'.format(self.current_measurement)
            if os.path.exists(filename):
                append_write = 'a'  # append if already exists
            else:
                append_write = 'w'  # make a new file if not
            fields = ['t', 'i_x', 'i_y', 'temp', 'pid_ctrl',
                      'ref_x', 'ref_y', 'ref_pa_r0', 'raw_pa_r', 'pa_delta_r']
            self.logfile = open(filename, append_write, newline='')
            self.writer = csv.writer(self.logfile)
            self.writer.writerow(fields)

    def stop_measurement(self):
        with self.data_lock:
            self.measurements_completed = self.current_measurement
            # close the csv
            self.logfile.close()
            self.writer = self.logfile = None
            self.current_measurement = None

    # called by serial connection (non-ui thread) when new raw data is available
    def on_new_data(self, t, i_x, i_y, temp, pid_ctrl):
        if not self.current_measurement:
            # not measuring anything at the moment, throw away the data
            return

        with self.data_lock:
            ref_x, ref_y = self.ref_x, self.ref_y
            msmt = self.data[self.current_measurement]
            msmt['t'].append(t)
            msmt['i_x'].append(i_x)
            msmt['i_y'].append(i_y)
            msmt['temp'].append(temp)
            msmt['pid_ctrl'].append(pid_ctrl)

            # calculate polarization anisotropy
            r = (i_x - i_y) / (i_x + 2 * i_y)
            r0 = (ref_x - ref_y) /(ref_x + 2* ref_y)
            delta_r = r - r0

            # update the measurement csv
            self.writer.writerow([t, i_x, i_y, temp, pid_ctrl,
                      ref_x, ref_y, r0, r, delta_r])

            # stop if we have enough samples for this measurement
            if len(msmt['t']) == self.samples_per_measurement:
                self.stop_measurement()