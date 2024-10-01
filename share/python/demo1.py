# Copyright (c) 2022, Tantor GmbH
# All rights reserved.
# published under MIT license

import time
from sys import exit  # to keep pyinstaller happy

import numpy
from multidaq import multiDaqLowLevel

# on windows: specify the path, where the DLL is
#             or it will search in system paths
#             example: myDev = multiDaqLowLevel("c:/bin")
myDev = multiDaqLowLevel()
# alternative to see debug output on console: myDev = multiDaqLowLevel(debug=True)


listDev = myDev.listDevices()
if len(listDev) == 0:
    print("no Device detected, exit now")
    exit(1)

myID = 0  # you may open up to 4 devices parallel with different IDs
# IDs are numbers from 0 ... 3

if not myDev.open(myID, listDev[0]):
    print("open fails")
    exit(1)

print("IDN response dev:", myDev.sendCmd(myID, "*idn?"))

if len(myDev.sendCmd(myID, "conf:sca:rat 1000")) > 0:
    print("Configuration Cmd failed")
    exit(1)

if len(myDev.sendCmd(myID, "conf:dev 0,2,0")) > 0:
    print("Configuration Cmd failed")
    exit(1)

myDev.sendCmd(myID, "init", True)

gotFirstData = False
for n in range(10):
    time.sleep(0.1)
    x1 = myDev.getStreamingData(myID)
    # new data are in x1, you may process them here
    # collect data in xAll
    if x1.size > 0:
        print("got array from stream", x1.shape)
        if not gotFirstData:
            gotFirstData = True
            xAll = x1
        else:
            xAll = numpy.vstack((xAll, x1))

myDev.sendCmd(myID, "abort", True)

print(xAll)
print("caution: data in xAll are casted 16 bit raw data and not scaled!!")
time.sleep(0.1)

myDev.close(myID)
