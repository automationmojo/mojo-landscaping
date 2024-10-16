

from mojo.landscaping.wellknown import LandscapeSingleton

from mojo.landscaping.landscape import Landscape

class AutomationPod:
    """
        The :class:`AutomationPodBase` object serves as a base class for derived :class:`AutomationPodBase` objects.
    """

    def __init__(self):
        self._lscape = LandscapeSingleton()
        return
    
    @property
    def landscape(self) -> Landscape:
        return self._lscape
