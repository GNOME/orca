# Orca
#
# Copyright 2006-2008 Sun Microsystems Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

"""Exposes a dictionary, pronunciation_dict, that maps words to what they sound like."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2006-2008 Sun Microsystems Inc."
__license__   = "LGPL"

def get_pronunciation(word: str, pronunciations: dict[str, list[str]] | None = None) -> str:
    """Returns a user-provided string that represents what the word sounds like."""

    dictionary = pronunciations or pronunciation_dict
    entry = dictionary.get(word.lower(), [word, word])
    return entry[1]

def set_pronunciation(
  word: str,
  replacement: str,
  pronunciations: dict[str, list[str]] | None = None
) -> None:
    """Adds word/replacement pair to the pronunciation dictionary."""

    key = word.lower()
    if pronunciations is not None:
        pronunciations[key] = [word, replacement]
    else:
        pronunciation_dict[key] = [word, replacement]

# pronunciation_dict is a dictionary where the keys are words and the value is a list
# containing the original word and the replacement pronunciation string.
pronunciation_dict: dict[str, list[str]] = {}
