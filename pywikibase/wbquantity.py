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
from decimal import Decimal

import json


class WbQuantity(object):

    """A Wikibase quantity representation."""

    _items = ('amount', 'upperBound', 'lowerBound', 'unit')

    @staticmethod
    def _todecimal(value):
        """
        Convert a string to a Decimal for use in WbQuantity.

        None value is returned as is.

        @param value: decimal number to convert
        @type value: str
        @rtype: Decimal
        """
        if isinstance(value, Decimal):
            return value
        elif value is None:
            return None
        return Decimal(str(value))

    @staticmethod
    def _fromdecimal(value):
        """
        Convert a Decimal to a string representation suitable for WikiBase.

        None value is returned as is.

        @param value: decimal number to convert
        @type value: Decimal
        @rtype: str
        """
        if value is None:
            return None
        return format(value, "+g")

    def __init__(self, amount, unit=None, error=None):
        u"""
        Create a new WbQuantity object.

        @param amount: number representing this quantity
        @type amount: string or Decimal. Other types are accepted, and converted
                      via str to Decimal.
        @param unit: not used (only unit-less quantities are supported)
        @param error: the uncertainty of the amount (e.g. ±1)
        @type error: same as amount, or tuple of two values, where the
                     first value is the upper error and the second
                     is the lower error value.
        """
        if amount is None:
            raise ValueError('no amount given')
        if unit is None:
            unit = '1'

        self.amount = self._todecimal(amount)
        self.unit = unit

        if error is None:
            self.upperBound = self.lowerBound = None
        else:
            if error is None:
                self.upperBound = self.lowerBound = Decimal(0)
            elif isinstance(error, tuple):
                upperError = self._todecimal(error[0])
                lowerError = self._todecimal(error[1])
            else:
                upperError = lowerError = self._todecimal(error)

            self.upperBound = self.amount + upperError
            self.lowerBound = self.amount - lowerError

    def toWikibase(self):
        """
        Convert the data to a JSON object for the Wikibase API.

        @return: Wikibase JSON
        @rtype: dict
        """
        json = {'amount': self._fromdecimal(self.amount),
                'upperBound': self._fromdecimal(self.upperBound),
                'lowerBound': self._fromdecimal(self.lowerBound),
                'unit': self.unit
                }
        return json

    @classmethod
    def fromWikibase(cls, wb):
        """
        Create a WbQuanity from the JSON data given by the Wikibase API.

        @param wb: Wikibase JSON
        @type wb: dict
        @rtype: pywikibot.WbQuanity
        """
        amount = cls._todecimal(wb['amount'])
        upperBound = cls._todecimal(wb.get('upperBound'))
        lowerBound = cls._todecimal(wb.get('lowerBound'))
        error = None
        if (upperBound and lowerBound):
            error = (upperBound - amount, amount - lowerBound)
        return cls(amount, wb['unit'], error)

    def __str__(self):
        return json.dumps(self.toWikibase(), indent=4, sort_keys=True,
                          separators=(',', ': '))

    def __repr__(self):

        values = ((attr, getattr(self, attr)) for attr in self._items)
        attrs = ', '.join('{0}={1}'.format(attr, value)
                          for attr, value in values)
        return '{0}({1})'.format(self.__class__.__name__, attrs)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
