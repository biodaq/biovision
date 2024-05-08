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
from sys import exit  # to keep pyinstaller happy

from multiDaq import multiDaqLowLevel

# on windows you may specify the DLL, example: myDev = multiDaqLowLevel("c:/bin")
myDev = multiDaqLowLevel()
# myDev.setDebugFlag(True)

listDev = myDev.listDevices()
if len(listDev) == 0:
    print("no Device detected, exit now")
    exit(1)
if len(listDev) < 2:
    print("Error: we need 2 devices, exit now")
    exit(1)

myDev.open(0, listDev[0])  # open the first detected als device 0
myDev.open(1, listDev[1])  # open the second detected als device 1

print("IDN response dev 1:", myDev.sendCmd(0, "*idn?"))
print("IDN response dev 2:", myDev.sendCmd(1, "*idn?"))


if len(myDev.sendCmd(0, "conf:dev 0,2,0")) > 0:
    exit(1)
if len(myDev.sendCmd(1, "conf:dev 0,3,0")) > 0:
    exit(1)

# use disableTx and enableTx to synchronize both init commands
myDev.disableTx()
myDev.sendCmd(0, "init", True)
myDev.sendCmd(1, "init", True)
# You may add Trigger commands here,
# myDev.sendCmd(0,'')
myDev.enableTx()
x01 = myDev.getStreamingData(0)
x02 = myDev.getStreamingData(1)


time.sleep(1)
x1 = myDev.getStreamingData(0)
x2 = myDev.getStreamingData(1)


myDev.sendCmd(0, "abort", True)
myDev.sendCmd(1, "abort", True)

print(x1)
print(x2)
time.sleep(0.1)

myDev.close(0)
myDev.close(1)
