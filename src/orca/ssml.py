# Copyright 2006, 2007, 2008, 2009 Brailcom, o.p.s.
# Copyright © 2024 GNOME Foundation Inc.
#
# Author: Andy Holmes <andyholmes@gnome.org>
# Contributor: Tomas Cerha <cerha@brailcom.org>
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

# pylint: disable=too-many-branches

"""SSML --- XML-based markup language for speech synthesis.

Class SSML defines a simple wrapper for holding and converting
text to SSML, suitable to be sent to a speech server. Services
can pass flags to control the elements and attributes used.
"""

# This has to be the first non-docstring line in the module to make linters happy.
from __future__ import annotations

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__author__    = "<andyholmes@gnome.org>"
__copyright__ = "Copyright © 2024 GNOME Foundation Inc. "
__license__   = "LGPL"

from enum import Enum, auto
from typing import Any

from . import debug


class SSMLCapabilities(Enum):
    """Enumeration of SSML capabilities."""

    SAY_AS_DATE = auto()
    SAY_AS_TIME = auto()
    SAY_AS_TELEPHONE = auto()
    SAY_AS_CHARACTERS = auto()
    SAY_AS_CHARACTERS_GLYPHS = auto()
    SAY_AS_CARDINAL = auto()
    SAY_AS_ORDINAL = auto()
    SAY_AS_CURRENCY = auto()
    BREAK = auto()
    SUB = auto()
    PHONEME = auto()
    EMPHASIS = auto()
    PROSODY = auto()
    MARK = auto()
    SENTENCE_PARAGRAPH = auto()
    TOKEN = auto()
    ALL = auto()

class SSML(dict[str, Any]):
    """Holds SSML representation of an utterance."""

    def __init__(self, text: str = "", features: SSMLCapabilities = SSMLCapabilities.ALL) -> None:
        """Create and initialize ACSS structure."""
        dict.__init__(self)
        self['text'] = text or ""
        self['features'] = SSMLCapabilities(features)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SSML):
            return False
        if self.get('text') != other.get('text'):
            return False
        if self.get('features') != other.get('features'):
            return False
        return True

    @staticmethod
    def _mark_words(text: str) -> tuple[str, list[tuple[int, int]]]:
        """Mark the word offsets of text for later formatting."""

        # Mark beginning of words with U+E000 (private use) and record the
        # string offsets
        # Note: we need to do this before disturbing the text offsets
        # Note2: we assume that subsequent text mangling leaves U+E000 untouched
        marked = ""
        offsets: list[tuple[int, int]] = []
        last_begin: int | None = None
        is_numeric: bool | None = None

        for i, c in enumerate(text):
            if c == "\ue000":
                # Original text already contains U+E000. But syntheses will not
                # know what to do with it anyway, so discard it
                continue

            if not c.isspace() and last_begin is None:
                # Word begin
                marked += "\ue000"
                last_begin = i
                is_numeric = c.isnumeric()

            elif c.isspace() and last_begin is not None:
                # Word end
                if is_numeric:
                    # We had a wholy numeric word, possibly next word is as well.
                    # Skip to next word
                    for j in range(i+1, len(text)):
                        if not text[j].isspace():
                            break
                    else:
                        is_numeric = False
                    # Check next word
                    while is_numeric and j < len(text) and not text[j].isspace():
                        if not text[j].isnumeric():
                            is_numeric = False
                        j += 1

                if not is_numeric:
                    # add a mark
                    offsets.append((last_begin, i))
                    last_begin = None
                    is_numeric = None

            elif is_numeric and not c.isnumeric():
                is_numeric = False

            marked += c

        if last_begin is not None:
            # Finished with a word
            offsets.append((last_begin, len(text)))

        return (marked, offsets)

    @staticmethod
    def markup_text(text: str, features: SSMLCapabilities = SSMLCapabilities.ALL) -> str:
        """Converts plain text to SSML markup.  If features is 0, the text
        will be returned unmodified.

        Arguments:
        - text:      optional text to add to the queue before speaking
        - features:  ssml.SSMLCapabilities flags. Currently, the only
                     supported element is SSMLCapabilities.MARK.

        Returns:
        - The SSML markup of the text, per the supported features.
        """

        text = text or ""
        if features == 0:
            return text

        # Annotate the text with U+E000 (private use) and record the offsets
        (text, offsets) = SSML._mark_words(text)

        # Transcribe to SSML, translating U+E000 into marks
        # Note: we need to do this after all mangling otherwise the ssml markup
        # would get mangled too
        ssml = "<speak>"
        i = 0
        for c in text:
            if c == "\ue000":
                if i >= len(offsets):
                    # This is really not supposed to happen
                    msg = f"{i}th U+E000 does not have corresponding index"
                    debug.print_message(debug.LEVEL_WARNING, msg, True)
                else:
                    ssml += f'<mark name="{offsets[i][0]}:{offsets[i][1]}"/>'
                i += 1
            # Disable for now, until speech dispatcher properly parses them (version 0.8.9 or later)
            #elif c == '"':
            #  ssml += '&quot;'
            #elif c == "'":
            #  ssml += '&apos;'
            elif c == "<":
                ssml += "&lt;"
            elif c == ">":
                ssml += "&gt;"
            elif c == "&":
                ssml += "&amp;"
            else:
                ssml += c
        ssml += "</speak>"

        return ssml

    def get_markup(self) -> str:
        """Return the text content as SSML, per the supported features"""

        return SSML.markup_text(self["text"], self["features"])

    def get_text(self) -> str:
        """Return the unmarked-up text content."""

        return self["text"]
