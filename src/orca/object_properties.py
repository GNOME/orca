# Orca
#
# Copyright 2004-2009 Sun Microsystems Inc.
# Copyright 2010-2013 The Orca Team
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

"""Propeerties of accessible objects. These have been put in their own module
so that we can present them in the correct language when users change the
language on the fly without having to reload a bunch of modules."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2004-2009 Sun Microsystems Inc." \
                "Copyright (c) 2010-2013 The Orca Team"
__license__   = "LGPL"

from .orca_i18n import _, C_

# Translators: The 'h' in this string represents a heading level attribute for
# content that you might find in something such as HTML content (e.g., <h1>).
# The translated form is meant to be a single character followed by a numeric
# heading level, where the single character is to indicate 'heading'.
ROLE_HEADING_LEVEL_BRAILLE = _("h%d")

# Translators: The %(level)d is in reference to a heading level in HTML (e.g.,
# For <h3>, the level is 3) and the %(role)s is in reference to a previously
# translated rolename for the heading.
ROLE_HEADING_LEVEL_SPEECH = _("%(role)s level %(level)d")

# Translators: This is an alternative name for the parent object of a series
# of icons.
ROLE_ICON_PANEL = _("Icon panel")

# Translators: This is a state which applies to the orientation of widgets
# such as sliders and scroll bars.
STATE_HORIZONTAL = _("horizontal")

# Translators: This is a state which applies to the orientation of widgets
# such as sliders and scroll bars.
STATE_VERTICAL =  _("vertical")

# Translators: This is a state which applies to a check box.
STATE_CHECKED = _("checked")

# Translators: This is a state which applies to a check box.
STATE_NOT_CHECKED = _("not checked")

# Translators: This is a state which applies to a check box.
STATE_PARTIALLY_CHECKED = _("partially checked")

# Translators: This is a state which applies to a toggle button.
STATE_PRESSED = _("pressed")

# Translators: This is a state which applies to a toggle button.
STATE_NOT_PRESSED = _("not pressed")

# Translators: This is a state which applies to a radio button.
STATE_SELECTED_RADIO_BUTTON = C_("radiobutton", "selected")

# Translators: This is a state which applies to a radio button.
STATE_UNSELECTED_RADIO_BUTTON = C_("radiobutton", "not selected")

# Translators: This is a state which applies to a table cell.
STATE_UNSELECTED_TABLE_CELL = C_("tablecell", "not selected")

# Translators: This is a state which applies to a link.
STATE_VISITED = C_("link state", "visited")

# Translators: This is a state which applies to a link.
STATE_UNVISITED = C_("link state", "unvisited")
