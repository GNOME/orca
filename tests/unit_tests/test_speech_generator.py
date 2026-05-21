# Unit tests for speech_generator.py methods.
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

# pylint: disable=wrong-import-position
# pylint: disable=import-outside-toplevel
# pylint: disable=protected-access

"""Unit tests for speech_generator.py methods."""

from __future__ import annotations

from dataclasses import fields
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from .orca_test_context import OrcaTestContext


@pytest.mark.unit
class TestSpeechGeneratorVoice:
    """Tests SpeechGenerator.voice() voice-type selection."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for speech_generator dependencies (leaving acss/speechserver real)."""

        additional_modules = [
            "orca.input_event_manager",
            "orca.math_presenter",
            "orca.object_properties",
            "orca.speech_presenter",
            "orca.text_attribute_manager",
            "orca.ax_document",
            "orca.ax_hypertext",
            "orca.ax_table",
            "orca.ax_text",
            "orca.ax_utilities",
            "orca.ax_value",
        ]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        ax_utilities_mock = essential_modules["orca.ax_utilities"]
        ax_utilities_mock.AXUtilities = test_context.Mock()
        ax_utilities_mock.AXUtilities.is_link = test_context.Mock(return_value=False)

        return essential_modules

    def _make_context(self, test_context: OrcaTestContext):
        """Returns a minimal speech-generator context with default and uppercase voices."""

        from orca.acss import ACSS
        from orca.speechserver import VoiceType

        context = test_context.Mock()
        context.voices = {
            VoiceType.DEFAULT: ACSS({}),
            VoiceType.UPPERCASE: ACSS({}),
        }
        context.speech_server = test_context.Mock()
        context.in_preferences_window = False
        context.language = ""
        context.dialect = ""
        return context

    def test_voice_uses_uppercase_voice_for_uppercase_string(
        self, test_context: OrcaTestContext
    ) -> None:
        """voice() must select the uppercase voice for an uppercase string passed by the caller."""

        self._setup_dependencies(test_context)
        from orca.acss import ACSS
        from orca.speech_generator import SpeechGenerator
        from orca.speechserver import VoiceType

        generator = SpeechGenerator(test_context.Mock())
        generator._resolve_language_and_dialect = test_context.Mock(return_value=("", ""))
        context = self._make_context(test_context)

        result = generator.voice(string="HELLO", obj=test_context.Mock(), context=context)

        assert result[0][ACSS.VOICE_TYPE] == VoiceType.UPPERCASE

    def test_voice_uses_default_voice_for_mixed_case_string(
        self, test_context: OrcaTestContext
    ) -> None:
        """voice() must select the default voice for a non-uppercase string."""

        self._setup_dependencies(test_context)
        from orca.acss import ACSS
        from orca.speech_generator import SpeechGenerator
        from orca.speechserver import VoiceType

        generator = SpeechGenerator(test_context.Mock())
        generator._resolve_language_and_dialect = test_context.Mock(return_value=("", ""))
        context = self._make_context(test_context)

        result = generator.voice(string="hello", obj=test_context.Mock(), context=context)

        assert result[0][ACSS.VOICE_TYPE] == VoiceType.DEFAULT


