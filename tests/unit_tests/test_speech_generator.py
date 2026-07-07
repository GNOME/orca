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
from typing import TYPE_CHECKING, Any

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
        ax_utilities.attributes_indicate_spelling_error = test_context.Mock(return_value=True)
        ax_utilities.attributes_indicate_grammar_error = test_context.Mock(return_value=False)
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


@pytest.mark.unit
class TestSpeechGeneratorTextRole:
    """Tests speech generation for text-role objects."""

    def test_text_role_includes_invalid_state(self, test_context: OrcaTestContext) -> None:
        """Text-role where-am-I output should include invalid-entry error details."""

        test_context.setup_shared_dependencies(_GENERATOR_TEST_MODULES)
        from orca.speech_generator import SpeechGenerator

        generator = SpeechGenerator(test_context.Mock())
        obj = test_context.Mock()
        generator._generate_default_prefix = test_context.Mock(return_value=[])
        generator._generate_accessible_label_and_name = test_context.Mock(return_value=["Name"])
        generator._generate_state_read_only = test_context.Mock(return_value=[])
        generator._generate_accessible_role = test_context.Mock(return_value=["text"])
        generator._generate_pause = test_context.Mock(return_value=[])
        generator._generate_text_indentation = test_context.Mock(return_value=[])
        generator._generate_text_line = test_context.Mock(return_value=["value"])
        generator._generate_accessible_placeholder_text = test_context.Mock(return_value=[])
        generator._generate_text_selection = test_context.Mock(return_value=[])
        generator._generate_state_invalid = test_context.Mock(return_value=["invalid: error"])
        generator._generate_keyboard_mnemonic = test_context.Mock(return_value=[])
        generator._generate_default_suffix = test_context.Mock(return_value=[])

        result = generator._generate_text(obj)

        assert result == ["Name", "text", "value", "invalid: error"]


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
class TestGeneratorCache:
    """Tests the manager-backed cache used by all generator modes."""

    def test_import_registers_generator_cache_namespaces(
        self, test_context: OrcaTestContext
    ) -> None:
        """Importing Generator registers presentation caches with their two-second policy."""

        test_context.setup_shared_dependencies(_GENERATOR_TEST_MODULES)
        from orca import ax_cache_manager

        manager = ax_cache_manager.get_manager()
        register = test_context.patch_object(
            manager,
            "register_cache",
            wraps=manager.register_cache,
        )

        from orca.generator import Generator

        assert register.call_count == 13
        assert {call.args[0] for call in register.call_args_list} == {Generator._CACHE}
        for call in register.call_args_list:
            assert call.kwargs["lifetime"] is ax_cache_manager.Lifetime.PROCESS
            assert call.kwargs["clear_on_demand"] is ax_cache_manager.ClearPolicy.PRESERVE
            assert (
                call.kwargs["clear_interval_seconds"]
                == Generator._CACHE._CACHE_CLEAR_INTERVAL_SECONDS
            )
        assert Generator._CACHE._CACHE_CLEAR_INTERVAL_SECONDS == 2

    def test_manager_clear_cache_now_preserves_generator_cache(
        self, test_context: OrcaTestContext
    ) -> None:
        """Routine cache clearing does not interrupt one presentation's generator reuse."""

        test_context.setup_shared_dependencies(_GENERATOR_TEST_MODULES)
        from orca import ax_cache_manager
        from orca.generator import Generator

        Generator._CACHE.set_value(Generator._CACHE.DESCRIPTION, 123, ["description"])

        ax_cache_manager.get_manager().clear_cache_now("test reason")

        assert Generator._CACHE.has_value(Generator._CACHE.DESCRIPTION, 123)
        assert Generator._CACHE.get_value(Generator._CACHE.DESCRIPTION, 123) == ["description"]

    def test_cached_lists_are_isolated_from_callers(self, test_context: OrcaTestContext) -> None:
        """Mutating a stored or returned list must not corrupt the cached value."""

        test_context.setup_shared_dependencies(_GENERATOR_TEST_MODULES)
        from orca.generator import Generator

        stored = ["text"]
        Generator._CACHE.set_value(Generator._CACHE.TEXT_SUBSTRING, 456, stored)
        stored.append("mutated after set")
        first = Generator._CACHE.get_value(Generator._CACHE.TEXT_SUBSTRING, 456)
        assert first == ["text"]

        first.append("voice appended by caller")
        assert Generator._CACHE.get_value(Generator._CACHE.TEXT_SUBSTRING, 456) == ["text"]

    def test_presentation_scope_keeps_values_bounded(self, test_context: OrcaTestContext) -> None:
        """Presentation-scoped values do not leak into the two-second fallback cache."""

        test_context.setup_shared_dependencies(_GENERATOR_TEST_MODULES)
        from orca import ax_cache_manager
        from orca.generator import Generator

        key = object()
        Generator._CACHE.set_value(Generator._CACHE.DESCRIPTION, key, ["fallback"])

        with Generator.presentation_scope():
            assert Generator._CACHE.has_value(Generator._CACHE.DESCRIPTION, key) is False
            Generator._CACHE.set_value(Generator._CACHE.DESCRIPTION, key, ["scoped"])
            assert Generator._CACHE.get_value(Generator._CACHE.DESCRIPTION, key) == ["scoped"]
            with Generator.presentation_scope():
                assert Generator._CACHE.get_value(Generator._CACHE.DESCRIPTION, key) == ["scoped"]

        assert Generator._CACHE.get_value(Generator._CACHE.DESCRIPTION, key) == ["fallback"]
        assert not ax_cache_manager.get_manager()._scoped_values

    def test_static_text_cache_returns_copy(self, test_context: OrcaTestContext) -> None:
        """Cached static text must not be mutable by callers."""

        test_context.setup_shared_dependencies(_GENERATOR_TEST_MODULES)
        from orca import ax_cache_manager
        from orca.generator import Generator, GeneratorMode

        generator = Generator(test_context.Mock(), GeneratorMode.SPEECH)
        obj = test_context.Mock()
        key = ax_cache_manager.get_object_key(obj)
        Generator._CACHE.set_value(Generator._CACHE.STATIC_TEXT, key, ["cached"])

        result = generator._generate_accessible_static_text(obj)

        result.append("caller mutation")
        assert Generator._CACHE.get_value(Generator._CACHE.STATIC_TEXT, key) == ["cached"]

    def test_static_text_generation_does_not_mutate_description_cache(
        self, test_context: OrcaTestContext
    ) -> None:
        """Unrelated-label fallback must not pollute cached descriptions."""

        test_context.setup_shared_dependencies(_GENERATOR_TEST_MODULES)
        from orca import ax_cache_manager
        from orca.generator import Generator, GeneratorMode

        script = test_context.Mock()
        label = test_context.Mock()
        obj = test_context.Mock()
        script.utilities.unrelated_labels.return_value = [label]
        generator = Generator(script, GeneratorMode.SPEECH)
        generator._generate_text_expanding_embedded_objects = test_context.Mock(return_value=[])
        generator._generate_accessible_name = test_context.Mock(return_value=["label name"])
        key = ax_cache_manager.get_object_key(obj)
        Generator._CACHE.set_value(Generator._CACHE.DESCRIPTION, key, [])

        result = generator._generate_accessible_static_text(obj)

        assert result == ["label name"]
        assert Generator._CACHE.get_value(Generator._CACHE.DESCRIPTION, key) == []


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


