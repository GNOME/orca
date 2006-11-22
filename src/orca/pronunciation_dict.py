# Orca
#
# Copyright 2006 Sun Microsystems Inc.
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

"""Exposes a dictionary, pronunciation_dict, that maps words to what
they sound like."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2006 Sun Microsystems Inc."
__license__   = "LGPL"

from orca_i18n import _ # for gettext support

# pronunciation_dict is a dictionary where the keys are words and the 
# values represent word the pronunciation of that word (in other words, 
# what the word sounds like).
#
# [[[TODO: richb - need to populate this dictionary with many more values.]]]
#
pronunciation_dict = {}
pronunciation_dict[_("ASAP")]    = _("as soon as possible")
pronunciation_dict[_("GHz")]     = _("gigahertz")
pronunciation_dict[_("IMAP")]    = _("eye map")
pronunciation_dict[_("LDAP")]    = _("ell dap")
pronunciation_dict[_("LOL")]     = _("laughing out loud")
pronunciation_dict[_("MHz")]     = _("megahertz")
pronunciation_dict[_("strikethrough")] = _("strike through")
pronunciation_dict[_("SELinux")] = _("ess ee linux")

def getPronunciation(word):
    """Given a word, return a string that represents what this word
    sounds like.

    Arguments:
    - key: the word to get the "sounds like" representation for.

    Returns a string that represents what this word sounds like, or 
    the word if there is no representation.
    """

    if isinstance(word, unicode):
        word = word.encode("UTF-8")

    try:
        return pronunciation_dict[word]
    except:
        return word
