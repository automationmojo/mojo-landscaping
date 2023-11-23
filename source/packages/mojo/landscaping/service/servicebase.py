"""
.. module:: servicebase
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module contains the :class:`BaseService` object which is a base
               class for objects that inter-operate with a computer service
               operating system.

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

from typing import TYPE_CHECKING

from mojo.landscaping.landscapeservice import LandscapeService
from mojo.landscaping.friendlyidentifier import FriendlyIdentifier


if TYPE_CHECKING:
    from mojo.landscaping.landscape import Landscape
    from mojo.landscaping.coordinators.coordinatorbase import CoordinatorBase

class ServiceBase(LandscapeService):

    def __init__(self, lscape: "Landscape", coordinator: "CoordinatorBase",
                 friendly_id:FriendlyIdentifier, service_type: str, service_config: dict):
        super().__init__(lscape, coordinator, friendly_id, service_type, service_config)

        self._host = service_config["host"]
        return

    @property
    def host(self) -> str:
        return self._host

    def enhance(self):
        """
            Called to allow a service to enhance its metadata past what is declared in the
            configuration file.  For service that only have a hint, this might trigger a
            discovery process which will result in determining connectivity with the service.
        """
        return
