"""
.. module:: servicecoordinatorcouplingbase
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Contains a :class:`ServiceCoordinatorCouplingBase` object to use for working with the
               computer services.

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


from typing import Any, Dict, List, Tuple, TYPE_CHECKING

from functools import partial

from mojo.errors.exceptions import SemanticError

from mojo.landscaping.coupling.coordinatorcoupling import CoordinatorCoupling
from mojo.landscaping.service.servicecoordinatorbase import ServiceCoordinatorBase

from mojo.landscaping.constants import StartupLevel

# Types imported only for type checking purposes
if TYPE_CHECKING:
    from mojo.landscaping.landscape import Landscape

SUPPORTED_INTEGRATION_CLASS = "network/service-base"

def is_matching_service_config(integ_class, service_info):
    is_matching_service = False

    svc_type = service_info["serviceType"]
    if svc_type == integ_class:
        is_matching_service = True

    return is_matching_service

class ServiceCoordinatorCouplingBase(CoordinatorCoupling):
    """
        The ServiceCoordinatorCouplingBase handle the requirement registration for the OSX coordinator.
    """

    integration_root: str = "infrastructure"
    integration_section: str = "services"
    integration_leaf: str = "serviceType"
    integration_class: str = SUPPORTED_INTEGRATION_CLASS

    COORDINATOR_TYPE = ServiceCoordinatorBase

    def __init__(self, *args, **kwargs):
        """
            The default contructor for an :class:`BaseServiceCoordinatorIntegration`.
        """
        super().__init__(*args, **kwargs)
        return

    @classmethod
    def attach_to_environment(cls, landscape: "Landscape"):
        """
            This API is called so that the IntegrationCoupling can process configuration information.  The :class:`IntegrationCoupling`
            will verify that it has a valid environment and configuration to run in.

            :raises :class:`mojo.errors.exceptions.AKitMissingConfigError`, :class:`mojo.errors.exceptions.ConfigurationError`:
        """

        cls.landscape = landscape
        layer_config = landscape.layer_configuration

        service_list = layer_config.get_service_configs()
        if len(service_list) > 0:
            svc_service_list = [svc for svc in filter(partial(is_matching_service_config, cls.integration_class), service_list)]

            if len(svc_service_list) > 0:
                layer_integ = landscape.layer_integration
                layer_integ.register_integration_dependency(cls)

        return

    @classmethod
    def collect_resources(cls):
        """
            This API is called so the `IntegrationCoupling` can connect with a resource management
            system and gain access to the resources required for the automation run.

            :raises :class:`mojo.errors.exceptions.AKitResourceError`:
        """
        return

    @classmethod
    def create_coordinator(cls, landscape: "Landscape") -> object:
        """
            This API is called so that the landscape can create a coordinator for a given integration role.
        """
        cls.coordinator = cls.COORDINATOR_TYPE(landscape)
        return cls.coordinator

    @classmethod
    def declare_precedence(cls) -> int:
        """
            This API is called so that the IntegrationCoupling can declare an ordinal precedence that should be
            utilized for bringing up its integration state.
        """
        return StartupLevel.PrimaryProtocol

    @classmethod
    def diagnostic(cls, label: str, level: int, diag_folder: str):
        """
            The API is called by the :class:`akit.sequencer.Sequencer` object when the automation sequencer is
            building out a diagnostic package at a diagnostic point in the automation sequence.  Example diagnostic
            points are:

            * pre-run
            * post-run

            Each diagnostic package has its own storage location so derived :class:`akit.scope.ScopeCoupling` objects
            can simply write to their specified output folder.

            :param label: The label associated with this diagnostic.
            :param level: The maximum diagnostic level to run dianostics for.
            :param diag_folder: The output folder path where the diagnostic information should be written.
        """
        return

    @classmethod
    def establish_connectivity(cls, allow_missing_services: bool=False) -> Tuple[List[str], dict]:
        """
            This API is called so the `IntegrationCoupling` can establish connectivity with any compute or storage
            resources.

            :returns: A tuple with a list of error messages for failed connections and dict of connectivity
                      reports for services based on the coordinator.
        """

        lscape = cls.landscape
        layer_integ = lscape.layer_integration

        service_list = layer_integ.get_services()
        if len(service_list) > 0:
            svc_service_list = [svc for svc in filter(partial(is_matching_service_config, cls.integration_class), service_list)]

            if len(svc_service_list) == 0:
                raise SemanticError("We should have not been called if no services are available.")

            svc_config_errors, matching_service_results, missing_service_results = cls.coordinator.attach_to_services(
                svc_service_list)

            svc_scan_results = {
                "default": {
                    "matching_services": matching_service_results,
                    "missing_services": missing_service_results
                }
            }

        return (svc_config_errors, svc_scan_results)

    @classmethod
    def establish_presence(cls) -> Tuple[List[str], dict]:
        """
            This API is called so the `IntegrationCoupling` can establish presence with any compute or storage
            resources.

            :returns: A tuple with a list of error messages for failed connections and dict of connectivity
                      reports for services based on the coordinator.
        """
        return

    @classmethod
    def validate_item_configuration(cls, item_info: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """
            Validate the item configuration.

            -   serviceType: network/service-something
                name: raspey03
                host: 172.16.1.33
                credentials:
                -    pi-cluster
                features:
                    isolation: false
                skip: false
        """
        errors = []
        warnings = []
        
        if "host" not in item_info:
            errmsg = "Service configuration 'network/service-base' must have a 'host' field."
            errors.append(errmsg)

        if "credentials" not in item_info:
            warnmsg = "Service configuration 'network/service-base' should have a 'credentials' field."
            warnings.append(warnmsg)

        return errors, warnings