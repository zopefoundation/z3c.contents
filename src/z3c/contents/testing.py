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

import zope.interface
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.index.text.interfaces import ISearchableText

import z3c.layer.ready2go

class IContentsTestBrowserLayer(z3c.layer.ready2go.IReady2GoBrowserLayer):
        """test layer."""


class IContentsTestBrowserSkin(IContentsTestBrowserLayer):
    """The browser skin."""


class IContent(zope.interface.Interface):

    title = zope.schema.TextLine(title=u'Title')
    number = zope.schema.Int(title=u'Number')


class Content(object):
    """Sample content which is pickable for copy test."""

    zope.interface.implements(IContent)

    def __init__(self, title, number):
        self.title = title
        self.number = number

    def __repr__(self):
        return u'<%s %s %s>' % (self.__class__.__name__, self.title,
            self.number)


class SearchableTextForContent:

    zope.interface.implements(ISearchableText)
    zope.component.adapts(IContent)

    def __init__(self, content):
        self.content = content

    def getSearchableText(self):
        return '%s %d' % (self.content.title, self.content.number)
