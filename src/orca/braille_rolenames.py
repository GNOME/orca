# Orca
#
# Copyright 2012 Igalia, S.L.
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

# pylint: disable=wrong-import-position

"""Dictionary of abbreviated rolenames for use with braille."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2012 Igalia, S.L."
__license__   = "LGPL"

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from .orca_i18n import _, C_ # pylint: disable=import-error

shortRoleNames = {
    # Translators: short braille for the rolename of an invalid GUI object.
    # We strive to keep it under three characters to preserve real estate.
    Atspi.Role.INVALID: _("???"),

    # Translators: short braille for the rolename of an alert dialog.
    # NOTE for all the short braille words: they we strive to keep them
    # around three characters to preserve real estate on the braille
    # display.  The letters are chosen to make them unique across all
    # other rolenames, and they typically act like an abbreviation.
    Atspi.Role.ALERT: _("alrt"),

    # Translators: short braille for the rolename of an animation widget.
    Atspi.Role.ANIMATION: _("anim"),

    # Translators: short braille for the rolename of an arrow widget.
    Atspi.Role.ARROW: _("arw"),

    # Translators: short braille for the rolename of a calendar widget.
    Atspi.Role.CALENDAR: _("cal"),

    # Translators: short braille for the rolename of a canvas widget.
    Atspi.Role.CANVAS: _("cnv"),

    # Translators: short braille for the rolename of a caption (e.g.,
    # table caption).
    Atspi.Role.CAPTION: _("cptn"),

    # Translators: short braille for the rolename of a checkbox.
    Atspi.Role.CHECK_BOX: _("chk"),

    # Translators: short braille for the rolename of a check menu item.
    Atspi.Role.CHECK_MENU_ITEM: _("chk"),

    # Translators: short braille for the rolename of a color chooser.
    Atspi.Role.COLOR_CHOOSER: _("clrchsr"),

    # Translators: short braille for the rolename of a column header.
    Atspi.Role.COLUMN_HEADER: _("colhdr"),

    # Translators: short braille for the rolename of a combo box.
    Atspi.Role.COMBO_BOX: _("cbo"),

    # Translators: short braille for the rolename of a date editor.
    Atspi.Role.DATE_EDITOR: _("dat"),

    # Translators: short braille for the rolename of a desktop icon.
    Atspi.Role.DESKTOP_ICON: _("icn"),

    # Translators: short braille for the rolename of a desktop frame.
    Atspi.Role.DESKTOP_FRAME: _("frm"),

    # Translators: short braille for the rolename of a dial.
    # You should attempt to treat it as an abbreviation of
    # the translated word for "dial".  It is OK to use an
    # unabbreviated word as long as it is relatively short.
    Atspi.Role.DIAL: C_("shortbraille", "dial"),

    # Translators: short braille for the rolename of a dialog.
    Atspi.Role.DIALOG: _("dlg"),

    # Translators: short braille for the rolename of a directory pane.
    Atspi.Role.DIRECTORY_PANE: _("dip"),

    # Translators: short braille for the rolename of an HTML document frame.
    Atspi.Role.DOCUMENT_FRAME: _("html"),

    # Translators: short braille for the rolename of a drawing area.
    Atspi.Role.DRAWING_AREA: _("draw"),

    # Translators: short braille for the rolename of a file chooser.
    Atspi.Role.FILE_CHOOSER: _("fchsr"),

    # Translators: short braille for the rolename of a filler.
    Atspi.Role.FILLER: _("flr"),

    # Translators: short braille for the rolename of a font chooser.
    Atspi.Role.FONT_CHOOSER: _("fnt"),

    # Translators: short braille for the rolename of a form.
    # You should attempt to treat it as an abbreviation of
    # the translated word for "form".  It is OK to use an
    # unabbreviated word as long as it is relatively short.
    Atspi.Role.FORM: C_("shortbraille", "form"),

    # Translators: short braille for the rolename of a frame.
    Atspi.Role.FRAME: _("frm"),

    # Translators: short braille for the rolename of a glass pane.
    Atspi.Role.GLASS_PANE: _("gpn"),

    # Translators: short braille for the rolename of a heading.
    Atspi.Role.HEADING: _("hdng"),

    # Translators: short braille for the rolename of an html container.
    Atspi.Role.HTML_CONTAINER: _("html"),

    # Translators: short braille for the rolename of a icon.
    Atspi.Role.ICON: _("icn"),

    # Translators: short braille for the rolename of a image.
    Atspi.Role.IMAGE: _("img"),

    # Translators: short braille for the rolename of an internal frame.
    Atspi.Role.INTERNAL_FRAME: _("ifrm"),

    # Translators: short braille for the rolename of a label.
    Atspi.Role.LABEL: _("lbl"),

    # Translators: short braille for the rolename of a layered pane.
    Atspi.Role.LAYERED_PANE: _("lyrdpn"),

    # Translators: short braille for the rolename of a link.
    Atspi.Role.LINK: _("lnk"),

    # Translators: short braille for the rolename of a list.
    Atspi.Role.LIST: _("lst"),

    # Translators: short braille for the rolename of a list item.
    Atspi.Role.LIST_ITEM: _("lstitm"),

    # Translators: short braille for the rolename of a menu.
    Atspi.Role.MENU: _("mnu"),

    # Translators: short braille for the rolename of a menu bar.
    Atspi.Role.MENU_BAR: _("mnubr"),

    # Translators: short braille for the rolename of a menu item.
    Atspi.Role.MENU_ITEM: _("mnuitm"),

    # Translators: short braille for the rolename of an option pane.
    Atspi.Role.OPTION_PANE: _("optnpn"),

    # Translators: short braille for the rolename of a page tab.
    Atspi.Role.PAGE_TAB: _("pgt"),

    # Translators: short braille for the rolename of a page tab list.
    Atspi.Role.PAGE_TAB_LIST: _("tblst"),

    # Translators: short braille for the rolename of a panel.
    Atspi.Role.PANEL: _("pnl"),

    # Translators: short braille for the rolename of a password field.
    Atspi.Role.PASSWORD_TEXT: _("pwd"),

    # Translators: short braille for the rolename of a popup menu.
    Atspi.Role.POPUP_MENU: _("popmnu"),

    # Translators: short braille for the rolename of a progress bar.
    Atspi.Role.PROGRESS_BAR: _("pgbar"),

    # Translators: short braille for the rolename of a push button.
    Atspi.Role.BUTTON: _("btn"),

    # Translators: short braille for the rolename of a radio button.
    Atspi.Role.RADIO_BUTTON: _("radio"),

    # Translators: short braille for the rolename of a radio menu item.
    Atspi.Role.RADIO_MENU_ITEM: _("rdmnuitm"),

    # Translators: short braille for the rolename of a root pane.
    Atspi.Role.ROOT_PANE: _("rtpn"),

    # Translators: short braille for the rolename of a row header.
    Atspi.Role.ROW_HEADER: _("rwhdr"),

    # Translators: short braille for the rolename of a scroll bar.
    Atspi.Role.SCROLL_BAR: _("scbr"),

    # Translators: short braille for the rolename of a scroll pane.
    Atspi.Role.SCROLL_PANE: _("scpn"),

    # Translators: short braille for the rolename of a section (e.g., in html).
    Atspi.Role.SECTION: _("sctn"),

    # Translators: short braille for the rolename of a separator.
    Atspi.Role.SEPARATOR: _("seprtr"),

    # Translators: short braille for the rolename of a slider.
    Atspi.Role.SLIDER: _("sldr"),

    # Translators: short braille for the rolename of a split pane.
    Atspi.Role.SPLIT_PANE: _("spltpn"),

    # Translators: short braille for the rolename of a spin button.
    Atspi.Role.SPIN_BUTTON: _("spin"),

    # Translators: short braille for the rolename of a statusbar.
    Atspi.Role.STATUS_BAR: _("statbr"),

    # Translators: short braille for the rolename of a table.
    Atspi.Role.TABLE: _("tbl"),

    # Translators: short braille for the rolename of a table cell.
    Atspi.Role.TABLE_CELL: _("cll"),

    # Translators: short braille for the rolename of a table column header.
    Atspi.Role.TABLE_COLUMN_HEADER: _("colhdr"),

    # Translators: short braille for the rolename of a table row header.
    Atspi.Role.TABLE_ROW_HEADER: _("rwhdr"),

    # Translators: short braille for the rolename of a tear off menu item.
    Atspi.Role.TEAROFF_MENU_ITEM: _("tomnuitm"),

    # Translators: short braille for the rolename of a terminal.
    Atspi.Role.TERMINAL: _("term"),

    # Translators: short braille for the rolename of a text entry field.
    Atspi.Role.TEXT: _("txt"),

    # Translators: short braille for the rolename of a toggle button.
    Atspi.Role.TOGGLE_BUTTON: _("tglbtn"),

    # Translators: short braille for the rolename of a toolbar.
    Atspi.Role.TOOL_BAR: _("tbar"),

    # Translators: short braille for the rolename of a tooltip.
    Atspi.Role.TOOL_TIP: _("tip"),

    # Translators: short braille for the rolename of a tree.
    Atspi.Role.TREE: _("tre"),

    # Translators: short braille for the rolename of a tree table.
    Atspi.Role.TREE_TABLE: _("trtbl"),

    # Translators: short braille for when the rolename of an object is unknown.
    Atspi.Role.UNKNOWN: _("unk"),

    # Translators: short braille for the rolename of a viewport.
    Atspi.Role.VIEWPORT: _("vwprt"),

    # Translators: short braille for the rolename of a window.
    Atspi.Role.WINDOW: _("wnd"),

    # Translators: short braille for the rolename of a header.
    Atspi.Role.HEADER: _("hdr"),

    # Translators: short braille for the rolename of a footer.
    Atspi.Role.FOOTER: _("ftr"),

    # Translators: short braille for the rolename of a paragraph.
    Atspi.Role.PARAGRAPH: _("para"),

    # Translators: short braille for the rolename of a application.
    Atspi.Role.APPLICATION: _("app"),

    # Translators: short braille for the rolename of a autocomplete.
    Atspi.Role.AUTOCOMPLETE: _("auto"),

    # Translators: short braille for the rolename of an editbar.
    Atspi.Role.EDITBAR: _("edtbr"),

    # Translators: short braille for the rolename of an embedded component.
    Atspi.Role.EMBEDDED: _("emb")
}
