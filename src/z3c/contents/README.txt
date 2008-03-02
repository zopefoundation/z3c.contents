========
Contents
========

The goal of this package is to offer a modular replacement for the default 
contents.html page used in Zope3.


Sample data setup
-----------------

Let's create a sample container which we can use as our context:

  >>> import zope.app.container.interfaces
  >>> class IContainer(zope.app.container.interfaces.IContainer):
  ...     """Custom container marker use as discriminator."""

  >>> import zope.interface
  >>> from zope.app.container import btree
  >>> class Container(btree.BTreeContainer):
  ...     """Sample container."""
  ... 
  ...     zope.interface.implements(IContainer)
  ... 
  >>> container = Container()

add them to the root:

  >>> root['container'] = container

Now setup some items based on our testing Content object. Note this object is
defined in the testing module because it must be pickable because the object
copier pickels objects during copy/paste:

  >>> from z3c.contents.testing import Content
  >>> container[u'zero'] = Content('Zero', 0)
  >>> container[u'first'] = Content('First', 1)
  >>> container[u'second'] = Content('Second', 2)
  >>> container[u'third'] = Content('Third', 3)
  >>> container[u'fourth'] = Content('Fourth', 4)

And we need to setup the form defaults first:

  >>> from z3c.form.testing import setupFormDefaults
  >>> setupFormDefaults()

And we need to configure our contents.pt template for the ContentsPage:

  >>> import os
  >>> import sys
  >>> from zope.configuration import xmlconfig
  >>> import z3c.template
  >>> context = xmlconfig.file('meta.zcml', z3c.template)
  >>> contentsTemplate = os.path.join(os.path.dirname(z3c.contents.__file__),
  ...     'contents.pt')
  >>> context = xmlconfig.string("""
  ... <configure
  ...     xmlns:z3c="http://namespaces.zope.org/z3c">
  ...   <z3c:template
  ...       for="z3c.contents.browser.ContentsPage"
  ...       template="%s"
  ...       />
  ... </configure>
  ... """ % contentsTemplate, context=context)


And load the formui confguration, which will make sure that all macros get 
registered correctly.

  >>> from zope.configuration import xmlconfig
  >>> import zope.component
  >>> import zope.viewlet
  >>> import zope.app.component
  >>> import zope.app.publisher.browser
  >>> import z3c.macro
  >>> import z3c.template
  >>> import z3c.formui
  >>> xmlconfig.XMLConfig('meta.zcml', zope.component)()
  >>> xmlconfig.XMLConfig('meta.zcml', zope.viewlet)()
  >>> xmlconfig.XMLConfig('meta.zcml', zope.app.component)()
  >>> xmlconfig.XMLConfig('meta.zcml', zope.app.publisher.browser)()
  >>> xmlconfig.XMLConfig('meta.zcml', z3c.macro)()
  >>> xmlconfig.XMLConfig('meta.zcml', z3c.template)()
  >>> xmlconfig.XMLConfig('configure.zcml', z3c.formui)()

And support the div form layer for our request:

  >>> from z3c.formui.interfaces import IDivFormLayer
  >>> from zope.interface import alsoProvides
  >>> from z3c.form.testing import TestRequest
  >>> request = TestRequest()
  >>> alsoProvides(request, IDivFormLayer)


ContentsPage
------------

Now we can create a ContentsPage:

  >>> from z3c.contents import browser
  >>> firstPage = browser.ContentsPage(container, request)
  >>> firstPage.update()
  >>> print firstPage.render()
  <form action="http://127.0.0.1" method="post"
        enctype="multipart/form-data" class="edit-form"
        name="contents" id="contents">
    <div class="viewspace">
        <div class="required-info">
           <span class="required">*</span>
           &ndash; required
        </div>
      <div>
    </div>
    </div>
    <div>
      <div class="buttons">
        <input type="submit" id="contents-buttons-copy"
               name="contents.buttons.copy"
               class="submit-widget button-field" value="Copy" />
        <input type="submit" id="contents-buttons-cut"
               name="contents.buttons.cut"
               class="submit-widget button-field" value="Cut" />
        <input type="submit" id="contents-buttons-delete"
               name="contents.buttons.delete"
               class="submit-widget button-field" value="Delete" />
        <input type="submit" id="contents-buttons-rename"
               name="contents.buttons.rename"
               class="submit-widget button-field" value="Rename" />
      </div>
    </div>
  </form>


