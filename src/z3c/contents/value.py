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

import zope.component
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.app.container.interfaces import IContainer
from zope.app.container.find import SimpleIdFindFilter

import z3c.table.value
from z3c.contents import interfaces
from z3c.contents import browser
from z3c.contents.search import SearchableTextFindFilter


class SearchableValues(z3c.table.value.ValuesMixin):
    """Values based on given search."""

    zope.component.adapts(IContainer, IBrowserRequest, interfaces.IContentsPage)

    @property
    def values(self):

        # first setup and update search form
        self.table.searchForm = browser.ContentsSearchForm(self.context,
            self.request)
        self.table.searchForm.table = self.table
        self.table.searchForm.update()

        # not searching
        if not self.table.searchterm:
            return self.context.values()

        # no search adapter for the context
        try:
            search = interfaces.ISearch(self.context)
        except TypeError:
            return self.context.values()

        # perform the search
        searchterms = self.table.searchterm.split(' ')

        # possible enhancement would be to look up these filters as adapters to
        # the container! Maybe we can use catalogs here?
        return search.search(id_filters=[SimpleIdFindFilter(searchterms)],
            object_filters=[SearchableTextFindFilter(searchterms)])
