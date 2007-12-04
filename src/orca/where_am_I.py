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

"""Speaks information about the current object of interest."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2007 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi
import debug
import orca_state
import rolenames
import settings
import speech
import urlparse, urllib2

from orca_i18n import _ # for gettext support
from orca_i18n import ngettext  # for ngettext support
from orca_i18n import Q_ # to provide qualified translatable strings

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

    def whereAmI(self, obj, doubleClick, titleOrStatus):
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
           \n  mnemonics=%s \
           \n  parent label= %s \
           \n  parent name=%s \
           \n  parent role=%s \
           \n  double-click=%s \
           \n  titleOrStatus=%s" % \
            (self._getObjLabel(obj),
             self._getObjName(obj),
             obj.getRoleName(),
             self._script.getAcceleratorAndShortcut(obj),
             self._getObjLabel(obj.parent),
             self._getObjName(obj.parent),
             obj.parent.getRoleName(),
             doubleClick,
             titleOrStatus))

        role = obj.getRole()

        if titleOrStatus:
            self._speakTitleOrStatus(obj, doubleClick)

        elif role == pyatspi.ROLE_CHECK_BOX:
            self._speakCheckBox(obj, doubleClick)

        elif role == pyatspi.ROLE_RADIO_BUTTON:
            self._speakRadioButton(obj, doubleClick)

        elif role == pyatspi.ROLE_COMBO_BOX:
            self._speakComboBox(obj, doubleClick)

        elif role == pyatspi.ROLE_SPIN_BUTTON:
            self._speakSpinButton(obj, doubleClick)

        elif role == pyatspi.ROLE_PUSH_BUTTON:
            self._speakPushButton(obj, doubleClick)

        elif role == pyatspi.ROLE_SLIDER:
            self._speakSlider(obj, doubleClick)

        elif role in [pyatspi.ROLE_MENU,
                      pyatspi.ROLE_MENU_ITEM,
                      pyatspi.ROLE_CHECK_MENU_ITEM,
                      pyatspi.ROLE_RADIO_MENU_ITEM]:
            self._speakMenuItem(obj, doubleClick)

        elif role == pyatspi.ROLE_PAGE_TAB:
            self._speakPageTab(obj, doubleClick)

        elif role in [pyatspi.ROLE_TEXT,
                      pyatspi.ROLE_TERMINAL]:
            self._speakText(obj, doubleClick)

        elif role == pyatspi.ROLE_TABLE_CELL:
            self._speakTableCell(obj, doubleClick)

        elif role == pyatspi.ROLE_LIST_ITEM:
            self._speakListItem(obj, doubleClick)

        elif role == pyatspi.ROLE_PARAGRAPH:
            self._speakParagraph(obj, doubleClick)

        elif role == pyatspi.ROLE_ICON:
            self._speakIconPanel(obj, doubleClick)
            
        elif role == pyatspi.ROLE_LINK:
            self._speakLink(obj, doubleClick)

        elif role == pyatspi.ROLE_TOGGLE_BUTTON:
            self._speakToggleButton(obj, doubleClick)

        else:
            self._speakGenericObject(obj, doubleClick)

        if not (doubleClick or titleOrStatus):
            self._speakObjDescription(obj)

        return True

    def _speakCheckBox(self, obj, doubleClick):
        """Checkboxes present the following information
        (an example is 'Enable speech, checkbox checked, Alt E'):
        1. label
        2. role
        3. state
        4. mnemonic (i.e. Alt plus the underlined letter), if any
        """

        utterances = []
        text = self.getObjLabelAndName(obj) + " " + \
               rolenames.getSpeechForRoleName(obj)
        text = text + " " + self._getCheckBoxState(obj)
        utterances.append(text)

        text = self._getObjMnemonic(obj)
        utterances.append(text)

        debug.println(self._debugLevel, "check box utterances=%s" \
                      % utterances)
        speech.speakUtterances(utterances)

    def _speakRadioButton(self, obj, doubleClick):
        """Radio Buttons present the following information (an example is
        'Punctuation Level, Some, Radio button, selected, item 2 of 4, Alt M'):

        1. group name
        2. label
        3. role
        4. state
        5. relative position
        6. mnemonic (i.e. Alt plus the underlined letter), if any
        """

        utterances = []
        text = self._getGroupLabel(obj)
        utterances.append(text)

        text = self.getObjLabelAndName(obj) + " " + \
               rolenames.getSpeechForRoleName(obj)
        utterances.append(text)

        state = obj.getState()
        if state.contains(pyatspi.STATE_CHECKED):
            # Translators: this is in reference to a radio button being
            # selected or not.
            #
            # ONLY TRANSLATE THE PART AFTER THE PIPE CHARACTER |
            #
            text = Q_("radiobutton|selected")
        else:
            # Translators: this is in reference to a radio button being
            # selected or not.
            #
            # ONLY TRANSLATE THE PART AFTER THE PIPE CHARACTER |
            #
            text = Q_("radiobutton|not selected")

        utterances.append(text)

        text = self._getPositionInGroup(obj)
        utterances.append(text)

        text = self._getObjMnemonic(obj)
        utterances.append(text)

        debug.println(self._debugLevel, "radio button utterances=%s" % \
                      utterances)
        speech.speakUtterances(utterances)

    def _speakComboBox(self, obj, doubleClick):
        """Comboboxes present the following information (an example is
        'Speech system: combo box, GNOME Speech Services, item 1 of 1,
        Alt S'):
        1. label
        2. role
        3. current value
        4. relative position
        5. mnemonic (i.e. Alt plus the underlined letter), if any
        """

        utterances = []
        text = self._getObjLabel(obj)
        utterances.append(text)

        text = rolenames.getSpeechForRoleName(obj)
        utterances.append(text)

        name = self._getObjName(obj)
        utterances.append(name)

        # child(0) is the popup list
        text = self._getPositionInList(obj[0], name)
        utterances.append(text)

        text = self._getObjMnemonic(obj)
        utterances.append(text)

        debug.println(self._debugLevel, "combo box utterances=%s" % \
                      utterances)
        speech.speakUtterances(utterances)

    def _speakSpinButton(self, obj, doubleClick):
        """Spin Buttons present the following information (an example is
        'Scale factor: spin button, 4.00, Alt F'):

        1. label
        2. role
        3. current value
        4. mnemonic (i.e. Alt plus the underlined letter), if any
        """

        utterances = []
        text = self._getObjLabel(obj)
        utterances.append(text)

        text = rolenames.getSpeechForRoleName(obj)
        utterances.append(text)

        name = self._getObjName(obj)
        utterances.append(name)
        
        text = self._getObjMnemonic(obj)
        utterances.append(text)

        debug.println(self._debugLevel, "spin button utterances=%s" % \
                      utterances)
        speech.speakUtterances(utterances)

    def _speakPushButton(self, obj, doubleClick):
        """ Push Buttons present the following information (an example is
        'Apply button, Alt A'):

        1. label
        2. role
        3. mnemonic (i.e. Alt plus the underlined letter), if any
        """

        utterances = []
        text = self.getObjLabelAndName(obj)
        utterances.append(text)

        text = rolenames.getSpeechForRoleName(obj)
        utterances.append(text)

        text = self._getObjMnemonic(obj)
        utterances.append(text)

        debug.println(self._debugLevel, "push button utterances=%s" % \
                      utterances)
        speech.speakUtterances(utterances)

    def _speakSlider(self, obj, doubleClick):
        """Sliders present the following information (examples include
        'Pitch slider, 5.0, 56%'; 'Volume slider, 9.0, 100%'):

        1. label
        2. role
        3. value
        4. percentage (if possible)
        5. mnemonic (i.e. Alt plus the underlined letter), if any
        """

        utterances = []
        text = self._getObjLabel(obj)
        utterances.append(text)

        text = rolenames.getSpeechForRoleName(obj)
        utterances.append(text)

        values = self._getSliderValues(obj)
        utterances.append(values[0])
        # Translators: this is the percentage value of a slider.
        #
        utterances.append(_("%s percent") % values[1])

        text = self._getObjMnemonic(obj)
        utterances.append(text)

        debug.println(self._debugLevel, "slider utterances=%s" % \
                      utterances)
        speech.speakUtterances(utterances)

    def _speakMenuItem(self, obj, doubleClick):
        """Menu items present the following information (examples include
        'File menu, Open..., Control + O, item 2 of 20, O', 'File menu,
        Wizards Menu, item 4 of 20, W'):

        1. Name of the menu containing the item, followed by its role
        2. item name, followed by its role (if a menu) followed by its
        accelerator key, if any
        3. relative position
        4. mnemonic (i.e. Alt plus the underlined letter), if any
        """

        utterances = []
        text = self.getObjLabelAndName(obj.parent) + " " + \
               rolenames.getSpeechForRoleName(obj.parent)
        utterances.append(text)

        text = self.getObjLabelAndName(obj)
        utterances.append(text)

        state = obj.getState()

        if obj.getRole() != pyatspi.ROLE_MENU_ITEM:
            text = rolenames.getSpeechForRoleName(obj)
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

        text = self._getObjAccelerator(obj)
        utterances.append(text)

        name = self._getObjName(obj)
        text = self._getPositionInList(obj.parent, name)
        utterances.append(text)

        text = self._getObjShortcut(obj)

        # The object's shortcut will be the full list of keys (e.g.
        # Alt FO for the open menu item in the File menu). We only
        # want to speak the shortcut associated with the menu item.
        #
        if text and obj.parent and obj.parent.getRole() == pyatspi.ROLE_MENU:
            text = text[-1]
        
        utterances.append(text)

        debug.println(self._debugLevel, "menu item utterances=%s" % \
                      utterances)
        speech.speakUtterances(utterances)

    def _speakPageTab(self, obj, doubleClick):
        """Tabs in a Tab List present the following information (an example
        is 'Tab list, braille page, item 2 of 5'):

        1. role
        2. label + 'page'
        3. relative position
        4. mnemonic (i.e. Alt plus the underlined letter), if any
        """

        utterances = []
        text = rolenames.getSpeechForRoleName(obj.parent)
        utterances.append(text)

        # Translators: "page" is the word for a page tab in a tab list.
        #
        text = _("%s page") % self.getObjLabelAndName(obj)
        utterances.append(text)

        name = self._getObjName(obj)
        text = self._getPositionInList(obj.parent, name)
        utterances.append(text)

        text = self._getObjMnemonic(obj)
        utterances.append(text)

        debug.println(self._debugLevel, "page utterances=%s" % \
                      utterances)
        speech.speakUtterances(utterances)

    def _speakText(self, obj, doubleClick):
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
        4. mnemonic (i.e. Alt plus the underlined letter), if any

        Gaim, gedit, OpenOffice Writer and Terminal
        """

        utterances = []
        text = self._getObjLabel(obj)
        utterances.append(text)

        text = rolenames.getSpeechForRoleName(obj)
        utterances.append(text)

        [textContents, startOffset, endOffset, selected] = \
                       self._getTextContents(obj, doubleClick)
        if doubleClick:
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
        speech.speakUtterances(utterances)

        if doubleClick:
            settings.verbalizePunctuationStyle = savedStyle

        utterances = []
        if selected:
            # Translators: when the user selects (highlights) text in
            # a document, Orca lets them know this.
            #
            # ONLY TRANSLATE THE PART AFTER THE PIPE CHARACTER |
            #
            text = Q_("text|selected")
            utterances.append(text)

        text = self._getObjMnemonic(obj)
        utterances.append(text)

        debug.println(self._debugLevel, "text utterances=%s" % \
                      utterances)
        speech.speakUtterances(utterances)

    def _speakTableCell(self, obj, doubleClick):
        """Tree Tables present the following information (an example is
        'Tree table, Mike Pedersen, item 8 of 10, tree level 2'):

        1. label, if any
        2. role
        3. current row (regardless of speak cell/row setting)
        4. relative position
        5. if expandable/collapsible: expanded/collapsed
        6. if applicable, the level

        Nautilus and Gaim
        """

        # Speak the first two items (and possibly the position)
        utterances = []
        if obj.parent.getRole() == pyatspi.ROLE_TABLE_CELL:
            obj = obj.parent
        parent = obj.parent

        text = self._getObjLabel(obj)
        utterances.append(text)

        text = rolenames.getSpeechForRoleName(obj)
        utterances.append(text)
        debug.println(self._debugLevel, "first table cell utterances=%s" % \
                      utterances)
        speech.speakUtterances(utterances)

        utterances = []
        if doubleClick:
            table = parent.queryTable()
            row = table.getRowAtIndex(
              orca_state.locusOfFocus.getIndexInParent())
            # Translators: this in reference to a row in a table.
            #
            text = _("row %d of %d") % ((row+1), table.nRows)
            utterances.append(text)
            speech.speakUtterances(utterances)

        # Speak the current row
        utterances = self._getTableRow(obj)
        debug.println(self._debugLevel, "second table cell utterances=%s" % \
                      utterances)
        speech.speakUtterances(utterances)

        # Speak the remaining items.
        utterances = []

        if not doubleClick:
            try:
                table = parent.queryTable()
            except NotImplementedError:
                debug.println(self._debugLevel, 
                              "??? parent=%s" % parent.getRoleName())
                return
            else:
                row = \
                    table.getRowAtIndex(
                       orca_state.locusOfFocus.getIndexInParent())
                # Translators: this in reference to a row in a table.
                #
                text = _("row %d of %d") % ((row+1), table.nRows)
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

        debug.println(self._debugLevel, "third table cell utterances=%s" % \
                      utterances)
        speech.speakUtterances(utterances)

    def _speakListItem(self, obj, doubleClick):
        """List items should be treated like tree cells:

        1. label, if any
        2. role
        3. name
        4. relative position
        5. if expandable/collapsible: expanded/collapsed
        6. if applicable, the level
        """

        utterances = []

        text = self._getObjLabel(obj)
        utterances.append(text)

        text = rolenames.getSpeechForRoleName(obj)
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

        debug.println(self._debugLevel, "list item utterances=%s" % \
                      utterances)
        speech.speakUtterances(utterances)

    def _speakParagraph(self, obj, doubleClick):
        """Speak a paragraph object.
        """

        self._speakText(obj, doubleClick)

    def _speakIconPanel(self, obj, doubleClick):
        """Speak the contents of the pane containing this icon. The
        number of icons in the pane is spoken. Plus the total number of
        selected icons. Plus the name of each of the selected icons.

        Arguments:
        - obj: the icon object that currently has focus.
        """

        utterances = []
        panel = obj.parent
        childCount = panel.childCount

        utterances.append(_("Icon panel"))
        utterances.append(self.getObjLabelAndName(obj))

        selectedItems = []
        totalSelectedItems = 0
        currentItem = 0
        for child in panel:
            state = child.getState()
            if state.contains(pyatspi.STATE_SELECTED):
                totalSelectedItems += 1
                selectedItems.append(child)
            if state.contains(pyatspi.STATE_FOCUSED):
                currentItem = child.getIndexInParent() + 1

        # Translators: this is a count of the number of selected icons 
        # and the count of the total number of icons within an icon panel. 
        # An example of an icon panel is the Nautilus folder view.
        #
        itemString = ngettext("%d of %d item selected",
                              "%d of %d items selected",
                              childCount) % \
                              (totalSelectedItems, childCount)
        utterances.append(itemString)

        # Translators: this is a indication of the focused icon and the
        # count of the total number of icons within an icon panel. An
        # example of an icon panel is the Nautilus folder view.
        #
        itemString = _("on item %d of %d") % (currentItem, childCount)
        utterances.append(itemString)

        if doubleClick:
            for i in range(0, len(selectedItems)):
                utterances.append(self.getObjLabelAndName(selectedItems[i]))

        speech.speakUtterances(utterances)
        
    def _speakLink(self, obj, doubleClick):
        """Speaks information about a link including protocol, domain 
        comparisons and size of file if possible
        
        Arguments:
        - obj: the icon object that currently has focus.
        - doubleClick: was it a doubleclick event?
        """
        
        # get the URI for the link of interest and parse it.
        # parsed URI is returned as a tuple containing six components: 
        # scheme://netloc/path;parameters?query#fragment.
        link_uri = self._script.getURI(obj)
        if link_uri:
            link_uri_info = urlparse.urlparse(link_uri)
        else:
            # something is wrong, just return
            return
      
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

        speech.speakUtterances([linkoutput, domainoutput, sizeoutput])

    def _speakToggleButton(self, obj, doubleClick):
        """Speak toggle button information:
           1. Name/Label
           2. Role
           3. State (pressed/not pressed)
        """

        utterances = []
        text = self.getObjLabelAndName(obj)
        utterances.append(text)

        text = rolenames.getSpeechForRoleName(obj)
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

        speech.speakUtterances(utterances)
      
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

    def _speakGenericObject(self, obj, doubleClick):
        """Speak a generic object; one not specifically handled by
        other methods.
        """

        utterances = []
        text = self.getObjLabelAndName(obj)
        utterances.append(text)

        text = rolenames.getSpeechForRoleName(obj)
        utterances.append(text)
        speech.speakUtterances(utterances)

    def _getObjName(self, obj):
        """Returns the name to speak for an object.
        """

        text = ""
        name = self._script.getDisplayedText(obj)
        if not name:
            name = obj.description

        if name and name != "None":
            text = name
        debug.println(self._debugLevel, "%s name=<%s>" % (obj.getRole(), text))

        return text

    def _getObjLabel(self, obj):
        """Returns the label to speak for an object.
        """

        text = ""
        label = self._script.getDisplayedLabel(obj)

        if label and label != "None":
            text = label

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

    def _getObjMnemonic(self, obj):
        """Returns the accellerator and/or shortcut for the object,
        if either exists.
        """

        results = self._script.getAcceleratorAndShortcut(obj)

        text = ""
        if not results[1]:
            text = results[0]
        else:
            text = results[0] + " " +  results[1]

        return text

    def _getObjAccelerator(self, obj):
        """Returns the accelerator for the object, if it exists.
        """

        results = self._script.getAcceleratorAndShortcut(obj)

        text = ""
        if results[0]:
            text = results[0]

        return text

    def _getObjShortcut(self, obj):
        """Returns the shortcut for the object, if it exists.
        """

        results = self._script.getAcceleratorAndShortcut(obj)

        text = ""
        if results[1]:
            text = results[1]

        return text

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
            row = table.getRowAtIndex(obj.getIndexInParent())

            for i in range(0, table.nColumns):
                acc = table.getAccessibleAt(row, i)
                utterances.append(self._getTableCell(acc))

            debug.println(self._debugLevel, "row=<%s>" % utterances)

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
                if action.getName(i) == "toggle":
                    isToggle = True
                    break

        if isToggle:
            text = rolenames.getSpeechForRoleName(obj, pyatspi.ROLE_CHECK_BOX)
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
                    if action.getName(i) == "toggle":
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

    def _getTextSelection(self, obj):
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
                "_getTextSelection: selection start=%d, end=%d" % \
                (startOffset, endOffset))

            selectedText = textObj.getText(startOffset, endOffset)
            debug.println(self._debugLevel,
                "_getTextSelection: selected text=<%s>" % selectedText)

            if i > 0:
                textContents += " "
            textContents += selectedText

        return [textContents, startOffset, endOffset]

    def getTextSelections(self, obj, doubleClick):
        """Get all the text applicable text selections for the given object.
        If the user doubleclicked, look to see if there are any previous 
        or next text objects that also have selected text and add in their 
        text contents.

        Arguments:
        - obj: the text object to start extracting the selected text from.
        - doubleClick: True if the user double-clicked the "where am I" key.

        Returns: all the selected text contents plus the start and end
        offsets within the text for the given object.
        """

        textContents = ""
        startOffset = 0
        endOffset = 0
        text = obj.queryText()
        if text.getNSelections() > 0:
            [textContents, startOffset, endOffset] = \
                                            self._getTextSelection(obj)

        if doubleClick:
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
                                         self._getTextSelection(prevObj)
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
                                         self._getTextSelection(nextObj)
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

    def _getTextContents(self, obj, doubleClick):
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
        if (doubleClick and (current or other)) or \
           (not doubleClick and current):
            selected = True
            [textContents, startOffset, endOffset] = \
                                  self.getTextSelections(obj, doubleClick)
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
            attribs = self._getAttributesForChar(text, textOffset, line, i)
            debug.println(self._debugLevel,
                          "line attribs <%s>" % (attribs))
            if attribs:
                newLine += " ; "
                newLine += attribs
                newLine += " "

            newLine += line[i]
            textOffset += 1

        debug.println(self._debugLevel, "newLine: <%s>" % (newLine))

        return newLine

    def _getAttributesForChar(self, text, textOffset, line, lineIndex):

        keys = [ "style", "weight", "underline" ]
        attribStr = ""
        charAttributes = text.getAttributes(textOffset)

        if charAttributes[0]:
            charDict = self._stringToDictionary(charAttributes[0])
            debug.println(self._debugLevel,
                          "charDict: %s" % (charDict))

            for key in keys:
                if charDict.has_key(key):
                    attribute = charDict[key]
                    if attribute:
                        # If it's the 'weight' attribute and greater than 400,
                        # just speak it as bold, otherwise speak the weight.
                        #
                        if key == "weight" and int(attribute) > 400:
                            attribStr += " "
                            # Translators: bold as in the font sense.
                            #
                            attribStr += _("bold")

                        elif key == "underline":
                            if attribute != "none":
                                attribStr += " "
                                attribStr += key

                        elif key == "style":
                            if attribute != "normal":
                                attribStr += " "
                                attribStr += attribute
                        else:
                            attribStr += " "
                            attribStr += (key + " " + attribute)

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

    def _speakTitleOrStatus(self, obj, doubleClick):
        """When pressed a single time, Orca will speak the following
        information:

        1. The contents of the title bar of the application main window
        2. If in a dialog box within an application, the contents of the
        title bar of the dialog box.
        3. Orca will pause briefly between these two pieces of information
        so that the speech user can distinguish each.

        If pressed twice, Orca will speak the status bar.
        """

        utterances = []

        results = self._getFrameAndDialog(obj)

        if doubleClick:
            if results[0]:
                self._statusBar = None
                self._getStatusBar(results[0])
                if self._statusBar:
                    self._speakStatusBar()
            window = results[1] or results[0]
            if window:
                self._speakDefaultButton(window)
        else:
            if results[0]:
                text = self.getObjLabelAndName(results[0])
                utterances.append(text)
            if results[1]:
                text = self.getObjLabelAndName(results[1])
                utterances.append(text)

            debug.println(self._debugLevel, "titlebar utterances=%s" % \
                          utterances)
            speech.speakUtterances(utterances)

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
        speech.speakUtterances(utterances)

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
        speech.speakUtterances(utterances)

    def _speakObjDescription(self, obj):
        """Speaks the object's description if it is not the same as
        the object's name or label.
        """

        description = obj.description
        name = self._getObjName(obj)
        label = self._getObjLabel(obj)

        if description and not description in [name, label]:
            speech.speak(description)
