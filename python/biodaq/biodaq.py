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
from os import times_result
import struct, time, socket
import serial.tools.list_ports  # For listing available serial ports
import serial  # For serial communication, they are in pyserial
import numpy as np


class bioplot:
    # ------------------------------------------------------------------------
    def __init__(self, addr=("127.0.0.1", 20012)):
        # print("Hello Plotter on port",port)
        self.serverAddressPort = addr
        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        # self.sock.bind(("127.0.0.1", 20013))
        self.sock.settimeout(0.1)

    def createbinblock(self, yy):
        out = b"#"
        l = len(yy) * 4
        out += str(len(str(l))).encode()
        out += str(l).encode()
        formN = str(len(yy))
        formN += "f"
        out += struct.pack(formN, *yy)
        out += b"\n"
        return out

    def createbinblock_from_raw(self, yy):
        out = b"#"
        l = len(yy)
        out += str(len(str(l))).encode()
        out += str(l).encode()
        out += yy
        out += b"\n"
        return out

    def sendDatablock(self, input):  # fire and forget
        bytesBinBlock = b""
        if isinstance(input, bytes):
            bytesBinBlock = self.createbinblock_from_raw(input)
        if isinstance(input, float):
            bytesBinBlock = self.createbinblock(input)
        if isinstance(input, np.ndarray):
            fout = np.float32(input)
            bytesBinBlock = self.createbinblock_from_raw(fout.tobytes())
        if len(bytesBinBlock) < 65518:  # this is maximum for udp
            if len(bytesBinBlock) != 0:
                self.sock.sendto(bytesBinBlock, self.serverAddressPort)
                return True
            print("biodaq: zero block")
            return False
        else:
            print("biodaq: error block is too big")
        return False

    def sendCmd(self, input):  # wait maximal timeout on answer and returns the answer
        if input.endswith("\n") == False:
            input += "\n"
        self.sock.sendto(input.encode(), self.serverAddressPort)
        msgFromServer = b""
        try:
            tmp = self.sock.recvfrom(1024)
            if len(tmp) != 2:
                return ""
            if tmp[1] == self.serverAddressPort:
                msgFromServer = tmp[0]
        # except socket.timeout:
        # print("biodaq: warning timeout")
        except:
            print("biodaq: warning exception UDP read")
        ans = msgFromServer.decode()
        if ans.endswith("\r\n"):
            ans = ans[:-2]
        elif ans.endswith("\n"):
            ans = ans[:-1]
        return ans


