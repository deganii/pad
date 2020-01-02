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
                     't':deque([np.nan] * plotLength, plotLength)}
        self.isConnected = False
        self.isRunning = False
        self.thread = None
        self.data_lock = Lock()
        self.start_time_s = time.time()

        if self.port is None:
            print('Determining Port and Baud rate')
            self.port = self.getTeensySerialPort()

        print('Trying to connect to: ' + str(self.port) + ' at ' + str(serialBaud) + ' BAUD.')
        try:
            self.serialConnection = serial.Serial(self.port, serialBaud, timeout=4)
            self.isConnected = True
            print('Connected to ' + str(self.port) + ' at ' + str(serialBaud) + ' BAUD.')
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


    def getSerialData(self, frame, ax, i_x, i_y):
        # move raw serial data into the pandas dataframe
        with self.data_lock:
            for line in self.rawdata:
                values = [float(v) for v in line.split()]
                # TODO: get this from microcontroller
                experiment_time = time.time() - self.start_time_s
                self.data['t'].append(experiment_time)
                self.data['i_x'].append(values[0])
                self.data['i_y'].append(values[1])
                i_x.set_data(self.data['t'], self.data['i_x'])
                i_y.set_data(self.data['t'], self.data['i_y'])
                ax.relim()
                ax.autoscale_view(True, True, True)

                #dataframe.loc[len(dataframe)] = [experiment_time, values[0], values[1]]
            self.rawdata.clear()
        return [i_x, i_y]
        #ax = sns.lineplot(x="Time(s)", y="Iy Fluorescence (a.u.)", data=dataframe)


    def backgroundThread(self):  # retrieve data
        # self.serialConnection.reset_input_buffer()
        while self.isRunning:
            if self.serialConnection.in_waiting:
                with self.data_lock:
                    self.rawdata.append(self.serialConnection.readline())
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

        fig, ax = plt.subplots()
        t = [np.nan] * 100
        i_x, = ax.plot(t, [np.nan] * len(t), label='$I_x$')
        i_y, = ax.plot(t, [np.nan] * len(t), label='$I_y$')

        ax.set_title('Raw Intensities $(I_x, I_y)$')
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Fluorescence (a.u.)")
        ax.legend()

        #ax.set_ylim([0, 1024])
        def init():  # only required for blitting to give a clean slate.
            i_x.set_ydata([np.nan] * len(t))
            i_y.set_ydata([np.nan] * len(t))
            return [i_x,i_y]

        anim = animation.FuncAnimation(fig, s.getSerialData,
                                       init_func=init, blit=False,
                                       fargs=(ax, i_x, i_y),
                                       interval=pltInterval)

        # plt.legend(loc="upper left")
        plt.show()
        #ax.plot()

    except Exception as e:
        print(e)
    finally:

        if s is not None:
            s.close()


if __name__ == '__main__':
    main()