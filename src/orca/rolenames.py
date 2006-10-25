# Orca
#
# Copyright 2004-2006 Sun Microsystems Inc.
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
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

"""Provides a methods that converts the role name of an Accessible
object into localized strings for speech and braille."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2006 Sun Microsystems Inc."
__license__   = "LGPL"

import debug
import settings

from orca_i18n import _ # for gettext support

########################################################################
#                                                                      #
# Rolenames derived from atk/atk/atkobject.c:role_items.               #
#                                                                      #
########################################################################

ROLE_INVALID             = "invalid"
ROLE_ACCEL_LABEL         = "accelerator label"
ROLE_ALERT               = "alert"
ROLE_ANIMATION           = "animation"
ROLE_ARROW               = "arrow"
ROLE_CALENDAR            = "calendar"
ROLE_CANVAS              = "canvas"
ROLE_CHECK_BOX           = "check box"
ROLE_CHECK_MENU_ITEM     = "check menu item"
ROLE_CHECK_MENU          = "check menu" # invented for items that are submenus
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
ROLE_RADIO_MENU          = "radio menu" # invented for items that are submenus
ROLE_ROOT_PANE           = "root pane"
ROLE_ROW_HEADER          = "row header"
ROLE_SCROLL_BAR          = "scroll bar"
ROLE_SCROLL_PANE         = "scroll pane"
ROLE_SECTION             = "section"
ROLE_SEPARATOR           = "separator"
ROLE_SLIDER              = "slider"
ROLE_SPLIT_PANE          = "split pane"
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

rolenames[ROLE_INVALID] = Rolename(ROLE_INVALID,
                                   _("???"),
                                   _("Invalid"),
                                   _("invalid"))

rolenames[ROLE_ACCEL_LABEL] = Rolename(ROLE_ACCEL_LABEL,
                                       _("acc"),
                                       _("Accelerator"),
                                       _("accelerator"))

rolenames[ROLE_ALERT] = Rolename(ROLE_ALERT,
                                 _("alert"),
                                 _("Alert"),
                                 _("alert"))

rolenames[ROLE_ANIMATION] = Rolename(ROLE_ANIMATION,
                                     _("Anim"),
                                     _("Animation"),
                                     _("animation"))

rolenames[ROLE_ARROW] = Rolename(ROLE_ARROW,
                                 _("arrow"),
                                 _("Arrow"),
                                 _("arrow"))

rolenames[ROLE_CALENDAR] = Rolename(ROLE_CALENDAR,
                                    _("cal"),
                                    _("Calendar"),
                                    _("calendar"))

rolenames[ROLE_CANVAS] = Rolename(ROLE_CANVAS,
                                  _("cnv"),
                                  _("Canvas"),
                                  _("canvas"))

rolenames[ROLE_CHECK_BOX] = Rolename(ROLE_CHECK_BOX,
                                     _("chk"),
                                     _("CheckBox"),
                                     _("check box"))

rolenames[ROLE_CHECK_MENU_ITEM] = Rolename(ROLE_CHECK_MENU_ITEM,
                                           _("chk"),
                                           _("CheckItem"),
                                           _("check item"))

rolenames[ROLE_CHECK_MENU] = Rolename(ROLE_CHECK_MENU,
                                      _("ckm"),
                                      _("CheckMenu"),
                                      _("check menu"))

rolenames[ROLE_COLOR_CHOOSER] = Rolename(ROLE_COLOR_CHOOSER,
                                         _("clrchsr"),
                                         _("ColorChooser"),
                                         _("color chooser"))

rolenames[ROLE_COLUMN_HEADER] = Rolename(ROLE_COLUMN_HEADER,
                                         _("colhdr"),
                                         _("ColumnHeader"),
                                         _("column header"))

rolenames[ROLE_COMBO_BOX] = Rolename(ROLE_COMBO_BOX,
                                     _("cbo"),
                                     _("Combo"),
                                     _("combo box"))

rolenames[ROLE_DATE_EDITOR] = Rolename(ROLE_DATE_EDITOR,
                                       _("dat"),
                                       _("DateEditor"),
                                       _("date editor"))

rolenames[ROLE_DESKTOP_ICON] = Rolename(ROLE_DESKTOP_ICON,
                                        _("icon"),
                                        _("DesktopIcon"),
                                        _("desktop icon"))

rolenames[ROLE_DESKTOP_FRAME] = Rolename(ROLE_DESKTOP_FRAME,
                                         _("frame"),
                                         _("DesktopFrame"),
                                         _("desktop frame"))

rolenames[ROLE_DIAL] = Rolename(ROLE_DIAL,
                                _("dial"),
                                _("Dial"),
                                _("dial"))

rolenames[ROLE_DIALOG] = Rolename(ROLE_DIALOG,
                                  _("dlg"),
                                  _("Dialog"),
                                  _("dialog"))

rolenames[ROLE_DIRECTORY_PANE] = Rolename(ROLE_DIRECTORY_PANE,
                                          _("dip"),
                                          _("DirectoryPane"),
                                          _("directory pane"))

rolenames[ROLE_DRAWING_AREA] = Rolename(ROLE_DRAWING_AREA,
                                        _("draw"),
                                        _("DrawingArea"),
                                        _("drawing area"))

rolenames[ROLE_FILE_CHOOSER] = Rolename(ROLE_FILE_CHOOSER,
                                        _("fchsr"),
                                        _("FileChooser"),
                                        _("file chooser"))

rolenames[ROLE_FILLER] = Rolename(ROLE_FILLER,
                                  _("flr"),
                                  _("Filler"),
                                  _("filler"))

rolenames[ROLE_FONT_CHOOSER] = Rolename(ROLE_FONT_CHOOSER,
                                        _("fnt"),
                                        _("FontChooser"),
                                        _("font chooser"))

rolenames[ROLE_FORM] = Rolename(ROLE_FORM,
                                _("form"),
                                _("Form"),
                                _("form"))

rolenames[ROLE_FRAME] = Rolename(ROLE_FRAME,
                                 _("frm"),
                                 _("Frame"),
                                 _("frame"))

rolenames[ROLE_GLASS_PANE] = Rolename(ROLE_GLASS_PANE,
                                      _("gpn"),
                                      _("GlassPane"),
                                      _("glass pane"))

rolenames[ROLE_HEADING] = Rolename(ROLE_HEADING,
                                   _("heading"),
                                   _("Heading"),
                                   _("hdng"))

rolenames[ROLE_HTML_CONTAINER] = Rolename(ROLE_HTML_CONTAINER,
                                          _("html"),
                                          _("HtmlContainer"),
                                          _("h t m l container"))

rolenames[ROLE_ICON] = Rolename(ROLE_ICON,
                                _("icon"),
                                _("Icon"),
                                _("icon"))

rolenames[ROLE_IMAGE] = Rolename(ROLE_IMAGE,
                                 _("img"),
                                 _("Image"),
                                 _("image"))

rolenames[ROLE_INTERNAL_FRAME] = Rolename(ROLE_INTERNAL_FRAME,
                                          _("frame"),
                                          _("InternalFrame"),
                                          _("internal frame"))

rolenames[ROLE_LABEL] = Rolename(ROLE_LABEL,
                                 _("lbl"),
                                 _("Label"),
                                 _("label"))

rolenames[ROLE_LAYERED_PANE] = Rolename(ROLE_LAYERED_PANE,
                                        _("lyrdpn"),
                                        _("LayeredPane"),
                                        _("layered pane"))

rolenames[ROLE_LINK] = Rolename(ROLE_LINK,
                                _("lnk"),
                                _("Link"),
                                _("link"))

rolenames[ROLE_LIST] = Rolename(ROLE_LIST,
                                _("lst"),
                                _("List"),
                                _("list"))

rolenames[ROLE_LIST_ITEM] = Rolename(ROLE_LIST_ITEM,
                                     _("lstitm"),
                                     _("ListItem"),
                                     _("list item"))

rolenames[ROLE_MENU] = Rolename(ROLE_MENU,
                                _("mnu"),
                                _("Menu"),
                                _("menu"))

rolenames[ROLE_MENU_BAR] = Rolename(ROLE_MENU_BAR,
                                    _("mnubr"),
                                    _("MenuBar"),
                                    _("menu bar"))

rolenames[ROLE_MENU_ITEM] = Rolename(ROLE_MENU_ITEM,
                                     _("mnuitm"),
                                     _("MenuItem"),
                                     _("menu item"))

rolenames[ROLE_OPTION_PANE] = Rolename(ROLE_OPTION_PANE,
                                       _("optnpn"),
                                       _("OptionPane"),
                                       _("option pane"))

rolenames[ROLE_PAGE_TAB] = Rolename(ROLE_PAGE_TAB,
                                    _("page"),
                                    _("Page"),
                                    _("page"))

rolenames[ROLE_PAGE_TAB_LIST] = Rolename(ROLE_PAGE_TAB_LIST,
                                         _("tblst"),
                                         _("TabList"),
                                         _("tab list"))

rolenames[ROLE_PANEL] = Rolename(ROLE_PANEL,
                                 _("pnl"),
                                 _("Panel"),
                                 _("panel"))

rolenames[ROLE_PASSWORD_TEXT] = Rolename(ROLE_PASSWORD_TEXT,
                                         _("pwd"),
                                         _("Password"),
                                         _("password"))

rolenames[ROLE_POPUP_MENU] = Rolename(ROLE_POPUP_MENU,
                                      _("popmnu"),
                                      _("PopupMenu"),
                                      _("popup menu"))

rolenames[ROLE_PROGRESS_BAR] = Rolename(ROLE_PROGRESS_BAR,
                                        _("pgbar"),
                                        _("Progress"),
                                        _("progress bar"))

rolenames[ROLE_PUSH_BUTTON] = Rolename(ROLE_PUSH_BUTTON,
                                       _("btn"),
                                       _("Button"),
                                       _("button"))

rolenames[ROLE_RADIO_BUTTON] = Rolename(ROLE_RADIO_BUTTON,
                                        _("radio"),
                                        _("RadioButton"),
                                        _("radio button"))

rolenames[ROLE_RADIO_MENU_ITEM] = Rolename(ROLE_RADIO_MENU_ITEM,
                                           _("rdmnuitm"),
                                           _("RadioItem"),
                                           _("radio menu item"))

rolenames[ROLE_RADIO_MENU] = Rolename(ROLE_RADIO_MENU,
                                      _("rdmnu"),
                                      _("RadioMenu"),
                                      _("radio menu"))

rolenames[ROLE_ROOT_PANE] = Rolename(ROLE_ROOT_PANE,
                                     _("rtpn"),
                                     _("RootPane"),
                                     _("root pane"))

rolenames[ROLE_ROW_HEADER] = Rolename(ROLE_ROW_HEADER,
                                      _("rwhdr"),
                                      _("RowHeader"),
                                      _("row header"))

rolenames[ROLE_SCROLL_BAR] = Rolename(ROLE_SCROLL_BAR,
                                      _("scbr"),
                                      _("ScrollBar"),
                                      _("scroll bar"))

rolenames[ROLE_SCROLL_PANE] = Rolename(ROLE_SCROLL_PANE,
                                       _("scpn"),
                                       _("ScrollPane"),
                                       _("scroll pane"))

rolenames[ROLE_SECTION] = Rolename(ROLE_SECTION,
                                   _("sctn"),
                                   _("Section"),
                                   _("section"))

rolenames[ROLE_SEPARATOR] = Rolename(ROLE_SEPARATOR,
                                     _("seprtr"),
                                     _("Separator"),
                                     _("separator"))

rolenames[ROLE_SLIDER] = Rolename(ROLE_SLIDER,
                                  _("sldr"),
                                  _("Slider"),
                                  _("slider"))

rolenames[ROLE_SPLIT_PANE] = Rolename(ROLE_SPLIT_PANE,
                                      _("spltpn"),
                                      _("SplitPane"),
                                      _("split pane"))

rolenames[ROLE_SPIN_BUTTON] = Rolename(ROLE_SPIN_BUTTON,
                                       _("spin"),
                                       _("SpinButton"),
                                       _("spin button"))

rolenames[ROLE_STATUSBAR] = Rolename(ROLE_STATUSBAR,
                                     _("statbr"),
                                     _("StatusBar"),
                                     _("status bar"))

rolenames[ROLE_TABLE] = Rolename(ROLE_TABLE,
                                 _("tbl"),
                                 _("Table"),
                                 _("table"))

rolenames[ROLE_TABLE_CELL] = Rolename(ROLE_TABLE_CELL,
                                      _("cell"),
                                      _("Cell"),
                                      _("cell"))

rolenames[ROLE_TABLE_COLUMN_HEADER] = Rolename(ROLE_TABLE_COLUMN_HEADER,
                                               _("colhdr"),
                                               _("ColumnHeader"),
                                               _("column header"))

rolenames[ROLE_TABLE_ROW_HEADER] = Rolename(ROLE_TABLE_ROW_HEADER,
                                            _("rwhdr"),
                                            _("RowHeader"),
                                            _("row header"))

rolenames[ROLE_TEAR_OFF_MENU_ITEM] = Rolename(ROLE_TEAR_OFF_MENU_ITEM,
                                              _("tomnuitm"),
                                              _("TearOffMenuItem"),
                                              _("tear off menu item"))

rolenames[ROLE_TERMINAL] = Rolename(ROLE_TERMINAL,
                                    _("term"),
                                    _("Terminal"),
                                    _("terminal"))

rolenames[ROLE_TEXT] = Rolename(ROLE_TEXT,
                                _("txt"),
                                _("Text"),
                                _("text"))

rolenames[ROLE_ENTRY] = rolenames[ROLE_TEXT]

rolenames[ROLE_TOGGLE_BUTTON] = Rolename(ROLE_TOGGLE_BUTTON,
                                         _("tglbtn"),
                                         _("ToggleButton"),
                                         _("toggle button"))

rolenames[ROLE_TOOL_BAR] = Rolename(ROLE_TOOL_BAR,
                                    _("tbar"),
                                    _("ToolBar"),
                                    _("tool bar"))

rolenames[ROLE_TOOL_TIP] = Rolename(ROLE_TOOL_TIP,
                                    _("tip"),
                                    _("ToolTip"),
                                    _("tool tip"))

rolenames[ROLE_TREE] = Rolename(ROLE_TREE,
                                _("tree"),
                                _("Tree"),
                                _("tree"))

rolenames[ROLE_TREE_TABLE] = Rolename(ROLE_TREE_TABLE,
                                      _("trtbl"),
                                      _("TreeTable"),
                                      _("tree table"))

rolenames[ROLE_UNKNOWN] = Rolename(ROLE_UNKNOWN,
                                   _("unk"),
                                   _("Unknown"),
                                   _("unknown"))

rolenames[ROLE_VIEWPORT] = Rolename(ROLE_VIEWPORT,
                                    _("vwprt"),
                                    _("Viewport"),
                                    _("viewport"))

rolenames[ROLE_WINDOW] = Rolename(ROLE_WINDOW,
                                  _("wnd"),
                                  _("Window"),
                                  _("window"))

rolenames[ROLE_HEADER] = Rolename(ROLE_HEADER,
                                  _("hdr"),
                                  _("Header"),
                                  _("header"))

rolenames[ROLE_FOOTER] = Rolename(ROLE_FOOTER,
                                  _("ftr"),
                                  _("Footer"),
                                  _("footer"))

rolenames[ROLE_PARAGRAPH] = Rolename(ROLE_PARAGRAPH,
                                     _("para"),
                                     _("Paragraph"),
                                     _("paragraph"))

rolenames[ROLE_APPLICATION] = Rolename(ROLE_APPLICATION,
                                       _("app"),
                                       _("Application"),
                                       _("application"))

rolenames[ROLE_AUTOCOMPLETE] = Rolename(ROLE_AUTOCOMPLETE,
                                        _("auto"),
                                        _("AutoComplete"),
                                        _("autocomplete"))

rolenames[ROLE_EDITBAR] = Rolename(ROLE_EDITBAR,
                                   _("edtbr"),
                                   _("EditBar"),
                                   _("edit bar"))

rolenames[ROLE_EMBEDDED] = Rolename(ROLE_EMBEDDED,
                                    _("emb"),
                                    _("EmbeddedComponent"),
                                    _("embedded component"))

# Extra stuff from Gnopernicus.
#
#rolenames[ROLE_EXTENDED] = Rolename(ROLE_EXTENDED,
#                                    _("EXT"),
#                                    _("EXTENDED"),
#                                    _("extended"))
#
#rolenames[ROLE_HYPER_LINK] = Rolename(ROLE_HYPER_LINK,
#                                      _("LNK"),
#                                      _("LINK"),
#                                      _("link"))
#
#rolenames[ROLE_LINK] = Rolename(ROLE_LINK,
#                                _("LNK"),
#                                _("LINK"),
#                                _("link"))
#
#rolenames[ROLE_MULTI_LINE_TEXT] = Rolename(ROLE_MULTI_LINE_TEXT,
#                                           _("TXT"),
#                                           _("MULTI LINE TEXT"),
#                                           _("multi Line Text"))
#
#rolenames[ROLE_SINGLE_LINE_TEXT] = Rolename(ROLE_SINGLE_LINE_TEXT,
#                                            _("TXT"),
#                                            _("SINGLE LINE TEXT"),
#                                            _("single Line Text"))
#
#rolenames[ROLE_TABLE_LINE] = Rolename(ROLE_TABLE_LINE,
#                                      _("TLI"),
#                                      _("TABLE LINE"),
#                                      _("table line"))
#
#rolenames[ROLE_TITLE_BAR] = Rolename(ROLE_TITLE_BAR,
#                                     _("TIT"),
#                                     _("TITLE BAR"),
#                                     _("title bar"))
#
#rolenames[ROLE_TREE_ITEM] = Rolename(ROLE_TREE_ITEM,
#                                     _("TRI"),
#                                     _("TREE ITEM"),
#                                     _("tree item"))

def getSpeechForRoleName(obj):
    """Returns the localized name of the given Accessible object; the name is
    suitable to be spoken.  If a localized name cannot be discovered, this
    will return the string as defined by the at-spi.

    Arguments:
    - obj: an Accessible object

    Returns a string containing the localized name of the object suitable
    to be spoken.
    """

    name = obj.role
    if rolenames.has_key(name):
        return rolenames[name].speech
    else:
        debug.println(debug.LEVEL_WARNING, "No rolename for %s" % name)
        localizedRoleName = obj.localizedRoleName
        if localizedRoleName and len(localizedRoleName):
            return localizedRoleName
        else:
            return name

def getShortBrailleForRoleName(obj):
    """Returns the localized name of the given Accessible object; the name is
    a short string suitable for a Braille display.  If a localized name cannot
    be discovered, this will return the string as defined by the at-spi.

    Arguments:
    - obj: an Accessible object

    Returns a short string containing the localized name of the object
    suitable for a Braille display.
    """

    name = obj.role
    if rolenames.has_key(name):
        return rolenames[name].brailleShort
    else:
        debug.println(debug.LEVEL_WARNING, "No rolename for %s" % name)
        localizedRoleName = obj.localizedRoleName
        if localizedRoleName and len(localizedRoleName):
            return localizedRoleName
        else:
            return name

def getLongBrailleForRoleName(obj):
    """Returns the localized name of the given Accessible object; the name is
    a long string suitable for a Braille display.  If a localized name cannot
    be discovered, this will return the string as defined by the at-spi.

    Arguments:
    - obj: an Accessible object

    Returns a string containing the localized name of the object suitable for
    a Braille display.
    """

    name = obj.role
    if rolenames.has_key(name):
        return rolenames[name].brailleLong
    else:
        debug.println(debug.LEVEL_WARNING, "No rolename for %s" % name)
        localizedRoleName = obj.localizedRoleName
        if localizedRoleName and len(localizedRoleName):
            return localizedRoleName
        else:
            return name

def getBrailleForRoleName(obj):
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
        return getShortBrailleForRoleName(obj)
    else:
        return getLongBrailleForRoleName(obj)
