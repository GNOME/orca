# Orca
#
# Copyright 2004-2005 Sun Microsystems Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.
#
#

"""Manages the Accessible class.  The main purpose of this class is to provide
a cache of Accessibility_Accessible objects and to keep that cache in sync
with the real objects.  Each Accessible instance is backed by an
Accessibility_Accessible object.

The main entry point to this module is the makeAccessible factory method.
This class keeps a cache of known accessible objects and only creates a
new one if necessary.  [[[TODO:  WDW - might consider the new-style class
__new__ method to handle singletons like this.]]]

This module also provides a number of convenience functions for working with
Accessible objects.
"""

import core
import debug
import rolenames

########################################################################
#                                                                      #
# DEBUG support.                                                       #
#                                                                      #
########################################################################
            
def getStateString(obj):
    """Returns a space-delimited string composed of the given object's
    Accessible state attribute.  This is for debug purposes.

    Arguments:
    - obj: an Accessible
    """
    
    set = obj.state
    stateString = " "
    if set.count(core.Accessibility.STATE_INVALID):
        stateString += "INVALID "
    if set.count(core.Accessibility.STATE_ACTIVE):
        stateString += "ACTIVE "
    if set.count(core.Accessibility.STATE_ARMED):
        stateString += "ARMED "
    if set.count(core.Accessibility.STATE_BUSY):
        stateString += "BUSY "
    if set.count(core.Accessibility.STATE_CHECKED):
        stateString += "CHECKED "
    if set.count(core.Accessibility.STATE_COLLAPSED):
        stateString += "COLLAPSED "
    if set.count(core.Accessibility.STATE_DEFUNCT):
        stateString += "DEFUNCT "
    if set.count(core.Accessibility.STATE_EDITABLE):
        stateString += "EDITABLE "
    if set.count(core.Accessibility.STATE_ENABLED):
        stateString += "ENABLED "
    if set.count(core.Accessibility.STATE_EXPANDABLE):
        stateString += "EXPANDABLE "
    if set.count(core.Accessibility.STATE_EXPANDED):
        stateString += "EXPANDED "
    if set.count(core.Accessibility.STATE_FOCUSABLE):
        stateString += "FOCUSABLE "
    if set.count(core.Accessibility.STATE_FOCUSED):
        stateString += "FOCUSED "
    if set.count(core.Accessibility.STATE_HAS_TOOLTIP):
        stateString += "HAS_TOOLTIP "
    if set.count(core.Accessibility.STATE_HORIZONTAL):
        stateString += "HORIZONTAL "
    if set.count(core.Accessibility.STATE_ICONIFIED):
        stateString += "ICONIFIED "
    if set.count(core.Accessibility.STATE_MODAL):
        stateString += "MODAL "
    if set.count(core.Accessibility.STATE_MULTI_LINE):
        stateString += "MULTI_LINE "
    if set.count(core.Accessibility.STATE_MULTISELECTABLE):
        stateString += "MULTISELECTABLE "
    if set.count(core.Accessibility.STATE_OPAQUE):
        stateString += "OPAQUE "
    if set.count(core.Accessibility.STATE_PRESSED):
        stateString += "PRESSED "
    if set.count(core.Accessibility.STATE_RESIZABLE):
        stateString += "RESIZABLE "
    if set.count(core.Accessibility.STATE_SELECTABLE):
        stateString += "SELECTABLE "
    if set.count(core.Accessibility.STATE_SELECTED):
        stateString += "SELECTED "
    if set.count(core.Accessibility.STATE_SENSITIVE):
        stateString += "SENSITIVE "
    if set.count(core.Accessibility.STATE_SHOWING):
        stateString += "SHOWING "
    if set.count(core.Accessibility.STATE_SINGLE_LINE):
        stateString += "SINGLE_LINE " 
    if set.count(core.Accessibility.STATE_STALE):
        stateString += "STALE "
    if set.count(core.Accessibility.STATE_TRANSIENT):
        stateString += "TRANSIENT " 
    if set.count(core.Accessibility.STATE_VERTICAL):
        stateString += "VERTICAL "
    if set.count(core.Accessibility.STATE_VISIBLE):
        stateString += "VISIBLE "
    if set.count(core.Accessibility.STATE_MANAGES_DESCENDANTS):
        stateString += "MANAGES_DESCENDANTS "
    if set.count(core.Accessibility.STATE_INDETERMINATE):
        stateString += "INDETERMINATE "

    return stateString;


