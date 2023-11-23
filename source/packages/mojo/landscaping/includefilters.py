"""
.. module:: includefilters
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing various device include filters.

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

from typing import Any

from mojo.interfaces.iincludefilter import IIncludeFilter

from mojo.landscaping.landscapedevice import LandscapeDevice
from mojo.landscaping.landscapeservice import LandscapeService

class IncludeDeviceBase(IIncludeFilter):
    """
        Base include type for device based includes
    """

class IncludeDeviceConfigBase(IIncludeFilter):
    """
        Base include type for device based includes
    """

class IncludeServiceBase(IIncludeFilter):
    """
        Base include type for service based includes
    """

class IncludeDeviceByDeviceType(IncludeDeviceBase):

    def __init__(self, device_type: str) -> None:
        super().__init__()
        self._device_type = device_type
        return

    def should_include(self, check_object: Any) -> bool:
        """
            Determines if a device matches an include criteria internalized in the filter object.

            :param check_object: The object to check for a match with the exclude criteria.
        """
        include = False

        if isinstance(check_object, LandscapeDevice):
            lsdevice: LandscapeDevice = check_object
            if lsdevice.device_type == self._device_type:
                include = True

        return include


class IncludeDeviceByDeviceTypeAndRole(IncludeDeviceBase):

    def __init__(self, device_type: str, role: str) -> None:
        super().__init__()
        self._device_type = device_type
        self._role = role
        return

    def should_include(self, check_object: Any) -> bool:
        """
            Determines if a device matches an include criteria internalized in the filter object.

            :param check_object: The object to check for a match with the exclude criteria.
        """
        include = False

        if isinstance(check_object, LandscapeDevice):
            lsdevice: LandscapeDevice = check_object
            if lsdevice.device_type == self._device_type and lsdevice.role == self._role:
                include = True

        return include


class IncludeDeviceByGroup(IncludeDeviceBase):

    def __init__(self, group: str) -> None:
        super().__init__()
        self._group = group
        return

    def should_include(self, check_object: Any) -> bool:
        """
            Determines if a device matches an include criteria internalized in the filter object.

            :param check_object: The object to check for a match with the exclude criteria.
        """
        include = False

        if isinstance(check_object, LandscapeDevice):
            lsdevice: LandscapeDevice = check_object
            if lsdevice.group == self._group:
                include = True

        return include


class IncludeDeviceByName(IncludeDeviceBase):

    def __init__(self, name: str) -> None:
        super().__init__()
        self._name = name
        return

    def should_include(self, check_object: Any) -> bool:
        """
            Determines if a device matches an include criteria internalized in the filter object.

            :param check_object: The object to check for a match with the exclude criteria.
        """
        include = False

        if isinstance(check_object, LandscapeDevice):
            lsdevice: LandscapeDevice = check_object
            if lsdevice.name == self._name:
                include = True

        return include


class IncludeDeviceByRole(IncludeDeviceBase):

    def __init__(self, role: str) -> None:
        super().__init__()
        self._role = role
        return

    def should_include(self, check_object: Any) -> bool:
        """
            Determines if a device matches an include criteria internalized in the filter object.

            :param check_object: The object to check for a match with the exclude criteria.
        """
        include = False

        if isinstance(check_object, LandscapeDevice):
            lsdevice: LandscapeDevice = check_object
            if lsdevice.role == self._role:
                include = True

        return include


class IncludeDeviceConfigByDeviceType(IncludeDeviceConfigBase):

    def __init__(self, device_type: str) -> None:
        super().__init__()
        self._device_type = device_type
        return

    def should_include(self, check_object: Any) -> bool:
        """
            Determines if a device config matches an include criteria internalized in the filter object.

            :param check_object: The object to check for a match with the exclude criteria.
        """
        include = False

        if isinstance(check_object, dict):
            devconfig: dict = check_object
            if devconfig["deviceType"] == self._device_type:
                include = True

        return include

class IncludeServiceByName(IncludeServiceBase):

    def __init__(self, name: str) -> None:
        super().__init__()
        self._name = name
        return

    def should_include(self, check_object: Any) -> bool:
        """
            Determines if a device matches an include criteria internalized in the filter object.

            :param check_object: The object to check for a match with the exclude criteria.
        """
        include = False

        if isinstance(check_object, LandscapeService):
            lsdevice: LandscapeService = check_object
            if lsdevice.name == self._name:
                include = True

        return include