@pytest.mark.unit
class TestGeneratorCellsToPresent:
    """Tests _cells_to_present: a lone cell vs. the whole row."""

    def _setup(
        self, test_context: OrcaTestContext, *, full_row: bool
    ) -> tuple[Any, dict[str, MagicMock]]:
        essential_modules = test_context.setup_shared_dependencies(_GENERATOR_TEST_MODULES)
        from orca.generator import PresentationReason
        from orca.speech_generator import SpeechGenerator, SpeechGeneratorContext

        script = test_context.Mock()
        script.utilities.should_read_full_row = test_context.Mock(return_value=full_row)
        generator = SpeechGenerator(script)
        generator._reading_row = False
        field_values = {field.name: None for field in fields(SpeechGeneratorContext)}
        field_values["reason"] = PresentationReason.FOCUS_CHANGE
        generator._context = SpeechGeneratorContext(**field_values)
        return generator, essential_modules

    def test_lone_cell_when_not_reading_a_row(self, test_context: OrcaTestContext) -> None:
        """A cell that does not trigger full-row reading is presented by itself."""

        generator, _modules = self._setup(test_context, full_row=False)
        cell = test_context.Mock()
        assert generator._cells_to_present(cell) == (False, [cell])

    def test_whole_row_when_full_row_reading_is_triggered(
        self, test_context: OrcaTestContext
    ) -> None:
        """A cell that triggers full-row reading yields every showing cell in its row."""

        generator, essential_modules = self._setup(test_context, full_row=True)
        row_cells = [test_context.Mock(), test_context.Mock(), test_context.Mock()]
        ax_utilities = essential_modules["orca.ax_utilities"].AXUtilities
        ax_utilities.get_showing_cells_in_same_row = test_context.Mock(return_value=row_cells)
        ax_utilities.is_spreadsheet_cell = test_context.Mock(return_value=False)

        assert generator._cells_to_present(test_context.Mock()) == (True, row_cells)