def accessibleToString(indent, accessible):
    if not accessible:
        return None
    
    string = ""
    string = string + "%sname   = (%s)\n" \
             % (indent, accessible.name)
    string = string + "%srole   = (%s)\n" \
             % (indent, rolenames.getRoleName(accessible))
    string = string +  "%sstate  = (%s)\n" \
             % (indent, getStateString(accessible))

    if accessible.app is None:
        string = string + "%sapp    = (None)" % indent
    else:
        string = string + "%sapp    = (%s)" % (indent, accessible.app.name)

    return string


def printDetails(level, indent, accessible):
    """Lists the details of the given accessible with the given
    indentation.

    Arguments:
    - level: the accepted debug level
    - indent: a string containing spaces for indentation
    - accessible: the accessible whose details are to be listed
    """

    debug.println(level, accessibleToString(indent, accessible))
        

########################################################################
#                                                                      #
# The Accessible class.                                                #
#                                                                      #
########################################################################
    
def makeAccessible(acc):
    """Make an Accessible.  This is used instead of a simple calls to
    Accessible's constructor because the object may already be in the
    cache.

    Arguments:
    - acc: the AT-SPI Accessibility_Accessible

    Returns a Python Accessible.
    """

    if acc is None:
        return None

    obj = None

    if Accessible._cache.has_key(acc):
        obj = Accessible._cache[acc]
    else:
        obj = Accessible(acc)

    return obj


