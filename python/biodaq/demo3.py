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
from biodaq import biodaq, bioplot
from keyboard import keyboard
import time

"""---------------------------------------------------------------------------------
simple demonstration in single threaded processing mode
data are send to daqPlotUdp.exe. if daqPlotUdp.exe is running else errmsg
------------------------------------------------------------------------------------
"""
testMaxDuration = 15.0  # in seconds , measurement stops automaticly
testNumChannels = (
    4  # for n!= 4 you have to change the configuration string of daqPlotUdp
)
testStackedView = True  # plot in stacked view? True or False
testSendToIP = [("127.0.0.1", 20012)]  # to localhost
#  you can plot simutanously to more than one IP
#  correct desired adresses and uncomment next line
# testSendToIP=[("127.0.0.1",20012),("192.168.178.114",20012)]
# depending on local machine, you have to edit firewall configuration

import socket


def getPlotDevices():
    ret = []
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    sock.settimeout(0.1)
    # Enable broadcasting mode
    # sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    sock.sendto(b"WhoIsPresent?", ("<broadcast>", 20012))
    while True:
        msgFromServer = b""
        try:
            tmp = sock.recvfrom(1024)
            if len(tmp) != 2:
                print("wassolldas")
            print("ipsearch found ", tmp[1], "inh", tmp[0])
            if tmp[0].startswith(b"I am here and ready\n"):
                ret.append(tmp[1])
        # except socket.timeout:
        # print("biodaq: warning timeout")
        except:
            break
            # print("biodaq: warning exception UDP read")
    return ret


if __name__ == "__main__":
    import sys

    mykey = keyboard()
    mydevice = biodaq()
    myIPlist = getPlotDevices()
    #myIPlist.append(("127.0.0.1", 20012))  # HACKHACKHACK
    myPlotList = []
    for x in myIPlist:
        myPlotList.append(
            bioplot(x)
        )  # here You may change the UDP port and IP Address , default is 20012 and "127.0.0.1"
    print("myplotList size = ", len(myPlotList))

    confPlot = ""  # This is the configuration string for the plotter
    if testStackedView == False:
        confPlot += "conf:dummy 1\n"  # first channel from biodaq is timing information do not display
        confPlot += "conf:chan 4,ch1,-2.4,2.4\n"  # 4 plots into one graph
        confPlot += "conf:timespan 20000\n"
    else:
        confPlot += "conf:dummy 1\n"  # first channel from biodaq is timing information do not display
        confPlot += "conf:chan 1,ch1,-2.4,2.4\n"
        confPlot += "conf:chan 1,ch2,-2.4,2.4\n"
        confPlot += "conf:chan 1,ch3,-2.4,2.4\n"
        confPlot += "conf:chan 1,ch4,-2.4,2.4\n"
        confPlot += "conf:timespan 20000\n"
    """ ----------------------
    # you may configure a mixed mode, this will run for 4 channels
    # uncomment for test, this will overwrite the cfg string
    confPlot='conf:dummy 1\n'     #first channel from biodaq is timing information do not display
    confPlot+='conf:chan 2,ch1,-2.4,2.4\n' # display the first 2 channels in the first graph
    confPlot+='conf:dummy 1\n'     # next channel no graph
    confPlot+='conf:chan 1,ch3,-2.4,2.4\n' # next one channel in one graph
    tmp+='conf:timespan 20000\n'
    """
    cnt1 = 0
    for x in myPlotList:
        tmp1 = x.sendCmd("*idn?")
        if len(tmp1) == 0:
            print(
                "there is no daqPlotUdp.exe running or port or IP are wrong\nwe quit now"
            )
            exit()
        else:
            print("found daqplot device", cnt1, "response was:", tmp1)
            cnt1 += 1
    for x in myPlotList:
        tmp1 = x.sendCmd(confPlot)
        if tmp1 != "ACK":
            print("msg received:", tmp1)
            print("There was an error in the configuring string of daqPlotUdp.exe")
            exit()
    # ---------------------------------------------------------------------- find device -----
    print("Hello")
    ports = mydevice.getDevices()
    if len(ports) == 0:
        print("no device present")
        exit()
    if len(ports) >= 2:
        print("Detected more than one device and choose the first")
    if mydevice.open(ports[0]) == False:
        print("could not open port. Connected? Busy?")
        exit()
    print("*IDN? reponse: ", mydevice.sendCmd("*idn?"))
    # --------------------------------------------------- setting up the measurement parameter ---
    mydevice.clear()
    mydevice.setSampleRate(1000)
    for x in range(testNumChannels):
        mydevice.addChannel(
            x, 1
        )  # gains above 1 may increase the SNR for small signals
    if mydevice.doConfig() == False:
        print("config failed")
        exit()
    print("start: you may abort with a keypress")
    mydevice.sendCmd("init", True)  # start streaming
    # --------------------------------------------------------------------- measurement loop ----
    ts = time.time()
    samplecnt = 0
    while True:
        newBinBlock = mydevice.readbinblock()
        if mydevice.errStatus() == True:
            print("biodaq error reason=", mydevice.errReason)
            break
        buf = mydevice.decodeChans(newBinBlock)
        samplecnt += len(buf)
        for x in myPlotList:
            x.sendDatablock(buf)  # fire and forget on UDP
        if mykey.kbhit() == True:
            break
        if time.time() - ts > testMaxDuration:
            break
        sys.stdout.write("got samples: %d   \r" % (samplecnt))
        sys.stdout.flush()
    print("\nstop it")  # leading \n to beautify output
    mydevice.sendCmd("abort", True)  # stop streaming
    # -------------------------------------------------------------------------- show results
    print("processed samples =", samplecnt)
    print("close the device")
    mydevice.close()
    print("this is the end")
