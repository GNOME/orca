# Orca
#
# Copyright 2004-2005 Sun Microsystems Inc.
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

"""Provides a method, getRoleName, that converts the role name of an
Accessible object into a localized string.
"""

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
ROLE_DRAWING_AREA        = "drawing area"
ROLE_FILE_CHOOSER        = "file chooser"
ROLE_FILLER              = "filler"
ROLE_FONT_CHOOSER        = "fontchooser"
ROLE_FRAME               = "frame"
ROLE_GLASS_PANE          = "glass pane"
ROLE_HTML_CONTAINER      = "html container"
ROLE_ICON                = "icon"
ROLE_IMAGE               = "image"
ROLE_INTERNAL_FRAME      = "internal frame"
ROLE_LABEL               = "label"
ROLE_LAYERED_PANE        = "layered pane"
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
# has developed a brand new component with a brand new role.]]]
#
rolenames = {}

rolenames[ROLE_INVALID] = Rolename(ROLE_INVALID,
                                   _("???"),
                                   _("INVALID"),
                                   _("invalid"))

rolenames[ROLE_ACCEL_LABEL] = Rolename(ROLE_ACCEL_LABEL,
                                       _("ACC"),
                                       _("ACCELERATOR LABEL"),
                                       _("accelerator label"))

rolenames[ROLE_ALERT] = Rolename(ROLE_ALERT,
                                 _("ALR"),
                                 _("ALERT"),
                                 _("alert"))

rolenames[ROLE_ANIMATION] = Rolename(ROLE_ANIMATION,
                                     _("ANI"),
                                     _("ANIMATION"),
                                     _("animation"))

rolenames[ROLE_ARROW] = Rolename(ROLE_ARROW,
                                 _("ARR"),
                                 _("ARROW"),
                                 _("arrow"))

rolenames[ROLE_CALENDAR] = Rolename(ROLE_CALENDAR,
                                    _("CAL"),
                                    _("CALENDAR"),
                                    _("calendar"))

rolenames[ROLE_CANVAS] = Rolename(ROLE_CANVAS,
                                  _("CNV"),
                                  _("CANVAS"),
                                  _("canvas"))

rolenames[ROLE_CHECK_BOX] = Rolename(ROLE_CHECK_BOX,
                                     _("CHK"),
                                     _("CHECK BOX"),
                                     _("check box"))

rolenames[ROLE_CHECK_MENU_ITEM] = Rolename(ROLE_CHECK_MENU_ITEM,
                                           _("CHK"),
                                           _("CHECK MENU ITEM"),
                                           _("check menu item"))

rolenames[ROLE_CHECK_MENU] = Rolename(ROLE_CHECK_MENU,
                                      _("CKM"),
                                      _("CHECK MENU"),
                                      _("check menu"))

rolenames[ROLE_COLOR_CHOOSER] = Rolename(ROLE_COLOR_CHOOSER,
                                         _("CCH"),
                                         _("COLOR CHOOSER"),
                                         _("color chooser"))

rolenames[ROLE_COLUMN_HEADER] = Rolename(ROLE_COLUMN_HEADER,
                                         _("CHD"),
                                         _("COLUMN HEADER"),
                                         _("column header"))

rolenames[ROLE_COMBO_BOX] = Rolename(ROLE_COMBO_BOX,
                                     _("CBO"),
                                     _("COMBO BOX"),
                                     _("combo box"))

rolenames[ROLE_DATE_EDITOR] = Rolename(ROLE_DATE_EDITOR,
                                       _("DAT"),
                                       _("DATE EDITOR"),
                                       _("date editor"))

rolenames[ROLE_DESKTOP_ICON] = Rolename(ROLE_DESKTOP_ICON,
                                        _("DIC"),
                                        _("DESKTOP ICON"),
                                        _("desktop icon"))

rolenames[ROLE_DESKTOP_FRAME] = Rolename(ROLE_DESKTOP_FRAME,
                                         _("DFR"),
                                         _("DESKTOP FRAME"),
                                         _("desktop frame"))

rolenames[ROLE_DIAL] = Rolename(ROLE_DIAL,
                                _("DIL"),
                                _("DIAL"),
                                _("dial"))

