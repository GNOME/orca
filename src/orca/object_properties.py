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

# Translators: this is the action name for the 'toggle' action. It must be the
# same string used in the *.po file for gail.
ACTION_TOGGLE = _("toggle")

# Translators: this is a indication of the focused icon and the count of the
# total number of icons within an icon panel. An example of an icon panel is
# the Nautilus folder view.
ICON_INDEX_SPEECH = _("on %(index)d of %(total)d")

# Translators: this refers to the position of an item in a list or group of
# objects, such as menu items in a menu, radio buttons in a radio button group,
# combobox item in a combobox, etc.
GROUP_INDEX_SPEECH = _("%(index)d of %(total)d")

# Translators: This message describes a list item in a document. Nesting level
# is how "deep" the item is (e.g., a level of 2 represents a list item inside a
# list that's inside another list).
NESTING_LEVEL_SPEECH = _("Nesting level %d")

# Translators: This message describes a list item in a document. Nesting level
# is how "deep" the item is (e.g., a level of 2 represents a list item inside a
# list that's inside another list). This string is specifically for braille.
# Because braille displays lack real estate, we're using a shorter string than
# we use for speech.
NESTING_LEVEL_BRAILLE = _("LEVEL %d")

# Translators: This represents the depth of a node in a TreeView (i.e. how many
# ancestors the node has). This is the spoken version.
NODE_LEVEL_SPEECH = _("tree level %d")

# Translators: This represents the depth of a node in a TreeView (i.e. how many
# ancestors the node has). This is the braille version.
NODE_LEVEL_BRAILLE = _("TREE LEVEL %d")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# The reason for including the editable state as part of the role is to make it
# possible for users to quickly identify combo boxes in which a value can be
# typed or arrowed to.
ROLE_EDITABLE_COMBO_BOX = _("editable combo box")

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

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# The "banner" role is defined in the ARIA specification as "A region that
# contains mostly site-oriented content, rather than page-specific content."
# See https://www.w3.org/TR/wai-aria-1.1/#banner
ROLE_LANDMARK_BANNER = C_("role", "banner")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# The "complementary" role is defined in the ARIA specification as "A supporting
# section of the document, designed to be complementary to the main content at a
# similar level in the DOM hierarchy, but remains meaningful when separated from
# the main content." See https://www.w3.org/TR/wai-aria-1.1/#complementary
ROLE_LANDMARK_COMPLEMENTARY = C_("role", "complementary content")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# The "contentinfo" role is defined in the ARIA specification as "A large
# perceivable region that contains information about the parent document.
# Examples of information included in this region of the page are copyrights and
# links to privacy statements." See https://www.w3.org/TR/wai-aria-1.1/#contentinfo
ROLE_LANDMARK_CONTENTINFO = C_("role", "information")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# The "main" role is defined in the ARIA specification as "The main content of
# a document." See https://www.w3.org/TR/wai-aria-1.1/#main
ROLE_LANDMARK_MAIN = C_("role", "main content")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# The "navigation" role is defined in the ARIA specification as "A collection of
# navigational elements (usually links) for navigating the document or related
# documents." See https://www.w3.org/TR/wai-aria-1.1/#navigation
ROLE_LANDMARK_NAVIGATION =  C_("role", "navigation")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# The "region" role is defined in the ARIA specification as "A perceivable
# section containing content that is relevant to a specific, author-specified
# purpose and sufficiently important that users will likely want to be able to
# navigate to the section easily and to have it listed in a summary of the page."
# See https://www.w3.org/TR/wai-aria-1.1/#region
ROLE_LANDMARK_REGION =  C_("role", "region")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# The "search" role is defined in the ARIA specification as "A landmark region
# that contains a collection of items and objects that, as a whole, combine to
# create a search facility." See https://www.w3.org/TR/wai-aria-1.1/#search
ROLE_LANDMARK_SEARCH = C_("role", "search")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# The reason for including the visited state as part of the role is to make it
# possible for users to quickly identify if the link is associated with content
# already read.
ROLE_VISITED_LINK = _("visited link")

# Translators: This is a state which applies to elements in document content
# which have an "onClick" action.
STATE_CLICKABLE = _("clickable")

# Translators: This is a state which applies to items which can be expanded
# or collapsed such as combo boxes and nodes/groups in a treeview. Collapsed
# means the item's children are not showing; expanded means they are.
STATE_COLLAPSED = _("collapsed")

# Translators: This is a state which applies to items which can be expanded
# or collapsed such as combo boxes and nodes/groups in a treeview. Collapsed
# means the item's children are not showing; expanded means they are.
STATE_EXPANDED = _("expanded")