class Accessible:
    """Wraps AT-SPI Accessible objects and caches properties such as
    name, description, and parent.

    It also adds some properties to the AT-SPI Accessible including
    the Application to which the object belongs.

    For efficiency purposes, this class also maintains a cache of all
    Accessible objects obtained so far, and will return an element
    from that cache instead of creating a duplicate object.
    """

    # The cache of the currently active accessible objects.  The key is
    # the AT-SPI Accessible, and the value is the Python Accessible.
    # [[[TODO: WDW - probably should look at the __new__ method as a means
    # to handle singletons.]]]
    #
    _cache = {} 

    def __init__(self, acc):
        """Obtains, and creates if necessary, a Python Accessible from
        an AT-SPI Accessibility_Accessible.  Applications should not
        call this method, but should instead call makeAccessible.
        
        Arguments:
        - acc: the AT-SPI Accessibility_Accessible
        
        Returns the associated Python Accessible.
        """

        # [[[TODO: WDW - should do an assert here to make sure we're
        # getting a raw AT-SPI Accessible and not one of our own locally
        # cached Accessible instances.]]]
        #
        if Accessible._cache.has_key(acc):
            return

        # The acc reference might be an Accessibility_Accessible or an
        # Accessibility_Application, so try both.  The setting of self.acc
        # to None here is merely to help with manual and unit testing of
        # this module.
        #
        try:
            self.acc = acc._narrow(core.Accessibility.Application)
        except:
            try:
                self.acc = acc._narrow(core.Accessibility.Accessible)
            except:
                debug.printException(debug.LEVEL_SEVERE)
                self.acc = None

        # Keep track of whether this object is defunct or not.  It's
        # not the case that we can check the state of a defunct object
        # to see if its defunct state has been set - remember, the object
        # is defunct and we cannot ask it anything.
        #
        self.defunct = False

        # Save a reference to the AT-SPI object, and also save this
        # new object away in the cache.
        #
        if self.acc:
            self.acc.ref()
            Accessible._cache[acc] = self

        
    def __del__(self):
        """Unrefs the AT-SPI Accessible associated with this object.
        """
        try:
            del Accessible._cache[sel.acc]
            self.acc.unref()
        except:
            pass


    def __get_name(self):
        """Returns the object's accessible name as a string.
        """

        self.name = self.acc.name
        return self.name


    def __get_description(self):
        """Returns the object's accessible description as a string.
        """

        self.description = self.acc.description
        return self.description


    def __get_parent(self):
        """Returns the object's parent as a Python Accessible.  If
        this object has no parent, None will be returned.
        """

        # We will never set self.parent if the backing accessible doesn't
        # have a parent.  The reason we do this is that we may sometimes
        # get events for objects without a parent, but then the object ends
        # up getting a parent later on.
        #
        obj = self.acc.parent
        if obj is None:
            return None
        else:
            self.parent = makeAccessible(obj);
            return self.parent;


    def __get_child_count(self):
        """Returns the number of children for this object.
        """

        self.childCount = self.acc.childCount
        return self.childCount


    def __get_index(self):
        """Returns the index of this object in its parent's child list.
        """

        self.index = self.acc.getIndexInParent()
        return self.index


    def __get_role(self):
        """Returns the Accessible role name of this object as a string.
        This string is not localized and can be used for comparison.
        """
        
        self.role = self.acc.getRoleName()
        return self.role


    def __get_state(self):
        """Returns the Accessible StateSeq of this object, which is a
        sequence of Accessible StateTypes.
        """

        set = self.acc.getState()
        set = set._narrow(core.Accessibility.StateSet)
        self.state = set.getStates()
        return self.state


    def __get_relations(self):
        """Returns the Accessible RelationSet of this object as a list.
        """

        relations = self.acc.getRelationSet()
        self.relations = []
        for relation in relations:
            self.relations.append(relation._narrow(
                core.Accessibility.Relation))
                                   
        return self.relations


    def __get_app(self):
        """Returns the AT-SPI Accessibility_Application associated with this
        object.  Returns None if the application cannot be found (usually
        the indication of an AT-SPI bug).
        """
        
        # [[[TODO: WDW - this code seems like it might break if this
        # object is an application to begin with.]]]
        #
        debug.println(debug.LEVEL_FINEST,
                      "Finding app for source=(" + self.name + ")")
        obj = self
        while (obj.parent != None) and (obj != obj.parent):
            obj = obj.parent
            debug.println(debug.LEVEL_FINEST,
                          "--> parent=(" + obj.name + ")")
        if (obj.parent != None):
            debug.println(debug.LEVEL_FINEST,
                          "--> obj=(" + obj.name
                          + ") parent=(" + obj.parent.name + ")")
            if (obj == obj.parent):
                debug.println(debug.LEVEL_SEVERE,
                              "    ERROR: obj == obj.parent!")
        else:
            debug.println(debug.LEVEL_FINEST,
                          "--> obj=(" + obj.name
                          + ") parent=(None)")
            
        if (obj == obj.parent) \
               or (obj.role != rolenames.ROLE_APPLICATION):
            self.app = None
        else:
            self.app = obj
        
        return self.app

    def __get_extents(self, coordinateType = 0):
        """Returns the object's accessible extents as an
        Accessibility.BoundingBox object, or None if the object doesn't
        implement the Accessibility Component interface.

        Arguments:
        - coordinateType: 0 = get the extents in screen coordinates,
                          1 = get the extents in window coordinates

        Returns:
        This object's accessible extents as an Accessibility.BoundingBox
        object, or None if the object doesn't implement the Accessibility
        Component interface.
        """

        component = self.component
        if component is None:
            return None
        else:
            self.extents = component.getExtents(coordinateType)
            return self.extents
        

    def __get_label(self):
        """Returns an object's label as a string.  The label is determined
        using the following logic:

        1. If the object has a LABELLED_BY relation, return the text of
           the targets of this relation

        2. Else if the object has no LABELLED_BY relation, return the name
           
        3. Else if the object has no name, return the description

        4. Else return an empty string
        """

        label = ""

        # Does the object have a relation set?
        #
        relations = self.relations
        for relation in relations:
            if relation.getRelationType() \
                   == core.Accessibility.RELATION_LABELLED_BY:
                target = makeAccessible(relation.getTarget(0))
                label = target.name
                break

        # If the object doesn't have a relation, but has a name, return
        # that
        #
        if (len(label) == 0) and (self.name is not None) \
               and (len(self.name) > 0):
            label = self.name

        # If the object has no name, but has a description, return that
        #
        elif (len(label) == 0) and (self.description is not None) \
                 and (len(self.description) > 0):
            label = self.description

        self.label = label
        return self.label


    def __get_action(self):
        """Returns an object that implements the Accessibility_Action
        interface for this object, or None if this object doesn't implement
        the Accessibility_Action interface.
        """

        bobj = self.acc._narrow(core.Accessibility.Accessible)
        action = bobj.queryInterface("IDL:Accessibility/Action:1.0")
        if action is not None:
            action = action._narrow(core.Accessibility.Action)
        self.action = action
        return self.action


    def __get_component(self):
        """Returns an object that implements the Accessibility_Component
        interface for this object, or None if this object doesn't implement
        the Accessibility_Component interface.
        """

        self.component = None

        try:
            bobj = self.acc._narrow(core.Accessibility.Accessible)
            component = bobj.queryInterface("IDL:Accessibility/Component:1.0")
            if component is not None:
                component = component._narrow(core.Accessibility.Component)
                self.component = component
        except:
            pass
        
        return self.component


    def __get_hypertext(self):
        """Returns an object that implements the Accessibility_Hypertext
        interface for this object, or None if this object doesn't implement
        the Accessibility_Hypertext interface.
        """

        bobj = self.acc._narrow(core.Accessibility.Accessible)
        hypertext = bobj.queryInterface("IDL:Accessibility/Hypertext:1.0")
        if hypertext is not None:
            hypertext = hypertext._narrow(core.Accessibility.Hypertext)
        self.hypertext = hypertext
        return self.hypertext


    def __get_selection(self):
        """Returns an object that implements the Accessibility_Selection
        interface for this object, or None if this object doesn't implement
        the Accessibility_Selection interface.
        """

        bobj = self.acc._narrow(core.Accessibility.Accessible)
        sel = bobj.queryInterface("IDL:Accessibility/Selection:1.0")
        if sel is not None:
            sel = sel._narrow(core.Accessibility.Selection)
        self.selection = sel
        return self.selection


    def __get_table(self):
        """Returns an object that implements the Accessibility_Table
        interface for this object, or None if this object doesn't implement
        the Accessibility_Table interface.
        """

        bobj = self.acc._narrow(core.Accessibility.Accessible)
        table = bobj.queryInterface("IDL:Accessibility/Table:1.0")
        if table is not None:
            table = table._narrow(core.Accessibility.Table)
        self.table = table
        return self.table


    def __get_text(self):
        """Returns an object that implements the Accessibility_Text
        interface for this object, or None if this object doesn't implement
        the Accessibility_Text interface.
        """

        bobj = self.acc._narrow(core.Accessibility.Accessible)
        text = bobj.queryInterface("IDL:Accessibility/Text:1.0")
        if text is not None:
            text = text._narrow(core.Accessibility.Text)
        self.text = text
        return self.text


    def __get_value(self):
        """Returns an object that implements the Accessibility_Value
        interface for this object, or None if this object doesn't implement
        the Accessibility_Value interface.
        """

        bobj = self.acc._narrow(core.Accessibility.Accessible)
        value = bobj.queryInterface("IDL:Accessibility/Value:1.0")
        if value is not None:
            value = value._narrow(core.Accessibility.Value)
        self.value = value
        return self.value


    def __get_value(self):
        """Returns an object that implements the Accessibility_Value
        interface for this object, or None if this object doesn't implement
        the Accessibility_Value interface.
        """

        bobj = self.acc._narrow(core.Accessibility.Accessible)
        value = bobj.queryInterface("IDL:Accessibility/Value:1.0")
        if value is not None:
            value = value._narrow(core.Accessibility.Value)
        self.value = value
        return self.value


    def __getattr__(self, attr):
        """Created virtual attributes for the Accessible object to make
        the syntax a bit nicer (e.g., acc.name rather than acc.name()).
        This method is also called if and only if the given attribute
        does not exist in the object.  Thus, we're effectively lazily
        building a cache to the remote object attributes here.
        
        Arguments:
        - attr: a string indicating the attribute name to retrieve

        Returns the value of the given attribute.
        """
 
        #print "__getattr__ defunct=%s attr=%s" % (self.defunct, attr)
        
        if attr == "name":
            return self.__get_name()
        elif attr == "label":
            return self.__get_label()
        elif attr == "description":
            return self.__get_description()
        elif attr == "parent":
            return self.__get_parent()
        elif attr == "childCount":
            return self.__get_child_count()
        elif attr == "index":
            return self.__get_index()
        elif attr == "role":
            return self.__get_role()
        elif attr == "state":
            return self.__get_state()
        elif attr == "relations":
            return self.__get_relations()
        elif attr == "app":
            return self.__get_app()
        elif attr == "extents":
            return self.__get_extents()
        elif attr == "action":
            return self.__get_action()
        elif attr == "component":
            return self.__get_component()
        elif attr == "hypertext":
            return self.__get_hypertext()
        elif attr == "selection":
            return self.__get_selection()
        elif attr == "table":
            return self.__get_table()
        elif attr == "text":
            return self.__get_text()
        elif attr == "value":
            return self.__get_value()
        elif attr.startswith('__') and attr.endswith('__'):
            raise AttributeError, attr
        else:
            return self.__dict__[attr]

    def child(self, index):
        """Returns the specified child of this object.

        Arguments:
        - index: an integer specifying which child to obtain

        Returns the child at the given index.  [[[TODO: WDW - what to do
        when an index out of bounds occurs?]]]
        """

        # Save away details we now know about this child
        #
        try:
            acc = self.acc.getChildAtIndex(index)
            if acc is None:
                return None
            newChild = makeAccessible(acc)
            newChild.index = index
            newChild.parent = self
            newChild.app = self.app
            return newChild
        except:
            debug.printException(debug.LEVEL_SEVERE)
            return None


