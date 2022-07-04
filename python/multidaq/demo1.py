# Copyright (c) 2022, Tantor GmbH
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer 
#     in the documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING,
# BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
# SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING 
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import matplotlib.pyplot as plt
from daqimu import daqimu
import time
import numpy as np
from sys import exit #for pyinstaller to work properly
"""---------------------------------------------------------------------------------
simple demonstration with graphical output
graphic shows the ACC of the first IMU
data are captured as numpy array and may be saved at the end
"""
# You may play with the parameters
testSamplerate = 500 # 100,200 or 500
testDuration=15  #in seconds , measurement stops automaticly
testNchannel=1       # from 1 ... 2 maximal 2 IMUs possible        
testAutoScale = False
testHistoryLen = testSamplerate*10 # Time Window for Graphic in samples

#######################################################################################
def plotresults(input,blocking=True):
    plt.clf()
    iii=1
    for x in range(3): # only the first ACC
        plt.plot(input[:,x],label='ch'+str(iii))
        iii+=1
        plt.grid()
    plt.title('daqimu Data')
    plt.legend(loc='upper left')
    plt.xlabel('sampleNumber')
    plt.ylabel('acc [g]')
    if testAutoScale==False:
        plt.ylim([-2,2])
    plt.show(block = blocking)
    plt.pause(0.001) # this pause is essential for non blocking mode, reason unknown

# ------- lets start
dev=daqimu() # (or  daqimu(False)) connects with USB interface
# dev=daqimu(True)  # wifi default 192.168.4.1 and port 1234
# dev=daqimu(True,'hostname')  # wifi with dedicated hostname (if device is in local net)
# dev=daqimu(True,("192.168.178.2",1234))  # wifi with dedicated ip address and port
#---------------------------------------------------------------------- find device -----
print('Hello')
ports=dev.getDevices()
if len(ports)==0:
    print("no device present") # wifi UDP is connectionless and will never fail here
    exit(1)
if len(ports)>1:
    print("Detected more than one device and choose the first")
if dev.open(ports[0]) == False:
    print('could not open port. Connected? Busy?')
    exit(1)
#--------------------------------------------------- setting up the measurement parameter ---
dev.clear()
dev.setSampleRate(testSamplerate)
for x in range(testNchannel):
    dev.addImu6(2,250)
if dev.doConfig()==False: # this optional step will configure your device and has a distinct duration
    #                       advantage: following startSampling() will start immideatly
    #                       if you dont do, startSampling() will do that step
    #                       but that will produce a delay
    #                       that is important if you want to start with trigger signals
    print('config failed')
    exit(1)
print ("device is configured, please Start Measurement")
input("Press Enter to continue.")    
print("startSampling()")    
dev.startSampling() # start streaming
#--------------------------------------------------------------------- measurement loop ----
ts = time.time()
allSamples = np.empty(0)
ts = time.time()
while True:
    y = dev.getStreamingData()
    if dev.isError() == True:
        print("Errors occurred during Sampling")
        break
    if y.shape != np.empty(0).shape:
        print("got array",y.shape)
        if allSamples.shape == np.empty(0).shape:
            print("got first non empty array, streaming is working")
            allSamples = y
            histbuf = np.zeros((testHistoryLen,testNchannel*6))# 6 columns for 1 IMU
        else:
            histbuf =np.vstack((histbuf,y))
            if len(histbuf)>testHistoryLen:
                nDel = len(histbuf)-testHistoryLen
                histbuf=np.delete(histbuf,range(nDel),0) 
            plotresults(histbuf,False)
            allSamples = np.vstack((allSamples,y))
    else:
        pass
    if (time.time() - ts > testDuration):
        break
    
print("stopSampling()")
dev.stopSampling()  #stop streaming (ignore response)
#time.sleep(1)  # this 2 lines are optional, if you need the rest of the data
#dev.getStreamingData()
dev.close()
# if you want to hold the last graphic, uncomment the following two lines
#print("success, close the Graphic to run cleanup!")
#plotresults(histbuf,True) # hold the last graphic
