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
import settings


# If True, attempt to cache accessible object information locally.
# If False, always use a CORBA call to get the object information.
#
CACHE_VALUES = True


########################################################################
#                                                                      #
# DEBUG support.                                                       #
#                                                                      #
########################################################################
            
def getStateString(obj):
    """Returns a space-delimited string composed of the given object's
    Accessible state attribute.  This is for debug purposes.

    NOTE: this will throw an InvalidObjectError exception if the AT-SPI
    Accessibility_Accessible can no longer be reached via CORBA.

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

    return stateString.strip()


def accessibleToString(indent, accessible):
    """Returns a string, suitable for printing, that describes the
    given accessible.

    NOTE: this will throw an InvalidObjectError exception if the AT-SPI
    Accessibility_Accessible can no longer be reached via CORBA.

    Arguments:
    - indent: A string to prefix the output with
    - accessible: the Accessible
    """
    
    if not accessible:
        return None

    appname = ""
    if accessible.app is None:
        appname = "None"
    else:
        appname = "'" + accessible.app.name + "'"
        
    string = indent + " app=%-20s" % appname

    string += " name='%s' role='%s' state='%s'" \
             % (accessible.name,
                rolenames.getRoleName(accessible),
                getStateString(accessible))
    
    return string


def printDetails(level, indent, accessible):
    """Lists the details of the given accessible with the given
    indentation.

    NOTE: this will throw an InvalidObjectError exception if the AT-SPI
    Accessibility_Accessible can no longer be reached via CORBA.

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

    NOTE: this will throw an InvalidObjectError exception if the AT-SPI
    Accessibility_Accessible can no longer be reached via CORBA.

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

    if obj.valid:
        return obj
    else:
        raise InvalidObjectError, "Attempting to use an invalid accessible"

