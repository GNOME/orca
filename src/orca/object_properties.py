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

from .orca_i18n import _, C_ # pylint: disable=import-error

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

# Translators: this refers to the position of an item in a list for which the
# size is unknown. Examples include unlimited scrolling news/article feeds
# on social media sites, and message lists on services such as gmail where
# you're currently viewing messages 1-100 out of some huge, unspecified
# number. Normally Orca announces both the position of the item and the
# total number (e.g. "3 of 5"). This is the corresponding message for the
# unknown-count scenario.
GROUP_INDEX_TOTAL_UNKNOWN_SPEECH = _("item %(index)d")

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

# Translators: In web content, authors can identify an element which contains
# detailed information about another element. For instance, for a password
# field, there may be a list of requirements (number of characters, number of
# special symbols, etc.). For an image, there may be an extended description
# before or after the image. Often there are visual clues connecting the
# detailed information to its related object. We need to convey this non-visually.
# This relationship will be presented for the object containing the details, e.g.
# when arrowing into or out of it. The string substitution is for the object to
# which the detailed information applies. For instance, when navigating into
# the details for an image named Pythagorean Theorem, Orca would present:
# "details for Pythagorean Theorem image".
# See https://w3c.github.io/aria/#aria-details
RELATION_DETAILS_FOR = _("details for %s")

