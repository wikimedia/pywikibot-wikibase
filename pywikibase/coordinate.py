# -*- coding: utf-8  -*-
"""
Wikibase coordinate.
"""

#
# (C) Pywikibot team, 2008-2015
#
# Distributed under the terms of the MIT license.
#
from __future__ import unicode_literals

import math

from pywikibase.exceptions import CoordinateGlobeUnknownException


class Coordinate(object):

    """
    Class for handling and storing Coordinates.

    For now its just being used for DataSite, but
    in the future we can use it for the GeoData extension.
    """

    def __init__(self, lat, lon, alt=None, precision=None, globe='earth',
                 typ="", name="", dim=None, site=None, entity=''):
        """
        Represent a geo coordinate.

        @param lat: Latitude
        @type lat: float
        @param lon: Longitude
        @type lon: float
        @param alt: Altitute? TODO FIXME
        @param precision: precision
        @type precision: float
        @param globe: Which globe the point is on
        @type globe: str
        @param typ: The type of coordinate point
        @type typ: str
        @param name: The name
        @type name: str
        @param dim: Dimension (in meters)
        @type dim: int
        @param entity: The URL entity of a Wikibase item
        @type entity: str
        """
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self._precision = precision
        if globe:
            globe = globe.lower()
        self.globe = globe
        self._entity = entity
        self.type = typ
        self.name = name
        self._dim = dim
        self.site = site

    def __repr__(self):
        string = 'Coordinate(%s, %s' % (self.lat, self.lon)
        if self.globe != 'earth':
            string += ', globe="%s"' % self.globe
        string += ')'
        return string

    def __eq__(self, other):
        return other.toWikibase() == self.toWikibase()

    @property
    def entity(self):
        if self._entity:
            return self._entity
        return self.site.globes()[self.globe]

    def toWikibase(self):
        """
        Export the data to a JSON object for the Wikibase API.

        FIXME: Should this be in the DataSite object?
        """
        if not self._entity and self.globe not in self.site.globes():
            raise CoordinateGlobeUnknownException(
                u"%s is not supported in Wikibase yet."
                % self.globe)
        return {'latitude': self.lat,
                'longitude': self.lon,
                'altitude': self.alt,
                'globe': self.entity,
                'precision': self.precision,
                }

    @classmethod
    def fromWikibase(cls, data, site=None):
        """Constructor to create an object from Wikibase's JSON output."""
        globes = {}
        if site:
            for k in site.globes():
                globes[site.globes()[k]] = k

        globekey = data['globe']
        if globekey:
            globe = globes.get(data['globe'])
        else:
            # Default to earth or should we use None here?
            globe = 'earth'

        return cls(data['latitude'], data['longitude'],
                   data['altitude'], data['precision'],
                   globe, site=site, entity=data['globe'])

    @property
    def precision(self):
        u"""
        Return the precision of the geo coordinate.

        The biggest error (in degrees) will be given by the longitudinal error;
        the same error in meters becomes larger (in degrees) further up north.
        We can thus ignore the latitudinal error.

        The longitudinal can be derived as follows:

        In small angle approximation (and thus in radians):

        M{Δλ ≈ Δpos / r_φ}, where r_φ is radius of earth at the given latitude.
        Δλ is the error in longitude.

        M{r_φ = r cos φ}, where r is the radius of earth, φ the latitude

        Therefore::
            precision = math.degrees(
                self._dim/(radius*math.cos(math.radians(self.lat))))
        """
        if not self._precision:
            radius = 6378137  # TODO: Support other globes
            self._precision = math.degrees(
                self._dim / (radius * math.cos(math.radians(self.lat))))
        return self._precision

    def precisionToDim(self):
        """Convert precision from Wikibase to GeoData's dim."""
        raise NotImplementedError
