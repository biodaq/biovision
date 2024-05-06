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

import atexit
import ctypes
import os
import platform
import sys
import time

import numpy

# from ctypes import byref


class multiDaqLowLevel:
    # ------------------------------------------------------------------------
    def __init__(self, dllPathName="", debug=False):
        self.isDebug = debug
        self.hasAdc32 = False
        my_os = platform.system()
        print("dllpath", dllPathName)
        if len(dllPathName) == 0:
            if my_os == "Linux":
                self.mydll = ctypes.CDLL("/usr/local/lib/libbiovisionMultiDaq.so")
            else:
                os.add_dll_directory(os.getcwd())
                filna = os.getcwd() + "\\biovisionMultiDaq.dll"
                print("dllpath", filna)
                self.mydll = ctypes.CDLL(filna, winmode=0)
        else:
            if my_os == "Linux":
                self.mydll = ctypes.CDLL(dllPathName + "/libbiovisionMultiDaq.so")
            else:
                self.mydll = ctypes.CDLL(
                    dllPathName + "/biovisionMultiDaq.dll", winmode=0
                )
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

        self.mydll.sdl2Window.argtypes = (
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
        )
        self.mydll.sdl2Window.restype = ctypes.c_int

        self.mydll.sdl2WindowConfigure.argtypes = (
            ctypes.c_int,
            ctypes.c_int,
        )
        self.mydll.sdl2WindowConfigure.restype = ctypes.c_int

        # void function: self.mydll.sdl2KillWindow.argtypes = ctypes.c_void
        self.mydll.sdl2KillWindow.restype = ctypes.c_int

        self.scratch_c = (ctypes.c_int16 * 256000)()  # c buffer to receive samples
        self.scratch_c32 = ctypes.cast(self.scratch_c, ctypes.POINTER(ctypes.c_int32))
        self.scratch_ts = (ctypes.c_int64 * 16)()  # c buffer to receive timestamps
        self.isGraphicOpen = False
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
        if self.isDebug and ans != 0:
            print("multiDaqLowLevel(): fatal Error in cleanup, deinit failed", ans)
        if self.isGraphicOpen:
            self.mydll.killSdl2Window()

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
        print("LL open", devId)
        if devId.startswith("bio"):
            print("LL detected ADC32")
            self.hasAdc32 = True
        else:
            self.hasAdc32 = False
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
        print("samplesize", sampleSize)
        if sampleSize == 0:
            print("Error multiDaq(): device is not configured properly")
            return False
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
            if nBytes == -2:  # that is timeout
                nBytes = 0
            else:  # severe error
                return False
        if self.hasAdc32:
            dat16 = numpy.ctypeslib.as_array(self.scratch_c32[0 : int(nBytes / 4)])
            dat16 = dat16.reshape((int(nBytes / int(sampleSize)), int(sampleSize / 4)))
        else:
            dat16 = numpy.ctypeslib.as_array(self.scratch_c[0 : int(nBytes / 2)])
            dat16 = dat16.reshape((int(nBytes / int(sampleSize)), int(sampleSize / 2)))
        # ret = dat16.astype(float)
        return dat16

    # ------------------------------------------------------------------------
    def configGraph(self, posx, posy, width, height):
        self.mydll.sdl2Window(int(posx), int(posy), int(width), int(height))
        self.mydll.sdl2WindowConfigure(0, 10000)

    # ------------------------------------------------------------------------
    def killGraph(self):
        self.mydll.sdl2KillWindow()