# Translators: In web content, authors can identify an element which contains
# detailed information about another element. For instance, for a password
# field, there may be a list of requirements (number of characters, number of
# special symbols, etc.). For an image, there may be an extended description
# before or after the image. Often there are visual clues connecting the
# detailed information to its related object. We need to convey this non-visually.
# This relationship will be presented for the object which has details to tell
# the user the type of object where the details can be found so that they can
# more quickly navigate to it. The string substitution is for the object to
# which the detailed information applies. For instance, when navigating to
# a password field which has details in a list named "Requirements", Orca would
# present: "has details in Requirements list".
# See https://w3c.github.io/aria/#aria-details
RELATION_HAS_DETAILS = _("has details in %s")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# This role refers to a container with a proposed change. This change can
# include the insertion and/or deletion of content, and would typically be seen
# in a collaborative editor, such as in Google Docs.
ROLE_CONTENT_SUGGESTION = C_("role", "suggestion")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# The reason for including the editable state as part of the role is to make it
# possible for users to quickly identify combo boxes in which a value can be
# typed or arrowed to.
ROLE_EDITABLE_COMBO_BOX = _("editable combo box")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# This role is to describe elements in web content which have the contenteditable
# attribute set to true, indicating that the element can be edited by the user.
ROLE_EDITABLE_CONTENT = _("editable content")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# The feed role is a scrollable list of articles where scrolling may cause
# articles to be added to or removed from either end of the list.
# https://w3c.github.io/aria/#feed
ROLE_FEED = C_("role", "feed")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# The figure role is a perceivable section of content that typically contains a
# graphical document, images, code snippets, or example text.
# https://w3c.github.io/aria/#figure
ROLE_FIGURE = C_("role", "figure")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# This role refers to the abstract in a digitally-published document.
# https://w3c.github.io/dpub-aria/#doc-abstract
ROLE_ABSTRACT = C_("role", "abstract")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# This role refers to the acknowledgments in a digitally-published document.
# https://w3c.github.io/dpub-aria/#doc-acknowledgments
ROLE_ACKNOWLEDGMENTS = C_("role", "acknowledgments")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# This role refers to the afterword in a digitally-published document.
# https://w3c.github.io/dpub-aria/#doc-afterword
ROLE_AFTERWORD = C_("role", "afterword")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# This role refers to the appendix in a digitally-published document.
# https://w3c.github.io/dpub-aria/#doc-appendix
ROLE_APPENDIX = C_("role", "appendix")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# This role refers to a bibliography entry in a digitally-published document.
# https://w3c.github.io/dpub-aria/#doc-biblioentry
ROLE_BIBLIOENTRY = C_("role", "bibliography entry")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# This role refers to the bibliography in a digitally-published document.
# https://w3c.github.io/dpub-aria/#doc-bibliography
ROLE_BIBLIOGRAPHY = C_("role", "bibliography")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# This role refers to a chapter in a digitally-published document.
# https://w3c.github.io/dpub-aria/#doc-chapter
ROLE_CHAPTER = C_("role", "chapter")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# This role refers to the colophon in a digitally-published document.
# https://w3c.github.io/dpub-aria/#doc-colophon
ROLE_COLOPHON = C_("role", "colophon")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# This role refers to the conclusion in a digitally-published document.
# https://w3c.github.io/dpub-aria/#doc-conclusion
ROLE_CONCLUSION = C_("role", "conclusion")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# This role refers to the cover in a digitally-published document.
# https://w3c.github.io/dpub-aria/#doc-cover
ROLE_COVER = C_("role", "cover")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# This role refers to a single credit in a digitally-published document.
# https://w3c.github.io/dpub-aria/#doc-credit
ROLE_CREDIT = C_("role", "credit")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# This role refers to the credits in a digitally-published document.
# https://w3c.github.io/dpub-aria/#doc-credits
ROLE_CREDITS = C_("role", "credits")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# This role refers to the dedication in a digitally-published document.
# https://w3c.github.io/dpub-aria/#doc-dedication
ROLE_DEDICATION = C_("role", "dedication")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# This role refers to a single endnote in a digitally-published document.
# https://w3c.github.io/dpub-aria/#doc-endnote
ROLE_ENDNOTE = C_("role", "endnote")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# This role refers to the endnotes in a digitally-published document.
# https://w3c.github.io/dpub-aria/#doc-endnotes
ROLE_ENDNOTES = C_("role", "endnotes")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# This role refers to the epigraph in a digitally-published document.
# https://w3c.github.io/dpub-aria/#doc-epigraph
ROLE_EPIGRAPH = C_("role", "epigraph")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# This role refers to the epilogue in a digitally-published document.
# https://w3c.github.io/dpub-aria/#doc-epilogue
ROLE_EPILOGUE = C_("role", "epilogue")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# This role refers to the errata in a digitally-published document.
# https://w3c.github.io/dpub-aria/#doc-errata
ROLE_ERRATA = C_("role", "errata")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# This role refers to an example in a digitally-published document.
# https://w3c.github.io/dpub-aria/#doc-example
ROLE_EXAMPLE = C_("role", "example")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# This role refers to the foreword in a digitally-published document.
# https://w3c.github.io/dpub-aria/#doc-foreword
ROLE_FOREWORD = C_("role", "foreword")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# This role refers to the glossary in a digitally-published document.
# https://w3c.github.io/dpub-aria/#doc-glossary
ROLE_GLOSSARY = C_("role", "glossary")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# This role refers to the index in a digitally-published document.
# https://w3c.github.io/dpub-aria/#doc-index
ROLE_INDEX = C_("role", "index")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# This role refers to the introduction in a digitally-published document.
# https://w3c.github.io/dpub-aria/#doc-introduction
ROLE_INTRODUCTION = C_("role", "introduction")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# This role refers to a pagebreak in a digitally-published document.
# https://w3c.github.io/dpub-aria/#doc-pagebreak
ROLE_PAGEBREAK = C_("role", "page break")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# This role refers to a page list in a digitally-published document.
# https://w3c.github.io/dpub-aria/#doc-pagelist
ROLE_PAGELIST = C_("role", "page list")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# This role refers to a named part in a digitally-published document.
# https://w3c.github.io/dpub-aria/#doc-part
ROLE_PART = C_("role", "part")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# This role refers to the preface in a digitally-published document.
# https://w3c.github.io/dpub-aria/#doc-preface
ROLE_PREFACE = C_("role", "preface")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# This role refers to the prologue in a digitally-published document.
# https://w3c.github.io/dpub-aria/#doc-prologue
ROLE_PROLOGUE = C_("role", "prologue")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# This role refers to a pullquote in a digitally-published document.
# https://w3c.github.io/dpub-aria/#doc-pullquote
ROLE_PULLQUOTE = C_("role", "pullquote")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# This role refers to a questions-and-answers section in a digitally-published
# document. https://w3c.github.io/dpub-aria/#doc-qna
# In English, "QNA" is generally recognized by native speakers. If your language
# lacks the equivalent, please prefer the shortest phrase which clearly conveys
# the meaning.
ROLE_QNA = C_("role", "QNA")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# This role refers to the subtitle in a digitally-published document.
# https://w3c.github.io/dpub-aria/#doc-subtitle
ROLE_SUBTITLE = C_("role", "subtitle")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# This role refers to the table of contents in a digitally-published document.
# https://w3c.github.io/dpub-aria/#doc-toc
ROLE_TOC = C_("role", "table of contents")

# Translators: The 'h' in this string represents a heading level attribute for
# content that you might find in something such as HTML content (e.g., <h1>).
# The translated form is meant to be a single character followed by a numeric
# heading level, where the single character is to indicate 'heading'.
ROLE_HEADING_LEVEL_BRAILLE = _("h%d")

