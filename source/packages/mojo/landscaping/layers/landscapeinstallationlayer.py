"""
.. module:: landscapeinstallationlayer
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`LandscapeInstallationLayer` class which is used
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

from typing import Dict, TYPE_CHECKING

from mojo.extension.wellknown import ConfiguredSuperFactorySingleton

from mojo.xmods.injection.coupling.integrationcoupling import IntegrationCouplingType

from mojo.landscaping.landscapingextensionprotocol import LandscapingExtensionProtocol
from mojo.landscaping.layers.landscapinglayerbase import LandscapingLayerBase

if TYPE_CHECKING:
    from mojo.landscaping.landscape import Landscape


class LandscapeInstallationLayer(LandscapingLayerBase):

    def __init__(self, lscape: "Landscape"):
        super().__init__(lscape)

        self._installed_integration_couplings: Dict[str, IntegrationCouplingType] = {}

        self._load_integration_coupling_types()
        return

    @property
    def installed_integration_couplings(self) -> Dict[str, IntegrationCouplingType]:
        """
            Returns a table of the installed integration couplings found.
        """
        return self._installed_integration_couplings

    def _load_integration_coupling_types(self):

        super_factory = ConfiguredSuperFactorySingleton()
        for integration_coupling_types in super_factory.iterate_override_types_for_each(
            LandscapingExtensionProtocol.get_integration_coupling_types):

            for itype in integration_coupling_types:
                itype: IntegrationCouplingType = itype
                integration_key = itype.get_integration_key()
                self._installed_integration_couplings[integration_key] = itype

        return
