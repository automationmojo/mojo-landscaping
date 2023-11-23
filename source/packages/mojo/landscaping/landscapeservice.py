"""
.. module:: landscapeservice
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`LandscapeService` class.

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

from typing import Callable, Dict, Union, TYPE_CHECKING

import logging
import os
import threading
import weakref

from datetime import datetime

from mojo.errors.exceptions import SemanticError

from mojo.credentials.basecredential import BaseCredential
from mojo.credentials.sshcredential import SshCredential
from mojo.landscaping.friendlyidentifier import FriendlyIdentifier
from mojo.landscaping.protocolextension import ProtocolExtension
from mojo.xmods.xfeature import FeatureAttachedObject
from mojo.xmods.xthreading.lockscopes import LockedScope, UnLockedScope

if TYPE_CHECKING:
    from mojo.landscaping.landscape import Landscape
    from mojo.landscaping.coordinators.coordinatorbase import CoordinatorBase

class LandscapeService(FeatureAttachedObject):
    """
        The base class for all landscape services.  The :class:`LandscapeService' represents attributes that are common
        to all services that might be present in a test landscape.   mechanisms for adding ServiceExtentions to
        the :class:`LandscapeService` device.
    """

    # Base landscape devices don't have any feature tags, but we want all devices to have feature
    # tag capability so we can filter all devices based on feature tags, whether they have
    # tags or not.
    FEATURE_TAGS = []

    logger = logging.getLogger()

    def __init__(self, lscape: "Landscape", coordinator: "CoordinatorBase", friendly_id: 
                 FriendlyIdentifier, service_type: str, service_config: dict):
        super().__init__()

        # These data items live for the life of the device, so they are not guarded
        # by a lock
        self._lscape_ref = weakref.ref(lscape)
        self._coord_ref = weakref.ref(coordinator)

        self._friendly_id = friendly_id
        self._service_type = service_type
        self._service_config = service_config

        self._service_lock = threading.RLock()

        self._contacted_first = None
        self._contacted_last = None
        self._is_watched = None
        self._is_isolated = None

        self._extensions: Dict[str, ProtocolExtension] = {}

        self._table_for_match_callbacks = {}
        self._table_for_status_callbacks = {}

        self._credentials = {}

        self._name = None
        if "name" in service_config:
            self._name = service_config["name"]

        self._features = {}
        if "features" in service_config:
             self._features = service_config["features"]

        self._configured_ipaddr = None
        if "ipaddr" in service_config:
            self._configured_ip = service_config["ipaddr"]

        credmgr = lscape.credential_manager

        if "credentials" in service_config:
            for cred_key in service_config["credentials"]:
                self._credentials[cred_key] = credmgr.lookup_credential(cred_key)

        self._has_ssh_credential = False
        self._primary_ssh_credential = None
        for cred in self._credentials.values():
            if isinstance(cred, SshCredential):
                self._has_ssh_credential = True
                self._ssh_credential = cred
                break

        return

    @property
    def configured_ipaddr(self) -> Union[str, None]:
        return self._configured_ip

    @property
    def contacted_first(self) -> datetime:
        """
            A datetime stamp of when this service was first contacted
        """
        return self._contacted_first

    @property
    def contacted_last(self) -> datetime:
        """
            A datetime stamp of when this service was last contacted
        """
        return self._contacted_last

    @property
    def coordinator(self) -> "CoordinatorBase":
        return self._coord_ref()

    @property
    def credentials(self) -> Dict[str, BaseCredential]:
        return self._credentials

    @property
    def name(self) -> str:
        """
            A string representing a name for the service. 
        """
        return self._name

    @property
    def service_config(self) -> dict:
        """
            A dictionary of the configuration information for this service.
        """
        return self._service_config

    @property
    def service_type(self) -> str:
        """
            A string representing the type of service.
        """
        return self._service_type

    @property
    def group(self) -> str:
        """
            A string represeting the group a service has been assigned to.
        """
        return self._group

    @property
    def extensions(self) -> Dict[str, ProtocolExtension]:
        extdict = self._extensions.copy()
        return extdict

    @property
    def friendly_id(self) -> FriendlyIdentifier:
        """
            The friendly identifier for this device, this is generally the identifier provided
            by the coordinator that created the device instance.
        """
        return self._friendly_id

    @property
    def full_identifier(self) -> str:
        """
            The full identifier for this device, if one has been resolved.
        """
        return self._friendly_id.full_identifier

    @property
    def has_ssh_credential(self) -> bool:
        """
            Indicates if a device has and SshCredential associated with it.
        """
        return self._has_ssh_credential

    @property
    def identity(self) -> str:
        """
            Returns a string that identifies a device in logs. This property can
            be overridden by custom landscape devices to customize identities in
            logs.
        """
        return self._friendly_id.identity

    @property
    def ipaddr(self) -> str:
        """
            The device IP of the device, if available.
        """
        ipaddr = self._resolve_ipaddress()
        return ipaddr

    @property
    def is_configured_for_power(self):
        rtnval = True if "power" in self._features else False
        return rtnval
    
    @property
    def is_configured_for_serial(self):
        rtnval = True if "serial" in self._features else False
        return rtnval

    @property
    def is_watched(self) -> bool:
        """
            A boolean indicating if this device is a watched device.
        """
        return self._is_watched

    @property
    def landscape(self) -> "Landscape":
        """
            Returns a strong reference to the the landscape object
        """
        return self._lscape_ref()

    @property
    def moniker(self) -> str:
        """
            Returns a moniker for this device.
        """
        return self._friendly_id.identity

    @property
    def pivots(self) -> str:
        """
            Returns a set of pivot data points that can be used to
            colate results.
        """
        pivots = (self._friendly_id.identity,)
        return pivots

    @property
    def ssh_credential(self) -> Union[SshCredential, None]:
        return self._ssh_credential

    def attach_extension(self, ext_type: str, extension: ProtocolExtension) -> None:
        """
            Method called by device coordinators to attach a device extension to a :class:`LandscapeService`.
        """

        if ext_type not in self._extensions:
            self._extensions[ext_type] = extension
        else:
            errmsg = f"attach_extension: called for pre-existing extension type '{ext_type}'."
            raise SemanticError(errmsg)

        return

    def begin_locked_scope(self) -> "LockedScope":
        """
            Method that creates a locked scope for this device.
        """
        lkd_scope = LockedScope(self._service_lock)
        return lkd_scope

    def begin_unlocked_scope(self) -> "UnLockedScope":
        """
            Method that creates an unlocked scope for this device.
        """
        unlkd_scope = UnLockedScope(self._service_lock)
        return unlkd_scope

    def checkout(self) -> None:
        """
            Method that makes it convenient to checkout device.
        """
        self.landscape.checkout_device(self)
        return

    def checkin(self) -> None:
        """
            Method that makes it convenient to checkin a device.
        """
        self.landscape.checkin_device(self)
        return

    def enhance(self):
        """
            Called to allow a device to enhance its metadata past what is declared in the
            configuration file.  For device that only have a hint, this might trigger a
            discovery process which will result in determining connectivity with the device.
        """
        return

    def has_extension_type(self, ext_type: str) -> bool:
        """
            Returns a boolean value indicating if this device has the specified extension
            type registered.
        """
        has_ext_type = False
        if ext_type in self._extensions:
            has_ext_type = True
        return has_ext_type

    def initialize_credentials(self, credentials: Dict[str, BaseCredential]) -> None:
        """
            Initializes the credentials of the device based on the credentials listed for
            the device in the device configuration and the credentials configuration.
        """
        self._credentials = credentials
        return

    def initialize_features(self) -> None:
        """
            Initializes the features of the device based on the feature declarations and the information
            found in the feature config.
        """
        if "features" in self._service_config:
            feature_info = self._service_config["features"]
            for fkey, fval in feature_info.items():
                if fkey == "isolation":
                    self._is_isolated = fval
                elif fkey == "":
                    pass
        return

    def match_using_params(self, match_type, *match_params) -> bool:
        """
            Method that allows you to match :class:`LandscapeService` objects by providing a match_type and
            parameters.  The match type is mapped to functions that are registered by device coordinators
            and then the function is called with the match parameters to determine if a device is a match.
        """
        matches = False
        match_func = None
        match_self = None

        with self.begin_locked_scope(self._service_lock) as lk_locked:

            if match_type in self._table_for_match_callbacks:
                dext_attr, match_func = self._table_for_match_callbacks[match_type]
                match_self = None
                if hasattr(self, dext_attr):
                    match_self = getattr(self, dext_attr)

        if match_self is not None and match_func is not None:
            matches = match_func(match_self, *match_params)

        return matches


    def update_full_identifier(self, full_identifier: str) -> None:
        """
            Update the full identifier associated with the FriendlyIdentifier for this device.
        """

        self._friendly_id.update_full_identifier(full_identifier)
        
        return

    def update_match_table(self, match_table: dict) -> None:
        """
            Method called  to update the match functions.
        """

        with self.begin_locked_scope(self._service_lock) as lk_locked:

            self._table_for_match_callbacks.update(match_table)

        return
    
    def update_status_verification_callback(self, protocol: str, status_callback: Callable) -> None:
        """
            Method called  to update the verification callback functions for a given protocol.
        """

        with self.begin_locked_scope(self._service_lock) as lk_locked:

            self._table_for_status_callbacks[protocol] = status_callback

        return

    def verify_status(self) -> None:
        """
            Verify the status of the specified device.
        """

        for protocol, verify_status_callback in self._table_for_status_callbacks.items():
            verify_status_callback()

        return

    def _resolve_ipaddress(self) -> str:

        ipaddr = None

        if self._configured_ipaddr is not None:
            ipaddr = self._configured_ipaddr
        else:
            errmsg = f"_resolve_ipaddress: Unable to resolve IP address for dev {self}."
            raise RuntimeError(errmsg)

        return ipaddr

    def _repr_html_(self) -> str:
        html_repr_lines = [
            "<h1>LandscapeService</h1>",
            "<h2>     type: {}</h2>".format(self._service_type),
            "<h2>    identity: {}</h2>".format(self.identity),
            "<h2>       ip: {}</h2>".format(self.ipaddr)
        ]

        html_repr = os.linesep.join(html_repr_lines)

        return html_repr

    def __repr__(self) -> str:

        thisType = type(self)

        ipaddr = "unknown"

        # Note: We may not have an assigned IP address, a repr function
        # should never raise an exception so guard against a RuntimeException
        # being raised if we dont have an IP
        try:
            ipaddr = self._resolve_ipaddress()
        except RuntimeError:
            pass

        devstr = "<{} type={} identity={} ip={} >".format(thisType.__name__, self._service_type, self.identity, ipaddr)

        return devstr

    def __str__(self) -> str:
        devstr = repr(self)
        return devstr
