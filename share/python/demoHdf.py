# Copyright (c) 2024, Tantor GmbH
# All rights reserved.
# published under MIT license

import time

import numpy
from multidaq import hdf_stream, multiDaq


def demoHdf():
    dev = multiDaq()

    A = dev.listDevices()
    if len(A) == 0:
        print("No Device found: exit now")
        exit(1)
    if not dev.open(A[0]):
        print("open() failed: Device Busy? exit now")
        exit(1)
    print("device ", [A[0]], "is opened")

    # ------------------ configure the device ------------------------
    dev.clearConfig()
    if not dev.setSampleRate(1000):
        print("fatal: Could not set samplerate")
        exit(1)
    # mitigate error handling, it will cause error in configure()
    if A[0].startswith("bio"):  # has 32 bit ADC
        dev.addAdc32(1)
        dev.addAdc32(1)
    else:
        dev.setOversamplingAdc(1)  # 1 or 2 are valid
        dev.addAdc16(6)
        dev.addAdc16(6)
        # dev.addImu6(3, 250)
        # dev.addAux(2)
    # it is an good idea to set the outputlevel to a defined state
    if not dev.configure():  # last command before startSampling()
        print("Fatal: Config failed")
        exit(1)

    # ------------------ configure storage ---------------------------
    filna = "example.h5"
    storage = hdf_stream(debug=True)
    storage.open(
        filna
    )  # you may open a file with constructor hdf_stream(filename="example.h5")
    print("AdcOvs =", dev.overSamplingAdc)
    print("ranges(ADC) =", dev.rangesAdc)
    storage.addAdc(dev.sampleRate, dev.rangesAdc, ovs=dev.overSamplingAdc)
    storage.addImu6(dev.sampleRate, dev.rangesImu6)
    storage.addAux(dev.nAux)

    # ------------------- measurement loop ----------------------------
    dev.startSampling()
    nDesired = 1500
    nAct = 0
    while True:
        time.sleep(0.1)
        y = dev.getStreamingData()
        nAct += len(y)
        if nAct >= nDesired:
            toSave = len(y) - (nAct - nDesired)
            print("got enough:", toSave, "samples still to save")
            if toSave > 0:
                storage.write(y[0:toSave])
                print("leave loop, written last", toSave, "samples")
            break
        storage.write(y)
        print("nAct =", nAct, ", written:", y.shape)
    dev.stopSampling()

    # ------------------- tear down ------------------------------------
    storage.close()  # not neccessary: closes file, cleanup() will do it nevertheless
    dev.close()


if __name__ == "__main__":
    demoHdf()
