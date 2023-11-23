"""
.. module:: poweragentbase
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module contains the :class:`PowerAgentBase` object which is a base
               class for object that allow for controlling the power of devices.

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

from typing import Union

from mojo.errors.exceptions import ConfigurationError

from mojo.landscaping.protocolextension import ProtocolExtension

class PowerAgentBase(ProtocolExtension):
    """
    """
    def __init__(self):
        ProtocolExtension.__init__(self)
        return

    def _lookup_power_interface(self, interface_name: str) -> Union[dict, None]:
        """
            Looks up a power interface by power interface name.
        """
        power_iface = None

        if interface_name in self._power_interfaces:
            power_iface = self._power_interfaces[interface_name]
        else:
            lscape = self.coordinator.landscape

            interface_config = self._power_config[interface_name]
            
            powerType = interface_config["powerType"]

            if powerType == "DliPowerSwitch":
                model = interface_config["model"]
                host = interface_config["host"]

                credential_name = interface_config["credential"]
                credobj = lscape.lookup_credential(credential_name)

                power_iface = dlipower.PowerSwitch(userid=credobj.username, password=credobj.password, hostname=host)

                self._power_interfaces[interface_name] = power_iface
            else:
                errmsg = "Un-Support power interface type={}.".format(powerType)
                raise ConfigurationError(errmsg) from None

        return power_iface
