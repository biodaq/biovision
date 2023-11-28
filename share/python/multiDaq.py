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

import ctypes

# from ctypes import byref
from sys import exit  # to keep pyinstaller happy

import numpy
import atexit
import platform
import time


class multiDaqLowLevel:
    # ------------------------------------------------------------------------
    def __init__(self, dllPathName=""):
        self.isDebug = False
        my_os = platform.system()
        if len(dllPathName) == 0:
            if my_os == "Linux":
                self.mydll = ctypes.CDLL("/usr/local/lib/libbiovisionMultiDaq.so")
            else:
                self.mydll = ctypes.CDLL("c:\\bin\\biovisionMultiDaq.dll")
        else:
            if my_os == "Linux":
                self.mydll = ctypes.CDLL(dllPathName + "/libbiovisionMultiDaq.so")
            else:
                self.mydll = ctypes.CDLL(dllPathName + "/biovisionMultiDaq.dll")
        self.masterID = -1
        self.mydll.multiDaqInit.argtypes = (ctypes.c_int,)
        self.mydll.multiDaqInit.restype = ctypes.c_int
        self.mydll.multiDaqDeInit.restype = ctypes.c_int
        self.mydll.multiDaqOpen.argtypes = (ctypes.c_int, ctypes.c_char_p)
        self.mydll.multiDaqOpen.restype = ctypes.c_int
        self.mydll.multiDaqClose.argtypes = (ctypes.c_int,)
        self.mydll.multiDaqClose.restype = ctypes.c_int

        self.mydll.multiDaqSetCallbackData.argtypes = (ctypes.c_int, ctypes.c_void_p)
        self.mydll.multiDaqSetCallbackData.restype = ctypes.c_int

        self.mydll.multiDaqGetSampleSize.argtypes = (ctypes.c_int,)
        self.mydll.multiDaqGetSampleSize.restype = ctypes.c_int
        self.mydll.multiDaqSendCmd.argtypes = (
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int),
        )
        self.mydll.multiDaqSendCmd.restype = ctypes.c_void_p
        self.mydll.multiDaqSendCmdWhileStreaming.argtypes = (
            ctypes.c_int,
            ctypes.c_char_p,
        )
        self.mydll.multiDaqSendCmdWhileStreaming.restype = ctypes.c_int

        # int DLLCALL multiDaqSendSCPIbinBlock(int dev, char *data, int len);
        self.mydll.multiDaqSendSCPIbinBlock.restype = ctypes.c_int
        self.mydll.multiDaqSendSCPIbinBlock.argtypes = (
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
        )
        # int DLLCALL multiDaqGetAdcOversampling(int dev);
        self.mydll.multiDaqGetAdcOversampling.restype = ctypes.c_int
        self.mydll.multiDaqGetAdcOversampling.argtypes = (ctypes.c_int,)

        # int DLLCALL multiDaqGetStreamingData(int dev, char *data,
        #                                      int minaligned, int maxSize);
        self.mydll.multiDaqGetStreamingData.restype = ctypes.c_int
        self.mydll.multiDaqGetStreamingData.argtypes = (
            ctypes.c_int,
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_int,
        )
        # void DLLCALL multiDaqClearSystemErrors(void); #TODO
        # char *DLLCALL multiDaqGetSystemErrors(void);
        self.mydll.multiDaqGetSystemErrors.restype = ctypes.c_char_p
        # int DLLCALL multiDaqDisableTx(void);
        self.mydll.multiDaqDisableTx.restype = ctypes.c_int
        # int DLLCALL multiDaqEnableTx(void);
        self.mydll.multiDaqEnableTx.restype = ctypes.c_int
        # int64_t DLLCALL multiDaqGetTicks(void);
        self.mydll.multiDaqGetTicks.restype = ctypes.c_int64
        # int DLLCALL multiDaqGetTimeStampsFromSynchronizedGroup(int dev,
        #                                                        int64_t *data);
        self.mydll.multiDaqGetTimeStampsFromSynchronizedGroup.restype = ctypes.c_int
        self.mydll.multiDaqGetTimeStampsFromSynchronizedGroup.argtypes = (
            ctypes.c_int,
            ctypes.c_void_p,
        )

        self.mydll.multiDaqGetSystemErrors.restype = ctypes.c_char_p
        self.mydll.multiDaqListDevices.restype = ctypes.c_char_p

        self.mydll.multiDaqGetLastError.restype = ctypes.c_char_p
        # const char *DLLCALL multiDaqGetVersion(void);
        self.mydll.multiDaqGetVersion.restype = ctypes.c_char_p
        self.mydll.multiDaqSendCmdWhileStreaming.restype = ctypes.c_int
        #    int DLLCALL registerAsMaster(void);
        # self.mydll.registerAsMaster.argtypes = (ctypes.c_int,)
        self.mydll.tMsgInit.restype = ctypes.c_int
        self.mydll.tMsgRegisterAsMaster.restype = ctypes.c_int
        #    int DLLCALL registerAsSlave(void);
        # self.mydll.registerAsSlave.argtypes = (ctypes.c_int,)
        self.mydll.tMsgRegisterAsSlave.restype = ctypes.c_int
        #    int DLLCALL unregisterAsMaster(int);
        self.mydll.tMsgUnregisterAsMaster.argtypes = (ctypes.c_int,)
        self.mydll.tMsgUnregisterAsMaster.restype = ctypes.c_int
        #    int DLLCALL unregisterAsSlave(int);
        self.mydll.tMsgUnregisterAsSlave.argtypes = (ctypes.c_int,)
        self.mydll.tMsgUnregisterAsSlave.restype = ctypes.c_int
        #    int DLLCALL sendMsgToSlave(char *, int address);
        self.mydll.tMsgSendMsgToSlave.argtypes = (
            ctypes.c_char_p,
            ctypes.c_int,
        )
        self.mydll.tMsgSendMsgToSlave.restype = ctypes.c_int
        #    int DLLCALL tMsgSendMsgToAllSlaves(char *in)
        self.mydll.tMsgSendMsgToAllSlaves.argtypes = (ctypes.c_char_p,)
        self.mydll.tMsgSendMsgToSlave.restype = ctypes.c_int
        #    int DLLCALL sendMsgToMaster(char *, int address);
        self.mydll.tMsgSendMsgToMaster.argtypes = (
            ctypes.c_char_p,
            ctypes.c_int,
        )
        self.mydll.tMsgSendMsgToMaster.restype = ctypes.c_int
        #    int DLLCALL getMasterMsg(char *, int address);
        self.mydll.tMsgGetMasterMsg.argtypes = (ctypes.c_char_p, ctypes.c_int)
        self.mydll.tMsgGetMasterMsg.restype = ctypes.c_int
        #    int DLLCALL getSlaveMsg(char *, int address);
        self.mydll.tMsgGetSlaveMsg.argtypes = (ctypes.c_void_p, ctypes.c_int)
        self.mydll.tMsgGetSlaveMsg.restype = ctypes.c_int
        self.mydll.tMsgGetTimeStamps.restype = ctypes.c_int
        self.mydll.tMsgGetTimeStamps.argtypes = (
            ctypes.c_void_p,
            ctypes.c_int,
        )

        self.scratch_c = (ctypes.c_int16 * 256000)()  # c buffer to receive samples
        self.scratch_ts = (ctypes.c_int64 * 16)()  # c buffer to receive timestamps
        ans = self.tMsgInit()
        if ans != 0:
            print("class multiDaq(): warning tMsgSystem not available")
        ans = self.mydll.multiDaqInit(0)  # 1 means output debug messages
        if ans != 0:
            try:
                # raise ValueError('Represents a hidden bug, do not catch this')
                raise Exception("class multiDaq(): could not initialize the driver")
            except Exception as error:
                print("Caught this error: " + repr(error))
        atexit.register(self.cleanup)

    # ------------------------------------------------------------------------
    def cleanup(self):
        if self.isDebug:
            print("multiDaqLowLevel(): Running cleanup")
        # self.mydll.sendCmd("abort\n*rst", True, True)
        ans = self.mydll.multiDaqDeInit()
        if ans != 0:
            print("multiDaqLowLevel(): fatal Error in cleanup, deinit failed", ans)

    # ------------------------------------------------------------------------
    def setDebugFlag(self, flag):
        self.isDebug = flag

    # ------------------------------------------------------------------------
    def listDevices(self):
        ans = self.mydll.multiDaqListDevices()
        if len(ans) == 0:
            return []
        ans = ans.decode()
        ans = ans.split("\n")
        while "" in ans:
            ans.remove("")
        if self.isDebug:
            print("listDevices():", ans)
        return ans

    # ------------------------------------------------------------------------
    def open(self, dev, devId):
        if self.mydll.multiDaqOpen(dev, ctypes.c_char_p(devId.encode())) == 0:
            return True
        if self.isDebug:
            print("open() failed, dev =", dev)
        return False

    # ------------------------------------------------------------------------
    def close(self, dev):
        if self.mydll.multiDaqClose(dev) == 0:
            return True
        return False

    # ------------------------------------------------------------------------
    def setDataCallback(self, dev, callbackfunction):
        self.mydll.multiDaqSetCallbackData(dev, callbackfunction)
        return True

    # ------------------------------------------------------------------------
    def checkSystemErrors(self):
        ans = self.mydll.multiDaqGetSystemErrors()
        return ans

    # ------------------------------------------------------------------------
    def getLastErrorMsg(self, dev):
        ans = self.mydll.multiDaqGetLastError(dev)
        return ans

    # ------------------------------------------------------------------------
    def getMultiTimeStamps(self, dev):
        # tmp = (ctypes.c_int64 * 4)()
        ans = self.mydll.multiDaqGetTimeStampsFromSynchronizedGroup(
            ctypes.c_int(dev),
            ctypes.addressof(self.scratch_ts),
        )
        if ans != 0:
            return False
        if self.isDebug:
            print("getTimeStamps(): returns", self.scratch_ts)
        return self.scratch_ts

    # ------------------------------------------------------------------------
    def getMsgTimeStamps(self, dev):
        if not type(dev) is int:
            raise TypeError("only integers are allowed")
        # tmp = (ctypes.c_int64 * 4)()

        ans = self.mydll.tMsgGetTimeStamps(
            ctypes.addressof(self.scratch_ts),
            ctypes.c_int(dev),
        )
        # ans = int(-1)
        print("ans", ans)
        ups = numpy.ctypeslib.as_array(self.scratch_ts[0 : int(4)], ctypes.c_int64)
        print("ups", ups)
        print("diffs", ups[1] - ups[0], ups[2] - ups[0], ups[3] - ups[0])

        return ups

    # ------------------------------------------------------------------------
    def getTicks(self):
        ans = self.mydll.multiDaqGetTicks()  # TODO its an in64!
        return ans

    # ------------------------------------------------------------------------
    def tMsgInit(self):
        ans = self.mydll.tMsgInit()
        return ans

    # ------------------------------------------------------------------------
    def getVersion(self):
        ans = self.mydll.multiDaqGetVersion()
        return ans

    # ------------------------------------------------------------------------
    def enableTx(self):
        if self.mydll.multiDaqEnableTx() == 0:
            return True
        return False

    # ------------------------------------------------------------------------
    def disableTx(self):
        if self.mydll.multiDaqDisableTx() == 0:
            if self.isDebug:
                print("disableTx(): success")
            return True
        if self.isDebug:
            print("disableTx(): failed")
        return False

    # ------------------------------------------------------------------------
    def registerAsMaster(self):
        self.masterID = self.mydll.tMsgRegisterAsMaster()
        print("masterID =", self.masterID)

    # ------------------------------------------------------------------------
    def unregisterAsMaster(self):
        self.mydll.tMsgUnregisterAsMaster(self.masterID)

    # ------------------------------------------------------------------------
    def sendMsgToSlave(self, dev, msg):
        msg = str(msg).encode()
        b = ctypes.c_int()
        if self.isDebug:
            print("sendMsg2Slave():", msg)
        b = self.mydll.tMsgSendMsgToSlave(msg, dev)
        if b < 0:
            return False
        else:
            return True

    # ------------------------------------------------------------------------
    def getMsgFromSlave(self, dev):
        tmp = (ctypes.c_char * 256)()
        ans = self.mydll.tMsgGetSlaveMsg(
            ctypes.addressof(tmp),
            ctypes.c_int(dev),
        )
        if ans != 0:
            # print("ppppp")
            return False
        ans = numpy.ctypeslib.as_array(tmp[0:256], ctypes.c_char)
        if self.isDebug:
            print("gotfromSlave():", ans)
        return ans

    # ------------------------------------------------------------------------
    def sendMsgToAllSlaves(self, msg):
        msg = str(msg).encode()
        if self.isDebug:
            print("sendMsg2Slave():", msg)
        return self.mydll.tMsgSendMsgToAllSlaves(msg)

    # ------------------------------------------------------------------------
    def getMsgResponseCmd(self, dev, cmd, timeout=1):
        # print("test(", dev, ")", cmd)
        ans = self.sendMsgToSlave(dev, cmd)
        if not ans:
            print("send failed")
            return False
        xCnt = 0
        t0 = time.time()
        while True:
            ans = self.getMsgFromSlave(dev)
            if not ans:
                xCnt = xCnt + 1
                continue
            else:
                break
            if time.time() - t0 > timeout:
                print("Message timeouted")
                return b""
        # print("Cnt=", xCnt)
        return ans

    # ------------------------------------------------------------------------
    def sendCmd(self, dev, cmd, isStreaming=False):
        # TODO if cmd contains ?
        # it is neccessary that it returns answerlen !=0, handle that
        cmd = str(cmd).encode()
        a = ctypes.c_int()
        b = ctypes.c_int()
        if self.isDebug:
            print("sendCmd():", cmd, "isStreaming =", isStreaming)
        if isStreaming:
            ans = self.mydll.multiDaqSendCmdWhileStreaming(dev, cmd)
            if ans < 0:
                raise Exception(
                    "class multiDaq(): multiDaqSendCmdWhileStreaming() failed"
                )
            return ans  # it is an integer
        else:
            ans = self.mydll.multiDaqSendCmd(dev, cmd, ctypes.byref(a), ctypes.byref(b))
            if ans == ctypes.c_char_p(0):
                raise Exception("class multiDaq(): multiDaqSendCmd() failed")
            if b.value != ctypes.c_int(0).value:
                if self.isDebug:
                    print("sendCmd(): is binary response, len =", a)
                arr_c = (ctypes.c_byte * a.value)()
                ctypes.memmove(arr_c, ans, a.value)
                # ttt = bytes(arr_c)  # it is an byte array
            else:
                arr_c = (ctypes.c_byte * a.value)()
                ctypes.memmove(arr_c, ans, a.value)
                tmp = bytes(arr_c).decode()
                if self.isDebug:
                    if len(tmp) > 0:
                        print("sendCmd() has response:", tmp.rstrip())
            return tmp.rstrip()

    # ------------------------------------------------------------------------
    def getStreamingData(self, dev):
        sampleSize = self.mydll.multiDaqGetSampleSize(
            ctypes.c_int(dev),
        )
        # print("got sampleSize =", sampleSize)
        nBytes = self.mydll.multiDaqGetStreamingData(
            ctypes.c_int(dev),
            ctypes.addressof(self.scratch_c),
            sampleSize,  # int(2 * self.numChannels),
            self.scratch_c._length_,
        )
        if self.isDebug:
            print(
                "getStreamingData(): received bytes =",
                nBytes,
                "samplesize =",
                sampleSize,
            )
        if nBytes < 0:
            if self.isDebug:
                print("Error in getStreamingData: (-2 means timeouted)", nBytes)
            return False
        ups = numpy.ctypeslib.as_array(
            self.scratch_c[0 : int(nBytes / 2)], ctypes.c_int16
        )
        ups = ups.reshape((int(nBytes / int(sampleSize)), int(sampleSize / 2)))
        pups = ups.astype(float)
        # TODO scaling
        return pups


