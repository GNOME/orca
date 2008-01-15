# Liblouis Python bindings
#
# Copyright 2007-2008 Eitan Isaacson
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


from orca.orca_i18n import _           # for gettext support
from orca.orca_i18n import Q_          # to provide qualified translatable strings

# Translators: These are the braille translation table names for different
# languages. You could read about braille tables at:
# http://en.wikipedia.org/wiki/Braille
#
TABLE_NAMES = {'Cz-Cz-g1': _('Czech Grade 1'),
               'Es-Es-g1': _('Spanish Grade 1'),
               'Fr-Ca-g2': _('Canada French Grade 2'),
               'Fr-Fr-g2': _('France French Grade 2'),
               'Lv-Lv-g1': _('Latvian Grade 1'),
               'Nl-Nl-g1': _('Netherlands Dutch Grade 1'),
               'No-No-g0': _('Norwegian Grade 0'),
               'No-No-g1': _('Norwegian Grade 1'),
               'No-No-g2': _('Norwegian Grade 2'),
               'No-No-g3': _('Norwegian Grade 3'),
               'Pl-Pl-g1': _('Polish Grade 1'),
               'Pt-Pt-g1': _('Portuguese Grade 1'),
               'Se-Se-g1': _('Swedish Grade 1'),
               'ar-ar-g1': _('Arabic Grade 1'),
               'cy-cy-g1': _('Welsh Grade 1'),
               'cy-cy-g2': _('Welsh Grade 2'),
               'de-de-g0': _('German Grade 0'),
               'de-de-g1': _('German Grade 1'),
               'de-de-g2': _('German Grade 2'),
               'en-GB-g2': _('U.K. English Grade 2'),
               'en-gb-g1': _('U.K. English Grade 1'),
               'en-us-g1': _('U.S. English Grade 1'),
               'en-us-g2': _('U.S. English Grade 2'),
               'fr-ca-g1': _('Canada French Grade 1'),
               'fr-fr-g1': _('France French 1'),
               'gr-gr-g1': _('Greek Grade 1'),
               'hi-in-g1': _('Hindi Grade 1'),
               'it-it-g1': _('Italian Grade 1'),
               'nl-be-g1': _('Belgium Dutch Grade 1')}


class TYPEFORM:
   plain_text = 0
   italic = 1
   underline = 2
   bold = 4
   computer_braille = 8

class MODE:
   noContractions = 1
   compbrlAtCursor = 2
   dotsIO = 4
   comp8Dots = 8
   
