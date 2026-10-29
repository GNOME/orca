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

# pylint: disable=too-many-instance-attributes

"""Settings contexts and content positions given to the generators."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import gi

    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from .acss import ACSS
    from .enums import ActivePresentationMode, PresentationReason
    from .speechserver import SpeechServer


@dataclass(frozen=True)
class ContentItem:
    """The slice of an object's content being presented (one entry in a contents batch)."""

    start_offset: int
    end_offset: int
    string: str
    caret_offset: int | None = None


@dataclass(frozen=True)
class ContentPosition:
    """An item's position within a batch of contents presented together."""

    index: int = 0
    total: int = 1
    last_for_object: bool = True


@dataclass(frozen=True)
class GeneratorContext:
    """Base settings context shared by all generators."""

    enabled: bool
    verbose: bool
    focus: Atspi.Accessible | None
    in_focus_mode: bool
    active_mode: ActivePresentationMode | None
    reason: PresentationReason
    prior_obj: Atspi.Accessible | None
    offset: int | None
    leaving: bool
    ancestor_of: Atspi.Accessible | None
    content_item: ContentItem | None
    content_position: ContentPosition | None
    content_subject: Atspi.Accessible | None
    resolved_role: Atspi.Role | str | None
    role_subject: Atspi.Accessible | None
    include_context: bool
    presented_names: set[Atspi.Accessible] | None = field(default=None, kw_only=True)


@dataclass(frozen=True)
class SpeechGeneratorContext(GeneratorContext):
    """Settings context for speech generators."""

    next_content_subject: Atspi.Accessible | None
    in_preferences_window: bool
    auto_language_switching_content: bool
    auto_language_switching_ui: bool
    only_switch_configured_languages: bool
    voice_set_languages: tuple[str, ...]
    insert_pauses_between_utterances: bool
    punctuation_level: str
    voices: dict[str, ACSS]
    speech_server: SpeechServer | None
    only_displayed_text: bool
    speak_description: bool
    speak_tutorial_messages: bool
    speak_position_in_set: bool
    speak_widget_mnemonic: bool
    speak_blank_lines: bool
    speak_indentation: bool
    announce_cell_headers: bool
    announce_cell_coordinates: bool
    announce_spreadsheet_cell_coordinates: bool
    announce_article: bool
    announce_blockquote: bool
    announce_code_block: bool
    announce_document: bool
    announce_form: bool
    announce_grouping: bool
    announce_inline_code: bool
    announce_header_and_footer: bool
    announce_landmark: bool
    announce_list: bool
    announce_table: bool
    announce_tracked_changes: bool
    text_attribute_change_mode: int
    speak_misspelled_indicator: bool
    use_color_names: bool
    language: str
    dialect: str
    eliminate_pauses: bool


@dataclass(frozen=True)
class BrailleGeneratorContext(GeneratorContext):
    """Settings context for braille generators."""

    full_rolenames: bool
    display_ancestors: bool
    end_of_line_indicator: bool
    present_mnemonics: bool
    indicate_links: bool
