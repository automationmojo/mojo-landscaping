"""
.. module:: landscapeconfigurationlayer
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`LandscapeConfigurationLayer` class which is used
               to load the various configuration files and to provide methods for working with
               configuration information.

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

import json
import os
import traceback
import yaml

from mojo.errors.exceptions import ConfigurationError

from mojo.collections.mergemap import MergeMap
from mojo.collections.wellknown import ContextSingleton

from mojo.config.configurationmaps import CONFIGURATION_MAPS

from mojo.credentials.credentialmanager import CredentialManager

from mojo.interfaces.iexcludefilter import IExcludeFilter
from mojo.interfaces.iincludefilter import IIncludeFilter

from mojo.landscaping.layers.landscapinglayerbase import LandscapingLayerBase

from mojo.landscaping.landscapeparameters import (
    LandscapeActivationParams
)

if TYPE_CHECKING:
    from mojo.landscaping.landscape import Landscape

APOD_RESERVED_SECTIONS = [
    "controller"
]

class LandscapeConfigurationLayer(LandscapingLayerBase):
    """
        The base class for all derived :class:`LandscapeDescription` objects.  The
        :class:`LandscapeDescription` is used to load a description of the entities
        and resources in the tests landscape that will be used by the tests.
    """

    def __init__(self, lscape: "Landscape"):
        super().__init__(lscape)

        self._credential_manager: CredentialManager = None

        self._landscape_files: List[str] = None
        self._landscape_info: MergeMap = None

        self._topology_files: List[str] = None
        self._topology_info: MergeMap = None

        # We can get runtime configuration from the global context which
        # should already be loaded
        self._global_context = ContextSingleton()
        return

    @property
    def credential_manager(self) -> CredentialManager:
        return self._credential_manager
    
    @property
    def landscape_files(self) -> List[str]:
        return self._landscape_files
    
    @property
    def landscape_info(self) -> Union[MergeMap, None]:
        return self._landscape_info

    @property
    def topology_files(self) -> List[str]:
        return self._topology_files
    
    @property
    def topology_info(self) -> Union[MergeMap, None]:
        return self._topology_info

    def get_device_configs(self, include_filters: Optional[List[IIncludeFilter]]=None, exclude_filters: Optional[List[IExcludeFilter]]=None) -> List[dict]:
        lscape = self.landscape

        candidate_configs = []

        with lscape.begin_locked_landscape_scope() as locked:
            candidate_configs = self.locked_get_device_configs()

        selected_configs = []

        if include_filters is None:
            selected_configs = candidate_configs
        else:
            while len(candidate_configs):
                dev = candidate_configs.pop()
                for ifilter in include_filters:
                    if ifilter.should_include(dev):
                        selected_configs.append(dev)
                        break

        if exclude_filters is not None:
            candidate_configs = selected_configs

            selected_configs = []

            while len(candidate_configs):
                dev = candidate_configs.pop()
                for xfilter in exclude_filters:
                    if not xfilter.should_exclude(dev):
                        selected_configs.append(dev)

        return selected_configs

    def get_power_configs(self) -> List[dict]:
        lscape = self.landscape

        power_configs = []

        with lscape.begin_locked_landscape_scope() as locked:
            power_configs = self.locked_get_power_configs()

        return power_configs

    def get_serial_configs(self) -> List[dict]:
        lscape = self.landscape

        serial_configs = []

        with lscape.begin_locked_landscape_scope() as locked:
            serial_configs = self.locked_get_serial_configs()

        return serial_configs

    def get_service_configs(self, include_filters: Optional[List[IIncludeFilter]]=None, exclude_filters: Optional[List[IExcludeFilter]]=None) -> List[dict]:
        lscape = self.landscape

        service_configs = []

        with lscape.begin_locked_landscape_scope() as locked:
            service_configs = self.locked_get_service_configs()

        return service_configs


    def attach_to_environment(self):

        lscape = self.landscape

        # During the landscape initialization and before we start creating devices, give
        # all of the installed coordinator couplings and opportunity to peek at the configuration
        # and perform any special validation or internal initialization, this also provides the
        # integrations with a first glance at the test landscape after the configuration files
        # have been loaded.
        integ_coupling_table = lscape.installed_integration_couplings
        for integ_key in integ_coupling_table:
            integ_coupling = integ_coupling_table[integ_key]
            integ_coupling.attach_to_environment(lscape)

        return

    def initialize_credentials(self) -> None:
        """
            Initialize the credentials manager for the landscape object.
        """
        self._credential_manager = CredentialManager()
        return

    def load_landscape(self, activation_params: LandscapeActivationParams) -> Union[MergeMap, None]:
        """
            Loads and validates the landscape description file.
        """

        if CONFIGURATION_MAPS.LANDSCAPE_CONFIGURATION_MAP is not None and \
            len(CONFIGURATION_MAPS.LANDSCAPE_CONFIGURATION_MAP) > 0:

            self._landscape_info = CONFIGURATION_MAPS.LANDSCAPE_CONFIGURATION_MAP

            errors, warnings = self.validate_landscape(self._landscape_info)

            if len(errors) > 0:
                errmsg_lines = [
                    "ERROR Landscape validation failures:"
                ]
                for err_path, err_msg in errors:
                    errmsg_lines.append("    {}: {}".format(err_path, err_msg))

                errmsg = os.linesep.join(errmsg_lines)
                raise ConfigurationError(errmsg) from None

            if len(warnings) > 0:
                for wrn_path, wrn_msg in warnings:
                    self.logger.warn("Landscape Configuration Warning: ({}) {}".format(wrn_path, wrn_msg))

        return self._landscape_info


    def load_topology(self, activation_params: LandscapeActivationParams) -> Union[MergeMap, None]:
        """
            Loads the topology file.
        """

        if CONFIGURATION_MAPS.TOPOLOGY_CONFIGURATION_MAP is not None and \
            len(CONFIGURATION_MAPS.TOPOLOGY_CONFIGURATION_MAP) > 0:

            self._topology_info = CONFIGURATION_MAPS.TOPOLOGY_CONFIGURATION_MAP

            errors, warnings = self.validate_topology(self._topology_info)

            if len(errors) > 0:
                errmsg_lines = [
                    "ERROR Topology validation failures:"
                ]
                for err_path, err_msg in errors:
                    errmsg_lines.append("    {}: {}".format(err_path, err_msg))

                errmsg = os.linesep.join(errmsg_lines)
                raise ConfigurationError(errmsg) from None

            if len(warnings) > 0:
                for wrn_path, wrn_msg in warnings:
                    self.logger.warn("Topology Configuration Warning: ({}) {}".format(wrn_path, wrn_msg))

        return self._topology_info


    def locked_get_device_configs(self) -> List[dict]:
        """
            Returns the list of device configurations from the landscape.  This will
            skip any device that have a "skip": true declared in the configuration.

            ..note: It is assumed that this call is being made in a thread safe context
                    or with the landscape lock held.
        """

        device_config_list = []

        if "apod" in self._landscape_info:
            pod_info = self._landscape_info["apod"]

            for devsection in pod_info.keys():
                if devsection not in APOD_RESERVED_SECTIONS:
                    section_items = pod_info[devsection]
                    for dev_config_info in section_items:
                        if "skip" in dev_config_info and dev_config_info["skip"]:
                            continue
                        dev_config_info["section"] = devsection
                        device_config_list.append(dev_config_info)

        return device_config_list


    def locked_get_power_configs(self) -> List[dict]:
        """
            Returns the list of device configurations from the landscape.  This will
            skip any device that have a "skip": true declared in the configuration.

            ..note: It is assumed that this call is being made in a thread safe context
                    or with the landscape lock held.
        """

        power_config_list = []

        if "apod" in self._landscape_info:
            pod_info = self._landscape_info["apod"]
            if "power" in pod_info:
                for power_config_info in pod_info["power"]:
                    power_config_list.append(power_config_info)

        return power_config_list
    
    def locked_get_serial_configs(self) -> List[dict]:
        """
            Returns the list of serial manager configurations from the landscape.  This will
            skip any device that have a "skip": true declared in the configuration.

            ..note: It is assumed that this call is being made in a thread safe context
                    or with the landscape lock held.
        """

        serial_config_list = []

        if "apod" in self._landscape_info:
            pod_info = self._landscape_info["apod"]
            if "serial" in pod_info:
                for serial_config_info in pod_info["serial"]:
                    serial_config_list.append(serial_config_info)

        return serial_config_list

    def locked_get_service_configs(self) -> List[dict]:
        """
            Returns the list of service configurations from the landscape.  This will
            skip any services that have a "skip": true declared in the configuration.

            ..note: It is assumed that this call is being made in a thread safe context
                    or with the landscape lock held.
        """

        service_config_list = []

        if "infrastructure" in self._landscape_info:
            infrastructure_info = self._landscape_info["infrastructure"]
            if "services" in infrastructure_info:
                for svc_config_info in infrastructure_info["services"]:
                    if "skip" in svc_config_info and svc_config_info["skip"]:
                        continue
                    service_config_list.append(svc_config_info)

        return service_config_list

    def record_configuration(self, log_to_directory: str):
        """
            Method code to record the landscape configuration to an output folder
        """
        
        if self._landscape_info is not None:
            landscape_info_copy = self._landscape_info.flatten()
            landscape_declared_file = None

            try:
                landscape_declared_file = os.path.join(log_to_directory, "landscape-declared.yaml")
                with open(landscape_declared_file, 'w') as lsf:
                    yaml.safe_dump(landscape_info_copy, lsf, indent=4, default_flow_style=False)

                landscape_declared_file = os.path.join(log_to_directory, "landscape-declared.json")
                with open(landscape_declared_file, 'w') as lsf:
                    json.dump(landscape_info_copy, lsf, indent=4)

            except Exception as xcpt:
                err_msg = "Error while logging the landscape configuration file (%s)%s%s" % (
                    landscape_declared_file, os.linesep, traceback.format_exc())
                raise RuntimeError(err_msg) from xcpt
        
        if self._topology_info is not None:
            topology_info_copy = self._topology_info.flatten()
            topology_declared_file = None

            try:
                topology_declared_file = os.path.join(log_to_directory, "topology-declared.yaml")
                with open(topology_declared_file, 'w') as lsf:
                    yaml.safe_dump(topology_info_copy, lsf, indent=4, default_flow_style=False)

                topology_declared_file = os.path.join(log_to_directory, "topology-declared.json")
                with open(topology_declared_file, 'w') as lsf:
                    json.dump(topology_info_copy, lsf, indent=4)

            except Exception as xcpt:
                err_msg = "Error while logging the topology configuration file (%s)%s%s" % (
                    topology_declared_file, os.linesep, traceback.format_exc())
                raise RuntimeError(err_msg) from xcpt

        # NOTE: The `LandscapeConfigurationLayer` is not responsible for recording the runtime configuration
        # information.  The loading and recording of runtime configuration is accomplished by the `mojo-runtime`
        # package.

        return


    def validate_landscape(self, landscape_info) -> Tuple[List[str], List[str]]:
        """
            Validates the landscape description file.
        """
        errors = []
        warnings = []

        if "apod" in landscape_info:
            podinfo = landscape_info["apod"]
            for section in podinfo:
                if section == "environment":
                    envinfo = landscape_info["environment"]
                    child_errors, child_warnings = self.validate_landscape_environment(envinfo)
                    errors.extend(child_errors)
                    warnings.extend(child_warnings)
                else:
                    section_items = podinfo[section]
                    child_errors, child_warnings = self.validate_landscape_pod_section(section, section_items)
                    errors.extend(child_errors)
                    warnings.extend(child_warnings)

        if "integrations" in landscape_info:
            integinfo = landscape_info["integrations"]
            for section in integinfo:
                if section == "services":
                    servicesinfo = integinfo[section]
                    child_errors, child_warnings = self.validate_landscape_integration_section(section, servicesinfo)
                    errors.extend(child_errors)
                    warnings.extend(child_warnings)


        return errors, warnings


    def validate_landscape_environment(self, envinfo) -> Tuple[List[str], List[str]]:
        """
        "environment":
            "label": "production"
        """
        errors = []
        warnings = []

        return errors, warnings


    def validate_landscape_integration_section(self, section: str, section_items: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:

        errors = []
        warnings = []

        return errors, warnings

    def validate_landscape_pod_section(self, section: str, section_items: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:

        errors = []
        warnings = []

        lscape: "Landscape" = self.landscape

        remaining_items = [item for item in section_items]

        for nxt_coupling_type in lscape.installed_integration_couplings.values():

            if nxt_coupling_type.integration_section == section:
                validated_items = []

                for nxt_item in remaining_items:
                    if nxt_coupling_type.integration_leaf in nxt_item:
                        nxt_class = nxt_item[nxt_coupling_type.integration_leaf]
                        if nxt_class == nxt_coupling_type.integration_class:
                            ierrors, iwarnings = nxt_coupling_type.validate_item_configuration(nxt_item)
                            errors.extend(ierrors)
                            warnings.extend(iwarnings)
                            validated_items.append(nxt_item)

                for item in validated_items:
                    remaining_items.remove(item)

        return errors, warnings


    def validate_runtime(self, runtime_info: dict) -> Tuple[List[str], List[str]]:
        """
            Validates the runtime configuration.
        """
        errors = []
        warnings = []

        return errors, warnings


    def validate_topology(self, topology_info: dict) -> Tuple[List[str], List[str]]:
        """
            Validates the topology configuration.
        """
        errors = []
        warnings = []

        return errors, warnings

