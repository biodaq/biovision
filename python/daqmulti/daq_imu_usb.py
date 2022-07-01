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
# from os import times_result
import struct, time, socket
import serial.tools.list_ports  # For listing available serial ports
import serial  # For serial communication, they are in pyserial

# import numpy as np
import atexit
from threading import Timer
import queue


class daq_imu_usb:
    # ------------------------------------------------------------------------
    def __init__(self):
        # print("daq_imu_usb: constructor()")
        self.ser = ""
        self.isStreaming = False
        self.stopTimer = False
        self.streamError = False
        self.streamErrReason = ""
        self.isOpen = False
        self.streamQ = queue.Queue()
        self.CommandRespose = b""
        atexit.register(self.cleanup)

    # ------------------------------------------------------------------------
    def cleanup(self):
        # print("daq_imu_usb: Running cleanup...")
        if self.isOpen == False:
            return
        self.sendCmd("abort\n*rst", True, True)
        time.sleep(0.5)
        anz = self.ser.inWaiting()
        ans = self.ser.read(anz)
        self.ser.close()

    # ------------------------------------------------------------------------
    def errStatus(self):
        return self.error

    # ------------------------------------------------------------------------
    def clear(self):
        self.chans = []
        self.gains = []
        self.sampleRate = 100

    # ------------------------------------------------------------------------
    def setSampleRate(self, dr):
        self.sampleRate = dr

    # ------------------------------------------------------------------------
    def getDevices(self, checksn=""):
        # print("daq_imu_usb: getDevices()")
        a = serial.tools.list_ports.comports()
        ports = []
        for w in a:
            # print('found %s  vid=%d pid=%d sn=%s'%(w.name,w.vid,w.pid,w.serial_number))
            if (
                (w.vid == 1155 and w.pid == 22336)
                or (w.vid == 6790 and w.pid == 29987)
                or (w.vid == 0x10C4 and w.pid == 0xEA60)
            ):
                sn = str(w.serial_number).lower()
                if sn.startswith("g") or sn.startswith("h"):
                    ports.append(w)  # (w.vid, w.device, w.serial_number))
        return ports

    # ------------------------------------------------------------------------
    def open(self, input):
        # print("daq_imu_usb: open()")
        try:
            self.ser = serial.Serial(
                port=input.device,
                baudrate=500000,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=0.3,
            )
            # print("daq_imu_usb: open(): connected to: " + self.ser.portstr)
            # self.ser.set_buffer_size(rx_size = 200000, tx_size = 100000)
            self.isOpen = True
            return True
        except serial.SerialException as e:
            print("serial throwed Exception:", e)
            return False
        return True

    # ------------------------------------------------------------------------
    def close(self):
        self.sendCmd("abort", False, True)  # safety: force abort streaming
        time.sleep(0.15)
        self.ser.flushInput()
        self.ser.close()
        self.isOpen = False

    # ------------------------------------------------------------------------
    def read(self, anz):  # this is blocking read
        ans = self.ser.read(anz)
        return ans

    # ------------------------------------------------------------------------
    def read_all(self):
        anz = self.ser.inWaiting()
        ans = self.ser.read(anz)
        return ans

    # ------------------------------------------------------------------------
    def sendRaw(self, input):  # only use this, if you know, what you do
        ans = self.ser.write(input)
        return ans

    # ------------------------------------------------------------------------
    def readbinblock(self):  # this is blocking read
        a = self.ser.read(1)
        # except:
        # return b''
        if len(a) == 0:
            # self.error = True
            self.streamErrReason = "#1"
            return b""
        if a == b"*":  # errormessage instead of streaming data
            self.streamErrReason = "*"
            return b""
        if a == b"#":
            a = self.ser.read(1)
            if len(a) == 0:
                # self.error = True
                self.streamErrReason = "#2"
                return b""
            n = int(a)
            a = self.ser.read(n)
            if len(a) != n:
                # self.error = True
                self.streamErrReason = "#3"
                return b""
            n = int(a)
            # print(n)
            retwert = self.ser.read(n)
            if len(retwert) != n:
                # self.error = True
                self.streamErrReason = "#4"
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
                    # self.error = True
                    self.streamErrReason = "#5"
                    return b""
            else:
                # self.error = True
                self.streamErrReason = "#6"
                # print("a=",a,"avail",self.ser.inWaiting())
                return b""
        print("a", a)
        return b""

    # ------------------------------------------------------------------------
    def timer_irq(self):
        # print("timer_irq(): tick",time.time())
        if self.ser.in_waiting > 5:
            ans = self.readbinblock()  # blocks until complete
            if len(ans) > 0:
                self.streamQ.put(ans)
            else:
                print("daq_imu_usb: Streamerror, Failed init?")
                # time.sleep(50)
                tmp = self.read_all()
                print("daq_imu_usb: got Errormsg:", str(tmp))
                self.streamErrReason += str(tmp)
                self.streamError = True
        if self.isStreaming == True:
            thread = Timer(0.02, self.timer_irq)
            thread.start()

    # ------------------------------------------------------------------------
    def getStreamingData(self):
        y = []
        while self.streamQ.qsize() > 0:
            y.append(self.streamQ.get())
        return y

    # ------------------------------------------------------------------------
    def sendCmd(self, input, expectResponse=True, ignoreResponse=False):
        # print("daq_imu_usb: sendCmd()",input)
        if input.endswith("\n") == False:
            input += "\n"
        self.CommandResponse = b""
        if input.startswith("init"):
            self.streamQ.queue.clear()
            if self.isStreaming == False:
                self.thread = Timer(0.02, self.timer_irq)
                self.thread.start()
            self.isStreaming = True
        if input.startswith("abort"):
            self.isStreaming = False
        self.ser.write(input.encode())
        if ignoreResponse == True:  #
            return b""
        cmdResp = b""
        if self.isStreaming == True:
            print(
                "daq_imu_usb: Error, Device is streaming, serialport doesnt allow sending Commands in this state"
            )
            exit(1)
        if expectResponse == True:
            for i in range(10):
                time.sleep(0.1)
                cmdResp = cmdResp + self.read_all()
                if len(cmdResp) > 0:
                    # ans = self.CommandResponse
                    if cmdResp.endswith(b"\r\n"):
                        cmdResp = cmdResp[:-2]
                        return cmdResp
                    elif cmdResp.endswith(b"\n"):
                        cmdResp = cmdResp[:-1]
                        return cmdResp
                    return ""
            print("daq_imu_usb: warning sendCmd(): Missed expected answer on command")
            return b""
        time.sleep(1)
        ans = cmdResp
        if ans.endswith(b"\r\n"):
            ans = ans[:-2]
        elif ans.endswith(b"\n"):
            ans = ans[:-1]
        return ans