Columns
-------

We register our predefined columns as adapters this allows us later to enhance 
existing contents.html pages with additional columns. Use the adapter directive
for this:

  >>> import zope.component
  >>> from z3c.table.interfaces import IColumn
  >>> from z3c.contents import interfaces
  >>> from z3c.table.column import CheckBoxColumn
  >>> zope.component.provideAdapter(CheckBoxColumn,
  ...     (IContainer, None, interfaces.IContentsPage),
  ...      provides=IColumn, name='checkBoxColumn')

  >>> from z3c.contents import column
  >>> zope.component.provideAdapter(column.RenameColumn,
  ...     (IContainer, None, interfaces.IContentsPage),
  ...      provides=IColumn, name='renameColumn')

  >>> from z3c.table.column import CreatedColumn
  >>> zope.component.provideAdapter(CreatedColumn,
  ...     (IContainer, None, interfaces.IContentsPage),
  ...      provides=IColumn, name='createdColumn')

  >>> from z3c.table.column import ModifiedColumn
  >>> zope.component.provideAdapter(ModifiedColumn,
  ...     (IContainer, None, interfaces.IContentsPage),
  ...      provides=IColumn, name='modifiedColumn')

Now let's update and render the contents page again:

  >>> firstPage.update()
  >>> print firstPage.render()
  <form action="http://127.0.0.1" method="post"
        enctype="multipart/form-data" class="edit-form"
        name="contents" id="contents">
    <div class="viewspace">
        <div class="required-info">
           <span class="required">*</span>
           &ndash; required
        </div>
      <div>
        <table>
          <thead>
            <tr>
              <th>X</th>
              <th>Name</th>
              <th>Created</th>
              <th>Modified</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="first"  /></td>
              <td>first</td>
              <td>01/01/01 01:01</td>
              <td>02/02/02 02:02</td>
            </tr>
            <tr>
              <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="fourth"  /></td>
              <td>fourth</td>
              <td>01/01/01 01:01</td>
              <td>02/02/02 02:02</td>
            </tr>
            <tr>
              <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="second"  /></td>
              <td>second</td>
              <td>01/01/01 01:01</td>
              <td>02/02/02 02:02</td>
            </tr>
            <tr>
              <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="third"  /></td>
              <td>third</td>
              <td>01/01/01 01:01</td>
              <td>02/02/02 02:02</td>
            </tr>
            <tr>
              <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="zero"  /></td>
              <td>zero</td>
              <td>01/01/01 01:01</td>
              <td>02/02/02 02:02</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div>
      <div class="buttons">
        <input type="submit" id="contents-buttons-copy"
               name="contents.buttons.copy"
               class="submit-widget button-field" value="Copy" />
        <input type="submit" id="contents-buttons-cut"
               name="contents.buttons.cut"
               class="submit-widget button-field" value="Cut" />
        <input type="submit" id="contents-buttons-delete"
               name="contents.buttons.delete"
               class="submit-widget button-field" value="Delete" />
        <input type="submit" id="contents-buttons-rename"
               name="contents.buttons.rename"
               class="submit-widget button-field" value="Rename" />
      </div>
    </div>
  </form>


Sorting
-------

