from threading import Thread, Lock
import serial
import time
from collections import deque
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import struct
import copy
import serial.tools.list_ports
import seaborn as sns
import pandas as pd
import numpy as np
import signal
from matplotlib.widgets import Slider
import traceback
from matplotlib.colors import ListedColormap

# Adapted from https://www.thepoorengineer.com/en/arduino-python-plot/#multiple
class SerialUpdater:
    def __init__(self, serialPort=None,
                 serialBaud=9600, plotLength=100):
        self.port = serialPort
        self.baud = serialBaud
        self.plotMaxLength = plotLength
        self.rawdata = []
        self.data = {'i_x': deque([np.nan] * plotLength, plotLength),
                     'i_y': deque([np.nan] * plotLength, plotLength),
                     'pid_ctrl': deque([np.nan] * plotLength, plotLength),
                     'temp': deque([np.nan] * plotLength, plotLength),
                     't':deque([np.nan] * plotLength, plotLength)}
        self.isConnected = False
        self.isRunning = False
        self.thread = None
        self.data_lock = Lock()
        self.start_time_s = time.time()
        # reset the arduino clock



        if self.port is None:
            print('Determining Port and Baud rate')
            self.port = self.getTeensySerialPort()

        print('Trying to connect to: ' + str(self.port) + ' at ' + str(serialBaud) + ' BAUD.')
        try:
            self.serialConnection = serial.Serial(self.port, serialBaud, timeout=4)
            self.isConnected = True
            print('Connected to ' + str(self.port) + ' at ' + str(serialBaud) + ' BAUD.')
            self.serialConnection.write(b'r')

        except:
            print("Failed to connect with " + str(self.port) + ' at ' + str(serialBaud) + ' BAUD.')
            self.isConnected = False



    def getTeensySerialPort(self):
        for port in serial.tools.list_ports.comports():
            print(port)
            if "Teensy" in port.description:
                return port.device
        raise Exception("Could not find a suitable (Teensy 3.2) micro-controller!")

    def readSerialStart(self):
        if self.isConnected and self.thread == None:
            self.thread = Thread(target=self.backgroundThread)
            self.isRunning = True
            self.thread.start()

    def getSerialData(self, frame, raw_ax, i_x, i_y, temp_ax, temp, pid_ctrl):
        # move raw serial data into the pandas dataframe
        with self.data_lock:
            for line in self.rawdata:
                values = [float(v) for v in line.split()]
                # TODO: get this from microcontroller
                # experiment_time = time.time() - self.start_time_s
                self.data['t'].append(values[0])
                self.data['i_x'].append(values[1])
                self.data['i_y'].append(values[2])
                self.data['temp'].append(values[3])
                self.data['pid_ctrl'].append(values[4])
                i_x.set_data(self.data['t'], self.data['i_x'])
                i_y.set_data(self.data['t'], self.data['i_y'])
                pid_ctrl.set_data(self.data['t'], self.data['pid_ctrl'])
                temp.set_data(self.data['t'], self.data['temp'])
                temp_ax.set_title('Temperature Monitor ({0:.2f}°C)'.format(values[2]))
                raw_ax.relim()
                temp_ax.relim()
                if np.nan in self.data['t']:
                    raw_ax.autoscale_view(True,False,True)
                    # temp_ax.autoscale_view(True, False, True)
                else:
                    raw_ax.set_xlim(auto=True)
                    raw_ax.autoscale_view(True,True,True)
                    temp_ax.set_xlim(auto=True)
                    temp_ax.autoscale_view(True,True,False)
            self.rawdata.clear()
        return [i_x, i_y, temp, pid_ctrl]



    def backgroundThread(self):  # retrieve data
        time.sleep(0.1) # give some time for the clock to reset
        self.serialConnection.reset_input_buffer()
        while self.isRunning:
            if self.serialConnection.in_waiting:
                with self.data_lock:
                    self.rawdata.append(self.serialConnection.readline())
                    # print(self.rawdata)
            time.sleep(0.05)


    def close(self):
        self.isRunning = False
        if self.thread is not None:
            self.thread.join()
        self.serialConnection.close()
        print('Disconnected...')
        self.thread = None

