# Orca
#
# Copyright 2004 Sun Microsystems Inc.
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

import os
import sys

# Import the Orca core module

import core

# Definition of the Accessible class
#
# This class wraps at-spi accessible objects -- it caches properties
# such as name, description, and parent.  It adds some properties to
# the at-spi accessible including the application to which the object
# belongs.

class Accessible:

    # A cache of the currently active accessible objects

    cache = {}

    # Create an Accessible

    def __init__ (self, acc):
        try:
            existing = Accessible.cache[acc]
            return
        except:
            pass

        # The acc reference might be an Accessible or an Application,
        # so try both

        try:
            self.acc = acc._narrow (core.Accessibility.Accessible)
        except:
            self.acc = acc._narrow (core.Accessibility.Application)
        self.acc.ref ()
        Accessible.cache[acc] = self

    # Desructor -- unref the accessible

    def __del__ (self):
        self.acc.unref ()

    # Because we're doing all our own attribute handling, we have to
    # provide some defaults

    # Retrieve the object's name

    def __get_name (self):
        self.name = self.acc.name
        return self.name

    # Retrieve an object's description

    def __get_description (self):
        self.description = self.acc.description
        return self.description

    # Retrieve an object's parent

    def __get_parent (self):

        # Get the CORBA object parent of this CORBA Object
        # accessible

        obj = self.acc.parent

        # If this object has no parent, return None

        if obj is None:
            self.parent = None
            return self.parent

        # Do we already have a cached object created for this
        # CORBa object?

        try:
            self.parent = Accessible.cache[obj]
        except:
            self.parent = Accessible (obj)
        return self.parent

    # Get this Accessible's child count

    def __get_child_count (self):
        self.childCount = self.acc.childCount
        return self.childCount

    # Get this Accessible's index in its parent

    def __get_index (self):
        self.index = self.acc.getIndexInParent ()
        return self.index

    # Get this Accessible's role

    def __get_role (self):
        self.role = self.acc.getRoleName ()
        return self.role

    # Get this object's state

    def __get_state (self):

        # Get the state set

        set = self.acc.getState ()
        set = set._narrow (core.Accessibility.StateSet)
        

        # Store the list of states in the Accessible

        self.state = set.getStates ()
        return self.state


    def __get_relations (self):

        # Get the state set

        self.relations = self.acc.getRelationSet ()

        return self.relations


    # Get the application containing this Accessible

    def __get_app (self):

        # Traverse up the tree until we find the app

        obj = self
        while obj.parent != None and obj != obj.parent:
            obj = obj.parent
        if obj == obj.parent:
            self.app = None
        else:
            self.app = obj
        return self.app

    # This function creates virtual attributes for the Accessible
    # object -- this makes syntax a bit nicer (I.E. acc.name rather
    # than cc.name().

    def __getattr__ (self, attr):
        if attr == "name":
            return self.__get_name ()
        elif attr == "description":
            return self.__get_description ()
        elif attr == "parent":
            return self.__get_parent ()
        elif attr == "childCount":
            return self.__get_child_count ()
        elif attr == "index":
            return self.__get_index ()
        elif attr == "role":
            return self.__get_role ()
        elif attr == "state":
            return self.__get_state ()
        elif attr == "relations":
            return self.__get_relations ()
        elif attr == "app":
            return self.__get_app ()

        # If we can't find the attribute, defer to the base object

        return super (object, self).__getattr__ (name)
    
    # Retrieve the specified child of this Accessible

    def child (self, index):
        acc = self.acc.getChildAtIndex (index)

        try:
            newChild = Accessible.cache[acc]
        except:
            newChild = Accessible (acc)

        # Set the index since we know it

        newChild.index = index

        # We also know the parent

        newChild.parent = self

        # If we know the app of this object, then we also know the
        # app of the child

        try:
            newChild.app = self.app
        except:
            pass
        return newChild
    
# Make an Accessible -- this is used instead of a simple calle to
# Accessible () because the object may already be in the cache, and
# constructors can't fail.  this seemed like the best way to
# encapsulate this functionality within this a11y module.

def makeAccessible (acc):
    try:
        obj = Accessible.cache[acc]
    except:
        obj = Accessible (acc)
    return obj

# This event handler gets called when an object gets focus

focussedObject = None
focussedApp = None

def onWindowActivated (e):
    global focussedApp

    focussedApp = makeAccessible (e.source.parent)

