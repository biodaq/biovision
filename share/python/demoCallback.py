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

import numpy
import ctypes
import time
from multiDaq import multiDaq

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
