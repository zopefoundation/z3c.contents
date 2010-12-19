##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import unittest
from zope.testing import doctest
from zope.app.testing import functional

from z3c.contents import testing

functional.defineLayer('TestLayer', 'ftesting.zcml',
                       allow_teardown=True)


def test_suite():
    docTest = functional.FunctionalDocFileSuite('BROWSER.txt',
        setUp=testing.doctestSetUp, tearDown=testing.doctestTearDown,
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    docTest.layer = TestLayer
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        docTest,
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