def onFocus (e):
    global focussedObject
    global focussedApp

    focussedObject = makeAccessible (e.source)

    # WE need this hack fo the time being due to a bug in Nautilus,
    # which makes it impossible to traverse to the application from
    # some objects withint Nautilus

# This function is called when an object's name changes

def onNameChanged (e):
    try:
        obj = Accessible.cache[e.source]
        obj.name = e.any_data
    except:
        pass

# This function is called when an object's description changes

def onDescriptionChanged (e):
    try:
        obj = Accessible.cache[e.source]
        obj.description = e.any_data
    except:
        pass

# This function is called when an object's parent changes

def onParentChanged (e):
    try:
        obj = Accessible.cache[e.source]
        del obj.parent
        del obj.app
    except:
        pass

# This function invalidates the state information cached in the Accessible when its state changes

def onStateChanged (e):
    try:
        obj = Accessible.cache[e.source]
        del obj.state
    except:
        pass

def onChildrenChanged (e):
    try:
        obj = Accessible.cache[e.source]
        del obj.childCount
    except:
        pass

# This event listener is called when an object becomes defunct -- it
# removes the object from the cache

def onDefunct (e):
    try:
        del Accessible.cache[e.source]
    except:
        pass


# Initialize the a11y utility module

initialized = False

def init ():
    global initialized
    if initialized:
        return True

    # Initialize the core

    core.init ()

    # Register our focus tracker and window activation tracker to keep
    # track of the currently focussed object and application

    core.registerEventListener (onWindowActivated, "window:activate")
    core.registerEventListener (onFocus, "focus:")

    # Register the event listeners that keep our cache up to date

    # Delete objects from the cache when they're defunct

    core.registerEventListener (onDefunct, "object:state-changed:defunct")

    # Invalidate any cached name if an object's name changes

    core.registerEventListener (onNameChanged, "object:property-change:accessible-name")

    # Invalidate any cached description if an object's description
    # changes

    core.registerEventListener (onDescriptionChanged, "object:property-change:accessible-description")

    # Invalidate any cached parent if an object's parent changes

    core.registerEventListener (onParentChanged, "object:property-change:accessible-parent")

    # Delete cached state information if an object's state changes

    core.registerEventListener (onStateChanged, "object:state-changed:")

    # Delete cached childCount when children change

    core.registerEventListener (onChildrenChanged, "object:children-changed:")

    initialized = True
    return True


def shutdown ():
    global initialized

    if not initialized:
            return False

    # Shutdown the core

    core.shutdown ()

    initialized = False
    return True

# This hash table maps at-spi event names to Python function names
# which are to be used in scripts.  For example, it maps "focus:"
# events to call a script function called onFocus and
# "window:activate" to onWindowActivated

dispatcher = {}

dispatcher["onWindowActivated"] = "window:activate"
dispatcher["onWindowDestroyed"] = "window:destroy"
dispatcher["onFocus"] = "focus:"
dispatcher["onStateChanged"] = "object:state-changed:"
dispatcher["onSelectionChanged"] = "object:selection-changed"
dispatcher["onCaretMoved"] = "object:text-caret-moved"
dispatcher["onTextInserted"] = "object:text-changed:insert"
dispatcher["onTextDeleted"] = "object:text-changed:delete"
dispatcher["onLinkSelected"] = "object:link-selected"
dispatcher["onNameChanged"] = "object:property-change:accessible-name"


# Get a list of all objects within the specified object
# Objects are returned in no particular drder - this function does a
# simple tree traversal, ignoring the children of objects which report
# the MANAGES_DESCENDANTS state is active


def getObjects (root):
    # Keep track of the objects we've found

    objvisitted = {}

    # The list of object we'll return

    objlist = []

    # Start at the first child of the given object

    if root.childCount <= 0:
        return objlist
    tmp = root.child (0)
    while tmp != root:

        # Traverse to the bottom of the tre

        while tmp.childCount > 0:

            # If tmp is None, we hit the bottom of the tree

            if tmp is None:
                break
            tmp = tmp.child (0)

            # Avoid traversing into objects which manage their
            # descendants (tables, etc)

            state = tmp.state
            if state.count (core.Accessibility.STATE_MANAGES_DESCENDANTS):
                break

        # Move up the tree until the current object has siblings

        i = tmp.index
        while tmp != root and i >= tmp.parent.childCount-1:
            try:
                t = objvisitted[tmp]
            except:
                objlist.append (tmp)
                objvisitted[tmp] = True
            tmp = tmp.parent
            i = tmp.index

        # If we're at the top, we're done

        if tmp == root:
            break
        try:
            t = objvisitted[tmp]
        except:
            objlist.append (tmp)
            objvisitted[tmp] = True

        # Move to the next sibling

        tmp = tmp.parent.child (i+1)
    return objlist

