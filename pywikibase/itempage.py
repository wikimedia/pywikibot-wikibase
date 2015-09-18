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

import re

from pywikibase.wikibasepage import WikibasePage


class ItemPage(WikibasePage):

    """Wikibase entity of type 'item'.

    A Wikibase item may be defined by either a 'Q' id (qid),
    or by a site & title.

    If an item is defined by site & title, once an item's qid has
    been looked up, the item is then defined by the qid.
    """

    def __init__(self, title=None, content=None):
        """
        Constructor.

        @param title: id number of item, "Q###",
                      -1 or None for an empty item.
        @type title: str
        """
        # Validate the title is 'Q' and a positive integer.
        if title and not re.match(r'^Q[1-9]\d*$', title):
            raise RuntimeError(
                u"'%s' is not a valid item page title"
                % title)
        self.id = title

    def get(self, *args, **kwargs):
        """
        Fetch all item data, and cache it.

        @param args: values of props
        """
        data = super(ItemPage, self).get(*args, **kwargs)

        # sitelinks and badges
        self.sitelinks = {}
        self.badges = {}
        if 'sitelinks' in self._content:
            for dbname in self._content['sitelinks']:
                self.sitelinks[dbname] = self._content[
                    'sitelinks'][dbname]['title']
                if self._content['sitelinks'][dbname]['badges']:
                    self.badges[dbname] = \
                        self._content['sitelinks'][dbname]['badges']

        data['claims'] = self.claims
        data['sitelinks'] = self.sitelinks
        return data

    def toJSON(self, diffto=None):
        """
        Create JSON suitable for Wikibase API.

        When diffto is provided, JSON representing differences
        to the provided data is created.

        @param diffto: JSON containing claim data
        @type diffto: dict

        @return: dict
        """
        data = super(ItemPage, self).toJSON(diffto=diffto)

        self._diff_to('sitelinks', 'site', 'title', diffto, data)

        return data

    def addClaim(self, claim):
        """
        Add a claim to the item.

        @param claim: The claim to add
        @type claim: Claim
        """
        claim.on_item = self
        if claim.getID() in self.claims:
            self.claims[claim.getID()].append(claim)
        else:
            self.claims[claim.getID()] = [claim]

    def removeClaims(self, claims, **kwargs):
        """
        Remove the claims from the item.

        @param claims: list of claims to be removed
        @type claims: list or pywikibot.Claim

        """
        # this check allows single claims to be removed by pushing them into a
        # list of length one.
        from pywikibase.claim import Claim
        if isinstance(claims, Claim):
            claims = [claims]
        for claim in claims:
            if claim in self.claims.get(claim.getID(), []):
                self.claims.get(claim.getID(), []).remove(claim)
            if claim.getID() in self.claims and not self.claims[claim.getID()]:
                self.claims.pop(claim.getID())
