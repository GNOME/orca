#!/usr/bin/python
# generate_dbus_documentation.py
#
# Generate markdown documentation for Orca's D-Bus remote controller.
# Must be run while Orca is active with the D-Bus service enabled.
#
# Copyright 2025 Igalia, S.L.
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

"""Generate markdown documentation for Orca's D-Bus remote controller."""

import os
import sys

from dasbus.connection import SessionMessageBus
from dasbus.error import DBusError

SERVICE_NAME = "org.gnome.Orca.Service"
SERVICE_PATH = "/org/gnome/Orca/Service"


def get_system_commands(proxy):
    """Get system-level commands from the main service interface."""
    try:
        commands = proxy.ListCommands()
        return sorted(commands, key=lambda x: x[0])
    except DBusError as e:
        print(f"Error getting system commands: {e}", file=sys.stderr)
        return []


def get_modules(proxy):
    """Get list of registered modules."""
    try:
        modules = proxy.ListModules()
        return sorted(modules)
    except DBusError as e:
        print(f"Error getting modules: {e}", file=sys.stderr)
        return []


def get_module_info(bus, module_name):
    """Get all commands, parameterized commands, getters, and setters for a module."""
    object_path = f"{SERVICE_PATH}/{module_name}"

    try:
        module_proxy = bus.get_proxy(SERVICE_NAME, object_path)

        commands = module_proxy.ListCommands()
        parameterized_commands = module_proxy.ListParameterizedCommands()
        getters = module_proxy.ListRuntimeGetters()
        setters = module_proxy.ListRuntimeSetters()

        return {
            "commands": sorted(commands, key=lambda x: x[0]),
            "parameterized_commands": sorted(parameterized_commands, key=lambda x: x[0]),
            "getters": sorted(getters, key=lambda x: x[0]),
            "setters": sorted(setters, key=lambda x: x[0]),
        }
    except DBusError as e:
        print(f"Error getting info for module {module_name}: {e}", file=sys.stderr)
        return {"commands": [], "parameterized_commands": [], "getters": [], "setters": []}


def format_system_commands(commands):
    """Format system-level commands as markdown."""
    lines = []
    lines.append("## Service-Level Commands")
    lines.append("")
    lines.append(
        "These commands are available directly on the main service object "
        "at `/org/gnome/Orca/Service`."
    )
    lines.append("")

    for name, description in commands:
        lines.append(f"- **`{name}`:** {description}")

    lines.append("")
    return "\n".join(lines)