The contents page supports sorting by columns. We can do this be set the 
sortOn request variable as we see in the head link of each column. Let's 
reverse the default sort order. Note, order depends on the alphabetic oder of 
number names and not on the number itself.

  >>> sorterRequest = TestRequest(form={'contents-sortOn': 'contents-checkBoxColumn-0',
  ...                                   'contents-sortOrder':'descending'})
  >>> alsoProvides(sorterRequest, IDivFormLayer)
  >>> sortingPage = browser.ContentsPage(container, sorterRequest)
  >>> sortingPage.update()
  >>> print sortingPage.render()
  <form action="http://127.0.0.1" method="post"
        enctype="multipart/form-data" class="edit-form"
        name="contents" id="contents">
  ...
  <tbody>
    <tr>
      <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="zero"  /></td>
      <td>zero</td>
      <td>01/01/01 01:01</td>
      <td>02/02/02 02:02</td>
    </tr>
    <tr>
      <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="third"  /></td>
      <td>third</td>
      <td>01/01/01 01:01</td>
      <td>02/02/02 02:02</td>
    </tr>
    <tr>
      <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="second"  /></td>
      <td>second</td>
      <td>01/01/01 01:01</td>
      <td>02/02/02 02:02</td>
    </tr>
    <tr>
      <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="fourth"  /></td>
      <td>fourth</td>
      <td>01/01/01 01:01</td>
      <td>02/02/02 02:02</td>
    </tr>
    <tr>
      <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="first"  /></td>
      <td>first</td>
      <td>01/01/01 01:01</td>
      <td>02/02/02 02:02</td>
    </tr>
  </tbody>
  ...

Let's make coverage happy and sort on the rename column:

  >>> sorterRequest = TestRequest(form={'contents-sortOn': 'contents-renameColumn-1',
  ...                                   'contents-sortOrder':'ascending'})
  >>> alsoProvides(sorterRequest, IDivFormLayer)
  >>> sortingPage = browser.ContentsPage(container, sorterRequest)
  >>> sortingPage.update()
  >>> print sortingPage.render()
  <form action="http://127.0.0.1" method="post"
        enctype="multipart/form-data" class="edit-form"
        name="contents" id="contents">
  ...
  <tbody>
    <tr>
      <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="first"  /></td>
      <td>first</td>
      <td>01/01/01 01:01</td>
      <td>02/02/02 02:02</td>
    </tr>
    <tr>
      <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="fourth"  /></td>
      <td>fourth</td>
      <td>01/01/01 01:01</td>
      <td>02/02/02 02:02</td>
    </tr>
    <tr>
      <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="second"  /></td>
      <td>second</td>
      <td>01/01/01 01:01</td>
      <td>02/02/02 02:02</td>
    </tr>
    <tr>
      <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="third"  /></td>
      <td>third</td>
      <td>01/01/01 01:01</td>
      <td>02/02/02 02:02</td>
    </tr>
    <tr>
      <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="zero"  /></td>
      <td>zero</td>
      <td>01/01/01 01:01</td>
      <td>02/02/02 02:02</td>
    </tr>
  </tbody>
  ...

Copy
----

Frist we need to setup another container which we can copy to:

  >>> secondContainer = Container()
  >>> root['secondContainer'] = secondContainer

And we need another contents page instance:

  >>> secondPage = browser.ContentsPage(secondContainer, request)

As you can see the second page for the second container has no items and 
no buttons:

  >>> secondPage.update()
  >>> print secondPage.render()
  <form action="http://127.0.0.1" method="post"
        enctype="multipart/form-data" class="edit-form"
        name="contents" id="contents">
    <div class="viewspace">
        <div class="required-info">
           <span class="required">*</span>
           &ndash; required
        </div>
      <div>
        <table>
          <thead>
            <tr>
              <th>X</th>
              <th>Name</th>
              <th>Created</th>
              <th>Modified</th>
            </tr>
          </thead>
          <tbody>
          </tbody>
        </table>
      </div>
    </div>
    <div>
      <div class="buttons">
      </div>
    </div>
  </form>

