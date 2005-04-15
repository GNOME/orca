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
from orca_i18n import _ # for gettext support

class Rolename:
    """Provides localized forms of rolenames for speech and Braille.
    """

    def __init__(self, rolename, brailleShort, brailleLong, speech):
        """Created a new rolename with the given parameters.

        Arguments:
        - rolename:     the internationalized (e.g., machine) name for the role
        - speech:       the localized string to speak for speech
        - brailleShort: the localized short string for Braille display
        - brailleLong:  the localized long string for Braille display
        """

        self.rolename = rolename
        self.brailleShort = brailleShort
        self.brailleLong = brailleLong
        self.speech = speech


# Table derived from atk/atk/atkobject.c:role_items and
# gnopernicus/srcore/srpres.c.  The first part matches the ATK role items
# in order, and the second consists of gnopernicus additions.
#
# [[[TODO: WDW - For some reason, the C SPI wants to put dashes in the role
# name whereas Python gets the name without dashes.
#
# [[[TODO: WDW - the AT-SPI also has getLocalizedRoleName, which might a
# more appropriate thing to use, as it covers the situation where an app
# has developed a brand new component with a brand new role.]]]
#
rolenames = {}

rolenames["invalid"] = Rolename("invalid",
                                _("???"),
                                _("INVALID"),
                                _("invalid"))

rolenames["accelerator label"] = Rolename("accelerator label",
                                          _("ACC"),
                                          _("ACCELERATOR LABEL"),
                                          _("accelerator label"))

rolenames["alert"] = Rolename("alert",
                              _("ALR"),
                              _("ALERT"),
                              _("alert"))

rolenames["animation"] = Rolename("animation",
                                  _("ANI"),
                                  _("ANIMATION"),
                                  _("animation"))

rolenames["arrow"] = Rolename("arrow",
                              _("ARR"),
                              _("ARROW"),
                              _("arrow"))

rolenames["calendar"] = Rolename("calendar",
                                 _("CAL"),
                                 _("CALENDAR"),
                                 _("calendar"))


rolenames["canvas"] = Rolename("canvas",
                               _("CNV"),
                               _("CANVAS"),
                               _("canvas"))

rolenames["check box"] = Rolename("check box",
                                  _("CHK"),
                                  _("CHECK_BOX"),
                                  _("check box"))

rolenames["check menu item"] = Rolename("check menu item",
                                        _("MIT"),
                                        _("MENU ITEM"),
                                        _("check Menu item"))

rolenames["color chooser"] = Rolename("color chooser",
                                      _("CCH"),
                                      _("COLOR CHOOSER"),
                                      _("color chooser"))

rolenames["column header"] = Rolename("column header",
                                      _("CHD"),
                                      _("COLUMN HEADER"),
                                      _("column header"))

rolenames["combo box"] = Rolename("combo box",
                                  _("CBO"),
                                  _("COMBO BOX"),
                                  _("combo box"))

rolenames["dateeditor"] = Rolename("dateeditor",
                                    _("DAT"),
                                    _("DATE EDITOR"),
                                    _("date editor"))

rolenames["desktop icon"] = Rolename("desktop icon",
                                     _("DIC"),
                                     _("DESKTOP ICON"),
                                     _("desktop icon"))

rolenames["desktop frame"] = Rolename("desktop frame",
                                      _("DFR"),
                                      _("DESKTOP FRAME"),
                                      _("desktop frame"))

rolenames["dial"] = Rolename("dial",
                             _("DIL"),
                             _("DIAL"),
                             _("dial"))

rolenames["dialog"] = Rolename("dialog",
                               _("DLG"),
                               _("DIALOG"),
                               _("dialog"))

rolenames["directory pane"] = Rolename("directory pane",
                                       _("DIP"),
                                       _("DIRECTORY PANE"),
                                       _("directory pane"))

rolenames["drawing area"] = Rolename("drawing area",
                                     _("DRW"),
                                     _("DRAWING AREA"),
                                     _("drawing area"))

rolenames["file chooser"] = Rolename("file chooser",
                                     _("FCH"),
                                     _("FILE CHOOSER"),
                                     _("file chooser"))

rolenames["filler"] = Rolename("filler",
                               _("FLR"),
                               _("FILLER"),
                               _("filler"))

rolenames["fontchooser"] = Rolename("fontchooser",
                                    _("FNT"),
                                    _("FONT CHOOSER"),
                                    _("font chooser"))

rolenames["frame"] = Rolename("frame",
                              _("FRM"),
                              _("FRAME"),
                              _("frame"))

rolenames["glass pane"] = Rolename("glass pane",
                                   _("GPN"),
                                   _("GLASS PANE"),
                                   _("glass pane"))

rolenames["html container"] = Rolename("html container",
                                       _("HTM"),
                                       _("HTML CONTAINER"),
                                       _("h T M L container"))

rolenames["icon"] = Rolename("icon",
                             _("ICO"),
                             _("ICON"),
                             _("icon"))

rolenames["image"] = Rolename("image",
                              _("IMG"),
                              _("IMAGE"),
                              _("image"))

