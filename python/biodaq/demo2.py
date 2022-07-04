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
import multiprocessing as mp
import matplotlib.pyplot as plt
import multiprocessing as mp
from biodaq import biodaq
from keyboard import keyboard
import time, sys
import numpy as np

""" --------------------------------------------------------------------
demonstration with worker thread for measurement loop:

matplotlib runs only in mainthread without runtime errors,
so we had to put the measurement loop into the worker thread

worker thread is running in multiprocessing mode
only threading is not a good idea, it does not work
main task takes al lot of time during the plot

increasing either buffer or samplerate leads to slow graphical output
but no sample drops occurred
------------------------------------------------------------------------
"""
# You may change following values
testSamplerate=1000               # 500,1000,2000 or 4000
testNchannel=8                    # 1...8
testHistorylen=testSamplerate*10  #in samples
testMaxDuration=15.             #in seconds , app and grahics close automaticly
testAutoScale=False

#######################################################################################
def plotresults(input,blocking=True):
    plt.clf()
    flag = False
    iii=1
    for x in range(len(input[0])):
        if flag==True:
            plt.plot(input[:,0],input[:,x],label='ch'+str(iii))
            iii+=1
        flag = True
    plt.grid()
    plt.title('Biodaq Data')
    plt.legend(loc='upper left')
    plt.xlabel('t [s]')
    plt.ylabel('U [V]')
    if testAutoScale==False:
        plt.ylim([-2.4,2.4])
    plt.show(block = blocking)
    plt.pause(0.001) # this pause is essential for non blocking mode, reason unknown


#######################################################################################
def worker(my_q,allIsDone,isKbhit):
    mydevice=biodaq()
    #---------------------------------------------------------------------- find device -----
    print('worker thread has started')
    ports=mydevice.getDevices()
    if len(ports)==0:
        print("no device present")
        allIsDone.value = True
        return
    if len(ports)>=2:
        print("Detected more than one device and choose the first")
    if mydevice.open(ports[0]) == False:
        print('could not open port. Connected? Busy?')
        allIsDone.value = True
        return
    print("*IDN? reponse: ",mydevice.sendCmd('*idn?'))
    #--------------------------------------------------- setting up the measurement parameter ---
    mydevice.clear()
    mydevice.setSampleRate(testSamplerate)
    for x in range(testNchannel):
        mydevice.addChannel(x,1) #gains above 1 may increase the SNR for small signals
    if mydevice.doConfig()==False:
        print('config failed')
        allIsDone.value = True
        return
    print('start: you may abort with a keypress')
    mydevice.sendCmd('init',True) # start streaming
    #--------------------------------------------------------------------- measurement loop ----
    ts = time.time()
    samplecnt=0
    while True:    
        newsamples = mydevice.readbinblock()
        if mydevice.errStatus()==True:
            print ("\nerror: mydevice had error in readbinblock ",mydevice.errReason)
            break
        if isKbhit.value==True:
            break
        if time.time()-ts > testMaxDuration:
            break
        buf = mydevice.decodeChans(newsamples)
        samplecnt += len(buf)
        my_q.put(buf)
        #may send data now via UDP, see demo3.py
        sys.stdout.write("got samples: %d    \r" % (samplecnt) )
        sys.stdout.flush()
        #print("sampleq",sample_q.qsize())
    print("\nstop it")  #leading \n to beautify output  
    mydevice.sendCmd('abort',True)  #stop streaming
    mydevice.close()
    print("end of worker thread")
    allIsDone.value=True

###############################################################################
#helper for graphic, creates negativ times for histbuf
def initHistBuf(histsize,nchan,samplerate):
    ret = np.zeros((histsize,nchan))#len(mydevice.skal))
    skal=1./float(samplerate)
    for i in range(histsize):
        ret[i,0] = float(i-histsize)*skal
    return ret


###############################################################################
def main_task():
    # on linux keyboard only runs in mainthread, so we have to do it here
    mykey = keyboard()
    allIsDone=mp.Value('b',False) # signals end of measuring from worker to mainthread
    isKbhit=mp.Value('b',False)  # signals kbhit from mainthread to workerthread to stop sampling
    sample_q = mp.Queue()
    print("start Multiproc")
    t1 = mp.Process(target=worker,args=(sample_q,allIsDone,isKbhit))
    t1.start()
    print("started")
    histbuf = []
    isInitialized=False
    while True:
        cnt=0
        input=[]
        tt=sample_q.qsize()
        isFirstPacket=True
        #---------------------------------------------------- empty the queue and collect data
        for i in range(tt):
        #while sample_q.empty() == False: #this is not reliable, reason unknown
            buf=sample_q.get()
            if isFirstPacket == True:
                input=buf; 
            else:
                input = np.vstack((input,buf))
            cnt+=1
            isFirstPacket=False
        #---------------------------------------------------------------- process data     
        if len(input)!=0:
            if isInitialized==False:
                histbuf=initHistBuf(testHistorylen,testNchannel+1,testSamplerate)
                isInitialized=True
                print("histbuflen",len(histbuf))
            if len(input) < len(histbuf):
                histbuf =np.vstack((histbuf,input))
            else:
                histbuf = input
            if len(histbuf)>testHistorylen:
                nDel = len(histbuf)-testHistorylen
                histbuf=np.delete(histbuf,range(nDel),0) 
            plotresults(histbuf,blocking=False) #does not work in other than mainthread, crash
        #---------------------------------------------------------------- break from worker task ?
        elif allIsDone.value==True:
            break
        time.sleep(.03) # some delay seems to be neccessary for matplotlib on some OS
        #---------------------------------------------------------- signal keystroke to workertask
        if mykey.kbhit()==True:
            isKbhit.value=True    
    #flush the queue, else eventually sample_q will not join
    while sample_q.empty()==False:
        sample_q.get()
        print("###")
    print("t1.join()")
    t1.join()

##############################################################################
if __name__ == '__main__':
    mp.freeze_support()
    print("here we start")
    main_task()
    print("this is the end")