########################################################################
#                                                                      #
# Methods for handling AT-SPI events.                                  #
#                                                                      #
########################################################################

def onNameChanged(e):
    """Core module event listener called when an object's name
    changes.  Updates the cache accordingly.

    Arguments:
    - e: AT-SPI event from the AT-SPI registry
    """

    if Accessible._cache.has_key(e.source):
        obj = Accessible._cache[e.source]
        obj.name = e.any_data


def onDescriptionChanged(e):
    """Core module event listener called when an object's description
    changes.  Updates the cache accordingly.

    Arguments:
    - e: AT-SPI event from the AT-SPI registry
    """

    if Accessible._cache.has_key(e.source):
        obj = Accessible._cache[e.source]
        obj.description = e.any_data


def onParentChanged(e):
    """Core module event listener called when an object's parent
    changes.  Updates the cache accordingly.

    Arguments:
    - e: AT-SPI event from the AT-SPI registry
    """

    # [[[TODO: WDW - I put this in here for now.  The idea is that
    # we will probably get parent changed events for objects that
    # are or will soon be defunct, so let's just forget about the
    # object rather than try to keep the cache in sync.]]]
    #
    if Accessible._cache.has_key(e.source):
        del Accessible._cache[e.source]
    return
    
    # This could fail if the e.source is now defunct.  [[[TODO: WDW - there
    # may be some really bad timing issues here.  Remember that the AT-SPI
    # events are added to a queue for processing later.  So...we could
    # potentially be processing queued events for an object that has been
    # pronounced defunct in a later event.]]]
    #
    obj = makeAccessible(e.source)

    if obj.__dict__.has_key("parent"):
        del obj.parent
        
    if obj.__dict__.has_key("app"):
        del obj.app
    