# Translators: The %(level)d is in reference to a heading level in HTML (e.g.,
# For <h3>, the level is 3) and the %(role)s is in reference to a previously
# translated rolename for the heading.
ROLE_HEADING_LEVEL_SPEECH = _("%(role)s %(level)d")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# The reason we include the orientation as part of the role is because in some
# applications and toolkits, it can dictate which keyboard keys should be used
# to modify the value of the widget.
ROLE_SCROLL_BAR_HORIZONTAL = _("horizontal scroll bar")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# The reason we include the orientation as part of the role is because in some
# applications and toolkits, it can dictate which keyboard keys should be used
# to modify the value of the widget.
ROLE_SCROLL_BAR_VERTICAL = _("vertical scroll bar")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# A slider is a widget which looks like a bar and displays a value as a range.
# A common example of a slider can be found in UI for modifying volume levels.
# The reason we include the orientation as part of the role is because in some
# applications and toolkits, it can dictate which keyboard keys should be used
# to modify the value of the widget.
ROLE_SLIDER_HORIZONTAL = _("horizontal slider")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# A slider is a widget which looks like a bar and displays a value as a range.
# A common example of a slider can be found in UI for modifying volume levels.
# The reason we include the orientation as part of the role is because in some
# applications and toolkits, it can dictate which keyboard keys should be used
# to modify the value of the widget.
ROLE_SLIDER_VERTICAL = _("vertical slider")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# A splitter is a bar that divides a container into two parts. It is often, but
# not necessarily, user resizable. A common example of a splitter can be found
# in email applications, where there is a container on the left which holds a
# list of all the mail folders and a container on the right which lists all of
# the messages in the selected folder. The bar which you click on and drag to
# resize these containers is the splitter. The reason we include the orientation
# as part of the role is because in some applications and toolkits, it can
# dictate which keyboard keys should be used to modify the value of the widget.
ROLE_SPLITTER_HORIZONTAL = _("horizontal splitter")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# A splitter is a bar that divides a container into two parts. It is often, but
# not necessarily, user resizable. A common example of a splitter can be found
# in email applications, where there is a container on the left which holds a
# list of all the mail folders and a container on the right which lists all of
# the messages in the selected folder. The bar which you click on and drag to
# resize these containers is the splitter. The reason we include the orientation
# as part of the role is because in some applications and toolkits, it can
# dictate which keyboard keys should be used to modify the value of the widget.
ROLE_SPLITTER_VERTICAL = _("vertical splitter")

# Translators: This string should be treated as a role describing an object.
# Examples of roles include "checkbox", "radio button", "paragraph", and "link."
# The "switch" role is a "light switch" style toggle, such as can be seen in
# https://developer.gnome.org/gtk3/stable/GtkSwitch.html
ROLE_SWITCH = C_("role", "switch")

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

# Translators: This string refers to a row or column whose sort-order has been set
# to ascending.
SORT_ORDER_ASCENDING = _("sorted ascending")

# Translators: This string refers to a row or column whose sort-order has been set
# to descending.
SORT_ORDER_DESCENDING = _("sorted descending")

# Translators: This string refers to a row or column whose sort-order has been set,
# but the nature of the sort order is unknown or something other than ascending or
# descending.
SORT_ORDER_OTHER = _("sorted")

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
# Please don't use the same translation as for "selected",
# or it will be impossible to differentiate a checkbox in a list-item.
STATE_CHECKED = C_("checkbox", "checked")

# Translators: This is a state which applies to a check box.
# Please don't use the same translation as for "not selected",
# or it will be impossible to differentiate a checkbox in a list-item.
STATE_NOT_CHECKED = C_("checkbox", "not checked")

# Translators: This is a state which applies to a switch. For an example of
# a switch, see https://developer.gnome.org/gtk3/stable/GtkSwitch.html
STATE_ON_SWITCH = C_("switch", "on")

# Translators: This is a state which applies to a switch. For an example of
# a switch, see https://developer.gnome.org/gtk3/stable/GtkSwitch.html
STATE_OFF_SWITCH = C_("switch", "off")

# Translators: This is a state which applies to a check box.
STATE_PARTIALLY_CHECKED = C_("checkbox", "partially checked")

# Translators: This is a state which applies to a toggle button.
STATE_PRESSED = C_("togglebutton", "pressed")

# Translators: This is a state which applies to a toggle button.
STATE_NOT_PRESSED = C_("togglebutton", "not pressed")

# Translators: This is a state which applies to an item or option
# in a selectable list.
STATE_UNSELECTED_LIST_ITEM = C_("listitem", "not selected")

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

