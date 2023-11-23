"""
.. module:: friendlyidentifier
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Module containing the :class:`FriendlyIdentifier` class which can
               be used to reference devices by a short name while allowing the landscaping
               modules to link or associate a full identifier with the short name.

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

from typing import Optional, Union

import re

from mojo.errors.exceptions import SemanticError

class FriendlyIdentifier:

    def __init__(self, full_identifier: str, hint: str, identity_match: Optional[Union[re.Pattern, str]]=None):
        self._full_identifier = full_identifier
        self._hint = hint

        self._identity_match = identity_match
        if self._identity_match is not None and isinstance(identity_match, str):
            self._identity_match = re.compile(identity_match)

        # If a short_match expression is specified, it must have a match in the full identifier.
        if self._identity_match is not None:
            mobj = self._identity_match.match(self._full_identifier)
            if mobj is None:
                errmsg = "The specified identifier is not compatible with the short match expression provided."
                raise SemanticError(errmsg)
        return
    
    @property
    def full_identifier(self):
        """
            The full identifier used to reference something.
        """
        return self._full_identifier
    
    @property
    def hint(self):
        """
            A reduced name that represents a adequatly unique portion
            of the full identifier.  
        """
        return self._hint

    @property
    def identity(self):
        id = None

        if self._identity_match is not None:
            mobj = self._identity_match.match(self._full_identifier)
            id = mobj.groups()[0]
        elif self._hint is not None:
            id = self._hint
        else:
            id = self._full_identifier

        return id

    def match(self, hint:str) -> bool:
        """
            Indicates if the hint provided provides a match for this FriendlyIdentifier.
        """
        result = False
        if self._full_identifier.find(hint) > -1 and hint.find(self._hint) > -1:
            result = True
        return result

    def relationship(self) -> str:
        rel = self._hint + " -> " + self._full_identifier
        return rel

    def update_full_identifier(self, full_identifer: str):
        self._full_identifier = full_identifer
        return

    def __eq__(self, other):
        result = False

        if isinstance(other, FriendlyIdentifier):
            result = self._full_identifier == self.full_identifier
        elif isinstance(other, str) and self._full_identifier.find(other) > -1:
            result = True
        else:
            errmsg = "Unable to compare FriendlyIdentifier with type '{}'".format(type(other))
            raise SemanticError(errmsg)
            
        return result

    def __str__(self):
        return self.identity