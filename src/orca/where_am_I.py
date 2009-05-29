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

"""Speaks information about the current object of interest."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi
import debug
import orca_state
import settings
import speech
import text_attribute_names
import urlparse, urllib2

from orca_i18n import _ # for gettext support
from orca_i18n import ngettext  # for ngettext support
from orca_i18n import C_ # to provide qualified translatable strings

class WhereAmI:

    def __init__(self, script):
        """Create a new WhereAmI that will be used to speak information
        about the current object of interest.
        """

        self._script = script
        self._debugLevel = debug.LEVEL_FINEST
        self._statusBar = None
        self._defaultButton = None
        self._lastAttributeString = ""

    def whereAmI(self, obj, basicOnly):
        """Speaks information about the current object of interest, including
        the object itself, which window it is in, which application, which
        workspace, etc.

        The object of interest can vary depending upon the mode the user
        is using at the time. For example, in focus tracking mode, the
        object of interest is the object with keyboard focus. In review
        mode, the object of interest is the object currently being visited,
        whether it has keyboard focus or not.
        """

        if (not obj):
            return False

        debug.println(self._debugLevel,
            "whereAmI: \
           \n  label=%s \
           \n  name=%s \
           \n  role=%s \
           \n  keybinding=%s \
           \n  parent label= %s \
           \n  parent name=%s \
           \n  parent role=%s \
           \n  basicOnly=%s" % \
            (self._getObjLabel(obj),
             self._getObjName(obj),
             obj.getRoleName(),
             self._script.getKeyBinding(obj),
             self._getObjLabel(obj.parent),
             self._getObjName(obj.parent),
             obj.parent.getRoleName(),
             basicOnly))

        role = obj.getRole()

        toolbar = self._getToolbar(obj)
        if toolbar:
            self._speakToolbar(toolbar)

        if role == pyatspi.ROLE_CHECK_BOX:
            self._speakCheckBox(obj, basicOnly)

        elif role == pyatspi.ROLE_RADIO_BUTTON:
            self._speakRadioButton(obj, basicOnly)

        elif role == pyatspi.ROLE_COMBO_BOX:
            self._speakComboBox(obj, basicOnly)

        elif role == pyatspi.ROLE_SPIN_BUTTON:
            self._speakSpinButton(obj, basicOnly)

        elif role == pyatspi.ROLE_PUSH_BUTTON:
            self._speakPushButton(obj, basicOnly)

        elif role == pyatspi.ROLE_SLIDER:
            self._speakSlider(obj, basicOnly)

        elif role in [pyatspi.ROLE_MENU,
                      pyatspi.ROLE_MENU_ITEM,
                      pyatspi.ROLE_CHECK_MENU_ITEM,
                      pyatspi.ROLE_RADIO_MENU_ITEM]:
            self._speakMenuItem(obj, basicOnly)

        elif role == pyatspi.ROLE_PAGE_TAB:
            self._speakPageTab(obj, basicOnly)

        elif role in [pyatspi.ROLE_ENTRY,
                      pyatspi.ROLE_TEXT,
                      pyatspi.ROLE_TERMINAL]:
            self._speakText(obj, basicOnly)

        elif role == pyatspi.ROLE_TABLE_CELL:
            self._speakTableCell(obj, basicOnly)

        elif role == pyatspi.ROLE_LIST_ITEM:
            self._speakListItem(obj, basicOnly)

        elif role in [pyatspi.ROLE_PARAGRAPH,
                      pyatspi.ROLE_SECTION,
                      pyatspi.ROLE_HEADING,
                      pyatspi.ROLE_DOCUMENT_FRAME]:
            self._speakParagraph(obj, basicOnly)

        elif role == pyatspi.ROLE_ICON:
            self._speakIconPanel(obj, basicOnly)

        elif role == pyatspi.ROLE_LINK:
            self._speakLink(obj, basicOnly)

        elif role == pyatspi.ROLE_TOGGLE_BUTTON:
            self._speakToggleButton(obj, basicOnly)

        elif role == pyatspi.ROLE_SPLIT_PANE:
            self._speakSplitPane(obj, basicOnly)

        elif role == pyatspi.ROLE_LABEL:
            self._speakLabel(obj, basicOnly)

        elif role  == pyatspi.ROLE_LAYERED_PANE:
            self._speakLayeredPane(obj, basicOnly)

        else:
            self._speakGenericObject(obj, basicOnly)

        if basicOnly:
            self._speakObjDescription(obj)

        self._lastAttributeString = ""

        return True

    def _speakCheckBox(self, obj, basicOnly):
        """Checkboxes present the following information
        (an example is 'Enable speech, checkbox checked, Alt E'):
        1. label
        2. role
        3. state
        4. accelerator (i.e. Alt plus the underlined letter), if any
        5. tutorial string if enableTutorialMessages is set.
        """

        utterances = []
        text = self.getObjLabelAndName(obj) + " " + \
               self._getSpeechForRoleName(obj)
        text = text + " " + self._getCheckBoxState(obj)
        utterances.append(text)

        accelerator = self._getObjAccelerator(obj)
        utterances.append(accelerator)

        text = self._getRequiredState(obj)
        if text:
            utterances.append(text)

        getTutorial = self._script.tutorialGenerator.getTutorial
        utterances.extend(getTutorial(obj, False, forceMessage=True))

        debug.println(self._debugLevel, "check box utterances=%s" \
                      % utterances)
        speech.speak(utterances)

    def _speakRadioButton(self, obj, basicOnly):
        """Radio Buttons present the following information (an example is
        'Punctuation Level, Some, Radio button, selected, item 2 of 4, Alt M'):

        1. group name
        2. label
        3. role
        4. state
        5. relative position
        6. accelerator (i.e. Alt plus the underlined letter), if any
        7. tutorial string if enableTutorialMessages is set.
        """

        utterances = []
        text = self._getGroupLabel(obj)
        utterances.append(text)

        text = self._getRequiredState(obj)
        if text:
            utterances.append(text)

        text = self.getObjLabelAndName(obj) + " " + \
               self._getSpeechForRoleName(obj)
        utterances.append(text)

        state = obj.getState()
        if state.contains(pyatspi.STATE_CHECKED):
            # Translators: this is in reference to a radio button being
            # selected or not.
            #
            text = C_("radiobutton", "selected")
        else:
            # Translators: this is in reference to a radio button being
            # selected or not.
            #
            text = C_("radiobutton", "not selected")

        utterances.append(text)

        text = self._getPositionInGroup(obj)
        utterances.append(text)

        text = self._getObjAccelerator(obj)
        utterances.append(text)

        getTutorial = self._script.tutorialGenerator.getTutorial
        utterances.extend(getTutorial(obj, False, forceMessage=True))

        debug.println(self._debugLevel, "radio button utterances=%s" % \
                      utterances)
        speech.speak(utterances)

    def _speakComboBox(self, obj, basicOnly):
        """Comboboxes present the following information (an example is
        'Speech system: combo box, GNOME Speech Services, item 1 of 1,
        Alt S'):
        1. label
        2. role
        3. current value
        4. relative position
        5. accelerator (i.e. Alt plus the underlined letter), if any
        6. tutorial string if enableTutorialMessages is set.
        """

        utterances = []
        text = self._getObjLabel(obj)
        utterances.append(text)

        text = self._getSpeechForRoleName(obj)
        utterances.append(text)

        name = self._getObjName(obj)
        utterances.append(name)

        # child(0) is the popup list
        text = self._getPositionInList(obj[0], name)
        utterances.append(text)

        accelerator = self._getObjAccelerator(obj)
        utterances.append(accelerator)

        getTutorial = self._script.tutorialGenerator.getTutorial
        utterances.extend(getTutorial(obj, False, forceMessage=True))

        debug.println(self._debugLevel, "combo box utterances=%s" % \
                      utterances)
        speech.speak(utterances)

    def _speakSpinButton(self, obj, basicOnly):
        """Spin Buttons present the following information (an example is
        'Scale factor: spin button, 4.00, Alt F'):

        1. label
        2. role
        3. current value
        4. selected (if True).
        5. accelerator (i.e. Alt plus the underlined letter), if any
        6. tutorial string if enableTutorialMessages is set.
        """

        utterances = []
        label = self._getObjLabel(obj)
        utterances.append(label)

        text = self._getSpeechForRoleName(obj)
        utterances.append(text)

        name = self._getObjName(obj)
        if name != label:
            utterances.append(name)

        utterances.extend(self._getSpeechForAllTextSelection(obj))

        text = self._getObjAccelerator(obj)
        utterances.append(text)

        text = self._getRequiredState(obj)
        if text:
            utterances.append(text)

        getTutorial = self._script.tutorialGenerator.getTutorial
        utterances.extend(getTutorial(obj, False, forceMessage=True))

        debug.println(self._debugLevel, "spin button utterances=%s" % \
                      utterances)
        speech.speak(utterances)

    def _speakPushButton(self, obj, basicOnly):
        """ Push Buttons present the following information (an example is
        'Apply button, Alt A'):

        1. label
        2. role
        3. accelerator (i.e. Alt plus the underlined letter), if any
        4. tutorial string if enableTutorialMessages is set.
        """

        utterances = []
        text = self.getObjLabelAndName(obj)
        utterances.append(text)

        text = self._getSpeechForRoleName(obj)
        utterances.append(text)

        text = self._getObjAccelerator(obj)
        utterances.append(text)

        getTutorial = self._script.tutorialGenerator.getTutorial
        utterances.extend(getTutorial(obj, False, forceMessage=True))

        debug.println(self._debugLevel, "push button utterances=%s" % \
                      utterances)
        speech.speak(utterances)

    def _speakSlider(self, obj, basicOnly):
        """Sliders present the following information (examples include
        'Pitch slider, 5.0, 56%'; 'Volume slider, 9.0, 100%'):

        1. label
        2. role
        3. value
        4. percentage (if possible)
        5. accelerator (i.e. Alt plus the underlined letter), if any
        6. tutorial string if enableTutorialMessages is set.
        """

        utterances = []
        text = self._getObjLabel(obj)
        utterances.append(text)

        text = self._getSpeechForRoleName(obj)
        utterances.append(text)

        values = self._getSliderValues(obj)
        utterances.append(values[0])
        # Translators: this is the percentage value of a slider.
        #
        utterances.append(_("%s percent") % values[1])

        text = self._getObjAccelerator(obj)
        utterances.append(text)

        text = self._getRequiredState(obj)
        if text:
            utterances.append(text)

        getTutorial = self._script.tutorialGenerator.getTutorial
        utterances.extend(getTutorial(obj, False, forceMessage=True))

        debug.println(self._debugLevel, "slider utterances=%s" % \
                      utterances)
        speech.speak(utterances)

    def _speakMenuItem(self, obj, basicOnly):
        """Menu items present the following information (examples include
        'File menu, Open..., Control + O, item 2 of 20, O', 'File menu,
        Wizards Menu, item 4 of 20, W'):

        1. Name of the menu containing the item, followed by its role
        2. item name, followed by its role (if a menu) followed by its
        accelerator key binding, if any
        3. relative position
        4. mnemonic (i.e. the underlined letter), if any
        5. tutorial string if enableTutorialMessages is set.
        """

        utterances = []
        text = self.getObjLabelAndName(obj.parent) + " " \
               + self._getSpeechForRoleName(obj.parent, force=True)
        utterances.append(text.strip())

        text = self.getObjLabelAndName(obj)
        utterances.append(text)

        state = obj.getState()

        if obj.getRole() != pyatspi.ROLE_MENU_ITEM:
            text = self._getSpeechForRoleName(obj)
            utterances.append(text)

        if obj.getRole() == pyatspi.ROLE_CHECK_MENU_ITEM:
            if state.contains(pyatspi.STATE_INDETERMINATE):
                # Translators: this represents the state of a checkbox.
                #
                text = _("partially checked")
            elif state.contains(pyatspi.STATE_CHECKED):
                # Translators: this represents the state of a checkbox.
                #
                text = _("checked")
            else:
                # Translators: this represents the state of a checkbox.
                #
                text = _("not checked")
            utterances.append(text)

        elif obj.getRole() == pyatspi.ROLE_RADIO_MENU_ITEM:
            if state.contains(pyatspi.STATE_CHECKED):
                # Translators: this is in reference to a radio button being
                # selected or not.
                #
                text = _("selected")
            else:
                # Translators: this is in reference to a radio button being
                # selected or not.
                #
                text = _("not selected")
            utterances.append(text)

        text = self._getObjAccelerator(obj, False, False)
        utterances.append(text)

        name = self._getObjName(obj)
        text = self._getPositionInList(obj.parent, name)
        utterances.append(text)

        if obj.parent \
           and obj.parent.getRole() in [pyatspi.ROLE_MENU,
                                        pyatspi.ROLE_MENU_BAR]:
            text = self._getObjMnemonic(obj)
            utterances.append(text)

        getTutorial = self._script.tutorialGenerator.getTutorial
        utterances.extend(getTutorial(obj, False, forceMessage=True))

        debug.println(self._debugLevel, "menu item utterances=%s" % \
                      utterances)
        speech.speak(utterances)

    def _speakPageTab(self, obj, basicOnly):
        """Tabs in a Tab List present the following information (an example
        is 'Tab list, braille page, item 2 of 5'):

        1. role
        2. label + 'page'
        3. relative position
        4. accelerator (i.e. Alt plus the underlined letter), if any
        5. tutorial string if enableTutorialMessages is set.
        """

        utterances = []
        text = self._getSpeechForRoleName(obj.parent)
        utterances.append(text)

        # Translators: "page" is the word for a page tab in a tab list.
        #
        text = _("%s page") % self.getObjLabelAndName(obj)
        utterances.append(text)

        name = self._getObjName(obj)
        text = self._getPositionInList(obj.parent, name)
        utterances.append(text)

        text = self._getObjAccelerator(obj)
        utterances.append(text)

        getTutorial = self._script.tutorialGenerator.getTutorial
        utterances.extend(getTutorial(obj, False, forceMessage=True))

        debug.println(self._debugLevel, "page utterances=%s" % \
                      utterances)
        speech.speak(utterances)

    def _speakText(self, obj, basicOnly):
        """Text boxes present the following information (an example is
        'Source display: text, blank, Alt O'):

        1. label, if any
        2. role
        3. contents
            A. if no text on the current line is selected, the current line
            B. if text is selected on the current line, that text, followed
            attibute information before  (bold "text")
            by 'selected' (single press)
            C. if the current line is blank/empty, 'blank'
        4. accelerator (i.e. Alt plus the underlined letter), if any
        5. tutorial string if enableTutorialMessages is set.

        Gaim, gedit, OpenOffice Writer and Terminal
        """

        ancestor = self._script.getAncestor(obj,
                                            [pyatspi.ROLE_TABLE_CELL,
                                             pyatspi.ROLE_LIST_ITEM],
                                            [pyatspi.ROLE_FRAME])
        if ancestor and not self._script.isLayoutOnly(ancestor.parent):
            # [[[TODO: WDW - we handle ROLE_ENTRY specially here because
            # there is a bug in getRealActiveDescendant: it doesn't dive
            # deep enough into the hierarchy (see comment #12 of bug
            # #542714).  So, we'll do this nasty hack until we can feel
            # more comfortable with mucking around with
            # getRealActiveDescendant.]]]
            #
            if ancestor.getRole() == pyatspi.ROLE_TABLE_CELL:
                if obj.getRole() != pyatspi.ROLE_ENTRY:
                    return self._speakTableCell(ancestor, basicOnly)
            else:
                return self._speakListItem(ancestor, basicOnly)

        utterances = []
        text = self._getObjLabel(obj)
        utterances.append(text)

        if settings.presentReadOnlyText \
           and self._script.isReadOnlyTextArea(obj):
            utterances.append(settings.speechReadOnlyString)

        text = self._getSpeechForRoleName(obj)
        utterances.append(text)

        [textContents, startOffset, endOffset, selected] = \
                       self._getTextContents(obj, basicOnly)
        if not basicOnly:
            # Speak character attributes.
            textContents = \
                self._insertAttributes(obj, startOffset,
                                       endOffset, textContents)
            savedStyle = settings.verbalizePunctuationStyle
            settings.verbalizePunctuationStyle = settings.PUNCTUATION_STYLE_SOME

        text = textContents
        utterances.append(text)
        debug.println(self._debugLevel, "first text utterances=%s" % \
                      utterances)

        speech.speak(utterances)

        if not basicOnly:
            settings.verbalizePunctuationStyle = savedStyle

        utterances = []
        if selected:
            # Translators: when the user selects (highlights) text in
            # a document, Orca lets them know this.
            #
            text = C_("text", "selected")
            utterances.append(text)

        text = self._getObjAccelerator(obj)
        utterances.append(text)

        getTutorial = self._script.tutorialGenerator.getTutorial
        utterances.extend(getTutorial(obj, False, forceMessage=True))

        debug.println(self._debugLevel, "text utterances=%s" % \
                      utterances)
        speech.speak(utterances)

    def _speakTableCell(self, obj, basicOnly):
        """Tree Tables present the following information (an example is
        'Tree table, Mike Pedersen, item 8 of 10, tree level 2'):

        1. parent's role
        2. column header of object
        3. row header of object
        4. object's role
        5. object's contents, if there are multiple columns
        6. relative position
        7. current row (regardless of speak cell/row setting), if
           performing a detailed whereAmI.
        8. if expandable/collapsible: expanded/collapsed
        9. if applicable, the level
        10. tutorial string if enableTutorialMessages is set.

        Nautilus and Gaim
        """

        utterances = []
        if obj.parent.getRole() == pyatspi.ROLE_TABLE_CELL:
            obj = obj.parent
        parent = obj.parent

        text = self._getSpeechForRoleName(parent)
        utterances.append(text)

        try:
            table = parent.queryTable()
        except:
            table = None
            nColumns = 0
        else:
            nColumns = table.nColumns
            index = self._script.getCellIndex(obj)
            column = table.getColumnAtIndex(index)
            header = table.getColumnHeader(column)
            if header:
                text = self._getObjName(header)
                utterances.append(text)

            row = table.getRowAtIndex(index)
            header = table.getRowHeader(row)
            if header:
                text = self._getObjName(header)
                utterances.append(text)

        text = self._getSpeechForRoleName(obj)
        utterances.append(text)

        if nColumns:
            text = self._getTableCell(obj)
            utterances.append(text)

        text = self._getRequiredState(obj)
        if text:
            utterances.append(text)

        debug.println(self._debugLevel, "first table cell utterances=%s" % \
                      utterances)
        speech.speak(utterances)

        utterances = []
        if table:
            # Translators: this is in references to a column in a
            # table.
            text = _("column %d of %d") % ((column + 1), table.nColumns)
            utterances.append(text)

            # Translators: this is in reference to a row in a table.
            #
            text = _("row %d of %d") % ((row + 1), table.nRows)
            utterances.append(text)
            speech.speak(utterances)

            # Speak the current row if performing a "detailed" whereAmI.
            #
            if not basicOnly:
                utterances = self._getTableRow(obj)
                debug.println(self._debugLevel, \
                              "second table cell utterances=%s" % \
                              utterances)
                speech.speak(utterances)

        utterances = []
        state = obj.getState()
        if state.contains(pyatspi.STATE_EXPANDABLE):
            if state.contains(pyatspi.STATE_EXPANDED):
                # Translators: this represents the state of a node in a tree.
                # 'expanded' means the children are showing.
                # 'collapsed' means the children are not showing.
                #
                text = _("expanded")
            else:
                # Translators: this represents the state of a node in a tree.
                # 'expanded' means the children are showing.
                # 'collapsed' means the children are not showing.
                #
                text = _("collapsed")
            utterances.append(text)

        level = self._script.getNodeLevel(orca_state.locusOfFocus)
        if level >= 0:
            # Translators: this represents the depth of a node in a tree
            # view (i.e., how many ancestors a node has).
            #
            utterances.append(_("tree level %d") % (level + 1))

        getTutorial = self._script.tutorialGenerator.getTutorial
        utterances.extend(getTutorial(obj, False, forceMessage=True))

        debug.println(self._debugLevel, "third table cell utterances=%s" % \
                      utterances)
        speech.speak(utterances)

    def _speakListItem(self, obj, basicOnly):
        """List items should be treated like tree cells:

        1. label, if any
        2. role
        3. name
        4. relative position
        5. if expandable/collapsible: expanded/collapsed
        6. if applicable, the level
        7. tutorial string if enableTutorialMessages is set.
        """

        utterances = []

        text = self._getObjLabel(obj)
        if text:
            utterances.append(text)

        text = self._getSpeechForRoleName(obj, force=True)
        utterances.append(text)

        text = self._getObjName(obj)
        utterances.append(text)

        parent = obj.parent
        relationset = obj.getRelationSet()
        for relation in relationset:
            if relation.getRelationType() == pyatspi.RELATION_NODE_CHILD_OF:
                parent = relation.getTarget(0)
                break

        name = self._getObjName(obj)
        text = self._getPositionInList(parent, name)
        utterances.append(text)

        state = obj.getState()
        if state.contains(pyatspi.STATE_EXPANDABLE):
            if state.contains(pyatspi.STATE_EXPANDED):
                # Translators: this represents the state of a node in a tree.
                # 'expanded' means the children are showing.
                # 'collapsed' means the children are not showing.
                #
                text = _("expanded")
            else:
                # Translators: this represents the state of a node in a tree.
                # 'expanded' means the children are showing.
                # 'collapsed' means the children are not showing.
                #
                text = _("collapsed")
            utterances.append(text)

        level = self._script.getNodeLevel(orca_state.locusOfFocus)
        if level >= 0:
            # Translators: this represents the depth of a node in a tree
            # view (i.e., how many ancestors a node has).
            #
            utterances.append(_("tree level %d") % (level + 1))
        else:
            nestingLevel = 0
            parent = obj.parent
            while parent.parent.getRole() == pyatspi.ROLE_LIST:
                nestingLevel += 1
                parent = parent.parent
            if nestingLevel:
                # Translators: this represents a list item in a document.
                # The nesting level is how 'deep' the item is (e.g., a
                # level of 2 represents a list item inside a list that's
                # inside another list).
                #
                utterances.append(_("Nesting level %d") % nestingLevel)

        getTutorial = self._script.tutorialGenerator.getTutorial
        utterances.extend(getTutorial(obj, False, forceMessage=True))

        debug.println(self._debugLevel, "list item utterances=%s" % \
                      utterances)
        speech.speak(utterances)

    def _speakParagraph(self, obj, basicOnly):
        """Speak a paragraph object.
        """

        self._speakText(obj, basicOnly)

    def _speakIconPanel(self, obj, basicOnly):
        """Speak the contents of the pane containing this icon. The
        1. Number of icons in the pane is spoken.
        2. The total number of selected icons.
        3. The name of each of the selected icons.
        4. tutorial string if enableTutorialMessages is set.

        Arguments:
        - obj: the icon object that currently has focus.
        """

        utterances = []
        panel = obj.parent
        childCount = panel.childCount

        utterances.append(_("Icon panel"))
        utterances.append(self.getObjLabelAndName(obj))
        utterances.extend(self._getSelectedItemCount(panel, basicOnly))

        # get our tutorial.
        getTutorial = self._script.tutorialGenerator.getTutorial
        utterances.extend(getTutorial(obj, False, forceMessage=True))
        # get the frames tutorial.
        [frame, dialogue] = self._getFrameAndDialog(obj)
        utterances.extend(getTutorial(frame, False, forceMessage=True))

        speech.speak(utterances)

    def _speakLink(self, obj, basicOnly):
        """Speaks information about a link including protocol, domain
        comparisons and size of file if possible.
        Also tutorial string if enableTutorialMessages is set.

        Arguments:
        - obj: the icon object that currently has focus.
        - basicOnly: True if the user is performing a standard/basic whereAmI.
        """

        # get the URI for the link of interest and parse it.
        # parsed URI is returned as a tuple containing six components:
        # scheme://netloc/path;parameters?query#fragment.
        link_uri = self._script.getURI(obj)
        if link_uri:
            link_uri_info = urlparse.urlparse(link_uri)
        else:
            # It might be an anchor.  Try to speak the text.
            #
            return self._speakText(obj, basicOnly)

        # Try to get the URI of the active document and parse it
        doc_uri = self._script.getDocumentFrameURI()
        if doc_uri:
            doc_uri_info = urlparse.urlparse(doc_uri)
        else:
            doc_uri_info = None

        # initialize our three outputs.  Output may change below for some
        # protocols.
        # Translators: this is the protocol of a link eg. http, mailto.
        #
        linkoutput = _('%s link') %link_uri_info[0]
        text = self._script.getDisplayedText(obj)
        if text:
            linkoutput += " " + text
        else:
            # If there's no text for the link, expose part of the
            # URI to the user.
            #
            basename = self._script.getLinkBasename(obj)
            if basename:
                linkoutput += " " + basename

        # If the link has a child which is an image, we want
        # to indicate that.
        #
        if obj.childCount and obj[0].getRole() == pyatspi.ROLE_IMAGE:
            linkoutput += " " + self._getSpeechForRoleName(obj[0])

        domainoutput = ''
        sizeoutput = ''

        # get size and other protocol specific information
        if link_uri_info[0] == 'ftp' or \
           link_uri_info[0] == 'ftps' or \
           link_uri_info[0] == 'file':
            # change link output message to include filename
            filename = link_uri_info[2].split('/')
            linkoutput = _('%s link to %s') %(link_uri_info[0], filename[-1])
            sizestr = self.__extractSize(link_uri)
            sizeoutput = self.__formatSizeOutput(sizestr)

        # determine location differences if doc uri info is available
        if doc_uri_info:
            if link_uri_info[1] == doc_uri_info[1]:
                if link_uri_info[2] == doc_uri_info[2]:
                    # Translators: this is the domain relationship of a given
                    # link to the current page.  eg. same page, same site.
                    domainoutput = _('same page')
                else:
                    domainoutput = _('same site')
            else:
                # check for different machine name on same site
                linkdomain = link_uri_info[1].split('.')
                docdomain = doc_uri_info[1].split('.')
                if len(linkdomain) > 1 and docdomain > 1  \
                    and linkdomain[-1] == docdomain[-1]  \
                    and linkdomain[-2] == docdomain[-2]:
                    domainoutput = _('same site')
                else:
                    domainoutput = _('different site')

        utterances = [linkoutput, domainoutput, sizeoutput]
        getTutorial = self._script.tutorialGenerator.getTutorial
        utterances.extend(getTutorial(obj, False, forceMessage=True))

        speech.speak(utterances)

    def _speakToggleButton(self, obj, basicOnly):
        """Speak toggle button information:
           1. Name/Label
           2. Role
           3. State (pressed/not pressed)
           4. tutorial string if enableTutorialMessages is set.
        """

        utterances = []
        text = self.getObjLabelAndName(obj)
        utterances.append(text)

        text = self._getSpeechForRoleName(obj)
        utterances.append(text)

        if obj.getState().contains(pyatspi.STATE_CHECKED):
            # Translators: the state of a toggle button.
            #
            checkedState = _("pressed")
        else:
            # Translators: the state of a toggle button.
            #
            checkedState = _("not pressed")
        utterances.append(checkedState)

        getTutorial = self._script.tutorialGenerator.getTutorial
        utterances.extend(getTutorial(obj, False, forceMessage=True))

        speech.speak(utterances)

    def _speakSplitPane(self, obj, basicOnly):
        """Speak split pane information:
           1. Name/Label
           2. Role
           3. Value
           4. tutorial string if enableTutorialMessages is set.
        """

        utterances = []
        text = self.getObjLabelAndName(obj)
        utterances.append(text)

        text = self._getSpeechForRoleName(obj)
        utterances.append(text)

        valueString = self._script.getTextForValue(obj)
        utterances.append(valueString)

        getTutorial = self._script.tutorialGenerator.getTutorial
        utterances.extend(getTutorial(obj, False, forceMessage=True))

        speech.speak(utterances)

    def _speakLabel(self, obj, basicOnly):
        """Speak label information:
           1. Name/Label
           2. selected (if True).
           3. Role
           4. tutorial string if enableTutorialMessages is set.
        """

        utterances = []
        text = self.getObjLabelAndName(obj)
        utterances.append(text)

        utterances.extend(self._getSpeechForAllTextSelection(obj))

        text = self._getSpeechForRoleName(obj)
        utterances.append(text)

        getTutorial = self._script.tutorialGenerator.getTutorial
        utterances.extend(getTutorial(obj, False, forceMessage=True))

        speech.speak(utterances)


    def _speakLayeredPane(self, obj, basicOnly):
        """Speak layered pane information:
           1. Name/Label
           2. Role
           3. Number of selected items and total number of items.
           4. tutorial string if enableTutorialMessages is set.
        """

        utterances = []
        text = self.getObjLabelAndName(obj)
        utterances.append(text)

        text = self._getSpeechForRoleName(obj)
        utterances.append(text)
        utterances.extend(self._getSelectedItemCount(obj, basicOnly))

        getTutorial = self._script.tutorialGenerator.getTutorial
        utterances.extend(getTutorial(obj, False, forceMessage=True))

        speech.speak(utterances)


    def _getSpeechForAllTextSelection(self, obj):
        """Check if this object has text associated with it and it's
        completely selected.

        Arguments:
        - obj: the object being presented
        """

        utterance = []
        try:
            textObj = obj.queryText()
        except:
            pass
        else:
            noOfSelections = textObj.getNSelections()
            if noOfSelections == 1:
                [string, startOffset, endOffset] = \
                   textObj.getTextAtOffset(0, pyatspi.TEXT_BOUNDARY_LINE_START)
                if startOffset == 0 and endOffset == len(string):
                    # Translators: when the user selects (highlights) text in
                    # a document, Orca lets them know this.
                    #
                    utterance = [C_("text", "selected")]

        return utterance

    def _getSelectedItemCount(self, obj, basicOnly):
        """Return an utterance indicating how many items are selected in this
        object, the current item, and (if a detailed whereAmI), the names of
        all the selected items. This object will be an icon panel or a
        layered pane.

        Arguments:
        - obj: the object being presented
        """

        childCount = obj.childCount
        selectedItems = []
        totalSelectedItems = 0
        currentItem = 0
        for child in obj:
            state = child.getState()
            if state.contains(pyatspi.STATE_SELECTED):
                totalSelectedItems += 1
                selectedItems.append(child)
            if state.contains(pyatspi.STATE_FOCUSED):
                currentItem = child.getIndexInParent() + 1

        utterances = []
        # Translators: this is a count of the number of selected icons
        # and the count of the total number of icons within an icon panel.
        # An example of an icon panel is the Nautilus folder view.
        #
        countString = ngettext("%d of %d item selected",
                              "%d of %d items selected",
                              childCount) % \
                              (totalSelectedItems, childCount)
        utterances.append(countString)

        # Translators: this is a indication of the focused icon and the
        # count of the total number of icons within an icon panel. An
        # example of an icon panel is the Nautilus folder view.
        #
        itemString = _("on item %d of %d") % (currentItem, childCount)
        utterances.append(itemString)

        if not basicOnly:
            for i in range(0, len(selectedItems)):
                utterances.append(self.getObjLabelAndName(selectedItems[i]))

        return utterances

    def __extractSize(self, uri):
        """Get the http header for a given uri and try to extract the size
        (Content-length).
        """
        try:
            x = urllib2.urlopen(uri)
            try:
                return x.info()['Content-length']
            except KeyError:
                return None
        except (ValueError, urllib2.URLError, OSError):
            return None

    def __formatSizeOutput(self, sizestr):
        """Format the size output announcement.  Changes wording based on
        size.
        """
        # sanity check
        if sizestr is None or sizestr == '':
            return ''
        size = int(sizestr)
        if size < 10000:
            # Translators: This is the size of a file in bytes
            #
            return ngettext('%d byte', '%d bytes', size) % size
        elif size < 1000000:
            # Translators: This is the size of a file in kilobytes
            #
            return _('%.2f kilobytes') % (float(size) * .001)
        elif size >= 1000000:
            # Translators: This is the size of a file in megabytes
            #
            return _('%.2f megabytes') % (float(size) * .000001)

    def _speakGenericObject(self, obj, basicOnly):
        """Speak a generic object; one not specifically handled by
        other methods.
        """

        utterances = []
        text = self.getObjLabelAndName(obj)
        utterances.append(text)

        text = self._getSpeechForRoleName(obj)
        utterances.append(text)

        getTutorial = self._script.tutorialGenerator.getTutorial
        utterances.extend(getTutorial(obj, False, forceMessage=True))

        speech.speak(utterances)


    def _getObjName(self, obj):
        """Returns the name to speak for an object.
        """

        text = ""
        name = self._script.getDisplayedText(obj)
        if not name:
            name = obj.description

        if name and name != "None":
            text = name.strip()
        debug.println(self._debugLevel, "%s name=<%s>" % (obj.getRole(), text))

        return text

    def _getObjLabel(self, obj):
        """Returns the label to speak for an object.
        """

        text = ""
        label = self._script.getDisplayedLabel(obj)

        if label and label != "None":
            text = label.strip()

        debug.println(self._debugLevel, "%s label=<%s>" % (obj.getRole(), text))

        return text

    def getObjLabelAndName(self, obj):
        """Returns the object label plus the object name.
        """

        name = self._getObjName(obj)
        label = self._getObjLabel(obj)

        if name != label:
            text = label + " " + name
        else:
            text = label

        try:
            textObj = obj.queryText()
        except NotImplementedError:
            pass
        else:
            [string, startOffset, endOffset] = textObj.getTextAtOffset(0,
                pyatspi.TEXT_BOUNDARY_LINE_START)

            debug.println(self._debugLevel, "%s text=<%s>" % \
                            (obj.getRoleName(), string))

        return text.strip()

    # pylint: disable-msg=W0142

    def _getSpeechForRoleName(self, obj, **args):
        """Returns the rolename to be spoken for the object.
        """

        try:
            result = self._script.speechGenerator.getRoleName(obj, **args)
            if result:
                result = result[0]
            else:
                result = ""
        except:
            debug.printException(debug.LEVEL_WARNING)
            result = ""

        return result

    def _getGroupLabel(self, obj):
        """Returns the label for a group of components.
        """

        text = ""
        labelledBy = None

        relations = obj.getRelationSet()
        for relation in relations:
            if relation.getRelationType() ==  pyatspi.RELATION_LABELLED_BY:
                labelledBy = relation.getTarget(0)
                break

        if labelledBy:
            text = self.getObjLabelAndName(labelledBy)
        else:
            parent = obj.parent
            while parent and (parent.parent != parent):
                if parent.getRole() in [pyatspi.ROLE_PANEL,
                                        pyatspi.ROLE_FILLER]:
                    label = self.getObjLabelAndName(parent)
                    if label and label != "":
                        text = label
                        break
                parent = parent.parent

        return text

    def _getPositionInGroup(self, obj):
        """Returns the relative position of an object in a group.
        """

        text = ""
        position = -1
        total = -1

        relations = obj.getRelationSet()
        for relation in relations:
            if relation.getRelationType() == pyatspi.RELATION_MEMBER_OF:
                total = relation.getNTargets()
                for i in range(0, total):
                    target = relation.getTarget(i)
                    if target == obj:
                        position = total - i
                        break

        if position >= 0:
            # Translators: this is an item in a list.
            #
            text += _("item %d of %d") % (position, total)

        return text

    def _getPositionInList(self, obj, name):
        """Returns the relative position of an object in a list.
        """

        text = ""
        position = -1
        index = 0
        total = 0

        # We want to return the position relative to this hierarchical
        # level and not the entire list.  If the object in question
        # uses the NODE_CHILD_OF relationship, we need to use it instead
        # of the childCount.
        #
        childNodes = self._script.getChildNodes(obj)
        total = len(childNodes)
        for i in range(0, total):
            childName = self._getObjName(childNodes[i])
            if childName == name:
                position = i+1
                break

        if not total:
            for child in obj:
                next = self._getObjName(child)
                state = child.getState()
                if next in ["", "Empty", "separator"] \
                   or not state.contains(pyatspi.STATE_VISIBLE):
                    continue

                index += 1
                total += 1

                if next == name:
                    position = index


        if position >= 0:
            # Translators: this is an item in a list.
            #
            text = _("item %d of %d") % (position, total)

        return text

    def _getObjAccelerator(self,
                           obj,
                           fallbackToMnemonic=True,
                           fallbackToFullPath=True):
        """Returns the accelerator for the object, if it exists.
        """

        # We'll try the real accelerator first, but fallback to the
        # mnemonic if there is no accelerator.  This is done because
        # some implementations, such as the Java platform, will
        # only give us the mnemonic sometimes.
        #
        results = self._script.getKeyBinding(obj)
        if results[2]:
            return results[2]

        mnemonic = results[0]
        if mnemonic and fallbackToMnemonic:
            return mnemonic

        if fallbackToFullPath:
            return results[1]

        return ""

    def _getObjMnemonic(self, obj):
        """Returns the mnemonic (a letter) for the object, if it exists.
        """
        results = self._script.getKeyBinding(obj)
        return results[0][-1:]

    def _getSliderValues(self, obj):
        """Returns the slider's current value and percentage.
        """

        value = obj.queryValue()

        currentValue = "%.1f" % value.currentValue
        percent = value.currentValue / value.maximumValue * 100
        rounded = "%d" % round(percent, 5)

        debug.println(self._debugLevel,
            "_getSliderValues: min=%f, cur=%f, max=%f, str=%s, percent=%s" % \
            (value.minimumValue, value.currentValue, value.maximumValue, \
             currentValue, rounded))

        return [currentValue, rounded]

    def _getTableRow(self, obj):
        """Get the speech for a table cell row or a single table cell
        if settings.readTableCellRow is False.
        Also return a tutorial string if enableTutorialMessages is set.

        Arguments:
        - obj: the table
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        utterances = []

        parent = obj.parent
        try:
            table = parent.queryTable()
        except NotImplementedError:
            debug.println(self._debugLevel, "??? parent=%s" % parent.getRole())
            return []
        else:
            index = self._script.getCellIndex(obj)
            row = table.getRowAtIndex(index)
            for i in range(0, table.nColumns):
                acc = table.getAccessibleAt(row, i)
                utterances.append(self._getTableCell(acc))

            debug.println(self._debugLevel, "row=<%s>" % utterances)

            getTutorial = self._script.tutorialGenerator.getTutorial
            utterances.extend(getTutorial(obj, False, forceMessage=True))
            return utterances

    def _getTableCell(self, obj):
        """Get the speech utterances for a single table cell.
        """

        isToggle = False
        try:
            action = obj.queryAction()
        except NotImplementedError:
            pass
        else:
            for i in range(0, action.nActions):
                # Translators: this is the action name for
                # the 'toggle' action. It must be the same
                # string used in the *.po file for gail.
                #
                if action.getName(i) in ["toggle", _("toggle")]:
                    isToggle = True
                    break

        if isToggle:
            text = self._getSpeechForRoleName(obj, role=pyatspi.ROLE_CHECK_BOX)
            text = text + " " + self._getCheckBoxState(obj)
        else:
            descendant = self._script.getRealActiveDescendant(obj)
            text = self._script.getDisplayedText(descendant)

        debug.println(self._debugLevel, "cell=<%s>" % text)
        return text

    def _getCheckBoxState(self, obj):
        """Get the state of a checkbox/toggle-able table cell.
        """

        isToggle = (obj.getRole() == pyatspi.ROLE_CHECK_BOX)
        if not isToggle:
            try:
                action = obj.queryAction()
            except NotImplementedError:
                pass
            else:
                for i in range(0, action.nActions):
                    # Translators: this is the action name for
                    # the 'toggle' action. It must be the same
                    # string used in the *.po file for gail.
                    #
                    if action.getName(i) in ["toggle", _("toggle")]:
                        isToggle = True
                        break
        if not isToggle:
            return ""

        state = obj.getState()
        if state.contains(pyatspi.STATE_INDETERMINATE):
            # Translators: this represents the state of a checkbox.
            #
            text = _("partially checked")
        elif state.contains(pyatspi.STATE_CHECKED):
            # Translators: this represents the state of a checkbox.
            #
            text = _("checked")
        else:
            # Translators: this represents the state of a checkbox.
            #
            text = _("not checked")

        return text

    def getTextSelection(self, obj):
        """Get the text selection for the given object.

        Arguments:
        - obj: the text object to extract the selected text from.

        Returns: the selected text contents plus the start and end
        offsets within the text.
        """

        textContents = ""
        textObj = obj.queryText()
        nSelections = textObj.getNSelections()
        for i in range(0, nSelections):
            [startOffset, endOffset] = textObj.getSelection(i)

            debug.println(self._debugLevel,
                "getTextSelection: selection start=%d, end=%d" % \
                (startOffset, endOffset))

            selectedText = textObj.getText(startOffset, endOffset)
            debug.println(self._debugLevel,
                "getTextSelection: selected text=<%s>" % selectedText)

            if i > 0:
                textContents += " "
            textContents += selectedText

        return [textContents, startOffset, endOffset]

    def getTextSelections(self, obj, basicOnly):
        """Get all the text applicable text selections for the given object.
        If the user is doing a detailed whereAmI, look to see if there are
        any previous or next text objects that also have selected text and
        add in their text contents.

        Arguments:
        - obj: the text object to start extracting the selected text from.
        - basicOnly: True if the user is performing a standard/basic whereAmI.

        Returns: all the selected text contents plus the start and end
        offsets within the text for the given object.
        """

        textContents = ""
        startOffset = 0
        endOffset = 0
        text = obj.queryText()
        if text.getNSelections() > 0:
            [textContents, startOffset, endOffset] = \
                                            self.getTextSelection(obj)

        if not basicOnly:
            current = obj
            morePossibleSelections = True
            while morePossibleSelections:
                morePossibleSelections = False
                for relation in current.getRelationSet():
                    if relation.getRelationType() == \
                           pyatspi.RELATION_FLOWS_FROM:
                        prevObj = relation.getTarget(0)
                        prevObjText = prevObj.queryText()
                        if prevObjText.getNSelections() > 0:
                            [newTextContents, start, end] = \
                                         self.getTextSelection(prevObj)
                            textContents = newTextContents + " " + textContents
                            current = prevObj
                            morePossibleSelections = True
                        else:
                            displayedText = prevObjText.getText(0, -1)
                            if len(displayedText) == 0:
                                current = prevObj
                                morePossibleSelections = True
                        break

            current = obj
            morePossibleSelections = True
            while morePossibleSelections:
                morePossibleSelections = False
                for relation in current.getRelationSet():
                    if relation.getRelationType() == \
                           pyatspi.RELATION_FLOWS_TO:
                        nextObj = relation.getTarget(0)
                        nextObjText = nextObj.queryText()
                        if nextObjText.getNSelections() > 0:
                            [newTextContents, start, end] = \
                                         self.getTextSelection(nextObj)
                            textContents += " " + newTextContents
                            current = nextObj
                            morePossibleSelections = True
                        else:
                            displayedText = nextObjText.getText(0, -1)
                            if len(displayedText) == 0:
                                current = nextObj
                                morePossibleSelections = True
                        break

        else:
            # We're only interested in the text selected on this line.
            #
            [line, lineStart, lineEnd] = \
                   text.getTextAtOffset(text.caretOffset,
                                        pyatspi.TEXT_BOUNDARY_LINE_START)
            if lineStart != endOffset:
                startOffset = max(startOffset, lineStart)
                endOffset = min(endOffset, lineEnd)
                textContents = line[startOffset - lineStart:
                                    endOffset - lineStart]

        return [textContents, startOffset, endOffset]

    def _hasTextSelections(self, obj):
        """Return an indication of whether this object has selected text.
        Note that it's possible that this object has no text, but is part
        of a selected text area. Because of this, we need to check the
        objects on either side to see if they are none zero length and
        have text selections.

        Arguments:
        - obj: the text object to start checking for selected text.

        Returns: an indication of whether this object has selected text,
        or adjacent text objects have selected text.
        """

        currentSelected = False
        otherSelected = False
        text = obj.queryText()
        nSelections = text.getNSelections()
        if nSelections:
            currentSelected = True
        else:
            otherSelected = False
            text = obj.queryText()
            displayedText = text.getText(0, -1)
            if len(displayedText) == 0:
                current = obj
                morePossibleSelections = True
                while morePossibleSelections:
                    morePossibleSelections = False
                    for relation in current.getRelationSet():
                        if relation.getRelationType() == \
                               pyatspi.RELATION_FLOWS_FROM:
                            prevObj = relation.getTarget(0)
                            prevObjText = prevObj.queryText()
                            if prevObjText.getNSelections() > 0:
                                otherSelected = True
                            else:
                                displayedText = prevObjText.getText(0, -1)
                                if len(displayedText) == 0:
                                    current = prevObj
                                    morePossibleSelections = True
                            break

                current = obj
                morePossibleSelections = True
                while morePossibleSelections:
                    morePossibleSelections = False
                    for relation in current.getRelationSet():
                        if relation.getRelationType() == \
                               pyatspi.RELATION_FLOWS_TO:
                            nextObj = relation.getTarget(0)
                            nextObjText = nextObj.queryText()
                            if nextObjText.getNSelections() > 0:
                                otherSelected = True
                            else:
                                displayedText = nextObjText.getText(0, -1)
                                if len(displayedText) == 0:
                                    current = nextObj
                                    morePossibleSelections = True
                            break

        return [currentSelected, otherSelected]

    def _getTextContents(self, obj, basicOnly):
        """Returns utterences for text.

        A. if no text on the current line is selected, the current line
        B. if text is selected on the current line, that text, followed
        by 'selected'
        C. if the current line is blank/empty, 'blank'
        """

        textObj = obj.queryText()
        caretOffset = textObj.caretOffset
        textContents = ""
        selected = False

        nSelections = textObj.getNSelections()
        debug.println(self._debugLevel,
            "_getTextContents: caretOffset=%d, nSelections=%d" % \
            (caretOffset, nSelections))

        [current, other] = self._hasTextSelections(obj)
        if (not basicOnly and (current or other)) or \
           (basicOnly and current):
            selected = True
            [textContents, startOffset, endOffset] = \
                                  self.getTextSelections(obj, basicOnly)
        else:
            # Get the line containing the caret
            #
            [line, startOffset, endOffset] = textObj.getTextAtOffset(
                textObj.caretOffset,
                pyatspi.TEXT_BOUNDARY_LINE_START)
            debug.println(self._debugLevel, \
                "_getTextContents: len=%d, start=%d, end=%d, line=<%s>" % \
                (len(line), startOffset, endOffset, line))

            if len(line):
                line = self._script.adjustForRepeats(line)
                textContents = line
            else:
                char = textObj.getTextAtOffset(caretOffset,
                    pyatspi.TEXT_BOUNDARY_CHAR)
                debug.println(self._debugLevel,
                    "_getTextContents: character=<%s>, start=%d, end=%d" % \
                    (char[0], char[1], char[2]))

                if char[0] == "\n" and startOffset == caretOffset \
                       and settings.speakBlankLines:
                    # Translators: "blank" is a short word to mean the
                    # user has navigated to an empty line.
                    #
                    textContents = (_("blank"))

        return [textContents, startOffset, endOffset, selected]

    def _insertAttributes(self, obj, startOffset, endOffset, line):
        """Adjust line to include attribute information.
        """

        try:
            text = obj.queryText()
        except NotImplementedError:
            return ""

        newLine = ""
        textOffset = startOffset

        for i in range(0, len(line)):
            attribs = self._getAttributesForChar(obj, text, textOffset, line, i)
            debug.println(self._debugLevel,
                          "line attribs <%s>" % (attribs))
            if attribs:
                if newLine:
                    newLine += " ; "
                newLine += attribs
                newLine += " "

            newLine += line[i]
            textOffset += 1

        attribs = self._getAttributesForChar(obj,
                                             text,
                                             startOffset,
                                             line,
                                             0,
                                             ["paragraph-style"])
        if attribs:
            if newLine:
                newLine += " ; "
            newLine += attribs

        debug.println(self._debugLevel, "newLine: <%s>" % (newLine))

        return newLine

    def _getAttributesForChar(self,
                              obj,
                              text,
                              textOffset,
                              line,
                              lineIndex,
                              keys=["style", "weight", "underline"]):

        attribStr = ""

        defaultAttributes = text.getDefaultAttributes()
        attributesDictionary = self._stringToDictionary(defaultAttributes)

        charAttributes = text.getAttributes(textOffset)
        if charAttributes[0]:
            charDict = self._stringToDictionary(charAttributes[0])
            for key in charDict.keys():
                attributesDictionary[key] = charDict[key]

        if attributesDictionary:
            for key in keys:
                localizedKey = text_attribute_names.getTextAttributeName(key)
                if key in attributesDictionary:
                    attribute = attributesDictionary[key]
                    localizedValue = \
                        text_attribute_names.getTextAttributeName(attribute)
                    if attribute:
                        # If it's the 'weight' attribute and greater than 400,
                        # just speak it as bold, otherwise speak the weight.
                        #
                        if key == "weight":
                            if int(attribute) > 400:
                                attribStr += " "
                                # Translators: bold as in the font sense.
                                #
                                attribStr += _("bold")
                        elif key == "underline":
                            if attribute != "none":
                                attribStr += " "
                                attribStr += localizedKey
                        elif key == "style":
                            if attribute != "normal":
                                attribStr += " "
                                attribStr += localizedValue
                        else:
                            attribStr += " "
                            attribStr += (localizedKey + " " + localizedValue)

            # Also check to see if this is a hypertext link.
            #
            if self._script.getLinkIndex(obj, textOffset) >= 0:
                attribStr += " "
                # Translators: this indicates that this piece of
                # text is a hypertext link.
                #
                attribStr += _("link")

            if line:
                debug.println(self._debugLevel,
                              "char <%s>: %s" % (line[lineIndex], attribStr))

        # Only return attributes for the beginning of an attribute run.
        if attribStr != self._lastAttributeString:
            self._lastAttributeString = attribStr
            return attribStr
        else:
            return ""

    def _stringToDictionary(self, tokenString):
        """Converts a string of text attribute tokens of the form
        <key>:<value>; into a dictionary of keys and values.
        Text before the colon is the key and text afterwards is the
        value. If there is a final semi-colon, then it's ignored.
        """

        dictionary = {}
        allTokens = tokenString.split(";")
        for token in allTokens:
            item = token.split(":")
            if len(item) == 2:
                item[0] = item[0].lstrip()
                item[1] = item[1].lstrip()
                dictionary[item[0]] = item[1]

        return dictionary

    def speakTitle(self, obj):
        """Orca will speak the following information:

        1. The contents of the title bar of the application main window
        2. If in a dialog box within an application, the contents of the
        title bar of the dialog box.
        3. '<n> unfocused dialogs' if this application has more than
           one unfocused alert or dialog window.
        4. Orca will pause briefly between these two pieces of information
        so that the speech user can distinguish each.
        """

        utterances = []

        results = self._getFrameAndDialog(obj)

        if results[0]:
            text = self.getObjLabelAndName(results[0])
            utterances.append(text)
        if results[1]:
            text = self.getObjLabelAndName(results[1])
            utterances.append(text)

        alertAndDialogCount = \
                    self._script.getUnfocusedAlertAndDialogCount(obj)
        if alertAndDialogCount > 0:
            # Translators: this tells the user how many unfocused
            # alert and dialog windows that this application has.
            #
            line = ngettext("%d unfocused dialog",
                            "%d unfocused dialogs",
                            alertAndDialogCount) % alertAndDialogCount
            utterances.append(line)

        debug.println(self._debugLevel, "titlebar utterances=%s" % \
                      utterances)
        speech.speak(utterances)

    def speakStatusBar(self, obj):
        """Speak the contents of the status bar of the window with focus.
        """

        utterances = []

        results = self._getFrameAndDialog(obj)

        if results[0]:
            self._statusBar = None
            self._getStatusBar(results[0])
            if self._statusBar:
                self._speakStatusBar()
        window = results[1] or results[0]
        if window:
            self._speakDefaultButton(window)

        debug.println(self._debugLevel, "status bar utterances=%s" % \
                      utterances)
        speech.speak(utterances)

    def _getFrameAndDialog(self, obj):
        """Returns the frame and (possibly) the dialog containing
        the object.
        """

        results = [None, None]

        parent = obj.parent
        while parent and (parent.parent != parent):
            #debug.println(self._debugLevel,
            #              "_getFrameAndDialog: parent=%s, %s" % \
            #              (parent.getRole(), self.getObjLabelAndName(parent)))
            if parent.getRole() == pyatspi.ROLE_FRAME:
                results[0] = parent
            if parent.getRole() in [pyatspi.ROLE_DIALOG,
                                    pyatspi.ROLE_FILE_CHOOSER]:
                results[1] = parent
            parent = parent.parent

        return results

    def _getStatusBar(self, obj):
        """Gets the status bar.
        """
        if self._statusBar:
            return

        # debug.println(self._debugLevel, "_findStatusBar: ROOT=%s, %s" % \
        #               (obj.getRole(), self.getObjLabelAndName(obj)))
        state = obj.getState()
        managesDescendants = state.contains(pyatspi.STATE_MANAGES_DESCENDANTS)
        if managesDescendants:
            return

        for child in obj:
            # debug.println(self._debugLevel,
            #               "_findStatusBar: child=%s, %s" % \
            #               (child.getRole(), self.getObjLabelAndName(child)))
            if child.getRole() == pyatspi.ROLE_STATUS_BAR:
                self._statusBar = child
                return

            if child.childCount > 0:
                self._getStatusBar(child)

    def _speakStatusBar(self):
        """Speaks the status bar.
        """

        if not self._statusBar:
            return

        utterances = []

        text = self._getObjName(self._statusBar)
        if text:
            utterances.append(text)
        elif self._statusBar.childCount:
            for child in self._statusBar:
                text = self._getObjName(child)
                utterances.append(text)

        debug.println(self._debugLevel, "statusbar utterances=%s" % \
                      utterances)
        speech.speak(utterances)

    def _getDefaultButton(self, obj):
        """Gets the default button in a dialog.

        Arguments:
        - obj: the dialog box for which the default button should be obtained
        """

        defaultButton = None
        for child in obj:
            # debug.println(self._debugLevel,
            #               "_getDefaultButton: child=%s, %s" % \
            #               (child.getRole(), self.getObjLabelAndName(child)))
            state = child.getState()
            if child.getRole() == pyatspi.ROLE_PUSH_BUTTON \
                and state.contains(pyatspi.STATE_IS_DEFAULT):
                defaultButton = child
            else:
                defaultButton = self._getDefaultButton(child)

            if defaultButton:
                break

        return defaultButton

    def _speakDefaultButton(self, obj):
        """Speaks the default button in a dialog.

        Arguments:
        - obj: the dialog box for which the default button should be obtained
        """

        defaultButton = self._getDefaultButton(obj)

        if not defaultButton:
            return

        state = defaultButton.getState()
        if not state.contains(pyatspi.STATE_SENSITIVE):
            return

        utterances = []

        # Translators: The "default" button in a dialog box is the button
        # that gets activated when Enter is pressed anywhere within that
        # dialog box.
        #
        text = _("Default button is %s") % \
               self._getObjName(defaultButton)
        utterances.append(text)

        debug.println(self._debugLevel, "default button utterances=%s" % \
                      utterances)
        speech.speak(utterances)

    def _speakObjDescription(self, obj):
        """Speaks the object's description if it is not the same as
        the object's name or label.
        """

        description = obj.description
        name = self._getObjName(obj)
        label = self._getObjLabel(obj)

        if description and not description in [name, label]:
            speech.speak(description)

    def _getToolbar(self, obj):
        """Returns the toolbar containing the object or None if the object
        is not contained in a toolbar.
        """

        parent = obj.parent
        while parent and (parent.parent != parent):
            if parent.getRole() == pyatspi.ROLE_TOOL_BAR:
                return parent
            parent = parent.parent

        return None

    def _speakToolbar(self, obj):
        """Speaks the label and/or name of a toolbar, followed by its role.
        """

        utterances = []
        text = self.getObjLabelAndName(obj) + " " + \
               self._getSpeechForRoleName(obj)
        utterances.append(text.strip())

        debug.println(self._debugLevel, "toolbar utterances=%s" \
                      % utterances)
        speech.speak(utterances)

    def _getRequiredState(self, obj):
        """Returns a string describing the required state of the given
        object.

        Arguments:
        - obj: the Accessible object
        """

        if not settings.presentRequiredState:
            return ""

        if obj.getRole() == pyatspi.ROLE_RADIO_BUTTON:
            obj = obj.parent

        state = obj.getState()
        if state.contains(pyatspi.STATE_REQUIRED):
            return settings.speechRequiredStateString
        else:
            return ""
