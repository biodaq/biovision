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

from threading import Timer
from datetime import datetime
import struct, time, socket, atexit
import numpy as np

#define PACKET_CMD_ACKNOWLEDGE 1
#define PACKET_CMD_STREAM 2
#define PACKET_CMD_STREAM_ACK 3
#define PACKET_CMD_PING 4
#define PACKET_CMD_CLEAR_Q 5
#define MAX_UDP_PAYLOAD 1024
#typedef struct{
#    uint16_t txID;
#    uint16_t cmd;
#    uint16_t len;
#    uint16_t responseToId;
#    uint32_t streamCnt;
#} udpHeader_t;


class daq_imu_udp():
    # ------------------------------------------------------------------------
    def __init__(self, ipadress=("192.168.4.1", 1234)):
        self.idCnt=0
        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.ipAddress = ipadress
        print(self.ipAddress)
        self.sock.settimeout(0.03)
        self.idList=[]
        self.cntAck=0
        self.streamBuffer=[]
        self.streamCnt = 0
        self.CommandResponse = b''
        self.stop_timer=False
        self.isStreaming = False
        self.streamError = False #
        atexit.register(self.cleanup)
        
    # ------------------------------------------------------------------------
    def cleanup(self):
        #print("daq_imu_udp: Running cleanup")
        self.sendCmd("abort\n*rst",True,True)

    # ------------------------------------------------------------------------
    def getStreamingData(self):
        self.streamBuffer.sort()
        y=[]
        toDelete = 0
        for i in self.streamBuffer:
            if self.streamCnt > i[0]:
                toDelete += 1
                continue
            if self.streamCnt == i[0]:
                toDelete += 1
                y.append(i[1])
                self.streamCnt += 1
            else:
                break
        del self.streamBuffer[:toDelete]    
        return y

    # ------------------------------------------------------------------------
    def timer_irq(self):
        #print("tick ",time.time())
        if self.stop_timer == False:
            thread = Timer(.01, self.timer_irq)
            thread.start()
        msgFromServer=b''
        #TODO might be more than one packet
        try:
            msgFromServer = self.sock.recvfrom(4096)
        except:
            return
        if len(msgFromServer):
            #print("msgfromserver:",msgFromServer)
            if len(msgFromServer[0]) < 12:
                print("warning: Packet too short. Unknown UDP Packet")
                return
            hdr=struct.unpack("HHHHI",msgFromServer[0][0:12])
            #print("hdr =",hdr)
            msg = msgFromServer[0][12::]
            if hdr[1]==2: # streamingpackage
                #print("got streaming packet",hdr[4])
                id=hdr[0]
                self.idList.append(id)
                if len(self.idList) > 30:
                    self.idList = self.idList[len(self.idList)-30::]#.remove(0)
                if self.isStreaming==True:
                    self.streamBuffer.append((hdr[4],msg))                
                if self.cntAck >= 8:
                    #print("send Ack List, actual sample received: ",hdr[4])
                    self.sendPacketAck ()
                    self.cntAck = 0
                self.cntAck += 1    
            if hdr[1]==1: # commandpacket
                #print("Got Cmd Ack Packet:",msg)
                self.CommandResponse = msg
                pass
            if hdr[1]==4: # pingpacket
                pass
        
    # ------------------------------------------------------------------------
    def open(self,dummy): #input is for compatibility with seriaport
        self.thread = Timer(.02, self.timer_irq)
        self.thread.start()
        return True

    # ------------------------------------------------------------------------
    def buildPacketCmd (self,msg):
        cmd = 1
        rxID=0
        reqACK = 0
        ret = struct.pack("HHHHI",self.idCnt,cmd,len(msg),reqACK,rxID)
        ret += msg.encode()
        #print("buildID =",idCnt)
        self.idCnt+=1
        if self.idCnt >= 65536:
            self.idCnt = 0
        return ret

    # ------------------------------------------------------------------------
    def sendPacketAck (self):
        cmd=3
        rxID=0
        reqACK=0
        msg=b''
        for i in range(len(self.idList)):
            msg += struct.pack("H",self.idList[i])
        ret = struct.pack("HHHHI",self.idCnt,cmd,len(msg),reqACK,rxID)
        ret += msg
        #print("buildPackageACK: len =",len(msg),"msg",msg)
        self.idCnt+=1
        if self.idCnt >= 65536:
            self.idCnt = 0
        self.sock.sendto(ret, self.ipAddress)

    # ------------------------------------------------------------------------
    def sendCmd(self, cmd, expectResponse=True,ignoreResponse=False):  # wait maximal timeout on answer and returns the answer
        if cmd.endswith("\n") == False:
            cmd += "\n"
        self.CommandResponse=b'';    
        out = self.buildPacketCmd(cmd)
        #print("sendCmd at t =",time.time(),input)
        if cmd.startswith('init'):
            # print("Reset Streambuffer")
            self.streamBuffer=[]
            self.streamCnt = 0
            self.isStreaming = True
        if cmd.startswith('abort'):
            self.isStreaming = False
        self.sock.sendto(out, self.ipAddress)
        if ignoreResponse == True: # repeat 2 times, it is UDQ, you never know
            self.sock.sendto(out, self.ipAddress)
            self.sock.sendto(out, self.ipAddress)
            #print("ignoreresponse and return")
            return b''
        if expectResponse == True:
            for i in range(10):
                time.sleep(.1)
                if len(self.CommandResponse) > 0:
                    ans = self.CommandResponse
                    self.CommandResponse = b''
                    if ans.endswith(b"\r\n"):
                        ans = ans[:-2]
                    elif ans.endswith(b"\n"):
                        ans = ans[:-1]
                    return ans
            print("warning: sendCmd():",cmd," Missed answer on command")        
            return b""
        time.sleep(1)
        ans = self.CommandResponse
        self.CommandResponse = b''
        if ans.endswith(b"\r\n"):
            ans = ans[:-2]
        elif ans.endswith(b"\n"):
            ans = ans[:-1]
        return ans.decode()

if __name__ == "__main__":
    # ------------------------------------------------------------------------
    def func():
        dev = daq_imu_udp(("192.168.178.2",1234))
        #dev = daq_imu_udp(("127.0.0.1",12345))
        dev.open('dummy') # you need a dummy variable (compatiblity with usb)
        print("sendCmd returned; ",dev.sendCmd("*rst\n*idn?",True))
        #time.sleep(1)

        print("sendCmd returned; ",dev.sendCmd("conf:sca:num?",True))
        #time.sleep(1)
        ans = dev.sendCmd("conf:sca:rat 500\nconf:sca:hea 0",False)
        if len(ans):
            print("Error in command, exit now")
            return
        dev.sendCmd("init 0,0,1",False,True)
        for i in range(20):
            xx = dev.getStreamingData()
            if len(xx)>0:
                print("got ",len(xx))
            time.sleep(.1)
        dev.sendCmd("abort",False,True)
        time.sleep(1)
        xx = dev.getStreamingData()
        print ("got data after abort:",len(xx))
        #print ("data:",xx)
        dev.stop_timer = True
        
        print("End of Test")
    # ------------------------------------------------------------------------
    func()