# Translators: STATE_INVALID_ENTRY indicates that the associated object, such
# as a form field, has an error. The following string is spoken when all we
# know is that an error has occurred, but not the type of error.
STATE_INVALID_SPEECH = C_("error", "invalid entry")

# Translators: STATE_INVALID_ENTRY indicates that the associated object, such
# as a form field, has an error. The following string is displayed in braille
# when all we know is that an error has occurred, but not the type of error.
# We prefer a smaller string than in speech because braille displays have a
# limited size.
STATE_INVALID_BRAILLE = C_("error", "invalid")

# Translators: STATE_INVALID_ENTRY indicates that the associated object, such
# as a form field, has an error. The following string is spoken when the error
# is related to spelling.
STATE_INVALID_SPELLING_SPEECH = C_("error", "invalid spelling")

# Translators: STATE_INVALID_ENTRY indicates that the associated object, such
# as a form field, has an error. The following string is displayed in braille
# when the error is related to spelling. We prefer a smaller string than in
# speech because braille displays have a limited size.
STATE_INVALID_SPELLING_BRAILLE = C_("error", "spelling")

# Translators: STATE_INVALID_ENTRY indicates that the associated object, such
# as a form field, has an error. The following string is spoken when the error
# is related to grammar.
STATE_INVALID_GRAMMAR_SPEECH = C_("error", "invalid grammar")

# Translators: STATE_INVALID_ENTRY indicates that the associated object, such
# as a form field, has an error. The following string is displayed in braille
# when the error is related to grammar. We prefer a smaller string than in
# speech because braille displays have a limited size.
STATE_INVALID_GRAMMAR_BRAILLE = C_("error", "grammar")

# TODO: Look at why we're doing this as lists.

CHECK_BOX_INDICATORS_SPEECH = \
    [STATE_NOT_CHECKED, STATE_CHECKED, STATE_PARTIALLY_CHECKED]
EXPANSION_INDICATORS_SPEECH = \
    [STATE_COLLAPSED, STATE_EXPANDED]
INVALID_INDICATORS_SPEECH = \
    [STATE_INVALID_SPEECH,
     STATE_INVALID_SPELLING_SPEECH,
     STATE_INVALID_GRAMMAR_SPEECH]
RADIO_BUTTON_INDICATORS_SPEECH = \
    [STATE_UNSELECTED_RADIO_BUTTON, STATE_SELECTED_RADIO_BUTTON]

SWITCH_INDICATORS_SPEECH = [STATE_OFF_SWITCH, STATE_ON_SWITCH]
TOGGLE_BUTTON_INDICATORS_SPEECH = \
    [STATE_NOT_PRESSED, STATE_PRESSED]

CHECK_BOX_INDICATORS_BRAILLE     = ["< >", "<x>", "<->"]
EXPANSION_INDICATORS_BRAILLE     = [STATE_COLLAPSED, STATE_EXPANDED]
INVALID_INDICATORS_BRAILLE       = [STATE_INVALID_BRAILLE,
                                    STATE_INVALID_SPELLING_BRAILLE,
                                    STATE_INVALID_GRAMMAR_BRAILLE]
RADIO_BUTTON_INDICATORS_BRAILLE  = ["& y", "&=y"]
SWITCH_INDICATORS_BRAILLE = ["& y", "&=y"]
TOGGLE_BUTTON_INDICATORS_BRAILLE = ["& y", "&=y"]

TABLE_CELL_DELIMITER_BRAILLE = " "
EOL_INDICATOR_BRAILLE = " $l"

CHECK_BOX_INDICATORS_SOUND = ["not_checked", "checked", "partially_checked"]
EXPANSION_INDICATORS_SOUND = ["collapsed", "expanded"]
INVALID_INDICATORS_SOUND = ["invalid", "invalid_spelling", "invalid_grammar"]
RADIO_BUTTON_INDICATORS_SOUND = ["unselected", "selected"]
SWITCH_INDICATORS_SOUND = ["off", "on"]
TOGGLE_BUTTON_INDICATORS_SOUND = ["not_pressed", "pressed"]
STATE_CLICKABLE_SOUND = "clickable"
STATE_HAS_LONGDESC_SOUND = "haslongdesc"
STATE_INSENSITIVE_SOUND = "insensitive"
STATE_MULTISELECT_SOUND = "multiselect"
STATE_READ_ONLY_SOUND = "readonly"
STATE_REQUIRED_SOUND = "required"
STATE_VISITED_SOUND = "visited"
