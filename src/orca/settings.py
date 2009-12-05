# Orca
#
# Copyright 2004-2009 Sun Microsystems Inc.
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

"""Manages the settings for Orca.  This will defer to user settings first, but
fallback to local settings if the user settings doesn't exist (e.g., in the
case of gdm) or doesn't have the specified attribute."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2004-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import os
import re

screenWidth = 640
screenHeight = 480
tty = 7

# Whether tool tips can be presented.
#
canPresentToolTips = False

try:
    # This can fail due to gtk not being available.  We want to
    # be able to recover from that if possible.  The main driver
    # for this is to allow "orca --text-setup" to work even if
    # the desktop is not running.
    #
    import gtk.gdk
    _display = gtk.gdk.display_get_default()
    _screen = _display.get_default_screen()
    _root_window = _screen.get_root_window()

    # These are used for placing the magnifier zoomer.
    #
    screenWidth = _screen.get_width()
    screenHeight = _screen.get_height()

    # The bug that caused gnome-panel to crash is fixed in GTK 2.10.11.
    minimum_gtk_version = (100000 * 2) + \
                          (1000 * 10) + \
                           11
    current_gtk_version  = (100000 * gtk.gtk_version[0]) + \
                           (1000 * gtk.gtk_version[1]) + \
                            gtk.gtk_version[2]
    canPresentToolTips = (current_gtk_version >= minimum_gtk_version)

    # We want to know what the tty is so we can send it to BrlAPI
    # if possible.
    #
    (atom, format, data) = _root_window.property_get("XFree86_VT")
    tty = data[0]
except:
    pass

try:
    import gconf
    gconfClient = gconf.client_get_default()
except:
    gconfClient = None

import pyatspi

import debug
from acss import ACSS
from orca_i18n import _           # for gettext support
from orca_i18n import C_          # to provide qualified translatable strings

# These are the settings that Orca supports the user customizing.
#
userCustomizableSettings = [
    "orcaModifierKeys",
    "enableSpeech",
    "speechServerFactory",
    "speechServerInfo",
    "voices",
    "speechVerbosityLevel",
    "readTableCellRow",
    "enableSpeechIndentation",
    "enableEchoByCharacter",
    "enableEchoByWord",
    "enableEchoBySentence",
    "enableKeyEcho",
    "enablePrintableKeys",
    "enableModifierKeys",
    "enableLockingKeys",
    "enableFunctionKeys",
    "enableActionKeys",
    "enableNavigationKeys",
    "enableDiacriticalKeys",
    "enablePauseBreaks",
    "enableTutorialMessages",
    "enableMnemonicSpeaking",
    "enablePositionSpeaking",
    "enableBraille",
    "enableBrailleContext",
    "enableBrailleGrouping",
    "disableBrailleEOL",
    "brailleEOLIndicator",
    "brailleVerbosityLevel",
    "brailleRolenameStyle",
    "brailleSelectorIndicator",
    "brailleLinkIndicator",
    "brailleAlignmentStyle",
    "enableBrailleMonitor",
    "enableMagnifier",
    "enableMagLiveUpdating",
    "enableMagCursor",
    "enableMagCursorExplicitSize",
    "magHideCursor",
    "magCursorSize",
    "magCursorColor",
    "enableMagCrossHair",
    "enableMagCrossHairClip",
    "magCrossHairSize",
    "magCrossHairColor",
    "magZoomerType",
    "magZoomerLeft",
    "magZoomerRight",
    "magZoomerTop",
    "magZoomerBottom",
    "magZoomFactor",
    "enableMagZoomerBorder",
    "magZoomerBorderSize",
    "magZoomerBorderColor",
    "enableMagZoomerColorInversion",
    "magBrightnessLevel",
    "magBrightnessLevelRed",
    "magBrightnessLevelBlue",
    "magBrightnessLevelGreen",
    "magContrastLevel",
    "magContrastLevelRed",
    "magContrastLevelGreen",
    "magContrastLevelBlue",
    "magSmoothingMode",
    "magMouseTrackingMode",
    "magControlTrackingMode",
    "magTextTrackingMode",
    "magEdgeMargin",
    "magPointerFollowsFocus",
    "magPointerFollowsZoomer",
    "magColorFilteringMode",
    "magSourceDisplay",
    "magTargetDisplay",
    "verbalizePunctuationStyle",
    "showMainWindow",
    "quitOrcaNoConfirmation",
    "presentToolTips",
    "sayAllStyle",
    "keyboardLayout",
    "speakBlankLines",
    "speakMultiCaseStringsAsWords",
    "enabledSpokenTextAttributes",
    "enabledBrailledTextAttributes",
    "textAttributesBrailleIndicator",
    "enableProgressBarUpdates",
    "progressBarUpdateInterval",
    "progressBarVerbosity",
    "enableContractedBraille",
    "brailleContractionTable",
    "enableMouseReview",
    "mouseDwellDelay",
    "speakCellCoordinates",
    "speakCellSpan",
    "speakCellHeaders",
    "skipBlankCells",
    "largeObjectTextLength",
    "wrappedStructuralNavigation",
    "presentRequiredState",
    "brailleRequiredStateString",
    "speechRequiredStateString"
]

# The name of the module that hold the user interface for the main window
# for Orca. This module is expected to have two methods, showMainUI and
# hideMainUI, which will show and hide the main window GUI.
#
mainWindowModule = "orca_gui_main"

# The name of the modules that hold the user interface for setting
# Orca preferences.  Each module is expected to have the method,
# showPreferencesUI, which will prompt the user for preferences.
#
guiPreferencesModule     = "orca_gui_prefs"
consolePreferencesModule = "orca_console_prefs"
appGuiPreferencesModule  = "app_gui_prefs"

# The name of the module that hold the user interface for quitting Orca.
# This module is expected to have the method, showQuitUI, which will
# display the quit GUI.
#
quitModule = "orca_quit"

# The name of the module that holds the user interface for performing a
# flat review find.
#
findModule = "orca_gui_find"

# A list of keys that can serve as the Orca modifier key.  The list is
# so we can provide better cross platform support (e.g., Sun keyboard
# vs. PC-104 keyboard layouts).  When any of these keys is pressed,
# the orca.MODIFIER_ORCA bit will be set in the 'modifiers' field of
# a KeyboardEvent input event.  The keys are currently compared to the
# event_string of a keyboard input event from AT-SPI.
#
# The initial set of modifier keys is dependant upon whether the user
# has specified a desktop or a laptop keyboard layout.
#
DESKTOP_MODIFIER_KEYS = ["Insert", "KP_Insert"]
LAPTOP_MODIFIER_KEYS  = ["Caps_Lock"]
orcaModifierKeys      = DESKTOP_MODIFIER_KEYS

# A new modifier to use (set by the press of any key in the
# orcaModifierKeys list) to represent the Orca modifier.
#
MODIFIER_ORCA = 8

# Verbosity levels (see setBrailleVerbosityLevel and
# setSpeechVerbosityLevel).  These will have an impact on the various
# individual verbosity levels for rolenames, accelerators, etc.
#
VERBOSITY_LEVEL_BRIEF   = 0
VERBOSITY_LEVEL_VERBOSE = 1
speechVerbosityLevel    = VERBOSITY_LEVEL_VERBOSE
brailleVerbosityLevel   = VERBOSITY_LEVEL_VERBOSE

BRAILLE_ROLENAME_STYLE_SHORT = 0 # three letter abbreviations
BRAILLE_ROLENAME_STYLE_LONG  = 1 # full rolename
brailleRolenameStyle    = BRAILLE_ROLENAME_STYLE_LONG

# Roles to force to be displayed even when the verbosity level
# is not verbose.
#
brailleForceRoles = [pyatspi.ROLE_COMBO_BOX,
                     pyatspi.ROLE_MENU,
                     pyatspi.ROLE_TEAROFF_MENU_ITEM]

# Braille Selection Indicator (see brailleSelectorIndicator).
# The values represent the character to be used in the attrOr
# field of brlAPI's writeStruct.
#
BRAILLE_SEL_NONE = 0x00 # 00000000
BRAILLE_SEL_7    = 0x40 # 01000000
BRAILLE_SEL_8    = 0x80 # 10000000
BRAILLE_SEL_BOTH = 0xc0 # 11000000
brailleSelectorIndicator = BRAILLE_SEL_BOTH

# Braille Link Indicator (see brailleLinkIndicator).
# The values represent the character to be used in the attrOr
# field of brlAPI's writeStruct.
#
BRAILLE_LINK_NONE = 0x00 # 00000000
BRAILLE_LINK_7    = 0x40 # 01000000
BRAILLE_LINK_8    = 0x80 # 10000000
BRAILLE_LINK_BOTH = 0xc0 # 11000000
brailleLinkIndicator = BRAILLE_LINK_BOTH

# Braille alignment styles.  These say how to align text on the
# edges of the braille display.  The brailleAlignmentMargin value
# says how close to the edge of the braille the display the cursor
# cell can get.  The brailleMaximumJump says how far we can jump
# the display when aligning by word.
#
ALIGN_BRAILLE_BY_EDGE   = 0
ALIGN_BRAILLE_BY_MARGIN = 1
ALIGN_BRAILLE_BY_WORD   = 2
brailleAlignmentMargin  = 3
brailleMaximumJump      = 8
brailleAlignmentStyle   = ALIGN_BRAILLE_BY_EDGE

# Speech punctuation levels (see verbalizePunctuationStyle).
#
PUNCTUATION_STYLE_NONE = 3
PUNCTUATION_STYLE_SOME = 2
PUNCTUATION_STYLE_MOST = 1
PUNCTUATION_STYLE_ALL  = 0
verbalizePunctuationStyle = PUNCTUATION_STYLE_MOST

# Say All styles (see sayAllStyle).
#
SAYALL_STYLE_LINE     = 0
SAYALL_STYLE_SENTENCE = 1
sayAllStyle = SAYALL_STYLE_SENTENCE

# The absolue amount to change the speech rate when
# increasing or decreasing speech.  This is a numerical
# value that represents an ACSS rate value.
#
speechRateDelta         = 5

# The absolue amount to change the speech pitch when
# increasing or decreasing pitch.  This is a numerical
# value that represents an ACSS pitch value.
#
speechPitchDelta        = 0.5

# The port to listen on if orca is to act as an HTTP server
# (mainly as a speech server for self-voicing applications).
#
httpServerPort          = 0

# The number of attempts to retry setting up an HTTP server
# connection (each time incrementing the port number by 1).
#
maxHttpServerRetries    = 20

# Whether or not to use DBUS.
#
if os.getenv("DBUS_SESSION_BUS_ADDRESS"):
    useDBus = True
else:
    useDBus = False

# Whether or not recording is enabled via the HTTP server.
#
enableRemoteLogging     = False

# If True, enable speech.
#
enableSpeech            = True
enableSpeechCallbacks   = True

# If True, speech has been temporarily silenced.
#
silenceSpeech           = False

# Settings that apply to the particular speech engine to
# use as well details on the default voices to use.
#
speechFactoryModules    = ["espeechfactory", \
                           "gnomespeechfactory", \
                           "speechdispatcherfactory"]
speechServerFactory     = "gnomespeechfactory"
speechServerInfo        = None # None means let the factory decide.

DEFAULT_VOICE           = "default"
UPPERCASE_VOICE         = "uppercase"
HYPERLINK_VOICE         = "hyperlink"

voices = {
    DEFAULT_VOICE   : ACSS({}),
    UPPERCASE_VOICE : ACSS({ACSS.AVERAGE_PITCH : 5.6}),
    HYPERLINK_VOICE : ACSS({})
}

# If True, enable speaking of speech indentation and justification.
#
enableSpeechIndentation = False

# If True, enable braille.
#
enableBraille           = False

# If True, add the hierarchical context of an object to the braille
# line.  People with very large braille displays may want to set this
# to False.
#
enableBrailleContext    = True

# If True, enable the grouping of children on the braille display.
# This is for things like displaying all items of a menu, tab list,
# menu bar, etc., on a single line of the braille display.
#
enableBrailleGrouping   = False

# The timeout (in milliseconds) to use for messages flashed in braille.
#
brailleFlashTime        = 5000

# If True, enable braille monitor.
#
enableBrailleMonitor    = False

# If True, enable magnification.
#
enableMagnifier                  = False

# If True, changes made in the Magnifier pane will take place
# immediately (i.e. without pressing the apply button).  Making
# them permanent still requires pressing Apply or OK.
#
enableMagLiveUpdating            = True

# If True, show the magnification cursor.
#
enableMagCursor                  = True

# If True, allow an explicit size for the magnification cursor.
#
enableMagCursorExplicitSize      = False

# If True, hide the system cursor.
#
magHideCursor                    = False

# Size of the magnification cursor (in pixels).
#
magCursorSize                    = 32

# Magnification cursor color value (hex color spec).
#
magCursorColor                   = '#000000'

# If True, show the magnification cross-hairs.
#
enableMagCrossHair               = True

# If True, enable magnification cross-hair clipping.
#
enableMagCrossHairClip           = False

# Size of the magnification cross-hairs (in pixels).
#
magCrossHairSize                 = 16

# Magnification cross-hair color value (hex color spec).
#
magCrossHairColor                   = '#000000'

# Magnification Zoomer type.
#
MAG_ZOOMER_TYPE_FULL_SCREEN      = 0
MAG_ZOOMER_TYPE_TOP_HALF         = 1
MAG_ZOOMER_TYPE_BOTTOM_HALF      = 2
MAG_ZOOMER_TYPE_LEFT_HALF        = 3
MAG_ZOOMER_TYPE_RIGHT_HALF       = 4
MAG_ZOOMER_TYPE_CUSTOM           = 5
magZoomerType                    = MAG_ZOOMER_TYPE_FULL_SCREEN

# Magnification zoomer region placement.
#
magZoomerLeft                    = screenWidth / 2
magZoomerRight                   = screenWidth
magZoomerTop                     = 0
magZoomerBottom                  = screenHeight

# Magnification zoom factor.
#
magZoomFactor                    = 4.0

# If True, display a border around the magnification zoomer region.
#
enableMagZoomerBorder           = False

# The color and size of the border which separates the target
# display from the source display.
#
magZoomerBorderSize              = 1
magZoomerBorderColor             = '#000000'

# If True, invert the magnification zoomer colors.
#
enableMagZoomerColorInversion    = False

# The brightness levels.  The range is from -1 to 1, with 0
# being "normal"/no change.
#
magBrightnessLevel               = 0
magBrightnessLevelRed            = 0
magBrightnessLevelGreen          = 0
magBrightnessLevelBlue           = 0

# The contrast levels.  The range is from -1 to 1, with 0
# being "normal"/no change.
#
magContrastLevel                 = 0
magContrastLevelRed              = 0
magContrastLevelGreen            = 0
magContrastLevelBlue             = 0

# Magnification libcolorblind color filtering mode (see magColorFilteringMode).
#
MAG_COLOR_FILTERING_MODE_NONE                 = 0
MAG_COLOR_FILTERING_MODE_SATURATE_RED         = 1
MAG_COLOR_FILTERING_MODE_SATURATE_GREEN       = 2
MAG_COLOR_FILTERING_MODE_SATURATE_BLUE        = 3
MAG_COLOR_FILTERING_MODE_DESATURATE_RED       = 4
MAG_COLOR_FILTERING_MODE_DESATURATE_GREEN     = 5
MAG_COLOR_FILTERING_MODE_DESATURATE_BLUE      = 6
MAG_COLOR_FILTERING_MODE_POSITIVE_HUE_SHIFT   = 7
MAG_COLOR_FILTERING_MODE_NEGATIVE_HUE_SHIFT   = 8
magColorFilteringMode = MAG_COLOR_FILTERING_MODE_NONE

# Magnification smoothing mode (see magSmoothingMode).
#
MAG_SMOOTHING_MODE_BILINEAR      = 0
MAG_SMOOTHING_MODE_NONE          = 1
magSmoothingMode                 = MAG_SMOOTHING_MODE_BILINEAR

# Magnification tracking mode styles (see magMouseTrackingMode,
# magControlTrackingMode and magTextTrackingMode).
#
MAG_TRACKING_MODE_CENTERED     = 0
MAG_TRACKING_MODE_PROPORTIONAL = 1
MAG_TRACKING_MODE_PUSH         = 2
MAG_TRACKING_MODE_NONE         = 3

# To retain backward compatibility with previous versions of Orca.
#
MAG_MOUSE_TRACKING_MODE_CENTERED = MAG_TRACKING_MODE_CENTERED
MAG_MOUSE_TRACKING_MODE_PROPORTIONAL = MAG_TRACKING_MODE_PROPORTIONAL
MAG_MOUSE_TRACKING_MODE_PUSH = MAG_TRACKING_MODE_PUSH
MAG_MOUSE_TRACKING_MODE_NONE = MAG_TRACKING_MODE_NONE

# Magnification mouse tracking mode.
#
magMouseTrackingMode           = MAG_TRACKING_MODE_CENTERED

# Magnification control and menu item tracking mode.
#
magControlTrackingMode         = MAG_TRACKING_MODE_PUSH

# Magnification text cursor tracking mode.
#
magTextTrackingMode            = MAG_TRACKING_MODE_PUSH

# Magnification edge margin (percentage of screen).
#
magEdgeMargin                  = 0

# If enabled, automatically repositions the mouse pointer to the
# menu item or control with focus.
#
magPointerFollowsFocus         = False

# If enabled, automatically repositions the mouse pointer into the
# zoomer if it's not visible when initially moved.
#
magPointerFollowsZoomer        = True

# Magnification source display
#
magSourceDisplay                 = ''

# Magnification target display
#
magTargetDisplay                 = ''

# if True, enable character echo.
# Note that it is allowable for both enableEchoByCharacter and enableKeyEcho
# to be True
#
enableEchoByCharacter   = False

# if True, enable word echo.
# Note that it is allowable for both enableEchoByWord and enableKeyEcho
# to be True
#
enableEchoByWord        = False

# if True, enable word echo.
# Note that it is allowable for both enableEchoByWord and enableEchoBySentence
# to be True.
#
enableEchoBySentence    = False

# If True, enable key echo.
# Note that it is allowable for both enableEchoByWord and enableKeyEcho
# to be True
#
enableKeyEcho           = True

# If True and key echo is enabled, echo Alphanumeric and punctuation keys.
#
enablePrintableKeys     = True

# If True and key echo is enabled, echo Modifier keys.
#
enableModifierKeys      = True

# If True and key echo is enabled, echo Locking keys.
#
enableLockingKeys       = True

# If True and key echo is enabled, echo Function keys.
#
enableFunctionKeys      = True

# If True and key echo is enabled, echo Action keys.
#
enableActionKeys        = True

# If True and key echo is enabled, echo Navigation keys.
#
enableNavigationKeys    = False

# If True and key echo is enabled, echo Diacritical keys.
#
enableDiacriticalKeys   = False

# If True, tutorial strings defined will be spoken.
#
enableTutorialMessages = False

# If True, mnemonics will be spoken.
#
enableMnemonicSpeaking = False

# If true, position indexes  will be spoken automaticaly
#
enablePositionSpeaking = False

# If True, show the main Orca window.
#
showMainWindow          = True

# If True, quit Orca without confirmation when the user presses
# <Orca-modifier>-q.
#
quitOrcaNoConfirmation  = False

# Whether the user wants tooltips presented or not.
#
presentToolTips = False and canPresentToolTips

# Keyboard layout options (see keyboardLayout).
#
GENERAL_KEYBOARD_LAYOUT_DESKTOP = 1
GENERAL_KEYBOARD_LAYOUT_LAPTOP  = 2
keyboardLayout                  = GENERAL_KEYBOARD_LAYOUT_DESKTOP

# The red, green, blue values to use to outline the current item in
# flat review mode. They are values between 0 and 65535 (0xFFFF), with
# 65535 (0xFFFF) indicating full intensitiy
#
outlineColor = [ 0xFFFF, 0x0000, 0x0000 ]

# Thickness in pixels of the outline around the the current item in flat
# review mode.
#
outlineThickness = 4

# Margin between the object being outlined and the actual outline
#
outlineMargin = 1

# The kind of outlining to do for flat review mode.
#
OUTLINE_NONE = 0
OUTLINE_BOX = 1
OUTLINE_LINE = 2
OUTLINE_WEDGES = 3
outlineStyle = OUTLINE_BOX

# If True, speak blank lines.
#
speakBlankLines         = True

# if True, process multi case strings as words.
#
speakMultiCaseStringsAsWords = False

# If True, reads all the table cells in the current row rather than just
# the current one.
#
readTableCellRow    = True

# If True, enable speaking of progress bar updates.
#
enableProgressBarUpdates = True

# The interval (in seconds) between speaking progress bar updates. A value
# of zero means that progress bar updates should not be spoken at all.
#
progressBarUpdateInterval = 10

# When progress bar updates should be spoken, assuming they are enabled.
# ALL means that any progress bar update will be spoken. APPLICATION
# means that progress bar updates from the active application will be
# spoken, even if they are not in the active window. WINDOW means that
# the progress bar must be contained in the active window in order to
# be spoken. The default verbosity level is APPLICATION.
#
PROGRESS_BAR_ALL = 0
PROGRESS_BAR_APPLICATION = 1
PROGRESS_BAR_WINDOW = 2
progressBarVerbosity = PROGRESS_BAR_APPLICATION

# Whether or not to present the 'read only' attribute of text areas
# if we can detect they are read only or not.
#
presentReadOnlyText = True

# The complete list of possible text attributes.
#
allTextAttributes = \
    "bg-color:; bg-full-height:; bg-stipple:; direction:; editable:; " \
    "family-name:; fg-color:; fg-stipple:; font-effect:none; indent:0; " \
    "invisible:; justification:left; language:; left-margin:; " \
    "line-height:100%; paragraph-style:Default; pixels-above-lines:; " \
    "pixels-below-lines:; pixels-inside-wrap:; right-margin:; rise:; " \
    "scale:; size:; stretch:; strikethrough:false; style:normal; " \
    "text-decoration:none; text-rotation:0; text-shadow:none; " \
    "underline:none; variant:; vertical-align:baseline; weight:400; " \
    "wrap-mode:; writing-mode:lr-tb;"

# The default set of text attributes to speak to the user. Specific
# application scripts (or individual users can override these values if
# so desired. Each of these text attributes is of the form <key>:<value>;
# The <value> part will be the "default" value for that attribute. In
# other words, if the attribute for a given piece of text has that value,
# it won't be spoken. If no value part is given, then that attribute will
# always be spoken.

enabledSpokenTextAttributes = \
    "size:; family-name:; weight:400; indent:0; underline:none; " \
    "strikethrough:false; justification:left; style:normal; " \
    "paragraph-style:;"

# The default set of text attributes to be brailled for the user. Specific
# application scripts (or individual users can override these values if
# so desired. Each of these text attributes is of the form <key>:<value>;
# The <value> part will be the "default" value for that attribute. In
# other words, if the attribute for a given piece of text has that value,
# it won't be spoken. If no value part is given, then that attribute will
# always be brailled.

enabledBrailledTextAttributes = \
    "size:; family-name:; weight:400; indent:0; underline:none; " \
    "strikethrough:false; justification:left; style:normal;"

# Text Attributes Braille Indicator (see textAttributesBrailleIndicator).
# The values represent the character to be used in the attrOr
# field of brlAPI's writeStruct.
#
TEXT_ATTR_BRAILLE_NONE = 0x00 # 00000000
TEXT_ATTR_BRAILLE_7    = 0x40 # 01000000
TEXT_ATTR_BRAILLE_8    = 0x80 # 10000000
TEXT_ATTR_BRAILLE_BOTH = 0xc0 # 11000000
textAttributesBrailleIndicator = TEXT_ATTR_BRAILLE_NONE

# The limit to enable a repeat character count to be spoken.
# If set to 0, then there will be no repeat character count.
# Each character will be spoken singularly (i.e. "dash dash
# dash dash dash" instead of "five dash characters").
# If the value is set to 1, 2 or 3 then it's treated as if it was
# zero. In other words, no repeat character count is given.
#
repeatCharacterLimit = 4

# Tags associated with ARIA landmarks.
#
ariaLandmarks = [
    "application",
    "article",
    "banner",
    "complementary",
    "contentinfo",
    "definition",
    "directory",
    "document",
    "grid",
    "log",
    "main",
    "menubar",
    "navigation",
    "note",
    "region",
    "search",
    "secondary",
    "seealso",
    "status",
]

# Script developer feature.  If False, just the default script
# will be used.  Helps determine difference between custom
# scripts and the default script behavior.
#
enableCustomScripts     = True

# Latent support to allow the user to override/define keybindings
# and braille bindings.  Unsupported and undocumented for now.
# Use at your own risk.
#
keyBindingsMap          = {}
brailleBindingsMap      = {}

# Script developer feature.  If False, no AT-SPI object values
# will be cached locally.  Helps determine if there might be a
# problem related to the cache being out of sync with the real
# objects.
#
cacheValues             = True
cacheDescriptions       = True

# Script developer feature.  If False, no AT-SPI objects
# will be cached locally.  Helps determine if there might be a
# problem related to the cache being out of sync with the real
# objects.
#
cacheAccessibles        = True

# Assists with learn mode (what you enter when you press Insert+F1
# and exit when you press escape.
#
learnModeEnabled        = False

# The location of the user's preferences. By default this is ~/.orca.
# It can be overridden by the Orca -d command line option.
#
userPrefsDir = os.path.join(os.environ["HOME"], ".orca")

# Assists with dealing with CORBA COMM_FAILURES.  A failure doesn't
# always mean an object disappeared - there just might be a network
# glitch.  So, on COMM_FAILURES, we might retry a few times before
# giving up on an object.  This might need to be overridden by the
# script.
#
commFailureWaitTime = 0.1
commFailureAttemptLimit = 5

# If non-zero, we use time.sleep() in various places to attempt to
# free up the global interpreter lock.  Take a look at the following
# URLs for more information:
#
# http://mail.python.org/pipermail/python-list/2002-October/126632.html
# http://twistedmatrix.com/pipermail/twisted-python/2005-July/011052.html
# http://www.pyzine.com/Issue001/Section_Articles/ \
#                                 article_ThreadingGlobalInterpreter.html
#
gilSleepTime            = 0.00001

# The value of the 'gil' parameter in the call to pyatspi.Registry.start
# See http://bugzilla.gnome.org/show_bug.cgi?id=576954.
#
useGILIdleHandler       = False

# If True, use the gidle __blockPreventor() code in atspi.py.
#
useBlockPreventor       = False

# If True, we use the bonobo main loop provided by bonobo to handle
# all events in atspi.py.  If False, we create our own loop.
#
useBonoboMain           = True

# If True, we handle events asynchronously - our normal mode of
# queueing events and processing them later on the gidle thread.
# If False, we handle events immediately - helpful for testing.
#
asyncMode               = True

# A list of toolkits whose events we need to process synchronously.
# The only one right now is the Java toolkit (see bug #531869), but
# we put this here to allow more toolkits to be more easily added
# and for Java to be removed if issues with asynchronous processing
# of its events are ever resolved.
#
synchronousToolkits     = ["J2SE-access-bridge"]

# If True, we output debug information for the event queue.  We
# use this in addition to log level to prevent debug logic from
# bogging down event handling.
#
debugEventQueue         = False

# If True, we collect information regarding memory usage and provide
# keystrokes to dump the usage information to the console:
# Orca+Ctrl+F8 for brief, Orca+Shift+Ctrl+F8 for detailed.
#
debugMemoryUsage        = False

# The timeout value (in seconds) and callback used to determine if
# Orca has hung or not.  The only setting one should muck with here is
# the timeoutTime unless you want to create a custom callback handler
# for the timeout.  See braille.py, atspi.py, and orca.py:init for how
# these are used.
#
timeoutTime             = 10   # a value of 0 means don't do hang checking
timeoutCallback         = None # Set by orca.py:init to orca.timeout

# Keyboard double-click period. If the same key is pressed within
# this time period, it's considered to be a double-click and might
# provide different functionality (for example, Numpad 5 double-click
# spells the current word rather than speaks it).
#
doubleClickTimeout = 0.5

# Obtain/set information regarding whether accessibility is enabled
# or not.
#
def isAccessibilityEnabled():
    try:
        return gconfClient.get_bool("/desktop/gnome/interface/accessibility")
    except:
        return False

def setAccessibilityEnabled(enable):
    try:
        return gconfClient.set_bool("/desktop/gnome/interface/accessibility",
                                    enable)
    except:
        return False

# Obtain/set information regarding whether Orca is autostarted for this
# user at login time.
#
def isOrcaAutostarted():
    """Return an indication of whether Orca autostart at login time is enabled.
    """
    prefix = "/desktop/gnome/applications/at/visual/"
    try:
        return ("orca" in gconfClient.get_string(prefix + "exec")) \
           and gconfClient.get_bool(prefix + "startup")
    except:
        return False

def setOrcaAutostart(enable):
    """Enable or disable the autostart of Orca at login time.

    Arguments:
    - enable: if True, whether Orca autostart at login time is enabled.

    Returns an indication of whether the operation was successful.
    """
    prefix = "/desktop/gnome/applications/at/visual/"
    try:
        return gconfClient.set_string(prefix + "exec", "orca") \
           and gconfClient.set_bool(prefix + "startup", enable)
    except:
        return False

# Obtain/set information regarding whether the gksu keyboard grab is enabled
# or not.
#
def isGKSUGrabDisabled():
    try:
        return gconfClient.get_bool("/apps/gksu/disable-grab")
    except:
        return False

def setGKSUGrabDisabled(disable):
    try:
        return gconfClient.set_bool("/apps/gksu/disable-grab",
                                    disable)
    except:
        return False

# Allow for the customization of key bindings.
#
def overrideKeyBindings(script, keyBindings):
    return keyBindings

# Allow for user customization of pronunciations.
#
def overridePronunciations(script, pronunciations):
    return pronunciations

# Which packages to search, and the order in which to search,
# for application settings.  These packages are expected to be on
# the PYTHONPATH and/or subpackages of the "orca" package.
# REMEMBER: to make something a package, the directory has to
# have a __init__.py file in it.
#
settingsPackages          = ["app-settings"]

# Which packages to search, and the order in which to search,
# for custom scripts.  These packages are expected to be on
# the PYTHONPATH and/or subpackages of the "orca" package.
# REMEMBER: to make something a package, the directory has to
# have a __init__.py file in it.
#
scriptPackages          = ["orca-scripts", "scripts",
                           "scripts.apps", "scripts.toolkits"]

# A list that helps us map application names to script module
# names.  The key is the name of an application, and the value is
# the name of a script module.  There are some default values here,
# but one may call the setScriptMapping method of this module to
# extend or override any mappings.
#
_scriptMappings = []

def setScriptMapping(regExpression, moduleName):
    """Tells this module what script module to look for a given
    application name.  The mappings are stored as a list and each
    new mapping is added to the beginning of the list, meaning it
    takes precedence over all other mappings.

    Arguments:
    - regExpression: a regular expression used to match against an
                     application name
    - moduleName:    the name of the Python module containing the script
                     class definition for the application
    """

    _scriptMappings.insert(0, [regExpression, moduleName])

def getScriptModuleName(app):
    """Returns the module name of the script to use for a given
    application.  Any script mapping set via the setScriptMapping
    method is searched first, with the ultimate fallback being the
    name of the application itself.

    Arguments:
    - app: the application to find a script module name for
    """

    if not app.name:
        return None

    for mapping in _scriptMappings:
        regExpression = mapping[0]
        moduleName = mapping[1]
        if regExpression.match(app.name):
            debug.println(
                debug.LEVEL_FINEST,
                "Script mapping for %s is %s" % (app.name, moduleName))
            return moduleName

    return app.name

# Translators: the regular expression here represents a string to
# match in the localized application name as seen by at-poke.  For
# most cases, the application name is the name of the binary used to
# start the application, but this is an unreliable assumption.  The
# only reliable way to do the translation is by running the
# application and then viewing its name in the main window of at-poke.
# I wish the AT-SPI spec'd this out as machine readable (unlocalized)
# names, but it's what we're stuck with (unfortunately).
#
setScriptMapping(re.compile(_('[\S\s]*StarOffice[\s\S]*')), "soffice")

# Translators: see the regular expression note above.  This is for
# OpenOffice and StarOffice.
#
setScriptMapping(re.compile(_('soffice.bin')), "soffice")

# Translators: see the regular expression note above.  This is for
# OpenOffice and StarOffice.
#
setScriptMapping(re.compile(_('soffice')), "soffice")

# Translators: see the regular expression note above.  This is for the
# Evolution mail application.
#
setScriptMapping(re.compile(_('[Ee]volution')), "evolution")

# Translators: see the regular expression note above.  This is for a
# version of Mozilla Firefox, which chooses to create strange names
# for itself at the drop of a hat.
#
setScriptMapping(re.compile(_('Deer Park')), "Mozilla")

# Translators: see the regular expression note above.  This is for a
# version of Mozilla Firefox, which chooses to create strange names
# for itself at the drop of a hat.
#
setScriptMapping(re.compile(_('Bon Echo')), "Mozilla")

# Translators: see the regular expression note above.  This is for a
# version of Mozilla Firefox, which chooses to create strange names
# for itself at the drop of a hat.
#
setScriptMapping(re.compile(_('Minefield')), "Mozilla")

# Translators: see the regular expression note above.  This is for a
# version of Mozilla Firefox, which chooses to create strange names
# for itself at the drop of a hat. [[[TODO - JD: Not marked for
# translation due to string freeze. I'm not convinced it needs to
# be translated either.]]]
#
#setScriptMapping(re.compile(_('Shiretoko')), "Mozilla")
setScriptMapping(re.compile('Shiretoko'), "Mozilla")

# This is a temporary fix for the schema/FF 3.0 not being accessible
# issue. (See GNOME bugs #535827 and #555466.)
#
setScriptMapping(re.compile('[Ff]irefox'), "Mozilla")

# Translators: see the regular expression note above.  This is for a
# version of Thunderbird, which chooses to now call itself by a different
# name.
#
#setScriptMapping(re.compile(_('Shredder')), "Thunderbird")
#
# Don't localize this. It seems to be messing us up. See bug 584103.
#
setScriptMapping(re.compile('Shredder'), "Thunderbird")

# Translators: see the regular expression note above.  This is for
# the Thunderbird e-mail application.
#
setScriptMapping(re.compile(_('Mail/News')), "Thunderbird")

# Translators: see the regular expression note above.  This is for
# gnome_segv2, which calls itself bug-buddy in at-poke.
#
setScriptMapping(re.compile(_('bug-buddy')), "gnome_segv2")

# Translators: see the regular expression note above.  This is for
# the underlying terminal support in gnome-terminal.
#
setScriptMapping(re.compile(_('vte')), "gnome-terminal")

# Translators: see the regular expression note above.  This is for
# supporting gaim, which has recently be renamed to pidgin.
#
setScriptMapping(re.compile(_('gaim')), "pidgin")
setScriptMapping(re.compile('Pidgin'), "pidgin")

# Translators: see the regular expression note above.  This is for
# supporting yelp, which sometimes identifies itself as gnome-help.
# [[[TODO - JD: Not marked for translation due to string freeze,
# plus gnome-help doesn't translate its app name as far as we can
# determine.  So, translating this string really seems like extra
# busy work for our translators.]]]
#
#setScriptMapping(re.compile(_('gnome-help')), "yelp")
setScriptMapping(re.compile('gnome-help'), "yelp")

# Strip off the extra 'py' that the Device Driver Utility includes
# as part of its accessible name.
#
setScriptMapping(re.compile('ddu.py'), "ddu")

# Show deprecated messeges in debug output.
# Set this to True to help find potential pyatspi porting problems
#
deprecatedMessages = False

# Focus history length. We keep a reference to past focused accessibles to
# maximize on caching.
#
focusHistoryLength = 5

# Listen to all AT-SPI events, regardless to if we are using them or not.
# This is useful for development and debugging.
#
listenAllEvents = False

# This is a list of events that Orca should immidiately drop and never look at.
#
ignoredEventsList = ['object:bounds-changed']

# Listen to Live Region events.  Tells Gecko.onChildrenChanged() and
# onTextInserted() event handlers to monitor these events for live region
# changes.
#
inferLiveRegions = True

# Contracted braille support.
#
enableContractedBraille = False

# Contracted braille table.
#
brailleContractionTable = ''

# Use Collection Interface?
#
useCollection = True

# Whether or not to speak the cell's coordinates when navigating
# from cell to cell in a table.
#
speakCellCoordinates = True

# Whether or not to speak the number of cells spanned by a cell
# that occupies more than one row or column of a table.
#
speakCellSpan = True

# Whether or not to announce the header that applies to the current
# when navigating from cell to cell in a table.
#
speakCellHeaders = True

# Whether blank cells should be skipped when navigating in a table
# using table navigation commands.
#
skipBlankCells = False

# The minimum size in characters to be considered a "large object"
# or "chunk" for structural navigation.
#
largeObjectTextLength = 75

# Whether to wrap around the document when structural navigation is used.
wrappedStructuralNavigation = True

# Report object under mouse.
#
enableMouseReview = False

# Mouse dwell delay in milliseconds for mouse review mode.
# If the value is zero, the review will be read time.
#
mouseDwellDelay = 0

# Maximum allowed drift while pointer is dwelling in mouse review mode.
#
mouseDwellMaxDrift = 3

# The different modifiers/modifier masks associated with keybindings
#
NO_MODIFIER_MASK              =  0
ALT_MODIFIER_MASK             =  1 << pyatspi.MODIFIER_ALT
CTRL_MODIFIER_MASK            =  1 << pyatspi.MODIFIER_CONTROL
ORCA_MODIFIER_MASK            =  1 << MODIFIER_ORCA
ORCA_ALT_MODIFIER_MASK        = (1 << MODIFIER_ORCA |
                                 1 << pyatspi.MODIFIER_ALT)
ORCA_CTRL_MODIFIER_MASK       = (1 << MODIFIER_ORCA |
                                 1 << pyatspi.MODIFIER_CONTROL)
ORCA_CTRL_ALT_MODIFIER_MASK   = (1 << MODIFIER_ORCA |
                                 1 << pyatspi.MODIFIER_CONTROL |
                                 1 << pyatspi.MODIFIER_ALT)
ORCA_SHIFT_MODIFIER_MASK      = (1 << MODIFIER_ORCA |
                                 1 << pyatspi.MODIFIER_SHIFT)
SHIFT_MODIFIER_MASK           =  1 << pyatspi.MODIFIER_SHIFT
SHIFT_ALT_MODIFIER_MASK       = (1 << pyatspi.MODIFIER_SHIFT |
                                 1 << pyatspi.MODIFIER_ALT)
COMMAND_MODIFIER_MASK         = (1 << pyatspi.MODIFIER_ALT |
                                 1 << pyatspi.MODIFIER_CONTROL |
                                 1 << pyatspi.MODIFIER_META2 |
                                 1 << pyatspi.MODIFIER_META3)
NON_LOCKING_MODIFIER_MASK     = (1 << pyatspi.MODIFIER_SHIFT |
                                 1 << pyatspi.MODIFIER_ALT |
                                 1 << pyatspi.MODIFIER_CONTROL |
                                 1 << pyatspi.MODIFIER_META2 |
                                 1 << pyatspi.MODIFIER_META3 |
                                 1 << MODIFIER_ORCA)
ALL_BUT_NUMLOCK_MODIFIER_MASK = (1 << MODIFIER_ORCA |
                                 1 << pyatspi.MODIFIER_SHIFT |
                                 1 << pyatspi.MODIFIER_SHIFTLOCK |
                                 1 << pyatspi.MODIFIER_CONTROL |
                                 1 << pyatspi.MODIFIER_ALT |
                                 1 << pyatspi.MODIFIER_META2 |
                                 1 << pyatspi.MODIFIER_META3)

# The 2nd parameter used when creating a keybinding refers to the
# modifiers "we care about."  We typically care about all of the
# modifiers which are not locking keys because we want to avoid
# conflicts with other commands, such as Orca's command for moving
# among headings (H) and the Help menu (Alt+H).
#
defaultModifierMask = NON_LOCKING_MODIFIER_MASK

# Whether or not we should present objects with STATE_REQUIRED to
# the user. Currently, this is only seen with ARIA widgets.
#
presentRequiredState = False

########################################################################
#                                                                      #
# Sounds                                                               #
#                                                                      #
########################################################################

# A dictionary where the keys are rolenames and the values are
# filenames containing audio snippets.
#
sounds = {}

########################################################################
#                                                                      #
# Strings for speech and braille                                       #
#                                                                      #
########################################################################

# Translators: "blank" is a short word to mean the
# user has navigated to an empty line.
#
speechBlankString = _("blank")

# Translators: Certain objects (such as form controls on web pages)
# can have STATE_REQUIRED set on them to inform the user that this
# field must be filled out. This string is the default string which
# will be spoken and displayed in braille to indicate this state is
# present.
#
speechRequiredStateString = _("required")

# Translators: this is used to indicate the user is in a text
# area that is not editable.  It is meant to be spoken to the user.
#
speechReadOnlyString = C_("text", "read only")

# Translators: this represents an item on the screen that has
# been set insensitive (or grayed out).
#
speechInsensitiveString = _("grayed")

# Translators: this represents the state of a checkbox.  It is meant
# to be spoken to the user.
#
speechCheckboxIndicators = [_("not checked"),
                            _("checked"),
                            _("partially checked")]

# Translators: this represents the state of a radio button.  It is
# meant to be spoken to the user.
#
speechRadioButtonIndicators = [C_("radiobutton", "not selected"),
                               C_("radiobutton", "selected")]

# Translators: this represents the state of a toggle button.  It is
# meant to be spoken to the user.
#
speechToggleButtonIndicators = [_("not pressed"), _("pressed")]

# Translators: this represents the state of a node in a tree.
# 'expanded' means the children are showing.  'collapsed' means the
# children are not showing.
#
speechExpansionIndicators = [_("collapsed"), _("expanded")]

# Translators: "multi-select" refers to a web form list
# in which more than one item can be selected at a time.
#
speechMultiSelectString = _("multi-select")

# Translators: this represents the depth of a node in a tree
# view (i.e., how many ancestors a node has).  It is meant to be
# spoken.
#
speechNodeLevelString = _("tree level %d")

# Translators: this represents a list item in a document.
# The nesting level is how 'deep' the item is (e.g., a
# level of 2 represents a list item inside a list that's
# inside another list). This is meant to be spoken.
#
speechNestingLevelString = _("Nesting level %d")

# Translators: this is a indication of the focused icon and the
# count of the total number of icons within an icon panel. An
# example of an icon panel is the Nautilus folder view.
#
speechIconIndexString = _("on %(index)d of %(total)d")

# Translators: this refers to the position of an item in a list
# or group of objects, such as menu items in a menu, radio buttons
# in a radio button group, combobox item in a combobox, etc.
#
speechGroupIndexString = _("%(index)d of %(total)d")

# string to indicate end of printed line for braille displays:
#
disableBrailleEOL = False
brailleEOLIndicator = " $l"

# Translators: Certain objects (such as form controls on web pages)
# can have STATE_REQUIRED set on them to inform the user that this
# field must be filled out. This string is the default string which
# will be spoken and displayed in braille to indicate this state is
# present.
#
brailleRequiredStateString = _("required")

# Translators: this is used to indicate the user is in a text
# area that is not editable.  It is meant to be a short abbreviation
# to be presented on the braille display.
#
brailleReadOnlyString = C_("text", "rdonly")

# Translators: this represents an item on the screen that has
# been set insensitive (or grayed out).
#
brailleInsensitiveString = _("grayed")

# Strings used to indicate checkbox/radio button states in braille:
#
brailleCheckBoxIndicators = ["< >", "<x>", "<->"]
brailleRadioButtonIndicators = ["& y", "&=y"]
brailleToggleButtonIndicators = ["& y", "&=y"]

# Translators: this represents the state of a node in a tree.
# 'expanded' means the children are showing.  'collapsed' means the
# children are not showing.
#
brailleExpansionIndicators = [_("collapsed"), _("expanded")]

# Translators: this represents the depth of a node in a tree
# view (i.e., how many ancestors a node has).  It is meant to
# be presented on a braille display.
#
brailleNodeLevelString = _("TREE LEVEL %d")

# Translators: this represents a list item in a document.
# The nesting level is how 'deep' the item is (e.g., a
# level of 2 represents a list item inside a list that's
# inside another list).  It is meant to be presented on
# the braille display.
#
brailleNestingLevelString = _("LEVEL %d")

# String for delimiters between table cells
#
brailleTableCellDelimiter = " "

# This is for bug #585417 - Allow pauses to be inserted into speech
# output. We're keeping it separate for now until we get the pauses
# sorted out just right.
#
useExperimentalSpeechProsody = True

# If True, whenever a 'pause' keyword is found in a speech formatting
# string, any string being created will be sent to the speech synthesis
# system immediately.  This is for bug #585417 and allows for some
# adaptation to how different systems handle queued speech.  For example,
# some introduce unnaturally long pauses between requests to speak.
#
enablePauseBreaks = True
