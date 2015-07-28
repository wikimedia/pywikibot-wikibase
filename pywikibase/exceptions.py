# -*- coding: utf-8  -*-
"""
Exceptions
"""

#
# (C) Pywikibot team, 2008-2015
#
# Distributed under the terms of the MIT license.
#
from __future__ import unicode_literals


class WikiBaseError(Exception):

    """Wikibase related error."""

    pass


class CoordinateGlobeUnknownException(WikiBaseError, NotImplementedError):

    """This globe is not implemented yet in either WikiBase or pywikibase."""

    pass


class EntityTypeUnknownException(WikiBaseError):

    """The requested entity type is not recognised on this site."""

    pass
