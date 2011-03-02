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

from pluglib.interfaces import *

class testPlugin(IPlugin):
    name = 'Test Plugin'
    description = 'A testing plugin for code tests' 
    version = '0.1pre'
    authors = ['J. Félix Ontañón <felixonta@gmail.com>', 'J. Ignacio Álvarez <neonigma@gmail.com>']
    website = 'http://fontanon.org'
    icon = 'gtk-missing-image'

    def __init__(self):
        print 'Hello World (plugin started)!'

IPlugin.register(testPlugin)
