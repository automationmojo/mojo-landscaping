"""
.. module:: landscapeintegrationlayer
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`LandscapeLayerBase` class which is used
               to provide common functionality to the different landscape layers.

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

import logging
import weakref

if TYPE_CHECKING:
    from mojo.landscaping.landscape import Landscape


class LandscapingLayerBase:

    logger = logging.getLogger()

    def __init__(self, lscape: "Landscape"):
        self._lscape_ref = weakref.ref(lscape)
        return
    
    @property
    def landscape(self):
        lscape = self._lscape_ref()
        return lscape
