# Copyright (c) 2022, Tantor GmbH
# All rights reserved.
# published under MIT license


"""
you may connect the triggeroutput to analog input 2 of the box
and connect input 1 to a suitable signal
if configured as schmitt trigger, you can see the trigger output
and the signal on input 1
"""
import platform
import time
from sys import exit  # to keep pyinstaller happy

import matplotlib.pyplot as plt
import numpy
from multidaq import multiDaq


# -----------------------------------------------------------------------------------
def plotresults(input, title, ylabel):
    plt.clf()
    iii = 1
    cols = input.shape[1]
    for x in range(cols):
        plt.plot(input[:, x], label="ch" + str(iii))
        iii += 1
    plt.grid()
    plt.title(title)
    plt.legend(loc="upper left")
    plt.xlabel("sampleNumber")
    plt.ylabel(ylabel)
    plt.show(block=True)
    plt.pause(0.001)  # this pause is essential for non blocking mode, reason unknown


if __name__ == "__main__":
    # You may open up to 4 devices parallel with different IDs ( from 0 ... 3 )
    # dev = multiDaq() # default uses channel 0
    # dev = multiDaq(2) # uses channel 2
    # dev = multiDaq(2,"path/to/DLL") # uses channel 2 and path to dll
    # dev = multiDaq(1,"c:/bin")
    # dev = multiDaq(1,"c:\\bin")

    my_os = platform.system()

    # on windows you may specify the DLL, example: msgDev = multiDaq("c:/bin")
    dev = multiDaq()

    print("Version of DLL:", dev.getVersionInfo())

    A = dev.listDevices()
    if len(A) == 0:
        print("No Device found: exit now")
        exit(1)
    if not dev.open(A[0]):
        print("open() failed: Device Busy? exit now")
        exit(1)
    print(A)

    # ------------------ configure the device ------------------------
    dev.clearConfig()
    if not dev.setSampleRate(1000):
        print("fatal: Could not set samplerate")
        exit(1)
    # mitigate error handling, it will cause error in configure()
    if A[0].startswith("bio"):  # has 32 bit ADC
        dev.addAdc32(1)
        dev.addAdc32()
    else:
        dev.addAdc16(6)
        dev.addAdc16(6)
    # dev.addImu6(3, 250)
    # it is an good idea to set the outputlevel to a defined state
    dev.configureTrigger("pulse", 20)
    time.sleep(0.3)
    # dev.setTrigger("0")
    """
    if not dev.configureTrigger("schmitt", "0", "10000", "5000"):
        print("fatal: could not configure the trigger")
        exit(1)
    """
    # minimal errorhandling should be done before startSampling !
    if not dev.configure():  # last command before startSampling()
        print("Fatal: Config failed")
        exit(1)
    for i in range(10):
        print(dev.LL.sendCmd(0, "conf:dev:stat?"))
        time.sleep(0.01)
    # for best synchronisation between startsampling and setTrigger()
    dev.disableTx()
    dev.startSampling()
    dev.setTrigger(True)
    dev.enableTx()

    # ------------------------------------ aquisition loop ------------------------
    gotFirstData = False
    toggle = False
    for i in range(10):
        time.sleep(0.2)
        dev.setTrigger(True)  # use toggle for level
        toggle = not toggle
        x = dev.getStreamingData()
        print("got data", x.shape, "toggle =", toggle)
        if x.size > 0:
            if not gotFirstData:
                gotFirstData = True
                xAll = x
            else:
                xAll = numpy.vstack((xAll, x))
    dev.stopSampling()
    dev.close()
    # cfgInfo ist a tupel with content (nAdc32,nAdc16,nImu)
    # or (nAdc32,nAdc16,nImu,nAux) {if Aux is employed}
    if dev.cfgInfo[0] > 0:
        print("may happen in future, till now it is handled as an Error")
        # exit(1)
    # plotresults(xAll[:, 1:4], "analogdata", "[V]")
    plotresults(xAll, "analogdata", "[V]")

    startidx = 0  # dev.cfgInfo[0]  # here Adc16 data starts
    if dev.cfgInfo[1] > 0:  # plot all analog channels in one plot
        plotresults(xAll, "analogdata", "[V]")

    startidx = dev.cfgInfo[0] + dev.cfgInfo[1]  # here imu data starts
    for i in range(dev.cfgInfo[2]):
        plotresults(
            xAll[:, startidx : startidx + 3], "Acceleration IMU " + str(i + 1), "[g]"
        )
        plotresults(
            xAll[:, startidx + 3 : startidx + 6], "Gyro IMU " + str(i + 1), "[°/s]"
        )
        startidx += 6
