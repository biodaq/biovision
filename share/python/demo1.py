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
import time
import numpy
from multiDaq import multiDaqLowLevel

myDev = multiDaqLowLevel()
# uncomment next line to see debug output on console
# myDev.setDebugFlag(True)

listDev = myDev.listDevices()
if len(listDev) == 0:
    print("no Device detected, exit now")
    exit(1)

myDev.open(0, listDev[0])  # open the first detected als device 0, 0 .. 3 is possible

print("IDN response dev:", myDev.sendCmd(0, "*idn?"))

if len(myDev.sendCmd(0, "conf:sca:rat 1000")) > 0:
    print("Configuration Cmd failed")
    exit(1)

if len(myDev.sendCmd(0, "conf:dev 0,2,0")) > 0:
    print("Configuration Cmd failed")
    exit(1)

myDev.sendCmd(0, "init", True)

gotFirstData = False
for n in range(10):
    # time.sleep(0.1)
    x1 = myDev.getStreamingData(0)
    print("---", x1.shape)
    # new data are in x1, you may process them here
    # collect data in xAll
    if x1.size > 0:
        print("got array", x1.shape)
        if not gotFirstData:
            gotFirstData = True
            xAll = x1
        else:
            xAll = numpy.vstack((xAll, x1))
    time.sleep(0.1)
myDev.sendCmd(0, "abort", True)

print(xAll)
print("caution: data in xAll are casted 16 bit raw data and not scaled!!")
time.sleep(0.1)

myDev.close(0)
myDev.close(1)
