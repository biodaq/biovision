# Copyright (c) 2022, Tantor GmbH
# All rights reserved.
# published under MIT license


import os
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
    # dev = multiDaq() # default uses channel 0 and dll in working directory
    # dev = multiDaq(2) # uses channel 2
    # dev = multiDaq(2,"path/to/DLL") # uses channel 2 and path to dll
    # dev = multiDaq(1,"c:/bin")
    # dev = multiDaq(1,"c:\\bin")

    my_os = platform.system()

    if my_os == "Windows":
        # check wether the dll exists in your working directory
        # if not, the dll has to be in $PATH
        pathname = os.getcwd()
        if not os.path.isfile(pathname + "/biovisionMultiDaq.dll"):
            pathname = ""
            print("No DLL found. Try to find the DLL in $PATH")
        else:
            print("found DLL in my Path:", pathname)
        dev = multiDaq(0, pathname)
    else:
        dev = multiDaq()

    print("Version of DLL:", dev.getVersionInfo())

    A = dev.listDevices()
    if len(A) == 0:
        print("No Device found: exit now")
        exit(1)
    if not dev.open(A[0]):
        print("open() failed: Device Busy? exit now")
        exit(1)

    # ------------------ configure the device ------------------------
    dev.clearConfig()
    if not dev.setSampleRate(1000):
        print("fatal: Could not set samplerate")
        exit(1)
    # mitigate error handling, it will cause error in configure()
    dev.addAdc16(6)  # only range = 6 for Adc16 allowed at the moment
    dev.addAdc16(6)
    # dev.addImu6(3, 250)

    # minimal errorhandling should be done before startSampling !
    if not dev.configure():  # last command before startSampling()
        print("Fatal: Config failed")
        exit(1)

    dev.startSampling()

    # ------------------------------------ aquisition loop ------------------------
    gotFirstData = False
    for i in range(20):
        time.sleep(0.1)
        x = dev.getStreamingData()
        print("got data", x.shape)
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
        exit(1)
    start = dev.cfgInfo[0]  # here Adc16 data starts
    if dev.cfgInfo[1] > 0:  # plot all analog channels in one plot
        plotresults(xAll[:, start : start + dev.cfgInfo[1]], "analogdata", "[V]")

    start = dev.cfgInfo[0] + dev.cfgInfo[1]  # here imu data starts
    for i in range(dev.cfgInfo[2]):
        plotresults(xAll[:, start : start + 3], "Acceleration IMU " + str(i + 1), "[g]")
        plotresults(xAll[:, start + 3 : start + 6], "Gyro IMU " + str(i + 1), "[°/s]")
        start += 6
