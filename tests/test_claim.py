import unittest
import json
import os

from collections import OrderedDict

from pywikibase import WikibasePage, Claim, ItemPage

try:
    unicode = unicode
except NameError:
    basestring = (str, bytes)


class TestClaim(unittest.TestCase):

    def setUp(self):
        with open(os.path.join(os.path.split(__file__)[0],
                               'data', 'Q7251.wd')) as f:
            self._content = json.load(f)['entities']['Q7251']
        wb_page = WikibasePage()
        wb_page.get(content=self._content)
        self.claim1 = wb_page.claims['P31'][0]
        self.claim2 = wb_page.claims['P570'][0]
        self.claim3 = wb_page.claims['P18'][0]

    def init_tests(self):
        self.assertEqual(self.claim1.snak,
                         'Q7251$22FE0362-8887-417C-A9AC-81850399468C')
        self.assertFalse(self.claim1.isReference)
        self.assertFalse(self.claim1.isQualifier)
        self.assertIsInstance(self.claim1.on_item, WikibasePage)
        self.assertEqual(self.claim1.on_item, 'Q7251')

        self.assertRaises(ValueError, Claim, 'P31', isQualifier=True,
                          isReference=True)

    def test_set_target(self):
        claim = Claim('P144', datatype='wikibase-item')
        self.assertRaises(ValueError, claim.setTarget, "Hello!")

        claim = Claim('P144', datatype='time')
        self.assertRaises(ValueError, claim.setTarget, ItemPage('Q5'))
        self.assertRaises(ValueError, claim.setTarget, "Hello!")

    def test_sources(self):
        self.assertIsInstance(self.claim1.sources, list)
        self.assertIsInstance(self.claim1.sources[0], OrderedDict)
        self.assertIn('P143', self.claim1.sources[0])
        self.assertIsInstance(self.claim1.sources[0]['P143'], list)
        self.assertEqual(len(self.claim1.sources), 2)
        self.assertEqual(self.claim1.getSources(), self.claim1.sources)

        sources_copy = self.claim1.sources
        source = Claim('P144', datatype='wikibase-item')
        source.setTarget(ItemPage('Q5'))
        self.claim1.addSource(source)
        self.assertIn('P144', self.claim1.sources[-1])
        self.assertEqual(source, self.claim1.sources[-1]['P144'][0])

        self.claim1.removeSource(source)
        self.assertEqual(self.claim1.sources, sources_copy)

    def test_snak_type(self):
        self.assertEqual(self.claim1.snaktype, 'value')
        self.assertRaises(ValueError, self.claim1.setSnakType, 'NULL')
        self.assertRaises(ValueError, self.claim1.setSnakType, None)

        claim = Claim('P31')
        claim.setSnakType('novalue')
        self.assertEqual(claim.snaktype, 'novalue')
        self.assertNotEqual(claim.snaktype, 'value')

    def test_qualifiers(self):
        source = self.claim1.sources[0]['P143'][0]
        self.assertRaises(ValueError, source.has_qualifier, 'P31', 'Q5')

        qualifier = Claim('P31', datatype='wikibase-item')
        qualifier.setTarget(ItemPage('Q5'))
        self.claim1.addQualifier(qualifier)
        self.assertRaises(ValueError, source.addQualifier, qualifier)
        self.assertEqual(self.claim1.qualifiers['P31'][0], qualifier)
        self.assertTrue(qualifier.isQualifier)
        self.assertTrue(self.claim1.has_qualifier('P31', 'Q5'))
        self.assertFalse(self.claim1.has_qualifier('P31', 'Q6'))
        self.assertFalse(self.claim1.has_qualifier('P32', 'Q5'))

    def test_target_equals(self):
        self.assertTrue(self.claim1.target_equals('Q5'))
        self.assertTrue(self.claim2.target_equals(1954))
        self.assertTrue(self.claim3.target_equals('Alan Turing Aged 16.jpg'))
        self.assertFalse(self.claim1.target_equals('Q6'))

    def test_rank(self):
        self.assertEqual(self.claim1.getRank(), 'normal')

        claim = Claim('P134', datatype='wikibase-item')
        claim.setRank('preferred')
        self.assertEqual(claim.getRank(), 'preferred')
        self.assertEqual(claim.rank, 'preferred')


if __name__ == '__main__':
    unittest.main()
