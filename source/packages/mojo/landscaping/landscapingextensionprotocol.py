"""
.. module:: extensionpoints
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing functions and classes that help create and work with
               configuration based extension objects.

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


from typing import List, Protocol, Type

from mojo.xmods.injection.coupling.integrationcoupling import IntegrationCoupling

class LandscapingExtensionProtocol(Protocol):

    ext_protocol_name = "mojo-landscaping-extension-protocol"

    @classmethod
    def get_landscape_type(self) -> Type:
        """
            Used to lookup and return the most relevant `Landscape` type.
        """

    @classmethod
    def get_integration_coupling_types(self) -> List[Type[IntegrationCoupling]]:
        """
            Used to lookup and return the most relevant list of integration coupling types.
        """

    

