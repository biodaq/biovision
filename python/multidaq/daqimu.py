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

# example usage:
#    daqimu() or daqimu(False):                  connects to USB
#    daqimu(True):                               connects to Wifi standard, that is ip=192.168.4.1 and port 1234
#    daq_imu(True,'myDeviceinLocalNetworkName'): tries to find the named device in your local network, uses Port 1234
#    daq_imu(True,("192.168.178.2",12345)):      connects with ip and port 12345, here you can fully specify the network
#                                                but you have to know, what you do

import struct, time
import numpy as np
import atexit
import socket
from daq_imu_udp import daq_imu_udp
from daq_imu_usb import daq_imu_usb

class daqimu:
    # ------------------------------------------------------------------------
    def __init__(self,isWifi = False, ip=("192.168.4.1",1234)):
        if type(ip) == str:
            try:
                myip=socket.gethostbyname(ip)
            except:
                print("daqimu: exception, could not resolve hostname",ip)
            finally:
                pass
            #print("daqimu: try to connect to: ",ip,(myip,1234))
            ip = (myip,1234)
        if isWifi==True:
            if(ip[1] != 1234):
                #print("Warning constructor daqimu: this is not the standard Port")
                pass
            self.interface = daq_imu_udp(ip)
        else:
            self.interface = daq_imu_usb()
        # print("isWifi ",isWifi)    
        self.isWifi = isWifi
        #self.sampleRate = 100
        self.error = False
        self.errReason = ""
        self.isOpen = False
        self.configuredDevices=[0,0,0]
        self.detectedDevices=[0,0,0]
        #self.numAdc16 = 0
        self.numAdc24 = 0
        self.numImu = 0
        self.config=[]
        self.skal = []
        self.initString=''
        self.configDone = False
        atexit.register(self.cleanup)
        
    # ------------------------------------------------------------------------
    def cleanup(self):
        # print("daqimu: Running cleanup")
        if self.isOpen == True:
            self.close()

    # ------------------------------------------------------------------------
    def errStatus(self):
        return self.error

    # ------------------------------------------------------------------------
    def clear(self):
        self.config = []
        self.configDone = False
        self.initString=''

    # ------------------------------------------------------------------------
    def getChoices(self):
        ans = {
            "sampleRate": [100, 200, 500],
            "rangeAcc": [2, 4, 8, 16],
            "rangeGyro": [250,500,1000,2000],
            "oversamplingAdc": 2
        }
        return ans

    # ------------------------------------------------------------------------
    def isError(self):
        if self.interface.streamError == True:
            print("daq_imu: isError() found streamerror, perhaps You configured too much channels")
            return True
        return False

    # ------------------------------------------------------------------------
    def getDevices(self, checksn=""):
        if self.isWifi == True:
            # TODO get the Serialnumber from device
            class Service(object): # dummy object for compatibility with seriaport, makes it simpler
                data = []
                def __init__(self):
                    self.serial_number = 'h99'
            a=[]
            fakePort = Service()
            a.append(fakePort)
            return a
        else:
            a=self.interface.getDevices()
            return a

    # ------------------------------------------------------------------------
    def testConfig(self):
        if self.interface.isStreaming == False:
            # for usb connection we have only to try once
            # but for udp this is not save
            for k in range(3): # special for Wifi connection, try it three times maximum
                ans = self.interface.sendCmd('conf:sca:num?',True)
                print("ans =",ans)
                if(len(ans)>0):
                    if k>0:
                        print("daqimu: testConfig() commands were lost, had to try n = ",k,"times")
                    break
            values = ans.split(b',')
            ok = True
            if len(values)!= 3:
                return False
            for i in range(3):
                self.detectedDevices[i] = int(values[i])
                if int(values[i]) < self.configuredDevices[i]:
                    ok = False
            if ok==False:
                print("daqimu: testConfig() Error: detected devices ",self.detectedDevices," configured devices",self.configuredDevices)        
            return ok
            #TODO test this
        else:
            return False    

    # ------------------------------------------------------------------------
    def doConfig(self):
        if self.isWifi == True:
            cfgStr='conf:sca:hea 0\n'
        else:
            cfgStr=''
        self.skal = []
        imu6skal = []
        adc16skal = []
        imuCnt=0
        adc16Cnt=0
        srString = 'conf:sca:rat 100' # default value
        for k in self.config:
            if k[0]=='sr':
                srString = 'conf:sca:rat ' + str(k[1]) +'\n'
            if k[0]=='imu6':
                cfgStr += 'conf:imu:para ' + str(imuCnt) + ',' + str(k[1]) + ',' + str(k[2]) + '\n'
                imu6skal.append(k)
                imuCnt += 1
                self.configuredDevices[2] =  self.configuredDevices[2] + 1
            if k[0]=='adc16':
                adc16skal.append(3/32768) # by now its konstant 3 Volt
                adc16Cnt += 1
                self.configuredDevices[0] += 1 #  self.configuredDevices[0] + 1
                print("****************************************added adc16")
            # TODO adc24 imu9, till now nothing is to do
        cfgStr += srString
        self.initString = 'init '+str(adc16Cnt)+',0,'+str(imuCnt);
        # build skaling list
        for i in range(len(adc16skal)):
            self.skal.append(adc16skal[i])    
        for i in range(len(imu6skal)):
            self.skal.append(1/32768 * imu6skal[i][1])    
            self.skal.append(1/32768 * imu6skal[i][1])    
            self.skal.append(1/32768 * imu6skal[i][1])    
            self.skal.append(1/32768 * imu6skal[i][2])    
            self.skal.append(1/32768 * imu6skal[i][2])    
            self.skal.append(1/32768 * imu6skal[i][2])    
        #print ("skallist = ",self.skal)

        ans = self.interface.sendCmd(cfgStr,False)
        if len(ans) > 0:
            self.configDone = False
            return False
        self.configDone = True
        return True

    # ------------------------------------------------------------------------
    def addImu6(self, rangeAcc, rangeGyro):
        self.config.append(('imu6',rangeAcc,rangeGyro))    
        return True

    # ------------------------------------------------------------------------
    def addImu9(self, nphys, gain=1):
        print("TODO implement")
        exit(1)

    # ------------------------------------------------------------------------
    def addAdc16(self):
        tmp = ('adc16','dummy') # a dummy is neccessary, I dont understand python
        self.config.append(tmp)
        return True

    # ------------------------------------------------------------------------
    def setSampleRate(self, dr):
        y = ('sr',dr)
        self.config.append(y)
        return True

    # ------------------------------------------------------------------------
    def startSampling(self):
        # print("startSampling(): ",self.initString)
        if self.configDone == False:
            self.doConfig()
        self.interface.sendCmd(self.initString,True,True)
        return True

    # ------------------------------------------------------------------------
    def stopSampling(self):
        # print("stopSampling()")
        self.interface.sendCmd('abort',True,True)

    # ------------------------------------------------------------------------
    def getStreamingData(self):
        nch = len(self.skal) #len(self.chans)
        dat = self.interface.getStreamingData();
        if len(dat) == 0:
            return np.empty(0)
        nn = len(dat[0])//2 # integer division
        form = "<"  # little endian
        for n in range(nn):
            form += "h"
        tmp = []
        sampleCnt = int(0)
        for i in dat:
            unpacked = struct.unpack(form, i)
            sampleCnt += len(unpacked)//nch
            for value in unpacked:
                tmp.append(float(value))
        y = np.array(tmp).reshape(sampleCnt,nch)
        for i in range(len(self.skal)):
            y[:,i] = self.skal[i] * y[:,i]
        return y

    # ------------------------------------------------------------------------
    def open(self, input):
        return self.interface.open(input)
    
    # ------------------------------------------------------------------------
    def close(self):
        if self.isWifi:
            #print("close(): daq_imu_udp needs stoptimercommand")
            self.interface.stop_timer = True
            return True
        else:
            self.interface.close()
            self.isOpen = False

