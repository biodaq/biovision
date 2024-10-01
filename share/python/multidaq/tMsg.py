# Copyright (c) 2022, Tantor GmbH
# All rights reserved.
# published under MIT license


import atexit
import ctypes
import os
import platform


class tMsgMaster:
    # ------------------------------------------------------------------------
    def __init__(self, dllPathName=""):
        self.slaveID = -1
        self.masterID = -1

        self.isDebug = False
        my_os = platform.system()
        if len(dllPathName) == 0:
            if my_os == "Linux":
                self.mydll = ctypes.CDLL("/usr/local/lib/libbiovisionMultiDaq.so")
            else:
                filna = os.getcwd() + "/biovisionMultiDaq.dll"
                self.mydll = ctypes.CDLL(filna)
                # self.mydll = ctypes.CDLL("c:\\bin\\biovisionMultiDaq.dll")
        else:
            if my_os == "Linux":
                self.mydll = ctypes.CDLL(dllPathName + "/libbiovisionMultiDaq.so")
            else:
                tt = dllPathName + "/biovisionMultiDaq.dll"
                print(tt)
                self.mydll = ctypes.CDLL(dllPathName + "/biovisionMultiDaq.dll")
        # int DLLCALL tMsgRegisterAsMaster(void);
        self.mydll.tMsgRegisterAsMaster.argtypes = None
        self.mydll.tMsgRegisterAsMaster.restype = ctypes.c_int
        # int DLLCALL tMsgUnregisterAsMaster(int);
        self.mydll.tMsgUnregisterAsMaster.argtypes = (ctypes.c_int,)
        self.mydll.tMsgUnregisterAsMaster.restype = ctypes.c_int
        # int DLLCALL tMsgSetMasterCallback(void (*pfunc)(char *data));
        self.mydll.tMsgSetMasterCallback.argtypes = (ctypes.c_void_p,)
        self.mydll.tMsgSetMasterCallback.restype = ctypes.c_int
        # int DLLCALL tMsgSendMsgToSlave(char *, int address);
        self.mydll.tMsgSendMsgToSlave.argtypes = (
            ctypes.c_char_p,
            ctypes.c_int,
        )
        self.mydll.tMsgSendMsgToSlave.restype = ctypes.c_int
        # int DLLCALL tMsgSendMsgToAllSlaves(char *);
        self.mydll.tMsgSendMsgToAllSlaves.argtypes = (ctypes.c_char_p,)
        self.mydll.tMsgSendMsgToAllSlaves.restype = ctypes.c_int
        # int DLLCALL tMsgGetSlaveMsg(char *, int address);
        self.mydll.tMsgGetSlaveMsg.argtypes = (
            ctypes.c_void_p,
            ctypes.c_int,
        )
        self.mydll.tMsgGetSlaveMsg.restype = ctypes.c_int
        # int DLLCALL tMsgGetTimeStamps(int64_t *, int address);
        # TODO
        self.mydll.tMsgGetTimeStamps.argtypes = (ctypes.c_int,)
        self.mydll.tMsgGetTimeStamps.restype = ctypes.c_int
        # int DLLCALL tMsgClearAllSlaveMessages();
        self.mydll.tMsgClearAllSlaveMessages.argtypes = None
        self.mydll.tMsgClearAllSlaveMessages.restype = ctypes.c_int
        self.mydll.multiDaqGetTicks.restype = ctypes.c_int64

        self.isConnected = False
        if self.register():
            self.isConnected = True
        atexit.register(self.cleanup)

    # ------------------------------------------------------------------------
    def cleanup(self):
        if self.isConnected:
            self.unregister()

    # ------------------------------------------------------------------------
    def register(self):
        if self.masterID < 0:
            self.masterID = self.mydll.tMsgRegisterAsMaster()
            if self.masterID < 0:
                return False
            self.mydll.tMsgInit()
            return True
        return False

    # ------------------------------------------------------------------------
    def unregister(self):
        if self.masterID >= 0:
            x = self.mydll.tMsgUnregisterAsMaster(self.masterID)
            self.masterID = -1
            if x >= 0:
                return True
        return False

    # ------------------------------------------------------------------------
    def sendMsgToSlave(self, slaveID, msg):
        tmp = str(msg).encode()
        if self.masterID >= 0:
            if self.mydll.tMsgSendMsgToSlave(tmp, slaveID) >= 0:
                return True
        return False

    # ------------------------------------------------------------------------
    def sendMsgToAllSlaves(self, msg):
        tmp = str(msg).encode()
        for i in range(4):
            if self.masterID >= 0:
                if self.mydll.tMsgSendMsgToSlave(tmp, i) >= 0:
                    pass
                    # print("successful send to slave id", i)
        return True

    # ------------------------------------------------------------------------
    def getMsg(self, ID):
        tmp = (ctypes.c_char * 256)()
        # return value is not tested
        self.mydll.tMsgGetSlaveMsg(
            ctypes.addressof(tmp),
            ctypes.c_int(ID),
        )
        tmp[255] = 0
        return tmp.value

    # ------------------------------------------------------------------------
    def setCallback(self, pfunc):
        if self.mydll.tMsgSetMasterCallback(pfunc) < 0:
            return False
        return True

    # ------------------------------------------------------------------------
    def getTicks(self):
        ans = self.mydll.multiDaqGetTicks()  # TODO its an in64!
        return ans


