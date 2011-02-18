# - coding: utf-8 -

from pluglib.confstore import GConfStore
from pluglib.interfaces import *

class gConfPlugin(GConfStore):
    defaults = {
            'enable':   True,
    }

    def __init__(self):
        super(gConfPlugin, self).__init__('/apps/orca/plugins/test')
        self.save()
        print 'Hello World (plugin started)!'

class testPlugin(IPlugin):
    name = 'Test Plugin'
    description = 'A testing plugin for code tests' 
    version = '0.1pre'
    authors = ['J. Félix Ontañón <felixonta@gmail.com>', 'J. Ignacio Álvarez <neonigma@gmail.com>']
    website = 'http://fontanon.org'
    icon = 'gtk-missing-image'

    def __init__(self):
        self.gc_plug = gConfPlugin()

    def disable(self):
        self.gc_plug.disable('enable')

IPlugin.register(testPlugin)
