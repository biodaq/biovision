"""
python interface for biovision digitizers
Classes:
    multiDaqLowLevel()
    multiDaq()
    tMsgSlave()
    tMsgMaster()
"""

# flake8: noqa F401,F403

__version__ = "0.0.6"

minDllVersion = "1.2.0.0"

from .hdf_stream import *
from .multidaq import *
from .tMsg import *