class tMsgSlave:
    # ------------------------------------------------------------------------
    def __init__(self, dllPathName=""):
        self.slaveID = -1
        self.masterID = -1

        self.isDebug = False
        my_os = platform.system()
        if len(dllPathName) == 0:
            if my_os == "Linux":
                self.mydll = ctypes.CDLL("/usr/local/lib/libbiovisionMultiDaq.so")
            else:
                filna = os.getcwd() + "/biovisionMultiDaq.dll"
                self.mydll = ctypes.CDLL(filna)
                # self.mydll = ctypes.CDLL("c:\\bin\\biovisionMultiDaq.dll")
        else:
            if my_os == "Linux":
                self.mydll = ctypes.CDLL(dllPathName + "/libbiovisionMultiDaq.so")
            else:
                tt = dllPathName + "/biovisionMultiDaq.dll"
                print(tt)
                self.mydll = ctypes.CDLL(dllPathName + "/biovisionMultiDaq.dll")
        self.mydll.multiDaqInit.argtypes = (ctypes.c_int,)
        self.mydll.multiDaqInit.restype = ctypes.c_int
        self.mydll.multiDaqDeInit.restype = ctypes.c_int
        # TODO remove int DLLCALL test();
        self.mydll.test.argtypes = None
        self.mydll.test.restype = ctypes.c_int
        # int DLLCALL tMsgRegisterAsSlave(void);
        self.mydll.tMsgRegisterAsSlave.argtypes = None
        self.mydll.tMsgRegisterAsSlave.restype = ctypes.c_int
        # int DLLCALL tMsgUnregisterAsMaster(int);
        self.mydll.tMsgUnregisterAsMaster.argtypes = (ctypes.c_int,)
        self.mydll.tMsgUnregisterAsMaster.restype = ctypes.c_int
        # int DLLCALL tMsgSetMasterCallback(void (*pfunc)(char *data));
        self.mydll.tMsgSetMasterCallback.argtypes = (ctypes.c_void_p,)
        self.mydll.tMsgSetMasterCallback.restype = ctypes.c_int

        # int DLLCALL tMsgGetMasterMsg(char *, int address);
        self.mydll.tMsgGetMasterMsg.argtypes = (
            ctypes.c_void_p,
            ctypes.c_int,
        )
        self.mydll.tMsgGetMasterMsg.restype = ctypes.c_int
        # int DLLCALL tMsgGetTimeStamps(int64_t *, int address);
        # TODO
        self.mydll.tMsgGetTimeStamps.argtypes = (ctypes.c_int,)
        self.mydll.tMsgGetTimeStamps.restype = ctypes.c_int
        # int DLLCALL tMsgClearAllSlaveMessages();
        self.mydll.tMsgClearAllSlaveMessages.argtypes = None
        self.mydll.tMsgClearAllSlaveMessages.restype = ctypes.c_int

        self.mydll.multiDaqGetTicks.restype = ctypes.c_int64

        if self.register():
            if self.slaveID < 0:
                print("Alert at register as slave")
        atexit.register(self.cleanup)

    # ------------------------------------------------------------------------
    def cleanup(self):
        if self.slaveID >= 0:
            self.unregister()

    # ------------------------------------------------------------------------
    def test(self):
        # TODO remove this function
        self.mydll.test()

    # ------------------------------------------------------------------------
    def register(self):
        if self.slaveID < 0:
            self.slaveID = self.mydll.tMsgRegisterAsSlave()
            if self.slaveID < 0:
                return False
            return True
        return False

    # ------------------------------------------------------------------------
    def unregister(self):
        if self.slaveID >= 0:
            self.mydll.tMsgUnregisterAsSlave(self.slaveID)
            return True
        return False

    # ------------------------------------------------------------------------
    def sendMsg(self, msg):
        tmp = str(msg).encode()
        if self.slaveID >= 0:
            # print("send to master:", msg)
            if self.mydll.tMsgSendMsgToMaster(tmp, self.slaveID) >= 0:
                return True
        return False

    # ------------------------------------------------------------------------
    def getMsg(self):
        tmp = (ctypes.c_char * 256)()
        ttt = ctypes.addressof(tmp)
        # return value not tested
        self.mydll.tMsgGetMasterMsg(ttt, self.slaveID)  # immer 0
        return tmp.value

    # ------------------------------------------------------------------------
    def setCallback(self, pfunc):
        if self.mydll.tMsgSetSlaveCallback(pfunc, self.slaveID) < 0:
            return False
        return True

    # ------------------------------------------------------------------------
    def getTicks(self):
        ans = self.mydll.multiDaqGetTicks()  # TODO its an in64!
        return ans


# ------------------------------------------------------------------------
if __name__ == "__main__":
    import time

    print("----------------- testarea -----------------")
    a = tMsgMaster("c:/bin")
    # b = tmsg_slave()

    # x2 = a.registerAsSlave()
    # print(x1, x2)
    for i in range(1):
        print("send", i)
        a.sendMsgToAllSlaves("name")
        time.sleep(0.2)
        print("getslave returned:", a.getMsg(0))
        print("getslave returned:", a.getMsg(1))
        print("getslave returned:", a.getMsg(2))
        print("getslave returned:", a.getMsg(3))
        time.sleep(1)
    a.sendMsgToAllSlaves("camera start")
    time.sleep(0.2)
    print("getslave(0) returned:", a.getMsg(0))
    print("getslave(1) returned:", a.getMsg(1))
    print("getslave(2) returned:", a.getMsg(2))
    print("getslave(3) returned:", a.getMsg(3))
    a.sendMsgToAllSlaves("camera stop")
    time.sleep(0.2)
    print("getslave returned:", a.getMsg(0))
    print("getslave returned:", a.getMsg(1))
    print("getslave returned:", a.getMsg(2))
    print("getslave returned:", a.getMsg(3))
    # print("Mastermeg:", a.getMasterMsg(0))
    exit(0)
