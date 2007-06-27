# Orca
#
# Copyright 2004-2007 Sun Microsystems Inc.
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

"""Manages the settings for Orca.  This will defer to user settings first, but
fallback to local settings if the user settings doesn't exist (e.g., in the
case of gdm) or doesn't have the specified attribute."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2007 Sun Microsystems Inc."
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

    # We want to know what the tty is so we can send it to BrlAPI
    # if possible.
    #
    (atom, format, data) = _root_window.property_get("XFree86_VT")
    tty = data[0]

    # The bug that caused gnome-panel to crash is fixed in GTK 2.10.11.
    minimum_gtk_version = (100000 * 2) + \
                          (1000 * 10) + \
                           11
    current_gtk_version  = (100000 * gtk.gtk_version[0]) + \
                           (1000 * gtk.gtk_version[1]) + \
                            gtk.gtk_version[2]
    canPresentToolTips = (current_gtk_version >= minimum_gtk_version)
except:
    pass

try:
    import gconf
    gconfClient = gconf.client_get_default()
except:
    gconfClient = None

import debug
from acss import ACSS
from orca_i18n import _           # for gettext support

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
    "enableEchoByWord",
    "enableKeyEcho",
    "enablePrintableKeys",
    "enableModifierKeys",
    "enableLockingKeys",
    "enableFunctionKeys",
    "enableActionKeys",
    "enableBraille",
    "enableBrailleGrouping",
    "brailleVerbosityLevel",
    "brailleRolenameStyle",
    "enableBrailleMonitor",
    "enableMagnifier",
    "enableMagCursor",
    "enableMagCursorExplicitSize",
    "magCursorSize",
    "magCursorColor",
    "enableMagCrossHair",
    "enableMagCrossHairClip",
    "magCrossHairSize",
    "magZoomerLeft",
    "magZoomerRight",
    "magZoomerTop",
    "magZoomerBottom",
    "magZoomFactor",
    "enableMagZoomerColorInversion",
    "magSmoothingMode",
    "magMouseTrackingMode",
    "magSourceDisplay",
    "magTargetDisplay",
    "verbalizePunctuationStyle",
    "showMainWindow",
    "quitOrcaNoConfirmation",
    "presentToolTips",
    "sayAllStyle",
    "keyboardLayout",
    "speakBlankLines",
    "enabledTextAttributes",
    "enableProgressBarUpdates",
    "progressBarUpdateInterval"
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
guiPreferencesModule    = "orca_gui_prefs"
consolePreferencesModule= "orca_console_prefs"
appGuiPreferencesModule = "app_gui_prefs"

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
httpServerPort          = 20433

# The number of attempts to retry setting up an HTTP server
# connection (each time incrementing the port number by 1).
#
maxHttpServerRetries   = 20

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
speechFactoryModules    = ["espeechfactory","gnomespeechfactory","speechdispatcherfactory"]
speechServerFactory     = "gnomespeechfactory"
speechServerInfo        = None # None means let the factory decide.

DEFAULT_VOICE           = "default"
UPPERCASE_VOICE         = "uppercase"
HYPERLINK_VOICE         = "hyperlink"

voices = {
    DEFAULT_VOICE   : ACSS({}),
    UPPERCASE_VOICE : ACSS({ACSS.AVERAGE_PITCH : 6}),
    HYPERLINK_VOICE : ACSS({})
}

# If True, enable speaking of speech indentation and justification.
#
enableSpeechIndentation = False

# If True, enable braille.
#
enableBraille           = True

# If True, enable the grouping of children on the braille display.
# This is for things like displaying all items of a menu, tab list,
# menu bar, etc., on a single line of the braille display.
#
enableBrailleGrouping   = False

# If True, enable braille monitor.
#
enableBrailleMonitor    = False

# Strings used to indicate checkbox/radio button states in braille:
#
brailleCheckBoxIndicators = ["< >", "<x>"]
brailleRadioButtonIndicators = ["& y", "&=y"]

# If True, enable magnification.
#
enableMagnifier                  = False

# If True, show the magnification cursor.
#
enableMagCursor                  = True

# If True, allow an explicit size for the magnification cursor.
#
enableMagCursorExplicitSize      = False

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

# Magnification zoomer region placement.
#
magZoomerLeft                    = screenWidth / 2
magZoomerRight                   = screenWidth
magZoomerTop                     = 0
magZoomerBottom                  = screenHeight

# Magnification zoom factor.
#
magZoomFactor                    = 4.0

# If True, invert the magnification zoomer colors.
#
enableMagZoomerColorInversion    = False

# Magnification smoothing mode (see magSmoothingMode).
#
MAG_SMOOTHING_MODE_BILINEAR      = 0
MAG_SMOOTHING_MODE_NONE          = 1
magSmoothingMode                 = MAG_SMOOTHING_MODE_BILINEAR

# Magnification mouse tracking mode (see magMouseTrackingMode).
#
MAG_MOUSE_TRACKING_MODE_CENTERED     = 0
MAG_MOUSE_TRACKING_MODE_NONE         = 1
MAG_MOUSE_TRACKING_MODE_PROPORTIONAL = 2
MAG_MOUSE_TRACKING_MODE_PUSH         = 3
magMouseTrackingMode                 = MAG_MOUSE_TRACKING_MODE_CENTERED

# Magnification source display
#
magSourceDisplay                 = ''

# Magnification target display
#
magTargetDisplay                 = ''

# if True, enable word echo.
# Note that it is allowable for both enableEchoByWord and enableKeyEcho
# to be True
#
enableEchoByWord        = False

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

# If True, speak blank lines.
#
speakBlankLines         = True

# If True, reads all the table cells in the current row rather than just
# the current one.
#
readTableCellRow    = True

# If True, enable speaking of progress bar updates.
#
enableProgressBarUpdates = False

# The interval (in seconds) between speaking progress bar updates. A value
# of zero means that progress bar updates should not be spoken at all.
#
progressBarUpdateInterval = 10

# The complete list of possible text attributes.
#
allTextAttributes = "bg-color:; bg-full-height:; bg-stipple:; direction:; editable:; family-name:; fg-color:; fg-stipple:; font-effect:none; indent:0; invisible:; justification:left; language:; left-margin:; line-height:100%; paragraph-style:Default; pixels-above-lines:; pixels-below-lines:; pixels-inside-wrap:; right-margin:; rise:; scale:; size:; stretch:; strikethrough:false; style:normal; text-decoration:none; text-rotation:0; text-shadow:none; underline:none; variant:; vertical-align:baseline; weight:400; wrap-mode:; writing-mode:lr-tb;"

# The default set of text attributes to speak to the user. Specific
# application scripts (or individual users can override these values if
# so desired. Each of these text attributes is of the form <key>:<value>;
# The <value> part will be the "default" value for that attribute. In
# other words, if the attribute for a given piece of text has that value,
# it won't be spoken. If no value part is given, then that attribute will
# always be spoken.

enabledTextAttributes = "size:; family-name:; weight:400; indent:0; underline:none; strikethrough:false; justification:left; style:normal;"

# The limit to enable a repeat character count to be spoken.
# If set to 0, then there will be no repeat character count.
# Each character will be spoken singularly (i.e. "dash dash
# dash dash dash" instead of "five dash characters").
# If the value is set to 1, 2 or 3 then it's treated as if it was
# zero. In other words, no repeat character count is given.
#
repeatCharacterLimit = 4

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

# If non-zero, we use time.sleep() in various places to attempt to
# free up the global interpreter lock.  Take a look at the following
# URLs for more information:
#
# http://mail.python.org/pipermail/python-list/2002-October/126632.html
# http://twistedmatrix.com/pipermail/twisted-python/2005-July/011052.html
# http://www.pyzine.com/Issue001/Section_Articles/article_ThreadingGlobalInterpreter.html
#
gilSleepTime            = 0.00001

# If True, use the gidle __blockPreventor() code in atspi.py.
#
useBlockPreventor       = False

# If True, we use the bonobo main loop provided by bonobo to handle
# all events in atspi.py.  If False, we create our own loop.
#
useBonoboMain           = True

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
scriptPackages          = ["orca-scripts", "scripts"]

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
setScriptMapping(re.compile(_('[\S\s]*StarOffice[\s\S]*')), "StarOffice")

# Translators: see the regular expression note above.  This is for
# OpenOffice and StarOffice.
#
setScriptMapping(re.compile(_('soffice.bin')), "StarOffice")

# Translators: see the regular expression note above.  This is for the
# Evolution mail application.
#
setScriptMapping(re.compile(_('[Ee]volution')), "Evolution")

# Translators: see the regular expression note above.  This is for the
# help application (yelp).
#
setScriptMapping(re.compile(_('yelp')), "Mozilla")

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
# supporting pidgin, which is the new name for gaim.
#
setScriptMapping(re.compile(_('pidgin')), "gaim")
