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

"""Exposes a dictionary, pronunciation_dict, that maps words to what
they sound like."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2006-2008 Sun Microsystems Inc."
__license__   = "LGPL"

def getPronunciation(word, pronunciations=None):
    """Given a word, return a string that represents what this word
    sounds like. Note: This code does not handle the pronunciation
    of character names. If you want a character name to be spoken,
    treat it as a punctuation character at LEVEL_NONE in
    puncutation_settings.py. See, for example, the left_arrow and
    right_arrow characters.

    Arguments:
    - word: the word to get the "sounds like" representation for.
    - pronunciations: an optional dictionary used to get the pronunciation
      from.

    Returns a string that represents what this word sounds like, or 
    the word if there is no representation.
    """

    lowerWord = word.lower()
    dictionary = pronunciations or pronunciation_dict
    entry = dictionary.get(lowerWord, [word, word])

    return entry[1]

def setPronunciation(word, replacementString, pronunciations=None):
    """Given an actual word, and a replacement string, set a key/value
    pair in a pronunciation dictionary.

    Arguments:
    - word: the word to be pronunced.
    - replacementString: the replacement string to use instead.
    - pronunciations: an optional dictionary used to set the pronunciation
      into.
    """

    key = word.lower()
    if pronunciations != None:
        pronunciations[key] = [ word, replacementString ]
    else:
        pronunciation_dict[key] = [ word, replacementString ]

# pronunciation_dict is a dictionary where the keys are words and the
# values represent word the pronunciation of that word (in other words,
# what the word sounds like).
#
pronunciation_dict = {}