def onStateChanged(e):
    """Core module event listener called when an object's state
    changes.  Updates the cache accordingly.

    Arguments:
    - e: AT-SPI event from the AT-SPI registry
    """

    if Accessible._cache.has_key(e.source):
        obj = Accessible._cache[e.source]
        
        # Let's get rid of defunct objects.  We hate them.
        #
        if e.type == "object:state-changed:defunct":
            obj.defunct = True
            del Accessible._cache[e.source]
        elif obj.__dict__.has_key("state"):
            del obj.state


def onChildrenChanged(e):
    """Core module event listener called when an object's child count
    changes.  Updates the cache accordingly.

    Arguments:
    - e: AT-SPI event from the AT-SPI registry
    """

    if Accessible._cache.has_key(e.source):
        obj = Accessible._cache[e.source]
        if obj.__dict__.has_key("childCount"):
            del obj.childCount


########################################################################
#                                                                      #
# Utility methods.                                                     #
#                                                                      #
########################################################################

_initialized = False


def isDefunct(acc):
    """If we've made an Accessible for an object, return True if it has
    been flagged as defunct.  Otherwise, return False.

    Arguments:
    - acc: an AT-SPI (not Python) Accessible
    """
    
    if Accessible._cache.has_key(acc):
        obj = Accessible._cache[acc]
        return obj.defunct
    else:
        return False

    
