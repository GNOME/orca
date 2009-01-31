# Orca
#
# Copyright 2004-2008 Sun Microsystems Inc.
# Copyright 2001, 2002 BAUM Retec, A.G.
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

"""Provides methods that convert the role name of an Accessible
object into localized strings for speech and braille."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2004-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import debug
import settings

import pyatspi

from orca_i18n import _  # for gettext support
from orca_i18n import C_ # to provide qualified translatable strings

########################################################################
#                                                                      #
# Rolenames derived from atk/atk/atkobject.c:role_items.               #
#                                                                      #
########################################################################

#[[[TODO: eitani - These are here for backward compatability, they should 
#disappear]]]

ROLE_INVALID             = "invalid"
ROLE_ACCEL_LABEL         = "accelerator label"
ROLE_ALERT               = "alert"
ROLE_ANIMATION           = "animation"
ROLE_ARROW               = "arrow"
ROLE_CALENDAR            = "calendar"
ROLE_CAPTION             = "caption"
ROLE_CANVAS              = "canvas"
ROLE_CHECK_BOX           = "check box"
ROLE_CHECK_MENU_ITEM     = "check menu item"
ROLE_COLOR_CHOOSER       = "color chooser"
ROLE_COLUMN_HEADER       = "column header"
ROLE_COMBO_BOX           = "combo box"
ROLE_DATE_EDITOR         = "dateeditor"
ROLE_DESKTOP_ICON        = "desktop icon"
ROLE_DESKTOP_FRAME       = "desktop frame"
ROLE_DIAL                = "dial"
ROLE_DIALOG              = "dialog"
ROLE_DIRECTORY_PANE      = "directory pane"
ROLE_DOCUMENT_FRAME      = "document frame"
ROLE_DRAWING_AREA        = "drawing area"
ROLE_ENTRY               = "entry"
ROLE_FILE_CHOOSER        = "file chooser"
ROLE_FILLER              = "filler"
ROLE_FONT_CHOOSER        = "fontchooser"
ROLE_FORM                = "form"
ROLE_FRAME               = "frame"
ROLE_GLASS_PANE          = "glass pane"
ROLE_HEADING             = "heading"
ROLE_HTML_CONTAINER      = "html container"
ROLE_ICON                = "icon"
ROLE_IMAGE               = "image"
ROLE_INTERNAL_FRAME      = "internal frame"
ROLE_INPUT_METHOD_WINDOW = "input method window"
ROLE_LABEL               = "label"
ROLE_LAYERED_PANE        = "layered pane"
ROLE_LINK                = "link"
ROLE_LIST                = "list"
ROLE_LIST_ITEM           = "list item"
ROLE_MENU                = "menu"
ROLE_MENU_BAR            = "menu bar"
ROLE_MENU_ITEM           = "menu item"
ROLE_OPTION_PANE         = "option pane"
ROLE_PAGE_TAB            = "page tab"
ROLE_PAGE_TAB_LIST       = "page tab list"
ROLE_PANEL               = "panel"
ROLE_PASSWORD_TEXT       = "password text"
ROLE_POPUP_MENU          = "popup menu"
ROLE_PROGRESS_BAR        = "progress bar"
ROLE_PUSH_BUTTON         = "push button"
ROLE_RADIO_BUTTON        = "radio button"
ROLE_RADIO_MENU_ITEM     = "radio menu item"
ROLE_ROOT_PANE           = "root pane"
ROLE_ROW_HEADER          = "row header"
ROLE_SCROLL_BAR          = "scroll bar"
ROLE_SCROLL_PANE         = "scroll pane"
ROLE_SECTION             = "section"
ROLE_SEPARATOR           = "separator"
ROLE_SLIDER              = "slider"
ROLE_SPLIT_PANE          = "split pane"
ROLE_SPIN_BOX            = "spinbox"
ROLE_SPIN_BUTTON         = "spin button"
ROLE_STATUSBAR           = "statusbar"
ROLE_TABLE               = "table"
ROLE_TABLE_CELL          = "table cell"
ROLE_TABLE_COLUMN_HEADER = "table column header"
ROLE_TABLE_ROW_HEADER    = "table row header"
ROLE_TEAR_OFF_MENU_ITEM  = "tear off menu item"
ROLE_TERMINAL            = "terminal"
ROLE_TEXT                = "text"
ROLE_TOGGLE_BUTTON       = "toggle button"
ROLE_TOOL_BAR            = "tool bar"
ROLE_TOOL_TIP            = "tool tip"
ROLE_TREE                = "tree"
ROLE_TREE_TABLE          = "tree table"
ROLE_UNKNOWN             = "unknown"
ROLE_VIEWPORT            = "viewport"
ROLE_WINDOW              = "window"
ROLE_HEADER              = "header"
ROLE_FOOTER              = "footer"
ROLE_PARAGRAPH           = "paragraph"
ROLE_APPLICATION         = "application"
ROLE_AUTOCOMPLETE        = "autocomplete"
ROLE_EDITBAR             = "edit bar"
ROLE_EMBEDDED            = "embedded component"

class Rolename:
    """Provides localized forms of rolenames for speech and Braille.
    """

    def __init__(self, rolename, brailleShort, brailleLong, speech):
        """Created a new rolename with the given parameters.

        Arguments:
        - rolename:     the internationalized (e.g., machine) name for the role
        - brailleShort: the localized short string for Braille display
        - brailleLong:  the localized long string for Braille display
        - speech:       the localized string to speak for speech
        """

        self.rolename = rolename
        self.brailleShort = brailleShort
        self.brailleLong = brailleLong
        self.speech = speech

# [[[TODO: WDW - the AT-SPI also has getLocalizedRoleName, which might a
# more appropriate thing to use, as it covers the situation where an app
# has developed a brand new component with a brand new role. Logged as
# buzilla bug 319780.]]]
#
rolenames = {}

rolenames[ROLE_INVALID] = Rolename(\
    ROLE_INVALID,
    # Translators: short braille for the rolename of an invalid GUI object.
    # We strive to keep it under three characters to preserve real estate.
    #
    _("???"),
    # Translators: long braille for the rolename of an invalid object.
    # We typically make these 'camel' case.
    #
    _("Invalid"),
    # Translators: spoken words for the rolename of an invalid object.
    #
    _("invalid"))

rolenames[ROLE_ACCEL_LABEL] = Rolename(
    ROLE_ACCEL_LABEL,
    # Translators: short braille for an accelerator (what you see in a menu).
    # We strive to keep it under three characters to preserve real estate.
    #
    _("acc"),
    # Translators: long braille for an accelerator (what you see in a menu).
    # We typically make these 'camel' case.
    #
    _("Accelerator"),
    # Translators: spoken words for an accelerator (what you see in a menu).
    #
    _("accelerator"))

rolenames[ROLE_ALERT] = Rolename(
    ROLE_ALERT,
    # Translators: short braille for the rolename of an alert dialog.
    # NOTE for all the short braille words: they we strive to keep them
    # around three characters to preserve real estate on the braille
    # display.  The letters are chosen to make them unique across all
    # other rolenames, and they typically act like an abbreviation.
    #
    _("alrt"),
    # Translators: long braille for the rolename of an alert dialog.
    # NOTE for all the long braille words: we typically make them
    # 'camel' case -- multiple words are bunched together with no
    # spaces between them and the first letter of each word is
    # capitalized.
    #
    _("Alert"),
    # Translators: spoken words for the rolename of an alert dialog.
    # NOTE for all the spoken words: these are the words one would use
    # when speaking.
    #
    _("alert"))

rolenames[ROLE_ANIMATION] = Rolename(
    ROLE_ANIMATION,
    # Translators: short braille for the rolename of an animation widget.
    #
    _("anim"),
    # Translators: long braille for the rolename of an animation widget.
    #
    _("Animation"),
    # Translators: spoken words for the rolename of an animation widget.
    #
    _("animation"))

rolenames[ROLE_ARROW] = Rolename(
    ROLE_ARROW,
    # Translators: short braille for the rolename of an arrow widget.
    #
    _("arw"),
    # Translators: long braille for the rolename of an animation widget.
    #
    _("Arrow"),
    # Translators: spoken words for the rolename of an animation widget.
    #
    _("arrow"))

rolenames[ROLE_CALENDAR] = Rolename(
    ROLE_CALENDAR,
    # Translators: short braille for the rolename of a calendar widget.
    #
    _("cal"),
    # Translators: long braille for the rolename of a calendar widget.
    #
    _("Calendar"),
    # Translators: spoken words for the rolename of a calendar widget.
    #
    _("calendar"))

rolenames[ROLE_CANVAS] = Rolename(
    ROLE_CANVAS,
    # Translators: short braille for the rolename of a canvas widget.
    #
    _("cnv"),
    # Translators: long braille for the rolename of a canvas widget.
    #
    _("Canvas"),
    # Translators: spoken words for the rolename of a canvas widget.
    #
    _("canvas"))

rolenames[ROLE_CAPTION] = Rolename(
    ROLE_CAPTION,
    # Translators: short braille for the rolename of a caption (e.g.,
    # table caption).
    #
    _("cptn"),
    # Translators: long braille for the rolename of a caption (e.g.,
    # table caption).
    #
    _("Caption"),
    # Translators: spoken words for the rolename of a caption (e.g.,
    # table caption).
    #
    _("caption"))

rolenames[ROLE_CHECK_BOX] = Rolename(
    ROLE_CHECK_BOX,
    # Translators: short braille for the rolename of a checkbox.
    #
    _("chk"),
    # Translators: long braille for the rolename of a checkbox.
    #
    _("CheckBox"),
    # Translators: spoken words for the rolename of a checkbox.
    #
    _("check box"))

rolenames[ROLE_CHECK_MENU_ITEM] = Rolename(
    ROLE_CHECK_MENU_ITEM,
    # Translators: short braille for the rolename of a check menu item.
    #
    _("chk"),
    # Translators: long braille for the rolename of a check menu item.
    #
    _("CheckItem"),
    # Translators: spoken words for the rolename of a check menu item.
    #
    _("check item"))

rolenames[ROLE_COLOR_CHOOSER] = Rolename(
    ROLE_COLOR_CHOOSER,
    # Translators: short braille for the rolename of a color chooser.
    #
    _("clrchsr"),
    # Translators: long braille for the rolename of a color chooser.
    #
    _("ColorChooser"),
    # Translators: spoken words for the rolename of a color chooser.
    #
    _("color chooser"))

rolenames[ROLE_COLUMN_HEADER] = Rolename(
    ROLE_COLUMN_HEADER,
    # Translators: short braille for the rolename of a column header.
    #
    _("colhdr"),
    # Translators: long braille for the rolename of a column header.
    #
    _("ColumnHeader"),
    # Translators: spoken words for the rolename of a column header.
    #
    _("column header"))

rolenames[ROLE_COMBO_BOX] = Rolename(
    ROLE_COMBO_BOX,
    # Translators: short braille for the rolename of a combo box.
    #
    _("cbo"),
    # Translators: long braille for the rolename of a combo box.
    #
    _("Combo"),
    # Translators: spoken words for the rolename of a combo box.
    #
    _("combo box"))

rolenames[ROLE_DATE_EDITOR] = Rolename(
    ROLE_DATE_EDITOR,
    # Translators: short braille for the rolename of a date editor.
    #
    _("dat"),
    # Translators: long braille for the rolename of a date editor.
    #
    _("DateEditor"),
    # Translators: spoken words for the rolename of a date editor.
    #
    _("date editor"))

rolenames[ROLE_DESKTOP_ICON] = Rolename(
    ROLE_DESKTOP_ICON,
    # Translators: short braille for the rolename of a desktop icon.
    #
    _("icn"),
    # Translators: long braille for the rolename of a desktop icon.
    #
    _("DesktopIcon"),
    # Translators: spoken words for the rolename of a desktop icon.
    #
    _("desktop icon"))

rolenames[ROLE_DESKTOP_FRAME] = Rolename(
    ROLE_DESKTOP_FRAME,
    # Translators: short braille for the rolename of a desktop frame.
    #
    _("frm"),
    # Translators: long braille for the rolename of a desktop frame.
    #
    _("DesktopFrame"),
    # Translators: spoken words for the rolename of a desktop frame.
    #
    _("desktop frame"))

rolenames[ROLE_DIAL] = Rolename(
    ROLE_DIAL,
    # Translators: short braille for the rolename of a dial.
    # You should attempt to treat it as an abbreviation of
    # the translated word for "dial".  It is OK to use an
    # unabbreviated word as long as it is relatively short.
    #
    C_("shortbraille", "dial"),
    # Translators: long braille for the rolename of a dial.
    #
    _("Dial"),
    # Translators: spoken words for the rolename of a dial.
    #
    _("dial"))

rolenames[ROLE_DIALOG] = Rolename(
    ROLE_DIALOG,
    # Translators: short braille for the rolename of a dialog.
    #
    _("dlg"),
    # Translators: long braille for the rolename of a dialog.
    #
    _("Dialog"),
    # Translators: spoken words for the rolename of a dialog.
    #
    _("dialog"))

rolenames[ROLE_DIRECTORY_PANE] = Rolename(
    ROLE_DIRECTORY_PANE,
    # Translators: short braille for the rolename of a directory pane.
    #
    _("dip"),
    # Translators: long braille for the rolename of a directory pane.
    #
    _("DirectoryPane"),
    # Translators: spoken words for the rolename of a directory pane.
    #
    _("directory pane"))

rolenames[ROLE_DOCUMENT_FRAME] = Rolename(
    ROLE_DOCUMENT_FRAME,
    # Translators: short braille for the rolename of an HTML document frame.
    #
    _("html"),
    # Translators: long braille for the rolename of an HTML document frame.
    #
    _("HtmlPane"),
    # Translators: spoken words for the rolename of an HTML document frame.
    #
    _("html content"))

rolenames[ROLE_DRAWING_AREA] = Rolename(
    ROLE_DRAWING_AREA,
    # Translators: short braille for the rolename of a drawing area.
    #
    _("draw"),
    # Translators: long braille for the rolename of a drawing area.
    #
    _("DrawingArea"),
    # Translators: spoken words for the rolename of a drawing area.
    #
    _("drawing area"))

rolenames[ROLE_FILE_CHOOSER] = Rolename(
    ROLE_FILE_CHOOSER,
    # Translators: short braille for the rolename of a file chooser.
    #
    _("fchsr"),
    # Translators: long braille for the rolename of a file chooser.
    #
    _("FileChooser"),
    # Translators: spoken words for the rolename of a file chooser.
    #
    _("file chooser"))

rolenames[ROLE_FILLER] = Rolename(
    ROLE_FILLER,
    # Translators: short braille for the rolename of a filler.
    #
    _("flr"),
    # Translators: long braille for the rolename of a filler.
    #
    _("Filler"),
    # Translators: spoken words for the rolename of a filler.
    #
    _("filler"))

rolenames[ROLE_FONT_CHOOSER] = Rolename(
    ROLE_FONT_CHOOSER,
    # Translators: short braille for the rolename of a font chooser.
    #
    _("fnt"),
    # Translators: long braille for the rolename of a font chooser.
    #
    _("FontChooser"),
    # Translators: spoken words for the rolename of a font chooser.
    #
    _("font chooser"))

rolenames[ROLE_FORM] = Rolename(
    ROLE_FORM,
    # Translators: short braille for the rolename of a form.
    # You should attempt to treat it as an abbreviation of
    # the translated word for "form".  It is OK to use an
    # unabbreviated word as long as it is relatively short.
    #
    C_("shortbraille", "form"),
    # Translators: long braille for the rolename of a form.
    #
    _("Form"),
    # Translators: spoken words for the rolename of a form.
    #
    _("form"))

rolenames[ROLE_FRAME] = Rolename(
    ROLE_FRAME,
    # Translators: short braille for the rolename of a frame.
    #
    _("frm"),
    # Translators: long braille for the rolename of a frame.
    #
    _("Frame"),
    # Translators: spoken words for the rolename of a frame.
    #
    _("frame"))

rolenames[ROLE_GLASS_PANE] = Rolename(
    ROLE_GLASS_PANE,
    # Translators: short braille for the rolename of a glass pane.
    #
    _("gpn"),
    # Translators: long braille for the rolename of a glass pane.
    #
    _("GlassPane"),
    # Translators: spoken words for the rolename of a glass pane.
    #
    _("glass pane"))

rolenames[ROLE_HEADING] = Rolename(
    ROLE_HEADING,
    # Translators: short braille for the rolename of a heading.
    #
    _("hdng"),
    # Translators: long braille for the rolename of a heading.
    #
    _("Heading"),
    # Translators: spoken words for the rolename of a heading.
    #
    _("heading"))

rolenames[ROLE_HTML_CONTAINER] = Rolename(
    ROLE_HTML_CONTAINER,
    # Translators: short braille for the rolename of an html container.
    #
    _("html"),
    # Translators: long braille for the rolename of an html container.
    #
    _("HtmlContainer"),
    # Translators: spoken words for the rolename of an html container.
    #
    _("h t m l container"))

rolenames[ROLE_ICON] = Rolename(
    ROLE_ICON,
    # Translators: short braille for the rolename of a icon.
    #
    _("icn"),
    # Translators: long braille for the rolename of a icon.
    #
    _("Icon"),
    # Translators: spoken words for the rolename of a icon.
    #
    _("icon"))

rolenames[ROLE_IMAGE] = Rolename(
    ROLE_IMAGE,
    # Translators: short braille for the rolename of a image.
    #
    _("img"),
    # Translators: long braille for the rolename of a image.
    #
    _("Image"),
    # Translators: spoken words for the rolename of a image.
    #
    _("image"))

rolenames[ROLE_INTERNAL_FRAME] = Rolename(
    ROLE_INTERNAL_FRAME,
    # Translators: short braille for the rolename of an internal frame.
    #
    _("ifrm"),
    # Translators: long braille for the rolename of an internal frame.
    #
    _("InternalFrame"),
    # Translators: spoken words for the rolename of an internal frame.
    #
    _("internal frame"))

rolenames[ROLE_LABEL] = Rolename(
    ROLE_LABEL,
    # Translators: short braille for the rolename of a label.
    #
    _("lbl"),
    # Translators: long braille for the rolename of a label.
    #
    _("Label"),
    # Translators: spoken words for the rolename of a label.
    #
    _("label"))

rolenames[ROLE_LAYERED_PANE] = Rolename(
    ROLE_LAYERED_PANE,
    # Translators: short braille for the rolename of a layered pane.
    #
    _("lyrdpn"),
    # Translators: long braille for the rolename of a layered pane.
    #
    _("LayeredPane"),
    # Translators: spoken words for the rolename of a layered pane.
    #
    _("layered pane"))

rolenames[ROLE_LINK] = Rolename(
    ROLE_LINK,
    # Translators: short braille for the rolename of a link.
    #
    _("lnk"),
    # Translators: long braille for the rolename of a link.
    #
    _("Link"),
    # Translators: spoken words for the rolename of a link.
    #
    _("link"))

rolenames[ROLE_LIST] = Rolename(
    ROLE_LIST,
    # Translators: short braille for the rolename of a list.
    #
    _("lst"),
    # Translators: long braille for the rolename of a list.
    #
    _("List"),
    # Translators: spoken words for the rolename of a list.
    #
    _("list"))

rolenames[ROLE_LIST_ITEM] = Rolename(
    ROLE_LIST_ITEM,
    # Translators: short braille for the rolename of a list item.
    #
    _("lstitm"),
    # Translators: long braille for the rolename of a list item.
    #
    _("ListItem"),
    # Translators: spoken words for the rolename of a list item.
    #
    _("list item"))

rolenames[ROLE_MENU] = Rolename(
    ROLE_MENU,
    # Translators: short braille for the rolename of a menu.
    #
    _("mnu"),
    # Translators: long braille for the rolename of a menu.
    #
    _("Menu"),
    # Translators: spoken words for the rolename of a menu.
    #
    _("menu"))

rolenames[ROLE_MENU_BAR] = Rolename(
    ROLE_MENU_BAR,
    # Translators: short braille for the rolename of a menu bar.
    #
    _("mnubr"),
    # Translators: long braille for the rolename of a menu bar.
    #
    _("MenuBar"),
    # Translators: spoken words for the rolename of a menu bar.
    #
    _("menu bar"))

rolenames[ROLE_MENU_ITEM] = Rolename(
    ROLE_MENU_ITEM,
    # Translators: short braille for the rolename of a menu item.
    #
    _("mnuitm"),
    # Translators: long braille for the rolename of a menu item.
    #
    _("MenuItem"),
    # Translators: spoken words for the rolename of a menu item.
    #
    _("menu item"))

rolenames[ROLE_OPTION_PANE] = Rolename(
    ROLE_OPTION_PANE,
    # Translators: short braille for the rolename of an option pane.
    #
    _("optnpn"),
    # Translators: long braille for the rolename of an option pane.
    #
    _("OptionPane"),
    # Translators: spoken words for the rolename of an option pane.
    #
    _("option pane"))

rolenames[ROLE_PAGE_TAB] = Rolename(
    ROLE_PAGE_TAB,
    # Translators: short braille for the rolename of a page tab.
    #
    _("pgt"),
    # Translators: long braille for the rolename of a page tab.
    #
    _("Page"),
    # Translators: spoken words for the rolename of a page tab.
    #
    _("page"))

rolenames[ROLE_PAGE_TAB_LIST] = Rolename(
    ROLE_PAGE_TAB_LIST,
    # Translators: short braille for the rolename of a page tab list.
    #
    _("tblst"),
    # Translators: long braille for the rolename of a page tab list.
    #
    _("TabList"),
    # Translators: spoken words for the rolename of a page tab list.
    #
    _("tab list"))

rolenames[ROLE_PANEL] = Rolename(
    ROLE_PANEL,
    # Translators: short braille for the rolename of a panel.
    #
    _("pnl"),
    # Translators: long braille for the rolename of a panel.
    #
    _("Panel"),
    # Translators: spoken words for the rolename of a panel.
    #
    _("panel"))

rolenames[ROLE_PASSWORD_TEXT] = Rolename(
    ROLE_PASSWORD_TEXT,
    # Translators: short braille for the rolename of a password field.
    #
    _("pwd"),
    # Translators: long braille for the rolename of a password field.
    #
    _("Password"),
    # Translators: spoken words for the rolename of a password field.
    #
    _("password"))

rolenames[ROLE_POPUP_MENU] = Rolename(
    ROLE_POPUP_MENU,
    # Translators: short braille for the rolename of a popup menu.
    #
    _("popmnu"),
    # Translators: long braille for the rolename of a popup menu.
    #
    _("PopupMenu"),
    # Translators: spoken words for the rolename of a popup menu.
    #
    _("popup menu"))

rolenames[ROLE_PROGRESS_BAR] = Rolename(
    ROLE_PROGRESS_BAR,
    # Translators: short braille for the rolename of a progress bar.
    #
    _("pgbar"),
    # Translators: long braille for the rolename of a progress bar.
    #
    _("Progress"),
    # Translators: spoken words for the rolename of a progress bar.
    #
    _("progress bar"))

rolenames[ROLE_PUSH_BUTTON] = Rolename(
    ROLE_PUSH_BUTTON,
    # Translators: short braille for the rolename of a push button.
    #
    _("btn"),
    # Translators: long braille for the rolename of a push button.
    #
    _("Button"),
    # Translators: spoken words for the rolename of a push button.
    #
    _("button"))

rolenames[ROLE_RADIO_BUTTON] = Rolename(
    ROLE_RADIO_BUTTON,
    # Translators: short braille for the rolename of a radio button.
    #
    _("radio"),
    # Translators: long braille for the rolename of a radio button.
    #
    _("RadioButton"),
    # Translators: spoken words for the rolename of a radio button.
    #
    _("radio button"))

rolenames[ROLE_RADIO_MENU_ITEM] = Rolename(
    ROLE_RADIO_MENU_ITEM,
    # Translators: short braille for the rolename of a radio menu item.
    #
    _("rdmnuitm"),
    # Translators: long braille for the rolename of a radio menu item.
    #
    _("RadioItem"),
    # Translators: spoken words for the rolename of a radio menu item.
    #
    _("radio menu item"))

rolenames[ROLE_ROOT_PANE] = Rolename(
    ROLE_ROOT_PANE,
    # Translators: short braille for the rolename of a root pane.
    #
    _("rtpn"),
    # Translators: long braille for the rolename of a root pane.
    #
    _("RootPane"),
    # Translators: spoken words for the rolename of a root pane.
    #
    _("root pane"))

rolenames[ROLE_ROW_HEADER] = Rolename(
    ROLE_ROW_HEADER,
    # Translators: short braille for the rolename of a row header.
    #
    _("rwhdr"),
    # Translators: long braille for the rolename of a row header.
    #
    _("RowHeader"),
    # Translators: spoken words for the rolename of a row header.
    #
    _("row header"))

rolenames[ROLE_SCROLL_BAR] = Rolename(
    ROLE_SCROLL_BAR,
    # Translators: short braille for the rolename of a scroll bar.
    #
    _("scbr"),
    # Translators: long braille for the rolename of a scroll bar.
    #
    _("ScrollBar"),
    # Translators: spoken words for the rolename of a scroll bar.
    #
    _("scroll bar"))

rolenames[ROLE_SCROLL_PANE] = Rolename(
    ROLE_SCROLL_PANE,
    # Translators: short braille for the rolename of a scroll pane.
    #
    _("scpn"),
    # Translators: long braille for the rolename of a scroll pane.
    #
    _("ScrollPane"),
    # Translators: spoken words for the rolename of a scroll pane.
    #
    _("scroll pane"))

rolenames[ROLE_SECTION] = Rolename(
    ROLE_SECTION,
    # Translators: short braille for the rolename of a section (e.g., in html).
    #
    _("sctn"),
    # Translators: long braille for the rolename of a section (e.g., in html).
    #
    _("Section"),
    # Translators: spoken words for the rolename of a section (e.g., in html).
    #
    _("section"))

rolenames[ROLE_SEPARATOR] = Rolename(
    ROLE_SEPARATOR,
    # Translators: short braille for the rolename of a separator.
    #
    _("seprtr"),
    # Translators: long braille for the rolename of a separator.
    #
    _("Separator"),
    # Translators: spoken words for the rolename of a separator.
    #
    _("separator"))

rolenames[ROLE_SLIDER] = Rolename(
    ROLE_SLIDER,
    # Translators: short braille for the rolename of a slider.
    #
    _("sldr"),
    # Translators: long braille for the rolename of a slider.
    #
    _("Slider"),
    # Translators: spoken words for the rolename of a slider.
    #
    _("slider"))

rolenames[ROLE_SPLIT_PANE] = Rolename(
    ROLE_SPLIT_PANE,
    # Translators: short braille for the rolename of a split pane.
    #
    _("spltpn"),
    # Translators: long braille for the rolename of a split pane.
    #
    _("SplitPane"),
    # Translators: spoken words for the rolename of a split pane.
    #
    _("split pane"))

rolenames[ROLE_SPIN_BUTTON] = Rolename(
    ROLE_SPIN_BUTTON,
    # Translators: short braille for the rolename of a spin button.
    #
    _("spin"),
    # Translators: long braille for the rolename of a spin button.
    #
    _("SpinButton"),
    # Translators: spoken words for the rolename of a spin button.
    #
    _("spin button"))

rolenames[ROLE_STATUSBAR] = Rolename(
    ROLE_STATUSBAR,
    # Translators: short braille for the rolename of a statusbar.
    #
    _("statbr"),
    # Translators: long braille for the rolename of a statusbar.
    #
    _("StatusBar"),
    # Translators: spoken words for the rolename of a statusbar.
    #
    _("status bar"))

rolenames[ROLE_TABLE] = Rolename(
    ROLE_TABLE,
    # Translators: short braille for the rolename of a table.
    #
    _("tbl"),
    # Translators: long braille for the rolename of a table.
    #
    _("Table"),
    # Translators: spoken words for the rolename of a table.
    #
    _("table"))

rolenames[ROLE_TABLE_CELL] = Rolename(
    ROLE_TABLE_CELL,
    # Translators: short braille for the rolename of a table cell.
    #
    _("cll"),
    # Translators: long braille for the rolename of a table cell.
    #
    _("Cell"),
    # Translators: spoken words for the rolename of a table cell.
    #
    _("cell"))

rolenames[ROLE_TABLE_COLUMN_HEADER] = Rolename(
    ROLE_TABLE_COLUMN_HEADER,
    # Translators: short braille for the rolename of a table column header.
    #
    _("colhdr"),
    # Translators: long braille for the rolename of a table column header.
    #
    _("ColumnHeader"),
    # Translators: spoken words for the rolename of a table column header.
    #
    _("column header"))

rolenames[ROLE_TABLE_ROW_HEADER] = Rolename(
    ROLE_TABLE_ROW_HEADER,
    # Translators: short braille for the rolename of a table row header.
    #
    _("rwhdr"),
    # Translators: long braille for the rolename of a table row header.
    #
    _("RowHeader"),
    # Translators: spoken words for the rolename of a table row header.
    #
    _("row header"))

rolenames[ROLE_TEAR_OFF_MENU_ITEM] = Rolename(
    ROLE_TEAR_OFF_MENU_ITEM,
    # Translators: short braille for the rolename of a tear off menu item.
    #
    _("tomnuitm"),
    # Translators: long braille for the rolename of a tear off menu item.
    #
    _("TearOffMenuItem"),
    # Translators: spoken words for the rolename of a tear off menu item.
    #
    _("tear off menu item"))

rolenames[ROLE_TERMINAL] = Rolename(
    ROLE_TERMINAL,
    # Translators: short braille for the rolename of a terminal.
    #
    _("term"),
    # Translators: long braille for the rolename of a terminal.
    #
    _("Terminal"),
    # Translators: spoken words for the rolename of a terminal.
    #
    _("terminal"))

rolenames[ROLE_TEXT] = Rolename(
    ROLE_TEXT,
    # Translators: short braille for the rolename of a text entry field.
    #
    _("txt"),
    # Translators: long braille for the rolename of a text entry field.
    #
    _("Text"),
    # Translators: spoken words for the rolename of a text entry field.
    #
    _("text"))

rolenames[ROLE_ENTRY] = rolenames[ROLE_TEXT]

rolenames[ROLE_TOGGLE_BUTTON] = Rolename(
    ROLE_TOGGLE_BUTTON,
    # Translators: short braille for the rolename of a toggle button.
    #
    _("tglbtn"),
    # Translators: long braille for the rolename of a toggle button.
    #
    _("ToggleButton"),
    # Translators: spoken words for the rolename of a toggle button.
    #
    _("toggle button"))

rolenames[ROLE_TOOL_BAR] = Rolename(
    ROLE_TOOL_BAR,
    # Translators: short braille for the rolename of a toolbar.
    #
    _("tbar"),
    # Translators: long braille for the rolename of a toolbar.
    #
    _("ToolBar"),
    # Translators: spoken words for the rolename of a toolbar.
    #
    _("tool bar"))

rolenames[ROLE_TOOL_TIP] = Rolename(
    ROLE_TOOL_TIP,
    # Translators: short braille for the rolename of a tooltip.
    #
    _("tip"),
    # Translators: long braille for the rolename of a tooltip.
    #
    _("ToolTip"),
    # Translators: spoken words for the rolename of a tooltip.
    #
    _("tool tip"))

rolenames[ROLE_TREE] = Rolename(
    ROLE_TREE,
    # Translators: short braille for the rolename of a tree.
    #
    _("tre"),
    # Translators: long braille for the rolename of a tree.
    #
    _("Tree"),
    # Translators: spoken words for the rolename of a tree.
    #
    _("tree"))

rolenames[ROLE_TREE_TABLE] = Rolename(
    ROLE_TREE_TABLE,
    # Translators: short braille for the rolename of a tree table.
    #
    _("trtbl"),
    # Translators: long braille for the rolename of a tree table.
    #
    _("TreeTable"),
    # Translators: spoken words for the rolename of a tree table.
    #
    _("tree table"))

rolenames[ROLE_UNKNOWN] = Rolename(
    ROLE_UNKNOWN,
    # Translators: short braille for when the rolename of an object is unknown.
    #
    _("unk"),
    # Translators: long braille for when the rolename of an object is unknown.
    #
    _("Unknown"),
    # Translators: spoken words for when the rolename of an object is unknown.
    #
    _("unknown"))

rolenames[ROLE_VIEWPORT] = Rolename(
    ROLE_VIEWPORT,
    # Translators: short braille for the rolename of a viewport.
    #
    _("vwprt"),
    # Translators: long braille for the rolename of a viewport.
    #
    _("Viewport"),
    # Translators: spoken words for the rolename of a viewport.
    #
    _("viewport"))

rolenames[ROLE_WINDOW] = Rolename(
    ROLE_WINDOW,
    # Translators: short braille for the rolename of a window.
    #
    _("wnd"),
    # Translators: long braille for the rolename of a window.
    #
    _("Window"),
    # Translators: spoken words for the rolename of a window.
    #
    _("window"))

rolenames[ROLE_HEADER] = Rolename(
    ROLE_HEADER,
    # Translators: short braille for the rolename of a header.
    #
    _("hdr"),
    # Translators: long braille for the rolename of a header.
    #
    _("Header"),
    # Translators: spoken words for the rolename of a header.
    #
    _("header"))

rolenames[ROLE_FOOTER] = Rolename(
    ROLE_FOOTER,
    # Translators: short braille for the rolename of a footer.
    #
    _("ftr"),
    # Translators: long braille for the rolename of a footer.
    #
    _("Footer"),
    # Translators: spoken words for the rolename of a footer.
    #
    _("footer"))

rolenames[ROLE_PARAGRAPH] = Rolename(
    ROLE_PARAGRAPH,
    # Translators: short braille for the rolename of a paragraph.
    #
    _("para"),
    # Translators: long braille for the rolename of a paragraph.
    #
    _("Paragraph"),
    # Translators: spoken words for the rolename of a paragraph.
    #
    _("paragraph"))

rolenames[ROLE_APPLICATION] = Rolename(
    ROLE_APPLICATION,
    # Translators: short braille for the rolename of a application.
    #
    _("app"),
    # Translators: long braille for the rolename of a application.
    #
    _("Application"),
    # Translators: spoken words for the rolename of a application.
    #
    _("application"))

rolenames[ROLE_AUTOCOMPLETE] = Rolename(
    ROLE_AUTOCOMPLETE,
    # Translators: short braille for the rolename of a autocomplete.
    #
    _("auto"),
    # Translators: long braille for the rolename of a autocomplete.
    #
    _("AutoComplete"),
    # Translators: spoken words for the rolename of a autocomplete.
    #
    _("autocomplete"))

rolenames[ROLE_EDITBAR] = Rolename(
    ROLE_EDITBAR,
    # Translators: short braille for the rolename of an editbar.
    #
    _("edtbr"),
    # Translators: long braille for the rolename of an editbar.
    #
    _("EditBar"),
    # Translators: spoken words for the rolename of an editbar.
    #
    _("edit bar"))

rolenames[ROLE_EMBEDDED] = Rolename(
    ROLE_EMBEDDED,
    # Translators: short braille for the rolename of an embedded component.
    #
    _("emb"),
    # Translators: long braille for the rolename of an embedded component.
    #
    _("EmbeddedComponent"),
    # Translators: spoken words for the rolename of an embedded component.
    #
    _("embedded component"))


# [[[TODO: eitani - This is for backward compatability, we now put in pyatspi 
# keys into the dictionary]]]

_legacy_rolename_keys = rolenames.keys()

for sym in dir(pyatspi):
    if sym.startswith('ROLE_'):
        possible_key = sym.replace('ROLE_','').replace('_','').lower()
        for key in _legacy_rolename_keys:
            if key.replace(' ','') == possible_key:
                pyatspi_role = getattr(pyatspi, sym)
                rolenames[pyatspi_role] = rolenames[key]

def _adjustRole(obj, role):
    """Adjust the role to what the role really is.
    """

    # Return fake "menu" role names.
    #
    if (role == pyatspi.ROLE_MENU_ITEM) \
          and (obj.childCount > 0):
        role = ROLE_MENU

    # If this is an ARIA button with the "haspopup:true" attribute, then
    # it's really a menu.
    #
    if role in [pyatspi.ROLE_PUSH_BUTTON, pyatspi.ROLE_MENU_ITEM]:
        attributes = obj.getAttributes()
        for attribute in attributes:
            if attribute.startswith("haspopup:true"):
                role = ROLE_MENU
                break

    return role

def getSpeechForRoleName(obj, role=None):
    """Returns the localized name of the given Accessible object; the name is
    suitable to be spoken.  If a localized name cannot be discovered, this
    will return the string as defined by the at-spi.

    Arguments:
    - obj: an Accessible object

    Returns a string containing the localized name of the object suitable
    to be spoken.
    """

    role = _adjustRole(obj, role or obj.getRole())

    # If the enum is not in the dictionary, check by name.
    role_entry = \
        rolenames.get(role) or rolenames.get(obj.getRoleName())
    if role_entry:
        return role_entry.speech
    else:
        debug.println(debug.LEVEL_WARNING, "No rolename for %s" % repr(role))
        localizedRoleName = obj.getLocalizedRoleName()
        if localizedRoleName and len(localizedRoleName):
            return localizedRoleName
        else:
            return repr(role)

def getShortBrailleForRoleName(obj, role=None):
    """Returns the localized name of the given Accessible object; the name is
    a short string suitable for a Braille display.  If a localized name cannot
    be discovered, this will return the string as defined by the at-spi.

    Arguments:
    - obj: an Accessible object

    Returns a short string containing the localized name of the object
    suitable for a Braille display.
    """

    role = _adjustRole(obj, role or obj.getRole())

    # If the enum is not in the dictionary, check by name.
    role_entry = \
        rolenames.get(role) or rolenames.get(obj.getRoleName())
    if role_entry:
        return role_entry.brailleShort
    else:
        debug.println(debug.LEVEL_WARNING, "No rolename for %s" % repr(role))
        localizedRoleName = obj.getLocalizedRoleName()
        if localizedRoleName and len(localizedRoleName):
            return localizedRoleName
        else:
            return repr(role)

def getLongBrailleForRoleName(obj, role=None):
    """Returns the localized name of the given Accessible object; the name is
    a long string suitable for a Braille display.  If a localized name cannot
    be discovered, this will return the string as defined by the at-spi.

    Arguments:
    - obj: an Accessible object

    Returns a string containing the localized name of the object suitable for
    a Braille display.
    """

    role = _adjustRole(obj, role or obj.getRole())

    # If the enum is not in the dictionary, check by name.
    role_entry = \
        rolenames.get(role) or rolenames.get(obj.getRoleName())
    if role_entry:
        return role_entry.brailleLong
    else:
        debug.println(debug.LEVEL_WARNING, "No rolename for %s" % repr(role))
        localizedRoleName = obj.getLocalizedRoleName()
        if localizedRoleName and len(localizedRoleName):
            return localizedRoleName
        else:
            return repr(role)

def getBrailleForRoleName(obj, role=None):
    """Returns the localized name of the given Accessible object; the name is
    a string suitable for a Braille display.  If a localized name cannot
    be discovered, this will return the string as defined by the at-spi.

    Arguments:
    - obj: an Accessible object

    Returns a string containing the localized name of the object suitable for
    a Braille display.  The actual string will depend upon the value of
    the 'brailleRolenameStyle' setting.
    """

    if settings.brailleRolenameStyle == settings.BRAILLE_ROLENAME_STYLE_SHORT:
        return getShortBrailleForRoleName(obj, role)
    else:
        return getLongBrailleForRoleName(obj, role)
