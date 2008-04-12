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
import zope.component
import zope.interface
from zope.annotation.interfaces import IAnnotations
from zope.copypastemove import ContainerItemRenamer
from zope.copypastemove import ObjectMover
from zope.copypastemove import ObjectCopier
from zope.copypastemove import PrincipalClipboard
from zope.copypastemove.interfaces import IContainerItemRenamer
from zope.copypastemove.interfaces import IObjectMover
from zope.copypastemove.interfaces import IObjectCopier
from zope.copypastemove.interfaces import IPrincipalClipboard
from zope.testing import doctest
from zope.app.container.interfaces import IContainer
from zope.app.container.interfaces import IContained
from zope.app.testing import setup

from z3c.macro import tales
import z3c.table.testing
import z3c.contents.search
import z3c.contents.value


class PrincipalAnnotations(dict):
    zope.interface.implements(IAnnotations)
    data = {}
    def __new__(class_, context=None):
        try:
            annotations = class_.data[str(context)]
        except KeyError:
            annotations = dict.__new__(class_)
            class_.data[str(context)] = annotations
        return annotations
    def __init__(self, context):
        pass
    def __repr__(self):
        return "<%s.PrincipalAnnotations object>" % __name__


def setUp(test):
    test.globs = {'root': setup.placefulSetUp(True)}

    from zope.app.pagetemplate import metaconfigure
    metaconfigure.registerType('macro', tales.MacroExpression)

    zope.component.provideAdapter(ObjectCopier, (IContained,), IObjectCopier)
    zope.component.provideAdapter(ObjectMover, (IContained,), IObjectMover)
    zope.component.provideAdapter(ContainerItemRenamer, (IContainer,), 
        IContainerItemRenamer)

    zope.component.provideAdapter(PrincipalClipboard, (IAnnotations,),
        IPrincipalClipboard)
    # use None as principal
    zope.component.provideAdapter(PrincipalAnnotations, (None,),
        IAnnotations)

    # dublin core stub adapter
    zope.component.provideAdapter(z3c.table.testing.DublinCoreAdapterStub)

    # value adapter
    zope.component.provideAdapter(z3c.contents.value.SearchableValues)


def tearDown(test):
    setup.placefulTearDown()


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
            setUp=setUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