# ------------------------------------------------------------------------
if __name__ == "__main__":
    mydevice = daq_imu_usb()
    # ports=mydevice.getDevices('mySerialNumber') #you may filter the serialnumber, then you get the desired device
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
        exit(1)
    else:
        print("port sucessfully opened")
        mydevice.sendCmd("abort", True)
        time.sleep(0.5)
        mydevice.read_all()
        print("device information string:", mydevice.sendCmd("*idn?"))
        print("SVN Version is:", mydevice.sendCmd("syst:vers:svn?"))
        # print("errcheck", mydevice.sendCmd("conf:sca:rat 1000\nconf:sca:hea 1"))
        # print("errcheck", mydevice.sendCmd("conf:imu:para 0,3,125"))
    ans = mydevice.sendCmd("conf:scan:rat 100", False)
    ans += mydevice.sendCmd(
        "conf:imu:para 0,2,250"
    )  # 0,2,250: channel rangeacc rangegyro
    if len(ans):
        print("Configuration failed errmsg =", ans)
        exit(1)
    ans = mydevice.sendCmd("conf:scan:num?", False)

    print("ans =", ans)
    mydevice.sendCmd("init 0,0,1", True)
    for i in range(10):
        ll = mydevice.readbinblock()
        # print("read blocklen",len(ll))
        y = mydevice.decodeChans(ll)
    print("last Block:\n", y)
    mydevice.sendCmd("abort", True)
    while True:
        print("read extra block")
        ll = mydevice.readbinblock()
        if len(ll) == 0:
            break
    print("close the port now")
    mydevice.close()