Now we start with copy the ``zero`` item from the first page. We can do this
by using some request variables. Let's setup a new request. See the feedback
we will get as form message:

  >>> copyRequest = TestRequest(
  ...     form={'contents-checkBoxColumn-0-selectedItems': ['zero'],
  ...           'contents.buttons.copy': 'Copy'})
  >>> alsoProvides(copyRequest, IDivFormLayer)
  >>> copyPage = browser.ContentsPage(container, copyRequest)
  >>> copyPage.update()
  >>> print copyPage.render()
  <form action="http://127.0.0.1" method="post"
        enctype="multipart/form-data" class="edit-form"
        name="contents" id="contents">
  ...
        <div class="status">
          <div class="summary">Items choosen for copy</div>
        </div>
  ...
    <thead>
      <tr>
        <th>X</th>
        <th>Name</th>
        <th>Created</th>
        <th>Modified</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="first"  /></td>
        <td>first</td>
        <td>01/01/01 01:01</td>
        <td>02/02/02 02:02</td>
      </tr>
      <tr>
        <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="fourth"  /></td>
        <td>fourth</td>
        <td>01/01/01 01:01</td>
        <td>02/02/02 02:02</td>
      </tr>
      <tr>
        <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="second"  /></td>
        <td>second</td>
        <td>01/01/01 01:01</td>
        <td>02/02/02 02:02</td>
      </tr>
      <tr>
        <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="third"  /></td>
        <td>third</td>
        <td>01/01/01 01:01</td>
        <td>02/02/02 02:02</td>
      </tr>
      <tr>
        <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="zero" checked="checked" /></td>
        <td>zero</td>
        <td>01/01/01 01:01</td>
        <td>02/02/02 02:02</td>
      </tr>
    </tbody>
  ...


Copy - Paste
------------

Now we can go to the second page and paste our selected object. Just prepare
a request which simualtes that we clicked at the paste button and we can see
that we pasted the selected item to the second container. You can see that 
there is an additional ``Paste`` button becase we have some items for paste
in the clipboard:

  >>> pasteRequest = TestRequest(form={'contents.buttons.paste': 'Paste'})
  >>> alsoProvides(pasteRequest, IDivFormLayer)
  >>> pastePage = browser.ContentsPage(secondContainer, pasteRequest)
  >>> pastePage.update()
  >>> print pastePage.render()
  <form action="http://127.0.0.1" method="post"
        enctype="multipart/form-data" class="edit-form"
        name="contents" id="contents">
  ...
        <div class="status">
          <div class="summary">Data successfully pasted</div>
        </div>
  ...
    <thead>
      <tr>
        <th>X</th>
        <th>Name</th>
        <th>Created</th>
        <th>Modified</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="zero"  /></td>
        <td>zero</td>
        <td>01/01/01 01:01</td>
        <td>02/02/02 02:02</td>
      </tr>
    </tbody>
  ...
      <div>
        <div class="buttons">
          <input type="submit" id="contents-buttons-copy"
                 name="contents.buttons.copy"
                 class="submit-widget button-field" value="Copy" />
          <input type="submit" id="contents-buttons-cut"
                 name="contents.buttons.cut"
                 class="submit-widget button-field" value="Cut" />
          <input type="submit" id="contents-buttons-paste"
                 name="contents.buttons.paste"
                 class="submit-widget button-field" value="Paste" />
          <input type="submit" id="contents-buttons-delete"
                 name="contents.buttons.delete"
                 class="submit-widget button-field" value="Delete" />
          <input type="submit" id="contents-buttons-rename"
                 name="contents.buttons.rename"
                 class="submit-widget button-field" value="Rename" />
        </div>
      </div>
    </form>


Cut
---

