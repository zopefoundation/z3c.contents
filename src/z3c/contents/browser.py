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

import transaction
import zope.interface
import zope.i18nmessageid
import zope.i18n
from zope.annotation.interfaces import IAnnotations
from zope.copypastemove import ItemNotFoundError
from zope.copypastemove.interfaces import IPrincipalClipboard
from zope.copypastemove.interfaces import IObjectCopier, IObjectMover
from zope.copypastemove.interfaces import IContainerItemRenamer
from zope.app.container.interfaces import IContainerNamesContainer
from zope.exceptions import DuplicationError
from zope.exceptions.interfaces import UserError
from zope.security.interfaces import Unauthorized
from zope.traversing.interfaces import TraversalError
from zope.traversing import api
from zope.app.container.find import SimpleIdFindFilter
from zope.app.container.interfaces import DuplicateIDError

from z3c.form import button, field
from z3c.formui import form
from z3c.table import table
from z3c.template.template import getPageTemplate

from z3c.contents import interfaces
from z3c.contents.search import SimpleAttributeFindFilter

_ = zope.i18nmessageid.MessageFactory('z3c')


def queryPrincipalClipboard(request):
    """Return the clipboard based on the request."""
    user = request.principal
    annotations = IAnnotations(user, None)
    if annotations is None:
        return None
    return IPrincipalClipboard(annotations, None)


def safeGetAttr(obj, attr, default):
    """Attempts to read the attr, returning default if Unauthorized."""
    try:
        return getattr(obj, attr, default)
    except Unauthorized:
        return default


class ContentsSearch(object):
    """An adapter for container context to satisfy search form requirements
    
    """

    zope.interface.implements(interfaces.IContentsSearch)
    zope.component.adapts(zope.interface.Interface)

    def __init__(self, context):
        self.context = context

    def get_searchterm(self):
        return u''

    def set_searchterm(self, value):
        pass

    searchterm = property(get_searchterm, set_searchterm)

