"""
.. module:: constants
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the constants associated with automation landscaping.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>

"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []


from enum import Enum, IntEnum

class DeviceExtensionType(str, Enum):
    SSH = "extension/ssh"
    UPNP = "extension/upnp"
    REST = "extension/rest"

class StartupLevel(IntEnum):
    Power = 10000
    Serial = 20000
    SecondaryProtocol = 30000
    PrimaryProtocol = 40000
