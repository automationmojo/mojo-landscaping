"""
.. module:: landscapedevicegroup
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module contains the :class:`LandscapeDeviceGroup` object which is a
               container object which groups :class:`Landscapedevice` object with
               thier group name.

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

from typing import List

import weakref

from mojo.landscaping.landscapedevice import LandscapeDevice

class LandscapeDeviceGroup:
    """
        A :class:`LandscapeDeviceGroup` object is used to group devices to an associated
        grouping label.
    """

    def __init__(self, label: str, items: List[LandscapeDevice]) -> None:
        self._label = label
        self._items = items
        
        self._coord_ref = weakref.ref(self._items[0].coordinator)
        return
    
    @property
    def coordinator(self):
        return self._coord_ref()

    @property
    def items(self):
        return self._items

    @property
    def label(self):
        return self._label