class biodaq:
    # ------------------------------------------------------------------------
    def __init__(self):
        self.ser = ""
        self.chans = []
        self.gains = []
        self.skal = []
        self.sampleRate = 1000
        self.error = False
        self.errReason = ""

    # ------------------------------------------------------------------------
    def errStatus(self):
        return self.error

    # ------------------------------------------------------------------------
    def clear(self):
        self.chans = []
        self.gains = []
        self.sampleRate = 1000

    # ------------------------------------------------------------------------
    def getChoices(self):
        # chans = [0,1,2,3,4,5,6,7]
        chans = []
        for i in range(8):
            chans.append(i)
        ans = {
            "chans": chans,
            "rates": [500, 1000, 2000, 4000],
            "gains": [1, 2, 4, 8, 12],
        }
        return ans

    # ------------------------------------------------------------------------
    def addChannel(self, nphys, gain=1):
        self.chans.append(nphys)
        self.gains.append(gain)
        sc = 1.0 / (32768.0 * 65536.0)
        sc = sc / float(gain)
        self.skal.append(sc)

    # ------------------------------------------------------------------------
    def setSampleRate(self, dr):
        self.sampleRate = dr

    # ------------------------------------------------------------------------
    def doConfig(self):
        if len(self.skal) == len(self.chans):
            sc = 1.0 / float(self.sampleRate)
            self.skal.insert(0, sc)
        configstr = ""
        Cnt = 0
        configstr += "conf:sca:rat " + str(self.sampleRate) + "\n"
        lststr = "conf:sca:lis "
        for x in self.chans:
            configstr += (
                "conf:sca:gai "
                + str(self.chans[Cnt])
                + ","
                + str(self.gains[Cnt])
                + "\n"
            )
            lststr += str(self.chans[Cnt]) + ","
            Cnt += 1
        lststr = lststr[:-1]
        configstr += lststr + "\n"
        # print("cfgstr="),configstr)
        a = self.sendCmd(str(configstr))
        if len(a) > 0:
            return False
        else:
            return True

    # ------------------------------------------------------------------------
    def decodeChans(self, dat):
        nch = len(self.chans) + 1
        form = "<I"  # first is an unsigned index
        for n in range(nch - 1):
            form += "i"
        unpacked = struct.iter_unpack(form, dat)
        tmp = []
        for sample in unpacked:
            for value in sample:
                tmp.append(float(value))
        y = np.array(tmp)
        chans = len(self.skal)
        lges = np.size(y)
        ret = np.zeros((int(lges / chans), chans))
        for x in range(chans):
            ret[:, x] = self.skal[x] * y[x:lges:chans]
        return ret

    # ------------------------------------------------------------------------
    def getDevices(self, checksn=""):
        a = serial.tools.list_ports.comports()
        ports = []
        for w in a:
            # print('found %s  vid=%d pid=%d sn=%s'%(w.name,w.vid,w.pid,w.serial_number))
            if (w.vid == 1155 and w.pid == 22336) or (w.vid == 6790 and w.pid == 29987):
                # for compatibility we remove trailing dirt
                w.serial_number = w.serial_number.lower()  # some os change that!
                for x in w.serial_number:
                    if x == "_" or x == " ":
                        w.serial_number = w.serial_number[1:]
                    else:
                        break
                # check the serialnumber whether it is compatible
                tst = w.serial_number[:1]
                if tst == "b" or tst == "c" or tst == "d" or tst.isdigit():
                    tst = w.serial_number
                    if tst[0].isdigit() == True:
                        try:
                            num = int(tst)
                        except:
                            num = -1
                    else:
                        try:
                            num = int(tst[1:])
                        except:
                            num = -1
                    if num != -1:
                        # print("found port",w,"SN=",w.serial_number,"num=",num)
                        if checksn == w.serial_number:
                            ports.append(w)  # (w.vid, w.device, w.serial_number))
                        elif checksn == "":
                            ports.append(w)  # (w.vid, w.device, w.serial_number))
        return ports

    # ------------------------------------------------------------------------
    def open(self, input):
        try:
            self.ser = serial.Serial(
                port=input.device,
                baudrate=115200,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=0.5,
            )
            # print("connected to: " + self.ser.portstr)
            # self.ser.set_buffer_size(rx_size = 200000, tx_size = 100000)
            return True
        except serial.SerialException:
            # print ('port is busy.')
            return False

    # ------------------------------------------------------------------------
    def close(self):
        self.sendCmd("abort", True)  # for safety reasons
        time.sleep(0.15)
        # rest = self.ser.read_all()
        self.ser.flushInput()
        # print('close')
        self.ser.close()

    # ------------------------------------------------------------------------
    def sendCmd(self, mycmd, ignoreResponse=False):
        tmp = mycmd + "\n"
        self.ser.write(tmp.encode())
        if ignoreResponse == True:
            return ""
        time.sleep(0.03)
        ans = self.ser.read_all()
        if ans.endswith(b"\r\n"):
            ans = ans[:-2]
        elif ans.endswith(b"\n"):
            ans = ans[:-1]
        return ans.decode()

    # ------------------------------------------------------------------------
    def readbinblock(self):
        # if self.ser.inWaiting() > 8000:
        # print("warn",self.ser.inWaiting())
        a = self.ser.read(1)
        if len(a) == 0:
            self.error = True
            self.errReason = "#1"
            return b""
        if a == b"#":
            a = self.ser.read(1)
            if len(a) == 0:
                self.error = True
                self.errReason = "#2"
                return b""
            n = int(a)
            a = self.ser.read(n)
            if len(a) != n:
                self.error = True
                self.errReason = "#3"
                return b""
            n = int(a)
            # print(n)
            retwert = self.ser.read(n)
            if len(retwert) != n:
                self.error = True
                self.errReason = "#4"
                return b""
            # print(retwert)
            a = self.ser.read(1)
            if a == b"\n":
                # print('found LF')
                return retwert
            elif a == b"\r":
                a = self.ser.read(1)
                if a == b"\n":
                    # print('found LF')
                    return retwert
                else:
                    self.error = True
                    self.errReason = "#5"
                    return b""
            else:
                self.error = True
                self.errReason = "#6"
                # print("a=",a,"avail",self.ser.inWaiting())
                return b""
        #print("a",a)
        return b""

if __name__ == "__main__":
    mydevice = biodaq()
    opts = mydevice.getChoices()
    print("allowed Parameter values:")
    for x in opts:
        print(x, opts[x])
    # ports=mydevice.getDevices('mySerialNumber') #you may test the serialnumber, then you get the desired device
    ports = mydevice.getDevices()
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
    else:
        print("port sucessfully opened")
        print("device information string:", mydevice.sendCmd("*idn?"))
        print("SVN Version is:", mydevice.sendCmd("syst:vers:svn?"))
    print("close the port now")
    mydevice.close()