This part shows how to cut an object from one container and paste it to another
container.

  >>> cutRequest = TestRequest(
  ...     form={'contents-checkBoxColumn-0-selectedItems': ['first', 'second'],
  ...           'contents.buttons.cut': 'Cut'})
  >>> alsoProvides(cutRequest, IDivFormLayer)
  >>> cutPage = browser.ContentsPage(container, cutRequest)
  >>> cutPage.update()
  >>> print cutPage.render()
  <form action="http://127.0.0.1" method="post"
        enctype="multipart/form-data" class="edit-form"
        name="contents" id="contents">
  ...
        <div class="status">
          <div class="summary">Items selected for cut</div>
        </div>
  ...
    <table>
      <thead>
        <tr>
          <th>X</th>
          <th>Name</th>
          <th>Created</th>
          <th>Modified</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="first" checked="checked" /></td>
          <td>first</td>
          <td>01/01/01 01:01</td>
          <td>02/02/02 02:02</td>
        </tr>
        <tr>
          <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="fourth"  /></td>
          <td>fourth</td>
          <td>01/01/01 01:01</td>
          <td>02/02/02 02:02</td>
        </tr>
        <tr>
          <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="second" checked="checked" /></td>
          <td>second</td>
          <td>01/01/01 01:01</td>
          <td>02/02/02 02:02</td>
        </tr>
        <tr>
          <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="third"  /></td>
          <td>third</td>
          <td>01/01/01 01:01</td>
          <td>02/02/02 02:02</td>
        </tr>
        <tr>
          <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="zero"  /></td>
          <td>zero</td>
          <td>01/01/01 01:01</td>
          <td>02/02/02 02:02</td>
        </tr>
      </tbody>
    </table>
  ...

Cut - Paste
-----------

And we can paste the selectded items to the second container:

  >>> pasteRequest = TestRequest(form={'contents.buttons.paste': 'Paste'})
  >>> alsoProvides(pasteRequest, IDivFormLayer)
  >>> pastePage = browser.ContentsPage(secondContainer, pasteRequest)
  >>> pastePage.update()
  >>> print pastePage.render()
  <form action="http://127.0.0.1" method="post"
        enctype="multipart/form-data" class="edit-form"
        name="contents" id="contents">
  ...
        <div class="status">
          <div class="summary">Data successfully pasted</div>
        </div>
  ...
  <table>
    <thead>
      <tr>
        <th>X</th>
        <th>Name</th>
        <th>Created</th>
        <th>Modified</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="first"  /></td>
        <td>first</td>
        <td>01/01/01 01:01</td>
        <td>02/02/02 02:02</td>
      </tr>
      <tr>
        <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="second"  /></td>
        <td>second</td>
        <td>01/01/01 01:01</td>
        <td>02/02/02 02:02</td>
      </tr>
      <tr>
        <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="zero"  /></td>
        <td>zero</td>
        <td>01/01/01 01:01</td>
        <td>02/02/02 02:02</td>
      </tr>
    </tbody>
  </table>
  ...
    <div>
      <div class="buttons">
        <input type="submit" id="contents-buttons-copy"
         name="contents.buttons.copy"
         class="submit-widget button-field" value="Copy" />
        <input type="submit" id="contents-buttons-cut"
         name="contents.buttons.cut"
         class="submit-widget button-field" value="Cut" />
        <input type="submit" id="contents-buttons-delete"
         name="contents.buttons.delete"
         class="submit-widget button-field" value="Delete" />
        <input type="submit" id="contents-buttons-rename"
         name="contents.buttons.rename"
         class="submit-widget button-field" value="Rename" />
      </div>
    </div>
  </form>


As you can see the first page does not contain the ``first`` and ``second`` 
item after paste them to the second container. Also the ``paste button`` is
gone:

  >>> firstPage.update()
  >>> print firstPage.render()
  <form action="http://127.0.0.1" method="post"
        enctype="multipart/form-data" class="edit-form"
        name="contents" id="contents">
  ...
  <table>
    <thead>
      <tr>
        <th>X</th>
        <th>Name</th>
        <th>Created</th>
        <th>Modified</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="fourth"  /></td>
        <td>fourth</td>
        <td>01/01/01 01:01</td>
        <td>02/02/02 02:02</td>
      </tr>
      <tr>
        <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="third"  /></td>
        <td>third</td>
        <td>01/01/01 01:01</td>
        <td>02/02/02 02:02</td>
      </tr>
      <tr>
        <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="zero"  /></td>
        <td>zero</td>
        <td>01/01/01 01:01</td>
        <td>02/02/02 02:02</td>
      </tr>
    </tbody>
  </table>
  ...
    <div>
      <div class="buttons">
        <input type="submit" id="contents-buttons-copy"
               name="contents.buttons.copy"
               class="submit-widget button-field" value="Copy" />
        <input type="submit" id="contents-buttons-cut"
               name="contents.buttons.cut"
               class="submit-widget button-field" value="Cut" />
        <input type="submit" id="contents-buttons-delete"
               name="contents.buttons.delete"
               class="submit-widget button-field" value="Delete" />
        <input type="submit" id="contents-buttons-rename"
               name="contents.buttons.rename"
               class="submit-widget button-field" value="Rename" />
      </div>
    </div>
  </form>


