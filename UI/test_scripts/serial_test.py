from time import sleep
import time
import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
import matplotlib.animation as animation


mcu_port = None

for port in serial.tools.list_ports.comports():
    print(port)
    if "Teensy" in port.description:
        mcu_port = port.device

if mcu_port is not None:
    ser = serial.Serial(mcu_port, 9600) # Establish the connection on a specific port
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)

    while ser.in_waiting:
         print(ser.readline()) # Read the newest output from the Arduino
         sleep(.05) # Delay for 50ms


    def animate(i):
        pullData = open("sampleText.txt","r").read()
        dataArray = pullData.split('\n')
        xar = []
        yar = []
        for eachLine in dataArray:
            if len(eachLine)>1:
                x,y = eachLine.split(',')
                xar.append(int(x))
                yar.append(int(y))
        ax1.clear()
        ax1.plot(xar,yar)
    ani = animation.FuncAnimation(fig, animate, interval=100)
    plt.show()