rolenames["internal frame"] = Rolename("internal frame",
                                       _("IFR"),
                                       _("INTERNAL FRAME"),
                                       _("internal frame"))

rolenames["label"] = Rolename("label",
                              _("LBL"),
                              _("LABEL"),
                              _("label"))

rolenames["layered pane"] = Rolename("layered pane",
                                     _("LPN"),
                                     _("LAYERED PANE"),
                                     _("layered pane"))

rolenames["list"] = Rolename("list",
                             _("LST"),
                             _("LIST"),
                             _("list"))

rolenames["list item"] = Rolename("list item",
                                  _("LIT"),
                                  _("LIST ITEM"),
                                  _("list item"))

rolenames["menu"] = Rolename("menu",
                             _("MNU"),
                             _("MENU"),
                             _("menu"))

rolenames["menu bar"] = Rolename("menu bar",
                                 _("MBR"),
                                 _("MENU BAR"),
                                 _("menu bar"))

rolenames["menu item"] = Rolename("menu item",
                                  _("MIT"),
                                  _("MENU ITEM"),
                                  _("menu item"))

rolenames["option pane"] = Rolename("option pane",
                                    _("OPN"),
                                    _("OPTION PANE"),
                                    _("option pane"))

rolenames["page tab"] = Rolename("page tab",
                                 _("PGT"),
                                 _("PAGE TAB"),
                                 _("page tab"))

rolenames["page tab list"] = Rolename("page tab list",
                                      _("PTL"),
                                      _("PAGE TAB LIST"),
                                      _("page tab list"))

rolenames["panel"] = Rolename("panel",
                              _("PNL"),
                              _("PANEL"),
                              _("panel"))

rolenames["password text"] = Rolename("password text",
                                      _("PWD"),
                                      _("PASSWORD TEXT"),
                                      _("password text"))

rolenames["popup menu"] = Rolename("popup menu",
                                   _("PMN"),
                                   _("POPUP MENU"),
                                   _("popup menu"))

rolenames["progress bar"] = Rolename("progress bar",
                                     _("PRG"),
                                     _("PROGRESS BAR"),
                                     _("progress bar"))

rolenames["push button"] = Rolename("push button",
                                    _("PBT"),
                                    _("PUSH BUTTON"),
                                    _("push button"))

rolenames["radio button"] = Rolename("radio button",
                                     _("RAD"),
                                     _("RADIO BUTTON"),
                                     _("radio button"))

rolenames["radio menu item"] = Rolename("radio menu item",
                                        _("MIT"),
                                        _("MENU ITEM"),
                                        _("radio Menu item"))

rolenames["root pane"] = Rolename("root pane",
                                  _("RPN"),
                                  _("ROOT PANE"),
                                  _("root pane"))

rolenames["row header"] = Rolename("row header",
                                   _("RHD"),
                                   _("ROW HEADER"),
                                   _("row header"))

rolenames["scroll bar"] = Rolename("scroll bar",
                                   _("SCR"),
                                   _("SCROLL BAR"),
                                   _("scroll bar"))

rolenames["scroll pane"] = Rolename("scroll pane",
                                    _("SPN"),
                                    _("SCROLL PANE"),
                                    _("scroll pane"))

rolenames["separator"] = Rolename("separator",
                                  _("SEP"),
                                  _("SEPARATOR"),
                                  _("separator"))

rolenames["slider"] = Rolename("slider",
                               _("SLD"),
                               _("SLIDER"),
                               _("slider"))

rolenames["split pane"] = Rolename("split pane",
                                   _("SPP"),
                                   _("SPLIT PANE"),
                                   _("split pane"))

rolenames["spin button"] = Rolename("spin button",
                                    _("SPN"),
                                    _("SPIN BUTTON"),
                                    _("spin button"))

rolenames["status bar"] = Rolename("status bar",
                                   _("STA"),
                                   _("STATUS BAR"),
                                   _("status bar"))

rolenames["table"] = Rolename("table",
                              _("TAB"),
                              _("TABLE"),
                              _("table"))

rolenames["table cell"] = Rolename("table cell",
                                   _("CEL"),
                                   _("TABLE CELL"),
                                   _("table cell"))

rolenames["table column header"] = Rolename("table column header",
                                            _("TCH"),
                                            _("TABLE COLUMN HEADER"),
                                            _("table column header"))

rolenames["table row header"] = Rolename("table row header",
                                         _("TRH"),
                                         _("TABLE ROW HEADER"),
                                         _("table row header"))

rolenames["tear off menu item"] = Rolename("tear off menu item",
                                           _("TOM"),
                                           _("TEAR OFF MENU ITEM"),
                                           _("tear off menu item"))

rolenames["terminal"] = Rolename("terminal",
                                 _("TRM"),
                                 _("TERMINAL"),
                                 _("terminal"))

rolenames["text"] = Rolename("text",
                             _("TXT"),
                             _("TEXT"),
                             _("text"))

rolenames["toggle button"] = Rolename("toggle button",
                                      _("TOG"),
                                      _("TOGGLE BUTTON"),
                                      _("toggle button"))

rolenames["tool bar"] = Rolename("tool bar",
                                 _("TOL"),
                                 _("TOOL BAR"),
                                 _("tool bar"))