def format_module_commands(module_name, info):
    """Format module-level commands as markdown."""

    lines = []
    lines.append(f"### {module_name}")
    lines.append("")
    lines.append(f"**Object Path:** `/org/gnome/Orca/Service/{module_name}`")
    lines.append("")

    if info["commands"]:
        lines.append("#### Commands")
        lines.append("")
        lines.append("**Method:** `org.gnome.Orca.Module.ExecuteCommand`")
        lines.append("")
        lines.append(
            "**Parameters:** `CommandName` (string), "
            "[`NotifyUser`](README-REMOTE-CONTROLLER.md#user-notification-applicability) (boolean)"
        )
        lines.append("")
        for name, description in info["commands"]:
            lines.append(f"- **`{name}`:** {description}")
        lines.append("")

    if info["parameterized_commands"]:
        lines.append("#### Parameterized Commands")
        lines.append("")
        lines.append("**Method:** `org.gnome.Orca.Module.ExecuteParameterizedCommand`")
        lines.append("")
        for name, description, parameters in info["parameterized_commands"]:
            param_list = ", ".join([f"`{pname}` ({ptype})" for pname, ptype in parameters])
            if param_list:
                lines.append(f"- **`{name}`:** {description} Parameters: {param_list}")
            else:
                lines.append(f"- **`{name}`:** {description}")
        lines.append("")

    if info["getters"] or info["setters"]:
        lines.append("#### Settings")
        lines.append("")
        lines.append(
            "**Methods:** `org.gnome.Orca.Module.ExecuteRuntimeGetter` / "
            "`org.gnome.Orca.Module.ExecuteRuntimeSetter`"
        )
        lines.append("")
        lines.append("**Parameters:** `PropertyName` (string), `Value` (variant, setter only)")
        lines.append("")

        # Build a merged dictionary of properties
        # Prefer setter descriptions as they may contain range/default info
        properties = {}
        for name, description in info["getters"]:
            properties[name] = {"description": description, "getter": True, "setter": False}
        for name, description in info["setters"]:
            if name in properties:
                properties[name]["setter"] = True
                properties[name]["description"] = description
            else:
                properties[name] = {"description": description, "getter": False, "setter": True}

        # Output sorted properties with annotations
        for name in sorted(properties.keys()):
            prop = properties[name]
            description = prop["description"]
            annotation = ""

            if prop["getter"] and not prop["setter"]:
                annotation = " (getter only)"
            elif prop["setter"] and not prop["getter"]:
                annotation = " (setter only)"
            # Both getter and setter - change "Returns" or "Sets" to "Gets/Sets"
            elif description.startswith("Returns "):
                description = description.replace("Returns ", "Gets/Sets ", 1)
            elif description.startswith("Sets "):
                description = description.replace("Sets ", "Gets/Sets ", 1)

            lines.append(f"- **`{name}`:** {description}{annotation}")
        lines.append("")

    return "\n".join(lines)


def generate_documentation():
    """Generate the complete documentation."""
    try:
        bus = SessionMessageBus()
    except DBusError as e:
        print(f"Error connecting to D-Bus: {e}", file=sys.stderr)
        return None

    try:
        proxy = bus.get_proxy(SERVICE_NAME, SERVICE_PATH)
    except DBusError as e:
        print(f"Error connecting to Orca service: {e}", file=sys.stderr)
        print("Make sure Orca is running with the D-Bus service enabled.", file=sys.stderr)
        return None

    system_commands = get_system_commands(proxy)
    modules = get_modules(proxy)
    if not system_commands and not modules:
        print(
            "No commands or modules found. Is Orca running with the D-Bus service enabled?",
            file=sys.stderr,
        )
        return None

    module_infos = {}
    for module_name in modules:
        module_infos[module_name] = get_module_info(bus, module_name)

    lines = []
    lines.append("# Orca D-Bus Service Commands Reference")
    lines.append("")
    lines.append("The service can be accessed at:")
    lines.append("")
    lines.append("- **Service Name:** `org.gnome.Orca.Service`")
    lines.append("- **Main Object Path:** `/org/gnome/Orca/Service`")
    lines.append("- **Module Object Paths:** `/org/gnome/Orca/Service/ModuleName`")
    lines.append("")
    lines.append(
        "Additional information about using the remote controller can be found in "
        "[README-REMOTE-CONTROLLER.md](README-REMOTE-CONTROLLER.md)."
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append(format_system_commands(system_commands))
    lines.append("---")
    lines.append("")

    lines.append("## Modules")
    lines.append("")
    lines.append(
        "Each module exposes commands, getters, and setters on its object "
        "at `/org/gnome/Orca/Service/ModuleName`."
    )
    lines.append("")

    for module_name in modules:
        lines.append(format_module_commands(module_name, module_infos[module_name]))
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def main():
    """Main entry point."""

    # Write to parent directory since script is in tools/
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    output_file = os.path.join(parent_dir, "REMOTE-CONTROLLER-COMMANDS.md")

    print("Generating D-Bus documentation...", file=sys.stderr)
    documentation = generate_documentation()

    if documentation is None:
        print("Failed to generate documentation.", file=sys.stderr)
        return 1

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(documentation)
        print(f"Documentation written to {output_file}", file=sys.stderr)
        return 0
    except OSError as e:
        print(f"Error writing to {output_file}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
