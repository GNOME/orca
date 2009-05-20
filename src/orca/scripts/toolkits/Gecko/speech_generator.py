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

"""Custom script for Gecko toolkit.
Please refer to the following URL for more information on the AT-SPI
implementation in Gecko:
http://developer.mozilla.org/en/docs/Accessibility/ATSPI_Support
"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.rolenames as rolenames
import orca.speechgenerator as speechgenerator

from orca.orca_i18n import _
from orca.orca_i18n import ngettext # for ngettext support

########################################################################
#                                                                      #
# Custom SpeechGenerator                                               #
#                                                                      #
########################################################################

class SpeechGenerator(speechgenerator.SpeechGenerator):
    """Provides a speech generator specific to Gecko.
    """

    # pylint: disable-msg=W0142

    def __init__(self, script):
        speechgenerator.SpeechGenerator.__init__(self, script)

    def _getName(self, obj, **args):
        result = []
        role = args.get('role', obj.getRole())
        if role == pyatspi.ROLE_COMBO_BOX:
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
                        result = \
                            speechgenerator.SpeechGenerator._getDisplayedText(
                                self, obj, **args)
                except:
                    # But just in case, we'll fall back on this.
                    # [[[TODO - JD: Will we ever have a case where the first
                    # fails, but this will succeed???]]]
                    #
                    for item in menu:
                        if item.getState().contains(pyatspi.STATE_SELECTED):
                            child = item
                            break
                if child and child.name:
                    result.append(child.name)
        else:
            result.extend(speechgenerator.SpeechGenerator._getName(self,
                                                                   obj,
                                                                   **args))
        if role == pyatspi.ROLE_LINK:
            # Handle empty alt tags.
            #
            if result and len(result[0].strip()):
                pass
            else:
                # If there's no text for the link, expose part of the
                # URI to the user.
                #
                basename = self._script.getLinkBasename(obj)
                if basename:
                    result.append(basename)
        return result

    def _getLabel(self, obj, **args):
        result = speechgenerator.SpeechGenerator._getLabel(self, obj, **args)
        role = args.get('role', obj.getRole())
        # We'll attempt to guess the label under some circumstances.
        #
        if not len(result) \
           and role in [pyatspi.ROLE_CHECK_BOX,
                        pyatspi.ROLE_COMBO_BOX,
                        pyatspi.ROLE_ENTRY,
                        pyatspi.ROLE_LIST,
                        pyatspi.ROLE_PARAGRAPH,
                        pyatspi.ROLE_PASSWORD_TEXT,
                        pyatspi.ROLE_RADIO_BUTTON,
                        pyatspi.ROLE_TEXT] \
           and self._script.inDocumentContent() \
           and not self._script.isAriaWidget(obj):
            label = self._script.guessTheLabel(obj)
            if label:
                result.append(label)
        return result

    def _getLabelAndName(self, obj, **args):
        result = []
        role = args.get('role', obj.getRole())
        # For radio buttons, the label is handled as a context and we
        # assume we don't have to guess it.  If we need to guess it,
        # we need to add it to utterances.
        #
        if role == pyatspi.ROLE_RADIO_BUTTON \
           and self._script.getDisplayedLabel(obj):
            pass
        else:
            result.extend(speechgenerator.SpeechGenerator._getLabelAndName(
                self, obj, **args))
        return result

    def _getLabelOrName(self, obj, **args):
        result = []
        if obj.parent.getRole() == pyatspi.ROLE_AUTOCOMPLETE:
            # This is the main difference between this class and the default
            # class - we'll give this thing a name here, and we'll make it
            # be the name of the autocomplete.
            #
            result.extend(self._getLabelOrName(obj.parent, **args))
        else:
            result.extend(speechgenerator.SpeechGenerator._getLabelOrName(
                self, obj, **args))
        return result

    def _getRoleName(self, obj, **args):
        """Prevents some roles from being spoken."""
        result = []
        role = args.get('role', obj.getRole())

        # Saying "menu item" for a combo box can confuse users. Therefore,
        # speak the combo box role instead.  Also, only do it if the menu
        # item is not focused (if the menu item is focused, it means we're
        # navigating in the combo box)
        #
        if not obj.getState().contains(pyatspi.STATE_FOCUSED):
            comboBox = self._script.getAncestor(obj,
                                                [pyatspi.ROLE_COMBO_BOX],
                                                [pyatspi.ROLE_DOCUMENT_FRAME])
            if comboBox:
                return self._getRoleName(comboBox, **args)

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

        if not (role in doNotSpeak):
            if role == pyatspi.ROLE_HEADING:
                level = self._script.getHeadingLevel(obj)
                if level:
                    # Translators: the %(level)d is in reference to a heading
                    # level in HTML (e.g., For <h3>, the level is 3)
                    # and the %(role)s is in reference to a previously
                    # translated rolename for the heading.
                    #
                    result.append(_("%(role)s level %(level)d") % {
                        'role': rolenames.getSpeechForRoleName(obj, role),
                        'level': level})
                else:
                    result.append(rolenames.getSpeechForRoleName(obj, role))
            else:
                result.append(rolenames.getSpeechForRoleName(obj, role))

        # If this is a link with a child which is an image, we want
        # to indicate that.
        #
        if role == pyatspi.ROLE_LINK \
           and obj.childCount and obj[0].getRole() == pyatspi.ROLE_IMAGE:
            result.extend(self._getRoleName(obj[0], **args))

        return result

    def getRoleName(self, obj):
        return self._getRoleName(obj)

    def _getExpandedEOCs(self, obj, **args):
        """Returns the expanded embedded object characters for an object."""
        result = []
        text = self._script.expandEOCs(obj)
        if text:
            result.append(text)
        return result

    def _getNumberOfChildren(self, obj, **args):
        result = []
        role = args.get('role', obj.getRole())
        if role == pyatspi.ROLE_LIST:
            # Translators: this represents a list in HTML.
            #
            result.append(ngettext("List with %d item",
                                   "List with %d items",
                                   obj.childCount) % obj.childCount)
        else:
            result.extend(speechgenerator.SpeechGenerator._getNumberOfChildren(
                self, obj, **args))
        return result

    def _getFocusedItem(self, obj, **args):
        result = []
        role = args.get('role', obj.getRole())
        if role == pyatspi.ROLE_LIST:
            item = None
            selection = obj.querySelection()
            for i in xrange(obj.childCount):
                if selection.isChildSelected(i):
                    item = obj[i]
                    break
            item = item or obj[0]
            if item:
                name = self._getName(item, **args)
                if name and name != self._getLabel(obj, **args):
                    result.extend(name)
        return result

    def _getAncestors(self, obj, **args):
        result = []
        priorObj = args.get('priorObj', None)
        commonAncestor = self._script.findCommonAncestor(priorObj, obj)

        if obj is commonAncestor:
            return result

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
            if self._script.isSameObject(parent, commonAncestor) \
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
            newResult = []
            if text and (text != label) and len(text.strip()) \
                and (not text.startswith("chrome://")):
                newResult.append(text)
            if label and len(label.strip()):
                newResult.append(label)

            # Finally add the role if it's not among the roles we don't
            # wish to speak.
            #
            if not (role in dontSpeakRoles) and len(newResult):
                result.append(rolenames.getSpeechForRoleName(parent))

            # If this object is an ARIA widget with STATE_REQUIRED, add
            # that. (Note that for the most part, the ARIA widget itself
            # has this state, but in the case of a group of radio buttons,
            # it is the group which has the state).
            #
            result.extend(self._getRequired(parent, **args))

            result.extend(newResult)

            parent = parent.parent

        result.reverse()

        return result

    def getSpeech(self, obj, **args):
        # ARIA widgets get treated like regular default widgets.
        #
        result = []
        args['isAria'] = self._script.isAriaWidget(obj)
        result = speechgenerator.SpeechGenerator.getSpeech(self, obj, **args)
        del args['isAria']
        return result
