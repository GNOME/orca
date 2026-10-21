# Orca
#
# Copyright 2026 Igalia, S.L.
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

"""Metadata classes for generated help."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

PreferenceKind = Literal[
    "switch", "integer", "number", "choice", "color", "list", "table", "group", "page", "button"
]


@dataclass(frozen=True)
class CommandDoc:
    """Metadata for one command in generated help."""

    name: str
    summary: str = ""
    details: str = ""
    since: str = ""


@dataclass(frozen=True)
class CommandSectionDoc:
    """Metadata for one command section in generated help."""

    title: str
    target: str = ""
    link_title: str = ""
    summary: str = ""
    link_summary: str = ""
    command_types: tuple[str, ...] = field(default_factory=tuple)
    command_names: tuple[str, ...] = field(default_factory=tuple)
    command_prefixes: tuple[str, ...] = field(default_factory=tuple)
    since: str = ""
    instructions: str = ""


@dataclass(frozen=True)
class CommandGroupDoc:
    """Metadata for one command group in generated help."""

    title: str = ""
    target: str = ""
    link_title: str = ""
    summary: str = ""
    see_also: tuple[str, ...] = field(default_factory=tuple)
    sections: tuple[CommandSectionDoc, ...] = field(default_factory=tuple)
    commands: tuple[CommandDoc, ...] = field(default_factory=tuple)
    since: str = ""


@dataclass(frozen=True)
class FeatureLinkDoc:
    """Documentation link for a feature topic."""

    target: str
    label: str = ""
    summary: str = ""


@dataclass(frozen=True)
class CommandShortcutDoc:
    """Associates a shortcut mentioned in prose with its command definition."""

    text: str
    command_name: str


@dataclass(frozen=True)
class FeatureSectionDoc:
    """Feature prose, links, and command placements for one topic section."""

    title: str
    target: str = ""
    intro: str = ""
    settings_and_commands: tuple[FeatureLinkDoc, ...] = field(default_factory=tuple)
    details: str = ""
    links: tuple[FeatureLinkDoc, ...] = field(default_factory=tuple)
    include_target: str = ""
    command_names: tuple[str, ...] = field(default_factory=tuple)
    command_groups: tuple[str, ...] = field(default_factory=tuple)
    preference_categories: tuple[str, ...] = field(default_factory=tuple)
    preference_panels: tuple[str, ...] = field(default_factory=tuple)
    preference_controls: tuple[str, ...] = field(default_factory=tuple)
    after_commands: str = ""
    shortcuts: tuple[CommandShortcutDoc, ...] = field(default_factory=tuple)
    topic_id: str = ""
    since: str = ""


@dataclass(frozen=True)
class FeatureDocumentationDoc:
    """Reusable feature documentation metadata."""

    pages: tuple[FeaturePageDoc, ...] = field(default_factory=tuple)
    sections: tuple[FeatureSectionDoc, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class FeaturePageDoc:
    """Generated Mallard page for a user-facing task or feature."""

    page_id: str
    title: str
    link_title: str
    description: str
    guide_xref: str
    target: str = ""
    intro: str = ""
    details: str = ""
    sections: tuple[FeatureSectionDoc, ...] = field(default_factory=tuple)
    sections_as_pages: bool = False
    topics_guide_xref: str = ""
    topics_title: str = ""
    generate_guide: bool = True
    preference_category: str = ""
    preference_panels: tuple[str, ...] = field(default_factory=tuple)
    topics: tuple[str, ...] = field(default_factory=tuple)
    since: str = ""


@dataclass(frozen=True)
class PreferenceValueDoc:
    """Metadata for one preference value in generated help."""

    label: str
    value: str = ""
    summary: str = ""
    since: str = ""


@dataclass(frozen=True)
class PreferenceActionDoc:
    """Metadata for an action associated with a preference control."""

    label: str
    summary: str = ""
    placement: Literal["", "header"] = ""


@dataclass(frozen=True)
class PreferenceControlDoc:
    """Metadata for one preference control in generated help."""

    label: str
    kind: PreferenceKind
    target: str = ""
    summary: str = ""
    schema: str = ""
    key: str = ""
    values: tuple[str, ...] = ()
    value_docs: tuple[PreferenceValueDoc, ...] = ()
    actions: tuple[PreferenceActionDoc, ...] = ()
    item_actions: tuple[PreferenceActionDoc, ...] = ()
    controls: tuple[PreferenceControlDoc, ...] = ()
    dynamic_values: bool = False
    minimum: str = ""
    maximum: str = ""
    default_labels: tuple[PreferenceValueDoc, ...] = ()
    since: str = ""


@dataclass(frozen=True)
class PreferenceCategoryDoc:
    """Directory description and contents for one preferences category."""

    category_id: str
    title: str
    description: str
    panels: tuple[str, ...]
    application_preferences: bool = True
    application_details: str = ""
    target: str = ""
    since: str = ""


@dataclass(frozen=True)
class PreferencePanelDoc:
    """Settings instructions and link text for one preferences panel."""

    title: str
    target: str = ""
    panel_id: str = ""
    instructions: str = ""
    link_summary: str = ""
    schema: str = ""
    controls: tuple[PreferenceControlDoc, ...] = ()
    show_available_settings: bool = True
    category: PreferenceCategoryDoc | None = None
    command_groups: tuple[str, ...] = ()
    command_names: tuple[str, ...] = ()
    since: str = ""