Delete
------

The contents page offers also an option for delete items. Let's select some
items and click the delete button:

  >>> deleteRequest = TestRequest(
  ...     form={'contents-checkBoxColumn-0-selectedItems': ['third', 'fourth'],
  ...           'contents.buttons.delete': 'Delete'})
  >>> alsoProvides(deleteRequest, IDivFormLayer)
  >>> deletePage = browser.ContentsPage(container, deleteRequest)
  >>> deletePage.update()
  >>> print deletePage.render()
  <form action="http://127.0.0.1" method="post"
        enctype="multipart/form-data" class="edit-form"
        name="contents" id="contents">
  ...
        <div class="status">
          <div class="summary">Data successfully deleted</div>
        </div>
  ...
  <table>
    <thead>
      <tr>
        <th>X</th>
        <th>Name</th>
        <th>Created</th>
        <th>Modified</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="zero"  /></td>
        <td>zero</td>
        <td>01/01/01 01:01</td>
        <td>02/02/02 02:02</td>
      </tr>
    </tbody>
  </table>
  ...

Rename
------

If we like to rename items, we can do this with the ``Rename`` button. This
means if we use them, we will get input widgets for the selected items rendered
in the table. After that, we can click the botton another time which will 
do the renaming. Let's setup a table which we select items and click the 
``Rename`` button:

  >>> renameRequest = TestRequest(
  ...     form={'contents-checkBoxColumn-0-selectedItems': ['first', 'second'],
  ...           'contents.buttons.rename': 'Rename'})
  >>> alsoProvides(renameRequest, IDivFormLayer)
  >>> renamePage = browser.ContentsPage(secondContainer, renameRequest)
  >>> renamePage.update()
  >>> print renamePage.render()
  <form action="http://127.0.0.1" method="post"
        enctype="multipart/form-data" class="edit-form"
        name="contents" id="contents">
  ...
  <table>
    <thead>
      <tr>
        <th>X</th>
        <th>Name</th>
        <th>Created</th>
        <th>Modified</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="first" checked="checked" /></td>
        <td>first&nbsp;<input type="text" name="contents-renameColumn-1-Zmlyc3Q=-rename" value="first" /></td>
        <td>01/01/01 01:01</td>
        <td>02/02/02 02:02</td>
      </tr>
      <tr>
        <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="second" checked="checked" /></td>
        <td>second&nbsp;<input type="text" name="contents-renameColumn-1-c2Vjb25k-rename" value="second" /></td>
        <td>01/01/01 01:01</td>
        <td>02/02/02 02:02</td>
      </tr>
      <tr>
        <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="zero"  /></td>
        <td>zero</td>
        <td>01/01/01 01:01</td>
        <td>02/02/02 02:02</td>
      </tr>
    </tbody>
  </table>
  ...

