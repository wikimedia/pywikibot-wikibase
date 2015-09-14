# -*- coding: utf-8  -*-
"""
Handling a Wikibase property.
"""

#
# (C) Pywikibot team, 2008-2015
#
# Distributed under the terms of the MIT license.
#
from __future__ import unicode_literals

from pywikibase.coordinate import Coordinate
from pywikibase.wbtime import WbTime
from pywikibase.wbquantity import WbQuantity

try:
    unicode = unicode
except NameError:
    basestring = (str, bytes)


class Property():

    """
    A Wikibase property.

    While every Wikibase property has a Page on the data repository,
    this object is for when the property is used as part of another concept
    where the property is not _the_ Page of the property.

    For example, a claim on an ItemPage has many property attributes, and so
    it subclasses this Property class, but a claim does not have Page like
    behaviour and semantics.
    """
    from pywikibase.itempage import ItemPage  # noqa
    types = {'wikibase-item': ItemPage,
             'string': basestring,
             'commonsMedia': basestring,
             'globe-coordinate': Coordinate,
             'url': basestring,
             'time': WbTime,
             'quantity': WbQuantity,
             }

    value_types = {'wikibase-item': 'wikibase-entityid',
                   'commonsMedia': 'string',
                   'url': 'string',
                   'globe-coordinate': 'globecoordinate',
                   }

    def __init__(self, id=None, datatype=None):
        """
        Constructor.

        @param datatype: datatype of the property;
            if not given, it will be queried via the API
        @type datatype: basestring
        """
        self.id = id.upper()
        if datatype:
            self._type = datatype

    @property
    def type(self):
        """
        Return the type of this property.

        @return: str
        """
        if not hasattr(self, '_type'):
            raise ValueError('Please provide type')
        return self._type

    def getID(self, numeric=False):
        """
        Get the identifier of this property.

        @param numeric: Strip the first letter and return an int
        @type numeric: bool
        """
        if numeric:
            return int(self.id[1:])
        else:
            return self.id
