"""
.. module:: landscapeintegrationlayer
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`LandscapeItegrationLayer` class which is used
               to load initialize the test landscape and integrate with all the available
               landscape resources.

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

from typing import Any, Dict, List, Optional, TYPE_CHECKING

from mojo.errors.exceptions import SemanticError

from mojo.interfaces.iexcludefilter import IExcludeFilter
from mojo.interfaces.iincludefilter import IIncludeFilter

from mojo.xmods.injection.coupling.integrationcoupling import IntegrationCouplingType

from mojo.landscaping.constants import DeviceExtensionType
from mojo.landscaping.coordinators.coordinatorbase import CoordinatorBase
from mojo.landscaping.coupling.coordinatorcoupling import CoordinatorCoupling
from mojo.landscaping.layers.landscapinglayerbase import LandscapingLayerBase
from mojo.landscaping.layers.landscapeconfigurationlayer import LandscapeConfigurationLayer
from mojo.landscaping.friendlyidentifier import FriendlyIdentifier
from mojo.landscaping.landscapedevice import LandscapeDevice
from mojo.landscaping.landscapedevicegroup import LandscapeDeviceGroup
from mojo.landscaping.landscapeservice import LandscapeService

from mojo.landscaping.landscapeparameters import (
    LandscapeActivationParams
)

if TYPE_CHECKING:
    from mojo.landscaping.landscape import Landscape


class LandscapeIntegrationLayer(LandscapingLayerBase):

    def __init__(self, lscape: "Landscape"):
        super().__init__(lscape)
        self._integrated_devices: Dict[str, LandscapeDevice] = None
        self._integrated_power: Dict[str, Any] = None
        self._integrated_serial: Dict[str, Any] = None
        self._integrated_services: Dict[str, LandscapeService] = None

        self._integrated_device_groups: Dict[str, LandscapeDeviceGroup] = {}

        self._requested_integration_couplings: Dict[str, IntegrationCouplingType] = {}

        self._coordinators_for_devices = {}
        self._coordinators_for_power = {}
        self._coordinators_for_serial = {}
        self._coordinators_for_services = {}

        self._power_request_count = 0
        self._serial_request_count = 0
        return
    
    @property
    def coordinators_for_devices(self) -> Dict[str, CoordinatorBase]:
        coord_table = {}

        lscape = self.landscape
        with lscape.begin_locked_landscape_scope() as locked:
            coord_table = self._coordinators_for_devices.copy()

        return coord_table
    
    @property
    def coordinators_for_power(self) -> Dict[str, CoordinatorBase]:
        coord_table = {}

        lscape = self.landscape
        with lscape.begin_locked_landscape_scope() as locked:
            coord_table = self._coordinators_for_power.copy()

        return coord_table
    
    @property
    def coordinators_for_serial(self) -> Dict[str, CoordinatorBase]:
        coord_table = {}

        lscape = self.landscape
        with lscape.begin_locked_landscape_scope() as locked:
            coord_table = self._coordinators_for_serial.copy()

        return coord_table

    @property
    def coordinators_for_services(self) -> Dict[str, CoordinatorBase]:
        coord_table = {}

        lscape = self.landscape
        with lscape.begin_locked_landscape_scope() as locked:
            coord_table = self._coordinators_for_services.copy()

        return coord_table

    @property
    def integrated_device_groups(self) -> Dict[str, LandscapeDeviceGroup]:
        """
            Provides a thread safe copy of the integration device group dictionary.
        """
        idevicegroups = {}

        lscape = self.landscape
        with lscape.begin_locked_landscape_scope() as locked:
            idevicegroups = self._integrated_device_groups.copy()

        return idevicegroups

    @property
    def integrated_devices(self) -> Dict[str, LandscapeDevice]:
        """
            Provides a thread safe copy of the integration device dictionary.
        """
        idevices = {}

        lscape = self.landscape
        with lscape.begin_locked_landscape_scope() as locked:
            idevices = self._integrated_devices.copy()

        return idevices
    
    @property
    def integrated_power(self) -> Dict[str, Any]:
        """
            Provides a thread safe copy of the integration power dictionary.
        """
        ipower = {}

        lscape = self.landscape
        with lscape.begin_locked_landscape_scope() as locked:
            ipower = self._integrated_power.copy()

        return ipower
    
    @property
    def integrated_serial(self) -> Dict[str, Any]:
        """
            Provides a thread safe copy of the integration serial dictionary.
        """
        iserial = {}

        lscape = self.landscape
        with lscape.begin_locked_landscape_scope() as locked:
            iserial = self._integrated_serial.copy()

        return iserial

    @property
    def integrated_services(self) -> Dict[str, LandscapeService]:
        """
            Provides a thread safe copy of the integration services dictionary.
        """
        iservices = {}

        lscape = self.landscape
        with lscape.begin_locked_landscape_scope() as locked:
            iservices = self._integrated_services.copy()

        return iservices

    @property
    def requested_integration_couplings(self) -> Dict[str, IntegrationCouplingType]:
        """
            Returns a table of the installed integration couplings found.
        """
        return self._requested_integration_couplings

    def get_devices(self, include_filters: Optional[List[IIncludeFilter]]=None, exclude_filters: Optional[List[IExcludeFilter]]=None) -> LandscapeDevice:
        """
            Gets a copy of the integrated devices list.
        """
        lscape = self.landscape

        candidate_devices = None

        with lscape.begin_locked_landscape_scope() as locked:
            candidate_devices = [dev for dev in self._integrated_devices.values()]
        
        selected_devices = []

        if include_filters is None:
            selected_devices = candidate_devices
        else:
            while len(candidate_devices):
                dev = candidate_devices.pop()
                for ifilter in include_filters:
                    if ifilter.should_include(dev):
                        selected_devices.append(dev)
                        break

        if exclude_filters is not None:
            candidate_devices = selected_devices

            selected_devices = []

            while len(candidate_devices):
                dev = candidate_devices.pop()
                for xfilter in exclude_filters:
                    if not xfilter.should_exclude(dev):
                        selected_devices.append(dev)

        return selected_devices
    
    def get_services(self, include_filters: Optional[List[IIncludeFilter]]=None, exclude_filters: Optional[List[IExcludeFilter]]=None) -> LandscapeService:
        """
            Gets a copy of the integrated service list.
        """
        lscape = self.landscape

        candidate_services = None

        with lscape.begin_locked_landscape_scope() as locked:
            candidate_services = [svc for svc in self._integrated_services.values()]
        
        selected_services = []

        if include_filters is None:
            selected_services = candidate_services
        else:
            while len(candidate_services):
                svc = candidate_services.pop()
                for ifilter in include_filters:
                    if ifilter.should_include(svc):
                        selected_services.append(svc)
                        break

        if exclude_filters is not None:
            candidate_services = selected_services

            selected_services = []

            while len(candidate_services):
                svc = candidate_services.pop()
                for xfilter in exclude_filters:
                    if not xfilter.should_exclude(svc):
                        selected_services.append(svc)

        return selected_services

    def initialize_landscape(self, activation_params: LandscapeActivationParams):

        lscape = self.landscape

        devices = None
        with lscape.begin_locked_landscape_scope() as locked:

            layer_config = lscape.layer_configuration

            if layer_config.landscape_info is not None:

                if not activation_params.disable_device_activation:
                    # Initialize the devices so we know what they are, this will create a LandscapeDevice object for each device
                    # and register it in the all_devices table where it can be found by the device coordinators for further activation
                    devices = self._initialize_landscape_devices(layer_config)

                    if self._power_request_count > 0:
                        self._initialize_landscape_power(layer_config)

                    if self._serial_request_count > 0:
                        self._initialize_landscape_serial(layer_config)
                else:
                    self.logger.info("LandscapeIntegrationLayer: 'Device Activation' was disabled.")
                    devices = {}

                if not activation_params.disable_service_activation:
                    services = self._initialize_landscape_services(layer_config)
                else:
                    self.logger.info("LandscapeIntegrationLayer: 'Service Activation' was disabled.")
                    services = {}

                self._integrated_devices = devices.copy()
                self._integrated_services = services.copy()
            else:
                devices = {}
                self._integrated_devices = {}
                self._integrated_power = {}
                self._integrated_serial = {}
                self._integrated_services = {}

        self._initialize_landscape_device_groups()

        return

    def register_device_extension_association(self, ext_type: DeviceExtensionType, device: LandscapeDevice):
        """
            This method is called by coordinator device in order to register device type
            associations for the device that a coordinator is creating.  A coornidator may
            create devices that have the characteristics of mulitiple devices.  For example,
            a cluster node device might have multiple device extension associations:

            :param ext_type: The device extension type to associate with the device being registered.
            :param device: The device being registered.
        """

        ext_for_type_table = None
        
        if ext_type in self._devices_by_ext_type:
            ext_for_type_table = self._devices_by_ext_type[ext_type]
        else:
            ext_for_type_table = {}
            self._devices_by_ext_type[ext_type] = ext_for_type_table
        
        ext_for_type_table[device.identity] = device

        return

    def register_integration_dependency(self, coupling: IntegrationCouplingType):
        """
            This method should be called from the attach_to_environment methods from individual couplings
            in order to register the base level integrations.  Integrations can be hierarchical so it
            is only necessary to register the root level integration couplings, the descendant couplings can
            be called from the root level couplings.

            :param role: The name of a role to assign for a coupling.
            :param coupling: The coupling to register for the associated role.
        """

        lscape = self.landscape

        with lscape.begin_locked_landscape_scope() as locked:
            integ_key = coupling.get_integration_key()
            self._requested_integration_couplings[integ_key] = coupling

        return

    def topology_overlay(self) -> None:

        return
    

    def _initialize_landscape_device_groups(self):

        dev_group_table = {}

        for dev_obj in self._integrated_devices.values():
            group_name = dev_obj.group
            if group_name != "":
                device_list = None
                if group_name in dev_group_table:
                    device_list = dev_group_table[group_name]
                else:
                    device_list = []
                    dev_group_table[group_name] = device_list
                device_list.append(dev_obj)
        
        for group_name, group_items in dev_group_table.items():
            device_group = LandscapeDeviceGroup(group_name, group_items)
            self._integrated_device_groups[group_name] = device_group

        return 
    

    def _initialize_landscape_devices(self, layer_config: LandscapeConfigurationLayer) -> Dict[FriendlyIdentifier, LandscapeDevice]:

        unrecognized_device_configs = []

        devices: Dict[FriendlyIdentifier: LandscapeDevice] = {}

        requested_coupling_table = self._requested_integration_couplings

        device_configs = layer_config.get_device_configs()

        if len(device_configs) > 0:
            lscape = self.landscape

            for dev_config_info in device_configs:
                dev_type = dev_config_info["deviceType"]
                dev_section = dev_config_info["section"]
                dev_integ_key = f"apod:{dev_section}:deviceType:{dev_type}"

                if dev_integ_key in requested_coupling_table:
                    coord_coupling: CoordinatorCoupling = requested_coupling_table[dev_integ_key]

                    # If we don't have a device coordinator for this type of device yet,
                    # create one.
                    coordinator = None
                    if dev_integ_key in self._coordinators_for_devices:
                        coordinator = self._coordinators_for_devices[dev_integ_key]
                    else:
                        coordinator = coord_coupling.create_coordinator(lscape)
                        self._coordinators_for_devices[dev_integ_key] = coordinator

                    friendly_id, lsdevice = coordinator.create_landscape_device(lscape, dev_config_info)

                    if lsdevice.is_configured_for_power:
                        self._power_request_count += 1

                    if lsdevice.is_configured_for_serial:
                        self._serial_request_count += 1

                    devices[friendly_id.identity] = lsdevice
                else:
                    unrecognized_device_configs.append(dev_config_info)

        return devices


    def _initialize_landscape_power(self, layer_config: LandscapeConfigurationLayer):

        power_configs = layer_config.get_power_configs()

        if len(power_configs) > 0:
            lscape = self.landscape

            for pwr_config_info in power_configs:
                power_type = pwr_config_info["powerType"]
                power_integ_key = f"apod:power:powerType:{power_type}"

        return


    def _initialize_landscape_serial(self, layer_config: LandscapeConfigurationLayer):

        serial_configs = layer_config.get_serial_configs()

        if len(serial_configs) > 0:
            lscape = self.landscape

            for serial_config_info in serial_configs:
                serial_type = serial_config_info["serialType"]
                serial_integ_key = f"apod:serial:serialType:{serial_type}"

        return

    def _initialize_landscape_services(self, layer_config: LandscapeConfigurationLayer) -> Dict[FriendlyIdentifier, LandscapeService]:

        unrecognized_service_configs = []

        services: Dict[FriendlyIdentifier: LandscapeService] = {}

        requested_coupling_table = self._requested_integration_couplings

        service_configs = layer_config.get_service_configs()

        if len(service_configs) > 0:
            lscape = self.landscape

            for svc_config_info in service_configs:
                svc_type = svc_config_info["serviceType"]
                svc_integ_key = f"infrastructure:services:serviceType:{svc_type}"

                if svc_integ_key in requested_coupling_table:
                    coord_coupling: CoordinatorCoupling = requested_coupling_table[svc_integ_key]

                    # If we don't have a device coordinator for this type of device yet,
                    # create one.
                    coordinator = None
                    if svc_integ_key in self._coordinators_for_services:
                        coordinator = self._coordinators_for_services[svc_integ_key]
                    else:
                        coordinator = coord_coupling.create_coordinator(lscape)
                        self._coordinators_for_services[svc_integ_key] = coordinator

                    friendly_id, lssvc = coordinator.create_landscape_service(lscape, svc_config_info)

                    services[friendly_id.identity] = lssvc
                else:
                    unrecognized_service_configs.append(svc_config_info)

        return services
