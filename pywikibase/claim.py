# -*- coding: utf-8  -*-
"""
Handling claims in a Wikibase entity.
"""

#
# (C) Pywikibot team, 2008-2015
#
# Distributed under the terms of the MIT license.
#
from __future__ import unicode_literals
from collections import defaultdict, OrderedDict

from pywikibase import Coordinate
from pywikibase import WbTime
from pywikibase import WbQuantity
from pywikibase import Property
import pywikibase.itempage

try:
    unicode = unicode
except NameError:
    basestring = (str, bytes)


class Claim(Property):

    """
    A Claim on a Wikibase entity.

    Claims are standard claims as well as references.
    """
    TARGET_CONVERTER = {
        'wikibase-item': lambda value:
            pywikibase.itempage.ItemPage('Q' + str(value['numeric-id'])),
        'globe-coordinate': Coordinate.fromWikibase,
        'time': lambda value: WbTime.fromWikibase(value),
        'quantity': lambda value: WbQuantity.fromWikibase(value),
    }

    def __init__(self, pid, snak=None, hash=None, isReference=False,
                 isQualifier=False, **kwargs):
        """
        Constructor.

        Defined by the "snak" value, supplemented by pid

        @param pid: property id, with "P" prefix
        @param snak: snak identifier for claim
        @param hash: hash identifier for references
        @param isReference: whether specified claim is a reference
        @param isQualifier: whether specified claim is a qualifier
        """
        Property.__init__(self, pid, **kwargs)
        self.snak = snak
        self.hash = hash
        self.isReference = isReference
        self.isQualifier = isQualifier
        if self.isQualifier and self.isReference:
            raise ValueError(
                u'Claim cannot be both a qualifier and reference.')
        self.sources = []
        self.qualifiers = OrderedDict()
        self.target = None
        self.snaktype = 'value'
        self.rank = 'normal'
        self.on_item = None  # The item it's on

    @classmethod
    def fromJSON(cls, data):
        """
        Create a claim object from JSON returned in the API call.

        @param data: JSON containing claim data
        @type data: dict

        @return: Claim
        """
        datatype = data['mainsnak'].get('datatype')
        if not datatype:
            datatype = data['mainsnak'].get('datavalue', {}).get('type')
        if 'datatype' not in data['mainsnak']:
            datatype = cls._format_datatype(datatype)
        claim = cls(data['mainsnak']['property'],
                    datatype=datatype)
        if 'id' in data:
            claim.snak = data['id']
        elif 'hash' in data:
            claim.isReference = True
            claim.hash = data['hash']
        else:
            claim.isQualifier = True
        claim.snaktype = data['mainsnak']['snaktype']
        if claim.getSnakType() == 'value':
            value = data['mainsnak']['datavalue']['value']
            # The default covers string, url types
            claim.target = Claim.TARGET_CONVERTER.get(
                claim.type, lambda value: value)(value)
        if 'rank' in data:  # References/Qualifiers don't have ranks
            claim.rank = data['rank']
        if 'references' in data:
            for source in data['references']:
                claim.sources.append(cls.referenceFromJSON(source))
        if 'qualifiers' in data:
            for prop in data['qualifiers-order']:
                claim.qualifiers[prop] = [
                    cls.qualifierFromJSON(qualifier)
                    for qualifier in data['qualifiers'][prop]]
        return claim

    @classmethod
    def referenceFromJSON(cls, data):
        """
        Create a dict of claims from reference JSON returned in the API call.

        Reference objects are represented a
        bit differently, and require some
        more handling.

        @return: dict
        """
        source = OrderedDict()

        # Before #84516 Wikibase did not implement snaks-order.
        # https://gerrit.wikimedia.org/r/#/c/84516/
        if 'snaks-order' in data:
            prop_list = data['snaks-order']
        else:
            prop_list = data['snaks'].keys()

        for prop in prop_list:
            for claimsnak in data['snaks'][prop]:
                claim = cls.fromJSON({'mainsnak': claimsnak,
                                      'hash': data['hash']})
                if claim.getID() not in source:
                    source[claim.getID()] = []
                source[claim.getID()].append(claim)
        return source

    @classmethod
    def qualifierFromJSON(cls, data):
        """
        Create a Claim for a qualifier from JSON.

        Qualifier objects are represented a bit
        differently like references, but I'm not
        sure if this even requires it's own function.

        @return: Claim
        """
        return cls.fromJSON({'mainsnak': data,
                             'hash': data['hash']})

    def __eq__(self, other):
        return other.toJSON() == self.toJSON()

    def toJSON(self):
        """
        Create dict suitable for the MediaWiki API.

        @rtype: dict
        """
        data = {
            'mainsnak': {
                'snaktype': self.snaktype,
                'property': self.getID()
            },
            'type': 'statement'
        }
        if hasattr(self, 'snak') and self.snak is not None:
            data['id'] = self.snak
        if hasattr(self, 'rank') and self.rank is not None:
            data['rank'] = self.rank
        if self.getSnakType() == 'value':
            data['mainsnak']['datatype'] = self.type
            data['mainsnak']['datavalue'] = self._formatDataValue()
        if self.isQualifier or self.isReference:
            data = data['mainsnak']
            if hasattr(self, 'hash') and self.hash is not None:
                data['hash'] = self.hash
        else:
            if len(self.qualifiers) > 0:
                data['qualifiers'] = {}
                data['qualifiers-order'] = list(self.qualifiers.keys())
                for prop, qualifiers in self.qualifiers.items():
                    for qualifier in qualifiers:
                        qualifier.isQualifier = True
                    data['qualifiers'][prop] = [qualifier.toJSON()
                                                for qualifier in qualifiers]
            if len(self.sources) > 0:
                data['references'] = []
                for collection in self.sources:
                    reference = {'snaks': {},
                                 'snaks-order': list(collection.keys())}
                    for prop, val in collection.items():
                        reference['snaks'][prop] = []
                        for source in val:
                            source.isReference = True
                            src_data = source.toJSON()
                            if 'hash' in src_data:
                                if 'hash' not in reference:
                                    reference['hash'] = src_data['hash']
                                del src_data['hash']
                            reference['snaks'][prop].append(src_data)
                    data['references'].append(reference)
        return data

    def setTarget(self, value):
        """
        Set the target value in the local object.

        @param value: The new target value.
        @type value: object

        @exception ValueError: if value is not of the type
            required for the Claim type.
        """
        value_class = self.types[self.type]
        if not isinstance(value, value_class):
            raise ValueError("%s is not type %s."
                             % (value, value_class))
        self.target = value

    def getTarget(self):
        """
        Return the target value of this Claim.

        None is returned if no target is set

        @return: object
        """
        return self.target

    def getSnakType(self):
        """
        Return the type of snak.

        @return: str ('value', 'somevalue' or 'novalue')
        """
        return self.snaktype

    def setSnakType(self, value):
        """Set the type of snak.

        @param value: Type of snak
        @type value: str ('value', 'somevalue', or 'novalue')
        """
        if value in ['value', 'somevalue', 'novalue']:
            self.snaktype = value
        else:
            raise ValueError(
                "snaktype must be 'value', 'somevalue', or 'novalue'.")

    def getRank(self):
        """Return the rank of the Claim."""
        return self.rank

    def setRank(self, rank):
        """Set the rank of the Claim."""
        self.rank = rank

    def getSources(self):
        """
        Return a list of sources, each being a list of Claims.

        @return: list
        """
        return self.sources

    def addSource(self, claim, **kwargs):
        """
        Add the claim as a source.

        @param claim: the claim to add
        @type claim: pywikibase.Claim
        """
        self.addSources([claim], **kwargs)

    def addSources(self, claims, **kwargs):
        """
        Add the claims as one source.

        @param claims: the claims to add
        @type claims: list of pywikibase.Claim
        """
        source = defaultdict(list)
        for claim in claims:
            source[claim.getID()].append(claim)
        self.sources.append(source)

    def removeSource(self, source, **kwargs):
        """
        Remove the source.

        @param source: the sources to remove
        @type source: pywikibase.Claim
        """
        self.removeSources([source], **kwargs)

    def removeSources(self, sources):
        """
        Remove the sources.

        @param sources: the sources to remove
        @type sources: list of pywikibase.Claim
        """
        for source in sources:
            source_dict = defaultdict(list)
            source_dict[source.getID()].append(source)
            self.sources.remove(source_dict)

    def addQualifier(self, qualifier):
        """Add the given qualifier.

        @param qualifier: the qualifier to add
        @type qualifier: Claim
        """
        qualifier.isQualifier = True
        if self.isQualifier is True or self.isReference is True:
            raise ValueError('Qualifiers and Sources can not have qualifier.')
        if qualifier.getID() in self.qualifiers:
            self.qualifiers[qualifier.getID()].append(qualifier)
        else:
            self.qualifiers[qualifier.getID()] = [qualifier]

    def target_equals(self, value):
        """
        Check whether the Claim's target is equal to specified value.

        The function checks for:
        - ItemPage ID equality
        - WbTime year equality
        - Coordinate equality, regarding precision
        - direct equality

        @param value: the value to compare with
        @return: true if the Claim's target is equal to the value provided,
            false otherwise
        @rtype: bool
        """
        import pywikibase.itempage
        if (isinstance(self.target, pywikibase.itempage.ItemPage) and
                isinstance(value, basestring) and
                self.target.id == value):
            return True

        if (isinstance(self.target, WbTime) and
                not isinstance(value, WbTime) and
                self.target.year == int(value)):
            return True

        if (isinstance(self.target, Coordinate) and
                isinstance(value, basestring)):
            coord_args = [float(x) for x in value.split(',')]
            if len(coord_args) >= 3:
                precision = coord_args[2]
            else:
                precision = 0.0001  # Default value (~10 m at equator)
            try:
                if self.target.precision is not None:
                    precision = max(precision, self.target.precision)
            except TypeError:
                pass

            if (abs(self.target.lat - coord_args[0]) <= precision and
                    abs(self.target.lon - coord_args[1]) <= precision):
                return True

        if self.target == value:
            return True

        return False

    def has_qualifier(self, qualifier_id, target):
        """
        Check whether Claim contains specified qualifier.

        @param qualifier_id: id of the qualifier
        @type qualifier_id: str
        @param target: qualifier target to check presence of
        @return: true if the qualifier was found, false otherwise
        @rtype: bool
        """
        if self.isQualifier or self.isReference:
            raise ValueError(u'Qualifiers and references cannot have '
                             u'qualifiers.')

        for qualifier in self.qualifiers.get(qualifier_id, []):
            if qualifier.target_equals(target):
                return True
        return False

    def _formatValue(self):
        """
        Format the target into the proper JSON value that Wikibase wants.

        @return: JSON value
        @rtype: dict
        """
        if self.type == 'wikibase-item':
            value = {'entity-type': 'item',
                     'numeric-id': self.getTarget().getID(numeric=True)}
        elif self.type in ('string', 'url', 'commonsMedia'):
            value = self.getTarget()
        elif self.type in ('globe-coordinate', 'time', 'quantity'):
            value = self.getTarget().toWikibase()
        else:
            raise NotImplementedError('%s datatype is not supported yet.'
                                      % self.type)
        return value

    def _formatDataValue(self):
        """
        Format the target into the proper JSON datavalue that Wikibase wants.

        @return: Wikibase API representation with type and value.
        @rtype: dict
        """
        return {'value': self._formatValue(),
                'type': self.value_types.get(self.type, self.type)
                }

    @staticmethod
    def _format_datatype(datatype):
        if datatype == 'wikibase-entityid':
            return 'wikibase-item'
        if datatype == 'globecoordinate':
            return 'globe-coordinate'
        return datatype
