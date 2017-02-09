from pywikibase.coordinate import Coordinate
from pywikibase.wbtime import WbTime
from pywikibase.wbquantity import WbQuantity
from pywikibase.wbproperty import Property
from pywikibase.claim import Claim
from pywikibase.wikibasepage import WikibasePage
from pywikibase.itempage import ItemPage
from pywikibase.propertypage import PropertyPage
from pywikibase.about import (__name__, __version__, __maintainer__,
                              __maintainer_email__, __description__,
                              __license__, __url__)


# Not to mess with pyflakes
__all__ = (Coordinate, WbQuantity, WbTime, ItemPage, Property, PropertyPage,
           WikibasePage, Claim, __name__, __version__, __maintainer__,
           __maintainer_email__, __description__, __license__, __url__)
