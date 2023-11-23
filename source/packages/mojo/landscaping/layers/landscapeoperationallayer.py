
from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING

import os

from mojo.errors.exceptions import CheckinError, CheckoutError, SemanticError

from mojo.interfaces.iexcludefilter import IExcludeFilter
from mojo.interfaces.iincludefilter import IIncludeFilter

from mojo.landscaping.layers.landscapinglayerbase import LandscapingLayerBase
from mojo.landscaping.layers.landscapeintegrationlayer import LandscapeIntegrationLayer
from mojo.landscaping.landscapedevice import LandscapeDevice
from mojo.landscaping.landscapedevicecluster import LandscapeDeviceCluster
from mojo.landscaping.cluster.nodecoordinatorbase import NodeCoordinatorBase

from mojo.landscaping.landscapeparameters import (
    LandscapeActivationParams,
    DEFAULT_LANDSCAPE_ACTIVATION_PARAMS,
)

if TYPE_CHECKING:
    from mojo.landscaping.landscape import Landscape


class LandscapeOperationalLayer(LandscapingLayerBase):

    def __init__(self, lscape: "Landscape"):
        super().__init__(lscape)

        self._operational_clusters: Dict[str, LandscapeDeviceCluster] = {}

        self._operational_clusters_pool: Dict[str, LandscapeDeviceCluster] = {}
        self._operational_clusters_outstanding: Dict[str, LandscapeDeviceCluster] = {}

        self._operational_device_pool: Dict[str, LandscapeDevice] = {}
        self._operational_device_outstanding: Dict[str, LandscapeDevice] = {}

        return

    @property
    def available_clusters(self) -> Dict[str, LandscapeDeviceCluster]:
        cluster_table = {}

        lscape = self.landscape
        with lscape.begin_locked_landscape_scope() as locked:
            cluster_table = self._operational_clusters_pool.copy()
        
        return cluster_table

    @property
    def available_devices(self) -> Dict[str, LandscapeDevice]:
        device_table = {}

        lscape = self.landscape
        with lscape.begin_locked_landscape_scope() as locked:
            device_table = self._operational_device_pool.copy()
        
        return device_table

    @property
    def operational_clusters(self) -> Dict[str, LandscapeDeviceCluster]:
        cluster_table = {}

        lscape = self.landscape
        with lscape.begin_locked_landscape_scope() as locked:
            cluster_table = self._operational_clusters.copy()
        
        return cluster_table

    def activate_coordinators(self, activation_params: LandscapeActivationParams):
        """
            Activates the coordinators by having them scan for devices in order to enhance the
            devices.
        """
        lscape = self.landscape

        layer_integ = lscape.layer_integration

        coordinators_for_power = layer_integ.coordinators_for_power
        for coord in coordinators_for_power.values():
            coord.activate(activation_params)

        coordinators_for_serial = layer_integ.coordinators_for_serial
        for coord in coordinators_for_serial.values():
            coord.activate(activation_params)

        coordinators_for_devices = layer_integ.coordinators_for_devices
        for coord in coordinators_for_devices.values():
            coord.activate(activation_params)

        return
    
    def checkin_cluster(self, cluster: LandscapeDeviceCluster):
        """
            Checkin clusters and associated devices to the operational pool.
        """

        lscape = self.landscape
        with lscape.begin_locked_landscape_scope() as locked:
            cname = cluster.name

            if cname not in self._operational_clusters_outstanding:
                err_msg_lines = [
                    f"Checkin of cluster '{cname}' that was not previously checked out."
                    "AVAILABLE POOL:"
                ]

                cluster_name_list = [ncname for ncname in self._operational_clusters_pool.keys()]
                cluster_name_list.sort()
                for ncname in cluster_name_list:
                    err_msg_lines.append(f"    {ncname}")

                err_msg_lines.append("OUTSTANDING POOL:")
                cluster_name_list = [ncname for ncname in self._operational_clusters_outstanding.keys()]
                cluster_name_list.sort()
                for ncname in cluster_name_list:
                    err_msg_lines.append(f"    {ncname}")

                err_msg = os.linesep.join(err_msg_lines)
                raise CheckinError(err_msg)
        
            for node in cluster.nodes.values():
                did = node.identity
                del self._operational_device_outstanding[did]
                self._operational_device_pool[did] = node

            del self._operational_clusters_outstanding[cname]
            self._operational_clusters_pool[cname] = cluster
            
        return

    def checkin_device(self, device: LandscapeDevice):
        """
            Checkin devices to the operational pool.
        """
        
        lscape = self.landscape
        with lscape.begin_locked_landscape_scope() as locked:
            dev_identity = device.identity

            if dev_identity not in self._operational_device_outstanding:
                err_msg_lines = [
                    f"Checkin of device '{dev_identity}' that was not previously checked out."
                    "AVAILABLE POOL:"
                ]

                device_identity_list = [did for did in self._operational_device_pool.keys()]
                device_identity_list.sort()
                for did in device_identity_list:
                    err_msg_lines.append(f"    {did}")

                err_msg_lines.append("OUTSTANDING POOL:")
                device_identity_list = [did for did in self._operational_device_outstanding.keys()]
                device_identity_list.sort()
                for did in device_identity_list:
                    err_msg_lines.append(f"    {did}")

                err_msg = os.linesep.join(err_msg_lines)
                raise CheckinError(err_msg)
            
            del self._operational_device_outstanding[dev_identity]
            self._operational_device_outstanding[dev_identity] = device

        return

    def checkout_cluster(self, cluster: LandscapeDeviceCluster):
        """
            Checkout clusters and associated devices from the operational pool.
        """

        lscape = self.landscape
        with lscape.begin_locked_landscape_scope() as locked:
            cname = cluster.name
            if cname not in self._operational_clusters:
                err_msg_lines = [
                    f"The cluster named '{cname}' does not exist.",
                    "EXISTING:"
                ]

                for exnames in self._operational_clusters:
                    err_msg_lines.append(f"    {exnames}")

                err_msg = os.lines.join(err_msg_lines)
                raise CheckoutError(err_msg)
            
            if cname not in self._operational_clusters_pool:
                if cname not in self._operational_clusters_outstanding:
                    err_msg = f"The specified cluster '{cname}' was not found in the pool or outstanding clusters."
                    raise CheckoutError(err_msg)

                # Trying to checkout a cluster that has already been checked out
                err_msg = f"The specified cluster '{cname}' has already been checked out of the pool."
                raise CheckoutError(err_msg)

            # When we checkout a cluster, we have to make sure all of its devices
            # are available for checkout
            unavailable_nodes = []
            for node in cluster.nodes.values():
                node_identity = node.identity
                if node_identity not in self._operational_device_pool:
                    unavailable_nodes.append(node)

            if len(unavailable_nodes) > 0:
                err_msg_lines = [
                    f"Not all of the nodes are available for cluster '{cname}'.",
                    "UNAVAILABLE NODES:"
                ]
                for node in unavailable_nodes:
                    err_msg_lines.append(f"    {node.name}")
                err_msg = os.linesep.join(err_msg_lines)
                raise CheckoutError(err_msg)

            # The cluster is available and all the devices are available, complete the checkout
            for node in cluster.nodes.values():
                node_identity = node.identity

                del self._operational_device_pool[node_identity]
                self._operational_device_outstanding[node_identity] = node

            del self._operational_clusters_pool[cname]
            self._operational_clusters_outstanding[cname] = cluster

        return

    def checkout_device(self, device: LandscapeDevice):
        """
            Checkout devices from the operational pool.
        """
        
        lscape = self.landscape
        with lscape.begin_locked_landscape_scope() as locked:

            device_identity = device.identity

            if device_identity not in self._operational_device_pool:
                err_msg = f"The specified device '{device_identity}' is not available for checkout."
                raise CheckoutError(err_msg)

            del self._operational_device_pool[device_identity]
            self._operational_device_outstanding[device_identity] = device

        return

    def establish_connectivity(self, activation_params: LandscapeActivationParams):
        
        lscape = self.landscape

        layer_integ = lscape.layer_integration

        coordinators_for_devices = layer_integ.coordinators_for_devices
        for coord in coordinators_for_devices.values():
            coord.establish_connectivity(activation_params)

        return
    
    def get_cluster_by_name(self, cluster_name: str) -> Union[LandscapeDeviceCluster, None]:

        cluster = None

        lscape = self.landscape

        with lscape.begin_locked_landscape_scope() as locked:
            if cluster_name in self._operational_clusters:
                cluster = self._operational_clusters[cluster_name]
        
        return cluster

    def get_clusters(self, include_filters: Optional[List[IIncludeFilter]]=None, exclude_filters: Optional[List[IExcludeFilter]]=None) -> List[LandscapeDeviceCluster]:
        """
            Gets a copy of the operational clusters list.
        """
        lscape = self.landscape

        candidate_clusters = None

        with lscape.begin_locked_landscape_scope() as locked:
            candidate_clusters = [dev for dev in self._operational_clusters]
        
        selected_clusters = []

        if include_filters is None:
            selected_clusters = candidate_clusters
        else:
            while len(candidate_clusters):
                dev = candidate_clusters.pop()
                for ifilter in include_filters:
                    if ifilter.should_include(dev):
                        selected_clusters.append(dev)
                        break

        if exclude_filters is not None:
            candidate_clusters = selected_clusters

            selected_clusters = []

            while len(candidate_clusters):
                dev = candidate_clusters.pop()
                for xfilter in exclude_filters:
                    if not xfilter.should_exclude(dev):
                        selected_clusters.append(dev)

        return selected_clusters

    def overlay_toplogy(self, activation_params: LandscapeActivationParams):

        lscape = self.landscape

        topology_info = lscape.layer_configuration.topology_info
        integ_layer = lscape.layer_integration

        if topology_info is not None:
            self._create_clusters(integ_layer, topology_info)

        self._operational_device_pool = integ_layer.integrated_devices
        self._operational_clusters_pool = self._operational_clusters.copy()

        return

    def validate_features(self, activation_params: LandscapeActivationParams):

        if activation_params.validate_features:
            pass

        return
    
    def validate_topology(self, activation_params: LandscapeActivationParams):

        if activation_params.validate_topology:
            pass

        return

    def _create_clusters(self, integ_layer: LandscapeIntegrationLayer, topology_info: Dict[str, Any]):

        table_of_device_groups = integ_layer.integrated_device_groups

        # ================= EXAMPLE ===================
        #
        #   - name: primary
        #     group: cluster/primary
        #     nodes:
        #         - mwalker-smbtest-green
        #         - mwalker-smbtest-orange
        #         - mwalker-smbtest-red
        #     spares:
        #         - mwalker-smbtest-yellow

        if "clusters" in topology_info:
            clusters = topology_info["clusters"]
            for cinfo in clusters:
                cname = cinfo["name"]
                group_name = cinfo["group"]

                nodes = []
                if "nodes" in cinfo:
                    nodes = cinfo["nodes"]
                
                spares = []
                if "spares" in cinfo:
                    spares = cinfo["spares"]

                if group_name in table_of_device_groups:
                    cgroup = table_of_device_groups[group_name]

                    coordinator: NodeCoordinatorBase = cgroup.coordinator
                    cluster = coordinator.create_cluster_for_devices(cname, cgroup, nodes, spares)

                    self._operational_clusters[cname] = cluster
        
        return
