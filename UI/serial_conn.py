from threading import Thread, Lock, RLock
import serial
import time
from collections import deque
import serial.tools.list_ports
import numpy as np
import signal
import traceback
import signal
import csv
import os
#
class SerialModule:
    def __init__(self, serialPort=None,
                 serialBaud=9600, dataLength=100):
        self.port = serialPort
        self.baud = serialBaud
        self.dataLength = dataLength
        self.rawdata = []
        self.init_data()
        self.isConnected = False
        self.isRunning = False
        self.isLogging = False
        self.thread = None
        self.data_lock = RLock()
        self.start_time_s = time.time()
        self.callback = None

        if self.port is None:
            print('Determining Port and Baud rate')
            self.port = self.getTeensySerialPort()

        print('Trying to connect to: ' + str(self.port) + ' at ' + str(serialBaud) + ' BAUD.')
        try:
            self.serialConnection = serial.Serial(self.port, serialBaud, timeout=4)
            self.isConnected = True
            print('Connected to ' + str(self.port) + ' at ' + str(serialBaud) + ' BAUD.')
            # reset the arduino clock
            self.serialConnection.write(b'r')
            self.set_heating(False)
            self.set_led(False)
        except Exception as e:
            print(e)
            traceback.print_exc()
            print("Failed to connect with " + str(self.port) + ' at ' + str(serialBaud) + ' BAUD.')
            self.isConnected = False

    def getTeensySerialPort(self):
        for port in serial.tools.list_ports.comports():
            print(port)
            if "Teensy" in port.description:
                return port.device
        raise Exception("Could not find a suitable (Teensy 3.2) micro-controller!")

    def init_data(self):
        self.data = {'i_x': deque([np.nan] * self.dataLength, self.dataLength),
             'i_y': deque([np.nan] * self.dataLength, self.dataLength),
             'pid_ctrl': deque([np.nan] * self.dataLength, self.dataLength),
             'temp': deque([np.nan] * self.dataLength, self.dataLength),
             't': deque([np.nan] * self.dataLength, self.dataLength)}

    def reset_mcu_clock(self):
        # reset the arduino clock
        self.serialConnection.write(b'r')
        # give it some time to reset
        time.sleep(0.2)
        with self.data_lock:
            self.init_data()

    def set_heating(self, isHeating):
        self.serialConnection.write(b'H' if isHeating else b'h')
        self.isHeating = isHeating
        time.sleep(0.2)

    def set_led(self, isIlluminating):
        self.serialConnection.write(b'L' if isIlluminating else b'l')
        self.isIlluminating = isIlluminating
        time.sleep(0.2)

    def start_logging(self, filename, callback):
        with self.data_lock:
            if os.path.exists(filename):
                append_write = 'a'  # append if already exists
            else:
                append_write = 'w'  # make a new file if not
            fields = ['t', 'i_x', 'i_y', 'temp',  'pid_ctrl']
            self.logfile = open(filename, append_write, newline='')
            self.writer = csv.writer(self.logfile)
            self.writer.writerow(fields)
            self.callback = callback
            self.isLogging = True

    def stop_logging(self):
        with self.data_lock:
            if self.logfile is not None:
                self.logfile.close()
            self.writer = self.logfile = None
            self.callback = None
            self.isLogging = False

    def readSerialStart(self):
        if self.isConnected and self.thread == None:
            self.thread = Thread(target=self.backgroundThread)
            self.isRunning = True
            self.thread.start()

    def updatePlotData(self, raw_ax, i_x, i_y, temp_ax, temp, pid_ctrl):
        # move raw serial data into the matplotlib drawing objects
        # print('Starting updatePlotData')
        with self.data_lock:
            # print('Processing updatePlotData')
            i_x.set_data(self.data['t'], self.data['i_x'])
            i_y.set_data(self.data['t'], self.data['i_y'])
            pid_ctrl.set_data(self.data['t'], self.data['pid_ctrl'])
            temp.set_data(self.data['t'], self.data['temp'])
            temp_ax.set_title('Temperature Monitor ({0:.2f}°C)'.format(self.data['temp'][-1]))
            # tell the UI that a full set of data is not yet received...
            # print('Completed updatePlotData\n')
            return np.nan in self.data['t']

    def get_raw_intensity(self):
        with self.data_lock:
            return (self.data['i_x'][-1], self.data['i_y'][-1])

    def backgroundThread(self):  # retrieve data
        time.sleep(0.2)  # give some time for the arduino clock to reset
        self.serialConnection.reset_input_buffer()
        while self.isRunning:
            with self.data_lock:
                # print('Starting backgroundThread')
                while self.serialConnection.in_waiting:
                    # print('Processing backgroundThread')
                    line = self.serialConnection.readline()
                    values = [float(v) for v in line.split()]
                    t, i_x, i_y, temp, pid_ctrl = values
                    self.data['t'].append(t)
                    self.data['i_x'].append(i_x)
                    self.data['i_y'].append(i_y)
                    self.data['temp'].append(temp)
                    self.data['pid_ctrl'].append(pid_ctrl)
                    if self.isLogging:
                        self.writer.writerow(values)
                    if self.callback is not None:
                        self.callback(t, i_x, i_y, temp, pid_ctrl)
                # print('Completed backgroundThread\n')
            time.sleep(0.1)

    def close(self):
        self.isRunning = False
        if self.thread is not None:
            self.thread.join()
        self.serialConnection.close()
        print('Disconnected...')
        self.thread = None

def main():
    try:
        s = None
        def exit_gracefully(self, signum, frame):
            print("Graceful exit triggered")
            if s is not None:
                s.close()
        signal.signal(signal.SIGINT, exit_gracefully)
        signal.signal(signal.SIGTERM, exit_gracefully)

        s = SerialModule()
        s.readSerialStart()

    except Exception as e:
        print(e)
        traceback.print_exc()
    finally:
        if s is not None:
            s.close()

if __name__ == '__main__':
    main()