class InvalidObjectError(EnvironmentError):
    """Used to indicate something is awry with the CORBA connection
    for an Accessible."""
    
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
        
        NOTE: this will throw an InvalidObjectError exception if the
        AT-SPI Accessibility_Accessible can no longer be reached via
        CORBA.

        Arguments:
        - acc: the AT-SPI Accessibility_Accessible to back this object
        
        Returns the associated Python Accessible.
        """
        
        # The setting of self._acc to None here is to help with manual
        # and unit testing of this module.  Furthermore, it helps us
        # determine if this particular instance is really backed by an
        # object or not.
        #
        self._acc = None

        # We'll also keep track of whether this object is any good to
        # us or not.  This object will be deleted when a defunct event
        # is received for it, but anything could happen prior to that
        # event, so we keep this extra field around to help us.
        #
        self.valid = False
        
        # [[[TODO: WDW - should do an assert here to make sure we're
        # getting a raw AT-SPI Accessible and not one of our own locally
        # cached Accessible instances.]]]
        #
        assert (not Accessible._cache.has_key(acc)), \
               "Attempt to create an Accessible that's already been made."
        
        # The acc reference might be an Accessibility_Accessible or an
        # Accessibility_Application, so try both.
        #
        try:
            self._acc = acc._narrow(core.Accessibility.Application)
        except:
            try:
                self._acc = acc._narrow(core.Accessibility.Accessible)
            except:
                debug.printException(debug.LEVEL_FINE)
                raise InvalidObjectError, "Unexpected issues with Accessible"

        # [[[TODO: WDW - the AT-SPI appears to give us a different accessible
        # when we repeatedly ask for the same child of a parent that manages
        # its descendants.  So...we probably shouldn't cache those kind of
        # children because we're likely to cause a memory leak.]]]
        #
        # Save a reference to the AT-SPI object, and also save this
        # new object away in the cache.
        #
        if self._acc:
            self._acc.ref()
            self.__origAcc = acc
            Accessible._cache[self.__origAcc] = self
            self.valid = True


    def __del__(self):
        """Unrefs the AT-SPI Accessible associated with this object.
        """

        if self._acc:
            try:
                self._acc.unref()
                del Accessible._cache[self.__origAcc]
            except:
                debug.printException(debug.LEVEL_FINE)


    def __get_name(self):
        """Returns the object's accessible name as a string.

        NOTE: this will throw an InvalidObjectError exception if the
        AT-SPI Accessibility_Accessible can no longer be reached via
        CORBA.
        """

        try:
            name = self._acc.name
            if CACHE_VALUES:
                self.name = name
            return name
        except:
            debug.printException(debug.LEVEL_FINE)
            self.valid = False
            raise InvalidObjectError, "Cannot get name"


    def __get_description(self):
        """Returns the object's accessible description as a string.

        NOTE: this will throw an InvalidObjectError exception if the
        AT-SPI Accessibility_Accessible can no longer be reached via
        CORBA.
        """

        try:
            description = self._acc.description
            if CACHE_VALUES:
                self.description = self._acc.description
            return description
        except:
            debug.printException(debug.LEVEL_FINE)
            self.valid = False
            raise InvalidObjectError, "Cannot get description"


    def __get_parent(self):
        """Returns the object's parent as a Python Accessible.  If
        this object has no parent, None will be returned.

        NOTE: this will throw an InvalidObjectError exception if the
        AT-SPI Accessibility_Accessible can no longer be reached via
        CORBA.
        """

        # We will never set self.parent if the backing accessible doesn't
        # have a parent.  The reason we do this is that we may sometimes
        # get events for objects without a parent, but then the object ends
        # up getting a parent later on.
        #
        try:
            obj = self._acc.parent
            if obj is None:
                return None
            else:
                parent = makeAccessible(obj);
                if CACHE_VALUES:
                    self.parent = parent
                return parent;
        except:
            debug.printException(debug.LEVEL_FINE)
            self.valid = False
            raise InvalidObjectError, "Cannot get parent"


    def __get_child_count(self):
        """Returns the number of children for this object.

        NOTE: this will throw an InvalidObjectError exception if the
        AT-SPI Accessibility_Accessible can no longer be reached via
        CORBA.
        """

        try:
            childCount = self._acc.childCount
            if CACHE_VALUES:
                self.childCount = childCount
            return childCount
        except:
            debug.printException(debug.LEVEL_FINE)
            self.valid = False
            raise InvalidObjectError, "Cannot get child count"


    def __get_index(self):
        """Returns the index of this object in its parent's child list.

        NOTE: this will throw an InvalidObjectError exception if the
        AT-SPI Accessibility_Accessible can no longer be reached via
        CORBA.
        """

        try:
            index = self._acc.getIndexInParent()
            if CACHE_VALUES:
                self.index = index
            return index
        except:
            debug.printException(debug.LEVEL_FINE)
            self.valid = False
            raise InvalidObjectError, "Cannot get index"
            

    def __get_role(self):
        """Returns the Accessible role name of this object as a string.
        This string is not localized and can be used for comparison.
        
        Note that this fudges the rolename of the object to match more closely
        what it is.  The only thing that is being fudged right now is to
        coalesce radio and check menu items that are also submenus; gtk-demo
        has an example of this in its menus demo.

        NOTE: this will throw an InvalidObjectError exception if the
        AT-SPI Accessibility_Accessible can no longer be reached via
        CORBA.
        """

        try:
            role = self._acc.getRoleName()
    
            # [[[TODO: WDW - HACK to coalesce menu items with children
            # into menus.  The menu demo in gtk-demo does this, and one
            # might view that as an edge case.  But, in gnome-terminal,
            # "Terminal" ->  "Set Character Encoding" is a menu item
            # with children, but it behaves like a menu.]]]
            #
            if (role == rolenames.ROLE_CHECK_MENU_ITEM) \
                and (self.childCount > 0):
                    role = rolenames.ROLE_CHECK_MENU
            elif (role == rolenames.ROLE_RADIO_MENU_ITEM) \
                and (self.childCount > 0):
                    role = rolenames.ROLE_RADIO_MENU
            elif (role == rolenames.ROLE_MENU_ITEM) \
                and (self.childCount > 0):
                    role = rolenames.ROLE_MENU

            if CACHE_VALUES:
                self.role = role
            return role
        except:
            debug.printException(debug.LEVEL_FINE)
            self.valid = False
            raise InvalidObjectError, "Cannot get role"
            

    def __get_state(self):
        """Returns the Accessible StateSeq of this object, which is a
        sequence of Accessible StateTypes.

        NOTE: this will throw an InvalidObjectError exception if the
        AT-SPI Accessibility_Accessible can no longer be reached via
        CORBA.
        """

        try:
            set = self._acc.getState()
            set = set._narrow(core.Accessibility.StateSet)
            state = set.getStates()
            if CACHE_VALUES:
                self.state = state
            return state
        except:
            debug.printException(debug.LEVEL_FINE)
            self.valid = False
            raise InvalidObjectError, "Cannot get state"
            

    def __get_relations(self):
        """Returns the Accessible RelationSet of this object as a list.

        NOTE: this will throw an InvalidObjectError exception if the
        AT-SPI Accessibility_Accessible can no longer be reached via
        CORBA.
        """

        try:
            relationSet = self._acc.getRelationSet()
            relations = []
            for relation in relationSet:
                relations.append(relation._narrow(
                    core.Accessibility.Relation))
            if CACHE_VALUES:
                self.relations = relations
            return relations
        except:
            debug.printException(debug.LEVEL_FINE)
            self.valid = False
            raise InvalidObjectError, "Cannot get relation set"
            

    def __get_app(self):
        """Returns the AT-SPI Accessibility_Application associated with this
        object.  Returns None if the application cannot be found (usually
        the indication of an AT-SPI bug).

        NOTE: this will throw an InvalidObjectError exception if the
        AT-SPI Accessibility_Accessible can no longer be reached via
        CORBA.
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
                              "ERROR: obj == obj.parent!")
                debug.println(debug.LEVEL_SEVERE,
                              "       name=(%s) role=(%s)" \
                              % (obj.name, obj.role))
                self.valid = False
                raise InvalidObjectError, "obj == obj.parent"
        else:
            debug.println(debug.LEVEL_FINEST,
                          "--> obj=(" + obj.name
                          + ") parent=(None)")

        if (obj == obj.parent) \
               or (obj.role != rolenames.ROLE_APPLICATION):
            return None
        else:
            if CACHE_VALUES:
                self.app = obj
            return obj

            
    def __get_extents(self, coordinateType = 0):
        """Returns the object's accessible extents as an
        Accessibility.BoundingBox object, or None if the object doesn't
        implement the Accessibility Component interface.

        NOTE: this will throw an InvalidObjectError exception if the
        AT-SPI Accessibility_Accessible can no longer be reached via
        CORBA.

        Arguments:
        - coordinateType: 0 = get the extents in screen coordinates,
                          1 = get the extents in window coordinates

        Returns:
        This object's accessible extents as an Accessibility.BoundingBox
        object, or None if the object doesn't implement the Accessibility
        Component interface.
        """

        try:
            component = self.component
            if component is None:
                return None
            else:
                # [[[TODO: WDW - caching the extents is dangerous because
                # the object may move, resulting in the current extents
                # becoming way out of date.  Perhaps need to cache just
                # the component interface and suffer the hit for getting
                # the extents if we cannot figure out how to determine if
                # the cached extents is out of date.]]]
                #
                extents = component.getExtents(coordinateType)
                #if CACHE_VALUES:
                #    self.extents = extents
                return extents
        except:
            debug.printException(debug.LEVEL_FINE)
            self.valid = False
            raise InvalidObjectError, "Cannot get component extents"
            

    def __get_label(self):
        """Returns an object's label as a string.  The label is determined
        using the following logic:

        1. If the object has a LABELLED_BY relation, return the text of
           the targets of this relation

        2. Else if the object has no LABELLED_BY relation, return the name
           
        3. Else if the object has no name, return the description

        4. Else return an empty string

        NOTE: this will throw an InvalidObjectError exception if the
        AT-SPI Accessibility_Accessible can no longer be reached via
        CORBA.
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

        # [[[TODO: WDW - HACK because push buttons can have labels as
        # their children.  But, they can also be labelled by something.
        # So...we'll make the label be a combination of the thing
        # labelling them (above) plus their name or the combination of
        # the names of their children if the children exist.]]]
        #
        if self.role == rolenames.ROLE_PUSH_BUTTON:
            if (self.name is not None) and (len(self.name) > 0):
                if len(label) > 0:
                    label += " " + self.name
                else:
                    label = self.name
            elif self.childCount > 0:
                i = 0
                while i < self.childCount:
                    child = self.child(i)
                    if child.role == rolenames.ROLE_LABEL:
                        if (child.name is not None) and (len(child.name) > 0):
                            if len(label) > 0:
                                label += " " + child.name
                            else:
                                label = child.name
                    i += 1
                    
        # If the object doesn't have a relation, but has a name, return
        # the name.
        #
        if (len(label) == 0) and (self.name is not None) \
               and (len(self.name) > 0):
            label = self.name

        # If the object has no name, but has a description, return that
        #
        elif (len(label) == 0) and (self.description is not None) \
                 and (len(self.description) > 0):
            # [[[TODO: HACK because yelp actually goes through the trouble
            # of setting the description of some of its text areas to
            # "no description".]]]
            #
            if self.description != "no description":
                label = self.description

        if CACHE_VALUES:
            self.label = label
        return label


    def __get_action(self):
        """Returns an object that implements the Accessibility_Action
        interface for this object, or None if this object doesn't implement
        the Accessibility_Action interface.

        NOTE: this will throw an InvalidObjectError exception if the
        AT-SPI Accessibility_Accessible can no longer be reached via
        CORBA.
        """

        try:
            bobj = self._acc._narrow(core.Accessibility.Accessible)
            action = bobj.queryInterface("IDL:Accessibility/Action:1.0")
            if action is not None:
                action = action._narrow(core.Accessibility.Action)
            if CACHE_VALUES:
                self.action = action
            return action
        except:
            debug.printException(debug.LEVEL_FINE)
            self.valid = False
            raise InvalidObjectError, "Cannot get action interface"
            

    def __get_component(self):
        """Returns an object that implements the Accessibility_Component
        interface for this object, or None if this object doesn't implement
        the Accessibility_Component interface.

        NOTE: this will throw an InvalidObjectError exception if the
        AT-SPI Accessibility_Accessible can no longer be reached via
        CORBA.
        """

        try:
            bobj = self._acc._narrow(core.Accessibility.Accessible)
            component = bobj.queryInterface("IDL:Accessibility/Component:1.0")
            if component is not None:
                component = component._narrow(core.Accessibility.Component)
            if CACHE_VALUES:
                self.component = component
            return component
        except:
            debug.printException(debug.LEVEL_FINE)
            self.valid = False
            raise InvalidObjectError, "Cannot get component interface"
            

    def __get_hypertext(self):
        """Returns an object that implements the Accessibility_Hypertext
        interface for this object, or None if this object doesn't implement
        the Accessibility_Hypertext interface.

        NOTE: this will throw an InvalidObjectError exception if the
        AT-SPI Accessibility_Accessible can no longer be reached via
        CORBA.
        """

        try:
            bobj = self._acc._narrow(core.Accessibility.Accessible)
            hypertext = bobj.queryInterface("IDL:Accessibility/Hypertext:1.0")
            if hypertext is not None:
                hypertext = hypertext._narrow(core.Accessibility.Hypertext)
            if CACHE_VALUES:
                self.hypertext = hypertext
            return hypertext
        except:
            debug.printException(debug.LEVEL_FINE)
            self.valid = False
            raise InvalidObjectError, "Cannot get hypertext interface"
            

    def __get_image(self):
        """Returns an object that implements the Accessibility_Image
        interface for this object, or None if this object doesn't implement
        the Accessibility_Image interface.

        NOTE: this will throw an InvalidObjectError exception if the
        AT-SPI Accessibility_Accessible can no longer be reached via
        CORBA.
        """

        try:
            bobj = self._acc._narrow(core.Accessibility.Accessible)
            image = bobj.queryInterface("IDL:Accessibility/Image:1.0")
            if image is not None:
                image = image._narrow(core.Accessibility.Image)
            if CACHE_VALUES:
                self.image = image
            return image
        except:
            debug.printException(debug.LEVEL_FINE)
            self.valid = False
            raise InvalidObjectError, "Cannot get image interface"
            

    def __get_selection(self):
        """Returns an object that implements the Accessibility_Selection
        interface for this object, or None if this object doesn't implement
        the Accessibility_Selection interface.

        NOTE: this will throw an InvalidObjectError exception if the
        AT-SPI Accessibility_Accessible can no longer be reached via
        CORBA.
        """

        try:
            bobj = self._acc._narrow(core.Accessibility.Accessible)
            selection = bobj.queryInterface("IDL:Accessibility/Selection:1.0")
            if selection is not None:
                selection = selection._narrow(core.Accessibility.Selection)
            if CACHE_VALUES:
                self.selection = selection
            return selection
        except:
            debug.printException(debug.LEVEL_FINE)
            self.valid = False
            raise InvalidObjectError, "Cannot get selection interface"
            

    def __get_table(self):
        """Returns an object that implements the Accessibility_Table
        interface for this object, or None if this object doesn't implement
        the Accessibility_Table interface.

        NOTE: this will throw an InvalidObjectError exception if the
        AT-SPI Accessibility_Accessible can no longer be reached via
        CORBA.
        """

        try:
            bobj = self._acc._narrow(core.Accessibility.Accessible)
            table = bobj.queryInterface("IDL:Accessibility/Table:1.0")
            if table is not None:
                table = table._narrow(core.Accessibility.Table)
            if CACHE_VALUES:
                self.table = table
            return table
        except:
            debug.printException(debug.LEVEL_FINE)
            self.valid = False
            raise InvalidObjectError, "Cannot get table interface"
            

    def __get_text(self):
        """Returns an object that implements the Accessibility_Text
        interface for this object, or None if this object doesn't implement
        the Accessibility_Text interface.

        NOTE: this will throw an InvalidObjectError exception if the
        AT-SPI Accessibility_Accessible can no longer be reached via
        CORBA.
        """

        try:
            bobj = self._acc._narrow(core.Accessibility.Accessible)
            text = bobj.queryInterface("IDL:Accessibility/Text:1.0")
            if text is not None:
                text = text._narrow(core.Accessibility.Text)
            if CACHE_VALUES:
                self.text = text
            return text
        except:
            debug.printException(debug.LEVEL_FINE)
            self.valid = False
            raise InvalidObjectError, "Cannot get text interface"
            

    def __get_value(self):
        """Returns an object that implements the Accessibility_Value
        interface for this object, or None if this object doesn't implement
        the Accessibility_Value interface.

        NOTE: this will throw an InvalidObjectError exception if the
        AT-SPI Accessibility_Accessible can no longer be reached via
        CORBA.
        """

        try:
            bobj = self._acc._narrow(core.Accessibility.Accessible)
            value = bobj.queryInterface("IDL:Accessibility/Value:1.0")
            if value is not None:
                value = value._narrow(core.Accessibility.Value)
            if CACHE_VALUES:
                self.value = value
            return value
        except:
            debug.printException(debug.LEVEL_FINE)
            self.valid = False
            raise InvalidObjectError, "Cannot get value interface"


    def __getattr__(self, attr):
        """Created virtual attributes for the Accessible object to make
        the syntax a bit nicer (e.g., acc.name rather than acc.name()).
        This method is also called if and only if the given attribute
        does not exist in the object.  Thus, we're effectively lazily
        building a cache to the remote object attributes here.

        NOTE: this will throw an InvalidObjectError exception if the
        AT-SPI Accessibility_Accessible can no longer be reached via
        CORBA.

        Arguments:
        - attr: a string indicating the attribute name to retrieve

        Returns the value of the given attribute.
        """
 
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
        elif attr == "image":
            return self.__get_image()
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

        NOTE: this will throw an InvalidObjectError exception if the
        AT-SPI Accessibility_Accessible can no longer be reached via
        CORBA.

        Arguments:
        - index: an integer specifying which child to obtain

        Returns the child at the given index.  [[[TODO: WDW - what to do
        when an index out of bounds occurs?]]]
        """

        # [[[TODO: WDW - the AT-SPI appears to give us a different accessible
        # when we repeatedly ask for the same child of a parent that manages
        # its descendants.  So...we probably shouldn't cache those kind of
        # children because we're likely to cause a memory leak.]]]
        #
        # Save away details we now know about this child
        #
        try:
            acc = self._acc.getChildAtIndex(index)
            if acc is None:
                return None
            newChild = makeAccessible(acc)
            newChild.index = index
            newChild.parent = self
            newChild.app = self.app
            return newChild
        except:
            debug.printException(debug.LEVEL_FINE)
            self.valid = False
            raise InvalidObjectError, "Cannot get child"


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
        if CACHE_VALUES:
            obj.name = e.any_data
        try:
            del obj.label
        except:
            pass

        
