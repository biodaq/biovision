import ctypes

# from ctypes import byref
from sys import exit  # to keep pyinstaller happy

import numpy
import atexit
import platform
import time


class multiDaq:
    # ------------------------------------------------------------------------
    def __init__(self, dllFullName=""):

        self.isDebug = False
        my_os = platform.system()
        if len(dllFullName) == 0:
            if my_os == "Linux":
                self.mydll = ctypes.CDLL("/usr/local/lib/libbiovisionMultiDaq.so")
            else:
                self.mydll = ctypes.CDLL(
                    "c:\\Program Files\\biovision\\multidaq\\biovisionMultiDaq.dll"
                )
        else:
            self.mydll = ctypes.CDLL(dllFullName)
        self.masterID = -1
        self.mydll.multiDaqInit.argtypes = (ctypes.c_int,)
        self.mydll.multiDaqInit.restype = ctypes.c_int
        self.mydll.multiDaqDeInit.restype = ctypes.c_int
        self.mydll.multiDaqOpen.argtypes = (ctypes.c_int, ctypes.c_char_p)
        self.mydll.multiDaqOpen.restype = ctypes.c_int
        self.mydll.multiDaqClose.argtypes = (ctypes.c_int,)
        self.mydll.multiDaqClose.restype = ctypes.c_int
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

        # int DLLCALL multiDaqGetStreamingData(int dev, char *data, int minaligned, int maxSize);
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
        # int DLLCALL multiDaqGetTimeStampsFromSynchronizedGroup(int dev, int64_t *data);
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
        ans = self.mydll.multiDaqInit(0)  # 1 means output debug messages via stdout
        if ans != 0:
            try:
                # raise ValueError('Represents a hidden bug, do not catch this')
                raise Exception("class multiDaq(): could not initialize the driver")
            except Exception as error:
                print("Caught this error: " + repr(error))
        atexit.register(self.cleanup)

    # ------------------------------------------------------------------------
    def cleanup(self):
        # print("daq_imu_udp: Running cleanup")
        # self.mydll.sendCmd("abort\n*rst", True, True)
        ans = self.mydll.multiDaqDeInit()
        if ans != 0:
            print("cleanup: deinit failed", ans)

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
        print("####")
        self.masterID = self.mydll.tMsgRegisterAsMaster()
        print("masterID =", self.masterID)

    # ------------------------------------------------------------------------
    def unregisterAsMaster(self):
        # TODO if cmd contains ? it is neccessary that it returns answerlen !=0, handle that
        self.mydll.tMsgUnregisterAsMaster(self.masterID)

    # ------------------------------------------------------------------------
    def sendMsgToSlave(self, dev, msg):
        # TODO if cmd contains ? it is neccessary that it returns answerlen !=0, handle that
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
        # TODO if cmd contains ? it is neccessary that it returns answerlen !=0, handle that
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
        # TODO if cmd contains ? it is neccessary that it returns answerlen !=0, handle that
        msg = str(msg).encode()
        if self.isDebug:
            print("sendMsg2Slave():", msg)
        return self.mydll.tMsgSendMsgToAllSlaves(msg)

    # ------------------------------------------------------------------------
    def getMsgResponseCmd(self, dev, cmd):
        # print("test(", dev, ")", cmd)
        ans = self.sendMsgToSlave(dev, cmd)
        if not ans:
            print("send failed")
            return False
        xCnt = 0
        while True:
            ans = self.getMsgFromSlave(dev)
            if not ans:
                xCnt = xCnt + 1
                continue
            else:
                break
        # print("Cnt=", xCnt)
        return ans

    # ------------------------------------------------------------------------
    def sendCmd(self, dev, cmd, isStreaming=False):
        # TODO if cmd contains ? it is neccessary that it returns answerlen !=0, handle that
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
            ans = self.mydll.multiDaqSendCmd(dev, cmd, byref(a), byref(b))
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


if __name__ == "__main__":

    if platform.system() == "Linux":
        try:
            mydriver = multiDaq("/usr/local/lib/libbiovisionMultiDaq.so")
        except Exception:
            print("Could not start driver")
            exit(1)
    else:
        try:
            mydriver = multiDaq(
                "c:\\projects\\multiDaq\\multiDaq\\build-windows\\multiDaq\\biovisionMultiDaq.dll"
            )
        except Exception:
            print("Could not start driver")
            exit(1)
    print("DLL loaded successfully")
    # uncomment next line, if you want to see what happens inside
    # mydriver.setDebugFlag(True)

    ans = mydriver.getVersion()
    print("reported Driver Version:", ans)
    # mydriver.sendMsgToAllSlaves("hallo")

    # uncomment next block for test of tMsg system, (driver and (linux only)) msgConsumerTest must run
    """time.sleep(0.1)
    print("register now")
    mydriver.registerAsMaster()
    print("registered")

    ans = mydriver.getMsgResponseCmd(0, "name")
    time.sleep(0.01)
    ans = mydriver.getMsgResponseCmd(0, "camera start")
    t0 = time.time()
    for i in range(10000):
        ans = mydriver.getMsgResponseCmd(0, "camera stop")
    print("10000 rounds took:", time.time() - t0)
    time.sleep(0.1)
    mydriver.unregisterAsMaster()
    exit(0)"""
    devs = mydriver.listDevices()
    if len(devs) == 0:
        print("no device found, exit now")
        exit(1)
    if len(devs) > 1:
        print("warning: more than one device found")
        print(devs)
        print("I will use the first")
    mydevID = devs[0]
    mydev = int(0)
    # mydriver.test(mydev)
    if not mydriver.open(mydev, mydevID):
        print("Error Open device")
        exit(1)
    ans = mydriver.sendCmd(mydev, "*idn?")
    print("response to identification command:", ans)
    ans = mydriver.sendCmd(mydev, "syst:vers:svn?")
    print("build Version of device Firmware:", ans)
    mydriver.sendCmd(mydev, "conf:sca:rat 1000")
    mydriver.sendCmd(mydev, "conf:sca:ove 1")
    # mydriver.sendCmd(mydev, "conf:sca:lis 1,1,1")

    ans = mydriver.sendCmd(mydev, "conf:dev 0,3,0")
    if len(ans) > 0:
        print("Configuration of device failed: ", ans)
        mydriver.close(mydev)
        exit(1)
    time.sleep(0.1)
    ans = mydriver.sendCmd(mydev, "init", True)
    time.sleep(1)
    erg = mydriver.getStreamingData(mydev)
    print("------------ results follows:")
    print(erg)
    ans = mydriver.sendCmd(mydev, "abort", True)
    if not mydriver.close(mydev):
        print("Error Close device")
        exit(1)
    exit(0)
