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

import zope.schema
import zope.i18nmessageid

from z3c.table import interfaces

_ = zope.i18nmessageid.MessageFactory('z3c')


class IContentsPage(interfaces.ITable):
    """Container management page
    """

class IContentsSearch(zope.interface.Interface):
    """We would like to provide a search field for searching within the
    container.
    
    Possible addition here could be a choice field to search within specific
    columns.
    """

    searchterm = zope.schema.TextLine(title=_(u'Search'))


class ISearch(zope.interface.Interface):
    """
    Search support for containers.

    This is different to z.a.c.interfaces.IFind in that the search method
    will match **any** filter whereas the find method of IFind will match
    if **all** filters match.
    """

    def search(id_filters=None, object_filters=None):
        """Find object that matches **any** filters in all sub-objects.

        This container itself is not included.
        """

