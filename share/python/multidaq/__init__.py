"""
python interface for biovision digitizers
Classes:
    multiDaqLowLevel()
    multiDaq()
    tMsgSlave()
    tMsgMaster()
"""
# flake8: noqa F401,F403
minDllVersion = "1.2.0.0"
__version__ = "1.0.2"

from .multidaq import *
from .hdf_stream import *
from .tMsg import *