def onDescriptionChanged(e):
    """Core module event listener called when an object's description
    changes.  Updates the cache accordingly.

    Arguments:
    - e: AT-SPI event from the AT-SPI registry
    """

    if Accessible._cache.has_key(e.source):
        obj = Accessible._cache[e.source]
        if CACHE_VALUES:
            obj.description = e.any_data
        try:
            del obj.label
        except:
            pass


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
        obj = Accessible._cache[e.source]
        del obj
    return
    
    # This could fail if the e.source is now defunct.  [[[TODO: WDW - there
    # may be some really bad timing issues here.  Remember that the AT-SPI
    # events are added to a queue for processing later.  So...we could
    # potentially be processing queued events for an object that has been
    # pronounced defunct in a later event.]]]
    #
    try:
        obj = makeAccessible(e.source)
    except:
        return
    
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
            del obj
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


def isValid(acc):
    """If we've made an Accessible for an object, return True if it has
    been flagged as valid.  Otherwise, return False.

    Arguments:
    - acc: an AT-SPI (not Python) Accessible
    """
    
    if Accessible._cache.has_key(acc):
        obj = Accessible._cache[acc]
        return obj.valid
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

    NOTE: this will throw an InvalidObjectError exception if the
    AT-SPI Accessibility_Accessible can no longer be reached via
    CORBA.

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

    NOTE: this will throw an InvalidObjectError exception if the
    AT-SPI Accessibility_Accessible can no longer be reached via
    CORBA.

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

    NOTE: this will throw an InvalidObjectError exception if the
    AT-SPI Accessibility_Accessible can no longer be reached via
    CORBA.

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


