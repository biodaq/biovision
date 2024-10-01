# Copyright (c) 2022, Tantor GmbH
# All rights reserved.
# published under MIT license


import ctypes
import time
from sys import exit  # to keep pyinstaller happy

import numpy
from multidaq import multiDaq

myScaling = []


def testCallbackFunction(dat, len):
    samplesize = int(myScaling.size)
    # callback delivers unscaled 16 bit data, so we first scale them here
    raw = numpy.frombuffer(
        dat[:len], dtype=numpy.dtype(ctypes.c_int16), count=int(len / 2)
    )
    values = raw.reshape(int(len / samplesize / 2), int(samplesize)).astype(float)
    for i in range(samplesize):
        values[:, i] *= myScaling[0, i]
    # All scaled data are in values now, do what you want to do
    print(values)


# -------------------------------------------------------------------------
# we need ID to set the right callback
MyID = 0  # 0 ... 3 allowed
dev = multiDaq(MyID)
print("Version of DLL", dev.getVersionInfo())
A = dev.listDevices()
if len(A) == 0:
    print("No Device found: exit now")
    exit(1)
if not dev.open(A[0]):
    print("open() failed: Device Busy? exit now")
    exit(1)
# dev.open(A[0],True) # test after open and output to console
dev.clearConfig()
dev.addAdc16(6)  # only range = 6 for Adc16 allowed at the moment
dev.addAdc16(6)
dev.addAdc16(6)
dev.configure()  # last command before startSampling()
# after configure() scaling vector is valid, so read it out
myScaling = dev.scale
callback_type = ctypes.CFUNCTYPE(None, ctypes.POINTER(ctypes.c_char), ctypes.c_int)
callback = callback_type(testCallbackFunction)
dev.LL.setDataCallback(MyID, callback)

print("############### Start")
dev.startSampling()
# for 3 seconds, Callbacks will be active
time.sleep(3)
print("############### Stop")
dev.stopSampling()
dev.close()
