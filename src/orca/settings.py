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

import sys

voices = {}
keyEcho = False
useSpeech = True
useBraille = False

try:
    userSettings = __import__("user-settings")
except:
    userSettings = None
    
def getSetting(name, default=None):
    """Obtain the value for the given named attribute, trying from the
    user settings first.  If the named attribute doesn't exist, then the
    default value is returned.

    Arguments:
    - name: the name of the attribute to obtain
    - default: the default value if the named attribute doesn't exist in
               either the user settings or here.
    """

    thisModule = sys.modules[__name__]
    if userSettings and hasattr(userSettings, name):
        return getattr(userSettings, name)
    elif hasattr(thisModule, name):
        return getattr(thisModule, name)
    else:
        return default