def findUnrelatedLabels(root):
    """Returns a list containing all the unrelated (i.e., have no
    relations to anything and are not a fundamental element of a
    more atomic component like a combo box) labels under the given
    root.  Note that the labels must also be showing on the display.

    Arguments:
    - root the Accessible object to traverse
    
    Returns a list of unrelated labels under the given root.
    """

    # Find all the labels in the dialog
    #
    allLabels = findByRole(root, rolenames.ROLE_LABEL)
    
    # add the names of only those labels which are not associated with
    # other objects (i.e., empty relation sets).  [[[TODO: WDW - HACK:
    # In addition, do not grab free labels whose parents are push
    # buttons because push buttons can have labels as
    # children.]]][[[TODO: WDW - HACK: panels with labelled borders will
    # have a child label that does not have its relation set.  So...we
    # check to see if the panel's name is the same as the label's name.
    # If so, we ignore the label.]]]
    #
    unrelatedLabels = []
    
    for label in allLabels:
        set = label.relations
        if len(set) == 0:
            parent = label.parent
            if parent and (parent.role == rolenames.ROLE_PUSH_BUTTON):
                pass
            elif parent and (parent.role == rolenames.ROLE_PANEL) \
               and (parent.name == label.name):
                pass
            elif label.state.count(core.Accessibility.STATE_SHOWING):
                unrelatedLabels.append(label)

    # Now sort the labels based on their geographic position, top to
    # bottom, left to right.  This is a very inefficient sort, but the
    # assumption here is that there will not be a lot of labels to
    # worry about.
    #
    sortedLabels = []
    for label in unrelatedLabels:
        index = 0
        for sortedLabel in sortedLabels:
            if (label.extents.y > sortedLabel.extents.y) \
               or ((label.extents.y == sortedLabel.extents.y) \
                   and (label.extents.x > sortedLabel.extents.x)):
                index += 1
            else:
                break
        sortedLabels.insert(index, label)
        
    #return unrelatedLabels
    return sortedLabels