def init():
    """Initialize the a11y module.  This also intializes the core
    module and registers the various core module event listeners in
    this module with the core module.

    Returns True if the module has been successfully initialized.
    """
    
    global _initialized
    if _initialized:
        return True

    # Register our various listeners.
    #
    core.init()
    core.registerEventListener(
        onNameChanged, "object:property-change:accessible-name")
    core.registerEventListener(
        onDescriptionChanged, "object:property-change:accessible-description")
    core.registerEventListener(
        onParentChanged, "object:property-change:accessible-parent")
    core.registerEventListener(
        onStateChanged, "object:state-changed:")
    core.registerEventListener(
        onChildrenChanged, "object:children-changed:")

    _initialized = True
    return True


def shutdown():
    """Shuts down this module as well as the core module.
    [[[TODO: WDW - should this free the cache as well?]]]
    """
    
    global _initialized

    if not _initialized:
        return False

    core.unregisterEventListener(
        onNameChanged, "object:property-change:accessible-name")
    core.unregisterEventListener(
        onDescriptionChanged, "object:property-change:accessible-description")
    core.unregisterEventListener(
        onParentChanged, "object:property-change:accessible-parent")
    core.unregisterEventListener(
        onStateChanged, "object:state-changed:")
    core.unregisterEventListener(
        onChildrenChanged, "object:children-changed:")

    core.shutdown()

    _initialized = False
    return True


def getObjects(root):
    """Returns a list of all objects under the given root.  Objects
    are returned in no particular order - this function does a simple
    tree traversal, ignoring the children of objects which report the
    MANAGES_DESCENDANTS state is active.

    Arguments:
    - root: the Accessible object to traverse

    Returns: a list of all objects under the specified object
    """

    # The list of object we'll return
    #
    objlist = []

    # Start at the first child of the given object
    #
    if root.childCount <= 0:
        return objlist

    i = root.childCount - 1
    while i >= 0:
        child = root.child(i)
        if child:
            objlist.append(child)
            state = child.state
            if (state.count(core.Accessibility.STATE_MANAGES_DESCENDANTS) == 0) \
                   and (child.childCount > 0):
                objlist.extend(getObjects(child))
        i = i - 1
        
    return objlist


def findByRole(root, role):
    """Returns a list of all objects of a specific role beneath the
    given root.  [[[TODO: MM - This is very inefficient - this should
    do it's own traversal and not add objects to the list that aren't
    of the specified role.  Instead it uses the traversal from
    getObjects and then deletes objects from the list that aren't of
    the specified role.]]]

    Arguments:
    - root the Accessible object to traverse
    - role the string describing the Accessible role of the object
    
    Returns a list of descendants of the root that are of the given role.
    """
    
    objlist = []
    allobjs = getObjects(root)
    for o in allobjs:
        if o.role == role:
            objlist.append(o)
    return objlist


