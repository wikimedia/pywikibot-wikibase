# -*- coding: utf-8  -*-
"""
Handling a Wikibase entity.
"""

#
# (C) Pywikibot team, 2008-2015
#
# Distributed under the terms of the MIT license.
#
from __future__ import unicode_literals
from collections import defaultdict, Counter

import json

try:
    unicode = unicode
except NameError:
    basestring = (str, bytes)


class WikibasePage(object):

    """
    The base page for the Wikibase extension.

    There should be no need to instantiate this directly.
    """

    def __init__(self, id=None):
        self.id = id

    def __eq__(self, other):
        if isinstance(other, basestring):
            return other == self.id
        return other.id == self.id

    def get(self, content=None):
        """
        Fetch all page data, and cache it.

        @param force: override caching
        @type force: bool
        @param content: content
        @param args: may be used to specify custom props.
        """
        if content:
            if isinstance(content, dict):
                self._content = content
            else:
                self._content = json.loads(content)
        if not hasattr(self, '_content'):
            raise ValueError('You must provide some content.')

        if 'id' in self._content or 'title' in self._content:
            self.id = self._content.get('title', self._content['id'])
        # aliases
        self.aliases = {}
        if 'aliases' in self._content:
            for lang in self._content['aliases']:
                self.aliases[lang] = list()
                for value in self._content['aliases'][lang]:
                    self.aliases[lang].append(value['value'])

        # labels
        self.labels = {}
        if 'labels' in self._content:
            for lang in self._content['labels']:
                if 'removed' not in self._content['labels'][lang]:  # Bug 54767
                    self.labels[lang] = self._content['labels'][lang]['value']

        # descriptions
        self.descriptions = {}
        if 'descriptions' in self._content:
            for lang in self._content['descriptions']:
                self.descriptions[lang] = self._content[
                    'descriptions'][lang]['value']

        # claims
        from pywikibase.claim import Claim
        self.claims = {}
        if 'claims' in self._content:
            for pid in self._content['claims']:
                self.claims[pid] = []
                for claim in self._content['claims'][pid]:
                    c = Claim.fromJSON(claim)
                    c.on_item = self
                    self.claims[pid].append(c)

        return {'aliases': self.aliases,
                'labels': self.labels,
                'descriptions': self.descriptions,
                'claims': self.claims,
                }

    def _diff_to(self, type_key, key_name, value_name, diffto, data):
        assert type_key not in data, 'Key type must be defined in data'
        source = getattr(self, type_key).copy()
        diffto = {} if not diffto else diffto.get(type_key, {})
        new = set(source.keys())
        for key in diffto:
            if key in new:
                if source[key] == diffto[key][value_name]:
                    del source[key]
            else:
                source[key] = ''
        for key, value in source.items():
            source[key] = {key_name: key, value_name: value}
        if source:
            data[type_key] = source

    def toJSON(self, diffto=None):
        """
        Create JSON suitable for Wikibase API.

        When diffto is provided, JSON representing differences
        to the provided data is created.

        @param diffto: JSON containing claim data
        @type diffto: dict

        @return: dict
        """
        data = {}
        self._diff_to('labels', 'language', 'value', diffto, data)

        self._diff_to('descriptions', 'language', 'value', diffto, data)

        aliases = self.aliases
        if diffto and 'aliases' in diffto:
            for lang in set(diffto['aliases'].keys()) - set(aliases.keys()):
                aliases[lang] = []
        for lang, strings in list(aliases.items()):
            if diffto and 'aliases' in diffto and lang in diffto['aliases']:
                empty = len(diffto['aliases'][lang]) - len(strings)
                if empty > 0:
                    strings += [''] * empty
                elif Counter(val['value'] for val
                             in diffto['aliases'][lang]) == Counter(strings):
                    del aliases[lang]
            if lang in aliases:
                aliases[lang] = [{'language': lang, 'value': i}
                                 for i in strings]

        if aliases:
            data['aliases'] = aliases

        claims = {}
        for prop in self.claims:
            if len(self.claims[prop]) > 0:
                claims[prop] = [claim.toJSON() for claim in self.claims[prop]]

        if diffto and 'claims' in diffto:
            temp = defaultdict(list)
            claim_ids = set()

            diffto_claims = diffto['claims']

            for prop in claims:
                for claim in claims[prop]:
                    if (prop not in diffto_claims or
                            claim not in diffto_claims[prop]):
                        temp[prop].append(claim)

                    claim_ids.add(claim['id'])

            for prop, prop_claims in diffto_claims.items():
                for claim in prop_claims:
                    if 'id' in claim and claim['id'] not in claim_ids:
                        temp[prop].append({'id': claim['id'], 'remove': ''})

            claims = temp

        if claims:
            data['claims'] = claims
        return data

    def getID(self, numeric=False, force=False):
        """
        Get the entity identifier.

        @param numeric: Strip the first letter and return an int
        @type numeric: bool
        @param force: Force an update of new data
        @type force: bool
        """
        if not hasattr(self, 'id') or force:
            self.get(force=force)
        if numeric:
            return int(self.id[1:]) if self.id != '-1' else -1

        return self.id

    @classmethod
    def _normalizeData(cls, data):
        """
        Helper function to expand data into the Wikibase API structure.

        @param data: The dict to normalize
        @type data: dict

        @return: the altered dict from parameter data.
        @rtype: dict
        """
        for prop in ('labels', 'descriptions'):
            if prop not in data:
                continue
            for key, value in data[prop].items():
                if isinstance(value, basestring):
                    data[prop][key] = {'language': key, 'value': value}

        if 'aliases' in data:
            for key, values in data['aliases'].items():
                if (isinstance(values, list) and
                        isinstance(values[0], basestring)):
                    data['aliases'][key] = [{'language': key, 'value': value}
                                            for value in values]

        return data
