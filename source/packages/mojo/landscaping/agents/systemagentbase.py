
"""
.. module:: commandagentbase
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module contains the :class:`CommandAgentBase` object which is a base
               class for object that allow running commands via some protocol interface.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>

"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []
__version__ = "1.0.0"
__maintainer__ = "Myron Walker"
__email__ = "myron.walker@gmail.com"
__status__ = "Development" # Prototype, Development or Production
__license__ = "MIT"

from mojo.interfaces.isystemcontext import ISystemContext
from mojo.landscaping.protocolextension import ProtocolExtension

class SystemAgentBase(ProtocolExtension, ISystemContext):
    """
    """
    def __init__(self):
        ProtocolExtension.__init__(self)
        return