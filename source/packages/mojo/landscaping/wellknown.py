
__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []
__version__ = "1.0.0"
__maintainer__ = "Myron Walker"
__email__ = "myron.walker@gmail.com"
__status__ = "Development" # Prototype, Development or Production
__license__ = "MIT"

from typing import TYPE_CHECKING

from threading import RLock

from mojo.extension.wellknown import ConfiguredSuperFactorySingleton

if TYPE_CHECKING:
    from mojo.landscaping.landscape import Landscape

LANDSCAPE_SINGLETON = None

SINGLETON_LOCK = RLock()

def LandscapeSingleton() -> "Landscape":
    """
        Instantiates and gets a global instance of the :class:`Landscape` class.  The
        :class:`Landscape` provides for management of resources.
    """

    global SINGLETON_LOCK
    global LANDSCAPE_SINGLETON

    # If the singleton is already set, don't bother grabbing a lock
    # to set it.  The full path of the setting of the singleton will only
    # ever be taken once
    if LANDSCAPE_SINGLETON is None:
        super_factory = ConfiguredSuperFactorySingleton()

        SINGLETON_LOCK.acquire()
        try:
            from mojo.landscaping.landscapingextensionprotocol import LandscapingExtensionProtocol

            if LANDSCAPE_SINGLETON is None:
                LandscapeType = super_factory.get_override_types_by_order(
                    LandscapingExtensionProtocol.get_landscape_type)

                if LandscapeType is None:
                    from mojo.landscaping.landscape import Landscape
                    LandscapeType = Landscape

                LANDSCAPE_SINGLETON = LandscapeType()
        finally:
            SINGLETON_LOCK.release()

    return LANDSCAPE_SINGLETON

