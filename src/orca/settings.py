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

# Constants for categorizing verbosity levels (see
# setBrailleVerbosityLevel and setSpeechVerbosityLevel).
# These will have an impact on the various individual
# verbosity levels for rolenames, accelerators, etc.
#
VERBOSITY_LEVEL_BRIEF   = 0
VERBOSITY_LEVEL_VERBOSE = 1

speechVerbosityLevel  = VERBOSITY_LEVEL_VERBOSE
brailleVerbosityLevel = VERBOSITY_LEVEL_VERBOSE

# Constants for determining braille rolename style.
#
BRAILLE_ROLENAME_STYLE_SHORT = 0 # three letter abbreviations
BRAILLE_ROLENAME_STYLE_LONG  = 1 # full rolename

brailleRolenameStyle = BRAILLE_ROLENAME_STYLE_LONG

voices = {}
keyEcho = False
useSpeech = True
useBraille = False
learnModeEnabled = False

_userSettings = None


def setSpeechVerbosityLevel(verbosityLevel):
    """Sets the verbosity level for speech output.

    Arguments:
    - verbosityLevel: one of VERBOSITY_LEVEL_BRIEF or VERBOSITY_LEVEL_VERBOSE
    """
    global speechVerbosityLevel
    speechVerbosityLevel = verbosityLevel
    debug.println(debug.LEVEL_CONFIGURATION,
                  "Changed braille verbosity level to %d" % verbosityLevel)

    
def setBrailleVerbosityLevel(verbosityLevel):
    """Sets the verbosity level for braille output.

    Arguments:
    - verbosityLevel: one of VERBOSITY_LEVEL_BRIEF or VERBOSITY_LEVEL_VERBOSE
    """
    global brailleVerbosityLevel
    brailleVerbosityLevel = verbosityLevel
    debug.println(debug.LEVEL_CONFIGURATION,
                  "Changed braille verbosity level to %d" % verbosityLevel)

    
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



# A list of package names to search for script modules.  The
# focus_tracking_presenter will search these in order when
# looking for a script module.  
#
scriptPackages = ["orca-scripts", "scripts"]


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

    global _scriptMappings
    
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
            return moduleName

    return app.name


setScriptMapping(re.compile('[\S\s]*StarOffice[\s\S]*'), "StarOffice")

