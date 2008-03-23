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
from zope.app.container.interfaces import (IObjectFindFilter,
                                           IReadContainer)
from zope.security.proxy import removeSecurityProxy

from z3c.contents.interfaces import ISearch

class SearchForContainer(object):

    zope.interface.implements(ISearch)

    __used_for__ = IReadContainer

    def __init__(self, context):
        self._context = context

    def search(self, id_filters=None, object_filters=None):
        'See ISearch'
        id_filters = id_filters or []
        object_filters = object_filters or []
        result = []
        container = self._context
        for id, object in container.items():
            _search_helper(id, object, container,
                         id_filters, object_filters,
                         result)
        return result


def _search_helper(id, object, container, id_filters, object_filters, result):
    # check id filters if we get a match then return immediately
    for id_filter in id_filters:
        if id_filter.matches(id):
            result.append(object)
            return

    # now check all object filters
    for object_filter in object_filters:
        if object_filter.matches(object):
            result.append(object)
            return

    # do we need to check sub containers?
    if not IReadContainer.providedBy(object):
        return

    container = object
    for id, object in container.items():
        _search_helper(id, object, container, id_filters, object_filters, result)


class SimpleAttributeFindFilter(object):
    """Filter objects on text or integer attributes"""
    zope.interface.implements(IObjectFindFilter)
    
    def __init__(self, terms):
        self.terms = terms
    
    def matches(self, object):
        """Check if one of the search terms is in any text or integer field of
        this object

        """
        # surely a better way to get to the attributes than is done here?
        object = removeSecurityProxy(object)

        for key in [k for k in dir(object) if not k.startswith('_')]:
            value = str(getattr(object, key)).lower()
            for term in self.terms:
                term = term.lower()
                if term in value:
                    return True
        return False

