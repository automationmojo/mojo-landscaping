
from typing import List, Optional, Tuple

import copy

from mojo.interfaces.iexcludefilter import IExcludeFilter
from mojo.interfaces.iincludefilter import IIncludeFilter

from mojo.landscaping.wellknown import LandscapeSingleton

class ConfigurationExtractor:
    """
        The :class:`ConfigurationExtractor` is used to create an extraction from the Landscape,
        Topology, Runtime, Credentials.
    """

    def __init__(self):

        self._landscape = LandscapeSingleton()
        
        self._description = {
            "apod": {
                "devices": []
            },
            "infrastructure": {
                "services": []
            }
        }

        return

    def extract_clusters(self, include_filters: Optional[List[IIncludeFilter]]=None, exclude_filters: Optional[List[IExcludeFilter]]=None):

        devices_list = self._description["apod"]["devices"]

        clusters_found = self._landscape.get_clusters(include_filters=include_filters, exclude_filters=exclude_filters)

        for cluster in clusters_found:
            for node in cluster.nodes.values():
                devices_list.append(copy.deepcopy(node.device_config))

        return
    
    def extract_devices(self, include_filters: Optional[List[IIncludeFilter]]=None, exclude_filters: Optional[List[IExcludeFilter]]=None):

        devices_list = self._description["apod"]["devices"]

        devices_found = self._landscape.get_devices(include_filters=include_filters, exclude_filters=exclude_filters)

        for dev in devices_found:
            devices_list.append(copy.deepcopy(dev.device_config))

        return
    
    def extract_services(self, include_filters: Optional[List[IIncludeFilter]]=None, exclude_filters: Optional[List[IExcludeFilter]]=None):

        services_list = self._description["infrastructure"]["services"]

        services_found = self._landscape.get_services(include_filters=include_filters, exclude_filters=exclude_filters)

        for service in services_found:
            services_list.append(copy.deepcopy(service.service_config))

        return

    def get_configurations(self) -> Tuple[dict, dict, dict, dict]:
        """
            Gets the configuration dictionaries that were extractive from the runtime.

            :returns: A tuple containing the Landscape, Topology, Runtime, Credentials
        """
        return self._description
