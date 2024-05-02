"""
.. module:: serialagentbase
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module contains the :class:`SerialAgentBase` object which is a base
               class for objects that allow for sending commands to a device via a
               serial interface.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>

"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []



from mojo.interfaces.isystemcontext import ISystemContext
from mojo.landscaping.protocolextension import ProtocolExtension

class SerialAgentBase(ProtocolExtension, ISystemContext):
    """
    """
    def __init__(self):
        ProtocolExtension.__init__(self)
        return
