import unittest
import codecs
import json
import os

from pywikibase import ItemPage, Claim

try:
    basestring
except NameError:
    basestring = str

class TestWikibasePage(unittest.TestCase):

    def setUp(self):
        with open(os.path.join(os.path.split(__file__)[0], 'data', 'Q7251.wd')) as f:
            self._content = json.load(f)['entities']['Q7251']
        self.item_page = ItemPage()
        self.item_page.get(content=self._content)

    def test_init_item(self):
        self.assertEqual(self.item_page.getID(), 'Q7251')
        self.assertRaises(RuntimeError, ItemPage, title='Null')
        self.assertRaises(RuntimeError, ItemPage, title='P15')

    def test_sitelinks(self):
        self.assertEqual(len(self.item_page.sitelinks), 134)
        self.assertIn('fawiki', self.item_page.sitelinks)
        self.assertNotIn('fa', self.item_page.sitelinks)
        self.assertIsInstance(self.item_page.sitelinks['enwiki'], basestring)

    def test_add_claim(self):
        claim = Claim('P17', datatype='wikibase-item')
        claim.setTarget(ItemPage('Q91'))
        self.item_page.addClaim(claim)
        self.assertIn('P17', self.item_page.claims)
        self.assertEqual(len(self.item_page.claims['P17']), 1)
        self.assertIsInstance(self.item_page.claims['P17'][0], Claim)

    def test_remove_claim(self):
        claim = self.item_page.claims['P31'][0]
        old_claims = self.item_page.claims.copy()
        self.item_page.removeClaims(claim)
        self.assertNotEqual(self.item_page.claims, old_claims)
        self.assertNotIn('P31', self.item_page.claims)

if __name__ == '__main__':
    unittest.main()
