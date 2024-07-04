# Copyright (c) 2022, Tantor GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer
#    in the documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
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
