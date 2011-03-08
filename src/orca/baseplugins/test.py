# - coding: utf-8 -

# Copyright (C) 2010, J. Félix Ontañón <felixonta@gmail.com>
# Copyright (C) 2011, J. Ignacio Álvarez <neonigma@gmail.com>

# This file is part of Pluglib.

# Pluglib is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Pluglib is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Pluglib.  If not, see <http://www.gnu.org/licenses/>.

from orca.pluglib.interfaces import *
import orca.input_event as input_event
import orca.scripts.default as default

from orca.orca_i18n import _         # for gettext support
from orca.orca_i18n import ngettext  # for ngettext support
from orca.orca_i18n import C_        # to provide qualified translatable strings

class testPlugin(IPlugin):
    name = 'Test Plugin'
    description = 'A testing plugin for code tests' 
    version = '0.1pre'
    authors = ['J. Félix Ontañón <felixonta@gmail.com>', 'J. Ignacio Álvarez <neonigma@gmail.com>']
    website = 'http://www.emergya.es'
    icon = 'gtk-missing-image'

    def __init__(self):
        print 'Hello World (plugin started)!'

IPlugin.register(testPlugin)
