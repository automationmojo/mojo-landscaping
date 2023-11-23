"""
.. module:: coordinatorbase
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains the CoordinatorBase which is the base object for coordinators to
               derive from and establishes patterns for coordinators which help to make
               them threadsafe.

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

from typing import List, Optional, TYPE_CHECKING

import threading
import weakref

from mojo.errors.exceptions import NotOverloadedError

from mojo.xmods.xthreading.lockscopes import LockedScope, UnLockedScope

from mojo.landscaping.landscapeparameters import LandscapeActivationParams
from mojo.landscaping.landscapedevice import LandscapeDevice

if TYPE_CHECKING:
    from mojo.landscaping.landscape import Landscape

class CoordinatorBase:
    """
        The CoordinatorBase utilizes the expected device declarations of type such as 'network/upnp' to establish and maintain
        connectivity and interoperability with a class of devices.  A derived coordinator will scan the medium such as a network
        for the devices declared in the landscape description.  The coordinator will also create the threads necessary to maintain
        communicates with the external devices over the medium.
    """

    def __init__(self, lscape: "Landscape", *args, coord_config=None, **kwargs):
        """
            Constructs an instance of a derived :class:`CoordinatorBase` object.

            :param lscape: The :class:`Landscape` singleton instance.
            :param *args: A pass through for other positional args.
            :param **kwargs: A pass through for the other keyword args.
        """

        self._lscape_ref = weakref.ref(lscape)
        self._coord_config = coord_config

        # If the landscape is in interactive mode, then all the coordinators should
        # default to using interactive mode
        self._interactive_mode = lscape.interactive_mode

        self._coord_lock = threading.RLock()

        self._cl_children = {}

        self._cl_expected_devices = []
        self._cl_found_devices = []
        self._cl_matched_devices = []
        self._cl_missing_devices = []

        return

    def activate(self, activation_params: LandscapeActivationParams):
        """
            Called by the :class:`LandscapeOperationalLayer` in order for the coordinator to be able to
            potentially enhanced devices.
        """
        raise NotOverloadedError("activate: must be overloaded by derived coordinator classes")


    def begin_locked_coordinator_scope(self) -> LockedScope:
        """
            Method that creates a locked scope for this device.
        """
        lkd_scope = LockedScope(self._coord_lock)
        return lkd_scope

    def begin_unlocked_coordinator_scope(self) -> UnLockedScope:
        """
            Method that creates an unlocked scope for this device.
        """
        unlkd_scope = UnLockedScope(self._coord_lock)
        return unlkd_scope

    def establish_connectivity(self, activation_params: LandscapeActivationParams):
        """
            Called by the :class:`LandscapeOperationalLayer` in order for the coordinator to be able to
            verify connectivity with devices.
        """
        raise NotOverloadedError("activate: must be overloaded by derived coordinator classes")

    @property
    def children(self) -> List[LandscapeDevice]:
        """
            Returns a list of the devices created by the coordinator and registered by the coordinator with the Landscape object.
        """
        chlist = []

        self._coord_lock.acquire()
        try:
            chlist = [c for c in self._cl_children.values()]
        finally:
            self._coord_lock.release()

        return chlist

    @property
    def coord_config(self):
        """
            The dedicated coordinator configuration for coordinators that have a dedicated
            configuration section in the landscape file.  Example: power, serial, wireless
        """

    @property
    def landscape(self) -> "Landscape":
        """
            Returns a hard reference to the Landscape singleton instance.
        """
        lscape = self._lscape_ref()
        return lscape

    @property
    def expected_devices(self):
        """
            The devices that were expected to be discovered by the coordinators discovery protocol.
        """
        return self._expected_devices

    @property
    def found_devices(self):
        """
            The devices that were dynamically discovery by the coordinators discovery protocol.
        """
        return self._found_devices

    @property
    def matched_devices(self):
        """
            The devices that the coordinator found during protocol discovery that matched corresponding
            expected devices.
        """
        return self._matched_devices

    @property
    def missing_devices(self):
        """
            The devices that the coordinator found to be missing during startup.
        """
        return self._missing_devices

    def establish_presence(self):
        """
            Implemented by derived coordinator classes to establish a specific presence in the
            landscape.
        """
        return

    def lookup_device_by_key(self, key) -> LandscapeDevice:
        """
            Looks up a device from the list of children by key in a thread safe way.
        """

        found = None

        self._coord_lock.acquire()
        try:
            if key in self._cl_children:
                found = self._cl_children[key].basedevice
        finally:
            self._coord_lock.release()

        return found

    def verify_connectivity(self, cmd: str = "echo 'It Works'", user: Optional[str] = None, raiseerror: bool = True):
        """
            Loops through the nodes in the coordinators pool in order to verify connectivity with the remote node.

            :param cmd: A command to run on the remote machine in order to verify that connectivity can be establish.
            :param user: The name of the user credentials to use for connectivity.
                         If the 'user' parameter is not provided, then the credentials
                         of the default or priviledged user will be used.
            :param raiseerror: A boolean value indicating if this API should raise an Exception on failure.

            :returns: A list of errors encountered when verifying connectivity with the devices managed or watched by the coordinator.
        """
        # pylint: disable=no-self-use
        raise NotOverloadedError("verify_connectivity: must be overloaded by derived coordinator classes")
