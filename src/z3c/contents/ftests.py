import os
import doctest
import transaction

from zope.app.testing import functional
import zope.component

ftesting_zcml = os.path.join(os.path.dirname(__file__), 
                                           'ftesting.zcml')
TestLayer = functional.ZCMLLayer(
                       ftesting_zcml, __name__, 'TestLayer')

def setUp(test):
    functional.FunctionalTestSetup().setUp()
    test.globs['getRootFolder'] = functional.getRootFolder

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
