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

# Track currently focussed object

focussedObject = None

def onFocus (event):
    global focussedObject

    focussedObject = event.source

# Track currently active toplevel window

activeWindow = None

def onActivate (event):
    global activeWindow

    activeWindow = event.source

# Initialize the a11y utility module

initialized = False

def init ():
    global initialized
    global focusEventListener
    global activateEventListener

    if initialized:
        return True

    # Track the currently focussed object

    core.registerEventListener (onFocus, "focus:")

    # Track the currently active toplevel window

    core.registerEventListener (onActivate, "window:activate")

    initialized = True
    return True


def shutdown ():
    global initialized

    if not initialized:
            return False

    # Deregister our focus tracker

    core.unregisterEventListener (onFocus, "focus:")
    
    # Deregister our window activation tracker

    core.unregisterEventListener (onActivate, "window:activate")

    initialized = False
    return True

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

    tmp = root.getChildAtIndex (0)
    while tmp != root:

        # Traverse to the bottom of the tre

        while tmp.childCount > 0:

            # If tmp is None, we hit the bottom of the tree

            if tmp is None:
                break
            tmp = tmp.getChildAtIndex (0)

            # Avoid traversing into objects which manage their
            # descendants (tables, etc)

            state = tmp.getState ()
            state = state._narrow (core.Accessibility.StateSet)
            if state.contains (core.Accessibility.STATE_MANAGES_DESCENDANTS):
                break

        # Move up the tree until the current object has siblings

        i = tmp.getIndexInParent ()
        while tmp != root and i >= tmp.parent.childCount-1:
            try:
                t = objvisitted[tmp]
            except:
                objlist.append (tmp)
                objvisitted[tmp] = True
            tmp = tmp.parent
            i = tmp.getIndexInParent ()

        # If we're at the top, we're done

        if tmp == root:
            break
        try:
            t = objvisitted[tmp]
        except:
            objlist.append (tmp)
            objvisitted[tmp] = True

        # Move to the next sibling

        tmp = tmp.parent.getChildAtIndex (i+1)
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
        if o.getRoleName () == role:
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

    relations = obj.getRelationSet ()
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
    bobj = obj.objref._narrow (core.Accessibility.Accessible)
    action = bobj.queryInterface ("IDL:Accessibility/Action:1.0")
    if action is not None:
        action = action._narrow (core.Accessibility.Action)
    return action

def getComponent (obj):
    bobj = obj.objref._narrow (Accessibility.Accessible)
    component = bobj.queryInterface ("IDL:Accessibility/Component:1.0")
    if component is not None:
        component = component._narrow (core.Accessibility.Component)
    return component

def getHypertext (obj):
    bobj = obj.objref._narrow (core.Accessibility.Accessible)
    hypertext = bobj.queryInterface ("IDL:Accessibility/Hypertext:1.0")
    if hypertext is not None:
        hypertext = hypertext._narrow (core.Accessibility.Hypertext)
    return hypertext

def getSelection (obj):
    bobj = obj.objref._narrow (core.Accessibility.Accessible)
    sel = bobj.queryInterface ("IDL:Accessibility/Selection:1.0")
    if sel is not None:
        sel = sel._narrow (core.Accessibility.Selection)
    return sel

def getTable (obj):
    bobj = obj.objref._narrow (core.Accessibility.Accessible)
    table = bobj.queryInterface ("IDL:Accessibility/Table:1.0")
    if table is not None:
        table = table._narrow (core.Accessibility.Table)
    return table

def getText (obj):
    bobj = obj.objref._narrow (core.Accessibility.Accessible)
    text = bobj.queryInterface ("IDL:Accessibility/Text:1.0")
    if text is not None:
        text = text._narrow (core.Accessibility.Text)
    return text

def getValue (obj):
    bobj = obj.objref._narrow (core.Accessibility.Accessible)
    value = bobj.queryInterface ("IDL:Accessibility/Value:1.0")
    if value is not None:
        value = value._narrow (core.Accessibility.Value)
    return value

