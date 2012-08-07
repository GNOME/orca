# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
# Copyright 2010 Orca Team.
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

"""Custom script for Gecko toolkit.
Please refer to the following URL for more information on the AT-SPI
implementation in Gecko:
http://developer.mozilla.org/en/docs/Accessibility/ATSPI_Support
"""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Orca Team."
__license__   = "LGPL"

import pyatspi

import orca.settings_manager as settings_manager
import orca.speech_generator as speech_generator
from orca.orca_i18n import _
from orca.orca_i18n import ngettext

_settingsManager = settings_manager.getManager()

########################################################################
#                                                                      #
# Custom SpeechGenerator                                               #
#                                                                      #
########################################################################

class SpeechGenerator(speech_generator.SpeechGenerator):
    """Provides a speech generator specific to Gecko.
    """

    # pylint: disable-msg=W0142

    def __init__(self, script):
        speech_generator.SpeechGenerator.__init__(self, script)

    def _generateName(self, obj, **args):
        result = []
        acss = self.voice(speech_generator.DEFAULT)
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
                        result = speech_generator.SpeechGenerator.\
                            _generateDisplayedText(self, obj, **args)
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
                if result:
                    result.extend(acss)

        else:
            result.extend(speech_generator.SpeechGenerator._generateName(
                              self, obj, **args))
        if not result and role == pyatspi.ROLE_LIST_ITEM:
            result.append(self._script.utilities.expandEOCs(obj))

        acss = self.voice(speech_generator.HYPERLINK)
        link = None
        if role == pyatspi.ROLE_LINK:
            link = obj
        elif role == pyatspi.ROLE_IMAGE and not result:
            link = self._script.utilities.ancestorWithRole(
                obj, [pyatspi.ROLE_LINK], [pyatspi.ROLE_DOCUMENT_FRAME])
        if link and (not result or len(result[0].strip()) == 0):
            # If there's no text for the link, expose part of the
            # URI to the user.
            #
            basename = self._script.utilities.linkBasename(link)
            if basename:
                result.append(basename)
                result.extend(acss)

        return result

    def _generateDescription(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the description of the object,
        if that description is different from that of the name and
        label.
        """
        if args.get('role', obj.getRole()) == pyatspi.ROLE_LINK \
           and obj.parent.getRole() == pyatspi.ROLE_IMAGE:
            result = self._generateName(obj, **args)
            # Translators: The following string is spoken to let the user
            # know that he/she is on a link within an image map. An image
            # map is an image/graphic which has been divided into regions.
            # Each region can be clicked on and has an associated link.
            # Please see http://en.wikipedia.org/wiki/Imagemap for more
            # information and examples.
            #
            result.append(_("image map link"))
        else:
            result = speech_generator.SpeechGenerator.\
                           _generateDescription(self, obj, **args)
        return result

    def _generateLabel(self, obj, **args):
        acss = self.voice(speech_generator.DEFAULT)
        result = speech_generator.SpeechGenerator._generateLabel(self,
                                                                 obj,
                                                                 **args)
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

        # XUL combo boxes don't always have a label for/by
        # relationship.  But, they will make their names be
        # the string of the thing labelling them.
        #
        if not len(result) \
           and role == pyatspi.ROLE_COMBO_BOX \
           and not self._script.inDocumentContent():
            result.append(obj.name)

        if result:
            result.extend(acss)
        return result

    def _generateLabelAndName(self, obj, **args):
        result = []
        role = args.get('role', obj.getRole())
        # For radio buttons, the label is handled as a context and we
        # assume we don't have to guess it.  If we need to guess it,
        # we need to add it to utterances.
        #
        if role == pyatspi.ROLE_RADIO_BUTTON \
           and self._script.utilities.displayedLabel(obj):
            pass
        else:
            result.extend(
                speech_generator.SpeechGenerator._generateLabelAndName(
                    self, obj, **args))
        return result

    def _generateLabelOrName(self, obj, **args):
        result = []
        if obj.parent.getRole() == pyatspi.ROLE_AUTOCOMPLETE:
            # This is the main difference between this class and the default
            # class - we'll give this thing a name here, and we'll make it
            # be the name of the autocomplete.
            #
            result.extend(self._generateLabelOrName(obj.parent, **args))
        else:
            result.extend(speech_generator.SpeechGenerator._generateLabelOrName(
                self, obj, **args))
        return result

    def _generateRoleName(self, obj, **args):
        """Prevents some roles from being spoken."""
        result = []
        acss = self.voice(speech_generator.SYSTEM)
        role = args.get('role', obj.getRole())
        force = args.get('force', False)

        # Saying "menu item" for a combo box can confuse users. Therefore,
        # speak the combo box role instead.  Also, only do it if the menu
        # item is not focused (if the menu item is focused, it means we're
        # navigating in the combo box)
        #
        if not obj.getState().contains(pyatspi.STATE_FOCUSED):
            comboBox = self._script.utilities.ancestorWithRole(
                obj, [pyatspi.ROLE_COMBO_BOX], [pyatspi.ROLE_DOCUMENT_FRAME])
            if comboBox:
                return self._generateRoleName(comboBox, **args)

        if not force:
            doNotSpeak = [pyatspi.ROLE_FORM,
                          pyatspi.ROLE_LABEL,
                          pyatspi.ROLE_MENU_ITEM,
                          pyatspi.ROLE_PARAGRAPH,
                          pyatspi.ROLE_SECTION,
                          pyatspi.ROLE_UNKNOWN]
        else:
            # We never ever want to speak 'unknown'
            #
            doNotSpeak = [pyatspi.ROLE_UNKNOWN]

        if not force and self._script.inDocumentContent(obj):
            doNotSpeak.append(pyatspi.ROLE_TABLE_CELL)
            if not self._script.isAriaWidget(obj) \
               and args.get('formatType', 'unfocused') != 'basicWhereAmI':
                doNotSpeak.append(pyatspi.ROLE_LIST_ITEM)
                doNotSpeak.append(pyatspi.ROLE_LIST)

        if not (role in doNotSpeak):
            if role == pyatspi.ROLE_IMAGE:
                link = self._script.utilities.ancestorWithRole(
                    obj, [pyatspi.ROLE_LINK], [pyatspi.ROLE_DOCUMENT_FRAME])
                if link:
                    result.append(self.getLocalizedRoleName(link))

            if role == pyatspi.ROLE_HEADING:
                level = self._script.getHeadingLevel(obj)
                if level:
                    # Translators: the %(level)d is in reference to a heading
                    # level in HTML (e.g., For <h3>, the level is 3)
                    # and the %(role)s is in reference to a previously
                    # translated rolename for the heading.
                    #
                    result.append(_("%(role)s level %(level)d") % {
                        'role': self.getLocalizedRoleName(obj, role),
                        'level': level})
                else:
                    result.append(self.getLocalizedRoleName(obj, role))
            else:
                result.append(self.getLocalizedRoleName(obj, role))

            if result:
                result.extend(acss)

            if role == pyatspi.ROLE_LINK \
               and obj.childCount and obj[0].getRole() == pyatspi.ROLE_IMAGE:
                # If this is a link with a child which is an image, we
                # want to indicate that.
                #
                acss = self.voice(speech_generator.HYPERLINK)
                result.append(self.getLocalizedRoleName(obj[0]))
                result.extend(acss)

        return result

    def _generateExpandedEOCs(self, obj, **args):
        """Returns the expanded embedded object characters for an object."""
        result = []
        text = self._script.utilities.expandEOCs(obj)
        if text:
            result.append(text)
        return result

    def _generateNumberOfChildren(self, obj, **args):
        if _settingsManager.getSetting('onlySpeakDisplayedText'):
            return []

        result = []
        acss = self.voice(speech_generator.SYSTEM)
        role = args.get('role', obj.getRole())
        if role == pyatspi.ROLE_LIST:
            # Translators: this represents a list in HTML.
            #
            result.append(ngettext("List with %d item",
                                   "List with %d items",
                                   obj.childCount) % obj.childCount)
            result.extend(acss)
        else:
            result.extend(
                speech_generator.SpeechGenerator._generateNumberOfChildren(
                    self, obj, **args))
        return result

    def _generateAncestors(self, obj, **args):
        result = []
        priorObj = args.get('priorObj', None)
        commonAncestor = self._script.utilities.commonAncestor(priorObj, obj)

        if obj is commonAncestor:
            return result

        # Skip items of unknown rolenames, menu bars, labels with
        # children, and autocompletes.  (With autocompletes, we
        # wind up speaking the text object). Beginning with Firefox
        # 3.2, list items have names corresponding with their text.
        # This results in displayedText returning actual text
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

        # [[[TODO - JD: Right now we're using this method to get the
        # full context of menu items in whereAmI. It seems to work for
        # gtk-demo, but here we're getting way too much context. So for
        # now, add in a check. Later, look for better way.]]]
        #
        if args.get('formatType', 'unfocused') == 'basicWhereAmI':
            stopRoles.append(pyatspi.ROLE_MENU_BAR)

        # There are some objects we want to include in the context,
        # but not add their rolenames.
        #
        dontSpeakRoles = [pyatspi.ROLE_TABLE_CELL,
                          pyatspi.ROLE_FILLER]

        parent = obj.parent
        while parent and (parent.parent != parent):
            role = parent.getRole()
            if self._script.utilities.isSameObject(parent, commonAncestor) \
               or role in stopRoles:
                break

            if role in skipRoles or self._script.utilities.isLayoutOnly(parent):
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
            # EMBEDDED_OBJECT_CHARACTER: displayedText will end up
            # coming back to the child of an object for the text if
            # an object's text contains a single EOC. In addition,
            # beginning with Firefox 3.2, a table cell may derive its
            # accessible name from focusable objects it contains (e.g.
            # links, form fields). displayedText will return the
            # object's name in this case (because of the presence of
            # the EOC and other characters). This causes us to be
            # chatty. So if it's a table cell which contains an EOC,
            # we will also skip the parent.
            #
            parentText = self._script.utilities.queryNonEmptyText(parent)
            if parentText:
                unicodeText = parentText.getText(0, -1).decode("UTF-8")
                if self._script.EMBEDDED_OBJECT_CHARACTER in unicodeText \
                   and (len(unicodeText) == 1 \
                        or role == pyatspi.ROLE_TABLE_CELL):
                    parent = parent.parent
                    continue

            # Put in the text and label (if they exist).
            #
            text = self._script.utilities.displayedText(parent)
            label = self._script.utilities.displayedLabel(parent)
            newResult = []
            acss = self.voice(speech_generator.DEFAULT)
            if text and (text != label) and len(text.strip()) \
                and (not text.startswith("chrome://")):
                newResult.extend(acss)
                newResult.append(text)
            if label and len(label.strip()):
                newResult.extend(acss)
                newResult.append(label)

            # Finally add the role if it's not among the roles we don't
            # wish to speak.
            #
            if not _settingsManager.getSetting('onlySpeakDisplayedText'):
                acss = self.voice(speech_generator.SYSTEM)
                if not (role in dontSpeakRoles) and len(newResult):
                    roleInfo = self.getLocalizedRoleName(parent)
                    if roleInfo:
                        result.extend(acss)
                        result.append(roleInfo)

            # If this object is an ARIA widget with STATE_REQUIRED, add
            # that. (Note that for the most part, the ARIA widget itself
            # has this state, but in the case of a group of radio buttons,
            # it is the group which has the state).
            #
            result.extend(self._generateRequired(parent, **args))

            result.extend(newResult)

            # [[[TODO - JD: Right now we're using this method to get the
            # full context of menu items in whereAmI. It seems to work for
            # gtk-demo, but here we're getting way too much context. So for
            # now, add in a check. Later, look for better way.]]]
            #
            if args.get('formatType', 'unfocused') == 'basicWhereAmI' \
               and parent.getRole() == pyatspi.ROLE_COMBO_BOX:
                break

            parent = parent.parent

        result.reverse()

        return result

    def _generateDefaultButton(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the default button in a dialog.
        This method should initially be called with a top-level window.
        """
        if self._script.inDocumentContent(obj) \
           and not self._script.isAriaWidget(obj):
            return []

        return speech_generator.SpeechGenerator.\
                     _generateDefaultButton(self, obj, **args)

    def _generateLiveRegionDescription(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the live region.
        """
        return self._script.liveMngr.\
                    generateLiveRegionDescription(obj, **args)

    def _generatePageSummary(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that summarize the objects found on the page
        containing obj.
        """
        result = []
        acss = self.voice(speech_generator.DEFAULT)
        headings, forms, tables, vlinks, uvlinks, percent = \
            self._script.getPageSummary(obj)
        if headings:
            # Translators: Announces the number of headings in the
            # web page that is currently being displayed.
            #
            result.append(ngettext \
                ('%d heading', '%d headings', headings) % headings)
        if forms:
            # Translators: Announces the number of forms in the
            # web page that is currently being displayed.
            #
            result.append(ngettext('%d form', '%d forms', forms) % forms)
        if tables:
            # Translators: Announces the number of non-layout tables in the
            # web page that is currently being displayed.
            #
            result.append(ngettext('%d table', '%d tables', tables) % tables)
        if vlinks:
            # Translators: Announces the number of visited links in the
            # web page that is currently being displayed.
            #
            result.append(ngettext \
                ('%d visited link', '%d visited links', vlinks) % vlinks)
        if uvlinks:
            # Translators: Announces the number of unvisited links in the
            # web page that is currently being displayed.
            #
            result.append(ngettext \
                ('%d unvisited link', '%d unvisited links', uvlinks) % uvlinks)
        if percent is not None:
            # Translators: Announces the percentage of the document that has
            # been read.  This is calculated by knowing the index of the
            # current position divided by the total number of objects on the
            # page.
            #
            result.append(ngettext \
                ('%d percent of document read',
                 '%d percent of document read',
                 percent) % percent)

        if result:
            result.extend(acss)
        return result

    def generateSpeech(self, obj, **args):
        result = []
        # Detailed WhereAmI should always be a page summary if we
        # are in document content.
        #
        if args.get('formatType', 'unfocused') == 'detailedWhereAmI' \
           and self._script.inDocumentContent(obj):
            oldRole = self._overrideRole('default', args)
            result.extend(speech_generator.SpeechGenerator.\
                                           generateSpeech(self, obj, **args))
            self._restoreRole(oldRole, args)
        elif self._script.utilities.isEntry(obj):
            oldRole = self._overrideRole(pyatspi.ROLE_ENTRY, args)
            result.extend(speech_generator.SpeechGenerator.\
                                           generateSpeech(self, obj, **args))
            self._restoreRole(oldRole, args)
        # ARIA widgets get treated like regular default widgets.
        #
        else:
            args['useDefaultFormatting'] = self._script.isAriaWidget(obj)
            result.extend(speech_generator.SpeechGenerator.\
                                           generateSpeech(self, obj, **args))
            del args['useDefaultFormatting']
        return result

    def getAttribute(self, obj, attributeName):
        attributes = obj.getAttributes()
        for attribute in attributes:
            if attribute.startswith(attributeName):
                return attribute.split(":")[1]

    def _generatePositionInList(self, obj, **args):
        position = self.getAttribute(obj, "posinset")
        total = self.getAttribute(obj, "setsize")
        if position and total and not obj.getRole() in \
                [pyatspi.ROLE_MENU_ITEM,
                 pyatspi.ROLE_TEAROFF_MENU_ITEM,
                 pyatspi.ROLE_CHECK_MENU_ITEM,
                 pyatspi.ROLE_RADIO_MENU_ITEM,
                 pyatspi.ROLE_MENU]:
            position = int(position)
            total = int(total)
            result = []
            if (_settingsManager.getSetting('enablePositionSpeaking') \
                or args.get('forceList', False)) \
                and position >= 0:
                result.append(self._script.formatting.getString(
                    mode='speech',
                    stringType='groupindex') \
                    % {"index" : position,
                    "total" : total})
                result.extend(self.voice(speech_generator.SYSTEM))
            return result
        else:
            return speech_generator.SpeechGenerator._generatePositionInList(
                self, obj, **args)
