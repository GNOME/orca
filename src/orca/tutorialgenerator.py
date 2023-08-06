# Orca
#
# Copyright 2008-2009 Sun Microsystems Inc.
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

"""Utilities for obtaining tutorial utterances for objects.  In general,
there probably should be a singleton instance of the TutorialGenerator
class.  For those wishing to override the generators, however,
one can create a new instance and replace/extend the tutorial generators
as they see fit."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2008-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import debug
from . import orca_state
from . import settings

from .ax_object import AXObject
from .ax_utilities import AXUtilities
from .orca_i18n import _         # for gettext support

class TutorialGenerator:
    """Takes accessible objects and produces a tutorial string to speak
    for those objects.  See the getTutorialString method, which is the
    primary entry point.  Subclasses can feel free to override/extend
    the getTutorialGenerators instance field as they see fit."""

    def __init__(self, script):

        # The script that created us.  This allows us to ask the
        # script for information if we need it.
        #
        self._script = script
        # storing the last spoken message.
        self.lastTutorial = ""

        self.lastRole = None

        # Set up a dictionary that maps role names to functions
        # that generate tutorial strings for objects that implement that role.
        #
        self.tutorialGenerators = {}
        self.tutorialGenerators[Atspi.Role.CHECK_BOX] = \
            self._getTutorialForCheckBox
        self.tutorialGenerators[Atspi.Role.COMBO_BOX] = \
            self._getTutorialForComboBox
        self.tutorialGenerators[Atspi.Role.FRAME] = \
            self._getTutorialForFrame
        self.tutorialGenerators[Atspi.Role.ICON] = \
            self._getTutorialForIcon
        self.tutorialGenerators[Atspi.Role.LAYERED_PANE] = \
            self._getTutorialForLayeredPane
        self.tutorialGenerators[Atspi.Role.LIST] = \
            self._getTutorialForList
        self.tutorialGenerators[Atspi.Role.LIST_ITEM] = \
            self._getTutorialForListItem
        self.tutorialGenerators[Atspi.Role.PAGE_TAB] = \
            self._getTutorialForPageTab
        self.tutorialGenerators[Atspi.Role.PARAGRAPH] = \
            self._getTutorialForText
        self.tutorialGenerators[Atspi.Role.PASSWORD_TEXT] = \
            self._getTutorialForText
        self.tutorialGenerators[Atspi.Role.ENTRY] = \
            self._getTutorialForText
        self.tutorialGenerators[Atspi.Role.PUSH_BUTTON] = \
            self._getTutorialForPushButton
        self.tutorialGenerators[Atspi.Role.SPIN_BUTTON] = \
            self._getTutorialForSpinButton
        self.tutorialGenerators[Atspi.Role.TABLE_CELL] = \
            self._getTutorialForTableCellRow
        self.tutorialGenerators[Atspi.Role.TEXT] = \
            self._getTutorialForText
        self.tutorialGenerators[Atspi.Role.TOGGLE_BUTTON] = \
            self._getTutorialForCheckBox
        self.tutorialGenerators[Atspi.Role.RADIO_BUTTON] = \
            self._getTutorialForRadioButton
        self.tutorialGenerators[Atspi.Role.MENU]                = \
            self._getTutorialForMenu
        self.tutorialGenerators[Atspi.Role.CHECK_MENU_ITEM]     = \
            self._getTutorialForCheckBox
        self.tutorialGenerators[Atspi.Role.MENU_ITEM]           = \
            self._getTutorialForMenuItem
        self.tutorialGenerators[Atspi.Role.RADIO_MENU_ITEM]     = \
            self._getTutorialForCheckBox
        self.tutorialGenerators[Atspi.Role.SLIDER]              = \
            self._getTutorialForSlider

    def _debugGenerator(self, generatorName, obj, alreadyFocused, utterances):
        """Prints debug.LEVEL_FINER information regarding
        the tutorial generator.

        Arguments:
        - generatorName: the name of the generator
        - obj: the object being presented
        - alreadyFocused: False if object just received focus
        - utterances: the generated text
        """

        debug.println(debug.LEVEL_FINER,
                      f"GENERATOR: {generatorName}")
        debug.println(debug.LEVEL_FINER,
                      f"           obj             = {AXObject.get_name(obj)}")
        debug.println(debug.LEVEL_FINER,
                      f"           role            = {AXObject.get_role_name(obj)}")
        debug.println(debug.LEVEL_FINER,
                      f"           alreadyFocused  = {alreadyFocused}")
        debug.println(debug.LEVEL_FINER,
                      "           utterances:")
        for text in utterances:
            debug.println(debug.LEVEL_FINER,
                    f"               ({text})")

    def _getDefaultTutorial(
        self, obj, alreadyFocused, forceTutorial, role=None):
        """The default tutorial generator returns the empty tutorial string
        because We have no associated tutorial function for the object.

        Arguments:
        - obj: an Accessible
        - alreadyFocused: False if object just received focus
        - forceTutorial: used for when whereAmI really needs the tutorial string
        - role: A role that should be used instead of the Accessible's
          possible role.

        Returns the empty list []
        """

        return []


    def _getTutorialForCheckBox(self, obj, alreadyFocused, forceTutorial):
        """Get the  tutorial string for a check box.

        Arguments:
        - obj: the check box
        - alreadyFocused: False if object just received focus
        - forceTutorial: used for when whereAmI really needs the tutorial string

        Returns a list of tutorial utterances to be spoken for the object.
        """

        utterances = []
        # Translators: this is a tip for the user on how to toggle a checkbox.
        msg = _("Press space to toggle.")

        if (not alreadyFocused and self.lastTutorial != [msg]) \
           or forceTutorial:
            utterances.append(msg)

        self._debugGenerator("_getTutorialForCheckBox",
                             obj,
                             alreadyFocused,
                             utterances)

        return utterances

    def _getTutorialForComboBox(self, obj, alreadyFocused, forceTutorial):
        """Get the  tutorial string for a combobox.

        Arguments:
        - obj: the combo box
        - alreadyFocused: False if object just received focus
        - forceTutorial: used for when whereAmI really needs the tutorial string

        Returns a list of tutorial utterances to be spoken for the object.
        """

        utterances = []
        # Translators: this is a tip for the user on how to interact
        # with a combobox.
        msg = _("Press space to expand, and use up and down to select an item.")

        if (not alreadyFocused and self.lastTutorial != [msg]) \
           or forceTutorial:
            utterances.append(msg)

        self._debugGenerator("_getTutorialForComboBox",
                             obj,
                             alreadyFocused,
                             utterances)

        return utterances

    def _getTutorialForFrame(self, obj, alreadyFocused, forceTutorial):
        """Get the  tutorial string for a frame.

        Arguments:
        - obj: the frame
        - alreadyFocused: False if object just received focus
        - forceTutorial: used for when whereAmI really needs the tutorial string

        Returns a list of tutorial utterances to be spoken for the object.
        """

        utterances = []

        # Translators: If this application has more than one unfocused alert or
        # dialog window, inform user of how to refocus these.
        childWindowsMsg = _("Press alt+f6 to give focus to child windows.")

        # If this application has more than one unfocused alert or
        # dialog window, tell user how to give them focus.
        try:
            alertAndDialogCount = \
                self._script.utilities.unfocusedAlertAndDialogCount(obj)
        except Exception:
            alertAndDialogCount = 0
        if alertAndDialogCount > 0:
            utterances.append(childWindowsMsg)

        self._debugGenerator("_getTutorialForFrame",
                             obj,
                             alreadyFocused,
                             utterances)

        return utterances

    def _getTutorialForIcon(self, obj, alreadyFocused, forceTutorial):
        """Get the  tutorial string for an icon.

        Arguments:
        - obj: the icon
        - alreadyFocused: False if object just received focus
        - forceTutorial: used for when whereAmI really needs the tutorial string

        Returns a list of tutorial utterances to be spoken for the object.
        """

        parent = AXObject.get_parent(obj)
        if AXUtilities.is_layered_pane(parent):
            utterances = self._getTutorialForLayeredPane(parent,
                                                         alreadyFocused,
                                                         forceTutorial)
        else:
            utterances = self._getDefaultTutorial(obj,
                                                  alreadyFocused,
                                                  forceTutorial)

        self._debugGenerator("_getTutorialForIcon",
                             obj,
                             alreadyFocused,
                             utterances)

        return utterances

    def _getTutorialForLayeredPane(self, obj, alreadyFocused, forceTutorial):
        """Get the  tutorial string for a layered pane.

        Arguments:
        - obj: the layered pane
        - alreadyFocused: False if object just received focus
        - forceTutorial: used for when whereAmI really needs the tutorial string

        Returns a list of tutorial utterances to be spoken for the object.
        """

        utterances = []

        # Translators: this gives tips on how to navigate items in a
        # layered pane.
        msg = _("To move to items, use either " \
                "the arrow keys or type ahead searching.")
        utterances.append(msg)

        # Translators: this is the tutorial string for when first landing
        # on the desktop, describing how to access the system menus.
        desktopMsg = _("To get to the system menus press the alt+f1 key.")

        scriptName = self._script.name
        sibling = AXObject.get_child(AXObject.get_parent(obj), 0)
        if 'nautilus' in scriptName and obj == sibling:
            utterances.append(desktopMsg)

        if (not alreadyFocused and self.lastTutorial != utterances) \
            or forceTutorial:
            pass
        else:
            utterances = []

        self._debugGenerator("_getTutorialForLayeredPane",
                             obj,
                             alreadyFocused,
                             utterances)

        return utterances

    def _getTutorialForList(self, obj, alreadyFocused, forceTutorial):
        """Get the  tutorial string for a list.

        Arguments:
        - obj: the list
        - alreadyFocused: False if object just received focus
        - forceTutorial: used for when whereAmI really needs the tutorial string

        Returns a list of tutorial utterances to be spoken for the object.
        """

        utterances = []

        # Translators: this is the tutorial string when navigating lists.
        msg = _("Use up and down to select an item.")

        if (not alreadyFocused and self.lastTutorial != [msg]) \
           or forceTutorial:
            utterances.append(msg)

        self._debugGenerator("_getTutorialForList",
                             obj,
                             alreadyFocused,
                             utterances)

        return utterances

    def _getTutorialForListItem(self, obj, alreadyFocused, forceTutorial):
        """Get the  tutorial string for a listItem.

        Arguments:
        - obj: the listitem
        - alreadyFocused: False if object just received focus
        - forceTutorial: used for when whereAmI really needs the tutorial string

        Returns a list of tutorial utterances to be spoken for the object.
        """

        utterances = []

        # Translators: this represents the state of a node in a tree.
        # 'expanded' means the children are showing.
        # 'collapsed' means the children are not showing.
        # this string informs the user how to collapse the node.
        expandedMsg = _("To collapse, press shift plus left.")

        # Translators: this represents the state of a node in a tree.
        # 'expanded' means the children are showing.
        # 'collapsed' means the children are not showing.
        # this string informs the user how to expand the node.
        collapsedMsg = _("To expand, press shift plus right.")


        # If already in focus then the tree probably collapsed or expanded
        if AXUtilities.is_expandable(obj):
            if AXUtilities.is_expanded(obj):
                if (self.lastTutorial != [expandedMsg]) or forceTutorial:
                    utterances.append(expandedMsg)
            else:
                if (self.lastTutorial != [collapsedMsg]) or forceTutorial:
                    utterances.append(collapsedMsg)

        self._debugGenerator("_getTutorialForListItem",
                             obj,
                             alreadyFocused,
                             utterances)
        return utterances

    def _getTutorialForMenuItem(self, obj, alreadyFocused, forceTutorial):
        """Get the tutorial string for a menu item

        Arguments:
        - obj: the menu item
        - alreadyFocused: False if object just received focus
        - forceTutorial: used for when whereAmI really needs the tutorial string

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []
        # Translators: this is the tutorial string for activating a menu item
        msg = _("To activate press return.")

        if (not alreadyFocused and self.lastTutorial != [msg]) \
           or forceTutorial:
            utterances.append(msg)

        self._debugGenerator("_getTutorialForMenuItem",
                             obj,
                             alreadyFocused,
                             utterances)

        return utterances

    def _getTutorialForText(self, obj, alreadyFocused, forceTutorial):
        """Get the tutorial string for a text object.

        Arguments:
        - obj: the text component
        - alreadyFocused: False if object just received focus
        - forceTutorial: used for when whereAmI really needs the tutorial string

        Returns a list of tutorial utterances to be spoken for the object.
        """

        if not AXUtilities.is_editable(obj):
            return []

        utterances = []
        # Translators: This is the tutorial string for when landing
        # on text fields.
        msg = _("Type in text.")

        if (not alreadyFocused or forceTutorial) and \
           not self._script.utilities.isReadOnlyTextArea(obj):
            utterances.append(msg)

        self._debugGenerator("_getTutorialForText",
                             obj,
                             alreadyFocused,
                             utterances)

        return utterances

    def _getTutorialForPageTab(self, obj, alreadyFocused, forceTutorial):
        """Get the tutorial string for a page tab.

        Arguments:
        - obj: the page tab
        - alreadyFocused: False if object just received focus
        - forceTutorial: used for when whereAmI really needs the tutorial string

        Returns a list of tutorial utterances to be spoken for the object.
        """

        utterances = []
        # Translators: this is the tutorial string for landing
        # on a page tab, we are informing the
        # user how to navigate these.
        msg = _("Use left and right to view other tabs.")

        if (self.lastTutorial != [msg]) or forceTutorial:
            utterances.append(msg)

        self._debugGenerator("_getTutorialForPageTabList",
                             obj,
                             alreadyFocused,
                             utterances)

        return utterances

    def _getTutorialForPushButton(self, obj, alreadyFocused, forceTutorial):
        """Get the tutorial string for a push button

        Arguments:
        - obj: the push button
        - alreadyFocused: False if object just received focus
        - forceTutorial: used for when whereAmI really needs the tutorial string

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []
        # Translators: this is the tutorial string for activating a push button.
        msg = _("To activate press space.")

        if (not alreadyFocused and self.lastTutorial != [msg]) \
           or forceTutorial:
            utterances.append(msg)

        self._debugGenerator("_getTutorialForPushButton",
                             obj,
                             alreadyFocused,
                             utterances)

        return utterances

    def _getTutorialForSpinButton(self, obj, alreadyFocused, forceTutorial):
        """Get the tutorial string for a spin button.  If the object already has
        focus, then no tutorial is given.

        Arguments:
        - obj: the spin button
        - alreadyFocused: False if object just received focus
        - forceTutorial: used for when whereAmI really needs the tutorial string

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []
        # Translators: this is the tutorial string for when landing
        # on a spin button.
        msg = _("Use up or down arrow to select value." \
              " Or type in the desired numerical value.")

        if (not alreadyFocused and self.lastTutorial != [msg]) \
           or forceTutorial:
            utterances.append(msg)

        self._debugGenerator("_getTutorialForSpinButton",
                             obj,
                             alreadyFocused,
                             utterances)

        return utterances

    def _getTutorialForTableCell(self, obj, alreadyFocused, forceTutorial):
        """Get the tutorial utterances for a single table cell

        Arguments:
        - obj: the table
        - alreadyFocused: False if object just received focus
        - forceTutorial: used for when whereAmI really needs the tutorial string

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []

        # Translators: this represents the state of a node in a tree.
        # 'expanded' means the children are showing.
        # 'collapsed' means the children are not showing.
        # this string informs the user how to collapse the node.
        expandedMsg = _("To collapse, press shift plus left.")

        # Translators: this represents the state of a node in a tree.
        # 'expanded' means the children are showing.
        # 'collapsed' means the children are not showing.
        # this string informs the user how to expand the node.
        collapsedMsg = _("To expand, press shift plus right.")

        # If this table cell has 2 children and one of them has a
        # 'toggle' action and the other does not, then present this
        # as a checkbox where:
        # 1) we get the checked state from the cell with the 'toggle' action
        # 2) we get the label from the other cell.
        # See Orca bug #376015 for more details.
        #
        if AXObject.get_child_count(obj) == 2:
            cellOrder = []
            hasToggle = [ False, False ]
            for i, child in enumerate(obj):
                if self._script.utilities.hasMeaningfulToggleAction(child):
                    hasToggle[i] = True
                    break
            if hasToggle[0] and not hasToggle[1]:
                cellOrder = [ 1, 0 ]
            elif not hasToggle[0] and hasToggle[1]:
                cellOrder = [ 0, 1 ]
            if cellOrder:
                for i in cellOrder:
                    # Don't speak the label if just the checkbox state has
                    # changed.
                    #
                    if alreadyFocused and not hasToggle[i]:
                        pass
                    else:
                        utterances.extend( \
                            self._getTutorialForTableCell(AXObject.get_child(obj, i),
                            alreadyFocused, forceTutorial))
                return utterances

        # [[[TODO: WDW - Attempt to infer the cell type.  There's a
        # bunch of stuff we can do here, such as check the EXPANDABLE
        # state, check the NODE_CHILD_OF relation, etc.  Logged as
        # bugzilla bug 319750.]]]
        #
        if self._script.utilities.hasMeaningfulToggleAction(obj):
            utterances = self._getTutorialForCheckBox(
                obj, alreadyFocused, forceTutorial)

        if AXUtilities.is_expandable(obj):
            if AXUtilities.is_expanded(obj):
                if self.lastTutorial != [expandedMsg] or forceTutorial:
                    utterances.append(expandedMsg)
            else:
                if self.lastTutorial != [collapsedMsg] or forceTutorial:
                    utterances.append(collapsedMsg)

        self._debugGenerator("_getTutorialForTableCell",
                             obj,
                             alreadyFocused,
                             utterances)

        return utterances

    def _getTutorialForTableCellRow(self, obj, alreadyFocused, forceTutorial):
        """Get the tutorial string for the active table cell in the table row.

        Arguments:
        - obj: the table
        - alreadyFocused: False if object just received focus
        - forceTutorial: used for when whereAmI really needs the tutorial string

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []

        if (not alreadyFocused):
            parent = AXObject.get_parent(obj)
            try:
                parent_table = parent.queryTable()
            except Exception:
                parent_table = None
            readFullRow = self._script.utilities.shouldReadFullRow(obj)
            if readFullRow and parent_table and not self._script.utilities.isLayoutOnly(parent):
                utterances.extend(self._getTutorialForTableCell(obj,
                                                                alreadyFocused, forceTutorial))
            else:
                utterances = self._getTutorialForTableCell(obj, alreadyFocused, forceTutorial)
        else:
            utterances = self._getTutorialForTableCell(obj, alreadyFocused, \
              forceTutorial)

        self._debugGenerator("_getTutorialForTableCellRow",
                             obj,
                             alreadyFocused,
                             utterances)

        return utterances

    def _getTutorialForRadioButton(self, obj, alreadyFocused, forceTutorial):
        """Get the tutorial string for a radio button.

        Arguments:
        - obj: the radio button
        - alreadyFocused: False if object just received focus
        - forceTutorial: used for when whereAmI really needs the tutorial string

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []
        # Translators: this is a tip for the user, how to navigate radiobuttons.
        msg = _("Use arrow keys to change.")

        if (not alreadyFocused and self.lastTutorial != [msg]) \
           or forceTutorial:
            utterances.append(msg)

        self._debugGenerator("_getTutorialForRadioButton",
                             obj,
                             alreadyFocused,
                             utterances)
        return utterances

    def _getTutorialForMenu(self, obj, alreadyFocused, forceTutorial):
        """Get the tutorial string for a menu.

        Arguments:
        - obj: the menu
        - alreadyFocused: False if object just received focus
        - forceTutorial: used for when whereAmI really needs the tutorial string

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []
        # Translators: this is a tip for the user, how to navigate menus.
        mainMenuMsg = _("To navigate, press left or right arrow. " \
                       "To move through items press up or down arrow.")

        # Translators: this is a tip for the user, how to
        # navigate into sub menus.
        subMenuMsg = _("To enter sub menu, press right arrow.")

        # Checking if we are a submenu,
        # we can't rely on our parent being just a menu.
        # TODO - JD: What exactly are the __class__ checks for? All accessible objects
        # have the same class. Should this be checking the role instead?
        parent = AXObject.get_parent(obj)
        if AXObject.get_name(parent) and parent.__class__ == obj.__class__:
            if (self.lastTutorial != [subMenuMsg]) or forceTutorial:
                utterances.append(subMenuMsg)
        else:
            if (self.lastTutorial != [mainMenuMsg]) or forceTutorial:
                utterances.append(mainMenuMsg)

        self._debugGenerator("_getTutorialForMenu",
                             obj,
                             alreadyFocused,
                             utterances)
        return utterances

    def _getTutorialForSlider(self, obj, alreadyFocused, forceTutorial):
        """Get the tutorial string for a slider.  If the object already has
        focus, then no tutorial is given.

        Arguments:
        - obj: the slider
        - alreadyFocused: False if object just received focus
        - forceTutorial: used for when whereAmI really needs the tutorial string

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []
        # Translators: this is the tutorial string for when landing
        # on a slider.
        msg = _("To decrease press left arrow, to increase press right arrow." \
          " To go to minimum press home, and for maximum press end.")

        if (not alreadyFocused and self.lastTutorial != [msg]) \
           or forceTutorial:
            utterances.append(msg)

        self._debugGenerator("_getTutorialForSlider",
                             obj,
                             alreadyFocused,
                             utterances)

        return utterances

    def _getBindingsForHandler(self, handlerName):
        handler = self._script.inputEventHandlers.get(handlerName)
        if not handler:
            return None

        bindings = self._script.keyBindings.getBindingsForHandler(handler)
        if not bindings:
            return None

        binding = bindings[0]
        return binding.asString()

    def _getModeTutorial(self, obj, alreadyFocused, forceTutorial):
        return []

    def getTutorial(self, obj, alreadyFocused, forceTutorial=False, role=None):
        """Get the tutorial for an Accessible object.  This will look
        first to the specific tutorial generators and if this
        does not exist then return the empty tutorial.
        This method is the primary method
        that external callers of this class should use.

        Arguments:
        - obj: the object
        - alreadyFocused: False if object just received focus
        - forceTutorial: used for when whereAmI really needs the tutorial string
        - role: Alternative role to use

        Returns a list of utterances to be spoken.
        """

        if not settings.enableTutorialMessages:
            return []

        if not (obj and obj == orca_state.locusOfFocus):
            return []

        # Widgets in document content don't necessarily have the same interaction
        # as native toolkits. Because we can't know for certain what a keystroke
        # will do, better to say nothing than to risk confusing the user with
        # bogus info.
        if self._script.utilities.inDocumentContent(obj):
            msg = f"INFO: Not generating tutorial for document object {obj}."
            debug.println(debug.LEVEL_INFO, msg, True)
            return []

        utterances = []
        role = role or AXObject.get_role(obj)
        msg = self._getModeTutorial(obj, alreadyFocused, forceTutorial)
        if not msg:
            if role in self.tutorialGenerators:
                generator = self.tutorialGenerators[role]
            else:
                generator = self._getDefaultTutorial
            msg = generator(obj, alreadyFocused, forceTutorial)
        if msg == self.lastTutorial and role == self.lastRole \
             and not forceTutorial:
            msg = []
        if msg:
            utterances = [" ".join(msg)]
            self.lastTutorial = msg
            self.lastRole = role
        if forceTutorial:
            self.lastTutorial = ""
            self.lastRole = None

        self._debugGenerator("getTutorial",
                             obj,
                             alreadyFocused,
                             utterances)
        return utterances