# Translators: This is a state which applies to elements in document content
# which have a longdesc attribute. http://www.w3.org/TR/WCAG20-TECHS/H45.html
STATE_HAS_LONGDESC = _("has long description")

# Translators: This is a state which applies to the orientation of widgets
# such as sliders and scroll bars.
STATE_HORIZONTAL = _("horizontal")

# Translators: This is a state which applies to the orientation of widgets
# such as sliders and scroll bars.
STATE_VERTICAL =  _("vertical")

# Translators: This is a state which applies to a check box.
STATE_CHECKED = C_("checkbox", "checked")

# Translators: This is a state which applies to a check box.
STATE_NOT_CHECKED = C_("checkbox", "not checked")

# Translators: This is a state which applies to a check box.
STATE_PARTIALLY_CHECKED = C_("checkbox", "partially checked")

# Translators: This is a state which applies to a toggle button.
STATE_PRESSED = C_("togglebutton", "pressed")

# Translators: This is a state which applies to a toggle button.
STATE_NOT_PRESSED = C_("togglebutton", "not pressed")

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

# Translators: This state represents an item on the screen that has been set
# insensitive (or grayed out).
STATE_INSENSITIVE_SPEECH = _("grayed")

# Translators: This state represents an item on the screen that has been set
# insensitive (or grayed out).
STATE_INSENSITIVE_BRAILLE = _("grayed")

# Translators: Certain objects (such as form controls on web pages) can have
# STATE_EDITABLE set to inform the user that this field can be filled out.
# It is assumed that form fields will be editable; if they lack this state,
# we need to present that information to the user. This string is the spoken
# version.
STATE_READ_ONLY_SPEECH = C_("text", "read only")

# Translators: Certain objects (such as form controls on web pages) can have
# STATE_EDITABLE set to inform the user that this field can be filled out.
# It is assumed that form fields will be editable; if they lack this state,
# we need to present that information to the user. This string is the braille
# version. (Because braille displays have limited real estate, we abbreviate.)
STATE_READ_ONLY_BRAILLE =  C_("text", "rdonly")

# Translators: Certain objects (such as form controls on web pages) can have
# STATE_REQUIRED set to inform the user that this field must be filled out.
STATE_REQUIRED_SPEECH = _("required")

# Translators: Certain objects (such as form controls on web pages) can have
# STATE_REQUIRED set to inform the user that this field must be filled out.
STATE_REQUIRED_BRAILLE = _("required")

# Translators: "multi-select" refers to a web form list in which more than
# one item can be selected at a time.
STATE_MULTISELECT_SPEECH = _("multi-select")



# TODO: Look at why we're doing this as lists.

CHECK_BOX_INDICATORS_SPEECH = \
    [STATE_NOT_CHECKED, STATE_CHECKED, STATE_PARTIALLY_CHECKED]
EXPANSION_INDICATORS_SPEECH = \
    [STATE_COLLAPSED, STATE_EXPANDED]
RADIO_BUTTON_INDICATORS_SPEECH = \
    [STATE_UNSELECTED_RADIO_BUTTON, STATE_SELECTED_RADIO_BUTTON]
TOGGLE_BUTTON_INDICATORS_SPEECH = \
    [STATE_NOT_PRESSED, STATE_PRESSED]

CHECK_BOX_INDICATORS_BRAILLE     = ["< >", "<x>", "<->"]
EXPANSION_INDICATORS_BRAILLE     = [STATE_COLLAPSED, STATE_EXPANDED]
RADIO_BUTTON_INDICATORS_BRAILLE  = ["& y", "&=y"]
TOGGLE_BUTTON_INDICATORS_BRAILLE = ["& y", "&=y"]

TABLE_CELL_DELIMITER_BRAILLE = " "
EOL_INDICATOR_BRAILLE = " $l"

CHECK_BOX_INDICATORS_SOUND = ["not_checked", "checked", "partially_checked"]
EXPANSION_INDICATORS_SOUND = ["collapsed", "expanded"]
RADIO_BUTTON_INDICATORS_SOUND = ["unselected", "selected"]
TOGGLE_BUTTON_INDICATORS_SOUND = ["not_pressed", "pressed"]
STATE_CLICKABLE_SOUND = "clickable"
STATE_HAS_LONGDESC_SOUND = "haslongdesc"
STATE_INSENSITIVE_SOUND = "insensitive"
STATE_MULTISELECT_SOUND = "multiselect"
STATE_READ_ONLY_SOUND = "readonly"
STATE_REQUIRED_SOUND = "required"
STATE_VISITED_SOUND = "visited"