if __name__ == "__main__":
    # ------------------------------------------------------------------------
    mydevice = daqimu(True,("192.168.178.2",1234))
    #mydevice = daqimu(True,'biovision1')
    opts = mydevice.getChoices()
    print("allowed Parameter values:")
    for x in opts:
        print(x, opts[x])
    # ports=mydevice.getDevices('desiredSerialNumber') #you may filter the serialnumber (only wih USB UDP is connectionless),
    #                                                   then you get the desired device
    ports = mydevice.getDevices()
    print("daq_imu: ports",ports)

    print("#############################")
    if len(ports) == 0:
        print("no device present")
        exit()
    if len(ports) >= 2:
        print("Detected more than one device and choose the first")
    for x in ports:
        print("present is serial =", x.serial_number)
    print("serialnumber of port to open:", ports[0].serial_number)
    if mydevice.open(ports[0]) == False:
        print("could not open port. Connected? Busy?")
        exit(1)
    else:
        print("port sucessfully opened")
    
    # ---------------------------------   do the configuration
    mydevice.clear();    # first clear config
    #mydevice.setSampleRate(500) # the first step is to set the samplerate, else configuration will fail
    mydevice.addImu6(2,250)      # add 
    mydevice.addImu6(2,250)      # add 
    #mydevice.addAdc16()      # force an error, if device has no adc16 
    mydevice.setSampleRate(500)
    if(mydevice.doConfig() ==False):
        print("config failed")
        mydevice.close()
        exit(1)
    # ---------------------------------   tests whether device is able to start this configuration
    # not neccessary step, duration is maximal 3 seconds (Wifi Configuration)
    # if You do not do this, the connection will fail after the init command   
    if(mydevice.testConfig() == False):
        print("device is unable to start this configuration without errors")
        mydevice.close()
        exit(1)
    nothingGot = True   
    mydevice.startSampling()
    
    allSamples = np.empty(0)
    for i in range(10):
        y = mydevice.getStreamingData()
        if mydevice.isError() == True:
            print("Errors occurred during Sampling")
            break
        if y.shape != np.empty(0).shape:
            print("gotSomething ",y.shape)
            if allSamples.shape == np.empty(0).shape:
                print("getfirst array")
                allSamples = y
            else:
                allSamples = np.vstack((allSamples,y))
        else:
            pass
            #print("got nothing")
        time.sleep(.1)    

    time.sleep(1)
    mydevice.stopSampling()
    time.sleep(.5)
    y = mydevice.getStreamingData()
    if y.shape != np.empty(0).shape:
        print("gotSomething ",y.shape)
        allSamples = np.vstack((allSamples,y))
    else:
        pass
        #print("got nothing")
    
    time.sleep(1)
    mydevice.close()
    #print(y)
    print ("format of last result:",y.shape)
    print ("format of allSamples:",allSamples.shape)
    #with open('test.npy', 'wb') as f:
        #np.save(f, allSamples   )
    exit(0)