def findByName(root, name):
    """Returns a list of all objects beneath the specified object with
    the specified name.  [[[TODO: MM - This is very inefficient - this
    should do it's own traversal and not add objects to the list that
    don't have the specified name.  Instead it uses the traversal from
    getObjects and then deletes objects from the list that don't have
    the specified name.]]]

    Arguments:
    - root the Accessible object to traverse
    - name the string containing the Accessible name of the object
    
    Returns a list of descendants of the root that are of the given role.
    """

    objlist = []
    list = getObjects(root)

    # Create a new list containing only those objects with the
    # specified name
    #
    for o in list:
        if o.name == name:
            objlist.append(o)
    return objlist


def getFrame(obj):
    """Returns the frame containing this object, or None if this object
    is not inside a frame.

    Arguments:
    - obj: the Accessible object
    """

    while (obj != None) \
              and (obj != obj.parent) \
              and (obj.role != rolenames.ROLE_FRAME):
        obj = obj.parent

    if obj and (obj.role == rolenames.ROLE_FRAME):
        return obj
    else:
        return None


def getGroup(obj):
    """Returns a list of an object's group members if it has a MEMBER_OF
    relation, or None if it doesn't.  Note that an object itself will also be
    a part of the list that is returned.

    Arguments:
    - obj: the Accessible object

    Returns the list of the object's group members it has a MEMBER_OF
    relation, or None if it doesn't.
    """

    i = 0
    group = []
    relations = obj.relations
    for relation in relations:
        if relation.getRelationType() \
               == core.Accessibility.RELATION_MEMBER_OF:
            group[i] = makeAccessible(relation.getTarget(0))
            i = i + 1

    if i:
        return group
    else:
        return None


def getTextLineAtCaret(obj):
    """Gets the line of text where the caret is.

    Argument:
    - obj: an Accessible object that implements the AccessibleText
           interface

    Returns the line of text where the caret is.
    """

    # Get the the AccessibleText interrface
    #
    text = obj.text

    if text is None:
        return ["", 0, 0]
    
    # Get the line containing the caret
    #
    offset = text.caretOffset
    line = text.getTextAtOffset(offset,
                                core.Accessibility.TEXT_BOUNDARY_LINE_START)

    # Line is actually a list of objects-- the first is the actual
    # text of the line, the second is the start offset, and the third
    # is the end offset.  Sometimes we get the trailing line-feed-- remove it
    #
    if line[0][-1:] == "\n":
        content = line[0][:-1]
    else:
        content = line[0]

    return [content, offset, line[1]]


def getAcceleratorAndShortcut(obj):
    """Gets the accelerator string (and possibly shortcut) for the given
    object.

    Arguments:
    - obj: the Accessible object

    A list containing the accelerator and shortcut for the given object,
    where the first element is the accelerator and the second element is
    the shortcut.
    """

    action = obj.action

    if action is None:
        return ["", ""]

    # [[[TODO: WDW - assumes the first keybinding is all that we care about.]]]
    #
    bindingStrings = action.getKeyBinding(0).split(';')

    debug.println(debug.LEVEL_FINEST,
                  "KEYBINDINGS: " + action.getKeyBinding(0))
                  
    # [[[TODO: WDW - assumes menu items have three bindings]]]
    #
    if len(bindingStrings) == 3:
        mnemonic       = bindingStrings[0]
        fullShortcut   = bindingStrings[1]
        accelerator    = bindingStrings[2]
    elif len(bindingStrings) > 0:
        fullShortcut   = bindingStrings[0]
        accelerator    = ""
    else:
        fullShortcut   = ""
        accelerator    = ""
        
    fullShortcut = fullShortcut.replace("<","")
    fullShortcut = fullShortcut.replace(">"," ")
    fullShortcut = fullShortcut.replace(":"," ")

    accelerator  = accelerator.replace("<","")
    accelerator  = accelerator.replace(">"," ")

    return [accelerator, fullShortcut]
