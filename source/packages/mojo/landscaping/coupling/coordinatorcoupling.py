"""
.. module:: coordinatorcoupling
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`CoordinatorCoupling` class and associated reflection methods.
        The :class:`CoordinatorCoupling` derived classes can be used to integraton automation resources and roles
        into the test environment.

.. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []



from typing import TYPE_CHECKING

from mojo.errors.exceptions import NotOverloadedError

from mojo.xmods.injection.coupling.integrationcoupling import IntegrationCoupling

if TYPE_CHECKING:
    from mojo.landscaping.landscape import Landscape

class CoordinatorCoupling(IntegrationCoupling):
    """
        The :class:`CoordinatorCoupling` object serves as the base object for the declaration of an
        automation integration coordinator coupling.
    """

    coordinator = None

    @classmethod
    def create_coordinator(cls, landscape: "Landscape") -> object:
        """
            This API is called so that the landscape can create a coordinator for a given coordinator
            integration role.
        """
        raise NotOverloadedError("This method must be overridden by derived coordinator classes.")

