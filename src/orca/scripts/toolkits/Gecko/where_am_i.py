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

import orca.debug as debug
import orca.orca_state as orca_state
import orca.settings as settings
import orca.speech as speech
import orca.where_am_I as where_am_I

from orca.orca_i18n import _
from orca.orca_i18n import ngettext # for ngettext support

########################################################################
#                                                                      #
# Custom WhereAmI                                                      #
#                                                                      #
######################################################################## 

class GeckoWhereAmI(where_am_I.WhereAmI):
    def __init__(self, script):
        """Gecko specific WhereAmI that will be used to speak information
        about the current object of interest and will provide additional Gecko
        specific information.
        """
        where_am_I.WhereAmI.__init__(self, script)
        self._script = script
        
    def whereAmI(self, obj, basicOnly):
        """Calls the base class method for basic information and Gecko
        specific presentation methods for detailed/custom information.
        """
        if basicOnly or not self._script.inDocumentContent(obj):
            where_am_I.WhereAmI.whereAmI(self, obj, basicOnly)
            self._script.liveMngr.outputLiveRegionDescription(obj)
        else:
            if settings.useCollection:
                try:
                    self._collectionPageSummary()
                except:
                    debug.printException(debug.LEVEL_SEVERE)
                    self._iterativePageSummary(obj)
            else:
                self._iterativePageSummary(obj)

    def _speakDefaultButton(self, obj):
        """Speaks the default button in a dialog.

        Arguments:
        - obj: the dialog box for which the default button should be obtained
        """

        if not (self._script.inDocumentContent(orca_state.locusOfFocus) \
                and not self._script.isAriaWidget(orca_state.locusOfFocus)):
            where_am_I.WhereAmI._speakDefaultButton(self, obj)

    def _collectionPageSummary(self):
        """Uses the Collection interface to get the quantity of headings, 
        forms, tables, visited and unvisited links.
        """
        docframe = self._script.getDocumentFrame()
        col = docframe.queryCollection()
        # We will initialize these after the queryCollection() call in case
        # Collection is not supported
        headings = 0 
        forms = 0
        tables = 0
        vlinks = 0
        uvlinks = 0

        stateset = pyatspi.StateSet()
        roles = [pyatspi.ROLE_HEADING, pyatspi.ROLE_LINK, pyatspi.ROLE_TABLE,
                 pyatspi.ROLE_FORM]
        rule = col.createMatchRule(stateset.raw(), col.MATCH_NONE,  
                                   "", col.MATCH_NONE,
                                   roles, col.MATCH_ANY,
                                   "", col.MATCH_NONE,
                                   False)

        matches = col.getMatches(rule, col.SORT_ORDER_CANONICAL, 0, True)

        col.freeMatchRule(rule)
        for obj in matches:
            role = obj.getRole()
            if role == pyatspi.ROLE_HEADING:
                headings += 1
            elif role == pyatspi.ROLE_FORM:
                forms += 1
            elif role == pyatspi.ROLE_TABLE \
                      and not self._script.isLayoutOnly(obj):
                tables += 1
            elif role == pyatspi.ROLE_LINK:
                if obj.getState().contains(pyatspi.STATE_VISITED):
                    vlinks += 1
                else:
                    uvlinks += 1

        self._outputPageSummary(headings, forms, tables, vlinks, uvlinks, None)
            
    def _iterativePageSummary(self, obj):
        """Reads the quantity of headings, forms, tables, visited and 
        unvisited links.
        """
        headings = 0 
        forms = 0
        tables = 0
        vlinks = 0
        uvlinks = 0
        nodetotal = 0
        obj_index = None
        currentobj = obj

        # start at the first object after document frame
        obj = self._script.getDocumentFrame()[0]
        while obj:
            nodetotal += 1
            if obj == currentobj:
                obj_index = nodetotal
            role = obj.getRole()
            if role == pyatspi.ROLE_HEADING:
                headings += 1
            elif role == pyatspi.ROLE_FORM:
                forms += 1
            elif role == pyatspi.ROLE_TABLE \
                      and not self._script.isLayoutOnly(obj):
                tables += 1
            elif role == pyatspi.ROLE_LINK:
                if obj.getState().contains(pyatspi.STATE_VISITED):
                    vlinks += 1
                else:
                    uvlinks += 1

            obj = self._script.findNextObject(obj)

        # Calculate the percentage of the document that has been read.
        if obj_index:
            percentread = int(obj_index*100/nodetotal)
        else:
            percentread = None

        self._outputPageSummary(headings, forms, tables, 
                               vlinks, uvlinks, percentread)

    def _outputPageSummary(self, headings, forms, tables, 
                                 vlinks, uvlinks, percent):

        utterances = []
        if headings:
            # Translators: Announces the number of headings in the
            # web page that is currently being displayed.
            #
            utterances.append(ngettext \
                 ('%d heading', '%d headings', headings) %headings)
        if forms:
            # Translators: Announces the number of forms in the
            # web page that is currently being displayed.
            #
            utterances.append(ngettext \
                 ('%d form', '%d forms', forms) %forms)
        if tables:
            # Translators: Announces the number of non-layout tables in the
            # web page that is currently being displayed.
            #
            utterances.append(ngettext \
                 ('%d table', '%d tables', tables) %tables)
        if vlinks:
            # Translators: Announces the number of visited links in the
            # web page that is currently being displayed.
            #
            utterances.append(ngettext \
                 ('%d visited link', '%d visited links', vlinks) %vlinks)
        if uvlinks:
            # Translators: Announces the number of unvisited links in the
            # web page that is currently being displayed.
            #
            utterances.append(ngettext \
                 ('%d unvisited link', '%d unvisited links', uvlinks) %uvlinks)
        if percent is not None:
            # Translators: Announces the percentage of the document that has
            # been read.  This is calculated by knowing the index of the 
            # current position divided by the total number of objects on the 
            # page.
            # 
            utterances.append(_('%d percent of document read') %percent)

        speech.speakUtterances(utterances)  

