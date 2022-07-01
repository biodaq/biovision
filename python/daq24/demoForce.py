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
from biodaq import biodaq
from keyboard import keyboard
import time
import numpy as np
import struct

"""---------------------------------------------------------------------------------
simple demonstration in single threaded mode
data are captured and displayed at the end
------------------------------------------------------------------------------------
"""
testSamplerate = 1000 #old forceplates do not function properly with rate=4000
testMaxDuration=10.  #in seconds , measurement stops automaticly
testNchannel=4       # forceplate has 4, do not change       

def plotresults(input):
    print('plotresults(): ',len(input),'samples' )
    # first column of input is time information
    # so we plot only the columns from 1 to end
    plt.plot(input[:,1::])
    plt.grid()
    plt.title('Biodaq Data')
    plt.xlabel('t [samplenumber]')
    plt.ylabel('U [V]')
    plt.show()

def getCalibration(device):
    print("getCalibration() ",device.sendCmd("*IDN?"))
    device.sendCmd('mem:cal:dat?',True)
    data=device.readbinblock();
    if data.find(b'ID ads131      '):
        print("found ID String, thats pretty good")
    else:
        print("error:  ID not found")
        return []
    if len(data)==1024:
        print("found calibration")
        values = struct.unpack('256f',data)
        scales=[]
        scales.append(values[6]);
        scales.append(values[9]);
        scales.append(values[12]);
        scales.append(values[15]);
        print (scales)
        return scales
    return []

if __name__ == '__main__':
    import sys
    mykey = keyboard()
    mydevice=biodaq()
    #---------------------------------------------------------------------- find device -----
    print('Hello')
    ports=mydevice.getDevices()
    if len(ports)==0:
        print("no device present")
        exit()
    if len(ports)>=2:
        print("Detected more than one device and choose the first")
    if mydevice.open(ports[0]) == False:
        print('could not open port. Connected? Busy?')
        exit()
    print("*IDN? reponse: ",mydevice.sendCmd('*idn?'))
    scales=getCalibration(mydevice)
    if len(scales)==0:
        print ("error: scaling not found")
        exit()
    #--------------------------------------------------- setting up the measurement parameter ---
    mydevice.clear()
    mydevice.setSampleRate(testSamplerate)
    for x in range(testNchannel):
        mydevice.addChannel(x,1) #gains above 1 may increase the SNR for small signals
    if mydevice.doConfig()==False:
        print('config failed')
        exit()
    print('start: you may abort with a keypress')
    mydevice.sendCmd('init',True) # start streaming (ignore response)
    #--------------------------------------------------------------------- measurement loop ----
    ts = time.time()
    #first we have to create samplebuf
    newsamples = mydevice.readbinblock()
    if mydevice.errStatus()==True:
        print ("error")
    samplebuf = mydevice.decodeChans(newsamples)
    while True:
        newsamples = mydevice.readbinblock()
        if mydevice.errStatus()==True:
            print ("error")
            break
        bu = mydevice.decodeChans(newsamples)
        samplebuf = np.vstack((samplebuf,bu))
        #samplebuf+=buf
        if mykey.kbhit()==True:
            break
        if time.time()-ts > testMaxDuration:
            break
        #print (time.time()-ts,myMaxDuration)
        sys.stdout.write("got samples: %d   \r" % (len(samplebuf)) )
        sys.stdout.flush()
    print("\nstop it")  #leading \n to beautify output  
    mydevice.sendCmd('abort',True)  #stop streaming (ignore response)
    #----------------------------------------------------------------- check on lost samples
    # this is a good thing, if you have time consuming routines in measurement loop
    # device will discard samples, if program waits too long to read data
    # in this example it is not neccesary
    cnt=2 # value of starting cnt may vary from dev to dev (and should be one or two)
    scaleToIndex=1./mydevice.skal[0]
    for x in samplebuf:
        if round(scaleToIndex*x[0]) != cnt:
            print("sample index error:",x[0],cnt)
        cnt+=1    
    #-------------------------------------------------------------------------- show results
    print("recorded chans = ",len(samplebuf[0])-1,"total samples: ",len(samplebuf))
    mydevice.close()
    for i in range(4):
        samplebuf[:,i+1] *= scales[i]
    plotresults(samplebuf)
