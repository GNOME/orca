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

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import cmdnames
from . import debug
from . import guilabels
from . import input_event
from . import keybindings
from . import messages
from . import object_properties
from . import orca_gui_navlist
from . import orca_state
from . import settings
from . import settings_manager
from .ax_collection import AXCollection
from .ax_event_synthesizer import AXEventSynthesizer
from .ax_object import AXObject
from .ax_selection import AXSelection
from .ax_utilities import AXUtilities

_settingsManager = settings_manager.getManager()

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
                 criteria, presentation, dialogData, getter):
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
        - predicate: the method to use to verify if a given accessible
          matches this structural navigation object. Used only when the
          collection interface does not provide a way for us to specify
          needed condition(s).
        - criteria: a method which returns a MatchRule object which is used
          to find all matching objects via AtspiCollection.
        - presentation: the method which should be called after performing
          the search for the structural navigation object.
        - dialogData: the method which returns the title, column headers,
          and row data which should be included in the "list of" dialog for
          the structural navigation object.
        - getter: The function which should be used instead of the criteria
          and predicate.
        """

        self.structuralNavigation = structuralNavigation
        self.objType = objType
        self.bindings = bindings
        self.predicate = predicate
        self.criteria = criteria
        self.present = presentation
        self._dialogData = dialogData
        self.getter = getter

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
            handlerName = f"{self.objType}GoPrevious"
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
            handlerName = f"{self.objType}GoNext"
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
            handlerName = f"{self.objType}ShowList"
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
        directions["Start"]  = self.bindings.get("start")
        directions["End"]  = self.bindings.get("end")

        for direction in directions:
            binding = directions.get(direction)
            if not binding:
                continue

            handler = self.goDirectionFactory(direction)
            handlerName = f"{self.objType}Go{direction}"
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

        objects = self.structuralNavigation._getAll(self)

        def _isValidMatch(x):
            if AXObject.is_dead(x):
                return False
            return not (script.utilities.isHidden(x) or script.utilities.isEmpty(x))

        objects = list(filter(_isValidMatch, objects))

        if self.predicate is not None:
            objects = list(filter(self.predicate, objects))

        if self._dialogData is None:
            msg = "STRUCTURAL NAVIGATION: Cannot show list without dialog data"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return

        title, columnHeaders, rowData = self._dialogData()
        count = len(objects)
        title = f"{title}: {messages.itemsFound(count)}"
        if not count:
            script.presentMessage(title)
            return

        currentObject, offset = script.utilities.getCaretContext()
        try:
            index = objects.index(currentObject)
        except Exception:
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
            objects = self.structuralNavigation._getAll(self, arg=level)

            def _isValidMatch(x):
                return not (script.utilities.isHidden(x) or script.utilities.isEmpty(x))

            objects = list(filter(_isValidMatch, objects))
            if self.predicate is not None:
                objects = list(filter(self.predicate, objects))

            title, columnHeaders, rowData = self._dialogData(arg=level)
            count = len(objects)
            title = f"{title}: {messages.itemsFound(count)}"
            if not count:
                script.presentMessage(title)
                return

            currentObject, offset = script.utilities.getCaretContext()
            try:
                index = objects.index(currentObject)
            except Exception:
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
            currentCoordinates = self.structuralNavigation.getCellCoordinates(thisCell, False)
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
                    nRows, nColumns = script.utilities.rowAndColumnCount(table, False)
                    lastRow = nRows - 1
                    lastCol = nColumns - 1
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

        def goContainerEdge(script, inputEvent):
            isStart = direction == "Start"
            self.structuralNavigation.goEdge(self, isStart)

        if self.objType == StructuralNavigation.CONTAINER:
            return goContainerEdge
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
    CONTAINER       = "container"
    ENTRY           = "entry"
    FORM_FIELD      = "formField"
    HEADING         = "heading"
    IMAGE           = "image"
    IFRAME          = "iframe"
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

    # Roles which are recognized as being potential "large objects"
    # or "chunks." Note that this refers to AT-SPI roles.
    #
    OBJECT_ROLES = [Atspi.Role.HEADING,
                    Atspi.Role.LIST_ITEM,
                    Atspi.Role.MATH,
                    Atspi.Role.PARAGRAPH,
                    Atspi.Role.STATIC,
                    Atspi.Role.COLUMN_HEADER,
                    Atspi.Role.ROW_HEADER,
                    Atspi.Role.TABLE_CELL,
                    Atspi.Role.TABLE_ROW,
                    Atspi.Role.TEXT,
                    Atspi.Role.SECTION,
                    Atspi.Role.ARTICLE,
                    Atspi.Role.DESCRIPTION_TERM,
                    Atspi.Role.DESCRIPTION_VALUE,
                    Atspi.Role.DOCUMENT_EMAIL,
                    Atspi.Role.DOCUMENT_FRAME,
                    Atspi.Role.DOCUMENT_PRESENTATION,
                    Atspi.Role.DOCUMENT_SPREADSHEET,
                    Atspi.Role.DOCUMENT_TEXT,
                    Atspi.Role.DOCUMENT_WEB]

    CONTAINER_ROLES = [Atspi.Role.BLOCK_QUOTE,
                       Atspi.Role.DESCRIPTION_LIST,
                       Atspi.Role.FORM,
                       Atspi.Role.FOOTER,
                       Atspi.Role.HEADER,
                       Atspi.Role.LANDMARK,
                       Atspi.Role.LOG,
                       Atspi.Role.LIST,
                       Atspi.Role.MARQUEE,
                       Atspi.Role.PANEL,
                       Atspi.Role.SECTION,
                       Atspi.Role.TABLE,
                       Atspi.Role.TREE,
                       Atspi.Role.TREE_TABLE]

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

        self._inModalDialog = False

    def clearCache(self, document=None):
        if document:
            self._objectCache[hash(document)] = {}
        else:
            self._objectCache = {}

    def structuralNavigationObjectCreator(self, name):
        """This convenience method creates a StructuralNavigationObject
        with the specified name and associated characteristics. (See the
        "Objects" section of code near the end of this class. Creators
        of StructuralNavigationObject's can still do things the old
        fashioned way should they so choose, by creating the instance
        and then adding it via addObject().

        Arguments:
        - name: the name/objType associated with this object.
        """

        # Bindings and presentation are mandatory.
        bindings = eval(f"self._{name}Bindings()")
        presentation = eval(f"self._{name}Presentation")

        # Predicates should be the exception; not the rule.
        try:
            predicate = eval(f"self._{name}Predicate")
        except Exception:
            predicate = None

        # Dialogs are nice, but we shouldn't insist upon them.
        try:
            dialogData = eval(f"self._{name}DialogData")
        except Exception:
            dialogData = None

        # Criteria is the present, but being phased out.
        try:
            criteria = eval(f"self._{name}Criteria")
        except Exception:
            criteria = None

        # Getters are the future!
        try:
            getter = eval(f"self._{name}Getter")
        except Exception:
            getter = None

        return StructuralNavigationObject(self, name, bindings, predicate,
                                          criteria, presentation, dialogData, getter)

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
                keybindings.defaultModifierMask,
                keybindings.ORCA_MODIFIER_MASK,
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

    def toggleStructuralNavigation(self, script, inputEvent, presentMessage=True):
        """Toggles structural navigation keys."""

        self.enabled = not self.enabled

        if self.enabled:
            string = messages.STRUCTURAL_NAVIGATION_KEYS_ON
        else:
            string = messages.STRUCTURAL_NAVIGATION_KEYS_OFF

        self._script.refreshKeyGrabs("toggling structural navigation")
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
        - thisCell: the accessible TABLE_CELL we're currently in
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
        if not table:
            self._script.presentMessage(messages.TABLE_NOT_IN_A)
            return None

        currentRow, currentCol = currentCoordinates
        desiredRow, desiredCol = desiredCoordinates
        rowDiff = desiredRow - currentRow
        colDiff = desiredCol - currentCol

        nRows, nColumns = self._script.utilities.rowAndColumnCount(table, False)
        cell = thisCell
        while cell:
            cell = self._script.utilities.cellForCoordinates(table, desiredRow, desiredCol)
            if not cell:
                if desiredCol < 0:
                    self._script.presentMessage(messages.TABLE_ROW_BEGINNING)
                    desiredCol = 0
                elif desiredCol > nColumns - 1:
                    self._script.presentMessage(messages.TABLE_ROW_END)
                    desiredCol = nColumns - 1
                if desiredRow < 0:
                    self._script.presentMessage(messages.TABLE_COLUMN_TOP)
                    desiredRow = 0
                elif desiredRow > nRows - 1:
                    self._script.presentMessage(messages.TABLE_COLUMN_BOTTOM)
                    desiredRow = nRows - 1
            elif (thisCell == cell and (colDiff or rowDiff)) \
                 or (settings.skipBlankCells and self._isBlankCell(cell)):
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
            oldRowHeaders = self._script.utilities.rowHeadersForCell(thisCell)
            oldColHeaders = self._script.utilities.columnHeadersForCell(thisCell)
            arg = [rowDiff, colDiff, oldRowHeaders, oldColHeaders]
            structuralNavigationObject.present(cell, arg)

    def _getAll(self, structuralNavigationObject, arg=None):
        """Returns all the instances of structuralNavigationObject."""

        modalDialog = self._script.utilities.getModalDialog(orca_state.locusOfFocus)
        inModalDialog = bool(modalDialog)
        if self._inModalDialog != inModalDialog:
            msg = (
                f"STRUCTURAL NAVIGATION: in modal dialog has changed from "
                f"{self._inModalDialog} to {inModalDialog}"
            )
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self.clearCache()
            self._inModalDialog = inModalDialog

        document = self._script.utilities.documentFrame()
        cache = self._objectCache.get(hash(document), {})
        key = f"{structuralNavigationObject.objType}:{arg}"
        matches = cache.get(key, [])
        if matches:
            tokens = ["STRUCTURAL NAVIGATION: Returning", len(matches), "matches from cache"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return matches.copy()

        if structuralNavigationObject.getter:
            matches = structuralNavigationObject.getter(document, arg)
        elif not structuralNavigationObject.criteria:
            return []
        elif not AXObject.supports_collection(document):
            tokens = ["STRUCTURAL NAVIGATION:", document, "does not support collection"]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            return []
        else:
            rule = structuralNavigationObject.criteria(arg)
            matches = AXCollection.get_all_matches(document, rule)

        if inModalDialog:
            originalSize = len(matches)
            matches = [m for m in matches if AXObject.find_ancestor(m, lambda x: x == modalDialog)]
            tokens = ["STRUCTURAL NAVIGATION: Removed", {originalSize - len(matches)},
                      "objects outside of modal dialog", modalDialog]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)

        rv = matches.copy()
        cache[key] = matches
        self._objectCache[hash(document)] = cache
        return rv

    def goEdge(self, structuralNavigationObject, isStart, container=None, arg=None):
        if container is None:
            obj, offset = self._script.utilities.getCaretContext()
            container = self.getContainerForObject(obj)

        if container is None or AXObject.is_dead(container):
            structuralNavigationObject.present(None, arg)
            return

        if isStart:
            obj, offset = self._script.utilities.nextContext(container, -1)
            structuralNavigationObject.present(obj, offset)
            return

        # Unlike going to the start of the container, when we move to the next edge
        # we pass beyond it on purpose. This makes us consistent with NVDA.
        obj, offset = self._script.utilities.lastContext(container)
        newObj, newOffset = self._script.utilities.nextContext(obj, offset)
        if not newObj:
            document = self._script.utilities.getDocumentForObject(obj)
            newObj = self._script.utilities.getNextObjectInDocument(obj, document)

        newContainer = self.getContainerForObject(newObj)
        if newObj and newContainer != container:
            structuralNavigationObject.present(newObj, newOffset)
            return

        if obj == container:
            obj = AXObject.get_child(obj, -1)

        structuralNavigationObject.present(obj, sameContainer=True)

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

        matches = self._getAll(structuralNavigationObject, arg)
        if not matches:
            structuralNavigationObject.present(None, arg)
            return

        if not isNext:
            matches.reverse()

        def _isValidMatch(obj):
            if AXObject.is_dead(obj):
                return False
            if self._script.utilities.isHidden(obj) or self._script.utilities.isEmpty(obj):
                return False
            if structuralNavigationObject.predicate is None:
                return True
            return structuralNavigationObject.predicate(obj)

        def _getMatchingObjAndIndex(obj):
            while obj:
                if obj in matches:
                    return obj, matches.index(obj)
                obj = AXObject.get_parent(obj)

            return None, -1

        offset = 0
        if not obj:
            obj, offset = self._script.utilities.getCaretContext()
        thisObj, index = _getMatchingObjAndIndex(obj)
        if thisObj:
            matches = matches[index:]
            obj = thisObj

        currentPath = AXObject.get_path(obj)
        for i, match in enumerate(matches):
            if not _isValidMatch(match):
                continue

            if AXObject.get_parent(match) == obj:
                comparison = self._script.utilities.characterOffsetInParent(match) - offset
            else:
                path = AXObject.get_path(match)
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

        matches = self._getAll(structuralNavigationObject, arg)
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

    def _getListDescription(self, obj):
        children = [x for x in AXObject.iter_children(obj, AXUtilities.is_list_item)]
        if not children:
            return ""

        return messages.listItemCount(len(children))

    def _getTableCaption(self, obj):
        """Returns a string which contains the table caption, or
        None if a caption could not be found.

        Arguments:
        - obj: the accessible table whose caption we want.
        """

        caption = obj.queryTable().caption
        try:
            caption.queryText()
        except Exception:
            return None
        else:
            return self._script.utilities.displayedText(caption)

    def _getTableDescription(self, obj):
        """Returns a string which describes the table."""

        nonUniformString = ""
        nonUniform = self._script.utilities.isNonUniformTable(obj)
        if nonUniform:
            nonUniformString = messages.TABLE_NON_UNIFORM + " "

        nRows, nColumns = self._script.utilities.rowAndColumnCount(obj, True)
        sizeString = messages.tableSize(nRows, nColumns)
        return (nonUniformString + sizeString)

    def getCellForObj(self, obj):
        """Looks for a table cell in the ancestry of obj, if obj is not a
        table cell.

        Arguments:
        - obj: the accessible object of interest.
        """

        if not AXUtilities.is_table_cell_or_header(obj):
            obj = AXObject.find_ancestor(obj, AXUtilities.is_table_cell_or_header)

        while obj and self._script.utilities.isLayoutOnly(self.getTableForCell(obj)):
            cell = AXObject.find_ancestor(obj, AXUtilities.is_table_cell_or_header)
            if cell is None:
                break
            obj = cell

        return obj

    def _isContainer(self, obj):
        role = AXObject.get_role(obj)
        if role not in self.CONTAINER_ROLES:
            return False

        if role == Atspi.Role.SECTION \
           and not self._script.utilities.isLandmark(obj) \
           and not self._script.utilities.isBlockquote(obj):
            return False

        return self._script.utilities.inDocumentContent(obj)

    def getContainerForObject(self, obj):
        if not obj:
            return None

        if self._isContainer(obj):
            return obj

        return AXObject.find_ancestor(obj, self._isContainer)

    def getTableForCell(self, obj):
        """Looks for a table in the ancestry of obj, if obj is not a table.

        Arguments:
        - obj: the accessible object of interest.
        """

        if obj and not AXUtilities.is_table(obj):
            obj = AXObject.find_ancestor(obj, AXUtilities.is_table)

        return obj

    def _isBlankCell(self, obj):
        """Returns True if the table cell is empty or consists of whitespace.

        Arguments:
        - obj: the accessible table cell to examine
        """

        if obj and (AXObject.get_name(obj) or AXObject.get_child_count(obj)):
            return False

        try:
            text = obj.queryText()
        except Exception:
            pass
        else:
            if text.getText(0, -1).strip():
                return False

        return True

    def _getCellText(self, obj):
        """Looks at the table cell and tries to get its text.

        Arguments:
        - obj: the accessible table cell to examine
        """

        text = ""
        if obj and not AXObject.get_child_count(obj):
            text = self._script.utilities.displayedText(obj)
        else:
            for child in AXObject.iter_children(obj):
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
                if header not in oldRowHeaders:
                    text = self._getCellText(header)
                    voice = self._script.speechGenerator.voice(string=text)
                    self._script.speakMessage(text, voice=voice, force=True)

        if colDiff:
            colHeaders = self._script.utilities.columnHeadersForCell(cell)
            for header in colHeaders:
                if header not in oldColHeaders:
                    text = self._getCellText(header)
                    voice = self._script.speechGenerator.voice(string=text)
                    self._script.speakMessage(text, voice=voice, force=True)

    def getCellCoordinates(self, obj, preferAttribute=True):
        """Returns the [row, col] of a ROLE_TABLE_CELL or [-1, -1]
        if the coordinates cannot be found.

        Arguments:
        - obj: the accessible table cell whose coordinates we want.
        - preferAttribute: If True, prefer object attribute over table interface
        """

        cell = self.getCellForObj(obj)
        table = self.getTableForCell(cell)
        thisRow, thisCol = self._script.utilities.coordinatesForCell(cell, preferAttribute)

        # If preferAttribute is True, we are getting coordinates to be spoken,
        # and not to deal with the logic below.
        if preferAttribute:
            return thisRow, thisCol

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

        return self._script.utilities.getFirstCaretPosition(obj)

    def _setCaretPosition(self, obj, characterOffset):
        """Sets the caret at the specified offset within obj."""

        objPath = AXObject.get_path(obj)
        objRole = AXObject.get_role(obj)
        if objRole == Atspi.Role.INVALID:
            return obj, characterOffset

        self._script.utilities.setCaretPosition(obj, characterOffset)
        AXObject.clear_cache(obj)
        if not AXUtilities.is_defunct(obj):
            return obj, characterOffset

        tokens = ["STRUCTURAL NAVIGATION:", obj, "became defunct after setting caret position"]
        debug.printTokens(debug.LEVEL_INFO, tokens, True)

        replicant = self._script.utilities.getObjectFromPath(objPath)
        if replicant and AXObject.get_role(replicant) == objRole:
            tokens = ["STRUCTURAL NAVIGATION: Updating obj to replicant", replicant]
            debug.printTokens(debug.LEVEL_INFO, tokens, True)
            obj = replicant

        return obj, characterOffset

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

    def _presentObject(self, obj, offset, priorObj=None):
        """Presents the entire object to the user.

        Arguments:
        - obj: the accessible object to be presented.
        - offset: the character offset within obj.
        """

        if not obj:
            return

        if self._presentWithSayAll(obj, offset):
            return

        AXEventSynthesizer.scroll_to_top_edge(obj)
        self._script.presentObject(obj, offset=offset, priorObj=priorObj, interrupt=True)

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
        if AXUtilities.is_combo_box(obj):
            obj = AXObject.get_child(obj, 0)

        if not AXObject.supports_selection(obj):
            return None

        return AXSelection.get_selected_child(obj, 0)

    def _getText(self, obj):
        # Another case where we'll do this for now, and clean it up when
        # object presentation is refactored.
        text = self._script.utilities.displayedText(obj)
        if not text:
            text = self._script.utilities.expandEOCs(obj)
        if not text:
            item = self._getSelectedItem(obj)
            if item:
                text = AXObject.get_name(item)
        if not text and AXUtilities.is_image(obj):
            try:
                image = obj.queryImage()
            except Exception:
                text = AXObject.get_description(obj)
            else:
                text = image.imageDescription or AXObject.get_description(obj)
            if not text:
                parent = AXObject.get_parent(obj)
                if AXUtilities.is_link(parent):
                    text = self._script.utilities.linkBasename(parent)
        if not text and AXUtilities.is_list(obj):
            children = [x for x in AXObject.iter_children(obj, AXUtilities.is_list_item)]
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

        # For now, we'll just grab the spoken indicator from settings.
        # When object presentation is refactored, we can clean this up.
        if AXUtilities.is_check_box(obj):
            unchecked, checked, partially = object_properties.CHECK_BOX_INDICATORS_SPEECH
            if AXUtilities.is_indeterminate(obj):
                return partially
            if AXUtilities.is_checked(obj):
                return checked
            return unchecked

        if AXUtilities.is_radio_button(obj):
            unselected, selected = object_properties.RADIO_BUTTON_INDICATORS_SPEECH
            if AXUtilities.is_checked(obj):
                return selected
            return unselected

        if AXUtilities.is_link(obj):
            if AXUtilities.is_visited(obj):
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
    # 1. Keybindings for goPrevious, goNext, and other such methods.
    #    This is a dictionary. See _setUpHandlersAndBindings() for
    #    supported values. But "previous", "next", and "list" are
    #    typically what you'll need.
    # 2. A means of identification: MatchCriteria and optional predicate.
    #    The MatchCriteria is required. For ATK implementations, AT-SPI2
    #    implements Collection. Applications and toolkits which implement
    #    AT-SPI2 directly should provide the implementation because our
    #    getting all objects via a tree dive is extremely non-performant.
    #    The predicate is only needed if Collection lacks something we
    #    need to identify the object is really the thing we want. Usually
    #    the predicate is not needed and can remain undefined.
    # 3. A definition of how the object should be presented (both when
    #    another instance of that object is found as well as when it is
    #    not). This function should do the presentation.
    # 4. Details needed to populate the dialog with the object list is
    #    presented.
    #
    # Convenience methods have been put into place whereby one can
    # create an object (FOO = "foo"), and then provide the following
    # methods: _fooBindings(), _fooPredicate(), _fooCriteria(), and
    # _fooPresentation().  With these in place, and with the object
    # FOO included among the StructuralNavigation.enabledTypes for
    # the script, the structural navigation object should be created
    # and set up automagically. At least that is the idea. :-) This
    # hopefully will also enable easy re-definition of existing
    # objects on a script-by-script basis.

    ########################
    #                      #
    # Blockquotes          #
    #                      #
    ########################

    def _blockquoteBindings(self):
        bindings = {}
        prevDesc = cmdnames.BLOCKQUOTE_PREV
        bindings["previous"] = ["q", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.BLOCKQUOTE_NEXT
        bindings["next"] = ["q", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.BLOCKQUOTE_LIST
        bindings["list"] = ["q", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]
        return bindings

    def _blockquoteGetter(self, document, arg=None):
        return AXUtilities.find_all_block_quotes(document)

    def _blockquotePresentation(self, obj, arg=None):
        if obj is not None:
            [obj, characterOffset] = self._getCaretPosition(obj)
            obj, characterOffset = self._setCaretPosition(obj, characterOffset)
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
        bindings = {}
        prevDesc = cmdnames.BUTTON_PREV
        bindings["previous"] = ["b", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.BUTTON_NEXT
        bindings["next"] = ["b", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.BUTTON_LIST
        bindings["list"] = ["b", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]
        return bindings

    def _buttonGetter(self, document, arg=None):
        return AXUtilities.find_all_buttons(document)

    def _buttonPresentation(self, obj, arg=None):
        if obj is not None:
            [obj, characterOffset] = self._getCaretPosition(obj)
            obj, characterOffset = self._setCaretPosition(obj, characterOffset)
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
        bindings = {}
        prevDesc = cmdnames.CHECK_BOX_PREV
        bindings["previous"] = ["x", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.CHECK_BOX_NEXT
        bindings["next"] = ["x", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.CHECK_BOX_LIST
        bindings["list"] = ["x", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]
        return bindings

    def _checkBoxGetter(self, document, arg=None):
        return AXUtilities.find_all_check_boxes(document)

    def _checkBoxPresentation(self, obj, arg=None):
        if obj is not None:
            [obj, characterOffset] = self._getCaretPosition(obj)
            obj, characterOffset = self._setCaretPosition(obj, characterOffset)
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
        bindings = {}
        prevDesc = cmdnames.LARGE_OBJECT_PREV
        bindings["previous"] = ["o", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.LARGE_OBJECT_NEXT
        bindings["next"] = ["o", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.LARGE_OBJECT_LIST
        bindings["list"] = ["o", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]
        return bindings

    def _chunkCriteria(self, arg=None):
        return AXCollection.create_match_rule(roles=self.OBJECT_ROLES + self.CONTAINER_ROLES)

    def _chunkPredicate(self, obj, arg=None):
        if AXUtilities.is_heading(obj):
            return True

        text = self._script.utilities.queryNonEmptyText(obj)
        if not (text and text.characterCount > settings.largeObjectTextLength):
            return False

        string = text.getText(0, -1)
        eocs = string.count(self._script.EMBEDDED_OBJECT_CHARACTER)
        if eocs/text.characterCount < 0.05:
            return True

        return False

    def _chunkPresentation(self, obj, arg=None):
        if obj is not None:
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
        bindings = {}
        prevDesc = cmdnames.COMBO_BOX_PREV
        bindings["previous"] = ["c", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.COMBO_BOX_NEXT
        bindings["next"] = ["c", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.COMBO_BOX_LIST
        bindings["list"] = ["c", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]
        return bindings

    def _comboBoxGetter(self, document, arg=None):
        return AXUtilities.find_all_combo_boxes(document)

    def _comboBoxPresentation(self, obj, arg=None):
        if obj is not None:
            [obj, characterOffset] = self._getCaretPosition(obj)
            obj, characterOffset = self._setCaretPosition(obj, characterOffset)
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
        bindings = {}
        prevDesc = cmdnames.ENTRY_PREV
        bindings["previous"] = ["e", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.ENTRY_NEXT
        bindings["next"] = ["e", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.ENTRY_LIST
        bindings["list"] = ["e", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]
        return bindings

    def _entryGetter(self, document, arg=None):
        def parent_is_not_editable(obj):
            parent = AXObject.get_parent(obj)
            return parent is not None and not AXUtilities.is_editable(parent)
        return AXUtilities.find_all_editable_objects(document, pred=parent_is_not_editable)

    def _entryPresentation(self, obj, arg=None):
        if obj is not None:
            [obj, characterOffset] = self._getCaretPosition(obj)
            obj, characterOffset = self._setCaretPosition(obj, characterOffset)
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
        bindings = {}
        prevDesc = cmdnames.FORM_FIELD_PREV
        bindings["previous"] = ["f", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.FORM_FIELD_NEXT
        bindings["next"] = ["f", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.FORM_FIELD_LIST
        bindings["list"] = ["f", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]
        return bindings

    def _formFieldGetter(self, document, arg=None):
        def is_not_noneditable_doc_frame(obj):
            if AXUtilities.is_document_frame(obj):
                return AXUtilities.is_editable(obj)
            return True
        return AXUtilities.find_all_form_fields(document, pred=is_not_noneditable_doc_frame)

    def _formFieldPresentation(self, obj, arg=None):
        if obj is not None:
            if AXUtilities.is_text(obj) and AXObject.get_child_count(obj):
                obj = AXObject.get_child(obj, 0)
            [obj, characterOffset] = self._getCaretPosition(obj)
            obj, characterOffset = self._setCaretPosition(obj, characterOffset)
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
        return [1, 6]

    def _headingGetter(self, document, arg=None):
        if arg is not None:
            return AXUtilities.find_all_headings_at_level(document, level=arg)
        return AXUtilities.find_all_headings(document)

    def _headingPresentation(self, obj, arg=None):
        if obj is not None:
            [obj, characterOffset] = self._getCaretPosition(obj)
            obj, characterOffset = self._setCaretPosition(obj, characterOffset)
            self._presentObject(obj, characterOffset)
        elif arg is None:
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
    # Iframes              #
    #                      #
    ########################

    def _iframeBindings(self):
        bindings = {}
        prevDesc = cmdnames.IFRAME_PREV
        bindings["previous"] = ["", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.IFRAME_NEXT
        bindings["next"] = ["", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.IFRAME_LIST
        bindings["list"] = ["", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]
        return bindings

    def _iframeGetter(self, document, arg=None):
        return AXUtilities.find_all_internal_frames(document)

    def _iframePresentation(self, obj, arg=None):
        if obj is not None:
            [newObj, characterOffset] = self._getCaretPosition(obj)
            self._setCaretPosition(newObj, characterOffset)
            self._presentObject(obj, 0)
        else:
            full = messages.NO_MORE_IFRAMES
            brief = messages.STRUCTURAL_NAVIGATION_NOT_FOUND
            self._script.presentMessage(full, brief)

    def _iframeDialogData(self):
        columnHeaders = [guilabels.SN_HEADER_IFRAME]

        def rowData(obj):
            name = AXObject.get_name(obj)
            if not name and AXObject.get_child_count(obj):
                name = AXObject.get_name(AXObject.get_child(obj, 0))
            return [name or self._getRoleName(obj)]

        return guilabels.SN_TITLE_IFRAME, columnHeaders, rowData

    ########################
    #                      #
    # Images               #
    #                      #
    ########################

    def _imageBindings(self):
        bindings = {}
        prevDesc = cmdnames.IMAGE_PREV
        bindings["previous"] = ["g", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.IMAGE_NEXT
        bindings["next"] = ["g", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.IMAGE_LIST
        bindings["list"] = ["g", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]
        return bindings

    def _imageGetter(self, document, arg=None):
        return AXUtilities.find_all_images_and_image_maps(document)

    def _imagePresentation(self, obj, arg=None):
        if obj is not None:
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
        bindings = {}
        prevDesc = cmdnames.LANDMARK_PREV
        bindings["previous"] = ["m", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.LANDMARK_NEXT
        bindings["next"] = ["m", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.LANDMARK_LIST
        bindings["list"] = ["m", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]
        return bindings

    def _landmarkGetter(self, document, arg=None):
        return AXUtilities.find_all_landmarks(document)

    def _landmarkPresentation(self, obj, arg=None):
        if obj is not None:
            [obj, characterOffset] = self._getCaretPosition(obj)
            obj, characterOffset = self._setCaretPosition(obj, characterOffset)
            self._script.presentMessage(AXObject.get_name(obj))
            self._presentLine(obj, characterOffset)
        else:
            full = messages.NO_LANDMARK_FOUND
            brief = messages.STRUCTURAL_NAVIGATION_NOT_FOUND
            self._script.presentMessage(full, brief)

    def _landmarkDialogData(self):
        columnHeaders = [guilabels.SN_HEADER_LANDMARK]
        columnHeaders.append(guilabels.SN_HEADER_ROLE)

        def rowData(obj):
            return [AXObject.get_name(obj), self._getRoleName(obj)]

        return guilabels.SN_TITLE_LANDMARK, columnHeaders, rowData

    ########################
    #                      #
    # Lists                #
    #                      #
    ########################

    def _listBindings(self):
        bindings = {}
        prevDesc = cmdnames.LIST_PREV
        bindings["previous"] = ["l", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.LIST_NEXT
        bindings["next"] = ["l", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.LIST_LIST
        bindings["list"] = ["l", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]
        return bindings

    def _listGetter(self, document, arg=None):
        return AXUtilities.find_all_lists(document)

    def _listPresentation(self, obj, arg=None):
        if obj is not None:
            self._script.speakMessage(self._getListDescription(obj))
            [obj, characterOffset] = self._getCaretPosition(obj)
            obj, characterOffset = self._setCaretPosition(obj, characterOffset)
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
        bindings = {}
        prevDesc = cmdnames.LIST_ITEM_PREV
        bindings["previous"] = ["i", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.LIST_ITEM_NEXT
        bindings["next"] = ["i", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.LIST_ITEM_LIST
        bindings["list"] = ["i", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]
        return bindings

    def _listItemGetter(self, document, arg=None):
        return AXUtilities.find_all_list_items(document)

    def _listItemPresentation(self, obj, arg=None):
        if obj is not None:
            [obj, characterOffset] = self._getCaretPosition(obj)
            obj, characterOffset = self._setCaretPosition(obj, characterOffset)
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
        bindings = {}
        prevDesc = cmdnames.LIVE_REGION_PREV
        bindings["previous"] = ["d", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.LIVE_REGION_NEXT
        bindings["next"] = ["d", keybindings.NO_MODIFIER_MASK, nextDesc]

        desc = cmdnames.LIVE_REGION_LAST
        bindings["last"] = ["y", keybindings.NO_MODIFIER_MASK, desc]
        return bindings

    def _liveRegionGetter(self, document, arg=None):
        return AXUtilities.find_all_live_regions(document)

    def _liveRegionPresentation(self, obj, arg=None):
        if obj is not None:
            [obj, characterOffset] = self._getCaretPosition(obj)
            obj, characterOffset = self._setCaretPosition(obj, characterOffset)
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
        bindings = {}
        prevDesc = cmdnames.PARAGRAPH_PREV
        bindings["previous"] = ["p", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.PARAGRAPH_NEXT
        bindings["next"] = ["p", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.PARAGRAPH_LIST
        bindings["list"] = ["p", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]
        return bindings

    def _paragraphGetter(self, document, arg=None):
        def has_at_least_three_characters(obj):
            if AXUtilities.is_heading(obj):
                return True

            try:
                text = obj.queryText()
                # We're choosing 3 characters as the minimum because some
                # paragraphs contain a single image or link and a text
                # of length 2: An embedded object character and a space.
                # We want to skip these.
                return text.characterCount > 2
            except Exception:
                return False

        return AXUtilities.find_all_paragraphs(document, True, has_at_least_three_characters)

    def _paragraphPresentation(self, obj, arg=None):
        if obj is not None:
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
        bindings = {}
        prevDesc = cmdnames.RADIO_BUTTON_PREV
        bindings["previous"] = ["r", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.RADIO_BUTTON_NEXT
        bindings["next"] = ["r", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.RADIO_BUTTON_LIST
        bindings["list"] = ["r", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]
        return bindings

    def _radioButtonGetter(self, document, arg=None):
        return AXUtilities.find_all_radio_buttons(document)

    def _radioButtonPresentation(self, obj, arg=None):
        if obj is not None:
            [obj, characterOffset] = self._getCaretPosition(obj)
            obj, characterOffset = self._setCaretPosition(obj, characterOffset)
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
        bindings = {}
        prevDesc = cmdnames.SEPARATOR_PREV
        bindings["previous"] = ["s", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.SEPARATOR_NEXT
        bindings["next"] = ["s", keybindings.NO_MODIFIER_MASK, nextDesc]
        return bindings

    def _separatorGetter(self, document, arg=None):
        return AXUtilities.find_all_separators(document)

    def _separatorPresentation(self, obj, arg=None):
        if obj is not None:
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
        bindings = {}
        prevDesc = cmdnames.TABLE_PREV
        bindings["previous"] = ["t", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.TABLE_NEXT
        bindings["next"] = ["t", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.TABLE_LIST
        bindings["list"] = ["t", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]
        return bindings

    def _tableGetter(self, document, arg=None):
        def is_not_layout_or_empty(obj):
            if not AXObject.get_child_count(obj):
                return False

            # This should no longer be needed once Atspi 2.8.4 is released.
            attrs = self._script.utilities.objectAttributes(obj)
            if attrs.get('layout-guess') == 'true':
                return False

            try:
                return obj.queryTable().nRows > 0
            except Exception:
                return False

        return AXUtilities.find_all_tables(document, is_not_layout_or_empty)

    def _tablePresentation(self, obj, arg=None):
        if obj is not None:
            caption = self._getTableCaption(obj)
            if caption:
                self._script.presentMessage(caption)
            self._script.presentMessage(self._getTableDescription(obj))
            cell = obj.queryTable().getAccessibleAt(0, 0)
            if not cell:
                tokens = ["STRUCTURAL NAVIGATION: Broken table interface for", obj]
                debug.printTokens(debug.LEVEL_INFO, tokens, True)
                cell = AXObject.find_descendant(obj, AXUtilities.is_table_cell)
                if cell:
                    tokens = ["STRUCTURAL NAVIGATION: Located", cell, "for first cell"]
                    debug.printTokens(debug.LEVEL_INFO, tokens, True)

            self.lastTableCell = [0, 0]
            self._presentObject(cell, 0, priorObj=obj)
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

    def _tableCellGetter(self, document, arg=None):
        # TODO - JD: It would be more performant to set the root to the table.
        # Actually, this doesn't seem to be getting used. Either use it or delete it.
        return AXUtilities.find_all_table_cells_and_headers(document)

    def _tableCellPresentation(self, cell, arg):
        if cell is None:
            return

        if settings.speakCellHeaders:
            self._presentCellHeaders(cell, arg)

        [obj, characterOffset] = self._getCaretPosition(cell)
        obj, characterOffset = self._setCaretPosition(obj, characterOffset)
        self._script.updateBraille(obj)

        blank = self._isBlankCell(cell)
        if not blank:
            self._presentObject(cell, 0)
        else:
            self._script.speakMessage(messages.BLANK)

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
        bindings = {}
        prevDesc = cmdnames.UNVISITED_LINK_PREV
        bindings["previous"] = ["u", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.UNVISITED_LINK_NEXT
        bindings["next"] = ["u", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.UNVISITED_LINK_LIST
        bindings["list"] = ["u", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]

        return bindings

    def _unvisitedLinkGetter(self, document, arg=None):
        return AXUtilities.find_all_unvisited_links(document)

    def _unvisitedLinkPresentation(self, obj, arg=None):
        if obj is not None:
            [obj, characterOffset] = self._getCaretPosition(obj)
            obj, characterOffset = self._setCaretPosition(obj, characterOffset)
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
        bindings = {}
        prevDesc = cmdnames.VISITED_LINK_PREV
        bindings["previous"] = ["v", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.VISITED_LINK_NEXT
        bindings["next"] = ["v", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.VISITED_LINK_LIST
        bindings["list"] = ["v", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]

        return bindings

    def _visitedLinkGetter(self, document, arg=None):
        return AXUtilities.find_all_visited_links(document)

    def _visitedLinkPresentation(self, obj, arg=None):
        if obj is not None:
            [obj, characterOffset] = self._getCaretPosition(obj)
            obj, characterOffset = self._setCaretPosition(obj, characterOffset)
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
        bindings = {}
        prevDesc = cmdnames.LINK_PREV
        bindings["previous"] = ["k", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.LINK_NEXT
        bindings["next"] = ["k", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.LINK_LIST
        bindings["list"] = ["k", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]
        return bindings

    def _linkGetter(self, document, arg=None):
        return AXUtilities.find_all_links(document)

    def _linkPresentation(self, obj, arg=None):
        if obj is not None:
            [obj, characterOffset] = self._getCaretPosition(obj)
            obj, characterOffset = self._setCaretPosition(obj, characterOffset)
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
        bindings = {}
        prevDesc = cmdnames.CLICKABLE_PREV
        bindings["previous"] = ["a", keybindings.SHIFT_MODIFIER_MASK, prevDesc]

        nextDesc = cmdnames.CLICKABLE_NEXT
        bindings["next"] = ["a", keybindings.NO_MODIFIER_MASK, nextDesc]

        listDesc = cmdnames.CLICKABLE_LIST
        bindings["list"] = ["a", keybindings.SHIFT_ALT_MODIFIER_MASK, listDesc]
        return bindings

    def _clickableCriteria(self, arg=None):
        return AXCollection.create_match_rule(
            interfaces=["action"],
            interface_match_type=Atspi.CollectionMatchType.ANY)

    def _clickablePredicate(self, obj, arg=None):
        return self._script.utilities.isClickableElement(obj)

    def _clickablePresentation(self, obj, arg=None):
        if obj is not None:
            [obj, characterOffset] = self._getCaretPosition(obj)
            obj, characterOffset = self._setCaretPosition(obj, characterOffset)
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

    ########################
    #                      #
    # Containers           #
    #                      #
    ########################

    def _containerBindings(self):
        bindings = {}
        desc = cmdnames.CONTAINER_START
        bindings["start"] = ["comma", keybindings.SHIFT_MODIFIER_MASK, desc]

        desc = cmdnames.CONTAINER_END
        bindings["end"] = ["comma", keybindings.NO_MODIFIER_MASK, desc]

        return bindings

    def _containerCriteria(self, arg=None):
        return AXCollection.create_match_rule(roles=self.CONTAINER_ROLES)

    def _containerPredicate(self, obj, arg=None):
        return self._isContainer(obj)

    def _containerPresentation(self, obj, arg=None, **kwargs):
        if obj is None:
            self._script.presentMessage(messages.CONTAINER_NOT_IN_A)
            return

        if kwargs.get("sameContainer"):
            self._script.presentMessage(messages.CONTAINER_END)

        characterOffset = arg
        if characterOffset is None:
            obj, characterOffset = self._getCaretPosition(obj)

        obj, characterOffset = self._setCaretPosition(obj, characterOffset)
        self._presentLine(obj, characterOffset)