rolenames["tool tip"] = Rolename("tool tip",
                                 _("TIP"),
                                 _("TOOL TIP"),
                                 _("tool tip"))

rolenames["tree"] = Rolename("tree",
                             _("TRE"),
                             _("TREE"),
                             _("tree"))

rolenames["tree table"] = Rolename("tree table",
                                   _("TRT"),
                                   _("TREE TABLE"),
                                   _("tree table"))

rolenames["unknown"] = Rolename("unknown",
                                _("UNK"),
                                _("UNKNOWN"),
                                _("unknown"))

rolenames["viewport"] = Rolename("viewport",
                                 _("VWP"),
                                 _("VIEWPORT"),
                                 _("viewport"))

rolenames["window"] = Rolename("window",
                               _("WND"),
                               _("WINDOW"),
                               _("window"))

rolenames["header"] = Rolename("header",
                               _("HDR"),
                               _("HEADER"),
                               _("header"))

rolenames["footer"] = Rolename("footer",
                               _("FTR"),
                               _("FOOTER"),
                               _("footer"))

rolenames["paragraph"] = Rolename("paragraph",
                               _("PGH"),
                               _("PARAGRAPH"),
                               _("paragraph"))

rolenames["application"] = Rolename("application",
                                    _("APP"),
                                    _("APPLICATION"),
                                    _("application"))

rolenames["autocomplete"] = Rolename("autocomplete",
                                     _("AUT"),
                                     _("AUTO COMPLETE"),
                                     _("autocomplete"))

rolenames["edit bar"] = Rolename("edit bar",
                                 _("EDB"),
                                 _("EDIT BAR"),
                                 _("edit bar"))

rolenames["embedded component"] = Rolename("embedded component",
                                           _("EMB"),
                                           _("EMBEDDED COMPONENT"),
                                           _("embedded component"))



# Extra stuff from Gnopernicus.
#
rolenames["extended"] = Rolename("extended",
                                 _("EXT"),
                                 _("EXTENDED"),
                                 _("extended"))

rolenames["hyper link"] = Rolename("hyper link",
                                   _("LNK"),
                                   _("LINK"),
                                   _("link"))

rolenames["link"] = Rolename("link",
                             _("LNK"),
                             _("LINK"),
                             _("link"))

rolenames["multi line text"] = Rolename("multi line text",
                                        _("TXT"),
                                        _("MULTI LINE TEXT"),
                                        _("multi Line Text"))

rolenames["single line text"] = Rolename("single line text",
                                         _("TXT"),
                                         _("SINGLE LINE TEXT"),
                                         _("single Line Text"))

rolenames["table line"] = Rolename("table line",
                                   _("TLI"),
                                   _("TABLE LINE"),
                                   _("table line"))

rolenames["table columns header"] = Rolename("table columns header",
                                             _("TCH"),
                                             _("TABLE COLUMNS HEADER"),
                                             _("table columns header"))

rolenames["title bar"] = Rolename("title bar",
                                  _("TIT"),
                                  _("TITLE BAR"),
                                  _("title bar"))

rolenames["tree item"] = Rolename("tree item",
                                  _("TRI"),
                                  _("TREE ITEM"),
                                  _("tree item"))



def getRoleName (obj):
    """Returns the localized name of the given Accessible object.
    If a localized name cannot be discovered, this will return
    the string as defined by the at-spi.
    
    Arguments:
    - obj: an Accessible object

    Returns a string containing the localized name of the object.
    """

    return getSpeechForRoleName (obj)


def getSpeechForRoleName (obj):
    """Returns the localized name of the given Accessible object; the name is
    suitable to be spoken.  If a localized name cannot be discovered, this
    will return the string as defined by the at-spi.
    
    Arguments:
    - obj: an Accessible object

    Returns a string containing the localized name of the object suitable
    to be spoken.
    """
    
    name = obj.role
    if rolenames.has_key (name):
        return rolenames[name].speech
    else:
        debug.println (debug.LEVEL_WARNING, "No rolename for %s" % name)
        return name


def getShortBrailleForRoleName (obj):
    """Returns the localized name of the given Accessible object; the name is
    a short string suitable for a Braille display.  If a localized name cannot
    be discovered, this will return the string as defined by the at-spi.
    
    Arguments:
    - obj: an Accessible object

    Returns a short string containing the localized name of the object
    suitable for a Braille display.
    """
    
    name = obj.role
    if rolenames.has_key (name):
        return rolenames[name].brailleShort
    else:
        debug.println (debug.LEVEL_WARNING, "No rolename for %s" % name)
        return name


def getLongBrailleForRoleName (obj):
    """Returns the localized name of the given Accessible object; the name is
    a long string suitable for a Braille display.  If a localized name cannot
    be discovered, this will return the string as defined by the at-spi.
    
    Arguments:
    - obj: an Accessible object

    Returns a string containing the localized name of the object suitable for
    a Braille display.
    """
    
    name = obj.role
    if rolenames.has_key (name):
        return rolenames[name].brailleLong
    else:
        debug.println (debug.LEVEL_WARNING, "No rolename for %s" % name)
        return name
