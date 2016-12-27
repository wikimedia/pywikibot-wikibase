import unittest
import json
import os

from pywikibase import WikibasePage, WbTime

try:
    unicode = unicode
except NameError:
    basestring = (str, bytes)


class TestWbTime(unittest.TestCase):

    def setUp(self):
        with open(os.path.join(os.path.split(__file__)[0],
                               'data', 'Q7251.wd')) as f:
            self._content = json.load(f)['entities']['Q7251']
        wb_page = WikibasePage()
        wb_page.get(content=self._content)
        self.time1 = wb_page.claims['P569'][0].target
        self.time2 = wb_page.claims['P570'][0].target

    def init_tests(self):
        self.assertRaises(ValueError, WbTime, precision=15)
        self.assertRaises(ValueError, WbTime, precision='invalid_precision')
        self.assertNotEqual(self.time1, self.time2)

    def wikibase_tests(self):
        t = self.time1.toWikibase()
        wb_t = {u'after': 0,
                u'precision': 11,
                u'time': u'+1912-06-23T00:00:00Z',
                u'timezone': 0,
                u'calendarmodel': u'http://www.wikidata.org/entity/Q1985727',
                u'before': 0}
        self.assertEqual(t, wb_t)

        # Consistency
        self.assertEqual(WbTime.fromWikibase(t), self.time1)
        self.assertEqual(t, WbTime.fromWikibase(t).toWikibase())

        self.assertNotEqual(t, self.time2.toWikibase())

    def timestr_tests(self):
        t = WbTime(year=2010, hour=12, minute=43, precision=14)
        self.assertEqual(t.toTimestr(), '+2010-01-01T12:43:00Z')

        # Consistency
        self.assertEqual(WbTime.fromTimestr(t.toTimestr()), t)


if __name__ == '__main__':
    unittest.main()
