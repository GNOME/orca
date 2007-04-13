# Orca
#
# Copyright 2006-2007 Sun Microsystems Inc.
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

"""Provides getPhoneticName method that maps each letter of the
alphabet into its localized phonetic equivalent."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2006-2007 Sun Microsystems Inc."
__license__   = "LGPL"

from orca_i18n import _ # for gettext support

try:
    # Translators: this is a structure to assist in the generation of
    # military-style spelling.  For example, 'abc' becomes 'alpha bravo
    # charlie'.
    #
    # It is a simple structure that consists of pairs of
    #
    # 'letter': 'word(s)'
    #
    # where the 'letter' and 'word(s)' are separate by colons and each
    # pair is separated by commas.  For example, we see:
    #
    # 'c': 'charlie'
    #
    # The complete set should consist of all the letters from the alphabet
    # for your language paired with the common military/phonetic word(s)
    # used to describe that letter. If more than one word is to be used,
    # they should all be inside the single quotes.  For example:
    #
    # 'w': 'double bourbon'
    #
    # Note that the form of this string is a Python programming language
    # construct, so you need to get the syntax right.  If you want to test
    # the syntax, build/install Orca and then type the following command
    # in a terminal with the locale set to the locale you're translating
    # to.  If no errors are emitted, and you get the correct name for
    # the character you type in (e.g., we choose "a" here and we should
    # get back "alpha" for English) you got it right:
    #
    # python -c 'import orca.phonnames; \
    #            print orca.phonnames.getPhoneticName("a")'
    #
    __phonnames = eval(_("{'a': 'alpha', 'b': 'bravo', 'c': 'charlie', "
                          "'d': 'delta', 'e': 'echo', 'f': 'foxtrot', "
                          "'g': 'golf', 'h': 'hotel', 'i': 'india', "
                          "'j': 'juliet', 'k': 'kilo', 'l': 'lima', "
                          "'m': 'mike', 'n': 'november', 'o': 'oscar', "
                          "'p': 'papa', 'q': 'quebec', 'r': 'romeo', "
                          "'s': 'sierra', 't': 'tango', 'u': 'uniform', "
                          "'v': 'victor', 'w': 'whiskey', 'x': 'xray', "
                          "'y': 'yankee', 'z': 'zulu'}"))
except:
    print "WARNING: Translation problem with phonnames.py dictionary."
    print "WARNING: Reverting to English military spelling."
    __phonnames = eval(   "{'a': 'alpha', 'b': 'bravo', 'c': 'charlie', "
                          "'d': 'delta', 'e': 'echo', 'f': 'foxtrot', "
                          "'g': 'golf', 'h': 'hotel', 'i': 'india', "
                          "'j': 'juliet', 'k': 'kilo', 'l': 'lima', "
                          "'m': 'mike', 'n': 'november', 'o': 'oscar', "
                          "'p': 'papa', 'q': 'quebec', 'r': 'romeo', "
                          "'s': 'sierra', 't': 'tango', 'u': 'uniform', "
                          "'v': 'victor', 'w': 'whiskey', 'x': 'xray', "
                          "'y': 'yankee', 'z': 'zulu'}")

def getPhoneticName(character):
    """Given a character, return its phonetic name, which is typically
    the 'military' term used for the character.

    Arguments:
    - character: the character to get the military name for

    Returns a string representing the military name for the character
    """

    if isinstance(character, unicode):
        character = character.encode("UTF-8")

    try:
        return __phonnames[character]
    except:
        return character
