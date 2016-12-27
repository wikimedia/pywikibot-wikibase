import unittest

from pywikibase import Coordinate


class TestCoordinate(unittest.TestCase):

    """Test Coordinate."""

    def setUp(self):
        self.params = {u'latitude': 38.897669444444,
                       u'altitude': None,
                       u'globe': u'http://www.wikidata.org/entity/Q2',
                       u'longitude': -77.03655,
                       u'precision': 2.7777777777778e-06}

        self.coordinate = Coordinate(
            38.897669444444, -77.03655, precision=2.7777777777778e-06,
            entity='http://www.wikidata.org/entity/Q2')

    def test_init(self):
        """Test __init__."""
        self.assertEqual(self.coordinate.lat, 38.897669444444)
        self.assertEqual(self.coordinate.lon, -77.03655)

    def test_wikibase(self):
        """Test Wikibase-related methods."""
        self.assertEqual(self.params, self.coordinate.toWikibase())
        self.assertEqual(self.coordinate, Coordinate.fromWikibase(self.params))

    def test_precision(self):
        """Test precision attribute."""
        self.assertEqual(self.coordinate.precision, 2.7777777777778e-06)
        coord = Coordinate(38.897669444444, -77.03655, dim=100)
        self.assertEqual(coord.precision, 0.0011542482624706185)

    def test_entity(self):
        """Test entity property."""
        self.assertEqual(
            self.coordinate.entity, 'http://www.wikidata.org/entity/Q2')


if __name__ == '__main__':
    unittest.main()
