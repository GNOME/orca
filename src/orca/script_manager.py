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

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

import importlib
import pyatspi

from . import debug
from . import orca_state
from .ax_object import AXObject
from .scripts import apps, toolkits

class ScriptManager:

    def __init__(self):
        debug.println(debug.LEVEL_INFO, 'SCRIPT MANAGER: Initializing', True)
        self.appScripts = {}
        self.toolkitScripts = {}
        self.customScripts = {}
        self._appModules = apps.__all__
        self._toolkitModules = toolkits.__all__
        self._defaultScript = None
        self._scriptPackages = \
            ["orca-scripts",
             "orca.scripts",
             "orca.scripts.apps",
             "orca.scripts.toolkits"]
        self._appNames = \
            {'Icedove': 'Thunderbird',
             'Nereid': 'Banshee',
             'empathy-chat': 'empathy',
             'gnome-calculator': 'gcalctool',
             'gtk-window-decorator': 'switcher',
             'marco': 'switcher',
             'mate-notification-daemon': 'notification-daemon',
             'metacity': 'switcher',
             'pluma': 'gedit',
            }
        self._toolkitNames = \
            {'WebKitGTK': 'WebKitGtk', 'GTK': 'gtk'}

        self.setActiveScript(None, "__init__")
        self._desktop = pyatspi.Registry.getDesktop(0)
        self._active = False
        debug.println(debug.LEVEL_INFO, 'SCRIPT MANAGER: Initialized', True)

    def activate(self):
        """Called when this script manager is activated."""

        debug.println(debug.LEVEL_INFO, 'SCRIPT MANAGER: Activating', True)
        self._defaultScript = self.getScript(None)
        self._defaultScript.registerEventListeners()
        self.setActiveScript(self._defaultScript, "activate")
        self._active = True
        debug.println(debug.LEVEL_INFO, 'SCRIPT MANAGER: Activated', True)

    def deactivate(self):
        """Called when this script manager is deactivated."""

        debug.println(debug.LEVEL_INFO, 'SCRIPT MANAGER: Dectivating', True)
        if self._defaultScript:
            self._defaultScript.deregisterEventListeners()
        self._defaultScript = None
        self.setActiveScript(None, "deactivate")
        self.appScripts = {}
        self.toolkitScripts = {}
        self.customScripts = {}
        self._active = False
        debug.println(debug.LEVEL_INFO, 'SCRIPT MANAGER: Deactivated', True)

    def getModuleName(self, app):
        """Returns the module name of the script to use for application app."""

        if app is None:
            msg = 'ERROR: Cannot get module name for null app'
            debug.println(debug.LEVEL_INFO, msg, True)
            return None

        name = AXObject.get_name(app)
        if not name:
            msg = 'ERROR: Cannot get module name for nameless app'
            debug.println(debug.LEVEL_INFO, msg, True)
            return None

        altNames = list(self._appNames.keys())
        if name.endswith(".py") or name.endswith(".bin"):
            name = name.split('.')[0]
        elif name.startswith("org.") or name.startswith("com."):
            name = name.split('.')[-1]

        names = [n for n in altNames if n.lower() == name.lower()]
        if names:
            name = self._appNames.get(names[0])
        else:
            for nameList in (self._appModules, self._toolkitModules):
                names = [n for n in nameList if n.lower() == name.lower()]
                if names:
                    name = names[0]
                    break

        msg = 'SCRIPT MANAGER: mapped %s to %s' % (AXObject.get_name(app), name)
        debug.println(debug.LEVEL_INFO, msg, True)
        return name

    def _toolkitForObject(self, obj):
        """Returns the name of the toolkit associated with obj."""

        name = ''
        if obj:
            try:
                attributes = obj.getAttributes()
            except (LookupError, RuntimeError):
                pass
            else:
                attrs = dict([attr.split(':', 1) for attr in attributes])
                name = attrs.get('toolkit', '')
                name = self._toolkitNames.get(name, name)

        return name

    def _scriptForRole(self, obj):
        role = AXObject.get_role(obj)
        if role == Atspi.Role.TERMINAL:
            return 'terminal'

        return ''

    def _newNamedScript(self, app, name):
        """Attempts to locate and load the named module. If successful, returns
        a script based on this module."""

        if not (app and name):
            return None

        script = None
        for package in self._scriptPackages:
            moduleName = '.'.join((package, name))
            try:
                module = importlib.import_module(moduleName)
            except ImportError:
                continue
            except OSError:
                debug.examineProcesses()

            debug.println(debug.LEVEL_INFO, 'SCRIPT MANAGER: Found %s' % moduleName, True)
            try:
                if hasattr(module, 'getScript'):
                    script = module.getScript(app)
                else:
                    script = module.Script(app)
                break
            except:
                debug.printException(debug.LEVEL_INFO)
                msg = 'ERROR: Could not load %s' % moduleName
                debug.println(debug.LEVEL_INFO, msg, True)

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
            msg = 'ERROR: Exception getting toolkitName for: %s' % app
            debug.println(debug.LEVEL_INFO, msg, True)
        else:
            if app and toolkitName:
                script = self._newNamedScript(app, toolkitName)

        if not script:
            script = self.getDefaultScript(app)
            msg = 'SCRIPT MANAGER: Default script created'
            debug.println(debug.LEVEL_INFO, msg, True)

        return script

    def getDefaultScript(self, app=None):
        if not app and self._defaultScript:
            return self._defaultScript

        from .scripts import default
        script = default.Script(app)

        if not app:
            self._defaultScript = script

        return script

    def sanityCheckScript(self, script):
        if not self._active:
            return script

        try:
            appInDesktop = script.app in self._desktop
        except:
            appInDesktop = False

        if appInDesktop:
            return script

        msg = "WARNING: %s is not in the registry's desktop" % script.app
        debug.println(debug.LEVEL_INFO, msg, True)

        newScript = self._getScriptForAppReplicant(script.app)
        if newScript:
            msg = "SCRIPT MANAGER: Script for app replicant found: %s" % newScript
            debug.println(debug.LEVEL_INFO, msg, True)
            return newScript

        msg = "WARNING: Failed to get a replacement script for %s" % script.app
        debug.println(debug.LEVEL_INFO, msg, True)
        return script

    def getScriptForMouseButtonEvent(self, event):
        state = AXObject.get_state_set(orca_state.activeWindow)
        isActive = state.contains(Atspi.StateType.ACTIVE)
        msg = "SCRIPT MANAGER: %s is active: %s" % (orca_state.activeWindow, isActive)
        debug.println(debug.LEVEL_INFO, msg, True)

        if isActive and orca_state.activeScript:
            return orca_state.activeScript

        script = self.getDefaultScript()
        activeWindow = script.utilities.activeWindow()
        if not activeWindow:
            return script

        focusedObject = script.utilities.focusedObject(activeWindow)
        if focusedObject:
            return self.getScript(AXObject.get_application(focusedObject), focusedObject)

        return self.getScript(AXObject.get_application(activeWindow), activeWindow)

    def getScript(self, app, obj=None, sanityCheck=False):
        """Get a script for an app (and make it if necessary).  This is used
        instead of a simple calls to Script's constructor.

        Arguments:
        - app: the Python app

        Returns an instance of a Script.
        """

        customScript = None
        appScript = None
        toolkitScript = None

        roleName = self._scriptForRole(obj)
        if roleName:
            customScripts = self.customScripts.get(app, {})
            customScript = customScripts.get(roleName)
            if not customScript:
                customScript = self._newNamedScript(app, roleName)
                customScripts[roleName] = customScript
            self.customScripts[app] = customScripts

        objToolkit = self._toolkitForObject(obj)
        if objToolkit:
            toolkitScripts = self.toolkitScripts.get(app, {})
            toolkitScript = toolkitScripts.get(objToolkit)
            if not toolkitScript:
                toolkitScript = self._createScript(app, obj)
                toolkitScripts[objToolkit] = toolkitScript
            self.toolkitScripts[app] = toolkitScripts

        try:
            if not app:
                appScript = self.getDefaultScript()
            elif app in self.appScripts:
                appScript = self.appScripts[app]
            else:
                appScript = self._createScript(app, None)
                self.appScripts[app] = appScript
        except:
            msg = 'WARNING: Exception getting app script.'
            debug.printException(debug.LEVEL_ALL)
            debug.println(debug.LEVEL_WARNING, msg, True)
            appScript = self.getDefaultScript()

        if customScript:
            return customScript

        role = AXObject.get_role(obj)
        forceAppScript = role in [Atspi.Role.FRAME, Atspi.Role.STATUS_BAR]

        # Only defer to the toolkit script for this object if the app script
        # is based on a different toolkit.
        if toolkitScript and not forceAppScript \
           and not issubclass(appScript.__class__, toolkitScript.__class__):
            return toolkitScript

        if app and sanityCheck:
            appScript = self.sanityCheckScript(appScript)

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
        msg = 'SCRIPT MANAGER: Setting active script: %s (reason=%s)' % \
              (newScript.name, reason)
        debug.println(debug.LEVEL_INFO, msg, True)

    def _getScriptForAppReplicant(self, app):
        if not self._active:
            return None

        def _pid(app):
            try:
                result = app.get_process_id()
                msg = "SCRIPT MANAGER: %s is has pid: %s" % (app, result)
                debug.println(debug.LEVEL_INFO, msg, True)
                return result
            except:
                msg = "SCRIPT MANAGER: Exception getting pid for %s" % app
                debug.println(debug.LEVEL_INFO, msg, True)
                return -1

        def _isValidApp(app):
            try:
                result = app in self._desktop
                msg = "SCRIPT MANAGER: %s is in desktop: %s" % (app, result)
                debug.println(debug.LEVEL_INFO, msg, True)
                return result
            except:
                msg = "SCRIPT MANAGER: Exception seeing if %s is in desktop" % app
                debug.println(debug.LEVEL_INFO, msg, True)
                return False

        pid = _pid(app)
        if pid == -1:
            return None

        items = self.appScripts.items()
        for a, script in items:
            if a != app and _pid(a) == pid and _isValidApp(a):
                return script

        return None

    def reclaimScripts(self):
        """Compares the list of known scripts to the list of known apps,
        deleting any scripts as necessary.
        """

        appList = list(self.appScripts.keys())
        try:
            appList = [a for a in appList if a is not None and a not in self._desktop]
        except:
            debug.printException(debug.LEVEL_FINEST)
            return

        for app in appList:
            msg = "SCRIPT MANAGER: %s is no longer in registry's desktop" % app
            debug.println(debug.LEVEL_INFO, msg, True)

            try:
                appScript = self.appScripts.pop(app)
            except KeyError:
                msg = "SCRIPT MANAGER: %s not found in appScripts" % app
                debug.println(debug.LEVEL_INFO, msg, True)
                continue

            msg = "SCRIPT MANAGER: Old script for app found: %s" % appScript
            debug.println(debug.LEVEL_INFO, msg, True)

            newScript = self._getScriptForAppReplicant(app)
            if newScript:
                msg = "SCRIPT MANAGER: Script for app replicant found: %s" % newScript
                debug.println(debug.LEVEL_INFO, msg, True)

                attrs = appScript.getTransferableAttributes()
                for attr, value in attrs.items():
                    msg = "SCRIPT MANAGER: Setting %s to %s" % (attr, value)
                    debug.println(debug.LEVEL_INFO, msg, True)
                    setattr(newScript, attr, value)

            del appScript

            try:
                toolkitScripts = self.toolkitScripts.pop(app)
            except KeyError:
                pass
            else:
                for toolkitScript in toolkitScripts.values():
                    del toolkitScript

            try:
                customScripts = self.customScripts.pop(app)
            except KeyError:
                pass
            else:
                for customScript in customScripts.values():
                    del customScript

            del app

_manager = ScriptManager()

def getManager():
    return _manager
