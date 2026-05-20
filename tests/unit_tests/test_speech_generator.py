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
