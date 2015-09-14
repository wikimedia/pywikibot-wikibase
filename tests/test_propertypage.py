import unittest
from pywikibase import PropertyPage, Claim

try:
    basestring
except NameError:
    basestring = str


class TestPropertyPage(unittest.TestCase):

    def setUp(self):
        self.property_page = PropertyPage('P31', 'wikibase-item')

    def test_init_item(self):
        self.assertEqual(self.property_page.getID(), 'P31')
        self.assertRaises(ValueError, PropertyPage, title='Null')
        self.assertRaises(ValueError, PropertyPage, title='Q15')

    def test_new_claim(self):
        claim = self.property_page.newClaim()
        self.assertIsInstance(claim, Claim)
        self.assertEqual(claim.id, self.property_page.getID())

if __name__ == '__main__':
    unittest.main()