Now we rename the ``second`` item to ``fifth``:

  >>> renameRequest = TestRequest(
  ...     form={'contents-checkBoxColumn-0-selectedItems': ['first', 'second'],
  ...           'contents-renameColumn-1-Zmlyc3Q=-rename': 'first',
  ...           'contents-renameColumn-1-c2Vjb25k-rename': 'fifth',
  ...           'contents.buttons.rename': 'Rename'})
  >>> alsoProvides(renameRequest, IDivFormLayer)
  >>> renamePage = browser.ContentsPage(secondContainer, renameRequest)
  >>> renamePage.update()
  >>> print renamePage.render()
  <form action="http://127.0.0.1" method="post"
        enctype="multipart/form-data" class="edit-form"
        name="contents" id="contents">
    <div class="viewspace">
        <div class="required-info">
           <span class="required">*</span>
           &ndash; required
        </div>
        <div class="status">
          <div class="summary">Could not rename all selected items</div>
        </div>
      <div>
    <table>
      <thead>
        <tr>
          <th>X</th>
          <th>Name</th>
          <th>Created</th>
          <th>Modified</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="fifth"  /></td>
          <td>fifth</td>
          <td>01/01/01 01:01</td>
          <td>02/02/02 02:02</td>
        </tr>
        <tr>
          <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="first" checked="checked" /></td>
          <td>first&nbsp;<input type="text" name="contents-renameColumn-1-Zmlyc3Q=-rename" value="first" />No new name given</td>
          <td>01/01/01 01:01</td>
          <td>02/02/02 02:02</td>
        </tr>
        <tr>
          <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="zero"  /></td>
          <td>zero</td>
          <td>01/01/01 01:01</td>
          <td>02/02/02 02:02</td>
        </tr>
      </tbody>
    </table>
  ...

If we try to rename one item to another items name we will get a duplication 
error. Let's test this:

  >>> renameRequest = TestRequest(
  ...     form={'contents-checkBoxColumn-0-selectedItems': ['fifth', 'first'],
  ...           'contents-renameColumn-1-Zmlyc3Q=-rename': 'fifth',
  ...           'contents-renameColumn-1-ZmlmdGg=-rename': 'first',
  ...           'contents.buttons.rename': 'Rename'})
  >>> alsoProvides(renameRequest, IDivFormLayer)
  >>> renamePage = browser.ContentsPage(secondContainer, renameRequest)
  >>> renamePage.update()
  >>> print renamePage.render()
  <form action="http://127.0.0.1" method="post"
        enctype="multipart/form-data" class="edit-form"
        name="contents" id="contents">
    <div class="viewspace">
      <div class="required-info">
         <span class="required">*</span>
         &ndash; required
      </div>
      <div class="status">
        <div class="summary">Could not rename all selected items</div>
      </div>
      <div>
        <table>
          <thead>
            <tr>
              <th>X</th>
              <th>Name</th>
              <th>Created</th>
              <th>Modified</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="fifth" checked="checked" /></td>
              <td>fifth&nbsp;<input type="text" name="contents-renameColumn-1-ZmlmdGg=-rename" value="first" />Duplicated item name</td>
              <td>01/01/01 01:01</td>
              <td>02/02/02 02:02</td>
            </tr>
            <tr>
              <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="first" checked="checked" /></td>
              <td>first&nbsp;<input type="text" name="contents-renameColumn-1-Zmlyc3Q=-rename" value="fifth" />Duplicated item name</td>
              <td>01/01/01 01:01</td>
              <td>02/02/02 02:02</td>
            </tr>
            <tr>
              <td><input type="checkbox" class="checkbox-widget" name="contents-checkBoxColumn-0-selectedItems" value="zero"  /></td>
              <td>zero</td>
              <td>01/01/01 01:01</td>
              <td>02/02/02 02:02</td>
            </tr>
          </tbody>
        </table>
  ...

As you can see everything goes right. We can check the containers which should
reflect the same as we see in the tables. Note the ``third`` and ``foruth`` 
items get deleted and are gone now and the ``second`` item get renamed to 
``fifth``:

  >>> sorted(container.items())
  [(u'zero', <Content Zero 0>)]

  >>> sorted(secondContainer.items())
  [(u'fifth', <Content Second 2>), (u'first', <Content First 1>),
   (u'zero', <Content Zero 0>)]
