# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
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
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

"""Implements structural navigation.  Right now this is only
being implemented by Gecko; however it can be used in any
script providing access to document content."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import braille
import debug
import input_event
import keybindings
import orca
import orca_state
import settings
import speech

from orca_i18n import _
from orca_i18n import ngettext

#############################################################################
#                                                                           #
# MatchCriteria                                                             #
#                                                                           #
#############################################################################

class MatchCriteria:
    """Contains the criteria which will be used to generate a collection
    matchRule.  We don't want to create the rule until we need it and
    are ready to use it. In addition, the creation of an AT-SPI match
    rule requires you specify quite a few things (see the __init__),
    most of which are irrelevant to the search at hand.  This class
    makes it possible for the StructuralNavigationObject creator to just
    specify the few criteria that actually matter.
    """

    def __init__(self,
                 collection,
                 states = [],
                 matchStates = None,
                 objAttrs = [],
                 matchObjAttrs = None,
                 roles = [],
                 matchRoles = None,
                 interfaces = "",
                 matchInterfaces = None,
                 invert = False,
                 applyPredicate = False):

        """Creates a new match criteria object.

        Arguments:
        - collection: the collection interface for the document in
          which the accessible objects can be found.
        - states: a list of pyatspi states of interest
        - matchStates: whether an object must have all of the states
          in the states list, any of the states in the list, or none
          of the states in the list.  Must be one of the collection
          interface MatchTypes if provided.
        - objAttrs: a list of object attributes (not text attributes)
        - matchObjAttrs: whether an object must have all of the
          attributes in the objAttrs list, any of the attributes in
          the list, or none of the attributes in the list.  Must be
          one of the collection interface MatchTypes if provided.
        - interfaces: (We aren't using this.  According to the at-spi
          idl, it is a string.)
        - matchInterfaces: The collection MatchType for matching by
          interface.
        - invert: If true the match rule will find objects that don't
          match. We always use False.
        - applyPredicate: whether or not a predicate should be applied
          as an additional check to see if an item is indeed a match.
          This is necessary, for instance, when one of the things we
          care about is a text attribute, something the collection
          interface doesn't include in its criteria.
        """

        self.collection = collection
        self.matchStates = matchStates or collection.MATCH_ANY
        self.objAttrs = objAttrs
        self.matchObjAttrs = matchObjAttrs or collection.MATCH_ANY
        self.roles = roles
        self.matchRoles = matchRoles or collection.MATCH_ANY
        self.interfaces = interfaces
        self.matchInterfaces = matchInterfaces or collection.MATCH_ALL
        self.invert = invert
        self.applyPredicate = applyPredicate

        self.states = pyatspi.StateSet()
        for state in states:
            self.states.add(state)

###########################################################################
#                                                                         #
# StructuralNavigationObject                                              #
#                                                                         #
###########################################################################

class StructuralNavigationObject:
    """Represents a document object which has identifiable characteristics
    which can be used for the purpose of navigation to and among instances
    of that object. These characteristics may be something as simple as a
    role and/or a state of interest. Or they may be something more complex
    such as character counts, text attributes, and other object attributes.
    """

    def __init__(self, structuralNavigation, objType, bindings, predicate,
                 criteria, presentation):

        """Creates a new structural navigation object.

        Arguments:
        - structuralNavigation: the StructuralNavigation class associated
          with this object.
        - objType: the type (e.g. BLOCKQUOTE) associated with this object.
        - bindings: a dictionary of all of the possible bindings for this
          object.  In the case of all but the "atLevel" bindings, each
          binding takes the form of [keysymstring, modifiers, description].
          The goPreviousAtLevel and goNextAtLevel bindings are each a list
          of bindings in that form.
        - predicate: the predicate to use to determine if a given accessible
          matches this structural navigation object. Used when a search via
          collection is not possible or practical.
        - criteria: a method which returns a MatchCriteria object which
          can in turn be used to locate the next/previous matching accessible
          via collection.
        - presentation: the method which should be called after performing
          the search for the structural navigation object.
        """

        self.structuralNavigation = structuralNavigation
        self.objType = objType
        self.bindings = bindings
        self.predicate = predicate
        self.criteria = criteria
        self.present = presentation

        self.inputEventHandlers = {}
        self.keyBindings = keybindings.KeyBindings()
        self.functions = []
        self._setUpHandlersAndBindings()

    def _setUpHandlersAndBindings(self):
        """Adds the inputEventHandlers and keyBindings for this object."""

        # Set up the basic handlers.  These are our traditional goPrevious
        # and goNext functions.
        #
        previous = self.bindings.get("previous")
        if previous:
            [keysymstring, modifiers, description] = previous
            handlerName = "%sGoPrevious" % self.objType
            self.inputEventHandlers[handlerName] = \
                input_event.InputEventHandler(self.goPrevious, description)

            self.keyBindings.add(
                keybindings.KeyBinding(
                    keysymstring,
                    settings.defaultModifierMask,
                    modifiers,
                    self.inputEventHandlers[handlerName]))

            self.functions.append(self.goPrevious)

        next = self.bindings.get("next")
        if next:
            [keysymstring, modifiers, description] = next
            handlerName = "%sGoNext" % self.objType
            self.inputEventHandlers[handlerName] = \
                input_event.InputEventHandler(self.goNext, description)

            self.keyBindings.add(
                keybindings.KeyBinding(
                    keysymstring,
                    settings.defaultModifierMask,
                    modifiers,
                    self.inputEventHandlers[handlerName]))

            self.functions.append(self.goNext)

        # Set up the "at level" handlers (e.g. to navigate among headings
        # at the specified level).
        #
        previousAtLevel = self.bindings.get("previousAtLevel") or []
        for i, binding in enumerate(previousAtLevel):
            level = i + 1
            handler = self.goPreviousAtLevelFactory(level)
            handlerName = "%sGoPreviousLevel%dHandler" % (self.objType, level)
            keysymstring, modifiers, description = binding

            self.inputEventHandlers[handlerName] = \
                input_event.InputEventHandler(handler, description)

            self.keyBindings.add(
                keybindings.KeyBinding(
                    keysymstring,
                    settings.defaultModifierMask,
                    modifiers,
                    self.inputEventHandlers[handlerName]))

            self.functions.append(handler)

        nextAtLevel = self.bindings.get("nextAtLevel") or []
        for i, binding in enumerate(nextAtLevel):
            level = i + 1
            handler = self.goNextAtLevelFactory(level)
            handlerName = "%sGoNextLevel%dHandler" % (self.objType, level)
            keysymstring, modifiers, description = binding

            self.inputEventHandlers[handlerName] = \
                input_event.InputEventHandler(handler, description)

            self.keyBindings.add(
                keybindings.KeyBinding(
                    keysymstring,
                    settings.defaultModifierMask,
                    modifiers,
                    self.inputEventHandlers[handlerName]))

            self.functions.append(handler)

        # Set up the "directional" handlers (e.g. for table cells. Live
        # region support has a handler to go to the last live region,
        # so we'll handle that here as well).
        #
        directions = {}
        directions["Left"]  = self.bindings.get("left")
        directions["Right"] = self.bindings.get("right")
        directions["Up"]    = self.bindings.get("up")
        directions["Down"]  = self.bindings.get("down")
        directions["First"] = self.bindings.get("first")
        directions["Last"]  = self.bindings.get("last")

        for direction in directions:
            binding = directions.get(direction)
            if not binding:
                continue

            handler = self.goDirectionFactory(direction)
            handlerName = "%sGo%s" % (self.objType, direction)
            keysymstring, modifiers, description = binding

            self.inputEventHandlers[handlerName] = \
                input_event.InputEventHandler(handler, description)

            self.keyBindings.add(
                keybindings.KeyBinding(
                    keysymstring,
                    settings.defaultModifierMask,
                    modifiers,
                    self.inputEventHandlers[handlerName]))

            self.functions.append(handler)

    def addHandlerAndBinding(self, binding, handlerName, function):
        """Adds a custom inputEventHandler and keybinding to the object's
        handlers and bindings.  Right now this is unused, but here in
        case a creator of a StructuralNavigationObject had some other
        desired functionality in mind.

        Arguments:
        - binding: [keysymstring, modifiers, description]
        - handlerName: a string uniquely identifying the handler
        - function: the function associated with the binding
        """

        [keysymstring, modifiers, description] = binding
        handler = input_event.InputEventHandler(function, description)
        keyBinding = keybindings.KeyBinding(
                         keysymstring,
                         settings.defaultModifierMask,
                         modifiers,
                         handler)

        self.inputEventHandlers[handlerName] = handler
        self.structuralNavigation.inputEventHandlers[handlerName] = handler

        self.functions.append(function)
        self.structuralNavigation.functions.append(function)

        self.keyBindings.add(keyBinding)
        self.structuralNavigation.keyBindings.add(keyBinding)

    def goPrevious(self, script, inputEvent):
        """Go to the previous object."""
        self.structuralNavigation.goObject(self, False)

    def goNext(self, script, inputEvent):
        """Go to the next object."""
        self.structuralNavigation.goObject(self, True)

    def goPreviousAtLevelFactory(self, level):
        """Generates a goPrevious method for the specified level. Right
        now, this is just for headings, but it may have applicability
        for other objects such as list items (i.e. for level-based
        navigation in an outline or other multi-tiered list.

        Arguments:
        - level: the desired level of the object as an int.
        """

        def goPreviousAtLevel(script, inputEvent):
            self.structuralNavigation.goObject(self, False, arg=level)
        return goPreviousAtLevel

    def goNextAtLevelFactory(self, level):
        """Generates a goNext method for the specified level. Right
        now, this is just for headings, but it may have applicability
        for other objects such as list items (i.e. for level-based
        navigation in an outline or other multi-tiered list.

        Arguments:
        - level: the desired level of the object as an int.

        """

        def goNextAtLevel(script, inputEvent):
            self.structuralNavigation.goObject(self, True, arg=level)
        return goNextAtLevel

    def goDirectionFactory(self, direction):
        """Generates the methods for navigation in a particular direction
        (i.e. left, right, up, down, first, last).  Right now, this is
        primarily for table cells, but it may have applicability for other
        objects.  For example, when navigating in an outline, one might
        want the ability to navigate to the next item at a given level,
        but then work his/her way up/down in the hierarchy.

        Arguments:
        - direction: the direction in which to navigate as a string.
        """

        def goCell(script, inputEvent):
            thisCell = self.structuralNavigation.getCellForObj(\
                self.structuralNavigation.getCurrentObject())
            currentCoordinates = \
                self.structuralNavigation.getCellCoordinates(thisCell)
            if direction == "Left":
                desiredCoordinates = [currentCoordinates[0],
                                      currentCoordinates[1] - 1]
            elif direction == "Right":
                desiredCoordinates = [currentCoordinates[0],
                                      currentCoordinates[1] + 1]
            elif direction == "Up":
                desiredCoordinates = [currentCoordinates[0] - 1,
                                      currentCoordinates[1]]
            elif direction == "Down":
                desiredCoordinates = [currentCoordinates[0] + 1,
                                      currentCoordinates[1]]
            elif direction == "First":
                desiredCoordinates = [0, 0]
            else:
                desiredCoordinates = [-1, -1]
                table = self.structuralNavigation.getTableForCell(thisCell)
                if table:
                    iTable = table.queryTable()
                    lastRow = iTable.nRows - 1
                    lastCol = iTable.nColumns - 1
                    desiredCoordinates = [lastRow, lastCol]
            self.structuralNavigation.goCell(self,
                                             thisCell,
                                             currentCoordinates,
                                             desiredCoordinates)

        def goLastLiveRegion(script, inputEvent):
            """Go to the last liveRegion."""
            if settings.inferLiveRegions:
                script.liveMngr.goLastLiveRegion()
            else:
                # Translators: this announces to the user that live region
                # support has been turned off.
                #
                speech.speak(_("Live region support is off"))

        if self.objType == StructuralNavigation.TABLE_CELL:
            return goCell
        elif self.objType == StructuralNavigation.LIVE_REGION \
             and direction == "Last":
            return goLastLiveRegion

#############################################################################
#                                                                           #
# StructuralNavigation                                                      #
#                                                                           #
#############################################################################

class StructuralNavigation:
    """This class implements the structural navigation functionality which
    is available to scripts. Scripts interested in implementing structural
    navigation need to override getEnabledStructuralNavigationTypes() and
    return a list of StructuralNavigation object types which should be
    enabled.
    """

    # The available object types.
    #
    # Convenience methods have been put into place whereby one can
    # create an object (FOO = "foo"), and then provide the following
    # methods: _fooBindings(), _fooPredicate(), _fooCriteria(), and
    # _fooPresentation(). With these in place, and with the object
    # FOO included among the object types returned by the script's
    # getEnabledStructuralNavigationTypes(), the StructuralNavigation
    # object should be created and set up automagically. At least that
    # is the idea. :-) This hopefully will also enable easy re-definition
    # of existing StructuralNavigationObjects on a script-by-script basis.
    # For instance, in the soffice script, overriding _blockquotePredicate
    # should be all that is needed to implement navigation by blockquote
    # in OOo Writer documents.
    #
    ANCHOR          = "anchor"
    BLOCKQUOTE      = "blockquote"
    BUTTON          = "button"
    CHECK_BOX       = "checkBox"
    CHUNK           = "chunk"
    COMBO_BOX       = "comboBox"
    ENTRY           = "entry"
    FORM_FIELD      = "formField"
    HEADING         = "heading"
    LANDMARK        = "landmark"
    LIST            = "list"        # Bulleted/numbered lists
    LIST_ITEM       = "listItem"    # Bulleted/numbered list items
    LIVE_REGION     = "liveRegion"
    PARAGRAPH       = "paragraph"
    RADIO_BUTTON    = "radioButton"
    TABLE           = "table"
    TABLE_CELL      = "tableCell"
    UNVISITED_LINK  = "unvisitedLink"
    VISITED_LINK    = "visitedLink"

    # Whether or not to attempt to use collection.  There's no point
    # in bothering if we know that the collection interface has not
    # been implemented in a given app (e.g. StarOffice/OOo) so this
    # variable can be overridden.
    #
    collectionEnabled = settings.useCollection

    # Roles which are recognized as being a form field. Note that this
    # is for the purpose of match rules and predicates and refers to
    # AT-SPI roles. 
    #
    FORM_ROLES = [pyatspi.ROLE_CHECK_BOX,
                  pyatspi.ROLE_RADIO_BUTTON,
                  pyatspi.ROLE_COMBO_BOX,
                  pyatspi.ROLE_LIST,
                  pyatspi.ROLE_ENTRY,
                  pyatspi.ROLE_PASSWORD_TEXT,
                  pyatspi.ROLE_PUSH_BUTTON,
                  pyatspi.ROLE_SPIN_BUTTON,
                  pyatspi.ROLE_TEXT]

    # Roles which are recognized as being potential "large objects"
    # or "chunks." Note that this refers to AT-SPI roles.
    #
    OBJECT_ROLES = [pyatspi.ROLE_HEADING,
                    pyatspi.ROLE_LIST,
                    pyatspi.ROLE_PARAGRAPH,
                    pyatspi.ROLE_TABLE,
                    pyatspi.ROLE_TABLE_CELL,
                    pyatspi.ROLE_TEXT,
                    pyatspi.ROLE_SECTION,
                    pyatspi.ROLE_DOCUMENT_FRAME]

    def __init__(self, script, enabledTypes, enabled=False):
        """Creates an instance of the StructuralNavigation class.

        Arguments:
        - script: the script which which this instance is associated.
        - enabledTypes: a list of StructuralNavigation object types
          which the script is interested in supporting.
        - enabled: Whether structural navigation should start out
          enabled.  For instance, in Gecko by default we do what it
          enabled; in soffice, we would want to start out with it
          disabled and have the user enable it via a keystroke when
          desired.
        """

        self._script = script
        self.enabled = enabled

        # Create all of the StructuralNavigationObject's in which the
        # script is interested, using the convenience method
        #
        self.enabledObjects = {}
        for objType in enabledTypes:
            self.enabledObjects[objType] = \
                self.structuralNavigationObjectCreator(objType)

        self.functions = []
        self.inputEventHandlers = {}
        self.setupInputEventHandlers()
        self.keyBindings = self.getKeyBindings()

        # When navigating in a non-uniform table, one can move to a
        # cell which spans multiple rows and/or columns.  When moving
        # beyond that cell, into a cell that does NOT span multiple
        # rows/columns, we want to be sure we land in the right place.
        # Therefore, we'll store the coordinates from "our perspective."
        #
        self.lastTableCell = [-1, -1]

    def structuralNavigationObjectCreator(self, name):
        """This convenience method creates a StructuralNavigationObject
        with the specified name and associated characterists. (See the
        "Objects" section of code near the end of this class. Creators
        of StructuralNavigationObject's can still do things the old
        fashioned way should they so choose, by creating the instance
        and then adding it via addObject().

        Arguments:
        - name: the name/objType associated with this object.
        """

        # We're going to assume bindings.  After all, a structural
        # navigation object is by defintion an object which one can
        # navigate to using the associated keybindings. For similar
        # reasons we'll also assume a predicate and a presentation
        # method.  (See the Objects section towards the end of this
        # class for examples of each.)
        #
        bindings = eval("self._%sBindings()" % name)
        predicate = eval("self._%sPredicate" % name)
        presentation = eval("self._%sPresentation" % name)

        # We won't make this assumption for match criteria because
        # the collection interface might not be implemented (e.g.
        # StarOffice/OpenOffice) and/or its use might not be possible
        # or practical for a given StructuralNavigationObject (e.g.
        # matching by text attributes, spatial navigation within tables).
        #
        try:
            criteria = eval("self._%sCriteria" % name)
        except:
            criteria = None

        return StructuralNavigationObject(self, name, bindings, predicate,
                                          criteria, presentation)

    def addObject(self, objType, structuralNavigationObject):
        """Adds structuralNavigationObject to the dictionary of enabled
        objects.

        Arguments:
        - objType: the name/object type of the StructuralNavigationObject.
        - structuralNavigationObject: the StructuralNavigationObject to
          add.
        """

        self.enabledObjects[objType] = structuralNavigationObject

    def setupInputEventHandlers(self):
        """Defines InputEventHandler fields for a script."""

        if not len(self.enabledObjects):
            return

        self.inputEventHandlers["toggleStructuralNavigationHandler"] = \
            input_event.InputEventHandler(
                self.toggleStructuralNavigation,
                # Translators: the structural navigation keys are designed
                # to move the caret around the document content by object
                # type. Thus H moves you to the next heading, Shift H to
                # the previous heading, T to the next table, and so on.
                # This feature needs to be toggle-able so that it does not
                # interfere with normal writing functions.
                #
                _("Toggles structural navigation keys."))

        for structuralNavigationObject in self.enabledObjects.values():
            self.inputEventHandlers.update(\
                structuralNavigationObject.inputEventHandlers)
            self.functions.extend(structuralNavigationObject.functions)

    def getKeyBindings(self):
        """Defines the structural navigation key bindings for a script.

        Returns: an instance of keybindings.KeyBindings.
        """

        keyBindings = keybindings.KeyBindings()

        if not len(self.enabledObjects):
            return keyBindings

        keyBindings.add(
            keybindings.KeyBinding(
                "z",
                settings.defaultModifierMask,
                settings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["toggleStructuralNavigationHandler"]))

        for structuralNavigationObject in self.enabledObjects.values():
            bindings = structuralNavigationObject.keyBindings.keyBindings
            for keybinding in bindings:
                keyBindings.add(keybinding)

        return keyBindings

    #########################################################################
    #                                                                       #
    # Input Event Handler Methods                                           #
    #                                                                       #
    #########################################################################

    def toggleStructuralNavigation(self, script, inputEvent):
        """Toggles structural navigation keys."""

        self.enabled = not self.enabled

        if self.enabled:
            # Translators: the structural navigation keys are designed
            # to move the caret around document content by object type.
            # Thus H moves you to the next heading, Shift H to the
            # previous heading, T to the next table, and so on. Some
            # users prefer to turn this off to use Firefox's search
            # when typing feature.  This message is sent to both the
            # braille display and the speech synthesizer when the user
            # toggles the structural navigation feature of Orca.
            # It should be a brief informative message.
            #
            string = _("Structural navigation keys on.")
        else:
            # Translators: the structural navigation keys are designed
            # to move the caret around document content by object type.
            # Thus H moves you to the next heading, Shift H to the
            # previous heading, T to the next table, and so on. Some
            # users prefer to turn this off to use Firefox's search
            # when typing feature.  This message is sent to both the
            # braille display and the speech synthesizer when the user
            # toggles the structural navigation feature of Orca.
            # It should be a brief informative message.
            #
            string = _("Structural navigation keys off.")

        debug.println(debug.LEVEL_CONFIGURATION, string)
        speech.speak(string)
        braille.displayMessage(string)

    #########################################################################
    #                                                                       #
    # Methods for Moving to Objects                                         #
    #                                                                       #
    #########################################################################

    def goCell(self, structuralNavigationObject, thisCell, 
               currentCoordinates, desiredCoordinates):
        """The method used for navigation among cells in a table.

        Arguments:
        - structuralNavigationObject: the StructuralNavigationObject which
          represents the table cell.
        - thisCell: the pyatspi accessible TABLE_CELL we're currently in
        - currentCoordinates: the [row, column] of thisCell.  Note, we
          cannot just get the coordinates because in table cells which
          span multiple rows and/or columns, the value returned by 
          table.getRowAtIndex() is the first row the cell spans. Likewise,
          the value returned by table.getColumnAtIndex() is the left-most
          column.  Therefore, we keep track of the row and column from
          our perspective to ensure we stay in the correct row and column.
        - desiredCoordinates: the [row, column] where we think we'd like to
          be.
        """

        table = self.getTableForCell(thisCell)
        try:
            iTable = table.queryTable()
        except:
            # Translators: this is for navigating document content by
            # moving from table cell to table cell. If the user gives a
            # table navigation command but is not in a table, Orca speaks
            # this message.
            #
            speech.speak(_("Not in a table."))
            return None

        currentRow, currentCol = currentCoordinates
        desiredRow, desiredCol = desiredCoordinates
        rowDiff = desiredRow - currentRow
        colDiff = desiredCol - currentCol
        oldRowHeaders = self._getRowHeaders(thisCell)
        oldColHeaders = self._getColumnHeaders(thisCell)
        cell = thisCell
        while cell:
            cell = iTable.getAccessibleAt(desiredRow, desiredCol)
            if not cell:
                if desiredCol < 0:
                    # Translators: this is for navigating document
                    # content by moving from table cell to table cell.
                    # This is the message spoken when the user attempts
                    # to move to the left of the current cell and is
                    # already in the first column.
                    #
                    speech.speak(_("Beginning of row."))
                    desiredCol = 0
                elif desiredCol > iTable.nColumns - 1:
                    # Translators: this is for navigating document
                    # content by moving from table cell to table cell.
                    # This is the message spoken when the user attempts
                    # to move to the right of the current cell and is
                    # already in the last column.
                    #
                    speech.speak(_("End of row."))
                    desiredCol = iTable.nColumns - 1
                if desiredRow < 0:
                    # Translators: this is for navigating document
                    # content by moving from table cell to table cell.
                    # This is the message spoken when the user attempts
                    # to move to the cell above the current cell and is
                    # already in the first row.
                    #
                    speech.speak(_("Top of column."))
                    desiredRow = 0
                elif desiredRow > iTable.nRows - 1:
                    # Translators: this is for navigating document
                    # content by moving from table cell to table cell.
                    # This is the message spoken when the user attempts
                    # to move to the cell below the current cell and is
                    # already in the last row.
                    #
                    speech.speak(_("Bottom of column."))
                    desiredRow = iTable.nRows - 1
            elif self._script.isSameObject(thisCell, cell) \
                 or settings.skipBlankCells and self._isBlankCell(cell):
                if colDiff < 0:
                    desiredCol -= 1
                elif colDiff > 0:
                    desiredCol += 1
                if rowDiff < 0:
                    desiredRow -= 1
                elif rowDiff > 0:
                    desiredRow += 1
            else:
                break

        self.lastTableCell = [desiredRow, desiredCol]
        if cell:
            arg = [rowDiff, colDiff, oldRowHeaders, oldColHeaders]
            structuralNavigationObject.present(cell, arg)

    def goObject(self, structuralNavigationObject, next, obj=None, arg=None):
        """The method used for navigation among StructuralNavigationObjects
        which are not table cells.

        Arguments:
        - structuralNavigationObject: the StructuralNavigationObject which
          represents the object of interest.
        - next: If True, we're interested in the next accessible object
          which matches structuralNavigationObject.  If False, we're 
          interested in the previous accessible object which matches.
        - obj: the current object (typically the locusOfFocus).
        - arg: optional arguments which may need to be passed along to
          the predicate, presentation method, etc. For instance, in the
          case of navigating amongst headings at a given level, the level
          is needed and passed in as arg.
        """

        obj = obj or self.getCurrentObject()

        # Yelp is seemingly fond of killing children for sport. Better
        # check for that.
        #
        try:
            state = obj.getState()
        except:
            return [None, False]
        else:
            if state.contains(pyatspi.STATE_DEFUNCT):
                #print "goObject: defunct object", obj
                debug.printException(debug.LEVEL_SEVERE)
                return [None, False]

        success = False
        wrap = settings.wrappedStructuralNavigation
        # Try to find it using Collection first.  But don't do this with form
        # fields for now.  It's a bit faster moving to the next form field,
        # but not on pages with huge forms (e.g. bugzilla's advanced search
        # page).  And due to bug #538680, we definitely don't want to use
        # collection to go to the previous chunk or form field.
        #
        formObjects = [self.BUTTON, self.CHECK_BOX, self.COMBO_BOX,
                       self.ENTRY, self.FORM_FIELD, self.RADIO_BUTTON]

        criteria = None
        objType = structuralNavigationObject.objType
        if self.collectionEnabled \
           and not objType in formObjects \
           and (next or objType != self.CHUNK):
            try:
                document = self._getDocument()
                collection = document.queryCollection()
                if structuralNavigationObject.criteria:
                    criteria = structuralNavigationObject.criteria(collection,
                                                                   arg)
            except:
                debug.printException(debug.LEVEL_SEVERE)
            else:
                # If the document frame itself contains content and that is
                # our current object, querying the collection interface will
                # result in our starting at the top when looking for the next
                # object rather than the current caret offset. See bug 567984.
                #
                if next and self._script.isSameObject(obj, document):
                    criteria = None

        if criteria:
            try:
                rule = collection.createMatchRule(criteria.states.raw(),
                                                  criteria.matchStates,
                                                  criteria.objAttrs,
                                                  criteria.matchObjAttrs,
                                                  criteria.roles,
                                                  criteria.matchRoles,
                                                  criteria.interfaces,
                                                  criteria.matchInterfaces,
                                                  criteria.invert)
                if criteria.applyPredicate:
                    predicate = structuralNavigationObject.predicate
                else:
                    predicate = None

                if not next:
                    [obj, wrapped] = self._findPrevByMatchRule(collection,
                                                               rule,
                                                               wrap,
                                                               obj,
                                                               predicate)
                else:
                    [obj, wrapped] = self._findNextByMatchRule(collection,
                                                               rule,
                                                               wrap,
                                                               obj,
                                                               predicate)
                success = True
                collection.freeMatchRule(rule)
                # print "collection", structuralNavigationObject.objType
            except NotImplementedError:
                debug.printException(debug.LEVEL_SEVERE)
            except:
                debug.printException(debug.LEVEL_SEVERE)
                collection.freeMatchRule(rule)

        # Do it iteratively when Collection failed or is disabled
        #
        if not success:
            pred = structuralNavigationObject.predicate
            if not next:
                [obj, wrapped] = self._findPrevByPredicate(pred, wrap,
                                                           obj, arg)
            else:
                [obj, wrapped] = self._findNextByPredicate(pred, wrap,
                                                           obj, arg)
            # print "predicate", structuralNavigationObject.objType
        if wrapped:
            if not next:
                # Translators: when the user is attempting to locate a
                # particular object and the top of the web page has been
                # reached without that object being found, we "wrap" to
                # the bottom of the page and continuing looking upwards.
                # We need to inform the user when this is taking place.
                #
                speech.speak(_("Wrapping to bottom."))
            else:
                # Translators: when the user is attempting to locate a
                # particular object and the bottom of the web page has been
                # reached without that object being found, we "wrap" to the
                # top of the page and continuing looking downwards. We need
                # to inform the user when this is taking place.
                #
                speech.speak(_("Wrapping to top."))

        structuralNavigationObject.present(obj, arg)

    #########################################################################
    #                                                                       #
    # Utility Methods for Finding Objects                                   #
    #                                                                       #
    #########################################################################

    def getCurrentObject(self):
        """Returns the current object.  Normally, the locusOfFocus. But
        in the case of Gecko, that doesn't always work.
        """

        return orca_state.locusOfFocus

    def _findPrevByMatchRule(self, collection, matchRule, wrap, currentObj,
                             predicate=None):
        """Finds the previous object using the given match rule as a
        pattern to match or not match.

        Arguments:
        -collection: the accessible collection interface
        -matchRule: the collections match rule to use
        -wrap: if True and the bottom of the document is reached, move
         to the top and keep looking.
        -currentObj: the object from which the search should begin
        -predicate: an optional predicate to further test if the item
         found via collection is indeed a match.

        Returns: [obj, wrapped] where wrapped is a boolean reflecting
        whether wrapping took place.
        """

        currentObj = currentObj or self.getCurrentObject()
        document = self._getDocument()

        # If the current object is the document itself, find an actual
        # object to use as the starting point. Otherwise we're in
        # danger of skipping over the objects in between our present
        # location and top of the document.
        #
        if self._script.isSameObject(currentObj, document):
            currentObj = self._findNextObject(currentObj, document)

        ancestors = []
        obj = currentObj.parent
        if obj.getRole() in [pyatspi.ROLE_LIST, pyatspi.ROLE_TABLE]:
            ancestors.append(obj)
        else:
            while obj:
                ancestors.append(obj)
                obj = obj.parent

        match, wrapped = None, False
        results = collection.getMatchesTo(currentObj,
                                          matchRule,
                                          collection.SORT_ORDER_CANONICAL,
                                          collection.TREE_INORDER,
                                          True,
                                          1,
                                          True)
        while not match:
            if len(results) == 0:
                if wrapped or not wrap:
                    break
                elif wrap:
                    lastObj = self._findLastObject(document)
                    # Collection does not do an inclusive search, meaning
                    # that the start object is not part of the search.  So
                    # we need to test the lastobj separately using the given
                    # matchRule.  We don't have this problem for 'Next' because
                    # the startobj is the doc frame.
                    #
                    secondLastObj = self._findPreviousObject(lastObj, document)
                    results = collection.getMatchesFrom(\
                        secondLastObj,
                        matchRule,
                        collection.SORT_ORDER_CANONICAL,
                        collection.TREE_INORDER,
                        1, 
                        True)
                    wrapped = True
                    if len(results) > 0 \
                       and (not predicate or predicate(results[0])):
                        match = results[0]
                    else:
                        results = collection.getMatchesTo(\
                            lastObj,
                            matchRule,
                            collection.SORT_ORDER_CANONICAL,
                            collection.TREE_INORDER, 
                            True,
                            1,
                            True)
            elif len(results) > 0:
                if results[0] in ancestors \
                   or predicate and not predicate(results[0]):
                    results = collection.getMatchesTo(\
                        results[0],
                        matchRule,
                        collection.SORT_ORDER_CANONICAL,
                        collection.TREE_INORDER,
                        True,
                        1,
                        True)
                else:
                    match = results[0]

        return [match, wrapped]

    def _findNextByMatchRule(self, collection, matchRule, wrap, currentObj,
                             predicate=None):
        """Finds the next object using the given match rule as a pattern
        to match or not match.

        Arguments:
        -collection:  the accessible collection interface
        -matchRule: the collections match rule to use
        -wrap: if True and the bottom of the document is reached, move
         to the top and keep looking.
        -currentObj: the object from which the search should begin
        -predicate: an optional predicate to further test if the item
         found via collection is indeed a match.

        Returns: [obj, wrapped] where wrapped is a boolean reflecting
        whether wrapping took place.
        """

        currentObj = currentObj or self.getCurrentObject()
        ancestors = []
        [currentObj, offset] = self._script.getCaretContext()
        obj = currentObj.parent
        while obj:
            ancestors.append(obj)
            obj = obj.parent

        match, wrapped = None, False
        while not match:
            results = collection.getMatchesFrom(\
                currentObj,
                matchRule,
                collection.SORT_ORDER_CANONICAL,
                collection.TREE_INORDER,
                1,
                True)
            if len(results) > 0 and not results[0] in ancestors:
                currentObj = results[0]
                if not predicate or predicate(currentObj):
                    match = currentObj
            elif wrap and not wrapped:
                wrapped = True
                ancestors = [currentObj]
                currentObj = self._getDocument()
            else:
                break

        return [match, wrapped]

    def _findPrevByPredicate(self, pred, wrap, currentObj=None, arg=None):
        """Finds the caret offset at the beginning of the previous object
        using the given predicate as a pattern to match.

        Arguments:
        -pred: a python callable that takes an accessible argument and
               returns true/false based on some match criteria
        -wrap: if True and the top of the document is reached, move
               to the bottom and keep looking.
        -currentObj: the object from which the search should begin
        -arg:  an additional value to be passed to the predicate

        Returns: [obj, wrapped] where wrapped is a boolean reflecting
        whether wrapping took place.
        """

        currentObj = currentObj or self.getCurrentObject()
        document = self._getDocument()

        # If the current object is the document itself, find an actual
        # object to use as the starting point. Otherwise we're in
        # danger of skipping over the objects in between our present
        # location and top of the document.
        #
        if self._script.isSameObject(currentObj, document):
            currentObj = self._findNextObject(currentObj, document)

        ancestors = []
        nestableRoles = [pyatspi.ROLE_LIST, pyatspi.ROLE_TABLE]
        obj = currentObj.parent
        while obj:
            ancestors.append(obj)
            obj = obj.parent

        obj = self._findPreviousObject(currentObj, document)
        wrapped = obj is None
        match = None

        if wrapped:
            obj = self._findLastObject(document)

        while obj and not match:
            isNested = (obj != currentObj.parent \
                        and currentObj.parent.getRole() == obj.getRole() \
                        and obj.getRole() in nestableRoles)
            if (not obj in ancestors or isNested) and pred(obj):
                if wrapped and self._script.isSameObject(currentObj, obj):
                    break
                else:
                    match = obj
            else:
                obj = self._findPreviousObject(obj, document)
                if not obj and wrap and not wrapped:
                    obj = self._findLastObject(document)
                    wrapped = True

        return [match, wrapped]

    def _findNextByPredicate(self, pred, wrap, currentObj=None, arg=None):
        """Finds the caret offset at the beginning of the next object
        using the given predicate as a pattern to match or not match.

        Arguments:
        -pred: a python callable that takes an accessible argument and
               returns true/false based on some match criteria
        -wrap: if True and the bottom of the document is reached, move
               to the top and keep looking.
        -currentObj: the object from which the search should begin
        -arg:  an additional value to be passed to the predicate

        Returns: [obj, wrapped] where wrapped is a boolean reflecting
        whether wrapping took place.
        """
        currentObj = currentObj or self.getCurrentObject()
        ancestors = []
        obj = currentObj.parent
        while obj:
            ancestors.append(obj)
            obj = obj.parent

        document = self._getDocument()
        obj = self._findNextObject(currentObj, document)
        wrapped = obj is None
        match = None

        if wrapped:
            [obj, offset] = self._getCaretPosition(document)

        while obj and not match:
            if (not obj in ancestors) and pred(obj, arg):
                if wrapped and self._script.isSameObject(currentObj, obj):
                    break
                else:
                    match = obj
            else:
                obj = self._findNextObject(obj, document)
                if not obj and wrap and not wrapped:
                    [obj, offset] = self._getCaretPosition(document)
                    wrapped = True

        return [match, wrapped]

    def _findPreviousObject(self, obj, stopAncestor):
        """Finds the object prior to this one, where the tree we're
        dealing with is a DOM and 'prior' means the previous object
        in a linear presentation sense.

        Arguments:
        -obj: the object where to start.
        -stopAncestor: the ancestor at which the search should stop
        """

        # NOTE: This method is based on some intial experimentation
        # with OOo structural navigation.  It might need refining
        # or fixing and is being overridden by the Gecko method
        # regardless, so this one can be modified as appropriate.
        #
        prevObj = None

        index = obj.getIndexInParent() - 1
        if index >= 0:
            prevObj = obj.parent[index]
            if prevObj.childCount:
                prevObj = prevObj[prevObj.childCount - 1]
        elif not self._script.isSameObject(obj.parent, stopAncestor):
            prevObj = obj.parent

        return prevObj

    def _findNextObject(self, obj, stopAncestor):
        """Finds the object after to this one, where the tree we're
        dealing with is a DOM and 'next' means the next object
        in a linear presentation sense.

        Arguments:
        -obj: the object where to start.
        -stopAncestor: the ancestor at which the search should stop
        """

        # NOTE: This method is based on some intial experimentation
        # with OOo structural navigation.  It might need refining
        # or fixing and is being overridden by the Gecko method
        # regardless, so this one can be modified as appropriate.
        #
        nextObj = None

        if obj and obj.childCount:
            nextObj = obj[0]

        while obj and obj.parent != obj and not nextObj:
            index = obj.getIndexInParent() + 1
            if 0 < index < obj.parent.childCount:
                nextObj = obj.parent[index]
            elif not self._script.isSameObject(obj.parent, stopAncestor):
                obj = obj.parent
            else:
                break

        return nextObj

    def _findLastObject(self, ancestor):
        """Returns the last object in ancestor.

        Arguments:
        - ancestor: the accessible object whose last (child) object
          is sought.
        """

        # NOTE: This method is based on some intial experimentation
        # with OOo structural navigation.  It might need refining
        # or fixing and is being overridden by the Gecko method
        # regardless, so this one can be modified as appropriate.
        #
        if not ancestor or not ancestor.childCount:
            return ancestor

        lastChild = ancestor[ancestor.childCount - 1]
        while lastChild:
            lastObj = self._findNextObject(lastChild, ancestor)
            if lastObj:
                lastChild = lastObj
            else:
                break

        return lastChild

    def _getDocument(self):
        """Returns the document or other object in which the object of
        interest is contained.
        """

        # This is script-specific and will need to be defined in the
        # script's custom StructuralNavigation class. But if this
        # method does nothing, pylint complains.  So... We might as
        # well take a guess for a generic version to make pylint
        # happy. :-) In some initial experimentation with OOo, this
        # method seemed to reliably return the child of the document
        # view, so it might not be too far off.  It's also being
        # overridden by Gecko, so one should feel free to modify this
        # one.
        #
        obj = self.getCurrentObject()
        lastTextObj = obj
        while obj and obj.getRole() != pyatspi.ROLE_FRAME:
            try:
                obj.queryText()
            except:
                pass
            else:
                lastTextObj = obj
            obj = obj.parent

        return lastTextObj

    def _isInDocument(self, obj):
        """Returns True if the accessible object obj is inside of
        the document.

        Arguments:
        -obj: the accessible object of interest.
        """

        document = self._getDocument()
        while obj and obj.parent:
            if self._script.isSameObject(obj.parent, document):
                return True
            else:
                obj = obj.parent

        return False

    def _isUselessObject(self, obj):
        """Returns True if the accessible object obj is an object
        that doesn't have any meaning associated with it. Individual
        scripts should override this method as needed.  Gecko does.

        Arguments:
        - obj: the accessible object of interest.
        """

        return False

    #########################################################################
    #                                                                       #
    # Methods for Presenting Objects                                        #
    #                                                                       #
    #########################################################################

    def _getTableCaption(self, obj):
        """Returns a string which contains the table caption, or
        None if a caption could not be found.

        Arguments:
        - obj: the accessible table whose caption we want.
        """

        caption = obj.queryTable().caption
        try:
            caption.queryText()
        except:
            return None
        else:
            return self._script.getDisplayedText(caption)

    def _getTableDescription(self, obj):
        """Returns a string which describes the table."""

        nonUniformString = ""
        nonUniform = self._isNonUniformTable(obj)
        if nonUniform:
            # Translators: a uniform table is one in which each table
            # cell occupies one row and one column (i.e. a perfect grid)
            # In contrast, a non-uniform table is one in which at least
            # one table cell occupies more than one row and/or column.
            #
            nonUniformString = _("Non-uniform") + " "

        table = obj.queryTable()
        nRows = table.nRows
        nColumns = table.nColumns
        # Translators: this represents the number of rows in a table.
        #
        rowString = ngettext("Table with %d row",
                             "Table with %d rows",
                             nRows) % nRows
        # Translators: this represents the number of cols in a table.
        #
        colString = ngettext("%d column",
                             "%d columns",
                             nColumns) % nColumns

        return (nonUniformString + rowString + " " + colString)

    def _isNonUniformTable(self, obj):
        """Returns True if the obj is a non-uniform table (i.e. a table
        where at least one cell spans multiple rows and/or columns).

        Arguments:
        - obj: the table to examine
        """

        try:
            table = obj.queryTable()
        except:
            pass
        else:
            for i in xrange(obj.childCount):
                [isCell, row, col, rowExtents, colExtents, isSelected] = \
                                       table.getRowColumnExtentsAtIndex(i)
                if (rowExtents > 1) or (colExtents > 1):
                    return True

        return False

    def getCellForObj(self, obj):
        """Looks for a table cell in the ancestry of obj, if obj is not a
        table cell.

        Arguments:
        - obj: the accessible object of interest.
        """

        if obj and obj.getRole() != pyatspi.ROLE_TABLE_CELL:
            document = self._getDocument()
            obj = self._script.getAncestor(obj,
                                           [pyatspi.ROLE_TABLE_CELL],
                                           [document.getRole()])
        return obj

    def getTableForCell(self, obj):
        """Looks for a table in the ancestry of obj, if obj is not a table.

        Arguments:
        - obj: the accessible object of interest.
        """

        if obj and obj.getRole() != pyatspi.ROLE_TABLE:
            document = self._getDocument()
            obj = self._script.getAncestor(obj,
                                           [pyatspi.ROLE_TABLE],
                                           [document.getRole()])
        return obj

    def _isBlankCell(self, obj):
        """Returns True if the table cell is empty or consists of whitespace.

        Arguments:
        - obj: the accessible table cell to examime
        """

        text = self._script.getDisplayedText(obj)
        if text and len(text.strip()) and text != obj.name:
            return False
        else:
            for child in obj:
                text = self._script.getDisplayedText(child)
                if text and len(text.strip()) \
                   or child.getRole() == pyatspi.ROLE_LINK:
                    return False

        return True

    def _getCellText(self, obj):
        """Looks at the table cell and tries to get its text.

        Arguments:
        - obj: the accessible table cell to examime
        """

        text = ""
        if obj and not obj.childCount:
            text = self._script.getDisplayedText(obj)
        else:
            for child in obj:
                childText = self._script.getDisplayedText(child)
                text = self._script.appendString(text, childText)

        return text

    def _presentCellHeaders(self, cell, oldCellInfo):
        """Speaks the headers of the accessible table cell, cell.

        Arguments:
        - cell: the accessible table cell whose headers we wish to
          present.
        - oldCellInfo: [rowDiff, colDiff, oldRowHeaders, oldColHeaders]
        """

        if not cell or not oldCellInfo:
            return

        rowDiff, colDiff, oldRowHeaders, oldColHeaders = oldCellInfo
        if not (oldRowHeaders or oldColHeaders):
            return

        # We only want to speak the header information that has
        # changed, and we don't want to speak headers if we're in
        # a header row/col.
        #
        if rowDiff and not self._isInHeaderRow(cell):
            rowHeaders = self._getRowHeaders(cell)
            for header in rowHeaders:
                if not header in oldRowHeaders:
                    text = self._getCellText(header)
                    speech.speak(text)

        if colDiff and not self._isInHeaderColumn(cell):
            colHeaders = self._getColumnHeaders(cell)
            for header in colHeaders:
                if not header in oldColHeaders:
                    text = self._getCellText(header)
                    speech.speak(text)

    def _getCellSpanInfo(self, obj):
        """Returns a string reflecting the number of rows and/or columns
        spanned by a table cell when multiple rows and/or columns are
        spanned.

        Arguments:
        - obj: the accessible table cell whose cell span we want.
        """

        if not obj or (obj.getRole() != pyatspi.ROLE_TABLE_CELL):
            return

        [row, col] = self.getCellCoordinates(obj)
        table = obj.parent.queryTable()
        rowspan = table.getRowExtentAt(row, col)
        colspan = table.getColumnExtentAt(row, col)
        spanString = ""
        if (colspan > 1) and (rowspan > 1):
            # Translators: The cell here refers to a cell within a table
            # within a document.  We need to announce when the cell occupies
            # or "spans" more than a single row and/or column.
            #
            spanString = _("Cell spans %(rows)d rows and %(columns)d columns") \
                         % {"rows" : rowspan,
                            "columns" : colspan}
        elif (colspan > 1):
            # Translators: The cell here refers to a cell within a table
            # within a document.  We need to announce when the cell occupies
            # or "spans" more than a single row and/or column.
            #
            spanString = _("Cell spans %d columns") % colspan
        elif (rowspan > 1):
            # Translators: The cell here refers to a cell within a table
            # within a document.  We need to announce when the cell occupies
            # or "spans" more than a single row and/or column.
            #
            spanString = _("Cell spans %d rows") % rowspan

        return spanString

    def getCellCoordinates(self, obj):
        """Returns the [row, col] of a ROLE_TABLE_CELL or [-1, -1]
        if the coordinates cannot be found.

        Arguments:
        - obj: the accessible table cell whose coordinates we want.
        """

        obj = self.getCellForObj(obj)
        parent = self.getTableForCell(obj)
        try:
            table = parent.queryTable()
        except:
            pass
        else:
            # If we're in a cell that spans multiple rows and/or columns,
            # thisRow and thisCol will refer to the upper left cell in
            # the spanned range(s).  We're storing the lastTableCell that
            # we're aware of in order to facilitate more linear movement.
            # Therefore, if the lastTableCell and this table cell are the
            # same cell, we'll go with the stored coordinates.
            #
            lastRow, lastCol = self.lastTableCell
            lastKnownCell = table.getAccessibleAt(lastRow, lastCol)
            if self._script.isSameObject(lastKnownCell, obj):
                return [lastRow, lastCol]
            else:
                index = self._script.getCellIndex(obj)
                thisRow = table.getRowAtIndex(index)
                thisCol = table.getColumnAtIndex(index)
                return [thisRow, thisCol]

        return [-1, -1]

    def _getRowHeaders(self, obj):
        """Returns a list of table cells that serve as a row header for
        the specified TABLE_CELL.

        Arguments:
        - obj: the accessible table cell whose header(s) we want.
        """

        rowHeaders = []
        if not obj:
            return rowHeaders

        try:
            table = obj.parent.queryTable()
        except:
            pass
        else:
            [row, col] = self.getCellCoordinates(obj)
            # Theoretically, we should be able to quickly get the text
            # of a {row, column}Header via get{Row,Column}Description().
            # Gecko doesn't expose the information that way, however.
            # get{Row,Column}Header seems to work sometimes.
            #
            header = table.getRowHeader(row)
            if header:
                rowHeaders.append(header)

            # Headers that are strictly marked up with <th> do not seem
            # to be exposed through get{Row, Column}Header.
            #
            else:
                # If our cell spans multiple rows, we want to get all of
                # the headers that apply.
                #
                rowspan = table.getRowExtentAt(row, col)
                for r in range(row, row+rowspan):
                    # We could have multiple headers for a given row, one
                    # header per column.  Presumably all of the headers are
                    # prior to our present location.
                    #
                    for c in range(0, col):
                        cell = table.getAccessibleAt(r, c)
                        if self._isHeader(cell) and not cell in rowHeaders:
                            rowHeaders.append(cell)

        return rowHeaders

    def _getColumnHeaders(self, obj):
        """Returns a list of table cells that serve as a column header for
        the specified TABLE_CELL.

        Arguments:
        - obj: the accessible table cell whose header(s) we want.
        """

        columnHeaders = []
        if not obj:
            return columnHeaders

        try:
            table = obj.parent.queryTable()
        except:
            pass
        else:
            [row, col] = self.getCellCoordinates(obj)
            # Theoretically, we should be able to quickly get the text
            # of a {row, column}Header via get{Row,Column}Description().
            # Gecko doesn't expose the information that way, however.
            # get{Row,Column}Header seems to work sometimes.
            #
            header = table.getColumnHeader(col)
            if header:
                columnHeaders.append(header)

            # Headers that are strictly marked up with <th> do not seem
            # to be exposed through get{Row, Column}Header.
            #
            else:
                # If our cell spans multiple columns, we want to get all of
                # the headers that apply.
                #
                colspan = table.getColumnExtentAt(row, col)
                for c in range(col, col+colspan):
                    # We could have multiple headers for a given column, one
                    # header per row.  Presumably all of the headers are
                    # prior to our present location.
                    #
                    for r in range(0, row):
                        cell = table.getAccessibleAt(r, c)
                        if self._isHeader(cell) and not cell in columnHeaders:
                            columnHeaders.append(cell)

        return columnHeaders

    def _isInHeaderRow(self, obj):
        """Returns True if all of the cells in the same row as this cell are
        headers.

        Arguments:
        - obj: the accessible table cell whose row is to be examined.
        """

        if obj and obj.getRole() == pyatspi.ROLE_TABLE_CELL:
            table = obj.parent.queryTable()
            index = self._script.getCellIndex(obj)
            row = table.getRowAtIndex(index)
            for col in xrange(table.nColumns):
                cell = table.getAccessibleAt(row, col)
                if not self._isHeader(cell):
                    return False

        return True

    def _isInHeaderColumn(self, obj):
        """Returns True if all of the cells in the same column as this cell
        are headers.

        Arguments:
        - obj: the accessible table cell whose column is to be examined.
        """

        if obj and obj.getRole() == pyatspi.ROLE_TABLE_CELL:
            table = obj.parent.queryTable()
            index = self._script.getCellIndex(obj)
            col = table.getColumnAtIndex(index)
            for row in xrange(table.nRows):
                cell = table.getAccessibleAt(row, col)
                if not self._isHeader(cell):
                    return False

        return True

    def _isHeader(self, obj):
        """Returns True if the table cell is a header.

        Arguments:
        - obj: the accessible table cell to examine.
        """

        if not obj:
            return False

        elif obj.getRole() in [pyatspi.ROLE_TABLE_COLUMN_HEADER,
                               pyatspi.ROLE_TABLE_ROW_HEADER]:
            return True

        else:
            attributes = obj.getAttributes()
            if attributes:
                for attribute in attributes:
                    if attribute == "tag:TH":
                        return True

    def _getHeadingLevel(self, obj):
        """Determines the heading level of the given object.  A value
        of 0 means there is no heading level.

        Arguments:
        - obj: the accessible whose heading level we want.
        """

        level = 0

        if obj is None:
            return level

        if obj.getRole() == pyatspi.ROLE_HEADING:
            attributes = obj.getAttributes()
            if attributes is None:
                return level
            for attribute in attributes:
                if attribute.startswith("level:"):
                    level = int(attribute.split(":")[1])
                    break

        return level

    def _getCaretPosition(self, obj):
        """Returns the [obj, characterOffset] where the caret should be
        positioned. For most scripts, the object should not change and
        the offset should be 0.  That's not always the case with Gecko.

        Arguments:
        - obj: the accessible object in which the caret should be
          positioned.
        """

        return [obj, 0]

    def _setCaretPosition(self, obj, characterOffset):
        """Sets the caret at the specified offset within obj.

        Arguments:
        - obj: the accessible object in which the caret should be
          positioned.
        - characterOffset: the offset at which to position the caret.
        """

        try:
            text = obj.queryText()
            text.setCaretOffset(characterOffset)
        except NotImplementedError:
            try:
                obj.queryComponent().grabFocus()
            except:
                debug.printException(debug.LEVEL_SEVERE)
        except:
            debug.printException(debug.LEVEL_SEVERE)

        orca.setLocusOfFocus(None, obj, notifyPresentationManager=False)

    def _presentLine(self, obj, offset):
        """Presents the first line of the object to the user.

        Arguments:
        - obj: the accessible object to be presented.
        - offset: the character offset within obj.
        """

        self._script.updateBraille(obj)
        self._script.sayLine(obj)

    def _presentObject(self, obj, offset):
        """Presents the entire object to the user.

        Arguments:
        - obj: the accessible object to be presented.
        - offset: the character offset within obj.
        """

        self._script.updateBraille(obj)

        # [[[TODO: WDW - move the voice selection to formatting.py
        # at some point.]]]
        #
        voices = self._script.voices
        if obj.getRole() == pyatspi.ROLE_LINK:
            voice = voices[settings.HYPERLINK_VOICE]
        else:
            voice = None

        utterances = self._script.speechGenerator.generateSpeech(obj)
        speech.speak(utterances, voice)

    #########################################################################
    #                                                                       #
    # Objects                                                               #
    #                                                                       #
    #########################################################################

    # All structural navigation objects have the following essential
    # characteristics:
    #
    # 1. Keybindings for goPrevious, goNext, and other such methods
    # 2. A means of identification (at least a predicate and possibly
    #    also criteria for generating a collection match rule)
    # 3. A definition of how the object should be presented (both
    #    when another instance of that object is found as well as
    #    when it is not)
    #
    # Convenience methods have been put into place whereby one can
    # create an object (FOO = "foo"), and then provide the following
    # methods: _fooBindings(), _fooPredicate(), _fooCriteria(), and
    # _fooPresentation().  With these in place, and with the object
    # FOO included among the StructuralNavigation.enabledTypes for
    # the script, the structural navigation object should be created
    # and set up automagically. At least that is the idea. :-) This
    # hopefully will also enable easy re-definition of existing
    # objects on a script-by-script basis.  For instance, in the
    # StarOffice script, overriding the _blockquotePredicate should
    # be all that is needed to implement navigation by blockquote
    # in OOo Writer documents.
    #

    ########################
    #                      #
    # Anchors              #
    #                      #
    ########################

    def _anchorBindings(self):
        """Returns a dictionary of [keysymstring, modifiers, description]
        lists for navigating amongst anchors.
        """

        # NOTE: This doesn't handle the case where the anchor is not an
        # old-school <a name/id="foo"></a> anchor. For instance on the
        # GNOME wiki, an "anchor" is actually an id applied to some other
        # tag (e.g. <h2 id="foo">My Heading</h2>.  We'll have to be a
        # bit more clever for those.  With the old-school anchors, this
        # seems to work nicely and provides the user with a way to jump
        # among defined areas without having to find a Table of Contents
        # group of links (assuming such a thing is even present on the
        # page).

        bindings = {}
        # Translators: this is for navigating among anchors in a document.
        # An anchor is a named spot that one can jump to.
        #
        prevDesc = _("Goes to previous anchor.")
        bindings["previous"] = ["", settings.NO_MODIFIER_MASK, prevDesc]
        # Translators: this is for navigating among anchors in a document.
        # An anchor is a named spot that one can jump to.
        #
        nextDesc = _("Goes to next anchor.")
        bindings["next"] = ["", settings.NO_MODIFIER_MASK, nextDesc]
        return bindings

    def _anchorCriteria(self, collection, arg=None):
        """Returns the MatchCriteria to be used for locating anchors
        by collection.

        Arguments:
        - collection: the collection interface for the document
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        role = [pyatspi.ROLE_LINK]
        state = [pyatspi.STATE_FOCUSABLE]
        stateMatch = collection.MATCH_NONE
        return MatchCriteria(collection,
                             states=state,
                             matchStates=stateMatch,
                             roles=role)

    def _anchorPredicate(self, obj, arg=None):
        """The predicate to be used for verifying that the object
        obj is an anchor.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        isMatch = False
        if obj and obj.getRole() == pyatspi.ROLE_LINK:
            state = obj.getState()
            isMatch = not state.contains(pyatspi.STATE_FOCUSABLE)
        return isMatch

    def _anchorPresentation(self, obj, arg=None):
        """Presents the anchor or indicates that one was not found.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        if obj:
            [obj, characterOffset] = self._getCaretPosition(obj)
            self._setCaretPosition(obj, characterOffset)
            self._presentObject(obj, characterOffset)
        else:
            # Translators: this is for navigating document content by
            # moving from anchor to anchor. (An anchor is a named spot
            # that one can jump to. This stirng is what orca will say
            # if there are no more anchors found.
            #
            speech.speak(_("No more anchors."))

    ########################
    #                      #
    # Blockquotes          #
    #                      #
    ########################

    def _blockquoteBindings(self):
        """Returns a dictionary of [keysymstring, modifiers, description]
        lists for navigating among blockquotes.
        """

        bindings = {}
        # Translators: this is for navigating among blockquotes in a
        # document.
        #
        prevDesc = _("Goes to previous blockquote.")
        bindings["previous"] = ["q", settings.SHIFT_MODIFIER_MASK, prevDesc]
        # Translators: this is for navigating among blockquotes in a
        # document.
        #
        nextDesc = _("Goes to next blockquote.")
        bindings["next"] = ["q", settings.NO_MODIFIER_MASK, nextDesc]
        return bindings

    def _blockquoteCriteria(self, collection, arg=None):
        """Returns the MatchCriteria to be used for locating blockquotes
        by collection.

        Arguments:
        - collection: the collection interface for the document
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        attrs = ['tag:BLOCKQUOTE']
        return MatchCriteria(collection, objAttrs=attrs)

    def _blockquotePredicate(self, obj, arg=None):
        """The predicate to be used for verifying that the object
        obj is a blockquote.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        if not obj:
            return False

        attributes = obj.getAttributes()
        if attributes:
            for attribute in attributes:
                if attribute == "tag:BLOCKQUOTE":
                    return True

        return False

    def _blockquotePresentation(self, obj, arg=None):
        """Presents the blockquote or indicates that one was not found.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        if obj:
            [obj, characterOffset] = self._getCaretPosition(obj)
            self._setCaretPosition(obj, characterOffset)
            # TODO: We currently present the line, so that's kept here.
            # But we should probably present the object, which would
            # be consistent with the change made recently for headings.
            #
            self._presentLine(obj, characterOffset)
        else:
            # Translators: this is for navigating document content by
            # moving from blockquote to blockquote. This string is what
            # Orca will say if there are no more blockquotes found.
            #
            speech.speak(_("No more blockquotes."))

    ########################
    #                      #
    # Buttons              #
    #                      #
    ########################

    def _buttonBindings(self):
        """Returns a dictionary of [keysymstring, modifiers, description]
        lists for navigating amongst buttons.
        """

        bindings = {}
        # Translators: this is for navigating among buttons in a form
        # within a document.
        #
        prevDesc = _("Goes to previous button.")
        bindings["previous"] = ["", settings.NO_MODIFIER_MASK, prevDesc]
        # Translators: this is for navigating among buttons in a form
        # within a document.
        #
        nextDesc = _("Goes to next button.")
        bindings["next"] = ["", settings.NO_MODIFIER_MASK, nextDesc]
        return bindings

    def _buttonCriteria(self, collection, arg=None):
        """Returns the MatchCriteria to be used for locating buttons
        by collection.

        Arguments:
        - collection: the collection interface for the document
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        role = [pyatspi.ROLE_PUSH_BUTTON]
        state = [pyatspi.STATE_FOCUSABLE, pyatspi.STATE_SENSITIVE]
        stateMatch = collection.MATCH_ALL
        return MatchCriteria(collection,
                             states=state,
                             matchStates=stateMatch,
                             roles=role)

    def _buttonPredicate(self, obj, arg=None):
        """The predicate to be used for verifying that the object
        obj is a button.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        isMatch = False
        if obj and obj.getRole() == pyatspi.ROLE_PUSH_BUTTON:
            state = obj.getState()
            isMatch = state.contains(pyatspi.STATE_FOCUSABLE) \
                  and state.contains(pyatspi.STATE_SENSITIVE)

        return isMatch

    def _buttonPresentation(self, obj, arg=None):
        """Presents the button or indicates that one was not found.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        if obj:
            obj.queryComponent().grabFocus()
        else:
            # Translators: this is for navigating in document content
            # by moving from push button to push button in a form. This
            # string is what Orca will say if there are no more buttons
            # found.
            #
            speech.speak(_("No more buttons."))

    ########################
    #                      #
    # Check boxes          #
    #                      #
    ########################

    def _checkBoxBindings(self):
        """Returns a dictionary of [keysymstring, modifiers, description]
        lists for navigating amongst check boxes.
        """

        bindings = {}
        # Translators: this is for navigating among check boxes in a form
        # within a document.
        #
        prevDesc = _("Goes to previous check box.")
        bindings["previous"] = ["", settings.NO_MODIFIER_MASK, prevDesc]
        # Translators: this is for navigating among check boxes in a form
        # within a document.
        #
        nextDesc = _("Goes to next check box.")
        bindings["next"] = ["", settings.NO_MODIFIER_MASK, nextDesc]
        return bindings

    def _checkBoxCriteria(self, collection, arg=None):
        """Returns the MatchCriteria to be used for locating check boxes
        by collection.

        Arguments:
        - collection: the collection interface for the document
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        role = [pyatspi.ROLE_CHECK_BOX]
        state = [pyatspi.STATE_FOCUSABLE, pyatspi.STATE_SENSITIVE]
        stateMatch = collection.MATCH_ALL
        return MatchCriteria(collection,
                             states=state,
                             matchStates=stateMatch,
                             roles=role)

    def _checkBoxPredicate(self, obj, arg=None):
        """The predicate to be used for verifying that the object
        obj is a check box.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        isMatch = False
        if obj and obj.getRole() == pyatspi.ROLE_CHECK_BOX:
            state = obj.getState()
            isMatch = state.contains(pyatspi.STATE_FOCUSABLE) \
                  and state.contains(pyatspi.STATE_SENSITIVE)

        return isMatch

    def _checkBoxPresentation(self, obj, arg=None):
        """Presents the check box or indicates that one was not found.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        if obj:
            obj.queryComponent().grabFocus()
        else:
            # Translators: this is for navigating in document content
            # by moving from checkbox to checkbox in a form. This
            # string is what Orca will say if there are no more check
            # boxes found.
            #
            speech.speak(_("No more check boxes."))

    ########################
    #                      #
    # Chunks/Large Objects #
    #                      #
    ########################

    def _chunkBindings(self):
        """Returns a dictionary of [keysymstring, modifiers, description]
        lists for navigating amongst chunks/large objects.
        """

        bindings = {}
        # Translators: this is for navigating a document in a
        # structural manner, where a 'large object' is a logical
        # chunk of text, such as a paragraph, a list, a table, etc.
        #
        prevDesc = _("Goes to previous large object.")
        bindings["previous"] = ["o", settings.SHIFT_MODIFIER_MASK, prevDesc]
        # Translators: this is for navigating a document in a
        # structural manner, where a 'large object' is a logical
        # chunk of text, such as a paragraph, a list, a table, etc.
        #
        nextDesc = _("Goes to next large object.")
        bindings["next"] = ["o", settings.NO_MODIFIER_MASK, nextDesc]
        # I don't think it makes sense to add support for a list
        # of chunks.  But one could always change that here.
        #
        return bindings

    def _chunkCriteria(self, collection, arg=None):
        """Returns the MatchCriteria to be used for locating chunks/
        large objects by collection.

        Arguments:
        - collection: the collection interface for the document
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        role = self.OBJECT_ROLES
        roleMatch = collection.MATCH_ANY
        return MatchCriteria(collection,
                             roles=role,
                             matchRoles=roleMatch,
                             applyPredicate=True)

    def _chunkPredicate(self, obj, arg=None):
        """The predicate to be used for verifying that the object
        obj is a chunk.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        isMatch = False

        if obj and obj.getRole() in self.OBJECT_ROLES:
            try:
                text = obj.queryText()
                characterCount = text.characterCount
            except:
                characterCount = 0

            if characterCount > settings.largeObjectTextLength \
               and not self._isUselessObject(obj):
                isMatch = True

        return isMatch

    def _chunkPresentation(self, obj, arg=None):
        """Presents the chunk or indicates that one was not found.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        if obj:
            [newObj, characterOffset] = self._getCaretPosition(obj)
            self._setCaretPosition(newObj, characterOffset)
            self._presentObject(obj, 0)
        else:
            # Translators: this is for navigating document content by
            # moving from 'large object' to 'large object'. A 'large
            # object' is a logical chunk of text, such as a paragraph,
            # a list, a table, etc. This string is what Orca will say
            # if there are no more large objects found.
            #
            speech.speak(_("No more large objects."))

    ########################
    #                      #
    # Combo Boxes          #
    #                      #
    ########################

    def _comboBoxBindings(self):
        """Returns a dictionary of [keysymstring, modifiers, description]
        lists for navigating amongst combo boxes.
        """

        bindings = {}
        # Translators: this is for navigating among combo boxes in a form
        # within a document.
        #
        prevDesc = _("Goes to previous combo box.")
        bindings["previous"] = ["", settings.NO_MODIFIER_MASK, prevDesc]
        # Translators: this is for navigating among combo boxes in a form
        # within a document.
        #
        nextDesc = _("Goes to next combo box.")
        bindings["next"] = ["", settings.NO_MODIFIER_MASK, nextDesc]
        return bindings

    def _comboBoxCriteria(self, collection, arg=None):
        """Returns the MatchCriteria to be used for locating combo boxes
        by collection.

        Arguments:
        - collection: the collection interface for the document
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        role = [pyatspi.ROLE_COMBO_BOX]
        state = [pyatspi.STATE_FOCUSABLE, pyatspi.STATE_SENSITIVE]
        stateMatch = collection.MATCH_ALL
        return MatchCriteria(collection,
                             states=state,
                             matchStates=stateMatch,
                             roles=role)

    def _comboBoxPredicate(self, obj, arg=None):
        """The predicate to be used for verifying that the object
        obj is a combo box.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        isMatch = False
        if obj and obj.getRole() == pyatspi.ROLE_COMBO_BOX:
            state = obj.getState()
            isMatch = state.contains(pyatspi.STATE_FOCUSABLE) \
                  and state.contains(pyatspi.STATE_SENSITIVE)

        return isMatch

    def _comboBoxPresentation(self, obj, arg=None):
        """Presents the combo box or indicates that one was not found.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        if obj:
            obj.queryComponent().grabFocus()
        else:
            # Translators: this is for navigating in document content
            # by moving from combo box to combo box in a form. This
            # string is what Orca will say if there are no more combo
            # boxes found.
            #
            speech.speak(_("No more combo boxes."))

    ########################
    #                      #
    # Entries              #
    #                      #
    ########################

    def _entryBindings(self):
        """Returns a dictionary of [keysymstring, modifiers, description]
        lists for navigating amongst entries.
        """

        bindings = {}
        # Translators: this is for navigating among text entries in a form
        # within a document.
        #
        prevDesc = _("Goes to previous entry.")
        bindings["previous"] = ["", settings.NO_MODIFIER_MASK, prevDesc]
        # Translators: this is for navigating among text entries
        # in a form.
        #
        nextDesc = _("Goes to next entry.")
        bindings["next"] = ["", settings.NO_MODIFIER_MASK, nextDesc]
        return bindings

    def _entryCriteria(self, collection, arg=None):
        """Returns the MatchCriteria to be used for locating entries
        by collection.

        Arguments:
        - collection: the collection interface for the document
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        role = [pyatspi.ROLE_ENTRY,
                pyatspi.ROLE_PASSWORD_TEXT,
                pyatspi.ROLE_TEXT]
        roleMatch = collection.MATCH_ANY
        state = [pyatspi.STATE_FOCUSABLE,
                 pyatspi.STATE_SENSITIVE,
                 pyatspi.STATE_EDITABLE]
        stateMatch = collection.MATCH_ALL
        return MatchCriteria(collection,
                             states=state,
                             matchStates=stateMatch,
                             roles=role,
                             matchRoles=roleMatch)

    def _entryPredicate(self, obj, arg=None):
        """The predicate to be used for verifying that the object
        obj is an entry.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        isMatch = False
        if obj and obj.getRole() in [pyatspi.ROLE_ENTRY,
                                     pyatspi.ROLE_PASSWORD_TEXT,
                                     pyatspi.ROLE_TEXT]:
            state = obj.getState()
            isMatch = state.contains(pyatspi.STATE_FOCUSABLE) \
                  and state.contains(pyatspi.STATE_SENSITIVE) \
                  and state.contains(pyatspi.STATE_EDITABLE)

        return isMatch

    def _entryPresentation(self, obj, arg=None):
        """Presents the entry or indicates that one was not found.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        if obj:
            obj.queryComponent().grabFocus()
        else:
            # Translators: this is for navigating in document content
            # by moving from text entry to text entry in a form. This
            # string is what Orca will say if there are no more entries
            # found.
            #
            speech.speak(_("No more entries."))

    ########################
    #                      #
    # Form Fields          #
    #                      #
    ########################

    def _formFieldBindings(self):
        """Returns a dictionary of [keysymstring, modifiers, description]
        lists for navigating amongst form fields.
        """

        bindings = {}
        # Translators: this is for navigating among fields in a form within
        # a document.
        #
        prevDesc = _("Goes to previous form field.")
        bindings["previous"] = ["Tab",
                                settings.ORCA_SHIFT_MODIFIER_MASK,
                                prevDesc]
        # Translators: this is for navigating among fields in a form within
        # a document.
        #
        nextDesc = _("Goes to next form field.")
        bindings["next"] = ["Tab", settings.ORCA_MODIFIER_MASK, nextDesc]
        return bindings

    def _formFieldCriteria(self, collection, arg=None):
        """Returns the MatchCriteria to be used for locating form fields
        by collection.

        Arguments:
        - collection: the collection interface for the document
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        role = self.FORM_ROLES
        roleMatch = collection.MATCH_ANY
        state = [pyatspi.STATE_FOCUSABLE, pyatspi.STATE_SENSITIVE]
        stateMatch = collection.MATCH_ALL
        return MatchCriteria(collection,
                             states=state,
                             matchStates=stateMatch,
                             roles=role,
                             matchRoles=roleMatch)

    def _formFieldPredicate(self, obj, arg=None):
        """The predicate to be used for verifying that the object
        obj is a form field.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        isMatch = False
        if obj and obj.getRole() in self.FORM_ROLES:
            state = obj.getState()
            isMatch = state.contains(pyatspi.STATE_FOCUSABLE) \
                  and state.contains(pyatspi.STATE_SENSITIVE)

        return isMatch

    def _formFieldPresentation(self, obj, arg=None):
        """Presents the form field or indicates that one was not found.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        if obj:
            if obj.getRole() in [pyatspi.ROLE_LIST, pyatspi.ROLE_COMBO_BOX]:
                obj.queryComponent().grabFocus()
            else:
                # TODO: I think we should just grab focus on the object
                # regardless of the object type.  But that's not what we
                # do now, and it causes an extra newline character to show
                # up in the regression test output for entries, so for the
                # purpose of passing the regression tests, I'm not making
                # that change yet.
                #
                [obj, characterOffset] = self._getCaretPosition(obj)
                self._setCaretPosition(obj, characterOffset)
                self._presentObject(obj, characterOffset)
        else:
            # Translators: this is for navigating in document content
            # by moving from form field to form field. This string is
            # what Orca will say if there are no more form fields found.
            #
            speech.speak(_("No more form fields."))

    ########################
    #                      #
    # Headings             #
    #                      #
    ########################

    def _headingBindings(self):
        """Returns a dictionary of [keysymstring, modifiers, description]
        lists for navigating amongst headings.
        """

        bindings = {}
        # Translators: this is for navigating in a document by heading.
        # (e.g. <h1>)
        #
        prevDesc = _("Goes to previous heading.")
        bindings["previous"] = ["h", settings.SHIFT_MODIFIER_MASK, prevDesc]
        # Translators: this is for navigating in a document by heading.
        # (e.g., <h1>)
        #
        nextDesc = _("Goes to next heading.")
        bindings["next"] = ["h", settings.NO_MODIFIER_MASK, nextDesc]

        prevAtLevelBindings = []
        nextAtLevelBindings = []
        minLevel, maxLevel = self._headingLevels()
        for i in range(minLevel, maxLevel + 1):
            # Translators: this is for navigating in a document by heading.
            # (e.g. <h1> is a heading at level 1).
            #
            prevDesc = _("Goes to previous heading at level %d.") % i
            prevAtLevelBindings.append([str(i),
                                        settings.SHIFT_MODIFIER_MASK,
                                        prevDesc])
            # Translators: this is for navigating in a document by heading.
            # (e.g. <h1> is a heading at level 1).
            #
            nextDesc = _("Goes to next heading at level %d.") % i
            nextAtLevelBindings.append([str(i),
                                        settings.NO_MODIFIER_MASK,
                                        nextDesc])
        bindings["previousAtLevel"] = prevAtLevelBindings
        bindings["nextAtLevel"] = nextAtLevelBindings
        return bindings

    def _headingLevels(self):
        """Returns the [minimum heading level, maximum heading level]
        which should be navigable via structural navigation.
        """

        return [1, 6]

    def _headingCriteria(self, collection, arg=None):
        """Returns the MatchCriteria to be used for locating headings
        by collection.

        Arguments:
        - collection: the collection interface for the document
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        role = [pyatspi.ROLE_HEADING]
        attrs = []
        if arg:
            attrs.append('level:%d' % arg)

        return MatchCriteria(collection,
                             roles=role,
                             objAttrs=attrs)

    def _headingPredicate(self, obj, arg=None):
        """The predicate to be used for verifying that the object
        obj is a heading.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        isMatch = False
        if obj and obj.getRole() == pyatspi.ROLE_HEADING:
            if arg:
                isMatch = (arg == self._getHeadingLevel(obj))
            else:
                isMatch = True

        return isMatch

    def _headingPresentation(self, obj, arg=None):
        """Presents the heading or indicates that one was not found.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        if obj:
            [obj, characterOffset] = self._getCaretPosition(obj)
            self._setCaretPosition(obj, characterOffset)
            self._presentObject(obj, characterOffset)
        elif not arg:
            # Translators: this is for navigating HTML content by
            # moving from heading to heading (e.g. <h1>, <h2>, etc).
            # This string is what Orca will say if there are no more
            # headings found.
            #
            speech.speak(_("No more headings."))
        else:
            # Translators: this is for navigating HTML content by
            # moving from heading to heading at a particular level
            # (i.e. only <h1> or only <h2>, etc.) This string is
            # what Orca will say if there are no more headings found.
            #
            speech.speak(_("No more headings at level %d.") % arg)

    ########################
    #                      #
    # Landmarks            #
    #                      #
    ########################

    def _landmarkBindings(self):
        """Returns a dictionary of [keysymstring, modifiers, description]
        lists for navigating amongst landmarks.
        """

        bindings = {}
        # Translators: this is for navigating to the previous ARIA
        # role landmark.  ARIA role landmarks are the W3C defined
        # HTML tag attribute 'role' used to identify important part
        # of webpage like banners, main context, search etc.
        #
        prevDesc = _("Goes to previous landmark.")
        bindings["previous"] = ["m", settings.SHIFT_MODIFIER_MASK, prevDesc]
        # Translators: this is for navigating to the next ARIA
        # role landmark.  ARIA role landmarks are the W3C defined
        # HTML tag attribute 'role' used to identify important part
        # of webpage like banners, main context, search etc.
        #
        nextDesc = _("Goes to next landmark.")
        bindings["next"] = ["m", settings.NO_MODIFIER_MASK, nextDesc]
        return bindings

    def _landmarkCriteria(self, collection, arg=None):
        """Returns the MatchCriteria to be used for locating landmarks
        by collection.

        Arguments:
        - collection: the collection interface for the document
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        # NOTE: there is a limitation in the AT-SPI Collections interface
        # when it comes to an attribute whose value can be a list.  For
        # example, the xml-roles attribute can be a space-separate list
        # of roles.  We'd like to make a match if the xml-roles attribute
        # has one (or any) of the roles we care about.  Instead, we're
        # restricted to an exact match.  So, the below will only work in 
        # the cases where the xml-roles attribute value consists solely of a
        # single role.  In practice, this seems to be the case that we run
        # into for the landmark roles.
        #
        attrs = []
        for landmark in settings.ariaLandmarks:
            attrs.append('xml-roles:' + landmark)

        return MatchCriteria(collection, objAttrs=attrs)

    def _landmarkPredicate(self, obj, arg=None):
        """The predicate to be used for verifying that the object
        obj is a landmark.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        if obj is None:
            return False

        attrs = dict([attr.split(':', 1) for attr in obj.getAttributes()])
        try:
            import sets
            if sets.Set(attrs['xml-roles']).intersection(\
                sets.Set(settings.ariaLandmarks)):
                return True
            else:
                return False
        except KeyError:
            return False

    def _landmarkPresentation(self, obj, arg=None):
        """Presents the landmark or indicates that one was not found.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        if obj:
            [obj, characterOffset] = self._getCaretPosition(obj)
            self._setCaretPosition(obj, characterOffset)
            self._presentObject(obj, characterOffset)
        else:
            # Translators: this is for navigating to the previous ARIA
            # role landmark.  ARIA role landmarks are the W3C defined
            # HTML tag attribute 'role' used to identify important part
            # of webpage like banners, main context, search etc.  This
            # is an indication that one was not found.
            #
            speech.speak(_("No landmark found."))

    ########################
    #                      #
    # Lists                #
    #                      #
    ########################

    def _listBindings(self):
        """Returns a dictionary of [keysymstring, modifiers, description]
        lists for navigating amongst (un)ordered lists.
        """

        bindings = {}
        # Translators: this is for navigating among bulleted/numbered
        # lists in a document.
        #
        prevDesc = _("Goes to previous list.")
        bindings["previous"] = ["l", settings.SHIFT_MODIFIER_MASK, prevDesc]
        # Translators: this is for navigating among bulleted/numbered
        # lists in a document.
        #
        nextDesc = _("Goes to next list.")
        bindings["next"] = ["l", settings.NO_MODIFIER_MASK, nextDesc]
        return bindings

    def _listCriteria(self, collection, arg=None):
        """Returns the MatchCriteria to be used for locating (un)ordered
        lists by collection.

        Arguments:
        - collection: the collection interface for the document
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        role = [pyatspi.ROLE_LIST]
        state = [pyatspi.STATE_FOCUSABLE]
        stateMatch = collection.MATCH_NONE
        return MatchCriteria(collection,
                             states=state,
                             matchStates=stateMatch,
                             roles=role)

    def _listPredicate(self, obj, arg=None):
        """The predicate to be used for verifying that the object
        obj is an (un)ordered list.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        isMatch = False

        if obj and obj.getRole() == pyatspi.ROLE_LIST:
            isMatch = not obj.getState().contains(pyatspi.STATE_FOCUSABLE)

        return isMatch

    def _listPresentation(self, obj, arg=None):
        """Presents the (un)ordered list or indicates that one was not
        found.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        # TODO: Ultimately it should be the job of the speech (and braille)
        # generator to present things like this.
        #
        if obj:
            nItems = 0
            for child in obj:
                if child.getRole() == pyatspi.ROLE_LIST_ITEM:
                    nItems += 1
            # Translators: this represents a list in HTML.
            #
            itemString = ngettext("List with %d item",
                                  "List with %d items",
                                  nItems) % nItems
            speech.speak(itemString)
            nestingLevel = 0
            parent = obj.parent
            while parent.getRole() == pyatspi.ROLE_LIST:
                nestingLevel += 1
                parent = parent.parent
            if nestingLevel:
                # Translators: this represents a list item in a document.
                # The nesting level is how 'deep' the item is (e.g., a
                # level of 2 represents a list item inside a list that's
                # inside another list).
                #
                speech.speak(_("Nesting level %d") % nestingLevel)
            [obj, characterOffset] = self._getCaretPosition(obj)
            self._setCaretPosition(obj, characterOffset)
            self._presentLine(obj, characterOffset)
        else:
            # Translators: this is for navigating document content by moving
            # from bulleted/numbered list to bulleted/numbered list. This
            # string is what Orca will say if there are no more lists found.
            #
            speech.speak(_("No more lists."))

    ########################
    #                      #
    # List Items           #
    #                      #
    ########################

    def _listItemBindings(self):
        """Returns a dictionary of [keysymstring, modifiers, description]
        lists for navigating amongst items in an (un)ordered list.
        """

        bindings = {}
        # Translators: this is for navigating among bulleted/numbered list
        # items in a document.
        #
        prevDesc = _("Goes to previous list item.")
        bindings["previous"] = ["i", settings.SHIFT_MODIFIER_MASK, prevDesc]
        # Translators: this is for navigating among bulleted/numbered list
        # items in a document.
        #
        nextDesc = _("Goes to next list item.")
        bindings["next"] = ["i", settings.NO_MODIFIER_MASK, nextDesc]
        return bindings

    def _listItemCriteria(self, collection, arg=None):
        """Returns the MatchCriteria to be used for locating items in an
        (un)ordered list by collection.

        Arguments:
        - collection: the collection interface for the document
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        role = [pyatspi.ROLE_LIST_ITEM]
        state = [pyatspi.STATE_FOCUSABLE]
        stateMatch = collection.MATCH_NONE
        return MatchCriteria(collection,
                             states=state,
                             matchStates=stateMatch,
                             roles=role)

    def _listItemPredicate(self, obj, arg=None):
        """The predicate to be used for verifying that the object
        obj is an item in an (un)ordered list.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        isMatch = False

        if obj and obj.getRole() == pyatspi.ROLE_LIST_ITEM:
            isMatch = not obj.getState().contains(pyatspi.STATE_FOCUSABLE)

        return isMatch

    def _listItemPresentation(self, obj, arg=None):
        """Presents the (un)ordered list item or indicates that one was not
        found.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        if obj:
            [obj, characterOffset] = self._getCaretPosition(obj)
            self._setCaretPosition(obj, characterOffset)
            # TODO: We currently present the line, so that's kept here.
            # But we should probably present the object, which would
            # be consistent with the change made recently for headings.
            #
            self._presentLine(obj, characterOffset)
        else:
            # Translators: this is for navigating document content by
            # moving from bulleted/numbered list item to  bulleted/
            # numbered list item.  This string is what Orca will say
            # if there are no more list items found.
            #
            speech.speak(_("No more list items."))

    ########################
    #                      #
    # Live Regions         #
    #                      #
    ########################

    def _liveRegionBindings(self):
        """Returns a dictionary of [keysymstring, modifiers, description]
        lists for navigating amongst live regions.
        """

        bindings = {}
        # Translators: this is for navigating between live regions
        #
        prevDesc = _("Goes to previous live region.")
        bindings["previous"] = ["r", settings.SHIFT_MODIFIER_MASK, prevDesc]
        # Translators: this is for navigating between live regions
        #
        nextDesc = _("Goes to next live region.")
        bindings["next"] = ["r", settings.NO_MODIFIER_MASK, nextDesc]
        # Translators: this is for navigating to the last live region
        # to make an announcement.
        #
        desc = _("Goes to last live region.")
        bindings["last"] = ["y", settings.NO_MODIFIER_MASK, desc]
        return bindings

    def _liveRegionPredicate(self, obj, arg=None):
        """The predicate to be used for verifying that the object
        obj is a live region.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        isMatch = False

        regobjs = self._script.liveMngr.getLiveNoneObjects()
        if self._script.liveMngr.matchLiveRegion(obj) or obj in regobjs:
            isMatch = True

        return isMatch

    def _liveRegionPresentation(self, obj, arg=None):
        """Presents the live region or indicates that one was not found.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        if obj:
            # TODO: We don't want to move to a list item.
            # Is this the best place to handle this?
            #
            if obj.getRole() == pyatspi.ROLE_LIST:
                characterOffset = 0
            else:
                [obj, characterOffset] = self._getCaretPosition(obj)
            self._setCaretPosition(obj, characterOffset)
            self._presentObject(obj, characterOffset)
            # For debugging
            #
            self._script.outlineAccessible(obj)
        else:
            # Translators: this is for navigating HTML in a structural
            # manner, where a 'live region' is a location in a web page
            # that are updated without having to refresh the entire page.
            #
            speech.speak(_("No more live regions."))

    ########################
    #                      #
    # Paragraphs           #
    #                      #
    ########################

    def _paragraphBindings(self):
        """Returns a dictionary of [keysymstring, modifiers, description]
        lists for navigating amongst paragraphs.
        """

        bindings = {}
        # Translators: this is for navigating among paragraphs in a document.
        #
        prevDesc = _("Goes to previous paragraph.")
        bindings["previous"] = ["p", settings.SHIFT_MODIFIER_MASK, prevDesc]
        # Translators: this is for navigating among paragraphs in a document.
        #
        nextDesc = _("Goes to next paragraph.")
        bindings["next"] = ["p", settings.NO_MODIFIER_MASK, nextDesc]
        return bindings

    def _paragraphCriteria(self, collection, arg=None):
        """Returns the MatchCriteria to be used for locating paragraphs
        by collection.

        Arguments:
        - collection: the collection interface for the document
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        role = [pyatspi.ROLE_PARAGRAPH]
        return MatchCriteria(collection, roles=role, applyPredicate=True)

    def _paragraphPredicate(self, obj, arg=None):
        """The predicate to be used for verifying that the object
        obj is a paragraph.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        isMatch = False
        if obj and obj.getRole() == pyatspi.ROLE_PARAGRAPH:
            try:
                text = obj.queryText()
                # We're choosing 3 characters as the minimum because some
                # paragraphs contain a single image or link and a text
                # of length 2: An embedded object character and a space.
                # We want to skip these.
                #
                isMatch = text.characterCount > 2
            except:
                pass

        return isMatch

    def _paragraphPresentation(self, obj, arg=None):
        """Presents the paragraph or indicates that one was not found.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        if obj:
            [newObj, characterOffset] = self._getCaretPosition(obj)
            self._setCaretPosition(newObj, characterOffset)
            self._presentObject(obj, 0)
        else:
            # Translators: this is for navigating document content by
            # moving from paragraph to paragraph. This string is what
            # Orca will say if there are no more large objects found.
            #
            speech.speak(_("No more paragraphs."))

    ########################
    #                      #
    # Radio Buttons        #
    #                      #
    ########################

    def _radioButtonBindings(self):
        """Returns a dictionary of [keysymstring, modifiers, description]
        lists for navigating amongst radio buttons.
        """

        bindings = {}
        # Translators: this is for navigating among radio buttons in a
        # form within a document.
        #
        prevDesc = _("Goes to previous radio button.")
        bindings["previous"] = ["", settings.NO_MODIFIER_MASK, prevDesc]
        # Translators: this is for navigating among radio buttons in a
        # form within a document.
        #
        nextDesc = _("Goes to next radio button.")
        bindings["next"] = ["", settings.NO_MODIFIER_MASK, nextDesc]
        return bindings

    def _radioButtonCriteria(self, collection, arg=None):
        """Returns the MatchCriteria to be used for locating radio buttons
        by collection.

        Arguments:
        - collection: the collection interface for the document
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        role = [pyatspi.ROLE_RADIO_BUTTON]
        state = [pyatspi.STATE_FOCUSABLE, pyatspi.STATE_SENSITIVE]
        stateMatch = collection.MATCH_ALL
        return MatchCriteria(collection,
                             states=state,
                             matchStates=stateMatch,
                             roles=role)

    def _radioButtonPredicate(self, obj, arg=None):
        """The predicate to be used for verifying that the object
        obj is a radio button.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        isMatch = False
        if obj and obj.getRole() == pyatspi.ROLE_RADIO_BUTTON:
            state = obj.getState()
            isMatch = state.contains(pyatspi.STATE_FOCUSABLE) \
                  and state.contains(pyatspi.STATE_SENSITIVE)

        return isMatch

    def _radioButtonPresentation(self, obj, arg=None):
        """Presents the radio button or indicates that one was not found.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        if obj:
            obj.queryComponent().grabFocus()
        else:
            # Translators: this is for navigating in document content
            # by moving from radio button to radio button in a form.
            # This string is what Orca will say if there are no more
            # radio buttons found.
            #
            speech.speak(_("No more radio buttons."))

    ########################
    #                      #
    # Tables               #
    #                      #
    ########################

    def _tableBindings(self):
        """Returns a dictionary of [keysymstring, modifiers, description]
        lists for navigating amongst tables.
        """

        bindings = {}
        # Translators: this is for navigating among tables in a document.
        #
        prevDesc = _("Goes to previous table.")
        bindings["previous"] = ["t", settings.SHIFT_MODIFIER_MASK, prevDesc]
        # Translators: this is for navigating among tables in a document.
        #
        nextDesc = _("Goes to next table.")
        bindings["next"] = ["t", settings.NO_MODIFIER_MASK, nextDesc]
        return bindings

    def _tableCriteria(self, collection, arg=None):
        """Returns the MatchCriteria to be used for locating tables
        by collection.

        Arguments:
        - collection: the collection interface for the document
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        role = [pyatspi.ROLE_TABLE]
        return MatchCriteria(collection, roles=role, applyPredicate=True)

    def _tablePredicate(self, obj, arg=None):
        """The predicate to be used for verifying that the object
        obj is a table.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        if obj and obj.childCount and obj.getRole() == pyatspi.ROLE_TABLE:
            try:
                return obj.queryTable().nRows > 0
            except:
                pass

        return False

    def _tablePresentation(self, obj, arg=None):
        """Presents the table or indicates that one was not found.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        if obj:
            caption = self._getTableCaption(obj)
            if caption:
                speech.speak(caption)
            speech.speak(self._getTableDescription(obj))
            cell = obj.queryTable().getAccessibleAt(0, 0)
            self.lastTableCell = [0, 0]
            [cell, characterOffset] = self._getCaretPosition(cell)
            self._setCaretPosition(cell, characterOffset)
            self._presentObject(cell, characterOffset)
        else:
            # Translators: this is for navigating document content by moving
            # from table to table.  This string is what Orca will say if there
            # are no more tables found.
            #
            speech.speak(_("No more tables."))

    ########################
    #                      #
    # Table Cells          #
    #                      #
    ########################

    def _tableCellBindings(self):
        """Returns a dictionary of [keysymstring, modifiers, description]
        lists for navigating spatially amongst table cells.
        """

        bindings = {}
        # Translators: this is for navigating among table cells in a document.
        #
        desc = _("Goes left one cell.")
        bindings["left"] = ["Left", settings.SHIFT_ALT_MODIFIER_MASK, desc]
        # Translators: this is for navigating among table cells in a document.
        #
        desc = _("Goes right one cell.")
        bindings["right"] = ["Right", settings.SHIFT_ALT_MODIFIER_MASK, desc]
        # Translators: this is for navigating among table cells in a document.
        #
        desc = _("Goes up one cell.")
        bindings["up"] = ["Up", settings.SHIFT_ALT_MODIFIER_MASK, desc]
        # Translators: this is for navigating among table cells in a document.
        #
        desc = _("Goes down one cell.")
        bindings["down"] = ["Down", settings.SHIFT_ALT_MODIFIER_MASK, desc]
        # Translators: this is for navigating among table cells in a document.
        #
        desc = _("Goes to the first cell in a table.")
        bindings["first"] = ["Home", settings.SHIFT_ALT_MODIFIER_MASK, desc]
        # Translators: this is for navigating among table cells in a document.
        #
        desc = _("Goes to the last cell in a table.")
        bindings["last"] = ["End", settings.SHIFT_ALT_MODIFIER_MASK, desc]
        return bindings

    def _tableCellCriteria(self, collection, arg=None):
        """Returns the MatchCriteria to be used for locating table cells
        by collection.

        Arguments:
        - collection: the collection interface for the document
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        role = [pyatspi.ROLE_TABLE_CELL]
        return MatchCriteria(collection, roles=role)

    def _tableCellPredicate(self, obj, arg=None):
        """The predicate to be used for verifying that the object
        obj is a table cell.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        return (obj and obj.getRole() == pyatspi.ROLE_TABLE_CELL)

    def _tableCellPresentation(self, cell, arg):
        """Presents the table cell or indicates that one was not found.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        if not cell:
            return

        if settings.speakCellHeaders:
            self._presentCellHeaders(cell, arg)

        [obj, characterOffset] = self._getCaretPosition(cell)
        self._setCaretPosition(obj, characterOffset)
        self._script.updateBraille(obj)

        blank = self._isBlankCell(cell)
        if not blank:
            self._presentObject(cell, 0)
        else:
            # Translators: "blank" is a short word to mean the
            # user has navigated to an empty line.
            #
            speech.speak(_("blank"))

        if settings.speakCellCoordinates:
            [row, col] = self.getCellCoordinates(cell)
            # Translators: this represents the (row, col) position of
            # a cell in a table.
            #
            speech.speak(_("Row %(row)d, column %(column)d.") \
                         % {"row" : row + 1, "column" : col + 1})

        spanString = self._getCellSpanInfo(cell)
        if spanString and settings.speakCellSpan:
            speech.speak(spanString)

    ########################
    #                      #
    # Unvisited Links      #
    #                      #
    ########################

    def _unvisitedLinkBindings(self):
        """Returns a dictionary of [keysymstring, modifiers, description]
        lists for navigating amongst unvisited links.
        """

        bindings = {}
        # Translators: this is for navigating among unvisited links in a
        # document.
        #
        prevDesc = _("Goes to previous unvisited link.")
        bindings["previous"] = ["u", settings.SHIFT_MODIFIER_MASK, prevDesc]
        # Translators: this is for navigating among unvisited links in a
        # document.
        #
        nextDesc = _("Goes to next unvisited link.")
        bindings["next"] = ["u", settings.NO_MODIFIER_MASK, nextDesc]
        return bindings

    def _unvisitedLinkCriteria(self, collection, arg=None):
        """Returns the MatchCriteria to be used for locating unvisited links
        by collection.

        Arguments:
        - collection: the collection interface for the document
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        role = [pyatspi.ROLE_LINK]
        state = [pyatspi.STATE_VISITED]
        stateMatch = collection.MATCH_NONE
        return MatchCriteria(collection,
                             states=state,
                             matchStates=stateMatch,
                             roles=role)

    def _unvisitedLinkPredicate(self, obj, arg=None):
        """The predicate to be used for verifying that the object
        obj is an unvisited link.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        isMatch = False

        if obj and obj.getRole() == pyatspi.ROLE_LINK:
            isMatch = not obj.getState().contains(pyatspi.STATE_VISITED)

        return isMatch

    def _unvisitedLinkPresentation(self, obj, arg=None):
        """Presents the unvisited link or indicates that one was not
        found.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        if obj:
            # We were counting on the Gecko script's setCaretPosition
            # to do the focus grab. It turns out that we do not always
            # want setCaretPosition to grab focus on a link (e.g. when
            # arrowing in the text of a paragraph which is a child of
            # a link. Therefore, we need to grab focus here.
            #
            obj.queryComponent().grabFocus()
        else:
            # Translators: this is for navigating document content by
            # moving from unvisited link to unvisited link. This string
            # is what Orca will say if there are no more unvisited links
            # found.
            #
            speech.speak(_("No more unvisited links."))

    ########################
    #                      #
    # Visited Links        #
    #                      #
    ########################

    def _visitedLinkBindings(self):
        """Returns a dictionary of [keysymstring, modifiers, description]
        lists for navigating amongst visited links.
        """

        bindings = {}
        # Translators: this is for navigating among visited links in a
        # document.
        #
        prevDesc = _("Goes to previous visited link.")
        bindings["previous"] = ["v", settings.SHIFT_MODIFIER_MASK, prevDesc]
        # Translators: this is for navigating among visited links in a
        # document.
        #
        nextDesc = _("Goes to next visited link.")
        bindings["next"] = ["v", settings.NO_MODIFIER_MASK, nextDesc]
        return bindings

    def _visitedLinkCriteria(self, collection, arg=None):
        """Returns the MatchCriteria to be used for locating visited links
        by collection.

        Arguments:
        - collection: the collection interface for the document
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        role = [pyatspi.ROLE_LINK]
        state = [pyatspi.STATE_VISITED]
        stateMatch = collection.MATCH_ANY
        return MatchCriteria(collection,
                             states=state,
                             matchStates=stateMatch,
                             roles=role)

    def _visitedLinkPredicate(self, obj, arg=None):
        """The predicate to be used for verifying that the object
        obj is a visited link.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        isMatch = False

        if obj and obj.getRole() == pyatspi.ROLE_LINK:
            isMatch = obj.getState().contains(pyatspi.STATE_VISITED)

        return isMatch

    def _visitedLinkPresentation(self, obj, arg=None):
        """Presents the visited link or indicates that one was not
        found.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """
        if obj:
            obj.queryComponent().grabFocus()
        else:
            # Translators: this is for navigating document content by
            # moving from visited link to visited link. This string is
            # what Orca will say if there are no more visited links
            # found.
            #
            speech.speak(_("No more visited links."))