@pytest.mark.unit
class TestGeneratorCombineCellResults:
    """Tests _combine_cell_results: which cells carry their surrounding context."""

    def _setup(
        self,
        test_context: OrcaTestContext,
        *,
        cells: list,
        reading_row: bool,
        detailed: bool,
    ) -> tuple[Any, list[bool], dict[str, MagicMock]]:
        essential_modules = test_context.setup_shared_dependencies(_GENERATOR_TEST_MODULES)
        from orca.generator import PresentationReason
        from orca.speech_generator import SpeechGenerator, SpeechGeneratorContext

        essential_modules["orca.ax_utilities"].AXUtilities.find_ancestor = test_context.Mock(
            return_value=None
        )

        generator = SpeechGenerator(test_context.Mock())
        generator._reading_row = False
        reason = (
            PresentationReason.WHERE_AM_I_DETAILED if detailed else PresentationReason.FOCUS_CHANGE
        )
        field_values = {field.name: None for field in fields(SpeechGeneratorContext)}
        field_values["reason"] = reason
        generator._context = SpeechGeneratorContext(**field_values)

        generator._cells_to_present = test_context.Mock(return_value=(reading_row, cells))
        generator._generate_position_in_list = test_context.Mock(return_value=[])

        included: list[bool] = []

        def _record(_cell: Any) -> list[Any]:
            included.append(generator._context.include_context)
            return []

        generator._generate_table_cell_contents = test_context.Mock(side_effect=_record)
        return generator, included, essential_modules

    def test_lone_cell_carries_its_context(self, test_context: OrcaTestContext) -> None:
        """A lone focused cell is generated with its surrounding context included."""

        cell = test_context.Mock()
        generator, included, _modules = self._setup(
            test_context, cells=[cell], reading_row=False, detailed=False
        )
        generator._combine_cell_results(cell)
        assert included == [True]

    def test_full_row_includes_context_only_for_the_first_cell(
        self, test_context: OrcaTestContext
    ) -> None:
        """Reading a row includes context only for the first cell."""

        cells = [test_context.Mock(), test_context.Mock(), test_context.Mock()]
        generator, included, _modules = self._setup(
            test_context, cells=cells, reading_row=True, detailed=False
        )
        generator._combine_cell_results(cells[0])
        assert included == [True, False, False]

    def test_detailed_where_am_i_includes_context_for_every_cell(
        self, test_context: OrcaTestContext
    ) -> None:
        """Detailed where-am-i keeps full per-cell context across the row."""

        cells = [test_context.Mock(), test_context.Mock(), test_context.Mock()]
        generator, included, _modules = self._setup(
            test_context, cells=cells, reading_row=True, detailed=True
        )
        generator._combine_cell_results(cells[0])
        assert included == [True, True, True]

    def test_named_row_is_presented_as_the_row_itself(self, test_context: OrcaTestContext) -> None:
        """A named, non-layout row is presented as the row, not as its cells."""

        cells = [test_context.Mock(), test_context.Mock()]
        generator, included, essential_modules = self._setup(
            test_context, cells=cells, reading_row=True, detailed=False
        )
        row = test_context.Mock()
        essential_modules["orca.ax_utilities"].AXUtilities.find_ancestor = test_context.Mock(
            return_value=row
        )
        essential_modules["orca.ax_utilities"].AXUtilities.is_layout_only = test_context.Mock(
            return_value=False
        )
        essential_modules["orca.ax_object"].AXObject.get_name = test_context.Mock(
            return_value="Totals"
        )
        generator.generate = test_context.Mock(return_value=["row presentation"])

        assert generator._combine_cell_results(cells[0]) == ["row presentation"]
        generator.generate.assert_called_once_with(row)
        generator._generate_table_cell_contents.assert_not_called()
        assert included == []
