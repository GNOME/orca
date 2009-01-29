# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
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

"""Custom script for Gecko toolkit.
Please refer to the following URL for more information on the AT-SPI
implementation in Gecko:
http://developer.mozilla.org/en/docs/Accessibility/ATSPI_Support
"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.rolenames as rolenames
import orca.settings as settings
import orca.speechgenerator as speechgenerator

from orca.orca_i18n import _
from orca.orca_i18n import ngettext # for ngettext support
from orca.orca_i18n import C_       # to provide qualified translatable strings

########################################################################
#                                                                      #
# Custom SpeechGenerator                                               #
#                                                                      #
########################################################################

class SpeechGenerator(speechgenerator.SpeechGenerator):
    """Provides a speech generator specific to Gecko.
    """

    def __init__(self, script):
        speechgenerator.SpeechGenerator.__init__(self, script)
        self.speechGenerators[pyatspi.ROLE_DOCUMENT_FRAME] = \
             self._getSpeechForDocumentFrame
        self.speechGenerators[pyatspi.ROLE_ENTRY]          = \
             self._getSpeechForText
        self.speechGenerators[pyatspi.ROLE_LINK]           = \
             self._getSpeechForLink
        self.speechGenerators[pyatspi.ROLE_LIST_ITEM]      = \
             self._getSpeechForListItem
        self.speechGenerators[pyatspi.ROLE_SLIDER]         = \
             self._getSpeechForSlider

    def getSpeechForObjectRole(self, obj, role=None):
        """Prevents some roles from being spoken."""
        doNotSpeak = [pyatspi.ROLE_FORM,
                      pyatspi.ROLE_LABEL,
                      pyatspi.ROLE_MENU_ITEM,
                      pyatspi.ROLE_PARAGRAPH,
                      pyatspi.ROLE_SECTION,
                      pyatspi.ROLE_UNKNOWN]

        if self._script.inDocumentContent(obj):
            doNotSpeak.append(pyatspi.ROLE_TABLE_CELL)
            if not self._script.isAriaWidget(obj):
                doNotSpeak.append(pyatspi.ROLE_LIST_ITEM)
                doNotSpeak.append(pyatspi.ROLE_LIST)

        utterances = []
        if role or not obj.getRole() in doNotSpeak:
            utterances.append(rolenames.getSpeechForRoleName(obj, role))
            if obj.getRole() == pyatspi.ROLE_HEADING:
                level = self._script.getHeadingLevel(obj)
                if level:
                    # Translators: this is in reference to a heading level
                    # in HTML (e.g., For <h3>, the level is 3).
                    #
                    utterances.append(_("level %d") % level)

        return utterances

    def _getSpeechForDocumentFrame(self, obj, already_focused):
        """Gets the speech for a document frame.

        Arguments:
        - obj: an Accessible
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []

        name = obj.name
        if name and len(name):
            utterances.append(name)
        utterances.extend(self.getSpeechForObjectRole(obj))

        self._debugGenerator("Gecko._getSpeechForDocumentFrame",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForText(self, obj, already_focused):
        """Gets the speech for an autocomplete box.

        Arguments:
        - obj: an Accessible
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        # Treat ARIA widgets like default.py widgets
        #
        if self._script.isAriaWidget(obj):
            return speechgenerator.SpeechGenerator.\
                       _getSpeechForText(self, obj, already_focused)
        
        utterances = []
        parent = obj.parent
        if parent.getRole() == pyatspi.ROLE_AUTOCOMPLETE:
            # This is the main difference between this class and the default
            # class - we'll give this thing a name here, and we'll make it
            # be the name of the autocomplete.
            #
            label = self._script.getDisplayedLabel(parent)
            if not label or not len(label):
                label = parent.name
            utterances.append(label)
        elif obj.getRole() in [pyatspi.ROLE_ENTRY,
                               pyatspi.ROLE_PASSWORD_TEXT] \
            and self._script.inDocumentContent():
            # This is a form field in web content.  If we don't get a label,
            # we'll try to guess what text on the page is functioning as
            # the label.
            #
            label = self._script.getDisplayedLabel(obj)
            if not label or not len(label):
                label = self._script.guessTheLabel(obj)
            if label:
                utterances.append(label)
        else:
            return speechgenerator.SpeechGenerator._getSpeechForText(
                self, obj, already_focused)

        if settings.presentReadOnlyText \
           and self._script.isReadOnlyTextArea(obj):
            utterances.append(settings.speechReadOnlyString)

        utterances.extend(self.getSpeechForObjectRole(obj))

        [text, caretOffset, startOffset] = self._script.getTextLineAtCaret(obj)
        utterances.append(text)

        self._debugGenerator("Gecko._getSpeechForText",
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

        # Treat ARIA widgets like default.py widgets
        #
        if self._script.isAriaWidget(obj):
            return speechgenerator.SpeechGenerator.\
                       _getSpeechForComboBox(self, obj, already_focused)
        
        utterances = []

        label = self._script.getDisplayedLabel(obj)
        if not label:
            if not self._script.inDocumentContent():
                label = obj.name
            else:
                label = self._script.guessTheLabel(obj)

        if not already_focused and label:
            utterances.append(label)

        # With Gecko, a combo box has a menu as a child.  The text being
        # displayed for the combo box can be obtained via the selected
        # menu item.
        #
        menu = None
        for child in obj:
            if child.getRole() == pyatspi.ROLE_MENU:
                menu = child
                break
        if menu:
            child = None
            try:
                # This should work...
                #
                child = menu.querySelection().getSelectedChild(0)
                if not child:
                    # It's probably a Gtk combo box.
                    #
                    return speechgenerator.SpeechGenerator.\
                        _getSpeechForComboBox(self, obj, already_focused)
            except:
                # But just in case, we'll fall back on this.
                # [[[TODO - JD: Will we ever have a case where the first
                # fails, but this will succeed???]]]
                #
                for item in menu:
                    if item.getState().contains(pyatspi.STATE_SELECTED):
                        child = item
                        break
            if child:
                utterances.append(child.name)

        utterances.extend(self._getSpeechForObjectAvailability(obj))

        if not already_focused:
            utterances.extend(self.getSpeechForObjectRole(obj))

        self._debugGenerator("Gecko._getSpeechForComboBox",
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

        # Treat ARIA widgets like default.py widgets
        #
        if self._script.isAriaWidget(obj):
            return speechgenerator.SpeechGenerator.\
                       _getSpeechForMenuItem(self, obj, already_focused)
        
        if not self._script.inDocumentContent():
            return speechgenerator.SpeechGenerator.\
                       _getSpeechForMenuItem(self, obj, already_focused)

        utterances = self._getSpeechForObjectName(obj)

        # Saying "menu item" for a combo box can confuse users. Therefore,
        # speak the combo box role instead.  Also, only do it if the menu
        # item is not focused (if the menu item is focused, it means we're
        # navigating in the combo box)
        #
        if not obj.getState().contains(pyatspi.STATE_FOCUSED):
            comboBox = \
                 self._script.getAncestor(obj,
                                          [pyatspi.ROLE_COMBO_BOX],
                                          [pyatspi.ROLE_DOCUMENT_FRAME])
            if comboBox:
                utterances.extend(self.getSpeechForObjectRole(comboBox))

        self._debugGenerator("Gecko._getSpeechForMenuItem",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForListItem(self, obj, already_focused):
        """Get the speech for a list item.

        Arguments:
        - obj: the list item
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        # Treat ARIA widgets like default.py widgets
        #

        if self._script.isAriaWidget(obj) \
           or not self._script.inDocumentContent(obj):
            return speechgenerator.SpeechGenerator.\
                       _getSpeechForListItem(self, obj, already_focused)
        
        if not obj.getState().contains(pyatspi.STATE_SELECTABLE):
            return speechgenerator.SpeechGenerator.\
                       _getDefaultSpeech(self, obj, already_focused)

        utterances = self._getSpeechForObjectName(obj)

        self._debugGenerator("Gecko._getSpeechForListItem",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForList(self, obj, already_focused):
        """Get the speech for a list.

        Arguments:
        - obj: the list
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        # Treat ARIA widgets like default.py widgets
        #
        if self._script.isAriaWidget(obj):
            return speechgenerator.SpeechGenerator.\
                       _getSpeechForList(self, obj, already_focused)
        
        if not obj.getState().contains(pyatspi.STATE_FOCUSABLE):
            return speechgenerator.SpeechGenerator.\
                       _getSpeechForList(self, obj, already_focused)

        utterances = []

        label = self._script.getDisplayedLabel(obj)
        if not label:
            if not self._script.inDocumentContent():
                label = obj.name
            else:
                label = self._script.guessTheLabel(obj)

        if not already_focused and label:
            utterances.append(label)

        item = None
        selection = obj.querySelection()
        for i in xrange(obj.childCount):
            if selection.isChildSelected(i):
                item = obj[i]
                break
        item = item or obj[0]
        if item:
            name = self._getSpeechForObjectName(item)
            if name != label:
                utterances.extend(name)

        if not already_focused:
            if obj.getState().contains(pyatspi.STATE_MULTISELECTABLE):
                # Translators: "multi-select" refers to a web form list
                # in which more than one item can be selected at a time.
                #
                utterances.append(_("multi-select"))

            # Translators: this represents a list in HTML.
            #
            itemString = ngettext("List with %d item",
                                  "List with %d items",
                                  obj.childCount) % obj.childCount
            utterances.append(itemString)

        self._debugGenerator("Gecko._getSpeechForList",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForImage(self, obj, already_focused):
        """Gets a list of utterances to be spoken for an image.

        The default speech will be of the following form:

        label name role availability

        Arguments:
        - obj: an Accessible
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        # Treat ARIA widgets like default.py widgets
        #
        if self._script.isAriaWidget(obj):
            return speechgenerator.SpeechGenerator.\
                       _getSpeechForImage(self, obj, already_focused)
        
        utterances = []

        if not already_focused:
            label = self._getSpeechForObjectLabel(obj)
            utterances.extend(label)
            name = self._getSpeechForObjectName(obj)
            if name != label:
                utterances.extend(name)

            # If there's no text for the image, expose the link to
            # the user if the image is in a link.
            #
            link = self._script.getAncestor(obj,
                                            [pyatspi.ROLE_LINK],
                                            [pyatspi.ROLE_DOCUMENT_FRAME])
            if link:
                if not len(utterances):
                    return self._getSpeechForLink(link, already_focused)
                else:
                    utterances.extend(self.getSpeechForObjectRole(link))

            utterances.extend(self.getSpeechForObjectRole(obj))

        utterances.extend(self._getSpeechForObjectAvailability(obj))

        self._debugGenerator("Gecko._getSpeechForImage",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def _getSpeechForLink(self, obj, already_focused):
        """Gets a list of utterances to be spoken for a link.

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

            # Handle empty alt tags.
            #
            if name:
                lengthOfName = len(name[0].strip())
                if (lengthOfName > 0) and (name != label):
                    utterances.extend(name)

            # If there's no text for the link, expose part of the
            # URI to the user.
            #
            if not len(utterances):
                basename = self._script.getLinkBasename(obj)
                if basename:
                    utterances.append(basename)

            utterances.extend(self.getSpeechForObjectRole(obj))

            # If the link has a child which is an image, we want
            # to indicate that.
            #
            if obj.childCount and obj[0].getRole() == pyatspi.ROLE_IMAGE:
                utterances.extend(self.getSpeechForObjectRole(obj[0]))

        utterances.extend(self._getSpeechForObjectAvailability(obj))

        self._debugGenerator("Gecko._getSpeechForLink",
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

        # Treat ARIA widgets like default.py widgets
        #
        if self._script.isAriaWidget(obj):
            return speechgenerator.SpeechGenerator.\
                       _getSpeechForTable(self, obj, already_focused)
        
        # [[[TODO: JD - We should decide if we want to provide
        # information about the table dimensions, whether or not
        # this is a layout table versus a data table, etc.  For now,
        # however, if it's in HTML content let's ignore it so that
        # SayAll by sentence works. :-) ]]]
        #
        utterances = []

        if not self._script.inDocumentContent():
            return speechgenerator.SpeechGenerator.\
                       _getSpeechForTable(self, obj, already_focused)

        return utterances

    def _getSpeechForRadioButton(self, obj, already_focused):
        """Get the speech for a radio button.  If the button already had
        focus, then only the state is spoken.

        Arguments:
        - obj: the radio button
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        # Treat ARIA widgets like default.py widgets
        #
        if self._script.isAriaWidget(obj):
            return speechgenerator.SpeechGenerator.\
                       _getSpeechForRadioButton(self, obj, already_focused)
        
        if not self._script.inDocumentContent():
            return speechgenerator.SpeechGenerator.\
                       _getSpeechForRadioButton(self, obj, already_focused)

        utterances = []
        if obj.getState().contains(pyatspi.STATE_CHECKED):
            # Translators: this is in reference to a radio button being
            # selected or not.
            #
            selectionState = C_("radiobutton", "selected")
        else:
            # Translators: this is in reference to a radio button being
            # selected or not.
            #
            selectionState = C_("radiobutton", "not selected")

        if not already_focused:
            # The label is handled as a context in default.py -- assuming we
            # don't have to guess it.  If  we need to guess it, we need to
            # add it to utterances.
            #
            label = self._script.getDisplayedLabel(obj)
            if not label:
                label = self._script.guessTheLabel(obj)
                if label:
                    utterances.append(label)

            utterances.append(selectionState)
            utterances.extend(self.getSpeechForObjectRole(obj))
            utterances.extend(self._getSpeechForObjectAvailability(obj))
        else:
            utterances.append(selectionState)

        self._debugGenerator("Gecko._getSpeechForRadioButton",
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

        # Treat ARIA widgets like default.py widgets
        #
        if self._script.isAriaWidget(obj):
            return speechgenerator.SpeechGenerator.\
                       _getSpeechForCheckBox(self, obj, already_focused)
        
        if not self._script.inDocumentContent():
            return speechgenerator.SpeechGenerator.\
                       _getSpeechForCheckBox(self, obj, already_focused)

        utterances = []
        state = obj.getState()
        if state.contains(pyatspi.STATE_INDETERMINATE):
            # Translators: this represents the state of a checkbox.
            #
            checkedState = _("partially checked")
        elif state.contains(pyatspi.STATE_CHECKED):
            # Translators: this represents the state of a checkbox.
            #
            checkedState = _("checked")
        else:
            # Translators: this represents the state of a checkbox.
            #
            checkedState = _("not checked")

        # If it's not already focused, say its label.
        #
        if not already_focused:
            label = self._script.getDisplayedLabel(obj)
            if not label:
                label = self._script.guessTheLabel(obj)
            if label:
                utterances.append(label)
            utterances.extend(self.getSpeechForObjectRole(obj))
            utterances.append(checkedState)
            utterances.extend(self._getSpeechForObjectAvailability(obj))
        else:
            utterances.append(checkedState)

        self._debugGenerator("Gecko._getSpeechForCheckBox",
                             obj,
                             already_focused,
                             utterances)

        return utterances

    def getSpeechContext(self, obj, stopAncestor=None):
        """Get the speech that describes the names and role of
        the container hierarchy of the object, stopping at and
        not including the stopAncestor.

        Arguments:
        - obj: the object
        - stopAncestor: the ancestor to stop at and not include (None
          means include all ancestors)

        Returns a list of utterances to be spoken.
        """

        utterances = []

        if obj is stopAncestor:
            return utterances

        # Skip items of unknown rolenames, menu bars, labels with 
        # children, and autocompletes.  (With autocompletes, we
        # wind up speaking the text object). Beginning with Firefox
        # 3.2, list items have names corresponding with their text.
        # This results in getDisplayedText returning actual text
        # and the parent list item being spoken when it should not
        # be. So we'll take list items out of the context.
        #
        skipRoles = [pyatspi.ROLE_UNKNOWN,
                     pyatspi.ROLE_MENU_BAR,
                     pyatspi.ROLE_LABEL,
                     pyatspi.ROLE_AUTOCOMPLETE,
                     pyatspi.ROLE_LIST_ITEM]

        # Stop if we get to a document frame or an internal frame.
        #
        stopRoles = [pyatspi.ROLE_DOCUMENT_FRAME,
                     pyatspi.ROLE_INTERNAL_FRAME]

        # There are some objects we want to include in the context,
        # but not add their rolenames.
        #
        dontSpeakRoles = [pyatspi.ROLE_TABLE_CELL,
                          pyatspi.ROLE_FILLER]

        parent = obj.parent
        while parent and (parent.parent != parent):
            role = parent.getRole()
            if self._script.isSameObject(parent, stopAncestor) \
               or role in stopRoles:
                break

            if role in skipRoles or self._script.isLayoutOnly(parent):
                parent = parent.parent
                continue

            # If the parent is a menu and its parent is a combo box
            # we'll speak the object as a combo box.
            #
            if role == pyatspi.ROLE_MENU \
               and parent.parent.getRole() == pyatspi.ROLE_COMBO_BOX:
                parent = parent.parent
                continue
                
            # Also skip the parent if its accessible text is a single 
            # EMBEDDED_OBJECT_CHARACTER: Script.getDisplayedText will
            # end up coming back to the child of an object for the text
            # if an object's text contains a single EOC. In addition,
            # beginning with Firefox 3.2, a table cell may derive its
            # accessible name from focusable objects it contains (e.g.
            # links, form fields). getDisplayedText will return the
            # object's name in this case (because of the presence of
            # the EOC and other characters). This causes us to be
            # chatty. So if it's a table cell which contains an EOC,
            # we will also skip the parent.
            #
            parentText = self._script.queryNonEmptyText(parent)
            if parentText:
                unicodeText = parentText.getText(0, -1).decode("UTF-8")
                if self._script.EMBEDDED_OBJECT_CHARACTER in unicodeText \
                   and (len(unicodeText) == 1 \
                        or role == pyatspi.ROLE_TABLE_CELL):
                    parent = parent.parent
                    continue

            # Put in the text and label (if they exist).
            #
            text = self._script.getDisplayedText(parent)
            label = self._script.getDisplayedLabel(parent)
            newUtterances = []
            if text and (text != label) and len(text.strip()) \
                and (not text.startswith("chrome://")):
                newUtterances.append(text)
            if label and len(label.strip()):
                newUtterances.append(label)

            # Finally add the role if it's not among the roles we don't
            # wish to speak.
            #
            if not role in dontSpeakRoles and len(newUtterances):
                utterances.append(rolenames.getSpeechForRoleName(parent))

            # If this object is an ARIA widget with STATE_REQUIRED, add
            # that. (Note that for the most part, the ARIA widget itself
            # has this state, but in the case of a group of radio buttons,
            # it is the group which has the state).
            #
            utterances.extend(self._getSpeechForRequiredObject(parent))

            utterances.extend(newUtterances)

            parent = parent.parent

        utterances.reverse()

        return utterances
            
    def _getSpeechForSlider(self, obj, already_focused):
        """Get the speech for a slider.  If the object already
        had focus, just the value is spoken.

        Arguments:
        - obj: the slider
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """
        
        # Let default handle non-ARIA widgets (XUL?)
        if self._script.isAriaWidget(obj):
            return speechgenerator.SpeechGenerator.\
                       _getSpeechForSlider(self, obj, already_focused)

        valueString = self._script.getTextForValue(obj)

        if already_focused:
            utterances = [valueString]
        else:
            utterances = []
            utterances.extend(self._getSpeechForObjectLabel(obj))
            utterances.extend(self.getSpeechForObjectRole(obj))
            utterances.append(valueString)
            utterances.extend(self._getSpeechForObjectAvailability(obj))

        self._debugGenerator("Gecko._getSpeechForSlider",
                             obj,
                             already_focused,
                             utterances)

        return utterances
                        
