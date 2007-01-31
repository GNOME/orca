# Orca
#
# Copyright 2005-2007 Sun Microsystems Inc.
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

"""Utilities for obtaining speech utterances for objects.  In general,
there probably should be a singleton instance of the SpeechGenerator
class.  For those wishing to override the speech generators, however,
one can create a new instance and replace/extend the speech generators
as they see fit."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2006 Sun Microsystems Inc."
__license__   = "LGPL"

import math

import atspi
import debug
import orca_state
import rolenames
import settings
import util

from orca_i18n import _                          # for gettext support

class SpeechGenerator:
    """Takes accessible objects and produces a string to speak for
    those objects.  See the getSpeech method, which is the primary
    entry point.  Subclasses can feel free to override/extend the
    speechGenerators instance field as they see fit."""

    def __init__(self, script):

        # The script that created us.  This allows us to ask the
        # script for information if we need it.
        #
        self._script = script

        # Set up a dictionary that maps role names to functions
        # that generate speech for objects that implement that role.
        #
        self.speechGenerators = {}
        self.speechGenerators[rolenames.ROLE_ALERT]               = \
             self._getSpeechForAlert
        self.speechGenerators[rolenames.ROLE_ANIMATION]           = \
             self._getSpeechForAnimation
        self.speechGenerators[rolenames.ROLE_ARROW]               = \
             self._getSpeechForArrow
        self.speechGenerators[rolenames.ROLE_CHECK_BOX]           = \
             self._getSpeechForCheckBox
        self.speechGenerators[rolenames.ROLE_CHECK_MENU]          = \
             self._getSpeechForCheckMenuItem
        self.speechGenerators[rolenames.ROLE_CHECK_MENU_ITEM]     = \
             self._getSpeechForCheckMenuItem
        self.speechGenerators[rolenames.ROLE_COLUMN_HEADER]       = \
             self._getSpeechForColumnHeader
        self.speechGenerators[rolenames.ROLE_COMBO_BOX]           = \
             self._getSpeechForComboBox
        self.speechGenerators[rolenames.ROLE_DESKTOP_ICON]        = \
             self._getSpeechForDesktopIcon
        self.speechGenerators[rolenames.ROLE_DIAL]                = \
             self._getSpeechForDial
        self.speechGenerators[rolenames.ROLE_DIALOG]              = \
             self._getSpeechForDialog
        self.speechGenerators[rolenames.ROLE_DIRECTORY_PANE]      = \
             self._getSpeechForDirectoryPane
        self.speechGenerators[rolenames.ROLE_FRAME]               = \
             self._getSpeechForFrame
        self.speechGenerators[rolenames.ROLE_HTML_CONTAINER]      = \
             self._getSpeechForHtmlContainer
        self.speechGenerators[rolenames.ROLE_ICON]                = \
             self._getSpeechForIcon
        self.speechGenerators[rolenames.ROLE_IMAGE]               = \
             self._getSpeechForImage
        self.speechGenerators[rolenames.ROLE_LABEL]               = \
             self._getSpeechForLabel
        self.speechGenerators[rolenames.ROLE_LAYERED_PANE]        = \
             self._getSpeechForLayeredPane
        self.speechGenerators[rolenames.ROLE_LIST]                = \
             self._getSpeechForList
        self.speechGenerators[rolenames.ROLE_MENU]                = \
             self._getSpeechForMenu
        self.speechGenerators[rolenames.ROLE_MENU_BAR]            = \
             self._getSpeechForMenuBar
        self.speechGenerators[rolenames.ROLE_MENU_ITEM]           = \
             self._getSpeechForMenuItem
        self.speechGenerators[rolenames.ROLE_OPTION_PANE]         = \
             self._getSpeechForOptionPane
        self.speechGenerators[rolenames.ROLE_PAGE_TAB]            = \
             self._getSpeechForPageTab
        self.speechGenerators[rolenames.ROLE_PAGE_TAB_LIST]       = \
             self._getSpeechForPageTabList
        self.speechGenerators[rolenames.ROLE_PARAGRAPH]           = \
             self._getSpeechForText
        self.speechGenerators[rolenames.ROLE_PASSWORD_TEXT]       = \
             self._getSpeechForText
        self.speechGenerators[rolenames.ROLE_PROGRESS_BAR]        = \
             self._getSpeechForProgressBar
        self.speechGenerators[rolenames.ROLE_PUSH_BUTTON]         = \
             self._getSpeechForPushButton
        self.speechGenerators[rolenames.ROLE_RADIO_BUTTON]        = \
             self._getSpeechForRadioButton
        self.speechGenerators[rolenames.ROLE_RADIO_MENU]          = \
             self._getSpeechForRadioMenuItem
        self.speechGenerators[rolenames.ROLE_RADIO_MENU_ITEM]     = \
             self._getSpeechForRadioMenuItem
        self.speechGenerators[rolenames.ROLE_ROW_HEADER]          = \
             self._getSpeechForRowHeader
        self.speechGenerators[rolenames.ROLE_SCROLL_BAR]          = \
             self._getSpeechForScrollBar
        self.speechGenerators[rolenames.ROLE_SLIDER]              = \
             self._getSpeechForSlider
        self.speechGenerators[rolenames.ROLE_SPIN_BUTTON]         = \
             self._getSpeechForSpinButton
        self.speechGenerators[rolenames.ROLE_SPLIT_PANE]          = \
             self._getSpeechForSplitPane
        self.speechGenerators[rolenames.ROLE_TABLE]               = \
             self._getSpeechForTable
        self.speechGenerators[rolenames.ROLE_TABLE_CELL]          = \
             self._getSpeechForTableCellRow
        self.speechGenerators[rolenames.ROLE_TABLE_COLUMN_HEADER] = \
             self._getSpeechForTableColumnHeader
        self.speechGenerators[rolenames.ROLE_TABLE_ROW_HEADER]    = \
             self._getSpeechForTableRowHeader
        self.speechGenerators[rolenames.ROLE_TEAR_OFF_MENU_ITEM]  = \
             self._getSpeechForMenu
        self.speechGenerators[rolenames.ROLE_TERMINAL]            = \
             self._getSpeechForTerminal
        self.speechGenerators[rolenames.ROLE_TEXT]                = \
             self._getSpeechForText
        self.speechGenerators[rolenames.ROLE_TOGGLE_BUTTON]       = \
             self._getSpeechForToggleButton
        self.speechGenerators[rolenames.ROLE_TOOL_BAR]            = \
             self._getSpeechForToolBar
        self.speechGenerators[rolenames.ROLE_TREE]                = \
             self._getSpeechForTable
        self.speechGenerators[rolenames.ROLE_TREE_TABLE]          = \
             self._getSpeechForTable
        self.speechGenerators[rolenames.ROLE_WINDOW]              = \
             self._getSpeechForWindow

    def _getSpeechForObjectAccelerator(self, obj):
        """Returns a list of utterances that describes the keyboard
        accelerator (and possibly shortcut) for the given object.

        Arguments:
        - obj: the Accessible object

        Returns a list of utterances to be spoken.
        """

        result = util.getAcceleratorAndShortcut(obj)

        accelerator = result[0]
        #shortcut = result[1]

        utterances = []

        # [[[TODO: WDW - various stuff preserved while we work out the
        # desired verbosity here.]]]
        #
        #if len(shortcut) > 0:
        #    utterances.append(_("shortcut") + " " + shortcut)
        #    utterances.append(accelerator)
        if len(accelerator) > 0:
            #utterances += (_("accelerator") + " " + accelerator)
            utterances.append(accelerator)

        return utterances

    def _getSpeechForObjectAvailability(self, obj):
        """Returns a list of utterances that describes the availability
        of the given object.

        Arguments:
        - obj: the Accessible object

        Returns a list of utterances to be spoken.
        """
        if obj.state.count(atspi.Accessibility.STATE_SENSITIVE) == 0:
            return [_("grayed")]
        else:
            return []

    def _getSpeechForObjectLabel(self, obj):
        label = util.getDisplayedLabel(obj)
        if label:
            return [label]
        else:
            return []

    def _getSpeechForObjectName(self, obj):
        name = util.getDisplayedText(obj)
        if name:
            return [name]
        elif obj.description:
            return [obj.description]
        else:
            return []

    def _getSpeechForObjectRole(self, obj):
        if (obj.role != rolenames.ROLE_UNKNOWN):
            return [rolenames.getSpeechForRoleName(obj)]
        else:
            return []

    def _debugGenerator(self, generatorName, obj, already_focused, utterances):
        """Prints debug.LEVEL_FINER information regarding the speech generator.

        Arguments:
        - generatorName: the name of the generator
        - obj: the object being presented
        - already_focused: False if object just received focus
        - utterances: the generated text
        """

        debug.println(debug.LEVEL_FINER,
                      "GENERATOR: %s" % generatorName)
        debug.println(debug.LEVEL_FINER,
                      "           obj             = %s" % obj.name)
        debug.println(debug.LEVEL_FINER,
                      "           role            = %s" % obj.role)
        debug.println(debug.LEVEL_FINER,
                      "           already_focused = %s" % already_focused)
        debug.println(debug.LEVEL_FINER,
                      "           utterances:")
        for text in utterances:
            debug.println(debug.LEVEL_FINER,
                      "               (%s)" % text)

    def _getDefaultSpeech(self, obj, already_focused):
        """Gets a list of utterances to be spoken for the current
        object's name, role, and any accelerators.  This is usually the
        fallback speech generator should no other specialized speech
        generator exist for this object.

        The default speech will be of the following form:

        label name role availability

        Arguments:
        - obj: an Accessible
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []

        if not already_focused:
            label = self._getSpeechForObjectLabel(obj)
            utterances.extend(label)
            name = self._getSpeechForObjectName(obj)
            if name != label:
                utterances.extend(name)
            utterances.extend(self._getSpeechForObjectRole(obj))

        utterances.extend(self._getSpeechForObjectAvailability(obj))

        self._debugGenerator("_getDefaultSpeech",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForAlert(self, obj, already_focused):
        """Gets the title of the dialog and the contents of labels inside the
        dialog that are not associated with any other objects.

        Arguments:
        - obj: the Accessible dialog
        - already_focused: False if object just received focus

        Returns a list of utterances be spoken.
        """

        utterances = []
        label = self._getSpeechForObjectLabel(obj)
        utterances.extend(label)
        name = self._getSpeechForObjectName(obj)
        if name != label:
            utterances.extend(name)

        # Find all the unrelated labels in the dialog and speak them.
        #
        labels = util.findUnrelatedLabels(obj)
        for label in labels:
            utterances.append(label.name)

        self._debugGenerator("_getSpeechForAlert",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForAnimation(self, obj, already_focused):
        """Gets the speech for an animation.

        Arguments:
        - obj: the animation
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken.
        """

        utterances = []
        label = self._getSpeechForObjectLabel(obj)
        utterances.extend(label)
        name = self._getSpeechForObjectName(obj)
        if name != label:
            utterances.extend(name)

        self._debugGenerator("_getSpeechForAnimation",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForArrow(self, obj, already_focused):
        """Gets a list of utterances to be spoken for an arrow.

        Arguments:
        - obj: the arrow
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        # [[[TODO: determine orientation of arrow.  Logged as bugzilla bug
        # 319744.]]]
        # text = arrow direction (left, right, up, down)
        #
        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForArrow",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForCheckBox(self, obj, already_focused):
        """Get the speech for a check box.  If the check box already had
        focus, then only the state is spoken.

        Arguments:
        - obj: the check box
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []
        if obj.state.count(atspi.Accessibility.STATE_CHECKED):
            checkedState = _("checked")
        else:
            checkedState = _("not checked")

        # If it's not already focused, say it's name
        #
        if not already_focused:
            label = self._getSpeechForObjectLabel(obj)
            utterances.extend(label)
            name = self._getSpeechForObjectName(obj)
            if name != label:
                utterances.extend(name)
            utterances.extend(self._getSpeechForObjectRole(obj))
            utterances.append(checkedState)
            utterances.extend(self._getSpeechForObjectAvailability(obj))
        else:
            utterances.append(checkedState)

        self._debugGenerator("_getSpeechForCheckBox",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForCheckMenuItem(self, obj, already_focused):
        """Get the speech for a check menu item.  If the check menu item
        already had focus, then only the state is spoken.

        Arguments:
        - obj: the check menu item
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getSpeechForCheckBox(obj, already_focused)

        if (settings.speechVerbosityLevel == settings.VERBOSITY_LEVEL_VERBOSE)\
           and not already_focused:
            utterances.extend(self._getSpeechForObjectAccelerator(obj))

        self._debugGenerator("_getSpeechForCheckMenuItem",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForColumnHeader(self, obj, already_focused):
        """Get the speech for a column header.

        Arguments:
        - obj: the column header
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForColumnHeader",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForComboBox(self, obj, already_focused):
        """Get the speech for a combo box.  If the combo box already has focus,
        then only the selection is spoken.

        Arguments:
        - obj: the combo box
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []

        if not already_focused:
            label = self._getSpeechForObjectLabel(obj)
            utterances.extend(label)
        else:
            label = None

        name = self._getSpeechForObjectName(obj)
        if name != label:
            utterances.extend(name)

        if not already_focused:
            utterances.extend(self._getSpeechForObjectRole(obj))

        utterances.extend(self._getSpeechForObjectAvailability(obj))

        self._debugGenerator("_getSpeechForComboBox",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForDesktopIcon(self, obj, already_focused):
        """Get the speech for a desktop icon.

        Arguments:
        - obj: the desktop icon
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForDesktopIcon",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForDial(self, obj, already_focused):
        """Get the speech for a dial.

        Arguments:
        - obj: the dial
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        # [[[TODO: WDW - might need to include the value here?  Logged as
        # bugzilla bug 319746.]]]
        #
        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForDial",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForDialog(self, obj, already_focused):
        """Get the speech for a dialog box.

        Arguments:
        - obj: the dialog box
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getSpeechForAlert(obj, already_focused)

        self._debugGenerator("_getSpeechForDialog",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForDirectoryPane(self, obj, already_focused):
        """Get the speech for a directory pane.

        Arguments:
        - obj: the dial
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForDirectoryPane",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForFrame(self, obj, already_focused):
        """Get the speech for a frame.

        Arguments:
        - obj: the frame
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        # [[[TODO: richb - readjusted to just get the default speech instead
        # of treating the frame like an alert and speaking all unrelated
        # labels. We'll need to see if this has any adverse effects and
        # adjust accordingly.]]]
        #
        utterances = self._getDefaultSpeech(obj, already_focused)
        #utterances = self._getSpeechForAlert(obj, already_focused)

        self._debugGenerator("_getSpeechForFrame",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForHtmlContainer(self, obj, already_focused):
        """Get the speech for an HTML container.

        Arguments:
        - obj: the dial
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForHtmlContainer",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForIcon(self, obj, already_focused):
        """Get the speech for an icon.

        Arguments:
        - obj: the icon
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        # [[[TODO: WDW - HACK to remove availability output because nautilus
        # doesn't include this information for desktop icons.  If, at some
        # point, it is determined that availability should be added back in,
        # then a custom script for nautilus needs to be written to remove the
        # availability.]]]
        #
        utterances = []
        label = self._getSpeechForObjectLabel(obj)
        utterances.extend(label)
        name = self._getSpeechForObjectName(obj)
        if name != label:
            utterances.extend(name)

        if obj.image:
            description = obj.image.imageDescription
            if description and len(description):
                utterances.append(description)

        if settings.speechVerbosityLevel == settings.VERBOSITY_LEVEL_VERBOSE:
            utterances.append(rolenames.getSpeechForRoleName(obj))

        self._debugGenerator("_getSpeechForIcon",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForImage(self, obj, already_focused):
        """Get the speech for an image.

        Arguments:
        - obj: the image
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForImage",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForLabel(self, obj, already_focused):
        """Get the speech for a label.

        Arguments:
        - obj: the label
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForLabel",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForLayeredPane(self, obj, already_focused):
        """Get the speech for a layered pane

        Arguments:
        - obj: the table
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForLayeredPane",
                             obj,
                             already_focused,
                             utterances)

        # If this has no children, then let the user know.
        #
        hasItems = False
        for i in range(0, obj.childCount):
            child = obj.child(i)
            if child.state.count(atspi.Accessibility.STATE_SHOWING):
                hasItems = True
                break
        if not hasItems:
            utterances.append(_("0 items"))

        return utterances

    def _getSpeechForList(self, obj, already_focused):
        """Get the speech for a list.

        Arguments:
        - obj: the list
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        # [[[TODO: WDW - include how many items in the list?
        # Logged as bugzilla bug 319749.]]]
        #
        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForList",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForMenu(self, obj, already_focused):
        """Get the speech for a menu.

        Arguments:
        - obj: the menu
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        if (obj == orca_state.locusOfFocus) \
               and (settings.speechVerbosityLevel \
                    == settings.VERBOSITY_LEVEL_VERBOSE):
            utterances.extend(self._getSpeechForObjectAccelerator(obj))

        self._debugGenerator("_getSpeechForMenu",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForMenuBar(self, obj, already_focused):
        """Get the speech for a menu bar.

        Arguments:
        - obj: the menu bar
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForMenuBar",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForMenuItem(self, obj, already_focused):
        """Get the speech for a menu item.

        Arguments:
        - obj: the menu item
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        # No need to say "menu item" because we already know that.
        #
        utterances = self._getSpeechForObjectName(obj)
        if settings.speechVerbosityLevel == settings.VERBOSITY_LEVEL_VERBOSE:
            utterances.extend(self._getSpeechForObjectAvailability(obj))
            utterances.extend(self._getSpeechForObjectAccelerator(obj))

        self._debugGenerator("_getSpeechForMenuItem",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForText(self, obj, already_focused):
        """Get the speech for a text component.

        Arguments:
        - obj: the text component
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        # [[[TODO: WDW - HACK to remove availability because some text
        # areas, such as those in yelp, come up as insensitive though
        # they really are ineditable.]]]
        #
        utterances = []
        utterances.extend(self._getSpeechForObjectLabel(obj))
        if len(utterances) == 0:
            if obj.name and (len(obj.name)):
                utterances.append(obj.name)
        if obj.role != rolenames.ROLE_PARAGRAPH:
            utterances.extend(self._getSpeechForObjectRole(obj))

        [text, caretOffset, startOffset] = util.getTextLineAtCaret(obj)
        utterances.append(text)

        self._debugGenerator("_getSpeechForText",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForOptionPane(self, obj, already_focused):
        """Get the speech for an option pane.

        Arguments:
        - obj: the option pane
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForOptionPane",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForPageTab(self, obj, already_focused):
        """Get the speech for a page tab.

        Arguments:
        - obj: the page tab
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForPageTab",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForPageTabList(self, obj, already_focused):
        """Get the speech for a page tab list.

        Arguments:
        - obj: the page tab list
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        #if obj.childCount == 1:
        #    utterances.append(_("one tab"))
        #else:
        #    utterances.append(("%d " % obj.childCount) + _("tabs"))

        self._debugGenerator("_getSpeechForPageTabList",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForProgressBar(self, obj, already_focused):
        """Get the speech for a progress bar.  If the object already
        had focus, just the new value is spoken.

        Arguments:
        - obj: the progress bar
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        percentage = ("%d" % obj.value.currentValue) + " " \
                     + _("percent") + ". "

        utterances = []

        if not already_focused:
            label = self._getSpeechForObjectLabel(obj)
            utterances.extend(label)
            name = self._getSpeechForObjectName(obj)
            if name != label:
                utterances.extend(name)
            utterances.extend(self._getSpeechForObjectRole(obj))

        utterances.append(percentage)

        self._debugGenerator("_getSpeechForProgressBar",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForPushButton(self, obj, already_focused):
        """Get the speech for a push button

        Arguments:
        - obj: the push button
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForPushButton",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForRadioButton(self, obj, already_focused):
        """Get the speech for a radio button.  If the button already had
        focus, then only the state is spoken.

        Arguments:
        - obj: the check box
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []
        if obj.state.count(atspi.Accessibility.STATE_CHECKED):
            selectionState = _("selected")
        else:
            selectionState = _("not selected")

        # If it's not already focused, say it's name
        #
        if not already_focused:
            # The label is handled as a context in default.py
            #
            #utterances.extend(self._getSpeechForObjectLabel(obj))
            utterances.extend(self._getSpeechForObjectName(obj))
            utterances.append(selectionState)
            utterances.extend(self._getSpeechForObjectRole(obj))
            utterances.extend(self._getSpeechForObjectAvailability(obj))
        else:
            utterances.append(selectionState)

        self._debugGenerator("_getSpeechForRadioButton",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForRadioMenuItem(self, obj, already_focused):
        """Get the speech for a radio menu item.  If the menu item
        already had focus, then only the state is spoken.

        Arguments:
        - obj: the check menu item
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getSpeechForRadioButton(obj, False)

        if settings.speechVerbosityLevel == settings.VERBOSITY_LEVEL_VERBOSE:
            utterances.extend(self._getSpeechForObjectAvailability(obj))
            utterances.extend(self._getSpeechForObjectAccelerator(obj))

        self._debugGenerator("_getSpeechForRadioMenuItem",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForRowHeader(self, obj, already_focused):
        """Get the speech for a row header.

        Arguments:
        - obj: the column header
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForRowHeader",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForScrollBar(self, obj, already_focused):
        """Get the speech for a scroll bar.

        Arguments:
        - obj: the scroll bar
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        # [[[TODO: WDW - want to get orientation and maybe the
        # percentage scrolled so far. Logged as bugzilla bug
        # 319744.]]]
        #
        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForScrollBar",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForSlider(self, obj, already_focused):
        """Get the speech for a slider.  If the object already
        had focus, just the value is spoken.

        Arguments:
        - obj: the slider
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        value = obj.value

        # OK, this craziness is all about trying to figure out the most
        # meaningful formatting string for the floating point values.
        # The number of places to the right of the decimal point should
        # be set by the minimumIncrement, but the minimumIncrement isn't
        # always set.  So...we'll default the minimumIncrement to 1/100
        # of the range.  But, if max == min, then we'll just go for showing
        # them off to two meaningful digits.
        #
        try:
            minimumIncrement = value.minimumIncrement
        except:
            minimumIncrement = 0.0

        if minimumIncrement == 0.0:
            minimumIncrement = (value.maximumValue - value.minimumValue) \
                               / 100.0

        try:
            decimalPlaces = max(0, -math.log10(minimumIncrement))
        except:
            try:
                decimalPlaces = max(0, -math.log10(value.minimumValue))
            except:
                try:
                    decimalPlaces = max(0, -math.log10(value.maximumValue))
                except:
                    decimalPlaces = 0

        formatter = "%%.%df" % decimalPlaces
        valueString = formatter % value.currentValue
        #minString   = formatter % value.minimumValue
        #maxString   = formatter % value.maximumValue

        if already_focused:
            utterances = [valueString]
        else:
            utterances = []
            utterances.extend(self._getSpeechForObjectLabel(obj))

            # Ignore the text on the slider.  See bug 340559
            # (http://bugzilla.gnome.org/show_bug.cgi?id=340559): the
            # implementors of the slider support decided to put in a
            # Unicode left-to-right character as part of the text,
            # even though that is not painted on the screen.
            #
            # In Java, however, there are sliders without a label. In
            # this case, we'll add to presentation the slider name if
            # it exists and we haven't found anything yet.
            #
            if not utterances:
                utterances.extend(self._getSpeechForObjectName(obj))

            utterances.extend(self._getSpeechForObjectRole(obj))
            utterances.append(valueString)
            utterances.extend(self._getSpeechForObjectAvailability(obj))

        self._debugGenerator("_getSpeechForSlider",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForSpinButton(self, obj, already_focused):
        """Get the speech for a spin button.  If the object already has
        focus, then only the new value is spoken.

        Arguments:
        - obj: the spin button
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        if already_focused:
            utterances = [util.getDisplayedText(obj)]
        else:
            utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForSpinButton",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForSplitPane(self, obj, already_focused):
        """Get the speech for a split pane.

        Arguments:
        - obj: the split pane
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForSplitPane",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForTable(self, obj, already_focused):
        """Get the speech for a table

        Arguments:
        - obj: the table
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForTable",
                             obj,
                             already_focused,
                             utterances)

        # If this is a table with no children, then let the user know.
        #
        hasItems = False
        for i in range(0, obj.childCount):
            child = obj.child(i)
            if child.state.count(atspi.Accessibility.STATE_SHOWING):
                hasItems = True
                break
        if not hasItems:
            utterances.append(_("0 items"))

        return utterances

    def _getSpeechForTableCell(self, obj, already_focused):
        """Get the speech utterances for a single table cell

        Arguments:
        - obj: the table
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []

        # [[[TODO: WDW - Attempt to infer the cell type.  There's a
        # bunch of stuff we can do here, such as check the EXPANDABLE
        # state, check the NODE_CHILD_OF relation, etc.  Logged as
        # bugzilla bug 319750.]]]
        #
        action = obj.action
        if action:
            for i in range(0, action.nActions):
                debug.println(debug.LEVEL_FINEST,
                    "speechgenerator.__getTableCellUtterances " \
                    + "looking at action %d" % i)
                if action.getName(i) == "toggle":
                    obj.role = rolenames.ROLE_CHECK_BOX
                    utterances = self._getSpeechForCheckBox(obj,
                                                            already_focused)
                    obj.role = rolenames.ROLE_TABLE_CELL
                    break

        utterances.append(util.getDisplayedText(\
                          util.getRealActiveDescendant(obj)))

        # [[[TODO: WDW - HACK attempt to determine if this is a node;
        # if so, describe its state.]]]
        #
        if obj.state.count(atspi.Accessibility.STATE_EXPANDABLE):
            if obj.state.count(atspi.Accessibility.STATE_EXPANDED):
                utterances.append(_("expanded"))
            else:
                utterances.append(_("collapsed"))

            # If this is an expandable table cell with no children, then
            # let the user know.
            #
            if obj.childCount == 0:
                utterances.append(_("0 items"))

        self._debugGenerator("_getSpeechForTableCell",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForTableCellRow(self, obj, already_focused):
        """Get the speech for a table cell row or a single table cell
        if settings.readTableCellRow is False.

        Arguments:
        - obj: the table
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []

        if (not already_focused):
            if settings.readTableCellRow and obj.parent.table \
                and (not self._script.isLayoutOnly(obj.parent)):
                parent = obj.parent
                row = parent.table.getRowAtIndex(obj.index)
                column = parent.table.getColumnAtIndex(obj.index)

                # This is an indication of whether we should speak all the
                # table cells (the user has moved focus up or down a row),
                # or just the current one (focus has moved left or right in
                # the same row).
                #
                speakAll = True
                if parent.__dict__.has_key("lastRow") and \
                    parent.__dict__.has_key("lastColumn"):
                    speakAll = (parent.lastRow != row) or \
                           ((row == 0 or row == parent.table.nRows-1) and \
                            parent.lastColumn == column)

                if speakAll:
                    for i in range(0, parent.table.nColumns):
                        accRow = parent.table.getAccessibleAt(row, i)
                        cell = atspi.Accessible.makeAccessible(accRow)
                        showing = cell.state.count( \
                                          atspi.Accessibility.STATE_SHOWING)
                        if showing:
                            utterances.extend(self._getSpeechForTableCell(cell,
                                                           already_focused))
                else:
                    utterances.extend(self._getSpeechForTableCell(obj,
                                                           already_focused))
            else:
                utterances = self._getSpeechForTableCell(obj, already_focused)
        else:
            utterances = self._getSpeechForTableCell(obj, already_focused)

        self._debugGenerator("_getSpeechForTableCellRow",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForTableColumnHeader(self, obj, already_focused):
        """Get the speech for a table column header

        Arguments:
        - obj: the table column header
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getSpeechForColumnHeader(obj, already_focused)

        self._debugGenerator("_getSpeechForTableColumnHeader",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForTableRowHeader(self, obj, already_focused):
        """Get the speech for a table row header

        Arguments:
        - obj: the table row header
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getSpeechForRowHeader(obj, already_focused)

        self._debugGenerator("_getSpeechForTableRowHeader",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForTearOffMenuItem(self, obj, already_focused):
        """Get the speech for a tear off menu item

        Arguments:
        - obj: the tear off menu item
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        if settings.speechVerbosityLevel == settings.VERBOSITY_LEVEL_VERBOSE:
            utterances = [_("tear off menu item")]
        else:
            utterances = [_("tear off")]

        self._debugGenerator("_getSpeechForTearOffMenuItem",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForTerminal(self, obj, already_focused):
        """Get the speech for a terminal

        Arguments:
        - obj: the terminal
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        title = None
        frame = util.getFrame(obj)
        if frame:
            title = frame.name
        if not title:
            title = util.getDisplayedLabel(obj)

        utterances = [title]

        self._debugGenerator("_getSpeechForTerminal",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForToggleButton(self, obj, already_focused):
        """Get the speech for a toggle button.  If the toggle button already
        had focus, then only the state is spoken.

        Arguments:
        - obj: the check box
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []
        if obj.state.count(atspi.Accessibility.STATE_CHECKED):
            checkedState = _("pressed")
        else:
            checkedState = _("not pressed")

        # If it's not already focused, say it's name
        #
        if not already_focused:
            label = self._getSpeechForObjectLabel(obj)
            utterances.extend(label)
            name = self._getSpeechForObjectName(obj)
            if name != label:
                utterances.extend(name)
            utterances.extend(self._getSpeechForObjectRole(obj))
            utterances.append(checkedState)
            utterances.extend(self._getSpeechForObjectAvailability(obj))
        else:
            utterances.append(checkedState)

        self._debugGenerator("_getSpeechForToggleButton",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForToolBar(self, obj, already_focused):
        """Get the speech for a tool bar

        Arguments:
        - obj: the tool bar
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForToolBar",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForTree(self, obj, already_focused):
        """Get the speech for a tree

        Arguments:
        - obj: the tree
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForTree",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForTreeTable(self, obj, already_focused):
        """Get the speech for a tree table

        Arguments:
        - obj: the tree table
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForTreeTable",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForWindow(self, obj, already_focused):
        """Get the speech for a window

        Arguments:
        - obj: the window
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = self._getDefaultSpeech(obj, already_focused)

        self._debugGenerator("_getSpeechForWindow",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def getSpeech(self, obj, already_focused):
        """Get the speech for an Accessible object.  This will look
        first to the specific speech generators and then to the
        default speech generator.  This method is the primary method
        that external callers of this class should use.

        Arguments:
        - obj: the object
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken.
        """

        if self.speechGenerators.has_key(obj.role):
            generator = self.speechGenerators[obj.role]
        else:
            generator = self._getDefaultSpeech

        return [" ".join(generator(obj, already_focused))]

    def getSpeechContext(self, obj, stopAncestor=None):
        """Get the speech that describes the names and role of
        the container hierarchy of the object, stopping at and
        not including the stopAncestor.

        Arguments:
        - obj: the object
        - stopAncestor: the anscestor to stop at and not include (None
          means include all ancestors)

        Returns a list of utterances to be spoken.
        """

        utterances = []

        if not obj:
            return utterances

        if obj is stopAncestor:
            return utterances

        # We try to ignore fillers and panels without names.
        # [[[TODO: WDW - HACK sometimes table cells can be children
        # of table cells (see the "Browse" dialog of gnome-terminal
        # via "Edit" -> "Current Profile" -> "General" Tab ->
        # "Profile icon:" button -> "Browse..." button - each element
        # in the list is a compound table cell where the icon and
        # text are child table cells of the table cell).  So...
        # we happily ignore those as well.  One thing we might
        # want to do is treat the parent as a compound object.
        # Logged as bugzilla bug 319751.]]]
        #
        parent = obj.parent
        if parent \
            and (obj.role == rolenames.ROLE_TABLE_CELL) \
            and (parent.role == rolenames.ROLE_TABLE_CELL):
            parent = parent.parent

        while parent and (parent.parent != parent):
            if parent == stopAncestor:
                break
            if (parent.role != rolenames.ROLE_FILLER) \
                and (parent.role != rolenames.ROLE_SECTION) \
                and (parent.role != rolenames.ROLE_LAYERED_PANE) \
                and (parent.role != rolenames.ROLE_SPLIT_PANE) \
                and (parent.role != rolenames.ROLE_SCROLL_PANE) \
                and (parent.role != rolenames.ROLE_UNKNOWN) \
                and (not self._script.isLayoutOnly(parent)):

                # Announce the label and text of the object in the hierarchy.
                #
                text = util.getDisplayedText(parent)
                label = util.getDisplayedLabel(parent)

                # Push announcement of cell after text and label.
                #
                if parent.role != rolenames.ROLE_TABLE_CELL:
                    utterances.append(rolenames.getSpeechForRoleName(parent))

                if text and len(text):
                    utterances.append(text)
                if label and len(label):
                    utterances.append(label)

                if parent.role == rolenames.ROLE_TABLE_CELL:
                    utterances.append(rolenames.getSpeechForRoleName(parent))

            # [[[TODO: HACK - we've discovered oddness in hierarchies
            # such as the gedit Edit->Preferences dialog.  In this
            # dialog, we have labeled groupings of objects.  The
            # grouping is done via a FILLER with two children - one
            # child is the overall label, and the other is the
            # container for the grouped objects.  When we detect this,
            # we add the label to the overall context.]]]
            #
            if parent.role == rolenames.ROLE_FILLER:
                label = util.getDisplayedLabel(parent)
                if label and len (label):
                    utterances.append(label)

            parent = parent.parent

        utterances.reverse()

        return utterances
