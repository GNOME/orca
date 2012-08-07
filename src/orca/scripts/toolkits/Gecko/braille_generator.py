# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
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
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import pyatspi

import orca.braille_generator as braille_generator

from orca.orca_i18n import _ # for gettext support

########################################################################
#                                                                      #
# Custom BrailleGenerator                                              #
#                                                                      #
########################################################################

class BrailleGenerator(braille_generator.BrailleGenerator):
    """Provides a braille generator specific to Gecko.
    """

    def __init__(self, script):
        braille_generator.BrailleGenerator.__init__(self, script)

    def _generateInDocumentContent(self, obj, **args):
        """Returns True if this object is in HTML document content.
        """
        return self._script.inDocumentContent(obj)

    def _generateImageLink(self, obj, **args):
        """Returns the link (if any) for this image.
        """
        imageLink = None
        role = args.get('role', obj.getRole())
        if role == pyatspi.ROLE_IMAGE:
            imageLink = self._script.utilities.ancestorWithRole(
                obj, [pyatspi.ROLE_LINK], [pyatspi.ROLE_DOCUMENT_FRAME])
        return imageLink

    def _generateRoleName(self, obj, **args):
        """Prevents some roles from being spoken."""
        result = []
        role = args.get('role', obj.getRole())
        if not obj.getRole() in [pyatspi.ROLE_SECTION,
                                 pyatspi.ROLE_FORM,
                                 pyatspi.ROLE_UNKNOWN]:
            result.extend(braille_generator.BrailleGenerator._generateRoleName(
                self, obj, **args))
        return result

    def _generateName(self, obj, **args):
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
                        result = braille_generator.BrailleGenerator.\
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
        else:
            result.extend(braille_generator.BrailleGenerator._generateName(
                              self, obj, **args))
        if not result and role == pyatspi.ROLE_LIST_ITEM:
            result.append(self._script.utilities.expandEOCs(obj))

        link = None
        if role == pyatspi.ROLE_LINK:
            link = obj
        elif role == pyatspi.ROLE_IMAGE and not result:
            link = self._generateImageLink(obj, **args)
        if link and (not result or len(result[0].strip()) == 0):
            # If there's no text for the link, expose part of the
            # URI to the user.
            #
            basename = self._script.utilities.linkBasename(link)
            if basename:
                result.append(basename)

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
            result = braille_generator.BrailleGenerator.\
                           _generateDescription(self, obj, **args)
        return result

    def _generateLabel(self, obj, **args):
        result = braille_generator.BrailleGenerator._generateLabel(self,
                                                                   obj,
                                                                   **args)
        role = args.get('role', obj.getRole())
        # We'll attempt to guess the label under some circumstances.
        #
        # [[[TODO: WDW - ROLE_ENTRY is noticeably absent from here.  If
        # we include it here, the label_guess_bug_546815.py tests will
        # end up showing the label twice.  So, I've pulled the ROLE_ENTRY
        # out of here.  The effect of that is that we go back to the old
        # way where the entry will appear on the same line as the text.
        # I think there's a bug lurking there, though, in that the EOC for
        # the entry seems to still exist on the braille line.  This was
        # in the old (pre-refactor) code, too]]]
        #
        # [[[TODO: WDW - ROLE_COMBO_BOX, ROLE_PASSWORD, ROLE_CHECK_BOX
        # and ROLE_RADIO_BUTTON are absent for reasons similar to
        # ROLE_ENTRY.]]]
        #
        if not len(result) \
           and role in [pyatspi.ROLE_LIST,
                        pyatspi.ROLE_PARAGRAPH,
                        pyatspi.ROLE_TEXT] \
           and self._script.inDocumentContent(obj) \
           and not self._script.isAriaWidget(obj):
            label = self._script.guessTheLabel(obj)
            if label:
                result.append(label)

        # XUL combo boxes don't always have a label for/by
        # relationship.  But, they will make their names be
        # the string of the thing labelling them.
        #
        # And certain entries (e.g. in the Downloads window) lack a proper
        # label, instead prefering to display text within the entry which
        # is deleted when the widget gets focus. We want to treat this
        # pseudo label as the actual label.
        #
        if not len(result) \
           and role in [pyatspi.ROLE_COMBO_BOX, pyatspi.ROLE_ENTRY] \
           and not self._script.inDocumentContent(obj):
            result.append(obj.name)

        # If this is an autocomplete, and we'll make the label be the
        # name of the autocomplete.
        #
        if not len(result):
            parent = obj.parent
            if parent and parent.getRole() == pyatspi.ROLE_AUTOCOMPLETE:
                label = self._script.utilities.displayedLabel(parent)
                if not label or not len(label):
                    label = parent.name
                result.append(label)

        return result

    def _generateExpandedEOCs(self, obj, **args):
        """Returns the expanded embedded object characters for an object."""
        result = []
        text = self._script.utilities.expandEOCs(obj)
        if text:
            result.append(text)
        return result

    def generateBraille(self, obj, **args):
        result = []
        # ARIA widgets get treated like regular default widgets.
        #
        args['includeContext'] = not self._script.inDocumentContent(obj)
        args['useDefaultFormatting'] = \
            self._script.isAriaWidget(obj) \
            or ((obj.getRole() == pyatspi.ROLE_LIST) \
                and (not obj.getState().contains(pyatspi.STATE_FOCUSABLE)))

        oldRole = None
        if self._script.utilities.isEntry(obj):
            oldRole = self._overrideRole(pyatspi.ROLE_ENTRY, args)

        # Treat menu items in collapsed combo boxes as if the combo box
        # had focus. This will make things more consistent with how we
        # present combo boxes outside of Gecko.
        #
        if obj.getRole() == pyatspi.ROLE_MENU_ITEM:
            comboBox = self._script.utilities.ancestorWithRole(
                obj, [pyatspi.ROLE_COMBO_BOX], [pyatspi.ROLE_FRAME])
            if comboBox \
               and not comboBox.getState().contains(pyatspi.STATE_EXPANDED):
                obj = comboBox
        result.extend(braille_generator.BrailleGenerator.\
                          generateBraille(self, obj, **args))
        del args['includeContext']
        del args['useDefaultFormatting']
        if oldRole:
            self._restoreRole(oldRole, args)
        return result