rolenames[ROLE_DIALOG] = Rolename(ROLE_DIALOG,
                                  _("DLG"),
                                  _("DIALOG"),
                                  _("dialog"))

rolenames[ROLE_DIRECTORY_PANE] = Rolename(ROLE_DIRECTORY_PANE,
                                          _("DIP"),
                                          _("DIRECTORY PANE"),
                                          _("directory pane"))

rolenames[ROLE_DRAWING_AREA] = Rolename(ROLE_DRAWING_AREA,
                                        _("DRW"),
                                        _("DRAWING AREA"),
                                        _("drawing area"))

rolenames[ROLE_FILE_CHOOSER] = Rolename(ROLE_FILE_CHOOSER,
                                        _("FCH"),
                                        _("FILE CHOOSER"),
                                        _("file chooser"))

rolenames[ROLE_FILLER] = Rolename(ROLE_FILLER,
                                  _("FLR"),
                                  _("FILLER"),
                                  _("filler"))

rolenames[ROLE_FONT_CHOOSER] = Rolename(ROLE_FONT_CHOOSER,
                                        _("FNT"),
                                        _("FONT CHOOSER"),
                                        _("font chooser"))

rolenames[ROLE_FRAME] = Rolename(ROLE_FRAME,
                                 _("FRM"),
                                 _("FRAME"),
                                 _("frame"))

rolenames[ROLE_GLASS_PANE] = Rolename(ROLE_GLASS_PANE,
                                      _("GPN"),
                                      _("GLASS PANE"),
                                      _("glass pane"))

rolenames[ROLE_HTML_CONTAINER] = Rolename(ROLE_HTML_CONTAINER,
                                          _("HTM"),
                                          _("HTML CONTAINER"),
                                          _("h t m l container"))

rolenames[ROLE_ICON] = Rolename(ROLE_ICON,
                                _("ICO"),
                                _("ICON"),
                                _("icon"))

rolenames[ROLE_IMAGE] = Rolename(ROLE_IMAGE,
                                 _("IMG"),
                                 _("IMAGE"),
                                 _("image"))

rolenames[ROLE_INTERNAL_FRAME] = Rolename(ROLE_INTERNAL_FRAME,
                                          _("IFR"),
                                          _("INTERNAL FRAME"),
                                          _("internal frame"))

rolenames[ROLE_LABEL] = Rolename(ROLE_LABEL,
                                 _("LBL"),
                                 _("LABEL"),
                                 _("label"))

rolenames[ROLE_LAYERED_PANE] = Rolename(ROLE_LAYERED_PANE,
                                        _("LPN"),
                                        _("LAYERED PANE"),
                                        _("layered pane"))

rolenames[ROLE_LIST] = Rolename(ROLE_LIST,
                                _("LST"),
                                _("LIST"),
                                _("list"))

rolenames[ROLE_LIST_ITEM] = Rolename(ROLE_LIST_ITEM,
                                     _("LIT"),
                                     _("LIST ITEM"),
                                     _("list item"))

rolenames[ROLE_MENU] = Rolename(ROLE_MENU,
                                _("MNU"),
                                _("MENU"),
                                _("menu"))

rolenames[ROLE_MENU_BAR] = Rolename(ROLE_MENU_BAR,
                                    _("MBR"),
                                    _("MENU BAR"),
                                    _("menu bar"))

rolenames[ROLE_MENU_ITEM] = Rolename(ROLE_MENU_ITEM,
                                     _("MIT"),
                                     _("MENU ITEM"),
                                     _("menu item"))

rolenames[ROLE_OPTION_PANE] = Rolename(ROLE_OPTION_PANE,
                                       _("OPN"),
                                       _("OPTION PANE"),
                                       _("option pane"))

rolenames[ROLE_PAGE_TAB] = Rolename(ROLE_PAGE_TAB,
                                    _("PGT"),
                                    _("PAGE TAB"),
                                    _("page tab"))

rolenames[ROLE_PAGE_TAB_LIST] = Rolename(ROLE_PAGE_TAB_LIST,
                                         _("PTL"),
                                         _("PAGE TAB LIST"),
                                         _("page tab list"))

