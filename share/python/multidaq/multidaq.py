# Copyright (c) 2022, Tantor GmbH
# All rights reserved.
# license: MIT

import atexit
import ctypes
import os
import platform
import sys
import time

import numpy

# import multidaq_biodaq

# from ctypes import byref


class multiDaqLowLevel:
    # ------------------------------------------------------------------------
    def __init__(self, dllPathName="", debug=False):
        """
        init
        called automaticly
        """
        self.isPackage = True
        self.isDebug = debug
        self.hasAdc32 = False
        my_os = platform.system()
        if len(dllPathName) == 0:
            if my_os == "Linux":
                dirr = os.path.dirname(sys.modules["multidaq"].__file__)
                filna = os.path.join(dirr, "libbiovisionMultiDaq.so")
                self.mydll = ctypes.CDLL(filna)
            else:
                dir = os.path.dirname(sys.modules["multidaq"].__file__)
                filna = os.path.join(dir, "biovisionMultiDaq.dll")
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
        self.mydll.multiDaqListAllDevices.restype = ctypes.c_char_p

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
                print("multiDaqLowLevel() caught this error: " + repr(error))
        atexit.register(self.cleanup)

    # ------------------------------------------------------------------------
    def cleanup(self):
        """
        internal function
        cleanup graphics and multiDaq()
        """
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
        """
        flag: bool value True/False
        if set, driver will printout some messages
        """
        self.isDebug = flag

    # ------------------------------------------------------------------------
    def listDevices(self, listForeign=False):
        """
        list all devices on USB
        this function is accessible before the init command
        """
        if listForeign:
            ans = self.mydll.multiDaqListAllDevices()
        else:
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
        """
        open a device
        dev handle as a number from 0 to 3
        devID might be a member of the list of listDevices()
        """
        if devId.startswith("bio"):
            if self.isDebug:
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
        """
        close Device
        """
        if self.mydll.multiDaqClose(dev) == 0:
            return True
        return False

    # ------------------------------------------------------------------------
    def setDataCallback(self, dev, callbackfunction):
        """
        set a callback function for new data arrived
        """
        self.mydll.multiDaqSetCallbackData(dev, callbackfunction)
        return True

    # ------------------------------------------------------------------------
    def checkSystemErrors(self):
        """
        checks internal system errors
        like buffer overflow e.g.
        returns string
        """
        ans = self.mydll.multiDaqGetSystemErrors()
        return ans

    # ------------------------------------------------------------------------
    def getLastErrorMsg(self, dev):
        """
        returns string with last error message
        """
        ans = self.mydll.multiDaqGetLastError(dev)
        return ans

    # ------------------------------------------------------------------------
    def getMultiTimeStamps(self, dev):
        """
        debugging function
        returns array of 4 64 bit timestamps
        """
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
        """
        return 10 MHz timestamps for debugging
        returns array of 4 64 bit timestamps
        """
        if not type(dev) is int:
            raise TypeError("only integers are allowed")
        # tmp = (ctypes.c_int64 * 4)()

        self.mydll.tMsgGetTimeStamps(
            ctypes.addressof(self.scratch_ts),
            ctypes.c_int(dev),
        )
        # ans = int(-1)
        ups = numpy.ctypeslib.as_array(self.scratch_ts[0 : int(4)], ctypes.c_int64)
        return ups

    # ------------------------------------------------------------------------
    def getTicks(self):
        """
        utility function
        gets 10 MHz ticks as a 64 bit value
        no need for init() before
        """
        ans = self.mydll.multiDaqGetTicks()  # TODO its an in64!
        return ans

    # ------------------------------------------------------------------------
    def getVersion(self):
        """
        return string with version information
        """
        ans = self.mydll.multiDaqGetVersion()
        return ans

    # ------------------------------------------------------------------------
    def enableTx(self):
        """
        enables transmission of commands to all devices
        """
        if self.mydll.multiDaqEnableTx() == 0:
            return True
        return False

    # ------------------------------------------------------------------------
    def disableTx(self):
        """
        disables transmission of commands to all devices
        be careful
        """
        if self.mydll.multiDaqDisableTx() == 0:
            if self.isDebug:
                print("disableTx(): success")
            return True
        if self.isDebug:
            print("disableTx(): failed")
        return False

    # ------------------------------------------------------------------------
    def sendCmd(self, dev, cmd, isStreaming=False):
        """
        send Command
        dev: integer from 0..3
        cmd: string with command to send
        in streaming mode isStreaming must be set to True
        """
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
        """
        returns numpy array with measured data
        """
        sampleSize = self.mydll.multiDaqGetSampleSize(
            ctypes.c_int(dev),
        )
        if sampleSize == 0:
            if self.isDebug:
                print("Error multiDaq(): device is not configured properly")
            return False
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


