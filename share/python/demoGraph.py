# Copyright (c) 2022, Tantor GmbH
# All rights reserved.
# published under MIT license

import platform
import sys
import time

# import matplotlib.pyplot as plt
# import numpy
from multidaq import multiDaq

if __name__ == "__main__":
    # You may open up to 4 devices parallel with different IDs ( from 0 ... 3 )
    # dev = multiDaq() # default uses channel 0 and dll in working directory
    # dev = multiDaq(2) # uses channel 2
    # dev = multiDaq(2,"path/to/DLL") # uses channel 2 and path to dll
    # dev = multiDaq(1,"c:/bin")
    # dev = multiDaq(1,"c:\\bin")

    my_os = platform.system()

    dev = multiDaq()
    # dev = multiDaq(0, "c:/projects/TantorSW/driver/bin")

    print("Version of DLL:", dev.getVersionInfo())

    A = dev.listDevices()
    if len(A) == 0:
        print("No Device found: exit now")
        exit(1)
    if not dev.open(A[0]):
        print("open() failed: Device Busy? exit now")
        exit(1)
    isBioDaq = False
    if A[0].startswith("bio"):
        print(A[0])
        isBioDaq = True

    # ------------------ configure the device ------------------------
    dev.clearConfig()
    if not dev.setSampleRate(1000):
        print("fatal: Could not set samplerate")
        exit(1)
    # mitigate error handling, it will cause error in configure()
    for i in range(3):
        if isBioDaq:
            dev.addAdc32(2)  # 1,2,4,8,12 allowed
        else:
            dev.addAdc16(6)  # 6 allowed at the moment
            # dev.addImu6(3, 250)
    if not dev.configure():
        print("could not configure, config Errors occurred")
        sys.exit(1)
    dev.LL.configGraph(1400, 30, 500, 1000)
    time.sleep(0.5)

    dev.startSampling()

    # ------------------------------------ aquisition loop ------------------------
    gotFirstData = False
    for i in range(30):
        time.sleep(0.1)
        x = dev.getStreamingData()
        print("got data", x.shape)

    dev.stopSampling()
    print("Wait 3 seconds, then close graphics")
    time.sleep(3)  # for convenience,
    dev.close()
    dev.LL.killGraph()
