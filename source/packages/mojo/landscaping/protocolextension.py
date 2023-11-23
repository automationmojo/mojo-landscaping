"""
.. module:: landscapeprotocolextension
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`ProtocolExtension` class which is used
               to attached protocol agents and interop capability to a :class:`LandscapeDevice`
               or :class:`LandscapeService`.

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

from typing import Dict, Union, TYPE_CHECKING

import logging
import weakref

if TYPE_CHECKING:
    from mojo.landscaping.coordinators.coordinatorbase import CoordinatorBase
    from mojo.landscaping.landscapedevice import LandscapeDevice
    from mojo.landscaping.landscapeservice import LandscapeService

class ProtocolExtension:
    """
        The :class:`ProtocolExtension` object is the base class object that allows for the
        extension of functionality for a :class:`LandscapeDevice` or :class:`LandscapeService`.  The 
        :class:`ProtocolExtension` is used by the UPnP, SSH and Other coordinators to extend landscape
        devices with metadata and device connectivity for the UPnp, SSH and Other protocols.
    """

    logger = logging.getLogger()

    def __init__(self):
        """
            Constructor use to create an instance of and to initialize a :class:`ProtocolExtension`.
        """
        self._coord_ref = None
        self._extends_ref = None
        self._configinfo = None
        self._extid = None
        self._location = None

        return

    @property
    def extends(self) -> Union["LandscapeDevice", "LandscapeService"]:
        """
            Returns a reference to the base :class:`LandscapeDevice` or :class:`LandscapeService` that this extension id attached to.
        """
        dev = None
        if self._extends_ref is not None:
            dev = self._extends_ref()
        return dev

    @property
    def coordinator(self) -> "CoordinatorBase":
        """
            Returns a reference to the coordinator that created the :class:`LandscapeDevice`.
        """
        coord = None
        if self._coord_ref is not None:
            coord = self._coord_ref()
        return coord

    @property
    def configuration(self) -> Dict[str, Union[str, dict]]:
        """
            The protocol specific configuration infor for the device.
        """
        return self._configinfo

    @property
    def extid(self) -> str:
        """
            A unique device identifier created by the coordinator for this device extension.  The identier is
            typically something associated with the protocol.
        """
        return self._extid

    @property
    def location(self) -> str:
        """
            A network location the device extension is referenced to.
        """
        return self._location

    def initialize(self, coord_ref: weakref.ReferenceType, extends_ref: weakref.ReferenceType,
                   extid: str, location: str, configinfo: dict) -> None:
        """
            Initializes the landscape device extension.
        """
        self._coord_ref = coord_ref
        self._extends_ref = extends_ref
        self._extid = extid
        self._location = location
        self._configinfo = configinfo
        return

    def update_extends_ref(self, extends_ref: weakref.ref) -> None:
        """
            Used by derived Landscape classes to update the reference to the base device if the base landscape
            device is swapped out to provide enhanced device functionality.
        """
        self._extends_ref = extends_ref
        return
