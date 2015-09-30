# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
# Copyright 2010-2013 The Orca Team
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

"""Implements structural navigation."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc." \
                "Copyright (c) 2010-2013 The Orca Team"
__license__   = "LGPL"

import pyatspi

from . import cmdnames
from . import debug
from . import guilabels
from . import input_event
from . import keybindings
from . import messages
from . import object_properties
from . import orca
from . import orca_gui_navlist
from . import orca_state
from . import settings
from . import settings_manager
from . import speech

_settingsManager = settings_manager.getManager()
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
                 criteria, presentation, dialogData):

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
        - dialogData: the method which returns the title, column headers,
          and row data which should be included in the "list of" dialog for
          the structural navigation object.
        """

        self.structuralNavigation = structuralNavigation
        self.objType = objType
        self.bindings = bindings
        self.predicate = predicate
        self.criteria = criteria
        self.present = presentation
        self._dialogData = dialogData

        self.inputEventHandlers = {}
        self.keyBindings = keybindings.KeyBindings()
        self.functions = []
        self._setUpHandlersAndBindings()

    def _setUpHandlersAndBindings(self):
        """Adds the inputEventHandlers and keyBindings for this object."""

        # Set up the basic handlers.  These are our traditional goPrevious
        # and goNext functions.
        #
        previousBinding = self.bindings.get("previous")
        if previousBinding:
            [keysymstring, modifiers, description] = previousBinding
            handlerName = "%sGoPrevious" % self.objType
            self.inputEventHandlers[handlerName] = \
                input_event.InputEventHandler(self.goPrevious, description)

            self.keyBindings.add(
                keybindings.KeyBinding(
                    keysymstring,
                    keybindings.defaultModifierMask,
                    modifiers,
                    self.inputEventHandlers[handlerName]))

            self.functions.append(self.goPrevious)

        nextBinding = self.bindings.get("next")
        if nextBinding:
            [keysymstring, modifiers, description] = nextBinding
            handlerName = "%sGoNext" % self.objType
            self.inputEventHandlers[handlerName] = \
                input_event.InputEventHandler(self.goNext, description)

            self.keyBindings.add(
                keybindings.KeyBinding(
                    keysymstring,
                    keybindings.defaultModifierMask,
                    modifiers,
                    self.inputEventHandlers[handlerName]))

            self.functions.append(self.goNext)

        listBinding = self.bindings.get("list")
        if listBinding:
            [keysymstring, modifiers, description] = listBinding
            handlerName = "%sShowList" % self.objType
            self.inputEventHandlers[handlerName] = \
                input_event.InputEventHandler(self.showList, description)

            self.keyBindings.add(
                keybindings.KeyBinding(
                    keysymstring,
                    keybindings.defaultModifierMask,
                    modifiers,
                    self.inputEventHandlers[handlerName]))

            self.functions.append(self.showList)

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
                    keybindings.defaultModifierMask,
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
                    keybindings.defaultModifierMask,
                    modifiers,
                    self.inputEventHandlers[handlerName]))

            self.functions.append(handler)

        listAtLevel = self.bindings.get("listAtLevel") or []
        for i, binding in enumerate(listAtLevel):
            level = i + 1
            handler = self.showListAtLevelFactory(level)
            handlerName = "%sShowListAtLevel%dHandler" % (self.objType, level)
            keysymstring, modifiers, description = binding

            self.inputEventHandlers[handlerName] = \
                input_event.InputEventHandler(handler, description)

            self.keyBindings.add(
                keybindings.KeyBinding(
                    keysymstring,
                    keybindings.defaultModifierMask,
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
                    keybindings.defaultModifierMask,
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
                         keybindings.defaultModifierMask,
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

    def showList(self, script, inputEvent):
        """Show a list of all the items with this object type."""

        try:
            objects, criteria = self.structuralNavigation._getAll(self)
        except:
            script.presentMessage(messages.NAVIGATION_DIALOG_ERROR)
            return

        def _isValidMatch(x):
            return not (script.utilities.isHidden(x) or script.utilities.isEmpty(x))

        objects = list(filter(_isValidMatch, objects))
        if criteria.applyPredicate:
            objects = list(filter(self.predicate, objects))

        title, columnHeaders, rowData = self._dialogData()
        count = len(objects)
        title = "%s: %s" % (title, messages.itemsFound(count))
        if not count:
            script.presentMessage(title)
            return

        currentObject, offset = script.utilities.getCaretContext()
        try:
            index = objects.index(currentObject)
        except:
            index = 0

        rows = [[obj, -1] + rowData(obj) for obj in objects]
        orca_gui_navlist.showUI(title, columnHeaders, rows, index)

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

    def showListAtLevelFactory(self, level):
        """Generates a showList method for the specified level. Right
        now, this is just for headings, but it may have applicability
        for other objects such as list items (i.e. for level-based
        navigation in an outline or other multi-tiered list.

        Arguments:
        - level: the desired level of the object as an int.
        """

        def showListAtLevel(script, inputEvent):
            try:
                objects, criteria = self.structuralNavigation._getAll(self, arg=level)
            except:
                script.presentMessage(messages.NAVIGATION_DIALOG_ERROR)
                return

            def _isValidMatch(x):
                return not (script.utilities.isHidden(x) or script.utilities.isEmpty(x))

            objects = list(filter(_isValidMatch, objects))
            if criteria.applyPredicate:
                objects = list(filter(self.predicate, objects))

            title, columnHeaders, rowData = self._dialogData(arg=level)
            count = len(objects)
            title = "%s: %s" % (title, messages.itemsFound(count))
            if not count:
                script.presentMessage(title)
                return

            currentObject, offset = script.utilities.getCaretContext()
            try:
                index = objects.index(currentObject)
            except:
                index = 0

            rows = [[obj, -1] + rowData(obj) for obj in objects]
            orca_gui_navlist.showUI(title, columnHeaders, rows, index)

        return showListAtLevel

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
            obj, offset = script.utilities.getCaretContext()
            thisCell = self.structuralNavigation.getCellForObj(obj)
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
                script.liveRegionManager.goLastLiveRegion()
            else:
                script.presentMessage(messages.LIVE_REGIONS_OFF)

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
    BLOCKQUOTE      = "blockquote"
    BUTTON          = "button"
    CHECK_BOX       = "checkBox"
    CHUNK           = "chunk"
    CLICKABLE       = "clickable"
    COMBO_BOX       = "comboBox"
    ENTRY           = "entry"
    FORM_FIELD      = "formField"
    HEADING         = "heading"
    IMAGE           = "image"
    LANDMARK        = "landmark"
    LINK            = "link"
    LIST            = "list"        # Bulleted/numbered lists
    LIST_ITEM       = "listItem"    # Bulleted/numbered list items
    LIVE_REGION     = "liveRegion"
    PARAGRAPH       = "paragraph"
    RADIO_BUTTON    = "radioButton"
    SEPARATOR       = "separator"
    TABLE           = "table"
    TABLE_CELL      = "tableCell"
    UNVISITED_LINK  = "unvisitedLink"
    VISITED_LINK    = "visitedLink"

    # Roles which are recognized as being a form field. Note that this
    # is for the purpose of match rules and predicates and refers to
    # AT-SPI roles. 
    #
    FORM_ROLES = [pyatspi.ROLE_CHECK_BOX,
                  pyatspi.ROLE_RADIO_BUTTON,
                  pyatspi.ROLE_COMBO_BOX,
                  pyatspi.ROLE_DOCUMENT_FRAME, # rich text editing
                  pyatspi.ROLE_LIST,
                  pyatspi.ROLE_LIST_BOX,
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
                    pyatspi.ROLE_DOCUMENT_EMAIL,
                    pyatspi.ROLE_DOCUMENT_FRAME,
                    pyatspi.ROLE_DOCUMENT_PRESENTATION,
                    pyatspi.ROLE_DOCUMENT_SPREADSHEET,
                    pyatspi.ROLE_DOCUMENT_TEXT,
                    pyatspi.ROLE_DOCUMENT_WEB]

    IMAGE_ROLES = [pyatspi.ROLE_IMAGE,
                   pyatspi.ROLE_IMAGE_MAP]

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

        self._objectCache = {}

    def clearCache(self, document=None):
        if document:
            self._objectCache[hash(document)] = {}
        else:
            self._objectCache = {}

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
        criteria = eval("self._%sCriteria" % name)
        predicate = eval("self._%sPredicate" % name)
        presentation = eval("self._%sPresentation" % name)

        try:
            dialogData = eval("self._%sDialogData" % name)
        except:
            dialogData = None

        return StructuralNavigationObject(self, name, bindings, predicate,
                                          criteria, presentation, dialogData)

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
                cmdnames.STRUCTURAL_NAVIGATION_TOGGLE)

        for structuralNavigationObject in list(self.enabledObjects.values()):
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
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
                self.inputEventHandlers["toggleStructuralNavigationHandler"]))

        for structuralNavigationObject in list(self.enabledObjects.values()):
            bindings = structuralNavigationObject.keyBindings.keyBindings
            for keybinding in bindings:
                keyBindings.add(keybinding)

        return keyBindings

    #########################################################################
    #                                                                       #
    # Input Event Handler Methods                                           #
    #                                                                       #
    #########################################################################

    def toggleStructuralNavigation(self, script, inputEvent, presentMessage=True):
        """Toggles structural navigation keys."""

        self.enabled = not self.enabled

        if self.enabled:
            string = messages.STRUCTURAL_NAVIGATION_KEYS_ON
        else:
            string = messages.STRUCTURAL_NAVIGATION_KEYS_OFF

        debug.println(debug.LEVEL_CONFIGURATION, string)
        if presentMessage:
            self._script.presentMessage(string)

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
            self._script.presentMessage(messages.TABLE_NOT_IN_A)
            return None

        currentRow, currentCol = currentCoordinates
        desiredRow, desiredCol = desiredCoordinates
        rowDiff = desiredRow - currentRow
        colDiff = desiredCol - currentCol
        oldRowHeaders = self._script.utilities.rowHeadersForCell(thisCell)
        oldColHeaders = self._script.utilities.columnHeadersForCell(thisCell)
        cell = thisCell
        while cell:
            cell = iTable.getAccessibleAt(desiredRow, desiredCol)
            if not cell:
                if desiredCol < 0:
                    self._script.presentMessage(messages.TABLE_ROW_BEGINNING)
                    desiredCol = 0
                elif desiredCol > iTable.nColumns - 1:
                    self._script.presentMessage(messages.TABLE_ROW_END)
                    desiredCol = iTable.nColumns - 1
                if desiredRow < 0:
                    self._script.presentMessage(messages.TABLE_COLUMN_TOP)
                    desiredRow = 0
                elif desiredRow > iTable.nRows - 1:
                    self._script.presentMessage(messages.TABLE_COLUMN_BOTTOM)
                    desiredRow = iTable.nRows - 1
            elif thisCell == cell or (settings.skipBlankCells and self._isBlankCell(cell)):
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

    def _getAll(self, structuralNavigationObject, arg=None):
        """Returns all the instances of structuralNavigationObject."""
        if not structuralNavigationObject.criteria:
            return [], None

        document = self._script.utilities.documentFrame()
        cache = self._objectCache.get(hash(document), {})
        key = "%s:%s" % (structuralNavigationObject.objType, arg)
        matches, criteria = cache.get(key, ([], None))
        if matches:
            return matches.copy(), criteria

        col = document.queryCollection()
        criteria = structuralNavigationObject.criteria(col, arg)
        rule = col.createMatchRule(criteria.states.raw(),
                                   criteria.matchStates,
                                   criteria.objAttrs,
                                   criteria.matchObjAttrs,
                                   criteria.roles,
                                   criteria.matchRoles,
                                   criteria.interfaces,
                                   criteria.matchInterfaces,
                                   criteria.invert)
        matches = col.getMatches(rule, col.SORT_ORDER_CANONICAL, 0, True)
        col.freeMatchRule(rule)

        rv = matches.copy(), criteria
        cache[key] = matches, criteria
        self._objectCache[hash(document)] = cache
        return rv

    def goObject(self, structuralNavigationObject, isNext, obj=None, arg=None):
        """The method used for navigation among StructuralNavigationObjects
        which are not table cells.

        Arguments:
        - structuralNavigationObject: the StructuralNavigationObject which
          represents the object of interest.
        - isNext: If True, we're interested in the next accessible object
          which matches structuralNavigationObject.  If False, we're 
          interested in the previous accessible object which matches.
        - obj: the current object (typically the locusOfFocus).
        - arg: optional arguments which may need to be passed along to
          the predicate, presentation method, etc. For instance, in the
          case of navigating amongst headings at a given level, the level
          is needed and passed in as arg.
        """

        matches, criteria = list(self._getAll(structuralNavigationObject, arg))
        if not matches:
            structuralNavigationObject.present(None, arg)
            return

        if not isNext:
            matches.reverse()

        def _isValidMatch(obj):
            if self._script.utilities.isHidden(obj) or self._script.utilities.isEmpty(obj):
                return False
            if not criteria.applyPredicate:
                return True
            return structuralNavigationObject.predicate(obj)

        def _getMatchingObjAndIndex(obj):
            while obj:
                if obj in matches:
                    return obj, matches.index(obj)
                obj = obj.parent

            return None, -1

        if not obj:
            obj, offset = self._script.utilities.getCaretContext()
        thisObj, index = _getMatchingObjAndIndex(obj)
        if thisObj:
            matches = matches[index:]
            obj = thisObj

        currentPath = pyatspi.utils.getPath(obj)
        for i, match in enumerate(matches):
            if not _isValidMatch(match):
                continue

            if match.parent == obj:
                comparison = self._script.utilities.characterOffsetInParent(match) - offset
            else:
                path = pyatspi.utils.getPath(match)
                comparison = self._script.utilities.pathComparison(path, currentPath)
            if (comparison > 0 and isNext) or (comparison < 0 and not isNext):
                structuralNavigationObject.present(match, arg)
                return

        if not settings.wrappedStructuralNavigation:
            structuralNavigationObject.present(None, arg)
            return

        if not isNext:
            self._script.presentMessage(messages.WRAPPING_TO_BOTTOM)
        else:
            self._script.presentMessage(messages.WRAPPING_TO_TOP)

        matches, criteria = list(self._getAll(structuralNavigationObject, arg))
        if not isNext:
            matches.reverse()

        for match in matches:
            if _isValidMatch(match):
                structuralNavigationObject.present(match, arg)
                return

        structuralNavigationObject.present(None, arg)

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
            return self._script.utilities.displayedText(caption)

    def _getTableDescription(self, obj):
        """Returns a string which describes the table."""

        nonUniformString = ""
        nonUniform = self._script.utilities.isNonUniformTable(obj)
        if nonUniform:
            nonUniformString = messages.TABLE_NON_UNIFORM + " "

        table = obj.queryTable()
        sizeString = messages.tableSize(table.nRows, table.nColumns)
        return (nonUniformString + sizeString)

    def getCellForObj(self, obj):
        """Looks for a table cell in the ancestry of obj, if obj is not a
        table cell.

        Arguments:
        - obj: the accessible object of interest.
        """

        cellRoles = [pyatspi.ROLE_TABLE_CELL,
                     pyatspi.ROLE_COLUMN_HEADER,
                     pyatspi.ROLE_ROW_HEADER]
        isCell = lambda x: x and x.getRole() in cellRoles
        if obj and not isCell(obj):
            obj = pyatspi.utils.findAncestor(obj, isCell)

        return obj

    def getTableForCell(self, obj):
        """Looks for a table in the ancestry of obj, if obj is not a table.

        Arguments:
        - obj: the accessible object of interest.
        """

        isTable = lambda x: x and x.getRole() == pyatspi.ROLE_TABLE
        if obj and not isTable(obj):
            obj = pyatspi.utils.findAncestor(obj, isTable)

        return obj

    def _isBlankCell(self, obj):
        """Returns True if the table cell is empty or consists of whitespace.

        Arguments:
        - obj: the accessible table cell to examime
        """

        if obj and (obj.name or obj.childCount):
            return False

        try:
            text = obj.queryText()
        except:
            pass
        else:
            if text.getText(0, -1).strip():
                return False

        return True

    def _getCellText(self, obj):
        """Looks at the table cell and tries to get its text.

        Arguments:
        - obj: the accessible table cell to examime
        """

        text = ""
        if obj and not obj.childCount:
            text = self._script.utilities.displayedText(obj)
        else:
            for child in obj:
                childText = self._script.utilities.displayedText(child)
                text = self._script.utilities.appendString(text, childText)

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

        if rowDiff:
            rowHeaders = self._script.utilities.rowHeadersForCell(cell)
            for header in rowHeaders:
                if not header in oldRowHeaders:
                    text = self._getCellText(header)
                    speech.speak(text)

        if colDiff:
            colHeaders = self._script.utilities.columnHeadersForCell(cell)
            for header in colHeaders:
                if not header in oldColHeaders:
                    text = self._getCellText(header)
                    speech.speak(text)

    def getCellCoordinates(self, obj):
        """Returns the [row, col] of a ROLE_TABLE_CELL or [-1, -1]
        if the coordinates cannot be found.

        Arguments:
        - obj: the accessible table cell whose coordinates we want.
        """

        cell = self.getCellForObj(obj)
        table = self.getTableForCell(cell)
        thisRow, thisCol = self._script.utilities.coordinatesForCell(cell)

        # If we're in a cell that spans multiple rows and/or columns,
        # thisRow and thisCol will refer to the upper left cell in
        # the spanned range(s).  We're storing the lastTableCell that
        # we're aware of in order to facilitate more linear movement.
        # Therefore, if the lastTableCell and this table cell are the
        # same cell, we'll go with the stored coordinates.
        lastRow, lastCol = self.lastTableCell
        lastCell = self._script.utilities.cellForCoordinates(table, lastRow, lastCol)
        if lastCell == cell:
            return lastRow, lastCol

        return thisRow, thisCol

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
        """Sets the caret at the specified offset within obj."""

        self._script.utilities.setCaretPosition(obj, characterOffset)

    def _presentLine(self, obj, offset):
        """Presents the first line of the object to the user.

        Arguments:
        - obj: the accessible object to be presented.
        - offset: the character offset within obj.
        """

        if not obj:
            return

        if self._presentWithSayAll(obj, offset):
            return

        self._script.updateBraille(obj)
        self._script.sayLine(obj)

    def _presentObject(self, obj, offset):
        """Presents the entire object to the user.

        Arguments:
        - obj: the accessible object to be presented.
        - offset: the character offset within obj.
        """

        if not obj:
            return

        if self._presentWithSayAll(obj, offset):
            return

        self._script.presentObject(obj, offset)

    def _presentWithSayAll(self, obj, offset):
        if self._script.inSayAll() \
           and _settingsManager.getSetting('structNavInSayAll'):
            self._script.sayAll(obj, offset)
            return True

        return False

    def _getRoleName(self, obj):
        # Another case where we'll do this for now, and clean it up when
        # object presentation is refactored.
        return self._script.speechGenerator.getLocalizedRoleName(obj)

    def _getSelectedItem(self, obj):
        # Another case where we'll do this for now, and clean it up when
        # object presentation is refactored.
        if obj.getRole() == pyatspi.ROLE_COMBO_BOX:
            obj = obj[0]
        try:
            selection = obj.querySelection()
        except NotImplementedError:
            return None

        return selection.getSelectedChild(0)

    def _getText(self, obj):
        # Another case where we'll do this for now, and clean it up when
        # object presentation is refactored.
        text = self._script.utilities.displayedText(obj)
        if not text:
            text = self._script.utilities.expandEOCs(obj)
        if not text:
            item = self._getSelectedItem(obj)
            if item:
                text = item.name
        if not text and obj.getRole() == pyatspi.ROLE_IMAGE:
            try:
                image = obj.queryImage()
            except:
                text = obj.description
            else:
                text = image.imageDescription or obj.description
            if not text and obj.parent.getRole() == pyatspi.ROLE_LINK:
                text = self._script.utilities.linkBasename(obj.parent)
        if not text and obj.getRole() == pyatspi.ROLE_LIST:
            children = [x for x in obj if x.getRole() == pyatspi.ROLE_LIST_ITEM]
            text = " ".join(list(map(self._getText, children)))

        return text

    def _getLabel(self, obj):
        # Another case where we'll do this for now, and clean it up when
        # object presentation is refactored.
        label = self._script.utilities.displayedLabel(obj)
        if not label:
            label, objects = self._script.labelInference.infer(
                obj, focusedOnly=False)

        return label

    def _getState(self, obj):
        # Another case where we'll do this for now, and clean it up when
        # object presentation is refactored.
        try:
            state = obj.getState()
            role = obj.getRole()
        except RuntimeError:
            return ''

        # For now, we'll just grab the spoken indicator from settings.
        # When object presentation is refactored, we can clean this up.
        if role == pyatspi.ROLE_CHECK_BOX:
            unchecked, checked, partially = object_properties.CHECK_BOX_INDICATORS_SPEECH
            if state.contains(pyatspi.STATE_INDETERMINATE):
                return partially
            if state.contains(pyatspi.STATE_CHECKED):
                return checked
            return unchecked

        if role == pyatspi.ROLE_RADIO_BUTTON:
            unselected, selected = object_properties.RADIO_BUTTON_INDICATORS_SPEECH
            if state.contains(pyatspi.STATE_CHECKED):
                return selected
            return unselected

        if role == pyatspi.ROLE_LINK:
            if state.contains(pyatspi.STATE_VISITED):
                return object_properties.STATE_VISITED
            else:
                return object_properties.STATE_UNVISITED

        return ''

    def _getValue(self, obj):
        # Another case where we'll do this for now, and clean it up when
        # object presentation is refactored.
        return self._getState(obj) or self._getText(obj)

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
    # Blockquotes          #
    #                      #
    ########################

    def _blockquoteBindings(self):
        """Returns a dictionary of [keysymstring, modifiers, description]
        lists for navigating among blockquotes.
        """

        bindings = {}
        prevDesc = cmdnames.BLOCKQUOTE_PREV
        bindings["previous"] = ["q", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.BLOCKQUOTE_NEXT
        bindings["next"] = ["q", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.BLOCKQUOTE_LIST
        bindings["list"] = ["q", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]
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
            self._presentObject(obj, characterOffset)
        else:
            full = messages.NO_MORE_BLOCKQUOTES
            brief = messages.STRUCTURAL_NAVIGATION_NOT_FOUND
            self._script.presentMessage(full, brief)

    def _blockquoteDialogData(self):
        columnHeaders = [guilabels.SN_HEADER_BLOCKQUOTE]

        def rowData(obj):
            return [self._getText(obj)]

        return guilabels.SN_TITLE_BLOCKQUOTE, columnHeaders, rowData

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
        prevDesc = cmdnames.BUTTON_PREV
        bindings["previous"] = ["b", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.BUTTON_NEXT
        bindings["next"] = ["b", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.BUTTON_LIST
        bindings["list"] = ["b", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]
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
            [obj, characterOffset] = self._getCaretPosition(obj)
            self._setCaretPosition(obj, characterOffset)
            self._presentObject(obj, characterOffset)
        else:
            full = messages.NO_MORE_BUTTONS
            brief = messages.STRUCTURAL_NAVIGATION_NOT_FOUND
            self._script.presentMessage(full, brief)

    def _buttonDialogData(self):
        columnHeaders = [guilabels.SN_HEADER_BUTTON]

        def rowData(obj):
            return [self._getText(obj)]

        return guilabels.SN_TITLE_BUTTON, columnHeaders, rowData

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
        prevDesc = cmdnames.CHECK_BOX_PREV
        bindings["previous"] = ["x", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.CHECK_BOX_NEXT
        bindings["next"] = ["x", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.CHECK_BOX_LIST
        bindings["list"] = ["x", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]
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
            [obj, characterOffset] = self._getCaretPosition(obj)
            self._setCaretPosition(obj, characterOffset)
            self._presentObject(obj, characterOffset)
        else:
            full = messages.NO_MORE_CHECK_BOXES
            brief = messages.STRUCTURAL_NAVIGATION_NOT_FOUND
            self._script.presentMessage(full, brief)

    def _checkBoxDialogData(self):
        columnHeaders = [guilabels.SN_HEADER_CHECK_BOX]
        columnHeaders.append(guilabels.SN_HEADER_STATE)

        def rowData(obj):
            return [self._getLabel(obj), self._getState(obj)]

        return guilabels.SN_TITLE_CHECK_BOX, columnHeaders, rowData

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
        prevDesc = cmdnames.LARGE_OBJECT_PREV
        bindings["previous"] = ["o", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.LARGE_OBJECT_NEXT
        bindings["next"] = ["o", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.LARGE_OBJECT_LIST
        bindings["list"] = ["o", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]
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

        if obj and obj.getRole() in self.OBJECT_ROLES:
            text = self._script.utilities.queryNonEmptyText(obj)
            if not (text and text.characterCount > settings.largeObjectTextLength):
                return False

            string = text.getText(0, -1)
            eocs = string.count(self._script.EMBEDDED_OBJECT_CHARACTER)
            if eocs/text.characterCount < 0.05:
                return True

        return False

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
            full = messages.NO_MORE_CHUNKS
            brief = messages.STRUCTURAL_NAVIGATION_NOT_FOUND
            self._script.presentMessage(full, brief)

    def _chunkDialogData(self):
        columnHeaders = [guilabels.SN_HEADER_OBJECT]
        columnHeaders.append(guilabels.SN_HEADER_ROLE)

        def rowData(obj):
            return [self._getText(obj), self._getRoleName(obj)]

        return guilabels.SN_TITLE_LARGE_OBJECT, columnHeaders, rowData

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
        prevDesc = cmdnames.COMBO_BOX_PREV
        bindings["previous"] = ["c", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.COMBO_BOX_NEXT
        bindings["next"] = ["c", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.COMBO_BOX_LIST
        bindings["list"] = ["c", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]
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
            [obj, characterOffset] = self._getCaretPosition(obj)
            self._setCaretPosition(obj, characterOffset)
            self._presentObject(obj, characterOffset)
        else:
            full = messages.NO_MORE_COMBO_BOXES
            brief = messages.STRUCTURAL_NAVIGATION_NOT_FOUND
            self._script.presentMessage(full, brief)

    def _comboBoxDialogData(self):
        columnHeaders = [guilabels.SN_HEADER_COMBO_BOX]
        columnHeaders.append(guilabels.SN_HEADER_SELECTED_ITEM)

        def rowData(obj):
            return [self._getLabel(obj), self._getText(obj)]

        return guilabels.SN_TITLE_COMBO_BOX, columnHeaders, rowData

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
        prevDesc = cmdnames.ENTRY_PREV
        bindings["previous"] = ["e", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.ENTRY_NEXT
        bindings["next"] = ["e", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.ENTRY_LIST
        bindings["list"] = ["e", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]
        return bindings

    def _entryCriteria(self, collection, arg=None):
        """Returns the MatchCriteria to be used for locating entries
        by collection.

        Arguments:
        - collection: the collection interface for the document
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        role = [pyatspi.ROLE_DOCUMENT_FRAME,
                pyatspi.ROLE_ENTRY,
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
                             matchRoles=roleMatch,
                             applyPredicate=True)

    def _entryPredicate(self, obj, arg=None):
        """The predicate to be used for verifying that the object
        obj is an entry.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        isMatch = False
        if obj and obj.getRole() in [pyatspi.ROLE_DOCUMENT_FRAME,
                                     pyatspi.ROLE_ENTRY,
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
            [obj, characterOffset] = self._getCaretPosition(obj)
            self._setCaretPosition(obj, characterOffset)
            self._presentObject(obj, characterOffset)
        else:
            full = messages.NO_MORE_ENTRIES
            brief = messages.STRUCTURAL_NAVIGATION_NOT_FOUND
            self._script.presentMessage(full, brief)

    def _entryDialogData(self):
        columnHeaders = [guilabels.SN_HEADER_LABEL]
        columnHeaders.append(guilabels.SN_HEADER_TEXT)

        def rowData(obj):
            return [self._getLabel(obj), self._getText(obj)]

        return guilabels.SN_TITLE_ENTRY, columnHeaders, rowData

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
        prevDesc = cmdnames.FORM_FIELD_PREV
        bindings["previous"] = ["Tab",
                                keybindings.ORCA_SHIFT_MODIFIER_MASK,
                                prevDesc]

        nextDesc = cmdnames.FORM_FIELD_NEXT
        bindings["next"] = ["Tab", keybindings.ORCA_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.FORM_FIELD_LIST
        bindings["list"] = ["f", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]
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
                             matchRoles=roleMatch,
                             applyPredicate=True)

    def _formFieldPredicate(self, obj, arg=None):
        """The predicate to be used for verifying that the object
        obj is a form field.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        if not obj:
            return False

        role = obj.getRole()
        if not role in self.FORM_ROLES:
            return False

        state = obj.getState()
        isMatch = state.contains(pyatspi.STATE_FOCUSABLE) \
                  and state.contains(pyatspi.STATE_SENSITIVE)

        if role == pyatspi.ROLE_DOCUMENT_FRAME:
            isMatch = isMatch and state.contains(pyatspi.STATE_EDITABLE)

        return isMatch

    def _formFieldPresentation(self, obj, arg=None):
        """Presents the form field or indicates that one was not found.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        if obj:
            if obj.getRole() == pyatspi.ROLE_TEXT and obj.childCount:
                obj = obj[0]
            [obj, characterOffset] = self._getCaretPosition(obj)
            self._setCaretPosition(obj, characterOffset)
            self._presentObject(obj, characterOffset)
        else:
            full = messages.NO_MORE_FORM_FIELDS
            brief = messages.STRUCTURAL_NAVIGATION_NOT_FOUND
            self._script.presentMessage(full, brief)

    def _formFieldDialogData(self):
        columnHeaders = [guilabels.SN_HEADER_LABEL]
        columnHeaders.append(guilabels.SN_HEADER_ROLE)
        columnHeaders.append(guilabels.SN_HEADER_VALUE)

        def rowData(obj):
            return [self._getLabel(obj),
                    self._getRoleName(obj),
                    self._getValue(obj)]

        return guilabels.SN_TITLE_FORM_FIELD, columnHeaders, rowData

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
        prevDesc = cmdnames.HEADING_PREV
        bindings["previous"] = ["h", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.HEADING_NEXT
        bindings["next"] = ["h", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.HEADING_LIST
        bindings["list"] = ["h", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]

        prevAtLevelBindings = []
        nextAtLevelBindings = []
        listAtLevelBindings = []
        minLevel, maxLevel = self._headingLevels()
        for i in range(minLevel, maxLevel + 1):
            prevDesc = cmdnames.HEADING_AT_LEVEL_PREV % i
            prevAtLevelBindings.append([str(i),
                                        keybindings.SHIFT_MODIFIER_MASK,
                                        prevDesc])

            nextDesc = cmdnames.HEADING_AT_LEVEL_NEXT % i
            nextAtLevelBindings.append([str(i),
                                        keybindings.NO_MODIFIER_MASK,
                                        nextDesc])

            listDesc = cmdnames.HEADING_AT_LEVEL_LIST %i
            listAtLevelBindings.append([str(i),
                                        keybindings.SHIFT_ALT_MODIFIER_MASK,
                                        listDesc])

        bindings["previousAtLevel"] = prevAtLevelBindings
        bindings["nextAtLevel"] = nextAtLevelBindings
        bindings["listAtLevel"] = listAtLevelBindings

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
                isMatch = arg == self._script.utilities.headingLevel(obj)
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
            full = messages.NO_MORE_HEADINGS
            brief = messages.STRUCTURAL_NAVIGATION_NOT_FOUND
            self._script.presentMessage(full, brief)
        else:
            full = messages.NO_MORE_HEADINGS_AT_LEVEL % arg
            brief = messages.STRUCTURAL_NAVIGATION_NOT_FOUND
            self._script.presentMessage(full, brief)

    def _headingDialogData(self, arg=None):
        columnHeaders = [guilabels.SN_HEADER_HEADING]

        if not arg:
            title = guilabels.SN_TITLE_HEADING
            columnHeaders.append(guilabels.SN_HEADER_LEVEL)

            def rowData(obj):
                return [self._getText(obj),
                        str(self._script.utilities.headingLevel(obj))]

        else:
            title = guilabels.SN_TITLE_HEADING_AT_LEVEL % arg

            def rowData(obj):
                return [self._getText(obj)]

        return title, columnHeaders, rowData

    ########################
    #                      #
    # Images               #
    #                      #
    ########################

    def _imageBindings(self):
        """Returns a dictionary of [keysymstring, modifiers, description]
        lists for navigating amongst images."""

        bindings = {}
        prevDesc = cmdnames.IMAGE_PREV
        bindings["previous"] = ["g", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.IMAGE_NEXT
        bindings["next"] = ["g", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.IMAGE_LIST
        bindings["list"] = ["g", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]
        return bindings

    def _imageCriteria(self, collection, arg=None):
        """Returns the MatchCriteria to be used for locating images
        by collection.

        Arguments:
        - collection: the collection interface for the document
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        return MatchCriteria(collection, roles=self.IMAGE_ROLES)

    def _imagePredicate(self, obj, arg=None):
        """The predicate to be used for verifying that the object
        obj is an image.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        return (obj and obj.getRole() in self.IMAGE_ROLES)

    def _imagePresentation(self, obj, arg=None):
        """Presents the image/graphic or indicates that one was not found.

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
            full = messages.NO_MORE_IMAGES
            brief = messages.STRUCTURAL_NAVIGATION_NOT_FOUND
            self._script.presentMessage(full, brief)

    def _imageDialogData(self):
        columnHeaders = [guilabels.SN_HEADER_IMAGE]

        def rowData(obj):
            return [self._getText(obj) or self._getRoleName(obj)]

        return guilabels.SN_TITLE_IMAGE, columnHeaders, rowData

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
        prevDesc = cmdnames.LANDMARK_PREV
        bindings["previous"] = ["m", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.LANDMARK_NEXT
        bindings["next"] = ["m", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.LANDMARK_LIST
        bindings["list"] = ["m", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]
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
            if set(attrs['xml-roles']).intersection(\
                set(settings.ariaLandmarks)):
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
            full = messages.NO_LANDMARK_FOUND
            brief = messages.STRUCTURAL_NAVIGATION_NOT_FOUND
            self._script.presentMessage(full, brief)

    def _landmarkDialogData(self):
        columnHeaders = [guilabels.SN_HEADER_LANDMARK]
        columnHeaders.append(guilabels.SN_HEADER_ROLE)

        def rowData(obj):
            return [self._getText(obj), self._getRoleName(obj)]

        return guilabels.SN_TITLE_LANDMARK, columnHeaders, rowData

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
        prevDesc = cmdnames.LIST_PREV
        bindings["previous"] = ["l", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.LIST_NEXT
        bindings["next"] = ["l", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.LIST_LIST
        bindings["list"] = ["l", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]
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

        if obj:
            speech.speak(self._script.speechGenerator.generateSpeech(obj))
            [obj, characterOffset] = self._getCaretPosition(obj)
            self._setCaretPosition(obj, characterOffset)
            self._presentLine(obj, characterOffset)
        else:
            full = messages.NO_MORE_LISTS
            brief = messages.STRUCTURAL_NAVIGATION_NOT_FOUND
            self._script.presentMessage(full, brief)

    def _listDialogData(self):
        columnHeaders = [guilabels.SN_HEADER_LIST]

        def rowData(obj):
            return [self._getText(obj)]

        return guilabels.SN_TITLE_LIST, columnHeaders, rowData

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
        prevDesc = cmdnames.LIST_ITEM_PREV
        bindings["previous"] = ["i", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.LIST_ITEM_NEXT
        bindings["next"] = ["i", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.LIST_ITEM_LIST
        bindings["list"] = ["i", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]
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
            self._presentLine(obj, characterOffset)
        else:
            full = messages.NO_MORE_LIST_ITEMS
            brief = messages.STRUCTURAL_NAVIGATION_NOT_FOUND
            self._script.presentMessage(full, brief)

    def _listItemDialogData(self):
        columnHeaders = [guilabels.SN_HEADER_LIST_ITEM]

        def rowData(obj):
            return [self._getText(obj)]

        return guilabels.SN_TITLE_LIST_ITEM, columnHeaders, rowData

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
        prevDesc = cmdnames.LIVE_REGION_PREV
        bindings["previous"] = ["d", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.LIVE_REGION_NEXT
        bindings["next"] = ["d", keybindings.NO_MODIFIER_MASK, nextDesc]

        desc = cmdnames.LIVE_REGION_LAST
        bindings["last"] = ["y", keybindings.NO_MODIFIER_MASK, desc]
        return bindings

    def _liveRegionCriteria(self, collection, arg=None):
        """Returns the MatchCriteria to be used for locating live regions
        by collection.

        Arguments:
        - collection: the collection interface for the document
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        # Matches based on object attributes assume unique name-value pairs
        # because pyatspi creates a dictionary from the list. In addition,
        # wildcard matching is not possible. As a result, we cannot search
        # for any object which has an attribute named container-live.
        return MatchCriteria(collection, applyPredicate=True)

    def _liveRegionPredicate(self, obj, arg=None):
        """The predicate to be used for verifying that the object
        obj is a live region.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        isMatch = False

        regobjs = self._script.liveRegionManager.getLiveNoneObjects()
        if self._script.liveRegionManager.matchLiveRegion(obj) or obj in regobjs:
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
            [obj, characterOffset] = self._getCaretPosition(obj)
            self._setCaretPosition(obj, characterOffset)
            self._presentObject(obj, characterOffset)
        else:
            full = messages.NO_MORE_LIVE_REGIONS
            brief = messages.STRUCTURAL_NAVIGATION_NOT_FOUND
            self._script.presentMessage(full, brief)

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
        prevDesc = cmdnames.PARAGRAPH_PREV
        bindings["previous"] = ["p", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.PARAGRAPH_NEXT
        bindings["next"] = ["p", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.PARAGRAPH_LIST
        bindings["list"] = ["p", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]
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
            full = messages.NO_MORE_PARAGRAPHS
            brief = messages.STRUCTURAL_NAVIGATION_NOT_FOUND
            self._script.presentMessage(full, brief)

    def _paragraphDialogData(self):
        columnHeaders = [guilabels.SN_HEADER_PARAGRAPH]

        def rowData(obj):
            return [self._getText(obj)]

        return guilabels.SN_TITLE_PARAGRAPH, columnHeaders, rowData

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
        prevDesc = cmdnames.RADIO_BUTTON_PREV
        bindings["previous"] = ["r", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.RADIO_BUTTON_NEXT
        bindings["next"] = ["r", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.RADIO_BUTTON_LIST
        bindings["list"] = ["r", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]
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
            [obj, characterOffset] = self._getCaretPosition(obj)
            self._setCaretPosition(obj, characterOffset)
            self._presentObject(obj, characterOffset)
        else:
            full = messages.NO_MORE_RADIO_BUTTONS
            brief = messages.STRUCTURAL_NAVIGATION_NOT_FOUND
            self._script.presentMessage(full, brief)

    def _radioButtonDialogData(self):
        columnHeaders = [guilabels.SN_HEADER_RADIO_BUTTON]
        columnHeaders.append(guilabels.SN_HEADER_STATE)

        def rowData(obj):
            return [self._getLabel(obj), self._getState(obj)]

        return guilabels.SN_TITLE_RADIO_BUTTON, columnHeaders, rowData

    ########################
    #                      #
    # Separators           #
    #                      #
    ########################

    def _separatorBindings(self):
        """Returns a dictionary of [keysymstring, modifiers, description]
        lists for navigating amongst separators.
        """

        bindings = {}
        prevDesc = cmdnames.SEPARATOR_PREV
        bindings["previous"] = ["s", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.SEPARATOR_NEXT
        bindings["next"] = ["s", keybindings.NO_MODIFIER_MASK, nextDesc]
        return bindings

    def _separatorCriteria(self, collection, arg=None):
        """Returns the MatchCriteria to be used for locating separators
        by collection.

        Arguments:
        - collection: the collection interface for the document
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        role = [pyatspi.ROLE_SEPARATOR]
        return MatchCriteria(collection, roles=role, applyPredicate=False)

    def _separatorPredicate(self, obj, arg=None):
        """The predicate to be used for verifying that the object
        obj is a separator.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        return obj and obj.getRole() == pyatspi.ROLE_SEPARATOR

    def _separatorPresentation(self, obj, arg=None):
        """Presents the separator or indicates that one was not found.

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
            full = messages.NO_MORE_SEPARATORS
            brief = messages.STRUCTURAL_NAVIGATION_NOT_FOUND
            self._script.presentMessage(full, brief)

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
        prevDesc = cmdnames.TABLE_PREV
        bindings["previous"] = ["t", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.TABLE_NEXT
        bindings["next"] = ["t", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.TABLE_LIST
        bindings["list"] = ["t", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]
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

        if not (obj and obj.childCount and obj.getRole() == pyatspi.ROLE_TABLE):
            return False

        try:
            attrs = dict([attr.split(':', 1) for attr in obj.getAttributes()])
        except:
            return False
        if attrs.get('layout-guess') == 'true':
            return False

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
                self._script.presentMessage(caption)
            self._script.presentMessage(self._getTableDescription(obj))
            cell = obj.queryTable().getAccessibleAt(0, 0)
            self.lastTableCell = [0, 0]
            self._presentObject(cell, 0)
            [cell, characterOffset] = self._getCaretPosition(cell)
            self._setCaretPosition(cell, characterOffset)
        else:
            full = messages.NO_MORE_TABLES
            brief = messages.STRUCTURAL_NAVIGATION_NOT_FOUND
            self._script.presentMessage(full, brief)

    def _tableDialogData(self):
        columnHeaders = [guilabels.SN_HEADER_CAPTION]
        columnHeaders.append(guilabels.SN_HEADER_DESCRIPTION)

        def rowData(obj):
            return [self._getTableCaption(obj) or '',
                    self._getTableDescription(obj)]

        return guilabels.SN_TITLE_TABLE, columnHeaders, rowData

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
        desc = cmdnames.TABLE_CELL_LEFT
        bindings["left"] = ["Left", keybindings.SHIFT_ALT_MODIFIER_MASK, desc]

        desc = cmdnames.TABLE_CELL_RIGHT
        bindings["right"] = ["Right", keybindings.SHIFT_ALT_MODIFIER_MASK, desc]

        desc = cmdnames.TABLE_CELL_UP
        bindings["up"] = ["Up", keybindings.SHIFT_ALT_MODIFIER_MASK, desc]

        desc = cmdnames.TABLE_CELL_DOWN
        bindings["down"] = ["Down", keybindings.SHIFT_ALT_MODIFIER_MASK, desc]

        desc = cmdnames.TABLE_CELL_FIRST
        bindings["first"] = ["Home", keybindings.SHIFT_ALT_MODIFIER_MASK, desc]

        desc = cmdnames.TABLE_CELL_LAST
        bindings["last"] = ["End", keybindings.SHIFT_ALT_MODIFIER_MASK, desc]
        return bindings

    def _tableCellCriteria(self, collection, arg=None):
        """Returns the MatchCriteria to be used for locating table cells
        by collection.

        Arguments:
        - collection: the collection interface for the document
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        role = [pyatspi.ROLE_TABLE_CELL,
                pyatspi.ROLE_COLUMN_HEADER,
                pyatspi.ROLE_ROW_HEADER]
        return MatchCriteria(collection, roles=role)

    def _tableCellPredicate(self, obj, arg=None):
        """The predicate to be used for verifying that the object
        obj is a table cell.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        return (obj and obj.getRole() in [pyatspi.ROLE_COLUMN_HEADER,
                                          pyatspi.ROLE_ROW_HEADER,
                                          pyatspi.ROLE_TABLE_CELL])

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
            speech.speak(messages.BLANK)

        if settings.speakCellCoordinates:
            [row, col] = self.getCellCoordinates(cell)
            self._script.presentMessage(messages.TABLE_CELL_COORDINATES \
                                        % {"row" : row + 1, "column" : col + 1})

        rowspan, colspan = self._script.utilities.rowAndColumnSpan(cell)
        spanString = messages.cellSpan(rowspan, colspan)
        if spanString and settings.speakCellSpan:
            self._script.presentMessage(spanString)

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
        prevDesc = cmdnames.UNVISITED_LINK_PREV
        bindings["previous"] = ["u", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.UNVISITED_LINK_NEXT
        bindings["next"] = ["u", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.UNVISITED_LINK_LIST
        bindings["list"] = ["u", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]

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
                             roles=role,
                             applyPredicate=True)

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
            state = obj.getState()
            isMatch = not state.contains(pyatspi.STATE_VISITED) \
                and state.contains(pyatspi.STATE_FOCUSABLE)

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
            [obj, characterOffset] = self._getCaretPosition(obj)
            self._setCaretPosition(obj, characterOffset)
            self._presentObject(obj, characterOffset)
        else:
            full = messages.NO_MORE_UNVISITED_LINKS
            brief = messages.STRUCTURAL_NAVIGATION_NOT_FOUND
            self._script.presentMessage(full, brief)

    def _unvisitedLinkDialogData(self):
        columnHeaders = [guilabels.SN_HEADER_LINK]
        columnHeaders.append(guilabels.SN_HEADER_URI)

        def rowData(obj):
            return [self._getText(obj), self._script.utilities.uri(obj)]

        return guilabels.SN_TITLE_UNVISITED_LINK, columnHeaders, rowData

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
        prevDesc = cmdnames.VISITED_LINK_PREV
        bindings["previous"] = ["v", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.VISITED_LINK_NEXT
        bindings["next"] = ["v", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.VISITED_LINK_LIST
        bindings["list"] = ["v", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]

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
        state = [pyatspi.STATE_VISITED, pyatspi.STATE_FOCUSABLE]
        stateMatch = collection.MATCH_ALL
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
            state = obj.getState()
            isMatch = state.contains(pyatspi.STATE_VISITED) \
                and state.contains(pyatspi.STATE_FOCUSABLE)

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
            [obj, characterOffset] = self._getCaretPosition(obj)
            self._setCaretPosition(obj, characterOffset)
            self._presentObject(obj, characterOffset)
        else:
            full = messages.NO_MORE_VISITED_LINKS
            brief = messages.STRUCTURAL_NAVIGATION_NOT_FOUND
            self._script.presentMessage(full, brief)

    def _visitedLinkDialogData(self):
        columnHeaders = [guilabels.SN_HEADER_LINK]
        columnHeaders.append(guilabels.SN_HEADER_URI)

        def rowData(obj):
            return [self._getText(obj), self._script.utilities.uri(obj)]

        return guilabels.SN_TITLE_VISITED_LINK, columnHeaders, rowData

    ########################
    #                      #
    # Plain ol' Links      #
    #                      #
    ########################

    def _linkBindings(self):
        """Returns a dictionary of [keysymstring, modifiers, description]
        lists for navigating amongst links.
        """

        bindings = {}
        prevDesc = cmdnames.LINK_PREV
        bindings["previous"] = ["k", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.LINK_NEXT
        bindings["next"] = ["k", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.LINK_LIST
        bindings["list"] = ["k", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]
        return bindings

    def _linkCriteria(self, collection, arg=None):
        """Returns the MatchCriteria to be used for locating unvisited links
        by collection.

        Arguments:
        - collection: the collection interface for the document
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        role = [pyatspi.ROLE_LINK]
        state = [pyatspi.STATE_FOCUSABLE]
        stateMatch = collection.MATCH_ALL
        return MatchCriteria(collection,
                             states=state,
                             matchStates=stateMatch,
                             roles=role)

    def _linkPredicate(self, obj, arg=None):
        """The predicate to be used for verifying that the object
        obj is an link.

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

    def _linkPresentation(self, obj, arg=None):
        """Presents the link or indicates that one was not found.

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
            full = messages.NO_MORE_LINKS
            brief = messages.STRUCTURAL_NAVIGATION_NOT_FOUND
            self._script.presentMessage(full, brief)

    def _linkDialogData(self):
        columnHeaders = [guilabels.SN_HEADER_LINK]
        columnHeaders.append(guilabels.SN_HEADER_STATE)
        columnHeaders.append(guilabels.SN_HEADER_URI)

        def rowData(obj):
            return [self._getText(obj),
                    self._getState(obj),
                    self._script.utilities.uri(obj)]

        return guilabels.SN_TITLE_LINK, columnHeaders, rowData

    ########################
    #                      #
    # Clickables           #
    #                      #
    ########################

    def _clickableBindings(self):
        """Returns a dictionary of [keysymstring, modifiers, description]
        lists for navigating amongst "clickable" objects."""

        bindings = {}
        prevDesc = cmdnames.CLICKABLE_PREV
        bindings["previous"] = ["a", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.CLICKABLE_NEXT
        bindings["next"] = ["a", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.CLICKABLE_LIST
        bindings["list"] = ["a", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]
        return bindings

    def _clickableCriteria(self, collection, arg=None):
        """Returns the MatchCriteria to be used for locating clickables
        by collection.

        Arguments:
        - collection: the collection interface for the document
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        # TODO - JD: At the moment, matching via interface crashes Orca.
        # Until that's addressed, we'll just use the predicate approach.
        # See https://bugzilla.gnome.org/show_bug.cgi?id=734805.
        return MatchCriteria(collection,
                             applyPredicate=True)

    def _clickablePredicate(self, obj, arg=None):
        """The predicate to be used for verifying that the object
        obj is a clickable.

        Arguments:
        - obj: the accessible object under consideration.
        - arg: an optional argument which may need to be included in
          the criteria (e.g. the level of a heading).
        """

        return self._script.utilities.isClickableElement(obj)

    def _clickablePresentation(self, obj, arg=None):
        """Presents the clickable or indicates that one was not found.

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
            full = messages.NO_MORE_CLICKABLES
            brief = messages.STRUCTURAL_NAVIGATION_NOT_FOUND
            self._script.presentMessage(full, brief)

    def _clickableDialogData(self):
        columnHeaders = [guilabels.SN_HEADER_CLICKABLE]
        columnHeaders.append(guilabels.SN_HEADER_ROLE)

        def rowData(obj):
            return [self._getText(obj), self._getRoleName(obj)]

        return guilabels.SN_TITLE_CLICKABLE, columnHeaders, rowData
