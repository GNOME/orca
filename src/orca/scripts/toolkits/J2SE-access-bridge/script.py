# Orca
#
# Copyright 2006-2009 Sun Microsystems Inc.
# Copyright 2010 Joanmarie Diggs
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

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc., "  \
                "Copyright (c) 2010 Joanmarie Diggs"
__license__   = "LGPL"

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

import orca.scripts.default as default
import orca.input_event as input_event
import orca.orca as orca
import orca.orca_state as orca_state
from orca.ax_object import AXObject
from orca.ax_selection import AXSelection
from orca.ax_utilities import AXUtilities

from .script_utilities import Utilities
from .speech_generator import SpeechGenerator
from .formatting import Formatting

########################################################################
#                                                                      #
# The Java script class.                                               #
#                                                                      #
########################################################################

class Script(default.Script):

    def __init__(self, app):
        """Creates a new script for Java applications.

        Arguments:
        - app: the application to create a script for.
        """
        default.Script.__init__(self, app)

        # Some objects which issue descendant changed events lack
        # STATE_MANAGES_DESCENDANTS. As a result, onSelectionChanged
        # doesn't ignore these objects. That in turn causes Orca to
        # double-speak some items and/or set the locusOfFocus to a
        # parent it shouldn't. See bgo#616582. [[[TODO - JD: remove
        # this hack if and when we get a fix for that bug]]]
        # 
        self.lastDescendantChangedSource = None

    def getSpeechGenerator(self):
        """Returns the speech generator for this script."""
        return SpeechGenerator(self)

    def getFormatting(self):
        """Returns the formatting strings for this script."""
        return Formatting(self)

    def getUtilities(self):
        """Returns the utilities for this script."""
        return Utilities(self)

    def onCaretMoved(self, event):
        # Java's SpinButtons are the most caret movement happy thing
        # I've seen to date.  If you Up or Down on the keyboard to
        # change the value, they typically emit three caret movement
        # events, first to the beginning, then to the end, and then
        # back to the beginning.  It's a very excitable little widget.
        # Luckily, it only issues one value changed event.  So, we'll
        # ignore caret movement events caused by value changes and
        # just process the single value changed event.
        #
        isSpinBox = self.utilities.hasMatchingHierarchy(
            event.source, [Atspi.Role.TEXT,
                           Atspi.Role.PANEL,
                           Atspi.Role.SPIN_BUTTON])
        if isSpinBox:
            eventStr, mods = self.utilities.lastKeyAndModifiers()
            if eventStr in ["Up", "Down"] or isinstance(
               orca_state.lastInputEvent, input_event.MouseButtonEvent):
                return

        default.Script.onCaretMoved(self, event)

    def onSelectionChanged(self, event):
        """Called when an object's selection changes.

        Arguments:
        - event: the Event
        """

        # Avoid doing this with objects that manage their descendants
        # because they'll issue a descendant changed event. (Note: This
        # equality check is intentional; utilities.isSameObject() is
        # especially thorough with trees and tables, which is not
        # performant.
        #
        if event.source == self.lastDescendantChangedSource:
            return

        # We treat selected children as the locus of focus. When the
        # selection changes in a list we want to update the locus of
        # focus. If there is no selection, we default the locus of
        # focus to the containing object.
        #
        if (AXUtilities.is_list(event.source) \
           or AXUtilities.is_page_tab_list(event.source) \
           or AXUtilities.is_tree(event.source)) \
           and AXUtilities.is_focused(event.source):
            newFocus = AXSelection.get_selected_child(event.source, 0) or event.source
            orca.setLocusOfFocus(event, newFocus)
        else:
            default.Script.onSelectionChanged(self, event)

    def onFocusedChanged(self, event):
        """Callback for object:state-changed:focused accessibility events."""

        if not event.detail1:
            return

        # Accessibility support for menus in Java is badly broken: Missing
        # events, missing states, bogus events from other objects, etc.
        # Therefore if we get an event, however broken, for menus or their
        # their items that suggests they are selected, we'll just cross our
        # fingers and hope that's true.
        if AXUtilities.is_menu_related(event.source) \
           or AXUtilities.is_menu_related(AXObject.get_parent(event.source)):
            orca.setLocusOfFocus(event, event.source)
            return

        if AXUtilities.is_root_pane(event.source) \
           and AXUtilities.is_menu_related(orca_state.locusOfFocus):
            return

        default.Script.onFocusedChanged(self, event)

    def onValueChanged(self, event):
        """Called whenever an object's value changes.

        Arguments:
        - event: the Event
        """

        # We'll ignore value changed events for Java's toggle buttons since
        # they also send a redundant object:state-changed:checked event.
        if AXUtilities.is_toggle_button(event.source) \
           or AXUtilities.is_radio_button(event.source) \
           or AXUtilities.is_check_box(event.source):
            return

        # Java's SpinButtons are the most caret movement happy thing
        # I've seen to date.  If you Up or Down on the keyboard to
        # change the value, they typically emit three caret movement
        # events, first to the beginning, then to the end, and then
        # back to the beginning.  It's a very excitable little widget.
        # Luckily, it only issues one value changed event.  So, we'll
        # ignore caret movement events caused by value changes and
        # just process the single value changed event.
        #
        if AXUtilities.is_spin_button(event.source):
            parent = AXObject.get_parent(orca_state.locusOfFocus)
            grandparent = AXObject.get_parent(parent)
            if grandparent == event.source:
                self._presentTextAtNewCaretPosition(event, orca_state.locusOfFocus)
                return

        default.Script.onValueChanged(self, event)

    def skipObjectEvent(self, event):

        # Accessibility support for menus in Java is badly broken. One problem
        # is bogus focus claims following menu-related focus claims. Therefore
        # in this particular toolkit, we mustn't skip events for menus.
        if AXUtilities.is_menu_related(event.source):
            return False

        return default.Script.skipObjectEvent(self, event)
