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
from zope.dublincore.interfaces import IZopeDublinCore
from zope.dublincore.interfaces import IDCDescriptiveProperties
from zope.copypastemove import ItemNotFoundError
from zope.copypastemove.interfaces import IPrincipalClipboard
from zope.copypastemove.interfaces import IObjectCopier, IObjectMover
from zope.copypastemove.interfaces import IContainerItemRenamer
from zope.exceptions import DuplicationError
from zope.exceptions.interfaces import UserError
from zope.security.interfaces import Unauthorized
from zope.traversing import api

from zope.app.container.interfaces import DuplicateIDError

from z3c.form import button
from z3c.formui import form
from z3c.table import table
from z3c.template.template import getPageTemplate

from z3c.contents import interfaces

_ = zope.i18nmessageid.MessageFactory('z3c')


def queryPrincipalClipboard(request):
    """Return the clipboard based on the request."""
    user = request.principal
    annotations = IAnnotations(user, None)
    if annotations is None:
        return None
    return IPrincipalClipboard(annotations, None)


def getDCTitle(ob):
    dc = IDCDescriptiveProperties(ob, None)
    if dc is None:
        return None
    else:
        return dc.title

def safeGetAttr(obj, attr, default):
    """Attempts to read the attr, returning default if Unauthorized."""
    try:
        return getattr(obj, attr, default)
    except Unauthorized:
        return default


class ContentsPage(table.Table, form.Form):
    """Generic IContainer management page."""

    zope.interface.implements(interfaces.IContentsPage)

    template = getPageTemplate()

    # internal defaults
    selectedItems = []
    supportsPaste = False
    ignoreContext = False

    # customize this part
    allowPaste = True
    prefix = 'contents'

    # error messages
    deleteErrorMessage = _('Could not delete the selected items')
    deleteNoItemsMessage = _('No items selected for delete')
    deleteSucsessMessage = _('Data successfully deleted')

    copyItemsSelected = _('Items choosen for copy')
    copyNoItemsMessage = _('No items selected for copy')
    copySucsessMessage = _('Data successfully copied')

    cutNoItemsMessage = _('No items selected for cut')
    cutItemsSelected = _('Items selected for cut')

    renameErrorMessage = _('Could not rename all selected items')
    renameDuplicationMessage = _('Duplicated item name')
    renameItemNotFoundMessage = _('Item not found')

    def update(self):
        # first setup columns and process the items as selected if any
        super(ContentsPage, self).update()
        # second find out if we support paste
        self.clipboard = queryPrincipalClipboard(self.request)
        if self.allowPaste:
            self.supportsPaste = self.pasteable()
        self.updateWidgets()
        self.updateActions()
        self.actions.execute()

    def render(self):
        """Render the template."""
        return self.template()

    def pasteable(self):
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

    def hasClipboardContents(self):
        """Interogate the ``PrinicipalAnnotation`` to see if clipboard
        contents exist."""
        if not self.supportsPaste:
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

    @button.buttonAndHandler(_('Copy'), name='copy')
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

    @button.buttonAndHandler(_('Cut'), name='cut')
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

    @button.buttonAndHandler(_('Paste'), name='paste')
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
            super(ContentsPage, self).update()
            self.status = self.copySucsessMessage

    @button.buttonAndHandler(_('Delete'), name='delete')
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
        self.status = self.deleteSucsessMessage
        # update the table rows before we start with rendering
        super(ContentsPage, self).update()

    @button.buttonAndHandler(_('Rename'), name='rename')
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
            super(ContentsPage, self).update()
            # and set error message back to the new rename column
            renameCol = self.columnByName.get('renameColumn')
            if renameCol:
                renameCol.errorMessages = errorMessages
