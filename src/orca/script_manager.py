# Orca
#
# Copyright 2011-2024 Igalia, S.L.
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

# pylint: disable=wrong-import-position

"""Manages Orca's scripts."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2011-2024 Igalia, S.L."
__license__   = "LGPL"

import importlib

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

# TODO - JD: The script manager should not be interacting with speech or braille directly.
# When the presentation manager is created, it should handle speech and braille.

from . import braille
from . import debug
from . import settings_manager
from . import speech_and_verbosity_manager
from .ax_object import AXObject
from .ax_utilities import AXUtilities
from .scripts import apps, default, sleepmode, toolkits


class ScriptManager:
    """Manages Orca's scripts."""

    def __init__(self) -> None:
        debug.print_message(debug.LEVEL_INFO, "SCRIPT MANAGER: Initializing", True)
        self.app_scripts: dict = {}
        self.toolkit_scripts: dict = {}
        self.custom_scripts: dict = {}
        self._sleep_mode_scripts: dict = {}
        self._default_script: default.Script | None = None
        self._active_script: default.Script | None = None
        self._active: bool = False
        debug.print_message(debug.LEVEL_INFO, "SCRIPT MANAGER: Initialized", True)

    def activate(self) -> None:
        """Called when this script manager is activated."""

        debug.print_message(debug.LEVEL_INFO, "SCRIPT MANAGER: Activating", True, True)
        if self._active:
            debug.print_message(debug.LEVEL_INFO, "SCRIPT MANAGER: Already activated", True)
            return

        self._default_script = self.get_default_script(None)
        self._default_script.register_event_listeners()
        self.set_active_script(self._default_script, "activate")
        self._active = True
        debug.print_message(debug.LEVEL_INFO, "SCRIPT MANAGER: Activated", True)

    def deactivate(self) -> None:
        """Called when this script manager is deactivated."""

        debug.print_message(debug.LEVEL_INFO, "SCRIPT MANAGER: Deactivating", True, True)
        if not self._active:
            debug.print_message(debug.LEVEL_INFO, "SCRIPT MANAGER: Already deactivated", True)
            return

        if self._default_script is not None:
            self._default_script.deregister_event_listeners()
        self._default_script = None
        self.set_active_script(None, "deactivate")
        self.app_scripts = {}
        self.toolkit_scripts = {}
        self.custom_scripts = {}
        self._active = False
        debug.print_message(debug.LEVEL_INFO, "SCRIPT MANAGER: Deactivated", True)

    def get_module_name(self, app: Atspi.Accessible | None) -> str | None:
        """Returns the module name of the script to use for application app."""

        if app is None:
            msg = "SCRIPT MANAGER: Cannot get module name for null app"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return None

        name = AXObject.get_name(app)
        if not name:
            msg = "SCRIPT MANAGER: Cannot get module name for nameless app"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return None

        app_names = {"gtk-window-decorator": "switcher",
                     "marco": "switcher",
                     "mate-notification-daemon": "notification-daemon",
                     "metacity": "switcher",
                     "budgie-daemon": "switcher",
                     "pluma": "gedit",
                     "xfce4-notifyd": "notification-daemon"}
        alt_names = list(app_names.keys())
        if name.endswith((".py", ".bin")):
            name = name.split(".")[0]
        elif name.startswith(("org.", "com.")):
            name = name.split(".")[-1]

        names = [n for n in alt_names if n.lower() == name.lower()]
        if names:
            name = app_names.get(names[0], "")
        else:
            for name_list in (apps.__all__, toolkits.__all__):
                names = [n for n in name_list if n.lower() == name.lower()]
                if names:
                    name = names[0]
                    break

        tokens = ["SCRIPT MANAGER: Mapped", app, "to", name]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return name

    def _toolkit_for_object(self, obj: Atspi.Accessible) -> str | None:
        """Returns the name of the toolkit associated with obj."""

        names = {"GTK": "gtk", "GAIL": "gtk"}
        name = AXObject.get_attribute(obj, "toolkit")
        return names.get(name, name)

    def _script_for_role(self, obj: Atspi.Accessible) -> str:
        """Returns the role-based script for obj."""

        if AXUtilities.is_terminal(obj):
            return "terminal"

        return ""

    def _new_named_script(self, app: Atspi.Accessible, name: str) -> default.Script | None:
        """Returns a script based on this module if it was located and loadable."""

        if not (app and name):
            return None

        packages = ["orca-scripts", "orca.scripts", "orca.scripts.apps", "orca.scripts.toolkits"]
        script = None
        for package in packages:
            module_name = ".".join((package, name))
            try:
                module = importlib.import_module(module_name)
            except ImportError:
                continue
            except OSError as error:
                tokens = ["EXCEPTION: Could not import", module_name, ":", error]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True, True)

            tokens = ["SCRIPT MANAGER: Found", module_name]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            try:
                if hasattr(module, "get_script"):
                    script = module.get_script(app)
                else:
                    script = module.Script(app)
                break
            except (AttributeError, TypeError, ImportError) as error:
                tokens = ["EXCEPTION: Could not load", module_name, ":", error]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True, True)

        return script

    def _create_script(
        self, app: Atspi.Accessible, obj: Atspi.Accessible | None = None
    ) -> default.Script:
        """For the given application, create a new script instance."""

        module_name = self.get_module_name(app) or ""
        script = self._new_named_script(app, module_name)
        if script:
            return script

        obj_toolkit = self._toolkit_for_object(obj) or ""
        script = self._new_named_script(app, obj_toolkit)
        if script:
            return script

        toolkit_name = AXUtilities.get_application_toolkit_name(app)
        if app and toolkit_name:
            script = self._new_named_script(app, toolkit_name)

        if not script:
            script = self.get_default_script(app)
            tokens = ["SCRIPT MANAGER: Default script created for", app, "(obj: ", obj, ")"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return script

    def get_default_script(self, app: Atspi.Accessible | None = None) -> default.Script:
        """Returns the default script."""

        if not app and self._default_script:
            return self._default_script

        script = default.Script(app)
        if not app:
            self._default_script = script

        return script

    def get_or_create_sleep_mode_script(self, app: Atspi.Accessible) -> sleepmode.Script:
        """Gets or crates the sleep mode script."""

        script = self._sleep_mode_scripts.get(app)
        if script is not None:
            return script

        script = sleepmode.Script(app)
        self._sleep_mode_scripts[app] = script
        return script

    def get_script(
        self, app: Atspi.Accessible | None, obj: Atspi.Accessible | None = None
    ) -> default.Script:
        """Get a script for an app (and make it if necessary)."""

        tokens = ["SCRIPT MANAGER: Getting script for", app, obj]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        custom_script: default.Script | None = None
        app_script: default.Script | None = None
        toolkit_script: default.Script | None = None

        role_name = self._script_for_role(obj)
        if role_name:
            custom_scripts = self.custom_scripts.get(app, {})
            custom_script = custom_scripts.get(role_name)
            if not custom_script:
                custom_script = self._new_named_script(app, role_name)
                custom_scripts[role_name] = custom_script
            self.custom_scripts[app] = custom_scripts

        obj_toolkit = self._toolkit_for_object(obj)
        if obj_toolkit:
            toolkit_scripts = self.toolkit_scripts.get(app, {})
            toolkit_script = toolkit_scripts.get(obj_toolkit)
            if not toolkit_script:
                toolkit_script = self._create_script(app, obj)
                toolkit_scripts[obj_toolkit] = toolkit_script
            self.toolkit_scripts[app] = toolkit_scripts

        try:
            if not app:
                app_script = self.get_default_script()
            elif app in self.app_scripts:
                app_script = self.app_scripts[app]
            else:
                app_script = self._create_script(app, None)
                self.app_scripts[app] = app_script
        except (KeyError, AttributeError, ImportError) as error:
            tokens = ["EXCEPTION: Exception getting app script for", app, ":", error]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            app_script = self.get_default_script()

        assert app_script is not None
        if app_script.get_sleep_mode_manager().is_active_for_app(app):
            tokens = ["SCRIPT MANAGER: Sleep-mode toggled on for", app_script, app]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return self.get_or_create_sleep_mode_script(app)

        if custom_script:
            tokens = ["SCRIPT MANAGER: Script is custom script", custom_script]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return custom_script

        # Only defer to the toolkit script for this object if the app script
        # is based on a different toolkit.
        if toolkit_script and not (AXUtilities.is_frame(obj) or AXUtilities.is_status_bar(obj)) \
           and not issubclass(app_script.__class__, toolkit_script.__class__):
            tokens = ["SCRIPT MANAGER: Script is toolkit script", toolkit_script]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return toolkit_script

        tokens = ["SCRIPT MANAGER: Script is app script", app_script]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return app_script

    def get_active_script(self) -> default.Script | None:
        """Returns the active script."""

        tokens = ["SCRIPT MANAGER: Active script is:", self._active_script]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return self._active_script

    def get_active_script_app(self) -> Atspi.Accessible | None:
        """Returns the app associated with the active script."""

        if self._active_script is None:
            return None

        tokens = ["SCRIPT MANAGER: Active script app is:", self._active_script.app]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return self._active_script.app

    def set_active_script(self, new_script: default.Script | None, reason: str = "") -> None:
        """Set the active script to new_script."""

        if self._active_script == new_script:
            return

        if self._active_script is not None:
            tokens = ["SCRIPT MANAGER: Deactivating", self._active_script, "reason:", reason]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            self._active_script.deactivate()

        old_script = self._active_script
        self._active_script = new_script
        if new_script is None:
            return

        manager = settings_manager.get_manager()
        runtime_settings = {}
        if old_script and old_script.app == new_script.app:
            # Example: old_script is terminal, new_script is mate-terminal (e.g. for UI)
            runtime_settings = manager.get_runtime_settings()

        tokens = ["SCRIPT MANAGER: Setting active script to", new_script, "reason:", reason]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        new_script.activate()

        for key, value in runtime_settings.items():
            manager.set_setting(key, value)

        braille.checkBrailleSetting()
        braille.setupKeyRanges(new_script.braille_bindings.keys())
        speech_and_verbosity_manager.get_manager().check_speech_setting()

    def reclaim_scripts(self) -> None:
        """Compares the list of known scripts to the list of known apps,
        deleting any scripts as necessary.
        """

        msg = "SCRIPT MANAGER: Checking and cleaning up scripts."
        debug.print_message(debug.LEVEL_INFO, msg, True)

        app_list = list(self.app_scripts.keys())
        for app in app_list:
            if AXUtilities.is_application_in_desktop(app):
                continue

            try:
                app_script = self.app_scripts.pop(app)
            except KeyError:
                tokens = ["SCRIPT MANAGER:", app, "not found in app_scripts"]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                continue

            tokens = ["SCRIPT MANAGER: Old script for app found:", app_script, app_script.app]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

            try:
                self._sleep_mode_scripts.pop(app)
            except KeyError:
                pass

            try:
                self.toolkit_scripts.pop(app)
            except KeyError:
                pass

            try:
                self.custom_scripts.pop(app)
            except KeyError:
                pass

_manager: ScriptManager = ScriptManager()

def get_manager() -> ScriptManager:
    """Returns the Script Manager singleton."""
    return _manager
