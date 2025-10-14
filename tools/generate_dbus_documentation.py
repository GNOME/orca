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
            "setters": sorted(setters, key=lambda x: x[0])
        }
    except DBusError as e:
        print(f"Error getting info for module {module_name}: {e}", file=sys.stderr)
        return {
            "commands": [],
            "parameterized_commands": [],
            "getters": [],
            "setters": []
        }


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


def _group_structural_navigator_commands(commands):
    """Group structural navigator commands by object type."""
    groups = {}
    other = []

    def normalize_obj_type(obj_type):  # pylint: disable=too-many-return-statements
        """Convert to a canonical form for grouping."""

        # Group all heading commands together. Ditto for link commands.
        if obj_type.startswith("Heading"):
            return "Heading"
        if "Link" in obj_type:
            return "Link"

        # Common plural patterns
        if obj_type.endswith("ies"):  # Entries -> Entry
            return obj_type[:-3] + "y"
        if obj_type.endswith("xes"):  # Checkboxes -> Checkbox
            return obj_type[:-2]
        if obj_type.endswith("shes") or obj_type.endswith("ches"):  # Matches -> Match
            return obj_type[:-2]
        if obj_type.endswith("s") and not obj_type.endswith("ss"):
            return obj_type[:-1]
        return obj_type

    for name, description in commands:
        # Extract the object type from command names like NextHeading, ListButtons, etc.
        if name.startswith("Next") or name.startswith("Previous"):
            prefix = "Next" if name.startswith("Next") else "Previous"
            obj_type = name[len(prefix):]
            normalized = normalize_obj_type(obj_type)
            if normalized not in groups:
                if normalized == "Heading":
                    display = "Headings"
                elif not obj_type.endswith("s"):
                    display = obj_type + "s"
                else:
                    display = obj_type
                groups[normalized] = {"commands": [], "display_name": display}
            groups[normalized]["commands"].append((name, description))
        elif name.startswith("List"):
            obj_type = name[4:]
            normalized = normalize_obj_type(obj_type)
            if normalized not in groups:
                display = "Headings" if normalized == "Heading" else obj_type
                groups[normalized] = {"commands": [], "display_name": display}
            else:
                current_display = groups[normalized]["display_name"]
                if not current_display.endswith("s") or normalized == "Heading":
                    new_display = "Headings" if normalized == "Heading" else obj_type
                    groups[normalized]["display_name"] = new_display
            groups[normalized]["commands"].append((name, description))
        else:
            # Other commands like ContainerStart, CycleMode
            other.append((name, description))

    return groups, other

