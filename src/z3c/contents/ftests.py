import os
import doctest
import lxml
import transaction

from zope.app.testing import functional
import zope.component

ftesting_zcml = os.path.join(os.path.dirname(__file__), 
                                           'ftesting.zcml')
TestLayer = functional.ZCMLLayer(
                       ftesting_zcml, __name__, 'TestLayer')

def printElement(browser, xpath, multiple=False, serialize=True):
    """Print method to use with z3c.etestbrowser"""
    result = [serialize and lxml.etree.tounicode(elem) or elem
              for elem in browser.etree.xpath(xpath)]
    if not multiple:
        print result[0]
        return
    for elem in result:
        print elem

def setUp(test):
    functional.FunctionalTestSetup().setUp()
    test.globs['getRootFolder'] = functional.getRootFolder
    test.globs['printElement'] = printElement

def tearDown(test):
    functional.FunctionalTestSetup().tearDown()

def test_suite():
    suite = functional.FunctionalDocFileSuite('BROWSER.txt',
        setUp=setUp, tearDown=tearDown,
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        )
    suite.layer = TestLayer
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
