# -*- coding: utf-8  -*-
"""
Wikibase Quantity.
"""

#
# (C) Pywikibot team, 2008-2015
#
# Distributed under the terms of the MIT license.
#
from __future__ import unicode_literals

import json


class WbQuantity(object):

    """A Wikibase quantity representation."""

    def __init__(self, amount, unit=None, error=None):
        u"""
        Create a new WbQuantity object.

        @param amount: number representing this quantity
        @type amount: float
        @param unit: not used (only unit-less quantities are supported)
        @param error: the uncertainty of the amount (e.g. ±1)
        @type error: float, or tuple of two floats, where the first value is
                     the upper error and the second is the lower error value.
        """
        if amount is None:
            raise ValueError('No amount given')
        if unit is None:
            unit = '1'
        self.amount = amount
        self.unit = unit
        upperError = lowerError = 0
        if isinstance(error, tuple):
            upperError, lowerError = error
        elif error is not None:
            upperError = lowerError = error
        self.upperBound = self.amount + upperError
        self.lowerBound = self.amount - lowerError

    def toWikibase(self):
        """Convert the data to a JSON object for the Wikibase API."""
        data = {'amount': self._normalize_value(self.amount),
                'upperBound': self._normalize_value(self.upperBound),
                'lowerBound': self._normalize_value(self.lowerBound),
                'unit': str(self.unit)
                }
        return data

    @classmethod
    def fromWikibase(cls, wb):
        """
        Create a WbQuanity from the JSON data given by the Wikibase API.

        @param wb: Wikibase JSON
        """
        amount = eval(wb['amount'])
        upperBound = eval(wb['upperBound'])
        lowerBound = eval(wb['lowerBound'])
        error = (upperBound - amount, amount - lowerBound)
        return cls(amount, wb['unit'], error)

    def __str__(self):
        return json.dumps(self.toWikibase(), indent=4, sort_keys=True,
                          separators=(',', ': '))

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return (u"WbQuantity(amount=%(amount)s, upperBound=%(upperBound)s, "
                u"lowerBound=%(lowerBound)s, unit=%(unit)s)" % self.__dict__)

    @staticmethod
    def _normalize_value(value):
        if value > 0:
            value = "+" + str(value)
        return value
