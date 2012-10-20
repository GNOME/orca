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

import importlib

from . import debug
from . import orca_state
from .scripts import apps, toolkits

class ScriptManager:

    def __init__(self):
        debug.println(debug.LEVEL_FINEST, 'INFO: Initializing script manager')
        self.appScripts = {}
        self.toolkitScripts = {}
        self._appModules = apps.__all__
        self._toolkitModules = toolkits.__all__
        self._defaultScript = None
        self._scriptPackages = \
            ["orca-scripts",
             "orca.scripts",
             "orca.scripts.apps",
             "orca.scripts.toolkits"]
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
             'Earlybird':        'Thunderbird',
             'bug-buddy':        'gnome_segv2',
             'gaim':             'pidgin',
             'empathy-chat':     'empathy',
             'gnome-calculator': 'gcalctool',
             'Nereid':           'Banshee',
             'vte':              'gnome-terminal'}
        self._toolkitNames = \
            {'gtk':              'GAIL',
             'clutter':          'CALLY'}

        self.setActiveScript(None, "__init__")
        debug.println(debug.LEVEL_FINEST, 'INFO: Script manager initialized')

    def activate(self):
        """Called when this script manager is activated."""

        debug.println(debug.LEVEL_FINEST, 'INFO: Activating script manager')
        self._defaultScript  = None
        self.setActiveScript(self.getScript(None), "activate")
        debug.println(debug.LEVEL_FINEST, 'INFO: Script manager activated')

    def deactivate(self):
        """Called when this script manager is deactivated."""

        debug.println(debug.LEVEL_FINEST, 'INFO: Dectivating script manager')
        self._defaultScript  = None
        self.setActiveScript(None, "deactivate")
        self.appScripts = {}
        self.toolkitScripts = {}
        debug.println(debug.LEVEL_FINEST, 'INFO: Script manager deactivated')

    def getModuleName(self, app):
        """Returns the module name of the script to use for application app."""

        try:
            appAndNameExist = app != None and app.name != ''
        except (LookupError, RuntimeError):
            appAndNameExist = False
            debug.println(debug.LEVEL_SEVERE,
                          "getModuleName: %s no longer exists" % app)

        if not appAndNameExist:
            return None

        # Many python apps have an accessible name which ends in '.py'.
        # Sometimes OOo has 'soffice.bin' as its name.
        name = app.name.split('.')[0]
        altNames = list(self._appNames.keys())

        names = [n for n in altNames if n.lower() == name.lower()]
        if names:
            name = self._appNames.get(names[0])
        else:
            for nameList in (self._appModules, self._toolkitModules):
                names = [n for n in nameList if n.lower() == name.lower()]
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

        altNames = list(self._toolkitNames.keys())
        names = [n for n in altNames if n.lower() == name.lower()]
        if names:
            newName = self._toolkitNames.get(names[0])
            debug.println(debug.LEVEL_FINEST,
                          "mapped %s to %s" % (name, newName))
            name = newName

        script = None
        for package in self._scriptPackages:
            moduleName = '.'.join((package, name))
            debug.println(debug.LEVEL_FINE, "Looking for %s.py" % moduleName)
            try:
                module = importlib.import_module(moduleName)
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

        try:
            toolkitName = getattr(app, "toolkitName", None)
        except (LookupError, RuntimeError):
            msg = "Error getting toolkitName for: %s" % app
            debug.println(debug.LEVEL_FINE, msg)
        else:
            if app and toolkitName:
                script = self._newNamedScript(app, toolkitName)

        if not script:
            script = self.getDefaultScript(app)
            debug.println(debug.LEVEL_FINE, "Default script created")

        return script

    def getDefaultScript(self, app=None):
        if not app and self._defaultScript:
            return self._defaultScript

        from .scripts import default
        script = default.Script(app)
        script.registerEventListeners()

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

        appScript = None
        toolkitScript = None

        objToolkit = self._toolkitForObject(obj)
        if objToolkit:
            toolkitScripts = self.toolkitScripts.get(app, {})
            toolkitScript = toolkitScripts.get(objToolkit)
            if not toolkitScript:
                toolkitScript = self._createScript(app, obj)
                toolkitScripts[objToolkit] = toolkitScript
                toolkitScript.registerEventListeners()
            self.toolkitScripts[app] = toolkitScripts

        if not app:
            appScript = self.getDefaultScript()
        elif app in self.appScripts:
            appScript = self.appScripts[app]
        else:
            appScript = self._createScript(app, None)
            self.appScripts[app] = appScript
            appScript.registerEventListeners()

        # Only defer to the toolkit script for this object if the app script
        # is based on a different toolkit.
        if toolkitScript \
           and not issubclass(appScript.__class__, toolkitScript.__class__):
            return toolkitScript

        return appScript

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

        appList = list(self.appScripts.keys())
        appList = [a for a in appList if a != None and a not in desktop]
        for app in appList:
            appScript = self.appScripts.pop(app)
            appScript.deregisterEventListeners()
            del appScript

            try:
                toolkitScripts = self.toolkitScripts.pop(app)
            except KeyError:
                pass
            else:
                for toolkitScript in list(toolkitScripts.values()):
                    toolkitScript.deregisterEventListeners()
                    del toolkitScript

            del app

_manager = ScriptManager()

def getManager():
    return _manager