class ContentsSearchForm(form.Form):

    template = getPageTemplate()
    fields = field.Fields(interfaces.IContentsSearch)
    prefix = 'search'
    table = None

    @button.buttonAndHandler(_('Search'), name='search')
    def handleSearch(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = u'Some error message'
            return
        self.table.searchterm = data.get('searchterm', '')


# conditions
def canCut(form):
    return form.supportsCut


def canCopy(form):
    return form.supportsCopy


def canDelete(form):
    return form.supportsDelete


def canPaste(form):
    return form.supportsPaste


def canRename(form):
    return form.supportsRename


class ContentsPage(table.Table, form.Form):
    """Generic IContainer management page."""

    zope.interface.implements(interfaces.IContentsPage)

    template = getPageTemplate()

    # search sub-form
    search = None

    # internal defaults
    selectedItems = []
    ignoreContext = False

    supportsCut = False
    supportsCopy = False
    supportsDelete = False
    supportsPaste = False
    supportsRename = False

    # sort attributes
    sortOn = 1 # initial sort on name column

    # customize this part
    allowCut = True
    allowCopy = True
    allowDelete = True
    allowPaste = True
    allowRename = True

    prefix = 'contents'
    searchterm = ''

    # error messages
    cutNoItemsMessage = _('No items selected for cut')
    cutItemsSelected = _('Items selected for cut')

    copyItemsSelected = _('Items choosen for copy')
    copyNoItemsMessage = _('No items selected for copy')
    copySucsessMessage = _('Data successfully copied')

    deleteErrorMessage = _('Could not delete the selected items')
    deleteNoItemsMessage = _('No items selected for delete')
    deleteSucsessMessage = _('Data successfully deleted')

    pasteSucsessMessage = _('Data successfully pasted')

    renameErrorMessage = _('Could not rename all selected items')
    renameDuplicationMessage = _('Duplicated item name')
    renameItemNotFoundMessage = _('Item not found')

    def update(self):

        self.search = ContentsSearchForm(self.context, self.request)
        self.search.table = self
        self.search.update()

        # first setup columns and process the items as selected if any
        super(ContentsPage, self).update()
        # second find out if we support paste
        self.clipboard = queryPrincipalClipboard(self.request)

        self.setupCopyPasteMove()
        self.updateWidgets()
        self.updateActions()
        self.actions.execute()

    def setupCopyPasteMove(self):
        hasContent = self.hasContent
        if self.allowCut:
            self.supportsCut = hasContent
        if self.allowCopy:
            self.supportsCopy = hasContent
        if self.allowDelete:
            self.supportsDelete = hasContent
        if self.allowPaste:
            self.supportsPaste = self.hasClipboardContents
        if self.allowRename:
            self.supportsRename = (hasContent and self.supportsCut and
                    not IContainerNamesContainer.providedBy(self.context))

    def updateAfterActionExecution(self):
        """Adjust new container length and copa paste move status."""
        super(ContentsPage, self).update()
        self.setupCopyPasteMove()
        self.updateActions()

    def render(self):
        """Render the template."""
        return self.template()

    @property
    def values(self):
        # not searching
        if not self.searchterm:
            return self.context.values()

        # no search adapter for the context
        try:
            search = interfaces.ISearch(self.context)
        except TypeError:
            return self.context.values()

        # perform the search
        searchterms = self.searchterm.split(' ')

        # possible enhancement would be to look up these filters as adapters to
        # the container!
        result = search.search(id_filters=[SimpleIdFindFilter(searchterms)],
                            object_filters=[SimpleAttributeFindFilter(searchterms)])
        return result


    @property
    def hasContent(self):
        return bool(self.values)

    @property
    def isPasteable(self):
        """Decide if there is anything to paste."""
        target = self.context
        if self.clipboard is None:
            return False
        items = self.clipboard.getContents()
        for item in items:
            try:
                obj = api.traverse(self.context, item['target'])
            except TraversalError:
                pass
            else:
                if item['action'] == 'cut':
                    mover = IObjectMover(obj)
                    moveableTo = safeGetAttr(mover, 'moveableTo', None)
                    if moveableTo is None or not moveableTo(self.context):
                        return False
                elif item['action'] == 'copy':
                    copier = IObjectCopier(obj)
                    copyableTo = safeGetAttr(copier, 'copyableTo', None)
                    if copyableTo is None or not copyableTo(self.context):
                        return False
                else:
                    raise
        return True

    @property
    def hasClipboardContents(self):
        """Interogate the ``PrinicipalAnnotation`` to see if clipboard
        contents exist."""
        if not self.isPasteable:
            return False
        # touch at least one item in clipboard to confirm contents
        items = self.clipboard.getContents()
        for item in items:
            try:
                api.traverse(self.context, item['target'])
            except TraversalError:
                pass
            else:
                return True
        return False

    @button.buttonAndHandler(_('Copy'), name='copy', condition=canCopy)
    def handleCopy(self, action):
        if not len(self.selectedItems):
            self.status = self.copyNoItemsMessage
            return

        items = []
        append = items.append
        for obj in self.selectedItems:
            __name__ = api.getName(obj)
            copier = IObjectCopier(obj)
            if not copier.copyable():
                m = {"name": __name__}
                if __name__:
                    m["name"] = __name__
                    self.status = _(
                        "Object '${name}' (${name}) cannot be copied",
                        mapping=m)
                else:
                    self.status = _("Object '${name}' cannot be copied",
                                   mapping=m)
                transaction.doom()
                return
            append(api.joinPath(api.getPath(self.context), __name__))

        self.status = self.copyItemsSelected
        # store the requested operation in the principal annotations:
        self.clipboard.clearContents()
        self.clipboard.addItems('copy', items)

    @button.buttonAndHandler(_('Cut'), name='cut', condition=canCut)
    def handleCut(self, action):
        if not len(self.selectedItems):
            self.status = self.cutNoItemsMessage
            return

        items = []
        append = items.append
        for obj in self.selectedItems:
            mover = IObjectMover(obj)
            __name__ = api.getName(obj)
            if not mover.moveable():
                m = {"name": __name__}
                if name:
                    m["name"] = __name__
                    self.status = _(
                        "Object '${name}' (${name}) cannot be moved",
                        mapping=m)
                else:
                    self.status = _("Object '${name}' cannot be moved",
                                   mapping=m)
                transaction.doom()
                return
            append(api.joinPath(api.getPath(self.context), __name__))

        self.status = self.cutItemsSelected
        # store the requested operation in the principal annotations:
        self.clipboard.clearContents()
        self.clipboard.addItems('cut', items)

    @button.buttonAndHandler(_('Paste'), name='paste', condition=canPaste)
    def handlePaste(self, action):
        items = self.clipboard.getContents()
        moved = False
        not_pasteable_ids = []
        for item in items:
            duplicated_id = False
            try:
                obj = api.traverse(self.context, item['target'])
            except TraversalError:
                pass
            else:
                if item['action'] == 'cut':
                    mover = IObjectMover(obj)
                    try:
                        mover.moveTo(self.context)
                        moved = True
                    except DuplicateIDError:
                        duplicated_id = True
                elif item['action'] == 'copy':
                    copier = IObjectCopier(obj)
                    try:
                        copier.copyTo(self.context)
                    except DuplicateIDError:
                        duplicated_id = True
                else:
                    raise

            if duplicated_id:
                not_pasteable_ids.append(api.getName(obj))

        if moved:
            # Clear the clipboard if we do a move, but not if we only do a copy
            self.clipboard.clearContents()

        if not_pasteable_ids != []:
            # Show the ids of objects that can't be pasted because
            # their ids are already taken.
            # TODO Can't we add a 'copy_of' or something as a prefix
            # instead of raising an exception ?
            transaction.doom()
            raise UserError(
                _("The given name(s) %s is / are already being used" %(
                str(not_pasteable_ids))))
        else:
            # we need to update the table rows again, otherwise we don't 
            # see the new item in the table
            self.updateAfterActionExecution()
            self.status = self.pasteSucsessMessage

    @button.buttonAndHandler(_('Delete'), name='delete', condition=canDelete)
    def handleDelete(self, action):
        if not len(self.selectedItems):
            self.status = self.deleteNoItemsMessage
            return
        try:
            for item in self.selectedItems:
                del self.context[api.getName(item)]
        except KeyError:
            self.status = self.deleteErrorMessage
            transaction.doom()
        # update the table rows before we start with rendering
        self.updateAfterActionExecution()
        self.status = self.deleteSucsessMessage

    @button.buttonAndHandler(_('Rename'), name='rename', condition=canRename)
    def handlerRename(self, action):
        changed = False
        errorMessages = {}
        renameCol = self.columnByName.get('renameColumn')
        if renameCol:
            for item in list(self.values):
                if item in self.selectedItems:
                    errorMsg = None
                    oldName = renameCol.getItemValue(item)
                    newName = renameCol.getRenameValue(item)
                    if newName is not None and oldName != newName:
                        try:
                            renamer = IContainerItemRenamer(self.context)
                            renamer.renameItem(oldName, newName)
                            changed = True
                        except DuplicationError:
                            errorMsg = self.renameDuplicationMessage
                            changed = True
                        except ItemNotFoundError:
                            errorMsg = self.renameItemNotFoundMessage
                            changed = True
                    elif newName is None:
                        errorMsg = _('No name given')
                    elif newName is not None and oldName == newName:
                        errorMsg = _('No new name given')
                    if errorMsg is not None:
                        key = renameCol.getItemKey(item)
                        errorMessages[key] = zope.i18n.translate(
                            errorMsg, context=self.request)
        if changed:
            self.status = self.renameErrorMessage
            # update the table rows before we start with rendering
            self.updateAfterActionExecution()
            # and set error message back to the new rename column
            renameCol = self.columnByName.get('renameColumn')
            if renameCol:
                renameCol.errorMessages = errorMessages