rolenames[ROLE_PANEL] = Rolename(ROLE_PANEL,
                                 _("PNL"),
                                 _("PANEL"),
                                 _("panel"))

rolenames[ROLE_PASSWORD_TEXT] = Rolename(ROLE_PASSWORD_TEXT,
                                         _("PWD"),
                                         _("PASSWORD TEXT"),
                                         _("password text"))

rolenames[ROLE_POPUP_MENU] = Rolename(ROLE_POPUP_MENU,
                                      _("PMN"),
                                      _("POPUP MENU"),
                                      _("popup menu"))

rolenames[ROLE_PROGRESS_BAR] = Rolename(ROLE_PROGRESS_BAR,
                                        _("PRG"),
                                        _("PROGRESS BAR"),
                                        _("progress bar"))

rolenames[ROLE_PUSH_BUTTON] = Rolename(ROLE_PUSH_BUTTON,
                                       _("PBT"),
                                       _("PUSH BUTTON"),
                                       _("push button"))

rolenames[ROLE_RADIO_BUTTON] = Rolename(ROLE_RADIO_BUTTON,
                                        _("RAD"),
                                        _("RADIO BUTTON"),
                                        _("radio button"))

rolenames[ROLE_RADIO_MENU_ITEM] = Rolename(ROLE_RADIO_MENU_ITEM,
                                           _("RAD"),
                                           _("RADIO MENU ITEM"),
                                           _("radio menu item"))

rolenames[ROLE_RADIO_MENU] = Rolename(ROLE_RADIO_MENU,
                                      _("RDM"),
                                      _("RADIO MENU"),
                                      _("radio menu"))

rolenames[ROLE_ROOT_PANE] = Rolename(ROLE_ROOT_PANE,
                                     _("RPN"),
                                     _("ROOT PANE"),
                                     _("root pane"))

rolenames[ROLE_ROW_HEADER] = Rolename(ROLE_ROW_HEADER,
                                      _("RHD"),
                                      _("ROW HEADER"),
                                      _("row header"))

rolenames[ROLE_SCROLL_BAR] = Rolename(ROLE_SCROLL_BAR,
                                      _("SCR"),
                                      _("SCROLL BAR"),
                                      _("scroll bar"))

rolenames[ROLE_SCROLL_PANE] = Rolename(ROLE_SCROLL_PANE,
                                       _("SPN"),
                                       _("SCROLL PANE"),
                                       _("scroll pane"))

rolenames[ROLE_SEPARATOR] = Rolename(ROLE_SEPARATOR,
                                     _("SEP"),
                                     _("SEPARATOR"),
                                     _("separator"))

rolenames[ROLE_SLIDER] = Rolename(ROLE_SLIDER,
                                  _("SLD"),
                                  _("SLIDER"),
                                  _("slider"))

rolenames[ROLE_SPLIT_PANE] = Rolename(ROLE_SPLIT_PANE,
                                      _("SPP"),
                                      _("SPLIT PANE"),
                                      _("split pane"))

rolenames[ROLE_SPIN_BUTTON] = Rolename(ROLE_SPIN_BUTTON,
                                       _("SPN"),
                                       _("SPIN BUTTON"),
                                       _("spin button"))

rolenames[ROLE_STATUSBAR] = Rolename(ROLE_STATUSBAR,
                                     _("STA"),
                                     _("STATUS BAR"),
                                     _("status bar"))

rolenames[ROLE_TABLE] = Rolename(ROLE_TABLE,
                                 _("TAB"),
                                 _("TABLE"),
                                 _("table"))

rolenames[ROLE_TABLE_CELL] = Rolename(ROLE_TABLE_CELL,
                                      _("CEL"),
                                      _("TABLE CELL"),
                                      _("table cell"))

rolenames[ROLE_TABLE_COLUMN_HEADER] = Rolename(ROLE_TABLE_COLUMN_HEADER,
                                               _("TCH"),
                                               _("TABLE COLUMN HEADER"),
                                               _("table column header"))

rolenames[ROLE_TABLE_ROW_HEADER] = Rolename(ROLE_TABLE_ROW_HEADER,
                                            _("TRH"),
                                            _("TABLE ROW HEADER"),
                                            _("table row header"))

