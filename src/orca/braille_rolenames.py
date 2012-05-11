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

"""Dictionary of abbreviated rolenames for use with braille."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2012 Igalia, S.L."
__license__   = "LGPL"

import pyatspi

from .orca_i18n import _
from .orca_i18n import C_

shortRoleNames = {
    # Translators: short braille for the rolename of an invalid GUI object.
    # We strive to keep it under three characters to preserve real estate.
    pyatspi.ROLE_INVALID: _("???"),

    # Translators: short braille for the rolename of an alert dialog.
    # NOTE for all the short braille words: they we strive to keep them
    # around three characters to preserve real estate on the braille
    # display.  The letters are chosen to make them unique across all
    # other rolenames, and they typically act like an abbreviation.
    pyatspi.ROLE_ALERT: _("alrt"),

    # Translators: short braille for the rolename of an animation widget.
    pyatspi.ROLE_ANIMATION: _("anim"),

    # Translators: short braille for the rolename of an arrow widget.
    pyatspi.ROLE_ARROW: _("arw"),

    # Translators: short braille for the rolename of a calendar widget.
    pyatspi.ROLE_CALENDAR: _("cal"),

    # Translators: short braille for the rolename of a canvas widget.
    pyatspi.ROLE_CANVAS: _("cnv"),

    # Translators: short braille for the rolename of a caption (e.g.,
    # table caption).
    pyatspi.ROLE_CAPTION: _("cptn"),

    # Translators: short braille for the rolename of a checkbox.
    pyatspi.ROLE_CHECK_BOX: _("chk"),

    # Translators: short braille for the rolename of a check menu item.
    pyatspi.ROLE_CHECK_MENU_ITEM: _("chk"),

    # Translators: short braille for the rolename of a color chooser.
    pyatspi.ROLE_COLOR_CHOOSER: _("clrchsr"),

    # Translators: short braille for the rolename of a column header.
    pyatspi.ROLE_COLUMN_HEADER: _("colhdr"),

    # Translators: short braille for the rolename of a combo box.
    pyatspi.ROLE_COMBO_BOX: _("cbo"),

    # Translators: short braille for the rolename of a date editor.
    pyatspi.ROLE_DATE_EDITOR: _("dat"),

    # Translators: short braille for the rolename of a desktop icon.
    pyatspi.ROLE_DESKTOP_ICON: _("icn"),

    # Translators: short braille for the rolename of a desktop frame.
    pyatspi.ROLE_DESKTOP_FRAME: _("frm"),

    # Translators: short braille for the rolename of a dial.
    # You should attempt to treat it as an abbreviation of
    # the translated word for "dial".  It is OK to use an
    # unabbreviated word as long as it is relatively short.
    pyatspi.ROLE_DIAL: C_("shortbraille", "dial"),

    # Translators: short braille for the rolename of a dialog.
    pyatspi.ROLE_DIALOG: _("dlg"),

    # Translators: short braille for the rolename of a directory pane.
    pyatspi.ROLE_DIRECTORY_PANE: _("dip"),

    # Translators: short braille for the rolename of an HTML document frame.
    pyatspi.ROLE_DOCUMENT_FRAME: _("html"),

    # Translators: short braille for the rolename of a drawing area.
    pyatspi.ROLE_DRAWING_AREA: _("draw"),

    # Translators: short braille for the rolename of a file chooser.
    pyatspi.ROLE_FILE_CHOOSER: _("fchsr"),

    # Translators: short braille for the rolename of a filler.
    pyatspi.ROLE_FILLER: _("flr"),

    # Translators: short braille for the rolename of a font chooser.
    pyatspi.ROLE_FONT_CHOOSER: _("fnt"),

    # Translators: short braille for the rolename of a form.
    # You should attempt to treat it as an abbreviation of
    # the translated word for "form".  It is OK to use an
    # unabbreviated word as long as it is relatively short.
    pyatspi.ROLE_FORM: C_("shortbraille", "form"),

    # Translators: short braille for the rolename of a frame.
    pyatspi.ROLE_FRAME: _("frm"),

    # Translators: short braille for the rolename of a glass pane.
    pyatspi.ROLE_GLASS_PANE: _("gpn"),

    # Translators: short braille for the rolename of a heading.
    pyatspi.ROLE_HEADING: _("hdng"),

    # Translators: short braille for the rolename of an html container.
    pyatspi.ROLE_HTML_CONTAINER: _("html"),

    # Translators: short braille for the rolename of a icon.
    pyatspi.ROLE_ICON: _("icn"),

    # Translators: short braille for the rolename of a image.
    pyatspi.ROLE_IMAGE: _("img"),

    # Translators: short braille for the rolename of an internal frame.
    pyatspi.ROLE_INTERNAL_FRAME: _("ifrm"),

    # Translators: short braille for the rolename of a label.
    pyatspi.ROLE_LABEL: _("lbl"),

    # Translators: short braille for the rolename of a layered pane.
    pyatspi.ROLE_LAYERED_PANE: _("lyrdpn"),

    # Translators: short braille for the rolename of a link.
    pyatspi.ROLE_LINK: _("lnk"),

    # Translators: short braille for the rolename of a list.
    pyatspi.ROLE_LIST: _("lst"),

    # Translators: short braille for the rolename of a list item.
    pyatspi.ROLE_LIST_ITEM: _("lstitm"),

    # Translators: short braille for the rolename of a menu.
    pyatspi.ROLE_MENU: _("mnu"),

    # Translators: short braille for the rolename of a menu bar.
    pyatspi.ROLE_MENU_BAR: _("mnubr"),

    # Translators: short braille for the rolename of a menu item.
    pyatspi.ROLE_MENU_ITEM: _("mnuitm"),

    # Translators: short braille for the rolename of an option pane.
    pyatspi.ROLE_OPTION_PANE: _("optnpn"),

    # Translators: short braille for the rolename of a page tab.
    pyatspi.ROLE_PAGE_TAB: _("pgt"),

    # Translators: short braille for the rolename of a page tab list.
    pyatspi.ROLE_PAGE_TAB_LIST: _("tblst"),

    # Translators: short braille for the rolename of a panel.
    pyatspi.ROLE_PANEL: _("pnl"),

    # Translators: short braille for the rolename of a password field.
    pyatspi.ROLE_PASSWORD_TEXT: _("pwd"),

    # Translators: short braille for the rolename of a popup menu.
    pyatspi.ROLE_POPUP_MENU: _("popmnu"),

    # Translators: short braille for the rolename of a progress bar.
    pyatspi.ROLE_PROGRESS_BAR: _("pgbar"),

    # Translators: short braille for the rolename of a push button.
    pyatspi.ROLE_PUSH_BUTTON: _("btn"),

    # Translators: short braille for the rolename of a radio button.
    pyatspi.ROLE_RADIO_BUTTON: _("radio"),

    # Translators: short braille for the rolename of a radio menu item.
    pyatspi.ROLE_RADIO_MENU_ITEM: _("rdmnuitm"),

    # Translators: short braille for the rolename of a root pane.
    pyatspi.ROLE_ROOT_PANE: _("rtpn"),

    # Translators: short braille for the rolename of a row header.
    pyatspi.ROLE_ROW_HEADER: _("rwhdr"),

    # Translators: short braille for the rolename of a scroll bar.
    pyatspi.ROLE_SCROLL_BAR: _("scbr"),

    # Translators: short braille for the rolename of a scroll pane.
    pyatspi.ROLE_SCROLL_PANE: _("scpn"),

    # Translators: short braille for the rolename of a section (e.g., in html).
    pyatspi.ROLE_SECTION: _("sctn"),

    # Translators: short braille for the rolename of a separator.
    pyatspi.ROLE_SEPARATOR: _("seprtr"),

    # Translators: short braille for the rolename of a slider.
    pyatspi.ROLE_SLIDER: _("sldr"),

    # Translators: short braille for the rolename of a split pane.
    pyatspi.ROLE_SPLIT_PANE: _("spltpn"),

    # Translators: short braille for the rolename of a spin button.
    pyatspi.ROLE_SPIN_BUTTON: _("spin"),

    # Translators: short braille for the rolename of a statusbar.
    pyatspi.ROLE_STATUS_BAR: _("statbr"),

    # Translators: short braille for the rolename of a table.
    pyatspi.ROLE_TABLE: _("tbl"),

    # Translators: short braille for the rolename of a table cell.
    pyatspi.ROLE_TABLE_CELL: _("cll"),

    # Translators: short braille for the rolename of a table column header.
    pyatspi.ROLE_TABLE_COLUMN_HEADER: _("colhdr"),

    # Translators: short braille for the rolename of a table row header.
    pyatspi.ROLE_TABLE_ROW_HEADER: _("rwhdr"),

    # Translators: short braille for the rolename of a tear off menu item.
    pyatspi.ROLE_TEAROFF_MENU_ITEM: _("tomnuitm"),

    # Translators: short braille for the rolename of a terminal.
    pyatspi.ROLE_TERMINAL: _("term"),

    # Translators: short braille for the rolename of a text entry field.
    pyatspi.ROLE_TEXT: _("txt"),

    # Translators: short braille for the rolename of a toggle button.
    pyatspi.ROLE_TOGGLE_BUTTON: _("tglbtn"),

    # Translators: short braille for the rolename of a toolbar.
    pyatspi.ROLE_TOOL_BAR: _("tbar"),

    # Translators: short braille for the rolename of a tooltip.
    pyatspi.ROLE_TOOL_TIP: _("tip"),

    # Translators: short braille for the rolename of a tree.
    pyatspi.ROLE_TREE: _("tre"),

    # Translators: short braille for the rolename of a tree table.
    pyatspi.ROLE_TREE_TABLE: _("trtbl"),

    # Translators: short braille for when the rolename of an object is unknown.
    pyatspi.ROLE_UNKNOWN: _("unk"),

    # Translators: short braille for the rolename of a viewport.
    pyatspi.ROLE_VIEWPORT: _("vwprt"),

    # Translators: short braille for the rolename of a window.
    pyatspi.ROLE_WINDOW: _("wnd"),

    # Translators: short braille for the rolename of a header.
    pyatspi.ROLE_HEADER: _("hdr"),

    # Translators: short braille for the rolename of a footer.
    pyatspi.ROLE_FOOTER: _("ftr"),

    # Translators: short braille for the rolename of a paragraph.
    pyatspi.ROLE_PARAGRAPH: _("para"),

    # Translators: short braille for the rolename of a application.
    pyatspi.ROLE_APPLICATION: _("app"),

    # Translators: short braille for the rolename of a autocomplete.
    pyatspi.ROLE_AUTOCOMPLETE: _("auto"),

    # Translators: short braille for the rolename of an editbar.
    pyatspi.ROLE_EDITBAR: _("edtbr"),

    # Translators: short braille for the rolename of an embedded component.
    pyatspi.ROLE_EMBEDDED: _("emb")
}