@pytest.mark.unit
class TestSpeechGeneratorMisspelledIndicator:
    """Tests _generate_text_with_attribute_changes honors speak_misspelled_indicator."""

    def _setup(self, test_context: OrcaTestContext, *, speak_misspelled: bool):
        """Returns (essential_modules, context) with a single misspelled attribute run."""

        additional_modules = [
            "orca.input_event_manager",
            "orca.math_presenter",
            "orca.object_properties",
            "orca.speech_presenter",
            "orca.text_attribute_manager",
            "orca.ax_document",
            "orca.ax_hypertext",
            "orca.ax_table",
            "orca.ax_text",
            "orca.ax_utilities",
            "orca.ax_value",
        ]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        ax_utilities = test_context.Mock()
        ax_utilities.is_terminal = test_context.Mock(return_value=False)
        ax_utilities.get_all_text_attributes = test_context.Mock(
            return_value=[(0, 3, {"language": "en-us"})]
        )
        ax_utilities.string_has_spelling_error = test_context.Mock(return_value=True)
        ax_utilities.string_has_grammar_error = test_context.Mock(return_value=False)
        essential_modules["orca.ax_utilities"].AXUtilities = ax_utilities

        essential_modules["orca.ax_text"].AXText.get_substring = test_context.Mock(
            return_value="Das"
        )

        presenter = essential_modules["orca.speech_presenter"].get_presenter.return_value
        presenter.adjust_for_presentation = test_context.Mock(return_value="Das")

        context = test_context.Mock()
        context.speak_misspelled_indicator = speak_misspelled
        return essential_modules, context

    def _generate(self, test_context: OrcaTestContext, essential_modules, context) -> list:
        """Runs _generate_text_with_attribute_changes for the misspelled run."""

        from orca.speech_generator import SpeechGenerator

        generator = SpeechGenerator(test_context.Mock())
        generator.voice = test_context.Mock(return_value=[])
        generator._context = context
        return generator._generate_text_with_attribute_changes(
            test_context.Mock(), 0, 3, announce_formatting=False
        )

    def test_misspelled_omitted_when_indicator_disabled(
        self, test_context: OrcaTestContext
    ) -> None:
        """The misspelled indicator must not be spoken when the setting is off."""

        essential_modules, context = self._setup(test_context, speak_misspelled=False)
        result = self._generate(test_context, essential_modules, context)

        assert essential_modules["orca.messages"].MISSPELLED not in result

    def test_misspelled_spoken_when_indicator_enabled(self, test_context: OrcaTestContext) -> None:
        """The misspelled indicator must be spoken when the setting is on."""

        essential_modules, context = self._setup(test_context, speak_misspelled=True)
        result = self._generate(test_context, essential_modules, context)

        assert essential_modules["orca.messages"].MISSPELLED in result


_GENERATOR_TEST_MODULES = [
    "orca.input_event_manager",
    "orca.math_presenter",
    "orca.object_properties",
    "orca.speech_presenter",
    "orca.text_attribute_manager",
    "orca.ax_object",
    "orca.ax_text",
    "orca.ax_utilities",
]


@pytest.mark.unit
class TestGeneratorContentSubjectBinding:
    """Tests per-object content accessors return the slice only for its subject object."""

    def test_content_accessors_bound_to_subject(self, test_context: OrcaTestContext) -> None:
        """The slice's string/offset/position are returned for its subject and no other object."""

        test_context.setup_shared_dependencies(_GENERATOR_TEST_MODULES)
        from orca.generator import ContentItem, ContentPosition
        from orca.speech_generator import SpeechGenerator, SpeechGeneratorContext

        subject = test_context.Mock()
        other = test_context.Mock()
        field_values = {field.name: None for field in fields(SpeechGeneratorContext)}
        field_values["content_subject"] = subject
        field_values["content_item"] = ContentItem(start_offset=0, end_offset=3, string="fix")
        field_values["content_position"] = ContentPosition(index=2, total=5)
        context = SpeechGeneratorContext(**field_values)

        generator = SpeechGenerator(test_context.Mock())
        generator._context = context

        assert generator._get_content_string(subject) == "fix"
        assert generator._get_start_offset(subject) == 0
        assert generator._get_content_position(subject) == ContentPosition(index=2, total=5)

        assert generator._get_content_string(other) is None
        assert generator._get_start_offset(other) is None
        assert generator._get_content_position(other) == ContentPosition()


@pytest.mark.unit
class TestGeneratorRoleSubjectBinding:
    """Tests the resolved role applies only to its subject object."""

    def test_resolved_role_bound_to_subject(self, test_context: OrcaTestContext) -> None:
        """resolved_role is returned for its subject; other objects get their own role."""

        essential_modules = test_context.setup_shared_dependencies(_GENERATOR_TEST_MODULES)
        from orca.speech_generator import SpeechGenerator, SpeechGeneratorContext

        essential_modules["orca.ax_object"].AXObject.get_role = test_context.Mock(
            return_value="heading"
        )

        subject = test_context.Mock()
        other = test_context.Mock()
        field_values = {field.name: None for field in fields(SpeechGeneratorContext)}
        field_values["resolved_role"] = "link"
        field_values["role_subject"] = subject
        context = SpeechGeneratorContext(**field_values)

        generator = SpeechGenerator(test_context.Mock())
        generator._context = context

        assert generator._get_resolved_role(subject) == "link"
        assert generator._get_resolved_role(other) == "heading"