rolenames[ROLE_TEAR_OFF_MENU_ITEM] = Rolename(ROLE_TEAR_OFF_MENU_ITEM,
                                              _("TOM"),
                                              _("TEAR OFF MENU ITEM"),
                                              _("tear off menu item"))

rolenames[ROLE_TERMINAL] = Rolename(ROLE_TERMINAL,
                                    _("TRM"),
                                    _("TERMINAL"),
                                    _("terminal"))

rolenames[ROLE_TEXT] = Rolename(ROLE_TEXT,
                                _("TXT"),
                                _("TEXT"),
                                _("text"))

rolenames[ROLE_TOGGLE_BUTTON] = Rolename(ROLE_TOGGLE_BUTTON,
                                         _("TOG"),
                                         _("TOGGLE BUTTON"),
                                         _("toggle button"))

rolenames[ROLE_TOOL_BAR] = Rolename(ROLE_TOOL_BAR,
                                    _("TOL"),
                                    _("TOOL BAR"),
                                    _("tool bar"))

rolenames[ROLE_TOOL_TIP] = Rolename(ROLE_TOOL_TIP,
                                    _("TIP"),
                                    _("TOOL TIP"),
                                    _("tool tip"))

rolenames[ROLE_TREE] = Rolename(ROLE_TREE,
                                _("TRE"),
                                _("TREE"),
                                _("tree"))

rolenames[ROLE_TREE_TABLE] = Rolename(ROLE_TREE_TABLE,
                                      _("TRT"),
                                      _("TREE TABLE"),
                                      _("tree table"))

rolenames[ROLE_UNKNOWN] = Rolename(ROLE_UNKNOWN,
                                   _("UNK"),
                                   _("UNKNOWN"),
                                   _("unknown"))

rolenames[ROLE_VIEWPORT] = Rolename(ROLE_VIEWPORT,
                                    _("VWP"),
                                    _("VIEWPORT"),
                                    _("viewport"))

rolenames[ROLE_WINDOW] = Rolename(ROLE_WINDOW,
                                  _("WND"),
                                  _("WINDOW"),
                                  _("window"))

rolenames[ROLE_HEADER] = Rolename(ROLE_HEADER,
                                  _("HDR"),
                                  _("HEADER"),
                                  _("header"))

rolenames[ROLE_FOOTER] = Rolename(ROLE_FOOTER,
                                  _("FTR"),
                                  _("FOOTER"),
                                  _("footer"))

rolenames[ROLE_PARAGRAPH] = Rolename(ROLE_PARAGRAPH,
                                     _("PGH"),
                                     _("PARAGRAPH"),
                                     _("paragraph"))

rolenames[ROLE_APPLICATION] = Rolename(ROLE_APPLICATION,
                                       _("APP"),
                                       _("APPLICATION"),
                                       _("application"))

rolenames[ROLE_AUTOCOMPLETE] = Rolename(ROLE_AUTOCOMPLETE,
                                        _("AUT"),
                                        _("AUTO COMPLETE"),
                                        _("autocomplete"))

rolenames[ROLE_EDITBAR] = Rolename(ROLE_EDITBAR,
                                   _("EDB"),
                                   _("EDIT BAR"),
                                   _("edit bar"))

rolenames[ROLE_EMBEDDED] = Rolename(ROLE_EMBEDDED,
                                    _("EMB"),
                                    _("EMBEDDED COMPONENT"),
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
    
    brailleRolenameStyle = settings.getSetting(
        "brailleRolenameStyle",
        settings.BRAILLE_ROLENAME_STYLE_LONG)

    if brailleRolenameStyle == settings.BRAILLE_ROLENAME_STYLE_SHORT:
        return getShortBrailleForRoleName(obj)
    else:
        return getLongBrailleForRoleName(obj)


def getRoleName(obj):
    """Returns the localized name of the given Accessible object.
    If a localized name cannot be discovered, this will return
    the string as defined by the at-spi.
    
    Arguments:
    - obj: an Accessible object

    Returns a string containing the localized name of the object.
    """

    return getSpeechForRoleName(obj)