def getFrame(obj):
    """Returns the frame containing this object, or None if this object
    is not inside a frame.

    NOTE: this will throw an InvalidObjectError exception if the
    AT-SPI Accessibility_Accessible can no longer be reached via
    CORBA.

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


def getTextLineAtCaret(obj):
    """Gets the line of text where the caret is.

    NOTE: this will throw an InvalidObjectError exception if the
    AT-SPI Accessibility_Accessible can no longer be reached via
    CORBA.

    Argument:
    - obj: an Accessible object that implements the AccessibleText
           interface

    Returns the line of text where the caret is.
    """

    # Get the the AccessibleText interrface
    #
    try:
        text = obj.text
        if text is None:
            return ["", 0, 0]
    except:
        obj.valid = False
        raise InvalidObjectError, "Cannot get text interface"
        
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


def getNodeLevel(obj):
    """Determines the node level of this object if it is in a tree
    relation, with 0 being the top level node.  If this object is
    not in a tree relation, then -1 will be returned.

    NOTE: this will throw an InvalidObjectError exception if the
    AT-SPI Accessibility_Accessible can no longer be reached via
    CORBA.

    Arguments:
    -obj: the Accessible object
    """

    if obj is None:
        return -1
    
    level = -1
    node = obj
    done = False
    while not done:
        relations = node.relations
        node = None
        for relation in relations:
            if relation.getRelationType() \
                   == core.Accessibility.RELATION_NODE_CHILD_OF:
                level += 1
                node = makeAccessible(relation.getTarget(0))
                break
        done = node is None

    return level

    
def getAcceleratorAndShortcut(obj):
    """Gets the accelerator string (and possibly shortcut) for the given
    object.

    NOTE: this will throw an InvalidObjectError exception if the
    AT-SPI Accessibility_Accessible can no longer be reached via
    CORBA.

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
