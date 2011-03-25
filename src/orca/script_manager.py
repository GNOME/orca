# Orca
#
# Copyright 2011. Orca Team.
# Author: Joanmarie Diggs <joanmarie.diggs@gmail.com>
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

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2011. Orca Team."
__license__   = "LGPL"

import debug
import orca
import orca_state

from scripts import apps, toolkits

_settingsManager = getattr(orca, '_settingsManager')
_eventManager = getattr(orca, '_eventManager')

class ScriptManager:

    def __init__(self):
        self.scripts = {}
        self._appModules = apps.__all__
        self._toolkitModules = toolkits.__all__
        self._defaultScript = None
        self._scriptPackages = \
            ["orca-scripts",
             "scripts",
             "scripts.apps",
             "scripts.toolkits"]
        self._appNames = \
            {'Bon Echo':         'Mozilla',
             'Deer Park':        'Mozilla',
             'Firefox':          'Mozilla',
             'Minefield':        'Mozilla',
             'Namoroka':         'Mozilla',
             'Shiretoko':        'Mozilla',
             'Lanikai':          'Thunderbird',
             'Mail/News':        'Thunderbird',
             'Miramar':          'Thunderbird',
             'Shredder':         'Thunderbird',
             'bug-buddy':        'gnome_segv2',
             'epiphany-browser': 'epiphany',
             'gaim':             'pidgin',
             'gnome-calculator': 'gcalctool',
             'gnome-help':       'yelp',
             'Nereid':           'Banshee',
             'vte':              'gnome-terminal'}

        self.setActiveScript(None, "__init__")

    def activate(self):
        """Called when this script manager is activated."""

        self._defaultScript  = None
        self.setActiveScript(self.getScript(None), "activate")

    def deactivate(self):
        """Called when this script manager is deactivated."""

        self._defaultScript  = None
        self.setActiveScript(None, "deactivate")
        self.scripts = {}

    def getModuleName(self, app):
        """Returns the module name of the script to use for application app."""

        if not (app and app.name):
            return None

        # Many python apps have an accessible name which ends in '.py'.
        # Sometimes OOo has 'soffice.bin' as its name.
        name = app.name.split('.')[0]
        altNames = self._appNames.keys()

        names = filter(lambda n: n.lower() == name.lower(), altNames)
        if names:
            name = self._appNames.get(names[0])
        else:
            for nameList in (self._appModules, self._toolkitModules):
                names = filter(lambda n: n.lower() == name.lower(), nameList)
                if names:
                    name = names[0]
                    break

        debug.println(debug.LEVEL_FINEST, "mapped %s to %s" % (app.name, name))

        return name

    def _toolkitForObject(self, obj):
        """Returns the name of the toolkit associated with obj."""

        name = ''
        if obj:
            try:
                attributes = obj.getAttributes()
            except (LookupError, RuntimeError):
                debug.println(debug.LEVEL_SEVERE,
                              "_toolkitForObject: %s no longer exists" % obj)
            else:
                attrs = dict([attr.split(':', 1) for attr in attributes])
                name = attrs.get('toolkit', '')

        return name

    def _newNamedScript(self, app, name):
        """Attempts to locate and load the named module. If successful, returns
        a script based on this module."""

        if not (app and name):
            return None

        script = None
        for package in self._scriptPackages:
            moduleName = '.'.join((package, name))
            debug.println(debug.LEVEL_FINE, "Looking for %s.py" % moduleName)
            try:
                module = __import__(moduleName, globals(), locals(), [''])
            except ImportError:
                debug.println(
                    debug.LEVEL_FINE, "Could not import %s.py" % moduleName)
                continue

            debug.println(debug.LEVEL_FINE, "Found %s.py" % moduleName)
            try:
                if hasattr(module, 'getScript'):
                    script = module.getScript(app)
                else:
                    script = module.Script(app)
                debug.println(debug.LEVEL_FINE, "Loaded %s.py" % moduleName)
                break
            except:
                debug.printException(debug.LEVEL_SEVERE)
                debug.println(
                    debug.LEVEL_SEVERE, "Could not load %s.py" % moduleName)

        return script

    def _createScript(self, app, obj=None):
        """For the given application, create a new script instance."""

        moduleName = self.getModuleName(app)
        script = self._newNamedScript(app, moduleName)
        if script:
            return script

        objToolkit = self._toolkitForObject(obj)
        script = self._newNamedScript(app, objToolkit)
        if script:
            return script

        if app and getattr(app, "toolkitName", None):
            script = self._newNamedScript(app, app.toolkitName)

        if not script:
            script = self.getDefaultScript(app)
            debug.println(debug.LEVEL_FINE, "Default script created")

        return script

    def getDefaultScript(self, app=None):
        if not app and self._defaultScript:
            return self._defaultScript
        import scripts.default as default
        script = default.Script(app)
        _eventManager.registerListeners(script)

        import scripts.default as default
        script = default.Script(app)
        _eventManager.registerListeners(script)

        if not app:
            self._defaultScript = script

        return script

    def getScript(self, app, obj=None):
        """Get a script for an app (and make it if necessary).  This is used
        instead of a simple calls to Script's constructor.

        Arguments:
        - app: the Python app

        Returns an instance of a Script.
        """

        script = None

        objToolkit = self._toolkitForObject(obj)
        if objToolkit:
            script = self.scripts.get(objToolkit)
            if not script:
                script = self._createScript(app, obj)
                if script:
                    self.scripts[objToolkit] = script
                    _eventManager.registerListeners(script)
            if script:
                # Only defer to the toolkit script for this object if the
                # app script is based on a different toolkit.
                appScript = self.scripts.get(app, self.getDefaultScript())
                if issubclass(appScript.__class__, script.__class__):
                    script = appScript
                return script

        if not app:
            script = self.getDefaultScript()
        elif app in self.scripts:
            script = self.scripts[app]
        else:
            script = self._createScript(app, obj)
            self.scripts[app] = script
            _eventManager.registerListeners(script)

        return script

    def setActiveScript(self, newScript, reason=None):
        """Set the new active script.

        Arguments:
        - newScript: the new script to be made active.
        """

        if orca_state.activeScript == newScript:
            return

        if orca_state.activeScript:
            orca_state.activeScript.deactivate()

        orca_state.activeScript = newScript
        if not newScript:
            return

        _settingsManager.loadAppSettings(newScript)
        newScript.activate()
        debug.println(debug.LEVEL_FINE, "ACTIVE SCRIPT: %s (reason=%s)" \
                          % (newScript.name, reason))

    def reclaimScripts(self):
        """Compares the list of known scripts to the list of known apps,
        deleting any scripts as necessary.
        """

        from pyatspi import Registry

        try:
            desktop = Registry.getDesktop(0)
        except:
            debug.printException(debug.LEVEL_FINEST)
            return

        appList = self.scripts.keys()
        appList = filter(lambda a: a!= None and a not in desktop, appList)
        for app in appList:
            script = self.scripts.pop(app)
            _eventManager.deregisterListeners(script)
            del app
            del script
