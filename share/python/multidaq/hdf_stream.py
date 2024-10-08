# Copyright (c) 2024, Tantor GmbH
# All rights reserved.
# pubished under MIT license
import atexit
import time

import h5py
import numpy


class hdf_stream:
    # ------------------------------------------------------------------------
    def __init__(self, filename="", debug=False, compression="gzip"):
        """
        init
        """
        self.isDebug = debug
        self.compression = compression
        atexit.register(self.cleanup)
        if self.isDebug:
            print("[hdf_stream] cleanup() registered")
        self.isOpened = False
        if len(filename):
            self.open(filename)
        self.adc = None
        self.imu6 = None
        self.aux = None
        self.nAdc = 0
        self.ovsAdc = 1
        self.nImu6 = 0
        self.nAux = 0
        self.nTotal = 0
        self.actSample = 0

    # ------------------------------------------------------------------------
    def cleanup(self):
        """
        internal function
        """
        if self.isDebug:
            print("[hdf_stream] cleanup()")
        if self.isOpened:
            print("[hdf_stream] close file")
            self.fp.close()

    # ------------------------------------------------------------------------
    def open(self, filna):
        """
        internal function
        """
        if self.isDebug:
            print("[hdf_stream] open(", filna, ")")
        if not self.isOpened:
            self.fp = h5py.File(filna, "w")
            self.isOpened = True
            self.fp.attrs["description"] = b"biovision data file"
            self.fp.attrs["creator"] = b"python script"
            self.fp.attrs["timestamp"] = str(int(time.time())).encode(encoding="ascii")
        else:
            print("error")

    # ------------------------------------------------------------------------
    def close(self):
        """
        internal function
        """
        if self.isDebug:
            print("[hdf_stream] close()")
        if self.isOpened:
            self.fp.close()
            self.isOpened = False

    # ------------------------------------------------------------------------
    def addAdc(self, samplerate, ranges, names=None, ovs=1):
        """
        add Adc to stream
        """
        if not self.isOpened:
            return False
        if self.isDebug:
            print(
                "[hdf_stream] addAdc(): sr =",
                samplerate,
                " ranges =",
                ranges,
                " len =",
                len(ranges),
                " names =",
                names,
                " ovs =",
                ovs,
            )
        if len(ranges) < 1:
            if self.isDebug:
                print("[hdf_stream] Warning, no Adc channels configured")
            return False
        self.fp.create_dataset(
            "/adc/fSample",
            (1),
            dtype=numpy.float64,
            data=samplerate * ovs,
        )
        self.fp.create_dataset(
            "/adc/ranges",
            (len(ranges)),
            dtype=numpy.float64,
            data=ranges,
        )
        self.nAdc = len(ranges)
        self.adc = self.fp.create_dataset(
            "/adc/values",
            (0, len(ranges)),
            maxshape=(None, self.nAdc),
            compression=self.compression,
            dtype=numpy.float32,
        )
        self.adc.attrs["unit"] = b"Volt"
        self.adc.attrs["oversamplingFactor"] = int(ovs)
        if type(names) != type(None):
            if len(names) == len(ranges):
                self.adc.attrs["names"] = names
            else:
                if self.isDebug:
                    print("[hdf_stream] Warning, no names for ADCs stored in file")
        self.nTotal += self.nAdc * ovs
        self.ovsAdc = ovs
        return True

    # ------------------------------------------------------------------------
    def addImu6(self, samplerate, ranges, names=None):
        """
        add Imu6 to stream
        """
        if not self.isOpened:
            return False
        if self.isDebug:
            print("[hdf_stream] addImu6(): sr =", samplerate, " ranges =", ranges)
        if len(ranges) < 1:
            if self.isDebug:
                print("[hdf_stream] Warning, no Imu6 channels configured")
            return False

        self.fp.create_dataset(
            "/imu6/fSample",
            (1),
            dtype=numpy.float64,
            data=samplerate,
        )
        self.fp.create_dataset(
            "/imu6/ranges",
            (len(ranges), 2),
            dtype=numpy.float64,
            data=ranges,
        )
        self.nImu6 = len(ranges)
        # print("nImu =", self.nImu6)
        self.imu6 = self.fp.create_dataset(
            "/imu6/values",
            (0, len(ranges), 6),
            maxshape=(None, self.nImu6, 6),
            compression=self.compression,
            dtype=numpy.float32,
        )
        self.nTotal += self.nImu6 * 6
        self.imu6.attrs["units"] = [b"g", b"grad/s"]
        if type(names) != type(None):
            if len(names) == len(ranges):
                self.imu6.attrs["names"] = names
            else:
                if self.isDebug:
                    print("[hdf_stream] Warning, no names for ADCs stored in file")
        return True

    # ------------------------------------------------------------------------
    def addAux(self, n, name=None):
        """
        add Aux to stream
        """
        if not self.isOpened:
            return False
        if self.isDebug:
            print("[hdf_stream] addAux(): n =", n)
        if n < 1:
            if self.isDebug:
                print("[hdf_stream] warning, nAux = 0")
            return False
        self.nAux = int(n)
        self.nTotal += self.nAux
        self.aux = self.fp.create_dataset(
            "/aux/values",
            (0, n),
            maxshape=(None, self.nAux),
            compression=self.compression,
            dtype=numpy.int16,
        )
        if type(name) != type(str):
            self.aux.attrs["name"] = name
        else:
            if self.isDebug:
                print("[hdf_stream] warning, no name for aucx stored")
        return True

    # ------------------------------------------------------------------------
    def write(self, y):
        """
        write data to file (all streams)
        input is output from multidaq.getStreamingData()
        """
        if not self.isOpened:
            return False
        if self.isDebug:
            print(
                "[hdf_stream] write(): n =",
                len(y),
                "shape =",
                y.shape,
                "nAdc =",
                self.nAdc,
                "ovsAdc",
                self.ovsAdc,
                "nImu6 =",
                self.nImu6,
                "nAux =",
                self.nAux,
            )
        if self.nTotal != self.nAdc * self.ovsAdc + self.nImu6 * 6 + self.nAux:
            if self.isDebug:
                print("error1", self.nTotal)
                print(self.ovsAdc)
            return False
        ns = y.shape[0]
        if self.nTotal != y.shape[1]:
            if self.isDebug:
                print("error2")
            return False
        start = 0
        if self.nAdc > 0:
            ovs = self.ovsAdc
            self.adc.resize(((ns + self.actSample) * self.ovsAdc, self.nAdc))
            for i in range(ovs):
                self.adc[
                    self.actSample * ovs + i : self.actSample * ovs + ovs * ns : ovs
                ] = y[0:ns, start : start + self.nAdc]
                start += self.nAdc
        if self.nImu6 > 0:
            self.imu6.resize((ns + self.actSample, self.nImu6, 6))
            for i in range(self.nImu6):
                self.imu6[self.actSample : self.actSample + ns, i, 0:6] = y[
                    0:ns, start : start + 6
                ]
                start += 6
        if self.nAux > 0:
            self.aux.resize((ns + self.actSample, self.nAux))
            self.aux[self.actSample : self.actSample + ns, 0 : self.nAux] = y[
                0:ns, start : start + self.nAux
            ]
        self.actSample += ns
        return True