# pylint: disable-next=too-many-branches,too-many-statements,too-many-locals
def format_module_commands(module_name, info):
    """Format module-level commands as markdown."""

    lines = []
    lines.append(f"### {module_name}")
    lines.append("")
    lines.append(f"**Object Path:** `/org/gnome/Orca/Service/{module_name}`")
    lines.append("")

    # Commands - special handling for certain modules
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

        if module_name == "SpeechAndVerbosityManager":
            # Group related increase/decrease commands
            def sort_speech_commands(cmd_tuple):
                name, _ = cmd_tuple
                # Define groups and their order
                groups = {
                    "Rate": 0, "Pitch": 1, "Volume": 2,
                }
                # Check if it's an Increase/Decrease command
                for group_name, group_order in groups.items():
                    if group_name in name:
                        if name.startswith("Increase"):
                            return (group_order, 0, name)
                        if name.startswith("Decrease"):
                            return (group_order, 1, name)
                # Other commands go at the end, sorted alphabetically
                return (100, 0, name)

            sorted_commands = sorted(info["commands"], key=sort_speech_commands)
            for name, description in sorted_commands:
                lines.append(f"- **`{name}`:** {description}")
            lines.append("")

        elif module_name == "FlatReviewPresenter":
            # Group Go commands at the top
            def sort_flat_review_commands(cmd_tuple):
                name, _ = cmd_tuple
                if name.startswith("Go"):
                    return (0, name)
                return (1, name)

            sorted_commands = sorted(info["commands"], key=sort_flat_review_commands)
            for name, description in sorted_commands:
                lines.append(f"- **`{name}`:** {description}")
            lines.append("")

        elif module_name == "CaretNavigator":
            # Group related navigation commands
            def sort_caret_commands(cmd_tuple):
                name, _ = cmd_tuple
                # Define groups for Character, Word, Line, File
                if "Character" in name:
                    group = 0
                elif "Word" in name:
                    group = 1
                elif "Line" in name:
                    group = 2
                elif "File" in name:
                    group = 3
                else:
                    group = 100

                # Within each group: Next, Previous, Start, End, Toggle
                if name.startswith("Next"):
                    order = 0
                elif name.startswith("Previous"):
                    order = 1
                elif name.startswith("Start"):
                    order = 0
                elif name.startswith("End"):
                    order = 1
                elif name.startswith("Toggle"):
                    order = 2
                else:
                    order = 99

                return (group, order, name)

            sorted_commands = sorted(info["commands"], key=sort_caret_commands)
            for name, description in sorted_commands:
                lines.append(f"- **`{name}`:** {description}")
            lines.append("")

        elif module_name == "StructuralNavigator":
            groups, other = _group_structural_navigator_commands(info["commands"])

            # Show grouped commands by object type first
            for obj_type in sorted(groups.keys()):
                cmds = groups[obj_type]
                display_name = cmds["display_name"]
                lines.append(f"##### {display_name}")
                lines.append("")

                # Sort commands in a specific order: Next, Previous, List, grouped by variant
                def sort_key(cmd_tuple):
                    name, _ = cmd_tuple
                    # Extract base command and any suffix (like Level1, UnvisitedLink, etc.)
                    if name.startswith("Next"):
                        prefix_order = 0
                        suffix = name[4:]  # Remove "Next"
                    elif name.startswith("Previous"):
                        prefix_order = 1
                        suffix = name[8:]  # Remove "Previous"
                    elif name.startswith("List"):
                        prefix_order = 2
                        suffix = name[4:]  # Remove "List"
                    else:
                        prefix_order = 3
                        suffix = name

                    # Extract level number or variant for proper ordering
                    level_or_variant = 0

                    if "Level" in suffix:
                        # For headings: extract level number
                        try:
                            level_or_variant = int(suffix.split("Level")[1])
                        except (IndexError, ValueError):
                            pass
                    elif "Unvisited" in suffix:
                        # For links: Unvisited comes after base
                        level_or_variant = 1
                    elif "Visited" in suffix:
                        # For links: Visited comes after Unvisited
                        level_or_variant = 2

                    return (level_or_variant, prefix_order, name)

                sorted_commands = sorted(cmds["commands"], key=sort_key)
                for name, desc in sorted_commands:
                    lines.append(f"- **`{name}`:** {desc}")
                lines.append("")

            # Show uncategorized commands at the end
            if other:
                lines.append("##### Other")
                lines.append("")
                for name, description in other:
                    lines.append(f"- **`{name}`:** {description}")
                lines.append("")
        else:
            for name, description in info["commands"]:
                lines.append(f"- **`{name}`:** {description}")
            lines.append("")

    # Parameterized Commands
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

    # Runtime Settings (combine getters and setters)
    if info["getters"] or info["setters"]:
        lines.append("#### Settings")
        lines.append("")
        lines.append("**Methods:** `org.gnome.Orca.Module.ExecuteRuntimeGetter` / `org.gnome.Orca.Module.ExecuteRuntimeSetter`")
        lines.append("")
        lines.append(
            "**Parameters:** `PropertyName` (string), "
            "`Value` (variant, setter only)"
        )
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
            else:
                # Both getter and setter - change "Returns" or "Sets" to "Gets/Sets"
                if description.startswith("Returns "):
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
    module_infos = {}
    for module_name in modules:
        module_infos[module_name] = get_module_info(bus, module_name)

    total_commands = len(system_commands)
    total_commands += sum(len(info["commands"]) for info in module_infos.values())
    total_commands += sum(len(info["parameterized_commands"]) for info in module_infos.values())
    total_getters = sum(len(info["getters"]) for info in module_infos.values())
    total_setters = sum(len(info["setters"]) for info in module_infos.values())

    lines = []
    lines.append("# Orca D-Bus Service Commands Reference")
    lines.append("")
    lines.append(
        f"This document lists all commands ({total_commands}), "
        f"runtime getters ({total_getters}), and runtime setters ({total_setters}) available"
    )
    lines.append("via Orca's D-Bus Remote Controller interface.")
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

    # System commands
    lines.append(format_system_commands(system_commands))
    lines.append("---")
    lines.append("")

    # Module commands
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
    except IOError as e:
        print(f"Error writing to {output_file}: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
