# -*- coding: utf-8  -*-
"""
Handling a Wikibase property pages.
"""

#
# (C) Pywikibot team, 2008-2015
#
# Distributed under the terms of the MIT license.
#
from __future__ import unicode_literals

from pywikibase.wikibasepage import WikibasePage
from pywikibase.wbproperty import Property
from pywikibase.claim import Claim


class PropertyPage(WikibasePage, Property):

    """
    A Wikibase entity in the property namespace.

    Should be created as::

        PropertyPage('P21')
    """

    def __init__(self, title=u"", datatype=None):
        """
        Constructor.

        @param title: page name of property, like "P##"
        @type title: str
        """
        if not title.startswith('P'):
            raise ValueError(
                u"'%s' is not an property page title" % title)
        self.id = title
        Property.__init__(self, self.id, datatype)

    def get(self, *args):
        """
        Fetch the property entity, and cache it.

        @param force: override caching
        @param args: values of props
        """
        if not hasattr(self, '_content'):
            WikibasePage.get(self, *args)

    def newClaim(self, *args, **kwargs):
        """
        Helper function to create a new claim object for this property.

        @return: Claim
        """
        return Claim(self.getID(), datatype=self.type,
                     *args, **kwargs)