def main():
    try:
        matplotlib.rcParams['toolbar'] = 'None'
        sns.set(style="darkgrid")
        maxPlotLength = 100  # number of points in x-axis of real time plot
        s = SerialUpdater()
        s.readSerialStart()

        def exit_gracefully(self, signum, frame):
            print("Graceful exit triggered")
            s.close()
            plt.close()
        signal.signal(signal.SIGINT, exit_gracefully)
        signal.signal(signal.SIGTERM, exit_gracefully)


        # Plot the responses for different events and regions


        # plotting starts below
        pltInterval = 50  # Period at which the plot animation updates [ms]

        # fig = plt.figure(figsize=(10, 8))
        # ax = plt.axes(xlim=(0, maxPlotLength), ylim=(0, 1024))
        # ax.set_title('Raw Intensities (Ix, Iy)')
        # ax.set_xlabel("Time (s)")
        # ax.set_ylabel("Fluorescence (a.u.)")

        # inputs
        # time = np.array([0.0, 0.1, 0.2, 0.3, 0.4])
        # ix = np.array([300, 302, 303, 302, 301])
        # iy = np.array([500, 502, 503, 502, 501])

        # convert to pandas dataframe
        #d = {'Time(s)':time, 'Ix Fluorescence (a.u.)': ix, 'Iy Fluorescence (a.u.)': iy}
        # dataframe = pd.DataFrame(columns=['Time(s)', 'Ix Fluorescence (a.u.)', 'Iy Fluorescence (a.u.)'])
        # ax = sns.lineplot(x="Time(s)", y="Ix Fluorescence (a.u.)", data=dataframe)
        # spos = Slider(ax, 'Pos', 0.1, 90.0)

        # fig, ax = plt.subplots(figsize=(14,8))
        fig, axs = plt.subplots(2, 2, figsize=(14,8))
        raw_ax = axs[0,0]
        t = [np.nan] * 100
        i_x, = raw_ax.plot(t, [np.nan] * len(t), label='$I_x$')
        i_y, = raw_ax.plot(t, [np.nan] * len(t), label='$I_y$')

        raw_ax.set_title('Raw Intensities $(I_x, I_y)$')
        raw_ax.set_xlabel("Time (s)")
        raw_ax.relim()
        raw_ax.autoscale_view(True, True, True)
        raw_ax.set_xlim(0, 15)
        raw_ax.set_ylabel("Fluorescence (a.u.)")
        raw_ax.legend()

        temp_ax = axs[0, 1]
        pid_ax = temp_ax.twinx()
        hls_cmp = ListedColormap(sns.hls_palette(8).as_hex())
        temp = temp_ax.plot(t, [np.nan] * len(t), label='Temp °C', color=hls_cmp(0))[0]
        pid_ctrl = pid_ax.plot(t, [np.nan] * len(t), label='PID Control', color=hls_cmp(1))[0]
        temp_ax.set_xlabel('Time(s)')
        temp_ax.set_ylabel('Temp (°C)')
        pid_ax.set_ylabel('PID Control')
        pid_ax.grid(False)
        temp_ax.set_title('Temperature Monitor (°C)')
        temp_ax.set_xlim(0, 15)
        temp_ax.set_ylim(10,85)
        pid_ax.set_ylim(-20,300)
        temp_ax.legend(loc='upper left')
        pid_ax.legend(loc='upper right')

        def init():  # only required for blitting to give a clean slate.
            i_x.set_ydata([np.nan] * len(t))
            i_y.set_ydata([np.nan] * len(t))
            return [i_x,i_y]

        anim = animation.FuncAnimation(fig, s.getSerialData,
                               init_func=init, blit=False,
                               fargs=(raw_ax, i_x, i_y,
                                      temp_ax, temp, pid_ctrl),
                               interval=pltInterval)

        # plt.legend(loc="upper left")
        plt.show()
        #ax.plot()

    except Exception as e:
        print(e)
        traceback.print_exc()
    finally:

        if s is not None:
            s.close()


if __name__ == '__main__':
    main()