class multiDaq:
    # ------------------------------------------------------------------------
    def __init__(self, devNum=0, dllPathName=""):
        self.devID = devNum
        self.LL = multiDaqLowLevel(dllPathName)
        self.clearConfig()
        self.configError = False
        self.hasAdc32 = False
        # self.LL.setDebugFlag(True)

    # ------------------------------------------------------------------------
    def cleanup(self):
        pass

    # ------------------------------------------------------------------------
    def listDevices(self):
        return self.LL.listDevices()

    # ------------------------------------------------------------------------
    def open(self, idString, doTest=False):
        ret = self.LL.open(self.devID, idString)
        if idString.startswith("bio"):
            self.hasAdc32 = True
        else:
            self.hasAdc32 = False
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
    def addAdc16(self, range=6):
        if self.hasAdc32:
            return False
        if range != 6:
            self.configError = True
            return False
        if len(self.rangesAdc16) > 7:
            self.configError = True
            return False
        self.rangesAdc16.append(range)
        return True

    # ------------------------------------------------------------------------
    def addAdc32(self, amplification=1):
        if not self.hasAdc32:
            print("has no ADC32")
            return False
        if (
            amplification != 1
            and amplification != 2
            and amplification != 4
            and amplification != 8
            and amplification != 12
        ):
            self.configError = True
            return False
        if len(self.preampAdc32) > 7:
            self.configError = True
            return False
        self.preampAdc32.append(amplification)
        return True

    # ------------------------------------------------------------------------
    def addImu6(self, rangeAcc, rangeGyro):
        ans = self.LL.sendCmd(self.devID, "conf:sca:num?")
        dings = ans.split(",")
        cc = []
        for xx in dings:
            cc.append(int(xx))
        if len(cc) < 3:
            self.configError = True
            return False
        if self.cfgInfo[2] + 1 > cc[2]:
            self.configError = True
            return False
        self.rangesImu6.append((rangeAcc, rangeGyro))
        return True

    # ------------------------------------------------------------------------
    def clearConfig(self):
        self.preampAdc32 = []
        self.rangesAdc16 = []
        self.rangesImu6 = []
        self.cfgInfo = (0, 0, 0)
        self.configError = False

    # ------------------------------------------------------------------------
    def setSampleRate(self, sr):
        if len(self.LL.sendCmd(self.devID, "conf:sca:rat " + str(sr))):
            self.configError = True
            return False
        return True

    # ------------------------------------------------------------------------
    def configure(self):
        nImu6 = len(self.rangesImu6)
        nAdc16 = len(self.rangesAdc16)
        nAdc32 = len(self.preampAdc32)
        if self.hasAdc32:
            self.scale = (2.4 / (32768.0 * 65536.0)) * numpy.ones((1, nAdc32))
        else:
            self.scale = (1 / 32768) * numpy.ones((1, nImu6 * 6 + nAdc16))
        cnt = 0
        for i in range(nAdc32):
            self.scale[0, cnt] /= self.preampAdc32[i]
            print("scal", self.scale[0, cnt])
            cnt += 1
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
        if nAdc16 > 0:
            cmd = ""
            cnt = 0
            for x in self.rangesAdc16:
                cmd += "conf:sca:gai " + str(cnt) + "," + str(x) + "\n"
                cnt += 1
            print(cmd)
            if len(self.LL.sendCmd(self.devID, cmd)):
                print("Config Range Adc16 failed")
                return False
        if nAdc32 > 0:
            cmd = ""
            cnt = 0
            for x in self.preampAdc32:
                cmd += "conf:sca:gai " + str(cnt) + "," + str(x) + "\n"
                cnt += 1
            if len(self.LL.sendCmd(self.devID, cmd)):
                print("Config Gain failed")
                return False
        cmd = "conf:dev %d,%d,%d" % (nAdc32, nAdc16, nImu6)
        print(cmd)
        if len(self.LL.sendCmd(self.devID, cmd)):
            print("Config failed")
            return False
        self.cfgInfo = (0, nAdc16, nImu6)
        time.sleep(0.3)
        return True

    # ------------------------------------------------------------------------
    def startSampling(self):
        if self.configError:
            print("Could not start Sampling: cause Config Error")
            print("Exit now")
            sys.exit(1)
            return False
        self.LL.sendCmd(self.devID, "init", True)
        return True

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
    def setTrigger(self, val):
        if int(val) == 1:
            val = True
        if int(val) == 0:
            val = False
        if val:
            cmd = "trig:set 1"
        else:
            cmd = "trig:set 0"
        print(cmd)
        self.LL.sendCmd(self.devID, cmd, True)
        return True

    # ------------------------------------------------------------------------
    def configureTrigger(self, lev="level", arg1="", arg2="2000", arg3="-2000"):
        print("configureTrigger()", lev, arg1, arg2)
        if not (lev == "level" or lev == "pulse" or lev == "schmitt"):
            print("shit")
            return False
        if lev == "schmitt":
            print("schmitt")
            if int(arg1) < 0 or int(arg1) > 7:
                print(
                    "configureTrigger(): arg1 (chan Number)  must be from 0 to 7 in mode schmitt"
                )
                return False
            cmd = (
                "conf:trig:mode "
                + lev
                + ","
                + str(arg1)
                + ","
                + str(arg2)
                + ","
                + str(arg3)
            )
        if lev == "level":
            print("Level")
            cmd = "conf:trig:mode level"
        if lev == "pulse":
            print("Pulse")
            cmd = "conf:trig:mode pulse"
            if int(arg1) < 1:
                print("Err")
                return False
            cmd += "," + str(arg1)
            print(cmd)

        ans = self.LL.sendCmd(self.devID, cmd)
        print("Ans", ans)
        if len(ans) > 0:
            print("what")
            return False
        return True

    # ------------------------------------------------------------------------
    def getStreamingData(self):
        tmp = self.LL.getStreamingData(self.devID)
        A = tmp.astype(float)

        offs = 0
        if self.hasAdc32:
            offs = 1
        for i in range(self.scale.size):
            A[:, i + offs] *= self.scale[0, i]
        if self.hasAdc32:
            return A[:, 1 : self.scale.size + 1]
        return A

    # ------------------------------------------------------------------------
    def getVersionInfo(self):
        return self.LL.getVersion()
