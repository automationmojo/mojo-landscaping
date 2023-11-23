"""
.. module:: servicecoordinatorbase
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module contains the :class:`ServiceCoordinatorBase` object which is a base
               class for objects create and manage service objects.

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

from typing import Any, Dict, List, Optional, Tuple, Union, TYPE_CHECKING

import os
import pprint

from mojo.errors.exceptions import ConfigurationError, NotOverloadedError

from mojo.credentials.basecredential import BaseCredential
from mojo.landscaping.friendlyidentifier import FriendlyIdentifier

from mojo.landscaping.coordinators.coordinatorbase import CoordinatorBase
from mojo.landscaping.landscapeparameters import LandscapeActivationParams
from mojo.landscaping.landscapeservice import LandscapeService

from mojo.landscaping.service.servicebase import ServiceBase


if TYPE_CHECKING:
    from mojo.landscaping.landscape import Landscape


def format_service_configuration_error(message, next_svc_config):
    """
        Takes an error message and an service configuration info dictionary and
        formats a configuration error message.
    """
    error_lines = [
        message,
        "DEVICE:"
    ]

    svc_repr_lines = pprint.pformat(next_svc_config, indent=4).splitlines(False)
    for dline in svc_repr_lines:
        error_lines.append("    " + dline)
    
    errmsg = os.linesep.join(error_lines)
    return errmsg

class ServiceCoordinatorBase(CoordinatorBase):
    """
        The :class:`BaseServicePoolCoordinator` creates a pool of agents that can be used to
        coordinate the interop activities of the automation process and remote OSX
        service.
    """
    # pylint: disable=attribute-defined-outside-init

    INTEGRATION_CLASS = ""
    SERVICE_TYPE = ServiceBase

    MUST_INCLUDE_SSH = False

    def __init__(self, lscape: "Landscape", *args, **kwargs):
        super().__init__(lscape, *args, **kwargs)

        self._cl_upnp_hint_to_ip_lookup: Dict[str, str] = {}
        self._cl_ip_to_host_lookup: Dict[str, str] = {}
        return

    def activate(self, activation_params: LandscapeActivationParams):
        """
            Called by the :class:`LandscapeOperationalLayer` in order for the coordinator to be able to
            potentially enhanced services.
        """
        return

    def attach_protocol_extensions(self, landscape: "Landscape", service_info: Dict[str, Any], service: LandscapeService):
        """
            Called when a landscape service is created in order to attach protocol extensions.
        """
        self.attach_extension_for_ssh(landscape, service_info, service)
        return

    def attach_extension_for_ssh(self, landscape: "Landscape", service_info: Dict[str, Any], service: LandscapeService):

        credentials = service.credentials

        ssh_cred = None
        for cred in credentials.values():
            if "ssh" in cred.categories:
                ssh_cred = cred
                break

        ssh_add_error = None
        
        if ssh_cred is not None:
            if "host" in service_info:
                host = service_info["host"]

                users = None
                if "users" in service_info:
                    users = service_info["users"]

                port = 22
                if "port" in service_info:
                    port = service_info["port"]

                pty_params = None
                if "pty_params" in service_info:
                    pty_params = service_info["pty_params"]

                self.create_ssh_agent(service, service_info, host, ssh_cred, 
                                      users=users, port=port, pty_params=pty_params)
            else:
                ssh_add_error = "missing 'host'"
        else:
            ssh_add_error = "missing 'ssh' credential"

        if self.MUST_INCLUDE_SSH and ssh_add_error is not None:
            type_name = type(self).__name__
            err_msg = f"{type_name} service needs to have an 'ssh' credential. ({ssh_add_error})"
            raise ConfigurationError(err_msg)

        return

    def create_landscape_service(self, landscape: "Landscape", service_info: Dict[str, Any]) -> Tuple[FriendlyIdentifier, ServiceBase]:
        """
            Called to declare a declared landscape service for a given coordinator.
        """
        host = service_info["host"]
        service_type = service_info["serviceType"]
        fid = FriendlyIdentifier(host, host)

        service = self.SERVICE_TYPE(landscape, self, fid, service_type, service_info)

        self.attach_protocol_extensions(landscape, service_info, service)

        return fid, service

    def create_ssh_agent(self, service: LandscapeService, service_info: Dict[str, Any], host: str, cred: BaseCredential,
                         users: Optional[dict] = None, port: int = 22, pty_params: Optional[dict] = None):
        
        if self.MUST_INCLUDE_SSH:
            err_mgs = "if 'MUST_INCLUDE_SSH' is 'True' then 'create_ssh_agent' must be overloaded."
            raise NotOverloadedError(err_mgs)

        return

    def establish_connectivity(self, activation_params: LandscapeActivationParams):
        """
            Called by the :class:`LandscapeOperationalLayer` in order for the coordinator to be able to
            verify connectivity with services.
        """
        results = []

        cmd: str = "echo 'It Works'"

        for agent in self.children_as_extension:
            host = agent.host
            ipaddr = agent.ipaddr
            try:
                status, stdout, stderr = agent.run_cmd(cmd)
                results.append((host, ipaddr, status, stdout, stderr, None))
            except Exception as xcpt: # pylint: disable=broad-except
                results.append((host, ipaddr, None, None, None, xcpt))

        return results

    def lookup_service_by_host(self, host: str) -> Union[LandscapeService, None]:
        """
            Looks up the agent for a service by its hostname.  If the
            agent is not found then the API returns None.

            :param host: The host name of the LandscapeService to search for.

            :returns: The found LandscapeService or None
        """
        service = None

        self._coord_lock.acquire()
        try:
            if host in self._cl_children:
                service = self._cl_children[host].extended
        finally:
            self._coord_lock.release()

        return service

    def lookup_service_by_ip(self, ip) -> Union[LandscapeService, None]:
        """
            Looks up the agent for a service by its ip address.  If the
            agent is not found then the API returns None.

            :param ip: The ip address of the LandscapeService to search for.

            :returns: The found LandscapeService or None
        """
        service = None

        self._coord_lock.acquire()
        try:
            if ip in self._cl_ip_to_host_lookup:
                if ip in self._cl_ip_to_host_lookup:
                    host = self._cl_ip_to_host_lookup[ip]
                    if host in self._cl_children:
                        service = self._cl_children[host].extended
        finally:
            self._coord_lock.release()

        return service

    def verify_connectivity(self, cmd: str = "echo 'It Works'", user: Optional[str] = None, raiseerror: bool = True) -> List[tuple]:
        """
            Loops through the nodes in the OSX service pool and utilizes the credentials for the specified user in order to verify
            connectivity with the remote node.

            :param cmd: A command to run on the remote machine in order
                        to verify that osx connectivity can be establish.
            :param user: The name of the user credentials to use for connectivity.
                         If the 'user' parameter is not provided, then the
                         credentials of the default or priviledged user will be used.
            :param raiseerror: A boolean value indicating if this API should raise an Exception on failure.

            :returns: A list of errors encountered when verifying connectivity with the services managed or watched by the coordinator.
        """
        results = []

        for agent in self.children_as_extension:
            host = agent.host
            ipaddr = agent.ipaddr
            try:
                status, stdout, stderr = agent.run_cmd(cmd)
                results.append((host, ipaddr, status, stdout, stderr, None))
            except Exception as xcpt: # pylint: disable=broad-except
                if raiseerror:
                    raise
                results.append((host, ipaddr, None, None, None, xcpt))

        return results
