# Orca
#
# Copyright 2004-2005 Sun Microsystems Inc.
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
case of gdm) or doesn't have the specified attribute.
"""

import re
import sys

import debug
from acss import ACSS
from orca_i18n import _           # for gettext support

#########################################################################
#                                                                       #
# String constants and default values for the common attributes.        #
#                                                                       #
#########################################################################

# Verbosity levels (see setBrailleVerbosityLevel and
# setSpeechVerbosityLevel).  These will have an impact on the various
# individual verbosity levels for rolenames, accelerators, etc.
#
BRAILLE_VERBOSITY_LEVEL = "brailleVerbosityLevel"
SPEECH_VERBOSITY_LEVEL  = "speechVerbosityLevel"
VERBOSITY_LEVEL_BRIEF   = 0
VERBOSITY_LEVEL_VERBOSE = 1
speechVerbosityLevel    = VERBOSITY_LEVEL_VERBOSE
brailleVerbosityLevel   = VERBOSITY_LEVEL_VERBOSE

BRAILLE_ROLENAME_STYLE  = "brailleRolenameStyle"
BRAILLE_ROLENAME_STYLE_SHORT = 0 # three letter abbreviations
BRAILLE_ROLENAME_STYLE_LONG  = 1 # full rolename
brailleRolenameStyle    = BRAILLE_ROLENAME_STYLE_LONG

# The absolue amount to change the speech rate when
# increasing or decreasing speech.  This is a numerical
# value that represents an ACSS rate value.
#
SPEECH_RATE_DELTA       = "speechRateDelta"
speechRateDelta         = 5

# If True, use speech.
#
USE_SPEECH              = "useSpeech"
useSpeech               = True

# Settings that apply to the particular speech engine to
# use as well details on the default voices to use.
#
SPEECH_FACTORY_MODULES  = "speechFactoryModules"
speechFactoryModules    = ["espeechfactory","gnomespeechfactory"]

SPEECH_SERVER_FACTORY   = "speechServerFactory"
speechServerFactory     = "gnomespeechfactory"

SPEECH_SERVER_INFO      = "speechServerInfo"
speechServerInfo        = None # None means let the factory decide.

DEFAULT_VOICE           = "default"
UPPERCASE_VOICE         = "uppercase"
HYPERLINK_VOICE         = "hyperlink"

VOICES                  = "voices"
voices = {
    DEFAULT_VOICE   : ACSS({}),
    UPPERCASE_VOICE : ACSS({ACSS.AVERAGE_PITCH : 6}),
    HYPERLINK_VOICE : ACSS({ACSS.AVERAGE_PITCH : 8})
}

# If True, use braille.
#
USE_BRAILLE             = "useBraille"
useBraille              = True

# If True, use braille monitor.
#
USE_BRAILLE_MONITOR     = "useBrailleMonitor"
useBrailleMonitor       = False

# If True, use magnification.
#
USE_MAGNIFIER           = "useMagnifier"
useMagnifier            = False

# if True, echo keys by word.
# Note that it is allowable for both useEchoByWord and useEchoByChar to be True
#
USE_ECHO_BY_WORD        = "useEchoByWord"
useEchoByWord           = False

# if True, echo keys by character.
# Note that it is allowable for both useEchoByWord and useEchoByChar to be True
#
USE_ECHO_BY_CHAR        = "useEchoByChar"
useEchoByChar           = False

# If True, reads all the table cells in the current row rather than just
# the current one.
#
READ_TABLE_CELL_ROW     = "readTableCellRow"
readTableCellRow        = False

# Script developer feature.  If False, just the default script
# will be used.  Helps determine difference between custom
# scripts and the default script behavior.
#
USE_CUSTOM_SCRIPTS      = "speechVerbosityLevel"
useCustomScripts        = True

# Latent support to allow the user to override/define keybindings
# and braille bindings.  Unsupported and undocumented for now.
# Use at your own risk.
#
KEY_BINDINGS_MAP        = "keyBindingsMap"
keyBindingsMap          = {}

BRAILLE_BINDINGS_MAP    = "brailleBindingsMap"
brailleBindingsMap      = {}

# Script developer feature.  If False, no AT-SPI object values
# will be cached locally.  Helps determine if there might be a
# problem related to the cache being out of sync with the real
# objects.
#
CACHE_VALUES            = "cacheValues"
cacheValues             = False

# Assists with learn mode (what you enter when you press Insert+F1
# and exit when you press escape.
#
LEARN_MODE_ENABLED      = "learnModeEnabled"
learnModeEnabled        = False

_userSettings = None

def setLearnModeEnabled(enabled):
    """Turns learning mode on and off.  If learn mode is enabled, input event
    handlers will merely report what they do rather than calling the function
    bound to them.

    Arguments:
    - enabled: boolean that, if True, will enable learn mode
    """

    global learnModeEnabled
    learnModeEnabled = enabled

def getSetting(name, default=None):
    """Obtain the value for the given named attribute, trying from the
    user settings first.  If the named attribute doesn't exist, then the
    default value is returned.

    Arguments:
    - name: the name of the attribute to obtain
    - default: the default value if the named attribute doesn't exist in
               either the user settings or here.
    """

    global _userSettings

    # This little hack is for the following reason:
    #
    # We want to lazily delay the importing of user settings (that is,
    # we do not want to import it when this module is loaded).
    #
    # We only want to try once.
    #
    # So...if _userSettings is None, we haven't tried loading it yet.
    # If it is 0, we've tried and failed.
    #
    if _userSettings == None:
        try:
            _userSettings = __import__("user-settings")
        except ImportError:
            _userSettings = 0
        except:
            debug.printException(debug.LEVEL_SEVERE)
            _userSettings = 0

    thisModule = sys.modules[__name__]
    if _userSettings and hasattr(_userSettings, name):
        return getattr(_userSettings, name)
    elif hasattr(thisModule, name):
        return getattr(thisModule, name)
    else:
        return default

# Which packages to search, and the order in which to search,
# for custom scripts.  These packages are expected to be on
# the PYTHONPATH and/or subpackages of the "orca" package.
# REMEMBER: to make something a package, the directory has to
# have a __init__.py file in it.
#
SCRIPT_PACKAGES         = "scriptPackages"
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

    for mapping in _scriptMappings:
        regExpression = mapping[0]
        moduleName = mapping[1]
        if regExpression.match(app.name):
            debug.println(
                debug.LEVEL_FINEST,
                "Script mapping for %s is %s" % (app.name, moduleName))
            return moduleName

    return app.name

# Note to translators: the regular expression here represents a
# string to match in the localized application name as seen by
# at-poke.  For most cases, the application name is the name of
# the binary used to start the application, but this is an
# unreliable assumption.  The only reliable way to do the
# translation is by running the application and then viewing its
# name in the main window of at-poke.
#
setScriptMapping(re.compile(_('[\S\s]*StarOffice[\s\S]*')), "StarOffice")
setScriptMapping(re.compile(_('soffice.bin')), "StarOffice")
setScriptMapping(re.compile(_('[Ee]volution')), "Evolution")
setScriptMapping(re.compile(_('Deer Park')), "Mozilla")