# ****************************************************************************
class multiDaq:
    # ------------------------------------------------------------------------
    def __init__(self, devNum=0, dllPathName="", debug=False):
        """
        init
        """
        self.isDebug = debug
        self.devID = devNum
        self.LL = multiDaqLowLevel(dllPathName, debug=debug)
        self.clearConfig()
        self.configError = False
        self.hasAdc32 = False
        self.nAux = 0
        self.nAdc = 0
        self.nImu6 = 0
        self.sampleRate = -1
        self.overSamplingAdc = int(1)
        # self.LL.setDebugFlag(True)

    # ------------------------------------------------------------------------
    def cleanup(self):
        """
        internal function
        cleanup graphics and multiDaq()
        """
        pass

    # ------------------------------------------------------------------------
    def listDevices(self, listForeign=False):
        """
        return list of detected devices on USB
        """
        return self.LL.listDevices(listForeign)

    # ------------------------------------------------------------------------
    def open(self, idString, doTest=False):
        """
        open Device
        idString = a valid element of the output of listDevices()
        """
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
        """
        close Device
        """
        return self.LL.close(self.devID)

    # ------------------------------------------------------------------------
    def addAdc16(self, myrange=6):
        """
        add a 16 bit ADC channel to configuration list
        """
        if self.hasAdc32:
            return False
        if myrange != 6:
            self.configError = True
            return False
        if len(self.rangesAdc) > 7:
            self.configError = True
            return False
        self.rangesAdc.append(myrange)
        return True

    # ------------------------------------------------------------------------
    def addAdc32(self, amplification=1):
        """
        add a 32 bit ADC channel to configuration list
        """
        if not self.hasAdc32:
            if self.isDebug:
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
        self.rangesAdc.append(2.4 / amplification)
        return True

    # ------------------------------------------------------------------------
    def addImu6(self, rangeAcc, rangeGyro):
        """
        add a 6 axis IMU sensor to configuration list
        """
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
        if len(
            self.LL.sendCmd(
                self.devID,
                "conf:imu:para "
                + str(len(self.rangesImu6))
                + ","
                + str(rangeAcc)
                + ","
                + str(rangeGyro),
            )
        ):
            self.configError = True
            return False
        self.rangesImu6.append((rangeAcc, rangeGyro))

        return True

    # ------------------------------------------------------------------------
    def addAux(self, nchan):
        """
        add an aux device with nchan channels
        """
        ans = self.LL.sendCmd(self.devID, "conf:sca:num?")
        dings = ans.split(",")
        cc = []
        for xx in dings:
            cc.append(int(xx))
        if len(cc) < 4 or self.nAux != 0:
            self.configError = True
            return False
        if nchan > cc[3]:
            self.configError = True
            return False
        self.nAux = nchan
        return True

    # ------------------------------------------------------------------------
    def clearConfig(self):
        """
        clear configuration list
        """
        self.preampAdc32 = []
        self.rangesAdc = []
        self.rangesImu6 = []
        self.cfgInfo = (0, 0, 0)
        self.configError = False
        self.overSamplingAdc = int(1)

    # ------------------------------------------------------------------------
    def setSampleRate(self, sr):
        """
        set Sample rate
        sr: samplerate (possible values depend on device)
        """
        if len(self.LL.sendCmd(self.devID, "conf:sca:rat " + str(sr))):
            self.configError = True
            return False
        self.sampleRate = sr
        return True

    # ------------------------------------------------------------------------
    def setOversamplingAdc(self, ovs):
        """
        set Oversampling of Adc
        ovs: oversampling Faktor
        """
        if self.hasAdc32:
            if ovs == 1:
                return True
            self.configError = True
            return False
        else:
            if len(self.LL.sendCmd(self.devID, "conf:sca:ove " + str(int(ovs)))):
                self.configError = True
                return False
        self.overSamplingAdc = int(ovs)
        return True

    # ------------------------------------------------------------------------
    def configure(self):
        """
        configurate device
        configuration list must be valid
        """
        nImu6 = len(self.rangesImu6)
        nAdc16 = len(self.rangesAdc)
        nAdc32 = len(self.preampAdc32)
        self.nAdc = len(self.rangesAdc)
        if self.hasAdc32:
            nAdc16 = 0
        else:
            nAdc32 = 0
        # if nAdc32 > 0:
        #    nAdc16 = 0
        if self.configError:
            if self.isDebug:
                print("Configuration Error")
            return False
        if self.hasAdc32:
            self.scale = (2.4 / (32768.0 * 65536.0)) * numpy.ones((1, nAdc32))
        else:
            self.scale = (1 / 32768) * numpy.ones(
                (1, nImu6 * 6 + nAdc16 * self.overSamplingAdc)
            )
        cnt = 0
        if self.hasAdc32:
            for i in range(self.nAdc):
                self.scale[0, cnt] /= self.preampAdc32[i]
                cnt += 1
        else:
            for i in range(self.nAdc):
                for k in range(self.overSamplingAdc):
                    self.scale[0, cnt + k] *= self.rangesAdc[i]
                cnt += self.overSamplingAdc
        for i in range(nImu6):
            x = self.rangesImu6[i]
            self.scale[0, cnt] *= x[0]
            self.scale[0, cnt + 1] *= x[0]
            self.scale[0, cnt + 2] *= x[0]
            self.scale[0, cnt + 3] *= x[1]
            self.scale[0, cnt + 4] *= x[1]
            self.scale[0, cnt + 5] *= x[1]
            cnt += 6
        if self.hasAdc32 == False and nAdc16 > 0:
            cmd = ""
            cnt = 0
            for x in self.rangesAdc:
                cmd += "conf:sca:gai " + str(cnt) + "," + str(x) + "\n"
                cnt += 1
            if len(self.LL.sendCmd(self.devID, cmd)):
                if self.isDebug:
                    print("Config Range Adc16 failed")
                return False
        if self.hasAdc32 and nAdc32 > 0:
            cmd = ""
            cnt = 0
            for x in self.preampAdc32:
                cmd += "conf:sca:gai " + str(cnt) + "," + str(x) + "\n"
                cnt += 1
            if len(self.LL.sendCmd(self.devID, cmd)):
                if self.isDebug:
                    print("Config Gain failed")
                return False
        if self.nAux > 0:
            cmd = "conf:dev %d,%d,%d,%d" % (nAdc32, nAdc16, nImu6, self.nAux)
        else:
            cmd = "conf:dev %d,%d,%d" % (nAdc32, nAdc16, nImu6)
        if self.isDebug:
            print(cmd)
        if len(self.LL.sendCmd(self.devID, cmd)):
            if self.isDebug:
                print("Config failed")
            return False
        self.cfgInfo = (0, nAdc16, nImu6)
        time.sleep(0.3)
        return True

    # ------------------------------------------------------------------------
    def startSampling(self):
        """
        start streaming mode
        """
        if self.configError:
            if self.isDebug:
                print("Could not start Sampling: cause Config Error")
                print("Exit now")
            sys.exit(1)
            return False
        self.LL.sendCmd(self.devID, "init", True)
        return True

    # ------------------------------------------------------------------------
    def stopSampling(self):
        """
        stop streaming mode
        """
        self.LL.sendCmd(self.devID, "abort", True)
        return True

    # ------------------------------------------------------------------------
    def enableTx(self):
        """
        enable transmission of commands to all devices
        """
        self.LL.enableTx()
        return True

    # ------------------------------------------------------------------------
    def disableTx(self):
        """
        disable transmission of commands to all devices
        """
        self.LL.disableTx()
        return True

    # ------------------------------------------------------------------------
    def setTrigger(self, val):
        """
        depends on mode (integer 0,1 or bool)
            'level': set output to high/Low
            'pulse': output polarity of output pulse
            'schmitt': no effect
        """
        if int(val) == 1:
            val = True
        if int(val) == 0:
            val = False
        if val:
            cmd = "trig:set 1"
        else:
            cmd = "trig:set 0"
        self.LL.sendCmd(self.devID, cmd, True)
        return True

    # ------------------------------------------------------------------------
    def configureTrigger(self, mod="level", arg1="", arg2="2000", arg3="-2000"):
        """
        configures trigger mode
        mod = 'level', 'pulse' or 'schmitt'
        argx depend on mod
        'pulse': arg1 is impulse length in samples
        'schmitt': arg1 channel number for input of schmitt trigger
                   arg2 level switch to high (16 bit integer)
                   arg3 level switch to low  (16 bit integer)
        """
        if not (mod == "level" or mod == "pulse" or mod == "schmitt"):
            return False
        if mod == "schmitt":
            if int(arg1) < 0 or int(arg1) > 7:
                return False
            cmd = (
                "conf:trig:mode "
                + mod
                + ","
                + str(arg1)
                + ","
                + str(arg2)
                + ","
                + str(arg3)
            )
        if mod == "level":
            cmd = "conf:trig:mode level"
        if mod == "pulse":
            cmd = "conf:trig:mode pulse"
            if int(arg1) < 1:
                return False
            cmd += "," + str(arg1)

        ans = self.LL.sendCmd(self.devID, cmd)
        if len(ans) > 0:
            return False
        return True

    # ------------------------------------------------------------------------
    def getStreamingData(self):
        """
        returns numpy array with actual data since last call
        """
        tmp = self.LL.getStreamingData(self.devID)
        A = tmp.astype(float)
        # print("Oversampling", self.overSamplingAdc)
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
        """
        get Version information
        """
        return self.LL.getVersion()