# Get all objects of a specific role - This is very inefficient - this
# should do it's own traversal and not add objects to the list that
# aren't of the specified role.  Instead it uses the traversal from
# getObjects and then deletes objects from the list that aren't of the
# specified role


def findByRole (root, role):
    objlist = []

    # Get all the children of the specified object

    allobjs = getObjects (root)

    # Create a new list containing only the objects of the specified role
    
    for o in allobjs:
        if o.role == role:
            objlist.append (o)
    return objlist

# Find all objects within the specified object with the specified name
# the same comment about inefficiency applies here as well


def findByName (root, name):
    objlist = []

    list = getObjects (root)

    # Create a new list containing only those objects with the
    # specified name

    for o in list:
        if o.name == name:
            objlist.append (o)
    return objlist

# Get an object's label - This function gets an object's label.  This
# function returns the label based on the following logic:
#
# If the object has a RLABELED_BY relation, the function returns the
# text of the targets of this relation
#
# If the object has no LABLELED_BY relation, this function returns its
# name
#
# If the object has no name, return the description




def getLabel (obj):

    label = ""

    # Does the object have a relation set?

    relations = obj.relations
    for relation in relations:
        if relation.getRelationType () == core.Accessibility.RELATION_LABELLED_BY:
            target = relation.getTarget (0)
            label = target.name
            break

    # If the object doesn't have a relation, but has a name, return
    # that

    if len (label) == 0 and obj.name is not None and len (obj.name) > 0:
            label = obj.name

    # If the object has no name, but has a description, return that

    elif len (label) == 0 and obj.description is not None and len (obj.description) > 0:
            label = obj.description
    return label



# Find object's group - This is busted for now.  It currently just
# returns the object's parent


def getGroup (obj):
    return obj.parent

# Convenience wrapper functions for QueryInterface

def getAccessible (obj):
    acc = obj.queryInterface ("IDL:Accessibility/Accessible:1.0")
    if acc is not None:
        acc = acc._narrow (core.Accessibility.Accessible)
    return acc

def getAction (obj):
    bobj = obj.acc._narrow (core.Accessibility.Accessible)
    action = bobj.queryInterface ("IDL:Accessibility/Action:1.0")
    if action is not None:
        action = action._narrow (core.Accessibility.Action)
    return action

def getComponent (obj):
    bobj = obj.acc._narrow (core.Accessibility.Accessible)
    component = bobj.queryInterface ("IDL:Accessibility/Component:1.0")
    if component is not None:
        component = component._narrow (core.Accessibility.Component)
    return component

def getHypertext (obj):
    bobj = obj.acc._narrow (core.Accessibility.Accessible)
    hypertext = bobj.queryInterface ("IDL:Accessibility/Hypertext:1.0")
    if hypertext is not None:
        hypertext = hypertext._narrow (core.Accessibility.Hypertext)
    return hypertext

def getSelection (obj):
    bobj = obj.acc._narrow (core.Accessibility.Accessible)
    sel = bobj.queryInterface ("IDL:Accessibility/Selection:1.0")
    if sel is not None:
        sel = sel._narrow (core.Accessibility.Selection)
    return sel

def getTable (obj):
    bobj = obj.acc._narrow (core.Accessibility.Accessible)
    table = bobj.queryInterface ("IDL:Accessibility/Table:1.0")
    if table is not None:
        table = table._narrow (core.Accessibility.Table)
    return table

def getText (obj):
    bobj = obj.acc._narrow (core.Accessibility.Accessible)
    text = bobj.queryInterface ("IDL:Accessibility/Text:1.0")
    if text is not None:
        text = text._narrow (core.Accessibility.Text)
    return text

def getValue (obj):
    bobj = obj.acc._narrow (core.Accessibility.Accessible)
    value = bobj.queryInterface ("IDL:Accessibility/Value:1.0")
    if value is not None:
        value = value._narrow (core.Accessibility.Value)
    return value

