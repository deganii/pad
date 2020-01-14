import csv
import traceback, os

# take discrete measurements, create a bar graph
from collections import deque
from threading import Lock, RLock
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
        self.exp_data = []
        self.data_lock = RLock()
        self.current_measurement = None
        self.measurements_completed = 0
        self.logfile = None
        try:
            self.init_data()
            #print('Completed init_data')
        except Exception as e:
            print(e)
            traceback.print_exc()
            print("Failed to start experiment")

    def init_data(self):
        with self.data_lock:
            for i in range(self.num_measurements):
                self.exp_data.append({'i_x': deque(maxlen=self.samples_per_measurement),
                    'i_y': deque(maxlen=self.samples_per_measurement),
                    'pid_ctrl': deque(maxlen=self.samples_per_measurement),
                    'temp': deque(maxlen=self.samples_per_measurement),
                    't': deque(maxlen=self.samples_per_measurement),
                    'ref_x': deque(maxlen=self.samples_per_measurement),
                    'ref_y': deque(maxlen=self.samples_per_measurement),
                    'ref_pa_r0': deque(maxlen=self.samples_per_measurement),
                    'raw_pa_r': deque(maxlen=self.samples_per_measurement),
                    'pa_delta_r': deque(maxlen=self.samples_per_measurement)})

    # called by UI timer thread when the UI wants an updated plot
    def draw_plot(self, ax):
        if self.measurements_completed >= 0:
            # print('Started Exp draw_plot')
            with self.data_lock:
                # print('Processing Exp draw_plot')
                ax.clear()
                msmt_avgs = np.empty(self.measurements_completed)
                msmt_stds = np.empty(self.measurements_completed)
                # compute statistics for each available measurements
                for i in range(self.measurements_completed):
                    msmt_avgs[i] = np.mean(self.exp_data[i]['pa_delta_r'])
                    msmt_stds[i] = np.std(self.exp_data[i]['pa_delta_r'])
                sns.barplot(x=list(range(1,self.measurements_completed+1)),
                            y=msmt_avgs, palette="Blues_d",
                            ax=ax, yerr=msmt_stds)
                ax.set_title(self.name + ' (Untitled)' if self.name == 'Experiment' else self.name)
                # ax.set_title('Anisotropy (\Delta r$ = {1})')
                ax.set_xlabel("Measurement ID (n)")
                ax.set_ylabel("$\Delta r$")
                ax.set_xlim(-1,self.num_measurements)
            # print('Completed Exp draw_plot\n')

    def start_measurement(self):
        with self.data_lock:
            # print('Processing start_measurement\n')
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
        # print('Processing stop_measurement\n')
        with self.data_lock:
            # print('Processing lock:stop_measurement\n')
            if self.current_measurement is not None:
                self.measurements_completed = self.current_measurement
            # close the csv
            if self.logfile is not None:
                self.logfile.close()
            self.writer = self.logfile = None
            self.current_measurement = None
        # print('Completed stop_measurement\n')

    def waiting_new_sample(self):
        return self.current_measurement is None

    def is_complete(self):
        return self.measurements_completed == self.num_measurements

    # called by serial connection (non-ui thread) when new raw data is available
    def on_new_data(self, t, i_x, i_y, temp, pid_ctrl):
        if not self.current_measurement:
            # not measuring anything at the moment, throw away the data
            return

        with self.data_lock:
            # print('Processing on_new_data\n')
            ref_x, ref_y = self.ref_x, self.ref_y

            # calculate polarization anisotropy
            r = (i_x - i_y) / (i_x + 2 * i_y)
            if ref_x + 2* ref_y == 0:
                r0 = 0
            else:
                r0 = (ref_x - ref_y) /(ref_x + 2* ref_y)
            delta_r = r - r0

            msmt = self.exp_data[self.current_measurement-1]
            msmt['t'].append(t)
            msmt['i_x'].append(i_x)
            msmt['i_y'].append(i_y)
            msmt['temp'].append(temp)
            msmt['pid_ctrl'].append(pid_ctrl)
            msmt['ref_x'].append(ref_x)
            msmt['ref_y'].append(ref_y)
            msmt['ref_pa_r0'].append(r0)
            msmt['raw_pa_r'].append(r)
            msmt['pa_delta_r'].append(delta_r)

            # update the measurement csv
            self.writer.writerow([t, i_x, i_y, temp, pid_ctrl,
                      ref_x, ref_y, r0, r, delta_r])

            # stop if we have enough samples for this measurement
            if len(msmt['t']) == self.samples_per_measurement:
                # print('Calling stop_measurement\n')
                self.stop_measurement()