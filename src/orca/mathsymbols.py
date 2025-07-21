# Orca
#
# Copyright 2014 Igalia, S.L.
#
# Author: Joanmarie Diggs <jdiggs@igalia.com>
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

# pylint: disable=too-many-lines
# pylint: disable=too-many-return-statements
# pylint: disable=too-many-branches

"""Turns math symbols into their spoken representation."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2014 Igalia, S.L."
__license__   = "LGPL"

import unicodedata

from . import debug
from .orca_i18n import C_ # pylint: disable=import-error

SPEAK_NEVER = 1
SPEAK_ALWAYS = 2
SPEAK_FOR_CHARS = 3
speak_style = SPEAK_ALWAYS # pylint: disable=invalid-name

fall_back_on_unicode_data = False # pylint: disable=invalid-name

_all: dict[str, str] = {}
_alnum: dict[str, str] = {}
_arrows: dict[str, str] = {}
_operators: dict[str, str] = {}
_shapes: dict[str, str] = {}
_combining: dict[str, str] = {}

# Note that the following are to help us identify what is likely a math symbol
# (as opposed to one serving the function of an image in "This way up.")
_arrows.update(dict.fromkeys(map(chr, range(0x2190, 0x2200)), ""))
_arrows.update(dict.fromkeys(map(chr, range(0x2750, 0x2800)), ""))
_arrows.update(dict.fromkeys(map(chr, range(0x2b30, 0x2b50)), ""))
_operators.update(dict.fromkeys(map(chr, range(0x2220, 0x2300)), ""))
_operators.update(dict.fromkeys(map(chr, range(0x2a00, 0x2b00)), ""))
_shapes.update(dict.fromkeys(map(chr, range(0x25a0, 0x2600)), ""))

# Unicode has a huge number of individual symbols to include styles, such as
# bold, italic, double-struck, etc. These are so far not supported by speech
# synthesizers. So we'll maintain a dictionary of equivalent symbols which
# speech synthesizers should know along with lists of the various styles.
_alnum['\u2102'] = 'C'
_alnum['\u210a'] = 'g'
_alnum['\u210b'] = 'H'
_alnum['\u210c'] = 'H'
_alnum['\u210d'] = 'H'
_alnum['\u210e'] = 'h'
_alnum['\u2110'] = 'I'
_alnum['\u2111'] = 'I'
_alnum['\u2112'] = 'L'
_alnum['\u2113'] = 'l'
_alnum['\u2115'] = 'N'
_alnum['\u2119'] = 'P'
_alnum['\u211a'] = 'Q'
_alnum['\u211b'] = 'R'
_alnum['\u211c'] = 'R'
_alnum['\u211d'] = 'R'
_alnum['\u2124'] = 'Z'
_alnum['\u2128'] = 'Z'
_alnum['\u212c'] = 'B'
_alnum['\u212d'] = 'C'
_alnum['\u212f'] = 'e'
_alnum['\u2130'] = 'E'
_alnum['\u2131'] = 'F'
_alnum['\u2133'] = 'M'
_alnum['\u2134'] = 'o'
_alnum['\U0001d400'] = 'A'
_alnum['\U0001d401'] = 'B'
_alnum['\U0001d402'] = 'C'
_alnum['\U0001d403'] = 'D'
_alnum['\U0001d404'] = 'E'
_alnum['\U0001d405'] = 'F'
_alnum['\U0001d406'] = 'G'
_alnum['\U0001d407'] = 'H'
_alnum['\U0001d408'] = 'I'
_alnum['\U0001d409'] = 'J'
_alnum['\U0001d40a'] = 'K'
_alnum['\U0001d40b'] = 'L'
_alnum['\U0001d40c'] = 'M'
_alnum['\U0001d40d'] = 'N'
_alnum['\U0001d40e'] = 'O'
_alnum['\U0001d40f'] = 'P'
_alnum['\U0001d410'] = 'Q'
_alnum['\U0001d411'] = 'R'
_alnum['\U0001d412'] = 'S'
_alnum['\U0001d413'] = 'T'
_alnum['\U0001d414'] = 'U'
_alnum['\U0001d415'] = 'V'
_alnum['\U0001d416'] = 'W'
_alnum['\U0001d417'] = 'X'
_alnum['\U0001d418'] = 'Y'
_alnum['\U0001d419'] = 'Z'
_alnum['\U0001d41a'] = 'a'
_alnum['\U0001d41b'] = 'b'
_alnum['\U0001d41c'] = 'c'
_alnum['\U0001d41d'] = 'd'
_alnum['\U0001d41e'] = 'e'
_alnum['\U0001d41f'] = 'f'
_alnum['\U0001d420'] = 'g'
_alnum['\U0001d421'] = 'h'
_alnum['\U0001d422'] = 'i'
_alnum['\U0001d423'] = 'j'
_alnum['\U0001d424'] = 'k'
_alnum['\U0001d425'] = 'l'
_alnum['\U0001d426'] = 'm'
_alnum['\U0001d427'] = 'n'
_alnum['\U0001d428'] = 'o'
_alnum['\U0001d429'] = 'p'
_alnum['\U0001d42a'] = 'q'
_alnum['\U0001d42b'] = 'r'
_alnum['\U0001d42c'] = 's'
_alnum['\U0001d42d'] = 't'
_alnum['\U0001d42e'] = 'u'
_alnum['\U0001d42f'] = 'v'
_alnum['\U0001d430'] = 'w'
_alnum['\U0001d431'] = 'x'
_alnum['\U0001d432'] = 'y'
_alnum['\U0001d433'] = 'z'
_alnum['\U0001d434'] = 'A'
_alnum['\U0001d435'] = 'B'
_alnum['\U0001d436'] = 'C'
_alnum['\U0001d437'] = 'D'
_alnum['\U0001d438'] = 'E'
_alnum['\U0001d439'] = 'F'
_alnum['\U0001d43a'] = 'G'
_alnum['\U0001d43b'] = 'H'
_alnum['\U0001d43c'] = 'I'
_alnum['\U0001d43d'] = 'J'
_alnum['\U0001d43e'] = 'K'
_alnum['\U0001d43f'] = 'L'
_alnum['\U0001d440'] = 'M'
_alnum['\U0001d441'] = 'N'
_alnum['\U0001d442'] = 'O'
_alnum['\U0001d443'] = 'P'
_alnum['\U0001d444'] = 'Q'
_alnum['\U0001d445'] = 'R'
_alnum['\U0001d446'] = 'S'
_alnum['\U0001d447'] = 'T'
_alnum['\U0001d448'] = 'U'
_alnum['\U0001d449'] = 'V'
_alnum['\U0001d44a'] = 'W'
_alnum['\U0001d44b'] = 'X'
_alnum['\U0001d44c'] = 'Y'
_alnum['\U0001d44d'] = 'Z'
_alnum['\U0001d44e'] = 'a'
_alnum['\U0001d44f'] = 'b'
_alnum['\U0001d450'] = 'c'
_alnum['\U0001d451'] = 'd'
_alnum['\U0001d452'] = 'e'
_alnum['\U0001d453'] = 'f'
_alnum['\U0001d454'] = 'g'
_alnum['\U0001d456'] = 'i'
_alnum['\U0001d457'] = 'j'
_alnum['\U0001d458'] = 'k'
_alnum['\U0001d459'] = 'l'
_alnum['\U0001d45a'] = 'm'
_alnum['\U0001d45b'] = 'n'
_alnum['\U0001d45c'] = 'o'
_alnum['\U0001d45d'] = 'p'
_alnum['\U0001d45e'] = 'q'
_alnum['\U0001d45f'] = 'r'
_alnum['\U0001d460'] = 's'
_alnum['\U0001d461'] = 't'
_alnum['\U0001d462'] = 'u'
_alnum['\U0001d463'] = 'v'
_alnum['\U0001d464'] = 'w'
_alnum['\U0001d465'] = 'x'
_alnum['\U0001d466'] = 'y'
_alnum['\U0001d467'] = 'z'
_alnum['\U0001d468'] = 'A'
_alnum['\U0001d469'] = 'B'
_alnum['\U0001d46a'] = 'C'
_alnum['\U0001d46b'] = 'D'
_alnum['\U0001d46c'] = 'E'
_alnum['\U0001d46d'] = 'F'
_alnum['\U0001d46e'] = 'G'
_alnum['\U0001d46f'] = 'H'
_alnum['\U0001d470'] = 'I'
_alnum['\U0001d471'] = 'J'
_alnum['\U0001d472'] = 'K'
_alnum['\U0001d473'] = 'L'
_alnum['\U0001d474'] = 'M'
_alnum['\U0001d475'] = 'N'
_alnum['\U0001d476'] = 'O'
_alnum['\U0001d477'] = 'P'
_alnum['\U0001d478'] = 'Q'
_alnum['\U0001d479'] = 'R'
_alnum['\U0001d47a'] = 'S'
_alnum['\U0001d47b'] = 'T'
_alnum['\U0001d47c'] = 'U'
_alnum['\U0001d47d'] = 'V'
_alnum['\U0001d47e'] = 'W'
_alnum['\U0001d47f'] = 'X'
_alnum['\U0001d480'] = 'Y'
_alnum['\U0001d481'] = 'Z'
_alnum['\U0001d482'] = 'a'
_alnum['\U0001d483'] = 'b'
_alnum['\U0001d484'] = 'c'
_alnum['\U0001d485'] = 'd'
_alnum['\U0001d486'] = 'e'
_alnum['\U0001d487'] = 'f'
_alnum['\U0001d488'] = 'g'
_alnum['\U0001d489'] = 'h'
_alnum['\U0001d48a'] = 'i'
_alnum['\U0001d48b'] = 'j'
_alnum['\U0001d48c'] = 'k'
_alnum['\U0001d48d'] = 'l'
_alnum['\U0001d48e'] = 'm'
_alnum['\U0001d48f'] = 'n'
_alnum['\U0001d490'] = 'o'
_alnum['\U0001d491'] = 'p'
_alnum['\U0001d492'] = 'q'
_alnum['\U0001d493'] = 'r'
_alnum['\U0001d494'] = 's'
_alnum['\U0001d495'] = 't'
_alnum['\U0001d496'] = 'u'
_alnum['\U0001d497'] = 'v'
_alnum['\U0001d498'] = 'w'
_alnum['\U0001d499'] = 'x'
_alnum['\U0001d49a'] = 'y'
_alnum['\U0001d49b'] = 'z'
_alnum['\U0001d49c'] = 'A'
_alnum['\U0001d49e'] = 'C'
_alnum['\U0001d49f'] = 'D'
_alnum['\U0001d4a2'] = 'G'
_alnum['\U0001d4a5'] = 'J'
_alnum['\U0001d4a6'] = 'K'
_alnum['\U0001d4a9'] = 'N'
_alnum['\U0001d4aa'] = 'O'
_alnum['\U0001d4ab'] = 'P'
_alnum['\U0001d4ac'] = 'Q'
_alnum['\U0001d4ae'] = 'S'
_alnum['\U0001d4af'] = 'T'
_alnum['\U0001d4b0'] = 'U'
_alnum['\U0001d4b1'] = 'V'
_alnum['\U0001d4b2'] = 'W'
_alnum['\U0001d4b3'] = 'X'
_alnum['\U0001d4b4'] = 'Y'
_alnum['\U0001d4b5'] = 'Z'
_alnum['\U0001d4b6'] = 'a'
_alnum['\U0001d4b7'] = 'b'
_alnum['\U0001d4b8'] = 'c'
_alnum['\U0001d4b9'] = 'd'
_alnum['\U0001d4bb'] = 'f'
_alnum['\U0001d4bd'] = 'h'
_alnum['\U0001d4be'] = 'i'
_alnum['\U0001d4bf'] = 'j'
_alnum['\U0001d4c0'] = 'k'
_alnum['\U0001d4c1'] = 'l'
_alnum['\U0001d4c2'] = 'm'
_alnum['\U0001d4c3'] = 'n'
_alnum['\U0001d4c5'] = 'p'
_alnum['\U0001d4c6'] = 'q'
_alnum['\U0001d4c7'] = 'r'
_alnum['\U0001d4c8'] = 's'
_alnum['\U0001d4c9'] = 't'
_alnum['\U0001d4ca'] = 'u'
_alnum['\U0001d4cb'] = 'v'
_alnum['\U0001d4cc'] = 'w'
_alnum['\U0001d4cd'] = 'x'
_alnum['\U0001d4ce'] = 'y'
_alnum['\U0001d4cf'] = 'z'
_alnum['\U0001d4d0'] = 'A'
_alnum['\U0001d4d1'] = 'B'
_alnum['\U0001d4d2'] = 'C'
_alnum['\U0001d4d3'] = 'D'
_alnum['\U0001d4d4'] = 'E'
_alnum['\U0001d4d5'] = 'F'
_alnum['\U0001d4d6'] = 'G'
_alnum['\U0001d4d7'] = 'H'
_alnum['\U0001d4d8'] = 'I'
_alnum['\U0001d4d9'] = 'J'
_alnum['\U0001d4da'] = 'K'
_alnum['\U0001d4db'] = 'L'
_alnum['\U0001d4dc'] = 'M'
_alnum['\U0001d4dd'] = 'N'
_alnum['\U0001d4de'] = 'O'
_alnum['\U0001d4df'] = 'P'
_alnum['\U0001d4e0'] = 'Q'
_alnum['\U0001d4e1'] = 'R'
_alnum['\U0001d4e2'] = 'S'
_alnum['\U0001d4e3'] = 'T'
_alnum['\U0001d4e4'] = 'U'
_alnum['\U0001d4e5'] = 'V'
_alnum['\U0001d4e6'] = 'W'
_alnum['\U0001d4e7'] = 'X'
_alnum['\U0001d4e8'] = 'Y'
_alnum['\U0001d4e9'] = 'Z'
_alnum['\U0001d4ea'] = 'a'
_alnum['\U0001d4eb'] = 'b'
_alnum['\U0001d4ec'] = 'c'
_alnum['\U0001d4ed'] = 'd'
_alnum['\U0001d4ee'] = 'e'
_alnum['\U0001d4ef'] = 'f'
_alnum['\U0001d4f0'] = 'g'
_alnum['\U0001d4f1'] = 'h'
_alnum['\U0001d4f2'] = 'i'
_alnum['\U0001d4f3'] = 'j'
_alnum['\U0001d4f4'] = 'k'
_alnum['\U0001d4f5'] = 'l'
_alnum['\U0001d4f6'] = 'm'
_alnum['\U0001d4f7'] = 'n'
_alnum['\U0001d4f8'] = 'o'
_alnum['\U0001d4f9'] = 'p'
_alnum['\U0001d4fa'] = 'q'
_alnum['\U0001d4fb'] = 'r'
_alnum['\U0001d4fc'] = 's'
_alnum['\U0001d4fd'] = 't'
_alnum['\U0001d4fe'] = 'u'
_alnum['\U0001d4ff'] = 'v'
_alnum['\U0001d500'] = 'w'
_alnum['\U0001d501'] = 'x'
_alnum['\U0001d502'] = 'y'
_alnum['\U0001d503'] = 'z'
_alnum['\U0001d504'] = 'A'
_alnum['\U0001d505'] = 'B'
_alnum['\U0001d507'] = 'D'
_alnum['\U0001d508'] = 'E'
_alnum['\U0001d509'] = 'F'
_alnum['\U0001d50a'] = 'G'
_alnum['\U0001d50d'] = 'J'
_alnum['\U0001d50e'] = 'K'
_alnum['\U0001d50f'] = 'L'
_alnum['\U0001d510'] = 'M'
_alnum['\U0001d511'] = 'N'
_alnum['\U0001d512'] = 'O'
_alnum['\U0001d513'] = 'P'
_alnum['\U0001d514'] = 'Q'
_alnum['\U0001d516'] = 'S'
_alnum['\U0001d517'] = 'T'
_alnum['\U0001d518'] = 'U'
_alnum['\U0001d519'] = 'V'
_alnum['\U0001d51a'] = 'W'
_alnum['\U0001d51b'] = 'X'
_alnum['\U0001d51c'] = 'Y'
_alnum['\U0001d51e'] = 'a'
_alnum['\U0001d51f'] = 'b'
_alnum['\U0001d520'] = 'c'
_alnum['\U0001d521'] = 'd'
_alnum['\U0001d522'] = 'e'
_alnum['\U0001d523'] = 'f'
_alnum['\U0001d524'] = 'g'
_alnum['\U0001d525'] = 'h'
_alnum['\U0001d526'] = 'i'
_alnum['\U0001d527'] = 'j'
_alnum['\U0001d528'] = 'k'
_alnum['\U0001d529'] = 'l'
_alnum['\U0001d52a'] = 'm'
_alnum['\U0001d52b'] = 'n'
_alnum['\U0001d52c'] = 'o'
_alnum['\U0001d52d'] = 'p'
_alnum['\U0001d52e'] = 'q'
_alnum['\U0001d52f'] = 'r'
_alnum['\U0001d530'] = 's'
_alnum['\U0001d531'] = 't'
_alnum['\U0001d532'] = 'u'
_alnum['\U0001d533'] = 'v'
_alnum['\U0001d534'] = 'w'
_alnum['\U0001d535'] = 'x'
_alnum['\U0001d536'] = 'y'
_alnum['\U0001d537'] = 'z'
_alnum['\U0001d538'] = 'A'
_alnum['\U0001d539'] = 'B'
_alnum['\U0001d53b'] = 'D'
_alnum['\U0001d53c'] = 'E'
_alnum['\U0001d53d'] = 'F'
_alnum['\U0001d53e'] = 'G'
_alnum['\U0001d540'] = 'I'
_alnum['\U0001d541'] = 'J'
_alnum['\U0001d542'] = 'K'
_alnum['\U0001d543'] = 'L'
_alnum['\U0001d544'] = 'M'
_alnum['\U0001d546'] = 'O'
_alnum['\U0001d54a'] = 'S'
_alnum['\U0001d54b'] = 'T'
_alnum['\U0001d54c'] = 'U'
_alnum['\U0001d54d'] = 'V'
_alnum['\U0001d54e'] = 'W'
_alnum['\U0001d54f'] = 'X'
_alnum['\U0001d550'] = 'Y'
_alnum['\U0001d552'] = 'a'
_alnum['\U0001d553'] = 'b'
_alnum['\U0001d554'] = 'c'
_alnum['\U0001d555'] = 'd'
_alnum['\U0001d556'] = 'e'
_alnum['\U0001d557'] = 'f'
_alnum['\U0001d558'] = 'g'
_alnum['\U0001d559'] = 'h'
_alnum['\U0001d55a'] = 'i'
_alnum['\U0001d55b'] = 'j'
_alnum['\U0001d55c'] = 'k'
_alnum['\U0001d55d'] = 'l'
_alnum['\U0001d55e'] = 'm'
_alnum['\U0001d55f'] = 'n'
_alnum['\U0001d560'] = 'o'
_alnum['\U0001d561'] = 'p'
_alnum['\U0001d562'] = 'q'
_alnum['\U0001d563'] = 'r'
_alnum['\U0001d564'] = 's'
_alnum['\U0001d565'] = 't'
_alnum['\U0001d566'] = 'u'
_alnum['\U0001d567'] = 'v'
_alnum['\U0001d568'] = 'w'
_alnum['\U0001d569'] = 'x'
_alnum['\U0001d56a'] = 'y'
_alnum['\U0001d56b'] = 'z'
_alnum['\U0001d56c'] = 'A'
_alnum['\U0001d56d'] = 'B'
_alnum['\U0001d56e'] = 'C'
_alnum['\U0001d56f'] = 'D'
_alnum['\U0001d570'] = 'E'
_alnum['\U0001d571'] = 'F'
_alnum['\U0001d572'] = 'G'
_alnum['\U0001d573'] = 'H'
_alnum['\U0001d574'] = 'I'
_alnum['\U0001d575'] = 'J'
_alnum['\U0001d576'] = 'K'
_alnum['\U0001d577'] = 'L'
_alnum['\U0001d578'] = 'M'
_alnum['\U0001d579'] = 'N'
_alnum['\U0001d57a'] = 'O'
_alnum['\U0001d57b'] = 'P'
_alnum['\U0001d57c'] = 'Q'
_alnum['\U0001d57d'] = 'R'
_alnum['\U0001d57e'] = 'S'
_alnum['\U0001d57f'] = 'T'
_alnum['\U0001d580'] = 'U'
_alnum['\U0001d581'] = 'V'
_alnum['\U0001d582'] = 'W'
_alnum['\U0001d583'] = 'X'
_alnum['\U0001d584'] = 'Y'
_alnum['\U0001d585'] = 'Z'
_alnum['\U0001d586'] = 'a'
_alnum['\U0001d587'] = 'b'
_alnum['\U0001d588'] = 'c'
_alnum['\U0001d589'] = 'd'
_alnum['\U0001d58a'] = 'e'
_alnum['\U0001d58b'] = 'f'
_alnum['\U0001d58c'] = 'g'
_alnum['\U0001d58d'] = 'h'
_alnum['\U0001d58e'] = 'i'
_alnum['\U0001d58f'] = 'j'
_alnum['\U0001d590'] = 'k'
_alnum['\U0001d591'] = 'l'
_alnum['\U0001d592'] = 'm'
_alnum['\U0001d593'] = 'n'
_alnum['\U0001d594'] = 'o'
_alnum['\U0001d595'] = 'p'
_alnum['\U0001d596'] = 'q'
_alnum['\U0001d597'] = 'r'
_alnum['\U0001d598'] = 's'
_alnum['\U0001d599'] = 't'
_alnum['\U0001d59a'] = 'u'
_alnum['\U0001d59b'] = 'v'
_alnum['\U0001d59c'] = 'w'
_alnum['\U0001d59d'] = 'x'
_alnum['\U0001d59e'] = 'y'
_alnum['\U0001d59f'] = 'z'
_alnum['\U0001d5a0'] = 'A'
_alnum['\U0001d5a1'] = 'B'
_alnum['\U0001d5a2'] = 'C'
_alnum['\U0001d5a3'] = 'D'
_alnum['\U0001d5a4'] = 'E'
_alnum['\U0001d5a5'] = 'F'
_alnum['\U0001d5a6'] = 'G'
_alnum['\U0001d5a7'] = 'H'
_alnum['\U0001d5a8'] = 'I'
_alnum['\U0001d5a9'] = 'J'
_alnum['\U0001d5aa'] = 'K'
_alnum['\U0001d5ab'] = 'L'
_alnum['\U0001d5ac'] = 'M'
_alnum['\U0001d5ad'] = 'N'
_alnum['\U0001d5ae'] = 'O'
_alnum['\U0001d5af'] = 'P'
_alnum['\U0001d5b0'] = 'Q'
_alnum['\U0001d5b1'] = 'R'
_alnum['\U0001d5b2'] = 'S'
_alnum['\U0001d5b3'] = 'T'
_alnum['\U0001d5b4'] = 'U'
_alnum['\U0001d5b5'] = 'V'
_alnum['\U0001d5b6'] = 'W'
_alnum['\U0001d5b7'] = 'X'
_alnum['\U0001d5b8'] = 'Y'
_alnum['\U0001d5b9'] = 'Z'
_alnum['\U0001d5ba'] = 'a'
_alnum['\U0001d5bb'] = 'b'
_alnum['\U0001d5bc'] = 'c'
_alnum['\U0001d5bd'] = 'd'
_alnum['\U0001d5be'] = 'e'
_alnum['\U0001d5bf'] = 'f'
_alnum['\U0001d5c0'] = 'g'
_alnum['\U0001d5c1'] = 'h'
_alnum['\U0001d5c2'] = 'i'
_alnum['\U0001d5c3'] = 'j'
_alnum['\U0001d5c4'] = 'k'
_alnum['\U0001d5c5'] = 'l'
_alnum['\U0001d5c6'] = 'm'
_alnum['\U0001d5c7'] = 'n'
_alnum['\U0001d5c8'] = 'o'
_alnum['\U0001d5c9'] = 'p'
_alnum['\U0001d5ca'] = 'q'
_alnum['\U0001d5cb'] = 'r'
_alnum['\U0001d5cc'] = 's'
_alnum['\U0001d5cd'] = 't'
_alnum['\U0001d5ce'] = 'u'
_alnum['\U0001d5cf'] = 'v'
_alnum['\U0001d5d0'] = 'w'
_alnum['\U0001d5d1'] = 'x'
_alnum['\U0001d5d2'] = 'y'
_alnum['\U0001d5d3'] = 'z'
_alnum['\U0001d5d4'] = 'A'
_alnum['\U0001d5d5'] = 'B'
_alnum['\U0001d5d6'] = 'C'
_alnum['\U0001d5d7'] = 'D'
_alnum['\U0001d5d8'] = 'E'
_alnum['\U0001d5d9'] = 'F'
_alnum['\U0001d5da'] = 'G'
_alnum['\U0001d5db'] = 'H'
_alnum['\U0001d5dc'] = 'I'
_alnum['\U0001d5dd'] = 'J'
_alnum['\U0001d5de'] = 'K'
_alnum['\U0001d5df'] = 'L'
_alnum['\U0001d5e0'] = 'M'
_alnum['\U0001d5e1'] = 'N'
_alnum['\U0001d5e2'] = 'O'
_alnum['\U0001d5e3'] = 'P'
_alnum['\U0001d5e4'] = 'Q'
_alnum['\U0001d5e5'] = 'R'
_alnum['\U0001d5e6'] = 'S'
_alnum['\U0001d5e7'] = 'T'
_alnum['\U0001d5e8'] = 'U'
_alnum['\U0001d5e9'] = 'V'
_alnum['\U0001d5ea'] = 'W'
_alnum['\U0001d5eb'] = 'X'
_alnum['\U0001d5ec'] = 'Y'
_alnum['\U0001d5ed'] = 'Z'
_alnum['\U0001d5ee'] = 'a'
_alnum['\U0001d5ef'] = 'b'
_alnum['\U0001d5f0'] = 'c'
_alnum['\U0001d5f1'] = 'd'
_alnum['\U0001d5f2'] = 'e'
_alnum['\U0001d5f3'] = 'f'
_alnum['\U0001d5f4'] = 'g'
_alnum['\U0001d5f5'] = 'h'
_alnum['\U0001d5f6'] = 'i'
_alnum['\U0001d5f7'] = 'j'
_alnum['\U0001d5f8'] = 'k'
_alnum['\U0001d5f9'] = 'l'
_alnum['\U0001d5fa'] = 'm'
_alnum['\U0001d5fb'] = 'n'
_alnum['\U0001d5fc'] = 'o'
_alnum['\U0001d5fd'] = 'p'
_alnum['\U0001d5fe'] = 'q'
_alnum['\U0001d5ff'] = 'r'
_alnum['\U0001d600'] = 's'
_alnum['\U0001d601'] = 't'
_alnum['\U0001d602'] = 'u'
_alnum['\U0001d603'] = 'v'
_alnum['\U0001d604'] = 'w'
_alnum['\U0001d605'] = 'x'
_alnum['\U0001d606'] = 'y'
_alnum['\U0001d607'] = 'z'
_alnum['\U0001d608'] = 'A'
_alnum['\U0001d609'] = 'B'
_alnum['\U0001d60a'] = 'C'
_alnum['\U0001d60b'] = 'D'
_alnum['\U0001d60c'] = 'E'
_alnum['\U0001d60d'] = 'F'
_alnum['\U0001d60e'] = 'G'
_alnum['\U0001d60f'] = 'H'
_alnum['\U0001d610'] = 'I'
_alnum['\U0001d611'] = 'J'
_alnum['\U0001d612'] = 'K'
_alnum['\U0001d613'] = 'L'
_alnum['\U0001d614'] = 'M'
_alnum['\U0001d615'] = 'N'
_alnum['\U0001d616'] = 'O'
_alnum['\U0001d617'] = 'P'
_alnum['\U0001d618'] = 'Q'
_alnum['\U0001d619'] = 'R'
_alnum['\U0001d61a'] = 'S'
_alnum['\U0001d61b'] = 'T'
_alnum['\U0001d61c'] = 'U'
_alnum['\U0001d61d'] = 'V'
_alnum['\U0001d61e'] = 'W'
_alnum['\U0001d61f'] = 'X'
_alnum['\U0001d620'] = 'Y'
_alnum['\U0001d621'] = 'Z'
_alnum['\U0001d622'] = 'a'
_alnum['\U0001d623'] = 'b'
_alnum['\U0001d624'] = 'c'
_alnum['\U0001d625'] = 'd'
_alnum['\U0001d626'] = 'e'
_alnum['\U0001d627'] = 'f'
_alnum['\U0001d628'] = 'g'
_alnum['\U0001d629'] = 'h'
_alnum['\U0001d62a'] = 'i'
_alnum['\U0001d62b'] = 'j'
_alnum['\U0001d62c'] = 'k'
_alnum['\U0001d62d'] = 'l'
_alnum['\U0001d62e'] = 'm'
_alnum['\U0001d62f'] = 'n'
_alnum['\U0001d630'] = 'o'
_alnum['\U0001d631'] = 'p'
_alnum['\U0001d632'] = 'q'
_alnum['\U0001d633'] = 'r'
_alnum['\U0001d634'] = 's'
_alnum['\U0001d635'] = 't'
_alnum['\U0001d636'] = 'u'
_alnum['\U0001d637'] = 'v'
_alnum['\U0001d638'] = 'w'
_alnum['\U0001d639'] = 'x'
_alnum['\U0001d63a'] = 'y'
_alnum['\U0001d63b'] = 'z'
_alnum['\U0001d63c'] = 'A'
_alnum['\U0001d63d'] = 'B'
_alnum['\U0001d63e'] = 'C'
_alnum['\U0001d63f'] = 'D'
_alnum['\U0001d640'] = 'E'
_alnum['\U0001d641'] = 'F'
_alnum['\U0001d642'] = 'G'
_alnum['\U0001d643'] = 'H'
_alnum['\U0001d644'] = 'I'
_alnum['\U0001d645'] = 'J'
_alnum['\U0001d646'] = 'K'
_alnum['\U0001d647'] = 'L'
_alnum['\U0001d648'] = 'M'
_alnum['\U0001d649'] = 'N'
_alnum['\U0001d64a'] = 'O'
_alnum['\U0001d64b'] = 'P'
_alnum['\U0001d64c'] = 'Q'
_alnum['\U0001d64d'] = 'R'
_alnum['\U0001d64e'] = 'S'
_alnum['\U0001d64f'] = 'T'
_alnum['\U0001d650'] = 'U'
_alnum['\U0001d651'] = 'V'
_alnum['\U0001d652'] = 'W'
_alnum['\U0001d653'] = 'X'
_alnum['\U0001d654'] = 'Y'
_alnum['\U0001d655'] = 'Z'
_alnum['\U0001d656'] = 'a'
_alnum['\U0001d657'] = 'b'
_alnum['\U0001d658'] = 'c'
_alnum['\U0001d659'] = 'd'
_alnum['\U0001d65a'] = 'e'
_alnum['\U0001d65b'] = 'f'
_alnum['\U0001d65c'] = 'g'
_alnum['\U0001d65d'] = 'h'
_alnum['\U0001d65e'] = 'i'
_alnum['\U0001d65f'] = 'j'
_alnum['\U0001d660'] = 'k'
_alnum['\U0001d661'] = 'l'
_alnum['\U0001d662'] = 'm'
_alnum['\U0001d663'] = 'n'
_alnum['\U0001d664'] = 'o'
_alnum['\U0001d665'] = 'p'
_alnum['\U0001d666'] = 'q'
_alnum['\U0001d667'] = 'r'
_alnum['\U0001d668'] = 's'
_alnum['\U0001d669'] = 't'
_alnum['\U0001d66a'] = 'u'
_alnum['\U0001d66b'] = 'v'
_alnum['\U0001d66c'] = 'w'
_alnum['\U0001d66d'] = 'x'
_alnum['\U0001d66e'] = 'y'
_alnum['\U0001d66f'] = 'z'
_alnum['\U0001d670'] = 'A'
_alnum['\U0001d671'] = 'B'
_alnum['\U0001d672'] = 'C'
_alnum['\U0001d673'] = 'D'
_alnum['\U0001d674'] = 'E'
_alnum['\U0001d675'] = 'F'
_alnum['\U0001d676'] = 'G'
_alnum['\U0001d677'] = 'H'
_alnum['\U0001d678'] = 'I'
_alnum['\U0001d679'] = 'J'
_alnum['\U0001d67a'] = 'K'
_alnum['\U0001d67b'] = 'L'
_alnum['\U0001d67c'] = 'M'
_alnum['\U0001d67d'] = 'N'
_alnum['\U0001d67e'] = 'O'
_alnum['\U0001d67f'] = 'P'
_alnum['\U0001d680'] = 'Q'
_alnum['\U0001d681'] = 'R'
_alnum['\U0001d682'] = 'S'
_alnum['\U0001d683'] = 'T'
_alnum['\U0001d684'] = 'U'
_alnum['\U0001d685'] = 'V'
_alnum['\U0001d686'] = 'W'
_alnum['\U0001d687'] = 'X'
_alnum['\U0001d688'] = 'Y'
_alnum['\U0001d689'] = 'Z'
_alnum['\U0001d68a'] = 'a'
_alnum['\U0001d68b'] = 'b'
_alnum['\U0001d68c'] = 'c'
_alnum['\U0001d68d'] = 'd'
_alnum['\U0001d68e'] = 'e'
_alnum['\U0001d68f'] = 'f'
_alnum['\U0001d690'] = 'g'
_alnum['\U0001d691'] = 'h'
_alnum['\U0001d692'] = 'i'
_alnum['\U0001d693'] = 'j'
_alnum['\U0001d694'] = 'k'
_alnum['\U0001d695'] = 'l'
_alnum['\U0001d696'] = 'm'
_alnum['\U0001d697'] = 'n'
_alnum['\U0001d698'] = 'o'
_alnum['\U0001d699'] = 'p'
_alnum['\U0001d69a'] = 'q'
_alnum['\U0001d69b'] = 'r'
_alnum['\U0001d69c'] = 's'
_alnum['\U0001d69d'] = 't'
_alnum['\U0001d69e'] = 'u'
_alnum['\U0001d69f'] = 'v'
_alnum['\U0001d6a0'] = 'w'
_alnum['\U0001d6a1'] = 'x'
_alnum['\U0001d6a2'] = 'y'
_alnum['\U0001d6a3'] = 'z'
_alnum['\U0001d6a4'] = 'i'
_alnum['\U0001d6a5'] = 'j'
_alnum['\U0001d6a8'] = 'Α'
_alnum['\U0001d6a9'] = 'Β'
_alnum['\U0001d6aa'] = 'Γ'
_alnum['\U0001d6ab'] = 'Δ'
_alnum['\U0001d6ac'] = 'Ε'
_alnum['\U0001d6ad'] = 'Ζ'
_alnum['\U0001d6ae'] = 'Η'
_alnum['\U0001d6af'] = 'ϴ'
_alnum['\U0001d6b0'] = 'Ι'
_alnum['\U0001d6b1'] = 'Κ'
_alnum['\U0001d6b2'] = 'Λ'
_alnum['\U0001d6b3'] = 'Μ'
_alnum['\U0001d6b4'] = 'Ν'
_alnum['\U0001d6b5'] = 'Ξ'
_alnum['\U0001d6b6'] = 'Ο'
_alnum['\U0001d6b7'] = 'Π'
_alnum['\U0001d6b8'] = 'Ρ'
_alnum['\U0001d6b9'] = 'ϴ'
_alnum['\U0001d6ba'] = 'Σ'
_alnum['\U0001d6bb'] = 'Τ'
_alnum['\U0001d6bc'] = 'Υ'
_alnum['\U0001d6bd'] = 'Φ'
_alnum['\U0001d6be'] = 'Χ'
_alnum['\U0001d6bf'] = 'Ψ'
_alnum['\U0001d6c0'] = 'Ω'
_alnum['\U0001d6c1'] = '∇'
_alnum['\U0001d6c2'] = 'α'
_alnum['\U0001d6c3'] = 'β'
_alnum['\U0001d6c4'] = 'γ'
_alnum['\U0001d6c5'] = 'δ'
_alnum['\U0001d6c6'] = 'ε'
_alnum['\U0001d6c7'] = 'ζ'
_alnum['\U0001d6c8'] = 'η'
_alnum['\U0001d6c9'] = 'θ'
_alnum['\U0001d6ca'] = 'ι'
_alnum['\U0001d6cb'] = 'κ'
_alnum['\U0001d6cc'] = 'λ'
_alnum['\U0001d6cd'] = 'μ'
_alnum['\U0001d6ce'] = 'ν'
_alnum['\U0001d6cf'] = 'ξ'
_alnum['\U0001d6d0'] = 'ο'
_alnum['\U0001d6d1'] = 'π'
_alnum['\U0001d6d2'] = 'ρ'
_alnum['\U0001d6d3'] = 'ς'
_alnum['\U0001d6d4'] = 'σ'
_alnum['\U0001d6d5'] = 'τ'
_alnum['\U0001d6d6'] = 'υ'
_alnum['\U0001d6d7'] = 'φ'
_alnum['\U0001d6d8'] = 'χ'
_alnum['\U0001d6d9'] = 'ψ'
_alnum['\U0001d6da'] = 'ω'
_alnum['\U0001d6db'] = '∂'
_alnum['\U0001d6dc'] = 'ϵ'
_alnum['\U0001d6dd'] = 'ϑ'
_alnum['\U0001d6de'] = 'ϰ'
_alnum['\U0001d6df'] = 'ϕ'
_alnum['\U0001d6e0'] = 'ϱ'
_alnum['\U0001d6e1'] = 'ϖ'
_alnum['\U0001d6e2'] = 'Α'
_alnum['\U0001d6e3'] = 'Β'
_alnum['\U0001d6e4'] = 'Γ'
_alnum['\U0001d6e5'] = 'Δ'
_alnum['\U0001d6e6'] = 'Ε'
_alnum['\U0001d6e7'] = 'Ζ'
_alnum['\U0001d6e8'] = 'Η'
_alnum['\U0001d6e9'] = 'ϴ'
_alnum['\U0001d6ea'] = 'Ι'
_alnum['\U0001d6eb'] = 'Κ'
_alnum['\U0001d6ec'] = 'Λ'
_alnum['\U0001d6ed'] = 'Μ'
_alnum['\U0001d6ee'] = 'Ν'
_alnum['\U0001d6ef'] = 'Ξ'
_alnum['\U0001d6f0'] = 'Ο'
_alnum['\U0001d6f1'] = 'Π'
_alnum['\U0001d6f2'] = 'Ρ'
_alnum['\U0001d6f3'] = 'ϴ'
_alnum['\U0001d6f4'] = 'Σ'
_alnum['\U0001d6f5'] = 'Τ'
_alnum['\U0001d6f6'] = 'Υ'
_alnum['\U0001d6f7'] = 'Φ'
_alnum['\U0001d6f8'] = 'Χ'
_alnum['\U0001d6f9'] = 'Ψ'
_alnum['\U0001d6fa'] = 'Ω'
_alnum['\U0001d6fb'] = '∇'
_alnum['\U0001d6fc'] = 'α'
_alnum['\U0001d6fd'] = 'β'
_alnum['\U0001d6fe'] = 'γ'
_alnum['\U0001d6ff'] = 'δ'
_alnum['\U0001d700'] = 'ε'
_alnum['\U0001d701'] = 'ζ'
_alnum['\U0001d702'] = 'η'
_alnum['\U0001d703'] = 'θ'
_alnum['\U0001d704'] = 'ι'
_alnum['\U0001d705'] = 'κ'
_alnum['\U0001d706'] = 'λ'
_alnum['\U0001d707'] = 'μ'
_alnum['\U0001d708'] = 'ν'
_alnum['\U0001d709'] = 'ξ'
_alnum['\U0001d70a'] = 'ο'
_alnum['\U0001d70b'] = 'π'
_alnum['\U0001d70c'] = 'ρ'
_alnum['\U0001d70d'] = 'ς'
_alnum['\U0001d70e'] = 'σ'
_alnum['\U0001d70f'] = 'τ'
_alnum['\U0001d710'] = 'υ'
_alnum['\U0001d711'] = 'φ'
_alnum['\U0001d712'] = 'χ'
_alnum['\U0001d713'] = 'ψ'
_alnum['\U0001d714'] = 'ω'
_alnum['\U0001d715'] = '∂'
_alnum['\U0001d716'] = 'ϵ'
_alnum['\U0001d717'] = 'ϑ'
_alnum['\U0001d718'] = 'ϰ'
_alnum['\U0001d719'] = 'ϕ'
_alnum['\U0001d71a'] = 'ϱ'
_alnum['\U0001d71b'] = 'ϖ'
_alnum['\U0001d71c'] = 'Α'
_alnum['\U0001d71d'] = 'Β'
_alnum['\U0001d71e'] = 'Γ'
_alnum['\U0001d71f'] = 'Δ'
_alnum['\U0001d720'] = 'Ε'
_alnum['\U0001d721'] = 'Ζ'
_alnum['\U0001d722'] = 'Η'
_alnum['\U0001d723'] = 'ϴ'
_alnum['\U0001d724'] = 'Ι'
_alnum['\U0001d725'] = 'Κ'
_alnum['\U0001d726'] = 'Λ'
_alnum['\U0001d727'] = 'Μ'
_alnum['\U0001d728'] = 'Ν'
_alnum['\U0001d729'] = 'Ξ'
_alnum['\U0001d72a'] = 'Ο'
_alnum['\U0001d72b'] = 'Π'
_alnum['\U0001d72c'] = 'Ρ'
_alnum['\U0001d72d'] = 'ϴ'
_alnum['\U0001d72e'] = 'Σ'
_alnum['\U0001d72f'] = 'Τ'
_alnum['\U0001d730'] = 'Υ'
_alnum['\U0001d731'] = 'Φ'
_alnum['\U0001d732'] = 'Χ'
_alnum['\U0001d733'] = 'Ψ'
_alnum['\U0001d734'] = 'Ω'
_alnum['\U0001d735'] = '∇'
_alnum['\U0001d736'] = 'α'
_alnum['\U0001d737'] = 'β'
_alnum['\U0001d738'] = 'γ'
_alnum['\U0001d739'] = 'δ'
_alnum['\U0001d73a'] = 'ε'
_alnum['\U0001d73b'] = 'ζ'
_alnum['\U0001d73c'] = 'η'
_alnum['\U0001d73d'] = 'θ'
_alnum['\U0001d73e'] = 'ι'
_alnum['\U0001d73f'] = 'κ'
_alnum['\U0001d740'] = 'λ'
_alnum['\U0001d741'] = 'μ'
_alnum['\U0001d742'] = 'ν'
_alnum['\U0001d743'] = 'ξ'
_alnum['\U0001d744'] = 'ο'
_alnum['\U0001d745'] = 'π'
_alnum['\U0001d746'] = 'ρ'
_alnum['\U0001d747'] = 'ς'
_alnum['\U0001d748'] = 'σ'
_alnum['\U0001d749'] = 'τ'
_alnum['\U0001d74a'] = 'υ'
_alnum['\U0001d74b'] = 'φ'
_alnum['\U0001d74c'] = 'χ'
_alnum['\U0001d74d'] = 'ψ'
_alnum['\U0001d74e'] = 'ω'
_alnum['\U0001d74f'] = '∂'
_alnum['\U0001d750'] = 'ϵ'
_alnum['\U0001d751'] = 'ϑ'
_alnum['\U0001d752'] = 'ϰ'
_alnum['\U0001d753'] = 'ϕ'
_alnum['\U0001d754'] = 'ϱ'
_alnum['\U0001d755'] = 'ϖ'
_alnum['\U0001d756'] = 'Α'
_alnum['\U0001d757'] = 'Β'
_alnum['\U0001d758'] = 'Γ'
_alnum['\U0001d759'] = 'Δ'
_alnum['\U0001d75a'] = 'Ε'
_alnum['\U0001d75b'] = 'Ζ'
_alnum['\U0001d75c'] = 'Η'
_alnum['\U0001d75d'] = 'ϴ'
_alnum['\U0001d75e'] = 'Ι'
_alnum['\U0001d75f'] = 'Κ'
_alnum['\U0001d760'] = 'Λ'
_alnum['\U0001d761'] = 'Μ'
_alnum['\U0001d762'] = 'Ν'
_alnum['\U0001d763'] = 'Ξ'
_alnum['\U0001d764'] = 'Ο'
_alnum['\U0001d765'] = 'Π'
_alnum['\U0001d766'] = 'Ρ'
_alnum['\U0001d767'] = 'ϴ'
_alnum['\U0001d768'] = 'Σ'
_alnum['\U0001d769'] = 'Τ'
_alnum['\U0001d76a'] = 'Υ'
_alnum['\U0001d76b'] = 'Φ'
_alnum['\U0001d76c'] = 'Χ'
_alnum['\U0001d76d'] = 'Ψ'
_alnum['\U0001d76e'] = 'Ω'
_alnum['\U0001d76f'] = '∇'
_alnum['\U0001d770'] = 'α'
_alnum['\U0001d771'] = 'β'
_alnum['\U0001d772'] = 'γ'
_alnum['\U0001d773'] = 'δ'
_alnum['\U0001d774'] = 'ε'
_alnum['\U0001d775'] = 'ζ'
_alnum['\U0001d776'] = 'η'
_alnum['\U0001d777'] = 'θ'
_alnum['\U0001d778'] = 'ι'
_alnum['\U0001d779'] = 'κ'
_alnum['\U0001d77a'] = 'λ'
_alnum['\U0001d77b'] = 'μ'
_alnum['\U0001d77c'] = 'ν'
_alnum['\U0001d77d'] = 'ξ'
_alnum['\U0001d77e'] = 'ο'
_alnum['\U0001d77f'] = 'π'
_alnum['\U0001d780'] = 'ρ'
_alnum['\U0001d781'] = 'ς'
_alnum['\U0001d782'] = 'σ'
_alnum['\U0001d783'] = 'τ'
_alnum['\U0001d784'] = 'υ'
_alnum['\U0001d785'] = 'φ'
_alnum['\U0001d786'] = 'χ'
_alnum['\U0001d787'] = 'ψ'
_alnum['\U0001d788'] = 'ω'
_alnum['\U0001d789'] = '∂'
_alnum['\U0001d78a'] = 'ϵ'
_alnum['\U0001d78b'] = 'ϑ'
_alnum['\U0001d78c'] = 'ϰ'
_alnum['\U0001d78d'] = 'ϕ'
_alnum['\U0001d78e'] = 'ϱ'
_alnum['\U0001d78f'] = 'ϖ'
_alnum['\U0001d790'] = 'Α'
_alnum['\U0001d791'] = 'Β'
_alnum['\U0001d792'] = 'Γ'
_alnum['\U0001d793'] = 'Δ'
_alnum['\U0001d794'] = 'Ε'
_alnum['\U0001d795'] = 'Ζ'
_alnum['\U0001d796'] = 'Η'
_alnum['\U0001d797'] = 'ϴ'
_alnum['\U0001d798'] = 'Ι'
_alnum['\U0001d799'] = 'Κ'
_alnum['\U0001d79a'] = 'Λ'
_alnum['\U0001d79b'] = 'Μ'
_alnum['\U0001d79c'] = 'Ν'
_alnum['\U0001d79d'] = 'Ξ'
_alnum['\U0001d79e'] = 'Ο'
_alnum['\U0001d79f'] = 'Π'
_alnum['\U0001d7a0'] = 'Ρ'
_alnum['\U0001d7a1'] = 'ϴ'
_alnum['\U0001d7a2'] = 'Σ'
_alnum['\U0001d7a3'] = 'Τ'
_alnum['\U0001d7a4'] = 'Υ'
_alnum['\U0001d7a5'] = 'Φ'
_alnum['\U0001d7a6'] = 'Χ'
_alnum['\U0001d7a7'] = 'Ψ'
_alnum['\U0001d7a8'] = 'Ω'
_alnum['\U0001d7a9'] = '∇'
_alnum['\U0001d7aa'] = 'α'
_alnum['\U0001d7ab'] = 'β'
_alnum['\U0001d7ac'] = 'γ'
_alnum['\U0001d7ad'] = 'δ'
_alnum['\U0001d7ae'] = 'ε'
_alnum['\U0001d7af'] = 'ζ'
_alnum['\U0001d7b0'] = 'η'
_alnum['\U0001d7b1'] = 'θ'
_alnum['\U0001d7b2'] = 'ι'
_alnum['\U0001d7b3'] = 'κ'
_alnum['\U0001d7b4'] = 'λ'
_alnum['\U0001d7b5'] = 'μ'
_alnum['\U0001d7b6'] = 'ν'
_alnum['\U0001d7b7'] = 'ξ'
_alnum['\U0001d7b8'] = 'ο'
_alnum['\U0001d7b9'] = 'π'
_alnum['\U0001d7ba'] = 'ρ'
_alnum['\U0001d7bb'] = 'ς'
_alnum['\U0001d7bc'] = 'σ'
_alnum['\U0001d7bd'] = 'τ'
_alnum['\U0001d7be'] = 'υ'
_alnum['\U0001d7bf'] = 'φ'
_alnum['\U0001d7c0'] = 'χ'
_alnum['\U0001d7c1'] = 'ψ'
_alnum['\U0001d7c2'] = 'ω'
_alnum['\U0001d7c3'] = '∂'
_alnum['\U0001d7c4'] = 'ϵ'
_alnum['\U0001d7c5'] = 'ϑ'
_alnum['\U0001d7c6'] = 'ϰ'
_alnum['\U0001d7c7'] = 'ϕ'
_alnum['\U0001d7c8'] = 'ϱ'
_alnum['\U0001d7c9'] = 'ϖ'
_alnum['\U0001d7ca'] = 'Ϝ'
_alnum['\U0001d7cb'] = 'ϝ'
_alnum['\U0001d7ce'] = '0'
_alnum['\U0001d7cf'] = '1'
_alnum['\U0001d7d0'] = '2'
_alnum['\U0001d7d1'] = '3'
_alnum['\U0001d7d2'] = '4'
_alnum['\U0001d7d3'] = '5'
_alnum['\U0001d7d4'] = '6'
_alnum['\U0001d7d5'] = '7'
_alnum['\U0001d7d6'] = '8'
_alnum['\U0001d7d7'] = '9'
_alnum['\U0001d7d8'] = '0'
_alnum['\U0001d7d9'] = '1'
_alnum['\U0001d7da'] = '2'
_alnum['\U0001d7db'] = '3'
_alnum['\U0001d7dc'] = '4'
_alnum['\U0001d7dd'] = '5'
_alnum['\U0001d7de'] = '6'
_alnum['\U0001d7df'] = '7'
_alnum['\U0001d7e0'] = '8'
_alnum['\U0001d7e1'] = '9'
_alnum['\U0001d7e2'] = '0'
_alnum['\U0001d7e3'] = '1'
_alnum['\U0001d7e4'] = '2'
_alnum['\U0001d7e5'] = '3'
_alnum['\U0001d7e6'] = '4'
_alnum['\U0001d7e7'] = '5'
_alnum['\U0001d7e8'] = '6'
_alnum['\U0001d7e9'] = '7'
_alnum['\U0001d7ea'] = '8'
_alnum['\U0001d7eb'] = '9'
_alnum['\U0001d7ec'] = '0'
_alnum['\U0001d7ed'] = '1'
_alnum['\U0001d7ee'] = '2'
_alnum['\U0001d7ef'] = '3'
_alnum['\U0001d7f0'] = '4'
_alnum['\U0001d7f1'] = '5'
_alnum['\U0001d7f2'] = '6'
_alnum['\U0001d7f3'] = '7'
_alnum['\U0001d7f4'] = '8'
_alnum['\U0001d7f5'] = '9'
_alnum['\U0001d7f6'] = '0'
_alnum['\U0001d7f7'] = '1'
_alnum['\U0001d7f8'] = '2'
_alnum['\U0001d7f9'] = '3'
_alnum['\U0001d7fa'] = '4'
_alnum['\U0001d7fb'] = '5'
_alnum['\U0001d7fc'] = '6'
_alnum['\U0001d7fd'] = '7'
_alnum['\U0001d7fe'] = '8'
_alnum['\U0001d7ff'] = '9'

_bold = range(0x1d400, 0x1d434)
_italic = range(0x1d434, 0x1d468)
_boldItalic = range(0x1d468, 0x1d49c)
_script = range(0x1d49c, 0x1d4d0)
_boldScript = range(0x1d4d0, 0x1d504)
_fraktur = range(0x1d504, 0x1d538)
_doubleStruck = range(0x1d538, 0x1d56c)
_boldFraktur = range(0x1d56c, 0x1d5a0)
_sansSerif = range(0x1d5a0, 0x1d5d4)
_sansSerifBold = range(0x1d5d4, 0x1d608)
_sansSerifItalic = range(0x1d608, 0x1d63c)
_sansSerifBoldItalic = range(0x1d63c, 0x1d670)
_monospace = range(0x1d670, 0x1d6a4)
_dotless = range(0x1d6a4, 0x1d6a8)
_boldGreek = range(0x1d6a8, 0x1d6e2)
_italicGreek = range(0x1d6e2, 0x1d71c)
_boldItalicGreek = range(0x1d71c, 0x1d756)
_sansSerifBoldGreek = range(0x1d756, 0x1d790)
_sansSerifBoldItalicGreek = range(0x1d790, 0x1d7ca)
_boldGreekDigamma = range(0x1d7ca, 0x1d7cc)
_boldDigits = range(0x1d7ce, 0x1d7d8)
_doubleStruckDigits = range(0x1d7d8, 0x1d7e2)
_sansSerifDigits = range(0x1d7e2, 0x1d7ec)
_sansSerifBoldDigits = range(0x1d7ec, 0x1d7f6)
_monospaceDigits = range(0x1d7f6, 0x1d800)
_otherDoubleStruck = [0x2102, 0x210d, 0x2115, 0x2119, 0x211a, 0x211d, 0x2124]
_otherFraktur = [0x212d, 0x210c, 0x2111, 0x211c, 0x2128]
_otherItalic = [0x210e]
_otherScript = [0x212c,
                0x2130,
                0x2131,
                0x210b,
                0x2110,
                0x2112,
                0x2133,
                0x211b,
                0x212f,
                0x210a,
                0x2134]

# Translators: Unicode has a large set of characters consisting of a common
# alphanumeric symbol and a style. For instance, character 1D400 is a bold A,
# 1D468 is a bold italic A, 1D4D0 is a bold script A,, etc., etc. These styles
# can have specific meanings in mathematics and thus should be spoken along
# with the alphanumeric character. However, given the vast quantity of these
# characters, string substitution is being used with the substituted string
# being a single alphanumeric character. The full set of symbols can be found
# at http://www.unicode.org/charts/PDF/U1D400.pdf.
BOLD = C_('math symbol', 'bold %s')

# Translators: Unicode has a large set of characters consisting of a common
# alphanumeric symbol and a style. For instance, character 1D400 is a bold A,
# 1D468 is a bold italic A, 1D4D0 is a bold script A,, etc., etc. These styles
# can have specific meanings in mathematics and thus should be spoken along
# with the alphanumeric character. However, given the vast quantity of these
# characters, string substitution is being used with the substituted string
# being a single alphanumeric character. The full set of symbols can be found
# at http://www.unicode.org/charts/PDF/U1D400.pdf.
ITALIC = C_('math symbol', 'italic %s')

# Translators: Unicode has a large set of characters consisting of a common
# alphanumeric symbol and a style. For instance, character 1D400 is a bold A,
# 1D468 is a bold italic A, 1D4D0 is a bold script A,, etc., etc. These styles
# can have specific meanings in mathematics and thus should be spoken along
# with the alphanumeric character. However, given the vast quantity of these
# characters, string substitution is being used with the substituted string
# being a single alphanumeric character. The full set of symbols can be found
# at http://www.unicode.org/charts/PDF/U1D400.pdf.
BOLD_ITALIC = C_('math symbol', 'bold italic %s')

# Translators: Unicode has a large set of characters consisting of a common
# alphanumeric symbol and a style. For instance, character 1D400 is a bold A,
# 1D468 is a bold italic A, 1D4D0 is a bold script A,, etc., etc. These styles
# can have specific meanings in mathematics and thus should be spoken along
# with the alphanumeric character. However, given the vast quantity of these
# characters, string substitution is being used with the substituted string
# being a single alphanumeric character. The full set of symbols can be found
# at http://www.unicode.org/charts/PDF/U1D400.pdf.
SCRIPT = C_('math symbol', 'script %s')

# Translators: Unicode has a large set of characters consisting of a common
# alphanumeric symbol and a style. For instance, character 1D400 is a bold A,
# 1D468 is a bold italic A, 1D4D0 is a bold script A,, etc., etc. These styles
# can have specific meanings in mathematics and thus should be spoken along
# with the alphanumeric character. However, given the vast quantity of these
# characters, string substitution is being used with the substituted string
# being a single alphanumeric character. The full set of symbols can be found
# at http://www.unicode.org/charts/PDF/U1D400.pdf.
BOLD_SCRIPT = C_('math symbol', 'bold script %s')

# Translators: Unicode has a large set of characters consisting of a common
# alphanumeric symbol and a style. For instance, character 1D400 is a bold A,
# 1D468 is a bold italic A, 1D4D0 is a bold script A,, etc., etc. These styles
# can have specific meanings in mathematics and thus should be spoken along
# with the alphanumeric character. However, given the vast quantity of these
# characters, string substitution is being used with the substituted string
# being a single alphanumeric character. The full set of symbols can be found
# at http://www.unicode.org/charts/PDF/U1D400.pdf.
FRAKTUR = C_('math symbol', 'fraktur %s')

# Translators: Unicode has a large set of characters consisting of a common
# alphanumeric symbol and a style. For instance, character 1D400 is a bold A,
# 1D468 is a bold italic A, 1D4D0 is a bold script A,, etc., etc. These styles
# can have specific meanings in mathematics and thus should be spoken along
# with the alphanumeric character. However, given the vast quantity of these
# characters, string substitution is being used with the substituted string
# being a single alphanumeric character. The full set of symbols can be found
# at http://www.unicode.org/charts/PDF/U1D400.pdf.
DOUBLE_STRUCK = C_('math symbol', 'double-struck %s')

# Translators: Unicode has a large set of characters consisting of a common
# alphanumeric symbol and a style. For instance, character 1D400 is a bold A,
# 1D468 is a bold italic A, 1D4D0 is a bold script A,, etc., etc. These styles
# can have specific meanings in mathematics and thus should be spoken along
# with the alphanumeric character. However, given the vast quantity of these
# characters, string substitution is being used with the substituted string
# being a single alphanumeric character. The full set of symbols can be found
# at http://www.unicode.org/charts/PDF/U1D400.pdf.
BOLD_FRAKTUR = C_('math symbol', 'bold fraktur %s')

# Translators: Unicode has a large set of characters consisting of a common
# alphanumeric symbol and a style. For instance, character 1D400 is a bold A,
# 1D468 is a bold italic A, 1D4D0 is a bold script A,, etc., etc. These styles
# can have specific meanings in mathematics and thus should be spoken along
# with the alphanumeric character. However, given the vast quantity of these
# characters, string substitution is being used with the substituted string
# being a single alphanumeric character. The full set of symbols can be found
# at http://www.unicode.org/charts/PDF/U1D400.pdf.
SANS_SERIF = C_('math symbol', 'sans-serif %s')

# Translators: Unicode has a large set of characters consisting of a common
# alphanumeric symbol and a style. For instance, character 1D400 is a bold A,
# 1D468 is a bold italic A, 1D4D0 is a bold script A,, etc., etc. These styles
# can have specific meanings in mathematics and thus should be spoken along
# with the alphanumeric character. However, given the vast quantity of these
# characters, string substitution is being used with the substituted string
# being a single alphanumeric character. The full set of symbols can be found
# at http://www.unicode.org/charts/PDF/U1D400.pdf.
SANS_SERIF_BOLD = C_('math symbol', 'sans-serif bold %s')

# Translators: Unicode has a large set of characters consisting of a common
# alphanumeric symbol and a style. For instance, character 1D400 is a bold A,
# 1D468 is a bold italic A, 1D4D0 is a bold script A,, etc., etc. These styles
# can have specific meanings in mathematics and thus should be spoken along
# with the alphanumeric character. However, given the vast quantity of these
# characters, string substitution is being used with the substituted string
# being a single alphanumeric character. The full set of symbols can be found
# at http://www.unicode.org/charts/PDF/U1D400.pdf.
SANS_SERIF_ITALIC = C_('math symbol', 'sans-serif italic %s')

# Translators: Unicode has a large set of characters consisting of a common
# alphanumeric symbol and a style. For instance, character 1D400 is a bold A,
# 1D468 is a bold italic A, 1D4D0 is a bold script A,, etc., etc. These styles
# can have specific meanings in mathematics and thus should be spoken along
# with the alphanumeric character. However, given the vast quantity of these
# characters, string substitution is being used with the substituted string
# being a single alphanumeric character. The full set of symbols can be found
# at http://www.unicode.org/charts/PDF/U1D400.pdf.
SANS_SERIF_BOLD_ITALIC = C_('math symbol', 'sans-serif bold italic %s')

# Translators: Unicode has a large set of characters consisting of a common
# alphanumeric symbol and a style. For instance, character 1D400 is a bold A,
# 1D468 is a bold italic A, 1D4D0 is a bold script A,, etc., etc. These styles
# can have specific meanings in mathematics and thus should be spoken along
# with the alphanumeric character. However, given the vast quantity of these
# characters, string substitution is being used with the substituted string
# being a single alphanumeric character. The full set of symbols can be found
# at http://www.unicode.org/charts/PDF/U1D400.pdf.
MONOSPACE = C_('math symbol', 'monospace %s')

# Translators: Unicode has a large set of characters consisting of a common
# alphanumeric symbol and a style. For instance, character 1D400 is a bold A,
# 1D468 is a bold italic A, 1D4D0 is a bold script A,, etc., etc. These styles
# can have specific meanings in mathematics and thus should be spoken along
# with the alphanumeric character. However, given the vast quantity of these
# characters, string substitution is being used with the substituted string
# being a single alphanumeric character. The full set of symbols can be found
# at http://www.unicode.org/charts/PDF/U1D400.pdf.
DOTLESS = C_('math symbol', 'dotless %s')

# Translators: this is the spoken representation for the character '←' (U+2190)
_arrows['\u2190'] = C_('math symbol', 'left arrow')

# Translators: this is the spoken representation for the character '↑' (U+2191)
_arrows['\u2191'] = C_('math symbol', 'up arrow')

# Translators: this is the spoken representation for the character '→' (U+2192)
_arrows['\u2192'] = C_('math symbol', 'right arrow')

# Translators: this is the spoken representation for the character '↓' (U+2193)
_arrows['\u2193'] = C_('math symbol', 'down arrow')

# Translators: this is the spoken representation for the character '↔' (U+2194)
_arrows['\u2194'] = C_('math symbol', 'left right arrow')

# Translators: this is the spoken representation for the character '↕' (U+2195)
_arrows['\u2195'] = C_('math symbol', 'up down arrow')

# Translators: this is the spoken representation for the character '↖' (U+2196)
_arrows['\u2196'] = C_('math symbol', 'north west arrow')

# Translators: this is the spoken representation for the character '↗' (U+2197)
_arrows['\u2197'] = C_('math symbol', 'north east arrow')

# Translators: this is the spoken representation for the character '↘' (U+2198)
_arrows['\u2198'] = C_('math symbol', 'south east arrow')

# Translators: this is the spoken representation for the character '↤' (U+21a4)
_arrows['\u21a4'] = C_('math symbol', 'left arrow from bar')

# Translators: this is the spoken representation for the character '↥' (U+21a5)
_arrows['\u21a5'] = C_('math symbol', 'up arrow from bar')

# Translators: this is the spoken representation for the character '↦' (U+21a6)
_arrows['\u21a6'] = C_('math symbol', 'right arrow from bar')

# Translators: this is the spoken representation for the character '↧' (U+21a7)
_arrows['\u21a7'] = C_('math symbol', 'down arrow from bar')

# Translators: this is the spoken representation for the character '⇐' (U+21d0)
_arrows['\u21d0'] = C_('math symbol', 'left double arrow')

# Translators: this is the spoken representation for the character '⇑' (U+21d1)
_arrows['\u21d1'] = C_('math symbol', 'up double arrow')

# Translators: this is the spoken representation for the character '⇒' (U+21d2)
_arrows['\u21d2'] = C_('math symbol', 'right double arrow')

# Translators: this is the spoken representation for the character '⇓' (U+21d3)
_arrows['\u21d3'] = C_('math symbol', 'down double arrow')

# Translators: this is the spoken representation for the character '⇔' (U+21d4)
_arrows['\u21d4'] = C_('math symbol', 'left right double arrow')

# Translators: this is the spoken representation for the character '⇕' (U+21d5)
_arrows['\u21d5'] = C_('math symbol', 'up down double arrow')

# Translators: this is the spoken representation for the character '⇖' (U+21d6)
_arrows['\u21d6'] = C_('math symbol', 'north west double arrow')

# Translators: this is the spoken representation for the character '⇗' (U+21d7)
_arrows['\u21d7'] = C_('math symbol', 'north east double arrow')

# Translators: this is the spoken representation for the character '⇘' (U+21d8)
_arrows['\u21d8'] = C_('math symbol', 'south east double arrow')

# Translators: this is the spoken representation for the character '⇙' (U+21d9)
_arrows['\u21d9'] = C_('math symbol', 'south west double arrow')

# Translators: this is the spoken representation for the character '➔' (U+2794)
_arrows['\u2794'] = C_('math symbol', 'right-pointing arrow')

# Translators: this is the spoken representation for the character '➢' (U+27a2)
_arrows['\u27a2'] = C_('math symbol', 'right-pointing arrowhead')

# Translators: this is the spoken word for the character '-' (U+002d) when used
# as a MathML operator.
_operators["\u002d"] = C_('math symbol', 'minus')

# Translators: this is the spoken word for the character '<' (U+003c) when used
# as a MathML operator.
_operators["\u003c"] = C_('math symbol', 'less than')

# Translators: this is the spoken word for the character '>' (U+003e) when used
# as a MathML operator.
_operators["\u003e"] = C_('math symbol', 'greater than')

# Translators: this is the spoken word for the character '^' (U+005e) when used
# as a MathML operator.
_operators['\u005e'] = C_('math symbol', 'circumflex')

# Translators: this is the spoken word for the character 'ˇ' (U+02c7) when used
# as a MathML operator.
_operators['\u02c7'] = C_('math symbol', 'háček')

# Translators: this is the spoken word for the character '˘' (U+02d8) when used
# as a MathML operator.
_operators['\u02d8'] = C_('math symbol', 'breve')

# Translators: this is the spoken word for the character '˙' (U+02d9) when used
# as a MathML operator.
_operators['\u02d9'] = C_('math symbol', 'dot')

# Translators: this is the spoken word for the character '‖' (U+2016) when used
# as a MathML operator.
_operators['\u2016'] = C_('math symbol', 'double vertical line')

# Translators: this is the spoken representation for the character '…' (U+2026)
_operators['\u2026'] = C_('math symbol', 'horizontal ellipsis')

# Translators: this is the spoken representation for the character '∀' (U+2200)
_operators['\u2200'] = C_('math symbol', 'for all')

# Translators: this is the spoken representation for the character '∁' (U+2201)
_operators['\u2201'] = C_('math symbol', 'complement')

# Translators: this is the spoken representation for the character '∂' (U+2202)
_operators['\u2202'] = C_('math symbol', 'partial differential')

# Translators: this is the spoken representation for the character '∃' (U+2203)
_operators['\u2203'] = C_('math symbol', 'there exists')

# Translators: this is the spoken representation for the character '∄' (U+2204)
_operators['\u2204'] = C_('math symbol', 'there does not exist')

# Translators: this is the spoken representation for the character '∅' (U+2205)
_operators['\u2205'] = C_('math symbol', 'empty set')

# Translators: this is the spoken representation for the character '∆' (U+2206)
_operators['\u2206'] = C_('math symbol', 'increment')

# Translators: this is the spoken representation for the character '∇' (U+2207)
_operators['\u2207'] = C_('math symbol', 'nabla')

# Translators: this is the spoken representation for the character '∈' (U+2208)
_operators['\u2208'] = C_('math symbol', 'element of')

# Translators: this is the spoken representation for the character '∉' (U+2209)
_operators['\u2209'] = C_('math symbol', 'not an element of')

# Translators: this is the spoken representation for the character '∊' (U+220a)
_operators['\u220a'] = C_('math symbol', 'small element of')

# Translators: this is the spoken representation for the character '∋' (U+220b)
_operators['\u220b'] = C_('math symbol', 'contains as a member')

# Translators: this is the spoken representation for the character '∌' (U+220c)
_operators['\u220c'] = C_('math symbol', 'does not contain as a member')

# Translators: this is the spoken representation for the character '∍' (U+220d)
_operators['\u220d'] = C_('math symbol', 'small contains as a member')

# Translators: this is the spoken representation for the character '∎' (U+220e)
_operators['\u220e'] = C_('math symbol', 'end of proof')

# Translators: this is the spoken representation for the character '∏' (U+220f)
_operators['\u220f'] = C_('math symbol', 'product')

# Translators: this is the spoken representation for the character '∐' (U+2210)
_operators['\u2210'] = C_('math symbol', 'coproduct')

# Translators: this is the spoken representation for the character '∑' (U+2211)
_operators['\u2211'] = C_('math symbol', 'sum')

# Translators: this is the spoken representation for the character '−' (U+2212)
_operators['\u2212'] = C_('math symbol', 'minus')

# Translators: this is the spoken representation for the character '∓' (U+2213)
_operators['\u2213'] = C_('math symbol', 'minus or plus')

# Translators: this is the spoken representation for the character '∔' (U+2214)
_operators['\u2214'] = C_('math symbol', 'dot plus')

# Translators: this is the spoken representation for the character '∕' (U+2215)
_operators['\u2215'] = C_('math symbol', 'division slash')

# Translators: this is the spoken representation for the character '∖' (U+2216)
_operators['\u2216'] = C_('math symbol', 'set minus')

# Translators: this is the spoken representation for the character '∗' (U+2217)
_operators['\u2217'] = C_('math symbol', 'asterisk operator')

# Translators: this is the spoken representation for the character '∘' (U+2218)
_operators['\u2218'] = C_('math symbol', 'ring operator')

# Translators: this is the spoken representation for the character '∙' (U+2219)
_operators['\u2219'] = C_('math symbol', 'bullet operator')

# Translators: this is the spoken representation for the character '√' (U+221a)
_operators['\u221a'] = C_('math symbol', 'square root')

# Translators: this is the spoken representation for the character '∛' (U+221b)
_operators['\u221b'] = C_('math symbol', 'cube root')

# Translators: this is the spoken representation for the character '∜' (U+221c)
_operators['\u221c'] = C_('math symbol', 'fourth root')

# Translators: this is the spoken representation for the character '∝' (U+221d)
_operators['\u221d'] = C_('math symbol', 'proportional to')

# Translators: this is the spoken representation for the character '∞' (U+221e)
_operators['\u221e'] = C_('math symbol', 'infinity')

# Translators: this is the spoken representation for the character '∟' (U+221f)
_operators['\u221f'] = C_('math symbol', 'right angle')

# Translators: this is the spoken representation for the character '∠' (U+2220)
_operators['\u2220'] = C_('math symbol', 'angle')

# Translators: this is the spoken representation for the character '∡' (U+2221)
_operators['\u2221'] = C_('math symbol', 'measured angle')

# Translators: this is the spoken representation for the character '∢' (U+2222)
_operators['\u2222'] = C_('math symbol', 'spherical angle')

# Translators: this is the spoken representation for the character '∣' (U+2223)
_operators['\u2223'] = C_('math symbol', 'divides')

# Translators: this is the spoken representation for the character '∤' (U+2224)
_operators['\u2224'] = C_('math symbol', 'does not divide')

# Translators: this is the spoken representation for the character '∥' (U+2225)
_operators['\u2225'] = C_('math symbol', 'parallel to')

# Translators: this is the spoken representation for the character '∦' (U+2226)
_operators['\u2226'] = C_('math symbol', 'not parallel to')

# Translators: this is the spoken representation for the character '∧' (U+2227)
_operators['\u2227'] = C_('math symbol', 'logical and')

# Translators: this is the spoken representation for the character '∨' (U+2228)
_operators['\u2228'] = C_('math symbol', 'logical or')

# Translators: this is the spoken representation for the character '∩' (U+2229)
_operators['\u2229'] = C_('math symbol', 'intersection')

# Translators: this is the spoken representation for the character '∪' (U+222a)
_operators['\u222a'] = C_('math symbol', 'union')

# Translators: this is the spoken representation for the character '∫' (U+222b)
_operators['\u222b'] = C_('math symbol', 'integral')

# Translators: this is the spoken representation for the character '∬' (U+222c)
_operators['\u222c'] = C_('math symbol', 'double integral')

# Translators: this is the spoken representation for the character '∭' (U+222d)
_operators['\u222d'] = C_('math symbol', 'triple integral')

# Translators: this is the spoken representation for the character '∮' (U+222e)
_operators['\u222e'] = C_('math symbol', 'contour integral')

# Translators: this is the spoken representation for the character '∯' (U+222f)
_operators['\u222f'] = C_('math symbol', 'surface integral')

# Translators: this is the spoken representation for the character '∰' (U+2230)
_operators['\u2230'] = C_('math symbol', 'volume integral')

# Translators: this is the spoken representation for the character '∱' (U+2231)
_operators['\u2231'] = C_('math symbol', 'clockwise integral')

# Translators: this is the spoken representation for the character '∲' (U+2232)
_operators['\u2232'] = C_('math symbol', 'clockwise contour integral')

# Translators: this is the spoken representation for the character '∳' (U+2233)
_operators['\u2233'] = C_('math symbol', 'anticlockwise contour integral')

# Translators: this is the spoken representation for the character '∴' (U+2234)
_operators['\u2234'] = C_('math symbol', 'therefore')

# Translators: this is the spoken representation for the character '∵' (U+2235)
_operators['\u2235'] = C_('math symbol', 'because')

# Translators: this is the spoken representation for the character '∶' (U+2236)
_operators['\u2236'] = C_('math symbol', 'ratio')

# Translators: this is the spoken representation for the character '∷' (U+2237)
_operators['\u2237'] = C_('math symbol', 'proportion')

# Translators: this is the spoken representation for the character '∸' (U+2238)
_operators['\u2238'] = C_('math symbol', 'dot minus')

# Translators: this is the spoken representation for the character '∹' (U+2239)
_operators['\u2239'] = C_('math symbol', 'excess')

# Translators: this is the spoken representation for the character '∺' (U+223a)
_operators['\u223a'] = C_('math symbol', 'geometric proportion')

# Translators: this is the spoken representation for the character '∻' (U+223b)
_operators['\u223b'] = C_('math symbol', 'homothetic')

# Translators: this is the spoken representation for the character '∼' (U+223c)
_operators['\u223c'] = C_('math symbol', 'tilde')

# Translators: this is the spoken representation for the character '∽' (U+223d)
_operators['\u223d'] = C_('math symbol', 'reversed tilde')

# Translators: this is the spoken representation for the character '∾' (U+223e)
_operators['\u223e'] = C_('math symbol', 'inverted lazy S')

# Translators: this is the spoken representation for the character '∿' (U+223f)
_operators['\u223f'] = C_('math symbol', 'sine wave')

# Translators: this is the spoken representation for the character '≀' (U+2240)
_operators['\u2240'] = C_('math symbol', 'wreath product')

# Translators: this is the spoken representation for the character '≁' (U+2241)
_operators['\u2241'] = C_('math symbol', 'not tilde')

# Translators: this is the spoken representation for the character '≂' (U+2242)
_operators['\u2242'] = C_('math symbol', 'minus tilde')

# Translators: this is the spoken representation for the character '≃' (U+2243)
_operators['\u2243'] = C_('math symbol', 'asymptotically equal to')

# Translators: this is the spoken representation for the character '≄' (U+2244)
_operators['\u2244'] = C_('math symbol', 'not asymptotically equal to')

# Translators: this is the spoken representation for the character '≅' (U+2245)
_operators['\u2245'] = C_('math symbol', 'approximately equal to')

# Translators: this is the spoken representation for the character '≆' (U+2246)
_operators['\u2246'] = C_('math symbol', 'approximately but not actually equal to')

# Translators: this is the spoken representation for the character '≇' (U+2247)
_operators['\u2247'] = C_('math symbol', 'neither approximately nor actually equal to')

# Translators: this is the spoken representation for the character '≈' (U+2248)
_operators['\u2248'] = C_('math symbol', 'almost equal to')

# Translators: this is the spoken representation for the character '≉' (U+2249)
_operators['\u2249'] = C_('math symbol', 'not almost equal to')

# Translators: this is the spoken representation for the character '≊' (U+224a)
_operators['\u224a'] = C_('math symbol', 'almost equal or equal to')

# Translators: this is the spoken representation for the character '≋' (U+224b)
_operators['\u224b'] = C_('math symbol', 'triple tilde')

# Translators: this is the spoken representation for the character '≌' (U+224c)
_operators['\u224c'] = C_('math symbol', 'all equal to')

# Translators: this is the spoken representation for the character '≍' (U+224d)
_operators['\u224d'] = C_('math symbol', 'equivalent to')

# Translators: this is the spoken representation for the character '≎' (U+224e)
_operators['\u224e'] = C_('math symbol', 'geometrically equivalent to')

# Translators: this is the spoken representation for the character '≏' (U+224f)
_operators['\u224f'] = C_('math symbol', 'difference between')

# Translators: this is the spoken representation for the character '≐' (U+2250)
_operators['\u2250'] = C_('math symbol', 'approaches the limit')

# Translators: this is the spoken representation for the character '≑' (U+2251)
_operators['\u2251'] = C_('math symbol', 'geometrically equal to')

# Translators: this is the spoken representation for the character '≒' (U+2252)
_operators['\u2252'] = C_('math symbol', 'approximately equal to or the image of')

# Translators: this is the spoken representation for the character '≓' (U+2253)
_operators['\u2253'] = C_('math symbol', 'image of or approximately equal to')

# Translators: this is the spoken representation for the character '≔' (U+2254)
_operators['\u2254'] = C_('math symbol', 'colon equals')

# Translators: this is the spoken representation for the character '≕' (U+2255)
_operators['\u2255'] = C_('math symbol', 'equals colon')

# Translators: this is the spoken representation for the character '≖' (U+2256)
_operators['\u2256'] = C_('math symbol', 'ring in equal to')

# Translators: this is the spoken representation for the character '≗' (U+2257)
_operators['\u2257'] = C_('math symbol', 'ring equal to')

# Translators: this is the spoken representation for the character '≘' (U+2258)
_operators['\u2258'] = C_('math symbol', 'corresponds to')

# Translators: this is the spoken representation for the character '≙' (U+2259)
_operators['\u2259'] = C_('math symbol', 'estimates')

# Translators: this is the spoken representation for the character '≚' (U+225a)
_operators['\u225a'] = C_('math symbol', 'equiangular to')

# Translators: this is the spoken representation for the character '≛' (U+225b)
_operators['\u225b'] = C_('math symbol', 'star equals')

# Translators: this is the spoken representation for the character '≜' (U+225c)
_operators['\u225c'] = C_('math symbol', 'delta equal to')

# Translators: this is the spoken representation for the character '≝' (U+225d)
_operators['\u225d'] = C_('math symbol', 'equal to by definition')

# Translators: this is the spoken representation for the character '≞' (U+225e)
_operators['\u225e'] = C_('math symbol', 'measured by')

# Translators: this is the spoken representation for the character '≟' (U+225f)
_operators['\u225f'] = C_('math symbol', 'questioned equal to')

# Translators: this is the spoken representation for the character '≠' (U+2260)
_operators['\u2260'] = C_('math symbol', 'not equal to')

# Translators: this is the spoken representation for the character '≡' (U+2261)
_operators['\u2261'] = C_('math symbol', 'identical to')

# Translators: this is the spoken representation for the character '≢' (U+2262)
_operators['\u2262'] = C_('math symbol', 'not identical to')

# Translators: this is the spoken representation for the character '≣' (U+2263)
_operators['\u2263'] = C_('math symbol', 'strictly equivalent to')

# Translators: this is the spoken representation for the character '≤' (U+2264)
_operators['\u2264'] = C_('math symbol', 'less than or equal to')

# Translators: this is the spoken representation for the character '≥' (U+2265)
_operators['\u2265'] = C_('math symbol', 'greater than or equal to')

# Translators: this is the spoken representation for the character '≦' (U+2266)
_operators['\u2266'] = C_('math symbol', 'less than over equal to')

# Translators: this is the spoken representation for the character '≧' (U+2267)
_operators['\u2267'] = C_('math symbol', 'greater than over equal to')

# Translators: this is the spoken representation for the character '≨' (U+2268)
_operators['\u2268'] = C_('math symbol', 'less than but not equal to')

# Translators: this is the spoken representation for the character '≩' (U+2269)
_operators['\u2269'] = C_('math symbol', 'greater than but not equal to')

# Translators: this is the spoken representation for the character '≪' (U+226a)
_operators['\u226a'] = C_('math symbol', 'much less than')

# Translators: this is the spoken representation for the character '≫' (U+226b)
_operators['\u226b'] = C_('math symbol', 'much greater than')

# Translators: this is the spoken representation for the character '≬' (U+226c)
_operators['\u226c'] = C_('math symbol', 'between')

# Translators: this is the spoken representation for the character '≭' (U+226d)
_operators['\u226d'] = C_('math symbol', 'not equivalent to')

# Translators: this is the spoken representation for the character '≮' (U+226e)
_operators['\u226e'] = C_('math symbol', 'not less than')

# Translators: this is the spoken representation for the character '≯' (U+226f)
_operators['\u226f'] = C_('math symbol', 'not greater than')

# Translators: this is the spoken representation for the character '≰' (U+2270)
_operators['\u2270'] = C_('math symbol', 'neither less than nor equal to')

# Translators: this is the spoken representation for the character '≱' (U+2271)
_operators['\u2271'] = C_('math symbol', 'neither greater than nor equal to')

# Translators: this is the spoken representation for the character '≲' (U+2272)
_operators['\u2272'] = C_('math symbol', 'less than or equivalent to')

# Translators: this is the spoken representation for the character '≳' (U+2273)
_operators['\u2273'] = C_('math symbol', 'greater than or equivalent to')

# Translators: this is the spoken representation for the character '≴' (U+2274)
_operators['\u2274'] = C_('math symbol', 'neither less than nor equivalent to')

# Translators: this is the spoken representation for the character '≵' (U+2275)
_operators['\u2275'] = C_('math symbol', 'neither greater than nor equivalent to')

# Translators: this is the spoken representation for the character '≶' (U+2276)
_operators['\u2276'] = C_('math symbol', 'less than or greater than')

# Translators: this is the spoken representation for the character '≷' (U+2277)
_operators['\u2277'] = C_('math symbol', 'greater than or less than')

# Translators: this is the spoken representation for the character '≸' (U+2278)
_operators['\u2278'] = C_('math symbol', 'neither less than nor greater than')

# Translators: this is the spoken representation for the character '≹' (U+2279)
_operators['\u2279'] = C_('math symbol', 'neither greater than nor less than')

# Translators: this is the spoken representation for the character '≺' (U+227a)
_operators['\u227a'] = C_('math symbol', 'precedes')

# Translators: this is the spoken representation for the character '≻' (U+227b)
_operators['\u227b'] = C_('math symbol', 'succeeds')

# Translators: this is the spoken representation for the character '≼' (U+227c)
_operators['\u227c'] = C_('math symbol', 'precedes or equal to')

# Translators: this is the spoken representation for the character '≽' (U+227d)
_operators['\u227d'] = C_('math symbol', 'succeeds or equal to')

# Translators: this is the spoken representation for the character '≾' (U+227e)
_operators['\u227e'] = C_('math symbol', 'precedes or equivalent to')

# Translators: this is the spoken representation for the character '≿' (U+227f)
_operators['\u227f'] = C_('math symbol', 'succeeds or equivalent to')

# Translators: this is the spoken representation for the character '⊀' (U+2280)
_operators['\u2280'] = C_('math symbol', 'does not precede')

# Translators: this is the spoken representation for the character '⊁' (U+2281)
_operators['\u2281'] = C_('math symbol', 'does not succeed')

# Translators: this is the spoken representation for the character '⊂' (U+2282)
_operators['\u2282'] = C_('math symbol', 'subset of')

# Translators: this is the spoken representation for the character '⊃' (U+2283)
_operators['\u2283'] = C_('math symbol', 'superset of')

# Translators: this is the spoken representation for the character '⊄' (U+2284)
_operators['\u2284'] = C_('math symbol', 'not a subset of')

# Translators: this is the spoken representation for the character '⊅' (U+2285)
_operators['\u2285'] = C_('math symbol', 'not a superset of')

# Translators: this is the spoken representation for the character '⊆' (U+2286)
_operators['\u2286'] = C_('math symbol', 'subset of or equal to')

# Translators: this is the spoken representation for the character '⊇' (U+2287)
_operators['\u2287'] = C_('math symbol', 'superset of or equal to')

# Translators: this is the spoken representation for the character '⊈' (U+2288)
_operators['\u2288'] = C_('math symbol', 'neither a subset of nor equal to')

# Translators: this is the spoken representation for the character '⊉' (U+2289)
_operators['\u2289'] = C_('math symbol', 'neither a superset of nor equal to')

# Translators: this is the spoken representation for the character '⊊' (U+228a)
_operators['\u228a'] = C_('math symbol', 'subset of with not equal to')

# Translators: this is the spoken representation for the character '⊋' (U+228b)
_operators['\u228b'] = C_('math symbol', 'superset of with not equal to')

# Translators: this is the spoken representation for the character '⊌' (U+228c)
_operators['\u228c'] = C_('math symbol', 'multiset')

# Translators: this is the spoken representation for the character '⊍' (U+228d)
_operators['\u228d'] = C_('math symbol', 'multiset multiplication')

# Translators: this is the spoken representation for the character '⊎' (U+228e)
_operators['\u228e'] = C_('math symbol', 'multiset union')

# Translators: this is the spoken representation for the character '⊏' (U+228f)
_operators['\u228f'] = C_('math symbol', 'square image of')

# Translators: this is the spoken representation for the character '⊐' (U+2290)
_operators['\u2290'] = C_('math symbol', 'square original of')

# Translators: this is the spoken representation for the character '⊑' (U+2291)
_operators['\u2291'] = C_('math symbol', 'square image of or equal to')

# Translators: this is the spoken representation for the character '⊒' (U+2292)
_operators['\u2292'] = C_('math symbol', 'square original of or equal to')

# Translators: this is the spoken representation for the character '⊓' (U+2293)
_operators['\u2293'] = C_('math symbol', 'square cap')

# Translators: this is the spoken representation for the character '⊔' (U+2294)
_operators['\u2294'] = C_('math symbol', 'square cup')

# Translators: this is the spoken representation for the character '⊕' (U+2295)
_operators['\u2295'] = C_('math symbol', 'circled plus')

# Translators: this is the spoken representation for the character '⊖' (U+2296)
_operators['\u2296'] = C_('math symbol', 'circled minus')

# Translators: this is the spoken representation for the character '⊗' (U+2297)
_operators['\u2297'] = C_('math symbol', 'circled times')

# Translators: this is the spoken representation for the character '⊘' (U+2298)
_operators['\u2298'] = C_('math symbol', 'circled division slash')

# Translators: this is the spoken representation for the character '⊙' (U+2299)
_operators['\u2299'] = C_('math symbol', 'circled dot operator')

# Translators: this is the spoken representation for the character '⊚' (U+229a)
_operators['\u229a'] = C_('math symbol', 'circled ring operator')

# Translators: this is the spoken representation for the character '⊛' (U+229b)
_operators['\u229b'] = C_('math symbol', 'circled asterisk operator')

# Translators: this is the spoken representation for the character '⊜' (U+229c)
_operators['\u229c'] = C_('math symbol', 'circled equals')

# Translators: this is the spoken representation for the character '⊝' (U+229d)
_operators['\u229d'] = C_('math symbol', 'circled dash')

# Translators: this is the spoken representation for the character '⊞' (U+229e)
_operators['\u229e'] = C_('math symbol', 'squared plus')

# Translators: this is the spoken representation for the character '⊟' (U+229f)
_operators['\u229f'] = C_('math symbol', 'squared minus')

# Translators: this is the spoken representation for the character '⊠' (U+22a0)
_operators['\u22a0'] = C_('math symbol', 'squared times')

# Translators: this is the spoken representation for the character '⊡' (U+22a1)
_operators['\u22a1'] = C_('math symbol', 'squared dot operator')

# Translators: this is the spoken representation for the character '⊢' (U+22a2)
_operators['\u22a2'] = C_('math symbol', 'right tack')

# Translators: this is the spoken representation for the character '⊣' (U+22a3)
_operators['\u22a3'] = C_('math symbol', 'left tack')

# Translators: this is the spoken representation for the character '⊤' (U+22a4)
_operators['\u22a4'] = C_('math symbol', 'down tack')

# Translators: this is the spoken representation for the character '⊥' (U+22a5)
_operators['\u22a5'] = C_('math symbol', 'up tack')

# Translators: this is the spoken representation for the character '⊦' (U+22a6)
_operators['\u22a6'] = C_('math symbol', 'assertion')

# Translators: this is the spoken representation for the character '⊧' (U+22a7)
_operators['\u22a7'] = C_('math symbol', 'models')

# Translators: this is the spoken representation for the character '⊨' (U+22a8)
_operators['\u22a8'] = C_('math symbol', 'true')

# Translators: this is the spoken representation for the character '⊩' (U+22a9)
_operators['\u22a9'] = C_('math symbol', 'forces')

# Translators: this is the spoken representation for the character '⊪' (U+22aa)
_operators['\u22aa'] = C_('math symbol', 'triple vertical bar right turnstile')

# Translators: this is the spoken representation for the character '⊫' (U+22ab)
_operators['\u22ab'] = C_('math symbol', 'double vertical bar double right turnstile')

# Translators: this is the spoken representation for the character '⊬' (U+22ac)
_operators['\u22ac'] = C_('math symbol', 'does not prove')

# Translators: this is the spoken representation for the character '⊭' (U+22ad)
_operators['\u22ad'] = C_('math symbol', 'not true')

# Translators: this is the spoken representation for the character '⊮' (U+22ae)
_operators['\u22ae'] = C_('math symbol', 'does not force')

# Translators: this is the spoken representation for the character '⊯' (U+22af)
_operators['\u22af'] = C_('math symbol', 'negated double vertical bar double right turnstile')

# Translators: this is the spoken representation for the character '⊰' (U+22b0)
_operators['\u22b0'] = C_('math symbol', 'precedes under relation')

# Translators: this is the spoken representation for the character '⊱' (U+22b1)
_operators['\u22b1'] = C_('math symbol', 'succeeds under relation')

# Translators: this is the spoken representation for the character '⊲' (U+22b2)
_operators['\u22b2'] = C_('math symbol', 'normal subgroup of')

# Translators: this is the spoken representation for the character '⊳' (U+22b3)
_operators['\u22b3'] = C_('math symbol', 'contains as normal subgroup')

# Translators: this is the spoken representation for the character '⊴' (U+22b4)
_operators['\u22b4'] = C_('math symbol', 'normal subgroup of or equal to')

# Translators: this is the spoken representation for the character '⊵' (U+22b5)
_operators['\u22b5'] = C_('math symbol', 'contains as normal subgroup of or equal to')

# Translators: this is the spoken representation for the character '⊶' (U+22b6)
_operators['\u22b6'] = C_('math symbol', 'original of')

# Translators: this is the spoken representation for the character '⊷' (U+22b7)
_operators['\u22b7'] = C_('math symbol', 'image of')

# Translators: this is the spoken representation for the character '⊸' (U+22b8)
_operators['\u22b8'] = C_('math symbol', 'multimap')

# Translators: this is the spoken representation for the character '⊹' (U+22b9)
_operators['\u22b9'] = C_('math symbol', 'hermitian conjugate matrix')

# Translators: this is the spoken representation for the character '⊺' (U+22ba)
_operators['\u22ba'] = C_('math symbol', 'intercalate')

# Translators: this is the spoken representation for the character '⊻' (U+22bb)
_operators['\u22bb'] = C_('math symbol', 'xor')

# Translators: this is the spoken representation for the character '⊼' (U+22bc)
_operators['\u22bc'] = C_('math symbol', 'nand')

# Translators: this is the spoken representation for the character '⊽' (U+22bd)
_operators['\u22bd'] = C_('math symbol', 'nor')

# Translators: this is the spoken representation for the character '⊾' (U+22be)
_operators['\u22be'] = C_('math symbol', 'right angle with arc')

# Translators: this is the spoken representation for the character '⊿' (U+22bf)
_operators['\u22bf'] = C_('math symbol', 'right triangle')

# Translators: this is the spoken representation for the character '⋀' (U+22c0)
_operators['\u22c0'] = C_('math symbol', 'logical and')

# Translators: this is the spoken representation for the character '⋁' (U+22c1)
_operators['\u22c1'] = C_('math symbol', 'logical or')

# Translators: this is the spoken representation for the character '⋂' (U+22c2)
_operators['\u22c2'] = C_('math symbol', 'intersection')

# Translators: this is the spoken representation for the character '⋃' (U+22c3)
_operators['\u22c3'] = C_('math symbol', 'union')

# Translators: this is the spoken representation for the character '⋄' (U+22c4)
_operators['\u22c4'] = C_('math symbol', 'diamond operator')

# Translators: this is the spoken representation for the character '⋅' (U+22c5)
_operators['\u22c5'] = C_('math symbol', 'dot operator')

# Translators: this is the spoken representation for the character '⋆' (U+22c6)
_operators['\u22c6'] = C_('math symbol', 'star operator')

# Translators: this is the spoken representation for the character '⋇' (U+22c7)
_operators['\u22c7'] = C_('math symbol', 'division times')

# Translators: this is the spoken representation for the character '⋈' (U+22c8)
_operators['\u22c8'] = C_('math symbol', 'bowtie')

# Translators: this is the spoken representation for the character '⋉' (U+22c9)
_operators['\u22c9'] = C_('math symbol', 'left normal factor semidirect product')

# Translators: this is the spoken representation for the character '⋊' (U+22ca)
_operators['\u22ca'] = C_('math symbol', 'right normal factor semidirect product')

# Translators: this is the spoken representation for the character '⋋' (U+22cb)
_operators['\u22cb'] = C_('math symbol', 'left semidirect product')

# Translators: this is the spoken representation for the character '⋌' (U+22cc)
_operators['\u22cc'] = C_('math symbol', 'right semidirect product')

# Translators: this is the spoken representation for the character '⋍' (U+22cd)
_operators['\u22cd'] = C_('math symbol', 'reversed tilde equals')

# Translators: this is the spoken representation for the character '⋎' (U+22ce)
_operators['\u22ce'] = C_('math symbol', 'curly logical or')

# Translators: this is the spoken representation for the character '⋏' (U+22cf)
_operators['\u22cf'] = C_('math symbol', 'curly logical and')

# Translators: this is the spoken representation for the character '⋐' (U+22d0)
_operators['\u22d0'] = C_('math symbol', 'double subset')

# Translators: this is the spoken representation for the character '⋑' (U+22d1)
_operators['\u22d1'] = C_('math symbol', 'double superset')

# Translators: this is the spoken representation for the character '⋒' (U+22d2)
_operators['\u22d2'] = C_('math symbol', 'double intersection')

# Translators: this is the spoken representation for the character '⋓' (U+22d3)
_operators['\u22d3'] = C_('math symbol', 'double union')

# Translators: this is the spoken representation for the character '⋔' (U+22d4)
_operators['\u22d4'] = C_('math symbol', 'pitchfork')

# Translators: this is the spoken representation for the character '⋕' (U+22d5)
_operators['\u22d5'] = C_('math symbol', 'equal and parallel to')

# Translators: this is the spoken representation for the character '⋖' (U+22d6)
_operators['\u22d6'] = C_('math symbol', 'less than with dot')

# Translators: this is the spoken representation for the character '⋗' (U+22d7)
_operators['\u22d7'] = C_('math symbol', 'greater than with dot')

# Translators: this is the spoken representation for the character '⋘' (U+22d8)
_operators['\u22d8'] = C_('math symbol', 'very much less than')

# Translators: this is the spoken representation for the character '⋙' (U+22d9)
_operators['\u22d9'] = C_('math symbol', 'very much greater than')

# Translators: this is the spoken representation for the character '⋚' (U+22da)
_operators['\u22da'] = C_('math symbol', 'less than equal to or greater than')

# Translators: this is the spoken representation for the character '⋛' (U+22db)
_operators['\u22db'] = C_('math symbol', 'greater than equal to or less than')

# Translators: this is the spoken representation for the character '⋜' (U+22dc)
_operators['\u22dc'] = C_('math symbol', 'equal to or less than')

# Translators: this is the spoken representation for the character '⋝' (U+22dd)
_operators['\u22dd'] = C_('math symbol', 'equal to or greater than')

# Translators: this is the spoken representation for the character '⋝' (U+22de)
_operators['\u22de'] = C_('math symbol', 'equal to or precedes')

# Translators: this is the spoken representation for the character '⋝' (U+22df)
_operators['\u22df'] = C_('math symbol', 'equal to or succeeds')

# Translators: this is the spoken representation for the character '⋠' (U+22e0)
_operators['\u22e0'] = C_('math symbol', 'does not precede or equal')

# Translators: this is the spoken representation for the character '⋡' (U+22e1)
_operators['\u22e1'] = C_('math symbol', 'does not succeed or equal')

# Translators: this is the spoken representation for the character '⋢' (U+22e2)
_operators['\u22e2'] = C_('math symbol', 'not square image of or equal to')

# Translators: this is the spoken representation for the character '⋣' (U+22e3)
_operators['\u22e3'] = C_('math symbol', 'not square original of or equal to')

# Translators: this is the spoken representation for the character '⋤' (U+22e4)
_operators['\u22e4'] = C_('math symbol', 'square image of or not equal to')

# Translators: this is the spoken representation for the character '⋥' (U+22e5)
_operators['\u22e5'] = C_('math symbol', 'square original of or not equal to')

# Translators: this is the spoken representation for the character '⋦' (U+22e6)
_operators['\u22e6'] = C_('math symbol', 'less than but not equivalent to')

# Translators: this is the spoken representation for the character '⋧' (U+22e7)
_operators['\u22e7'] = C_('math symbol', 'greater than but not equivalent to')

# Translators: this is the spoken representation for the character '⋨' (U+22e8)
_operators['\u22e8'] = C_('math symbol', 'precedes but not equivalent to')

# Translators: this is the spoken representation for the character '⋩' (U+22e9)
_operators['\u22e9'] = C_('math symbol', 'succeeds but not equivalent to')

# Translators: this is the spoken representation for the character '⋪' (U+22ea)
_operators['\u22ea'] = C_('math symbol', 'not normal subgroup of')

# Translators: this is the spoken representation for the character '⋫' (U+22eb)
_operators['\u22eb'] = C_('math symbol', 'does not contain as normal subgroup')

# Translators: this is the spoken representation for the character '⋬' (U+22ec)
_operators['\u22ec'] = C_('math symbol', 'not normal subgroup of or equal to')

# Translators: this is the spoken representation for the character '⋭' (U+22ed)
_operators['\u22ed'] = C_('math symbol', 'does not contain as normal subgroup or equal')

# Translators: this is the spoken representation for the character '⋮' (U+22ee)
_operators['\u22ee'] = C_('math symbol', 'vertical ellipsis')

# Translators: this is the spoken representation for the character '⋯' (U+22ef)
_operators['\u22ef'] = C_('math symbol', 'midline horizontal ellipsis')

# Translators: this is the spoken representation for the character '⋰' (U+22f0)
_operators['\u22f0'] = C_('math symbol', 'up right diagonal ellipsis')

# Translators: this is the spoken representation for the character '⋱' (U+22f1)
_operators['\u22f1'] = C_('math symbol', 'down right diagonal ellipsis')

# Translators: this is the spoken representation for the character '⋲' (U+22f2)
_operators['\u22f2'] = C_('math symbol', 'element of with long horizontal stroke')

# Translators: this is the spoken representation for the character '⋳' (U+22f3)
_operators['\u22f3'] = C_('math symbol',
                           'element of with vertical bar at end of horizontal stroke')

# Translators: this is the spoken representation for the character '⋴' (U+22f4)
_operators['\u22f4'] = C_('math symbol',
                          'small element of with vertical bar at end of horizontal stroke')

# Translators: this is the spoken representation for the character '⋵' (U+22f5)
_operators['\u22f5'] = C_('math symbol', 'element of with dot above')

# Translators: this is the spoken representation for the character '⋶' (U+22f6)
_operators['\u22f6'] = C_('math symbol', 'element of with overbar')

# Translators: this is the spoken representation for the character '⋷' (U+22f7)
_operators['\u22f7'] = C_('math symbol', 'small element of with overbar')

# Translators: this is the spoken representation for the character '⋸' (U+22f8)
_operators['\u22f8'] = C_('math symbol', 'element of with underbar')

# Translators: this is the spoken representation for the character '⋹' (U+22f9)
_operators['\u22f9'] = C_('math symbol', 'element of with two horizontal strokes')

# Translators: this is the spoken representation for the character '⋺' (U+22fa)
_operators['\u22fa'] = C_('math symbol', 'contains with long horizontal stroke')

# Translators: this is the spoken representation for the character '⋻' (U+22fb)
_operators['\u22fb'] = C_('math symbol', 'contains with vertical bar at end of horizontal stroke')

# Translators: this is the spoken representation for the character '⋼' (U+22fc)
_operators['\u22fc'] = C_('math symbol',
                          'small contains with vertical bar at end of horizontal stroke')

# Translators: this is the spoken representation for the character '⋽' (U+22fd)
_operators['\u22fd'] = C_('math symbol', 'contains with overbar')

# Translators: this is the spoken representation for the character '⋾' (U+22fe)
_operators['\u22fe'] = C_('math symbol', 'small contains with overbar')

# Translators: this is the spoken representation for the character '⋿' (U+22ff)
_operators['\u22ff'] = C_('math symbol', 'z notation bag membership')

# Translators: this is the spoken representation for the character '⌈' (U+2308)
_operators['\u2308'] = C_('math symbol', 'left ceiling')

# Translators: this is the spoken representation for the character '⌉' (U+2309)
_operators['\u2309'] = C_('math symbol', 'right ceiling')

# Translators: this is the spoken representation for the character '⌊' (U+230a)
_operators['\u230a'] = C_('math symbol', 'left floor')

# Translators: this is the spoken representation for the character '⌋' (U+230b)
_operators['\u230b'] = C_('math symbol', 'right floor')

# Translators: this is the spoken representation for the character '⏞' (U+23de)
_operators['\u23de'] = C_('math symbol', 'top brace')

# Translators: this is the spoken representation for the character '⏟' (U+23df)
_operators['\u23df'] = C_('math symbol', 'bottom brace')

# Translators: this is the spoken representation for the character '⟨' (U+27e8)
_operators['\u27e8'] = C_('math symbol', 'left angle bracket')

# Translators: this is the spoken representation for the character '⟩' (U+27e9)
_operators['\u27e9'] = C_('math symbol', 'right angle bracket')

# Translators: this is the spoken representation for the character '⨀' (U+2a00)
_operators['\u2a00'] = C_('math symbol', 'circled dot')

# Translators: this is the spoken representation for the character '⨁' (U+2a01)
_operators['\u2a01'] = C_('math symbol', 'circled plus')

# Translators: this is the spoken representation for the character '⨂' (U+2a02)
_operators['\u2a02'] = C_('math symbol', 'circled times')
# Translators: this is the spoken representation for the character '⨃' (U+2a03)
_operators['\u2a03'] = C_('math symbol', 'union with dot')
# Translators: this is the spoken representation for the character '⨄' (U+2a04)
_operators['\u2a04'] = C_('math symbol', 'union with plus')
# Translators: this is the spoken representation for the character '⨅' (U+2a05)
_operators['\u2a05'] = C_('math symbol', 'square intersection')
# Translators: this is the spoken representation for the character '⨆' (U+2a06)
_operators['\u2a06'] = C_('math symbol', 'square union')

# Translators: this is the spoken representation for the character '■' (U+25a0)
# when used as a geometric shape (i.e. as opposed to a bullet in a list).
_shapes['\u25a0'] = C_('math symbol', 'black square')

# Translators: this is the spoken representation for the character '□' (U+25a1)
# when used as a geometric shape (i.e. as opposed to a bullet in a list).
_shapes['\u25a1'] = C_('math symbol', 'white square')

# Translators: this is the spoken representation for the character '◆' (U+25c6)
# when used as a geometric shape (i.e. as opposed to a bullet in a list).
_shapes['\u25c6'] = C_('math symbol', 'black diamond')

# Translators: this is the spoken representation for the character '○' (U+25cb)
# when used as a geometric shape (i.e. as opposed to a bullet in a list).
_shapes['\u25cb'] = C_('math symbol', 'white circle')

# Translators: this is the spoken representation for the character '●' (U+25cf)
# when used as a geometric shape (i.e. as opposed to a bullet in a list).
_shapes['\u25cf'] = C_('math symbol', 'black circle')

# Translators: this is the spoken representation for the character '◦' (U+25e6)
_shapes['\u25e6'] = C_('math symbol', 'white bullet')

# Translators: this is the spoken representation for the character '◾' (U+25fe)
# when used as a geometric shape (i.e. as opposed to a bullet in a list).
_shapes['\u25fe'] = C_('math symbol', 'black medium small square')

# Translators: this is the spoken representation for the character '̱' (U+0331)
# which combines with the preceding character. '%s' is a placeholder for the
# preceding character. Some examples of combined symbols can be seen in this
# table: http://www.w3.org/TR/MathML3/appendixc.html#oper-dict.entries-table.
_combining['\u0331'] = C_('math symbol', '%s with underline')

# Translators: this is the spoken representation for the character '̸' (U+0338)
# which combines with the preceding character. '%s' is a placeholder for the
# preceding character. Some examples of combined symbols can be seen in this
# table: http://www.w3.org/TR/MathML3/appendixc.html#oper-dict.entries-table.
_combining['\u0338'] = C_('math symbol', '%s with slash')

# Translators: this is the spoken representation for the character '⃒' (U+20D2)
# which combines with the preceding character. '%s' is a placeholder for the
# preceding character. Some examples of combined symbols can be seen in this
# table: http://www.w3.org/TR/MathML3/appendixc.html#oper-dict.entries-table.
_combining['\u20D2'] = C_('math symbol', '%s with vertical line')

_all.update(_alnum)
_all.update(_arrows)
_all.update(_operators)
_all.update(_shapes)

def _get_style_string(symbol):
    o = ord(symbol)
    if o in _bold or o in _boldGreek or o in _boldDigits:
        return BOLD
    if o in _italic or o in _italicGreek or o in _otherItalic:
        return ITALIC
    if o in _boldItalic or o in _boldItalicGreek:
        return BOLD_ITALIC
    if o in _script or o in _otherScript:
        return SCRIPT
    if o in _boldScript:
        return BOLD_SCRIPT
    if o in _fraktur or o in _otherFraktur:
        return FRAKTUR
    if o in _doubleStruck or o in _doubleStruckDigits or o in _otherDoubleStruck:
        return DOUBLE_STRUCK
    if o in _boldFraktur:
        return BOLD_FRAKTUR
    if o in _sansSerif or o in _sansSerifDigits:
        return SANS_SERIF
    if o in _sansSerifBold or o in _sansSerifBoldGreek or o in _sansSerifBoldDigits:
        return SANS_SERIF_BOLD
    if o in _sansSerifItalic:
        return SANS_SERIF_ITALIC
    if o in _sansSerifBoldItalic or o in _sansSerifBoldItalicGreek:
        return SANS_SERIF_BOLD_ITALIC
    if o in _monospace or o in _monospaceDigits:
        return MONOSPACE
    if o in _dotless:
        return DOTLESS

    return "%s"

def _update_symbols(symbol_dict):
    _all.update(symbol_dict)

def _get_spokent_name(symbol, include_style):
    if symbol not in _all:
        return ""

    name = _all.get(symbol)
    if not name and fall_back_on_unicode_data:
        name = unicodedata.name(symbol).lower()
        _update_symbols({symbol: name})
        return name

    if include_style and symbol in _alnum:
        name = _get_style_string(symbol) % name

    return name

def get_character_name(symbol):
    """Returns the character name of symbol."""

    result = _get_spokent_name(symbol, speak_style != SPEAK_NEVER)
    msg = f"MATHSYMBOLS: Name of '{symbol}' is '{result}'"
    debug.print_message(debug.LEVEL_INFO, msg, True, True)
    return result

def adjust_for_speech(string):
    """Adjusts string for speech by replacing math symbols with their spoken names."""

    # Handle combining characters first
    # Combining characters modify the preceding character
    result = string
    for combining_char, name_template in _combining.items():
        # Look for any character followed by the combining character
        i = 0
        while i < len(result) - 1:
            if result[i + 1] == combining_char:
                base_char = result[i]
                name = name_template % base_char
                # Replace the base char + combining char with the spoken name
                result = result[:i] + f" {name} " + result[i + 2:]
                i += len(f" {name} ")
            else:
                i += 1

    # Handle regular math symbols
    include_style = speak_style == SPEAK_ALWAYS
    for char in _all:
        if char in result:
            name = _get_spokent_name(char, include_style)
            if name:
                result = result.replace(char, f" {name} ")

    return result
