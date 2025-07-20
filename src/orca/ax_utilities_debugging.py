# Orca
#
# Copyright 2024 Igalia, S.L.
# Copyright 2024 GNOME Foundation Inc.
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
# pylint: disable=too-many-branches
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-return-statements

"""Utilities for obtaining accessibility information for debugging."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2024 Igalia, S.L." \
                "Copyright (c) 2024 GNOME Foundation Inc."
__license__   = "LGPL"

import inspect
import pprint
import types
from typing import Any

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi
from gi.repository import GLib

from .ax_object import AXObject
from .ax_utilities_application import AXUtilitiesApplication
from .ax_utilities_relation import AXUtilitiesRelation


class AXUtilitiesDebugging:
    """Utilities for obtaining accessibility information for debugging."""

    @staticmethod
    def _format_string(string: str = "") -> str:
        if not string:
            return ""

        string = string.replace("\n", "\\n").replace("\ufffc", "[OBJ]")
        if len(string) < 100:
            return string

        words = string.split()
        string = f"{' '.join(words[:5])} ... {' '.join(words[-5:])} ({len(string)} chars.)"
        return string

    @staticmethod
    def as_string(obj: Any) -> str:
        """Turns obj into a human-consumable string."""

        if isinstance(obj, Atspi.Accessible):
            result = AXObject.get_role_name(obj)
            name = AXObject.get_name(obj)
            if name:
                result += f": '{AXUtilitiesDebugging._format_string(name)}'"
            if not result:
                result = "DEAD"

            return f"[{result} ({hex(id(obj))})] "

        if isinstance(obj, Atspi.Event):
            any_data = AXUtilitiesDebugging._format_string(
                AXUtilitiesDebugging.as_string(obj.any_data))
            return (
                f"{obj.type} for {AXUtilitiesDebugging.as_string(obj.source)} in "
                f"{AXUtilitiesApplication.application_as_string(obj.source)} "
                f"({obj.detail1}, {obj.detail2}, {any_data})"
            )

        if isinstance(obj, (Atspi.Role, Atspi.StateType, Atspi.CollectionMatchType,
                            Atspi.TextGranularity, Atspi.ScrollType)):
            return obj.value_nick

        if isinstance(obj, Atspi.Rect):
            return f"(x:{obj.x}, y:{obj.y}, width:{obj.width}, height:{obj.height})"

        if isinstance(obj, (list, set)):
            return f"[{', '.join(map(AXUtilitiesDebugging.as_string, obj))}]"

        if isinstance(obj, dict):
            stringified = {key: AXUtilitiesDebugging.as_string(value) for key, value in obj.items()}
            formatter = pprint.PrettyPrinter(width=150)
            return f"{formatter.pformat(stringified)}"

        if isinstance(obj, types.FunctionType):
            if hasattr(obj, "__self__"):
                return f"{obj.__module__}.{obj.__self__.__class__.__name__}.{obj.__name__}"
            return f"{obj.__module__}.{obj.__name__}"

        if isinstance(obj, types.MethodType):
            if hasattr(obj, "__self__"):
                return f"{obj.__self__.__class__.__name__}.{obj.__name__}"
            return f"{obj.__name__}"

        if isinstance(obj, types.FrameType):
            module_name = inspect.getmodulename(obj.f_code.co_filename)
            return f"{module_name}.{obj.f_code.co_name}"

        if isinstance(obj, inspect.FrameInfo):
            module_name = inspect.getmodulename(obj.filename) or "<unknown>"
            return f"{module_name}.{obj.function}:{obj.lineno}"

        return str(obj)

    @staticmethod
    def actions_as_string(obj: Atspi.Accessible) -> str:
        """Returns information about the actions as a string."""

        results = []
        for i in range(AXObject.get_n_actions(obj)):
            result = AXObject.get_action_name(obj, i)
            keybinding = AXObject.get_action_key_binding(obj, i)
            if keybinding:
                result += f" ({keybinding})"
            results.append(result)

        return "; ".join(results)

    @staticmethod
    def attributes_as_string(obj: Atspi.Accessible) -> str:
        """Returns the object attributes of obj as a string."""

        def as_string(attribute):
            return f"{attribute[0]}:{attribute[1]}"

        return ", ".join(map(as_string, AXObject.get_attributes_dict(obj).items()))

    @staticmethod
    def interfaces_as_string(obj: Atspi.Accessible) -> str:
        """Returns the supported interfaces of obj as a string."""

        if not AXObject.is_valid(obj):
            return ""

        iface_checks = [
            (AXObject.supports_action, "Action"),
            (AXObject.supports_collection, "Collection"),
            (AXObject.supports_component, "Component"),
            (AXObject.supports_document, "Document"),
            (AXObject.supports_editable_text, "EditableText"),
            (AXObject.supports_hyperlink, "Hyperlink"),
            (AXObject.supports_hypertext, "Hypertext"),
            (AXObject.supports_image, "Image"),
            (AXObject.supports_selection, "Selection"),
            (AXObject.supports_table, "Table"),
            (AXObject.supports_table_cell, "TableCell"),
            (AXObject.supports_text, "Text"),
            (AXObject.supports_value, "Value"),
        ]

        ifaces = [iface for check, iface in iface_checks if check(obj)]
        return ", ".join(ifaces)

    @staticmethod
    def relations_as_string(obj: Atspi.Accessible) -> str:
        """Returns the relations associated with obj as a string."""

        if not AXObject.is_valid(obj):
            return ""

        def as_string(relations):
            return relations.value_name[15:].replace("_", "-").lower()

        def obj_as_string(acc):
            result = AXObject.get_role_name(acc)
            name = AXObject.get_name(acc)
            if name:
                result += f": '{name}'"
            if not result:
                result = "DEAD"
            return f"[{result}]"

        results = []
        for rel in AXUtilitiesRelation.get_relations(obj):
            type_string = as_string(rel.get_relation_type())
            targets = AXUtilitiesRelation.get_relation_targets_for_debugging(
                obj, rel.get_relation_type())
            target_string = ",".join(map(obj_as_string, targets))
            results.append(f"{type_string}: {target_string}")

        return "; ".join(results)

    @staticmethod
    def state_set_as_string(obj: Atspi.Accessible) -> str:
        """Returns the state set associated with obj as a string."""

        if not AXObject.is_valid(obj):
            return ""

        def as_string(state):
            return state.value_name[12:].replace("_", "-").lower()

        return ", ".join(map(as_string, AXObject.get_state_set(obj).get_states()))

    @staticmethod
    def text_for_debugging(obj: Atspi.Accessible) -> str:
        """Returns the text content of obj for debugging."""

        if not AXObject.supports_text(obj):
            return ""

        try:
            result = Atspi.Text.get_text(obj, 0, Atspi.Text.get_character_count(obj))
        except GLib.GError:
            return ""

        return AXUtilitiesDebugging._format_string(result)

    @staticmethod
    def object_details_as_string(
        obj: Atspi.Accessible,
        indent: str = "",
        include_app: bool = True
    ) -> str:
        """Returns a string, suitable for printing, that describes details about obj."""

        if not isinstance(obj, Atspi.Accessible):
            return ""

        if AXObject.is_dead(obj):
            return "(exception fetching data)"

        if include_app:
            string = f"{indent}app='{AXUtilitiesApplication.application_as_string(obj)}' "
        else:
            string = indent

        name = AXUtilitiesDebugging._format_string(AXObject.get_name(obj))
        desc = AXUtilitiesDebugging._format_string(AXObject.get_description(obj))
        help_text = AXUtilitiesDebugging._format_string(AXObject.get_help_text(obj))
        ax_id = AXObject.get_accessible_id(obj)
        string += (
            f"name='{name}' role='{AXObject.get_role_name(obj)}'"
            f" axid='{ax_id}' id={hex(id(obj))}\n"
            f"{indent}description='{desc}'\n"
            f"{indent}help='{help_text}'\n"
            f"{indent}states='{AXUtilitiesDebugging.state_set_as_string(obj)}'\n"
            f"{indent}relations='{AXUtilitiesDebugging.relations_as_string(obj)}'\n"
            f"{indent}actions='{AXUtilitiesDebugging.actions_as_string(obj)}'\n"
            f"{indent}interfaces='{AXUtilitiesDebugging.interfaces_as_string(obj)}'\n"
            f"{indent}attributes='{AXUtilitiesDebugging.attributes_as_string(obj)}'\n"
            f"{indent}text='{AXUtilitiesDebugging.text_for_debugging(obj)}'\n"
            f"{indent}path={AXObject.get_path(obj)}"
        )
        return string

    @staticmethod
    def object_event_details_as_string(event: Atspi.Event, indent: str = "") -> str:
        """Returns a string, suitable for printing, with details about event."""

        if event.type.startswith("mouse:"):
            return ""

        source = AXUtilitiesDebugging.object_details_as_string(event.source, indent, True)
        any_data = AXUtilitiesDebugging.object_details_as_string(event.any_data, indent, False)
        string = f"EVENT SOURCE:\n{source}\n"
        if any_data:
            string += f"\nEVENT ANY DATA:\n{any_data}\n"
        return string
