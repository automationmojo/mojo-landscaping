"""
.. module:: landscapedevicecluster
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module contains the :class:`LandscapeDeviceCluster` object which 
               represents a cluster of devices that are compute nodes in a
               computer or storage cluster.

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

from typing import Dict

from mojo.landscaping.cluster.nodebase import NodeBase
from mojo.landscaping.landscapedevicegroup import LandscapeDeviceGroup

class LandscapeDeviceCluster:
    """
        A :class:`LandscapeDeviceCluster` object is used to manage a group of
        nodes that are part of a computer cluster and a collection of spares
        that are eligible to participate in the cluster.
    """

    def __init__(self, name: str, nodes: Dict[str, NodeBase], spares: Dict[str, NodeBase],
                 group: LandscapeDeviceGroup) -> None:
        self._name = name
        self._nodes = nodes
        self._spares = spares
        self._group = group
        return

    @property
    def group(self) -> LandscapeDeviceGroup:
        return self._group

    @property
    def name(self) -> str:
        return self._name

    @property
    def nodes(self) -> Dict[str, NodeBase]:
        return self._nodes
    
    @property
    def spares(self) -> Dict[str, NodeBase]:
        return self._spares