class multiDaq:
    # ------------------------------------------------------------------------
    def __init__(self, devNum=0, dllPathName=""):
        self.devID = devNum
        self.LL = multiDaqLowLevel(dllPathName)
        # self.LL.setDebugFlag(True)
        self.rangesAdc32 = []
        self.rangesAdc16 = []
        self.rangesImu6 = []
        self.cfgInfo = (0, 0, 0)
        print("Init complete")

    # ------------------------------------------------------------------------
    def cleanup(self):
        print("Cleanup")

    # ------------------------------------------------------------------------
    def listDevices(self):
        return self.LL.listDevices()

    # ------------------------------------------------------------------------
    def open(self, idString, doTest=False):
        ret = self.LL.open(self.devID, idString)
        if not ret:
            return False
        if doTest:
            print("IDN Response:", self.LL.sendCmd(self.devID, "*idn?"))
            print("conf:sca:num? tells:", self.LL.sendCmd(self.devID, "conf:sca:num?"))
        return True

    # ------------------------------------------------------------------------
    def close(self):
        return self.LL.close(self.devID)

    # ------------------------------------------------------------------------
    def addAdc16(self, range):
        if range != 6:
            return False
        if len(self.rangesAdc16) >= 7:
            return False
        self.rangesAdc16.append(range)
        return True

    # ------------------------------------------------------------------------
    def addImu6(self, rangeAcc, rangeGyro):
        ans = self.LL.sendCmd(self.devID, "conf:sca:num?")
        dings = ans.split(",")
        cc = []
        for xx in dings:
            cc.append(int(xx))
        if len(cc) < 3:
            return False
        if self.cfgInfo[2] + 1 > cc[2]:
            return False
        self.rangesImu6.append((rangeAcc, rangeGyro))
        return True

    # ------------------------------------------------------------------------
    def clearConfig(self):
        self.rangesAdc16 = []
        self.rangesImu6 = []
        self.cfgInfo = (0, 0, 0)

    # ------------------------------------------------------------------------
    def setSampleRate(self, sr):
        if len(self.LL.sendCmd(self.devID, "conf:sca:rat " + str(sr))):
            return False
        return True

    # ------------------------------------------------------------------------
    def configure(self):
        nImu6 = len(self.rangesImu6)
        nAdc16 = len(self.rangesAdc16)
        self.scale = (1 / 32768) * numpy.ones((1, nImu6 * 6 + nAdc16))
        cnt = 0
        for i in range(nAdc16):
            self.scale[0, cnt] *= self.rangesAdc16[i]
            cnt += 1
        for i in range(nImu6):
            x = self.rangesImu6[i]
            self.scale[0, cnt] *= x[0]
            self.scale[0, cnt + 1] *= x[0]
            self.scale[0, cnt + 2] *= x[0]
            self.scale[0, cnt + 3] *= x[1]
            self.scale[0, cnt + 4] *= x[1]
            self.scale[0, cnt + 5] *= x[1]
            cnt += 6
        cmd = "conf:dev 0,%d,%d" % (nAdc16, nImu6)
        if len(self.LL.sendCmd(self.devID, cmd)):
            print("Config failed")
            return False
        self.cfgInfo = (0, nAdc16, nImu6)
        time.sleep(0.3)
        return True

    # ------------------------------------------------------------------------
    def startSampling(self):
        self.LL.sendCmd(self.devID, "init", True)

    # ------------------------------------------------------------------------
    def stopSampling(self):
        self.LL.sendCmd(self.devID, "abort", True)
        return True

    # ------------------------------------------------------------------------
    def enableTx(self):
        self.LL.enableTx()
        return True

    # ------------------------------------------------------------------------
    def disableTx(self):
        self.LL.disableTx()
        return True

    # ------------------------------------------------------------------------
    def getStreamingData(self):
        A = self.LL.getStreamingData(self.devID)
        # TODO scale
        for i in range(self.scale.size):
            A[:, i] *= self.scale[0, i]
        return A

    # ------------------------------------------------------------------------
    def getVersionInfo(self):
        return self.LL.getVersion()
