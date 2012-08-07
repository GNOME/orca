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

"""Custom formatting for Gecko."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import copy

import pyatspi

import orca.formatting
import orca.settings

# pylint: disable-msg=C0301

########################################################################
#                                                                      #
# Formatting for things that are not ARIA widgets.  For things that    #
# are ARIA widgets, we use the default formatting (see the             #
# getFormat method).                                                   #
#                                                                      #
########################################################################
formatting = {
    'speech': {
        'suffix': {
            'focused': '[]',
            'unfocused': 'newNodeLevel + unselectedCell + ' + orca.formatting.TUTORIAL,
            'basicWhereAmI': orca.formatting.TUTORIAL + ' + description + liveRegionDescription',
            'detailedWhereAmI' : '[]'
            },
        'default': {
            'focused': '[]',
            'unfocused': 'labelAndName + allTextSelection + roleName + availability + ' + orca.formatting.MNEMONIC + ' + accelerator',
            'basicWhereAmI': 'labelAndName + roleName',
            'detailedWhereAmI' : 'pageSummary'
            },
        pyatspi.ROLE_ALERT: {
            'unfocused': 'expandedEOCs or (labelAndName + unrelatedLabels)'
            },
        pyatspi.ROLE_DIALOG: {
            'unfocused': 'expandedEOCs or (labelAndName + unrelatedLabels)'
            },
        pyatspi.ROLE_DOCUMENT_FRAME: {
            'unfocused': 'name + roleName'
            },
        # [[[TODO: JD - We should decide if we want to provide
        # information about the table dimensions, whether or not
        # this is a layout table versus a data table, etc.  For now,
        # however, if it's in HTML content let's ignore it so that
        # SayAll by sentence works. :-) ]]]
        #
        pyatspi.ROLE_TABLE: {
            'unfocused': '[]'
            },
    },
    'braille': {
        # [[[TODO: WDW - we're doing very little here.  The goal for
        # autocomplete boxes at the moment is that their children (e.g.,
        # a text area, a menu, etc., do all the interactive work and
        # the autocomplete acts as more of a container.]]]
        #
        pyatspi.ROLE_AUTOCOMPLETE: {
            'unfocused': '[Component(obj, asString(roleName))]'
        },
        pyatspi.ROLE_CHECK_BOX: {
            'unfocused': '[Component(obj,\
                                     asString((not inDocumentContent\
                                               and (label + displayedText)\
                                               or (label and [""] or name))\
                                              + roleName),\
                                     indicator=asString(checkedState))]'
        },
        pyatspi.ROLE_COMBO_BOX: {
            'unfocused': '[Component(obj,\
                                     asString(label + name + roleName),\
                                     asString(label) and (len(asString(label)) + 1) or 0)]'
            },
        pyatspi.ROLE_IMAGE: {
            'unfocused':  '(imageLink\
                           and [Link(obj, (asString(label + displayedText)\
                                           or asString(name))\
                                          + " " + asString(value + roleName))]\
                           or [Component(obj,\
                                        asString(label + displayedText + value + roleName))])'
        },
        # [[[TODO: WDW - yikes!  We need more parameters to send to
        # the Link constructor.]]]
        #
        pyatspi.ROLE_LINK: {
            'unfocused': '[Link(obj, asString(currentLineText)\
                                     or asString(displayedText)\
                                     or asString(name))]',
        },
        # If we're in document content, we present the indicator followed
        # immediately by the role, followed by the label/displayed text,
        # etc. The label/displayed text is obtained as part of the line
        # contents, therefore we do not want to include it here.
        #
        pyatspi.ROLE_RADIO_BUTTON: {
            'unfocused': '[Component(obj,\
                                     asString((not inDocumentContent\
                                               and ((label + displayedText) or description)\
                                               or [""])\
                                             + roleName),\
                                   indicator=asString(radioState))]'
        }
    }
}

class Formatting(orca.formatting.Formatting):

    # pylint: disable-msg=W0142

    def __init__(self, script):
        orca.formatting.Formatting.__init__(self, script)
        self.update(copy.deepcopy(formatting))
        # This is a copy of the default formatting, which we will
        # use for ARIA widgets.
        #
        self._defaultFormatting = orca.formatting.Formatting(script)

    def getFormat(self, **args):
        # ARIA widgets get treated like regular default widgets.
        #
        if args.get('useDefaultFormatting', False):
            return self._defaultFormatting.getFormat(**args)
        else:
            return orca.formatting.Formatting.getFormat(self, **args)
