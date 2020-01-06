from threading import Thread, Lock
import serial
import time
from collections import deque
import serial.tools.list_ports
import numpy as np
import signal
import traceback
import signal

#
class SerialModule:
    def __init__(self, serialPort=None,
                 serialBaud=9600, dataLength=100):
        self.port = serialPort
        self.baud = serialBaud
        self.dataLength = dataLength
        self.rawdata = []
        self.data = {'i_x': deque([np.nan] * dataLength, dataLength),
                     'i_y': deque([np.nan] * dataLength, dataLength),
                     'pid_ctrl': deque([np.nan] * dataLength, dataLength),
                     'temp': deque([np.nan] * dataLength, dataLength),
                     't':deque([np.nan] * dataLength, dataLength)}
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
            # reset the arduino clock
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

    def updatePlotData(self, raw_ax, i_x, i_y, temp_ax, temp, pid_ctrl):
        # move raw serial data into the matplotlib drawing objects
        with self.data_lock:
            i_x.set_data(self.data['t'], self.data['i_x'])
            i_y.set_data(self.data['t'], self.data['i_y'])
            pid_ctrl.set_data(self.data['t'], self.data['pid_ctrl'])
            temp.set_data(self.data['t'], self.data['temp'])
            temp_ax.set_title('Temperature Monitor ({0:.2f}°C)'.format(self.data['temp'][-1]))
            # tell the UI that a full set of data is not yet received...
            return np.nan in self.data['t']

    def get_raw_intensity(self):
        with self.data_lock:
            return (self.data['i_x'][-1], self.data['i_y'][-1])

    def backgroundThread(self):  # retrieve data
        time.sleep(0.2)  # give some time for the arduino clock to reset
        self.serialConnection.reset_input_buffer()
        while self.isRunning:
            with self.data_lock:
                while self.serialConnection.in_waiting:
                    line = self.serialConnection.readline()
                    values = [float(v) for v in line.split()]
                    self.data['t'].append(values[0])
                    self.data['i_x'].append(values[1])
                    self.data['i_y'].append(values[2])
                    self.data['temp'].append(values[3])
                    self.data['pid_ctrl'].append(values[4])
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