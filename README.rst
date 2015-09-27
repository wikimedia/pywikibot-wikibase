.. image:: https://travis-ci.org/wikimedia/pywikibot-wikibase.svg?branch=master
    :target: https://travis-ci.org/wikimedia/pywikibot-wikibase

.. image:: http://codecov.io/github/wikimedia/pywikibot-wikibase/coverage.svg?branch=master
    :target: http://codecov.io/github/wikimedia/pywikibot-wikibase?branch=master

pywikibase
==========
pywikibase is the library designed to handle DataModel of Wikibase.

It was forked from pywikibot-core in 28 July 2015.

Quick start
-----------
::

    pip install pywikibase

Usage
-----

::

    import pywikibot
    item = pywikibase.ItemPage('Q91')
    item.get(content=content_from_api)

Contributing
------------
Our code is maintained on Wikimedia's `Gerrit installation <https://gerrit.wikimedia.org/>`_,
`learn <https://www.mediawiki.org/wiki/Special:MyLanguage/Developer_access>`_ how to get
started.


Credits of this code belong to pywikibot team.
pywikibase and pywikibot are distributed under MIT license.
