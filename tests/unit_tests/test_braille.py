# Unit tests for braille.py functionality.
#
# Copyright 2026 Igalia, S.L.
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

# pylint: disable=protected-access
# pylint: disable=import-outside-toplevel

"""Unit tests for braille.py functionality."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext


@pytest.mark.unit
class TestBrailleLineRanges:
    """Tests for braille line range computation."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> None:
        debug_mock = test_context.Mock()
        debug_mock.LEVEL_INFO = 800
        debug_mock.print_message = test_context.Mock()
        debug_mock.print_tokens = test_context.Mock()

        ax_event_synthesizer_mock = test_context.Mock()
        ax_event_synthesizer_mock.AXEventSynthesizer = test_context.Mock()

        ax_hypertext_mock = test_context.Mock()
        ax_hypertext_mock.AXHypertext = test_context.Mock()

        ax_object_mock = test_context.Mock()
        ax_object_mock.AXObject = test_context.Mock()

        ax_text_mock = test_context.Mock()
        ax_text_mock.AXText = test_context.Mock()
        ax_text_mock.AXTextAttribute = test_context.Mock()

        platform_mock = test_context.Mock()
        platform_mock.tablesdir = "/tmp"

        braille_presenter_mock = test_context.Mock()
        braille_presenter_mock.get_presenter.return_value.use_braille.return_value = True

        test_context.patch_modules(
            {
                "orca.braille_monitor": test_context.Mock(),
                "orca.braille_presenter": braille_presenter_mock,
                "orca.brltablenames": test_context.Mock(),
                "orca.cmdnames": test_context.Mock(),
                "orca.debug": debug_mock,
                "orca.script_manager": test_context.Mock(),
                "orca.text_attribute_manager": test_context.Mock(),
                "orca.ax_event_synthesizer": ax_event_synthesizer_mock,
                "orca.ax_hypertext": ax_hypertext_mock,
                "orca.ax_object": ax_object_mock,
                "orca.ax_text": ax_text_mock,
                "orca.orca_platform": platform_mock,
            }
        )

    def test_compute_ranges_basic(self, test_context: OrcaTestContext) -> None:
        """Compute ranges across words when the display width is exceeded."""

        self._setup_dependencies(test_context)
        from orca import braille

        ranges = braille._compute_ranges("Hello world", -1, 10)
        assert ranges == [[0, 6], [6, 11]]

    def test_compute_ranges_long_word(self, test_context: OrcaTestContext) -> None:
        """Compute ranges for a single long word."""

        self._setup_dependencies(test_context)
        from orca import braille

        ranges = braille._compute_ranges("abcdefghijk", -1, 4)
        assert ranges == [[0, 4], [4, 8], [8, 11]]

    def test_compute_ranges_splits_on_focus_offset(self, test_context: OrcaTestContext) -> None:
        """Compute ranges that split on the focus offset."""

        self._setup_dependencies(test_context)
        from orca import braille

        ranges = braille._compute_ranges("abc def", 4, 10)
        assert ranges == [[0, 4], [4, 7]]

    def test_get_region_at_cell_returns_region(self, test_context: OrcaTestContext) -> None:
        """Return the region and offset for a given cell."""

        self._setup_dependencies(test_context)
        from orca import braille

        braille._clear()
        region = braille.Region("abc", 0)
        line = braille.Line(region)
        braille._set_lines([line])

        region_info = braille.get_region_at_cell(2)
        braille_region, offset_in_region = region_info
        assert braille_region is region
        assert offset_in_region == 1

    def test_get_caret_context_non_text(self, test_context: OrcaTestContext) -> None:
        """Return no caret context for non-text regions."""

        self._setup_dependencies(test_context)
        from orca import braille

        braille._clear()
        region = braille.Region("abc", 0)
        braille._set_lines([braille.Line(region)])

        event = test_context.Mock()
        event.event = {"argument": 0}
        context = braille.get_caret_context(event)
        obj, offset = context
        assert obj is None
        assert offset == -1

    def test_focus_invalidation_updates_focus_offset(self, test_context: OrcaTestContext) -> None:
        """Ensure cache invalidation updates focus offsets when focus changes."""

        self._setup_dependencies(test_context)
        from orca import braille

        braille._clear()
        region_one = braille.Region("one", 0)
        region_two = braille.Region("two", 0)
        line = braille.Line()
        line.add_regions([region_one, region_two])
        braille._set_lines([line])

        braille._set_focus(region_one)
        first_info = line.get_info()
        assert first_info.focus_offset == 0

        braille._set_focus(region_two)
        second_info = line.get_info()
        assert second_info.focus_offset == len(region_one.string)

    def test_display_message_sets_focus(self, test_context: OrcaTestContext) -> None:
        """Display message should create a line and set focus."""

        self._setup_dependencies(test_context)
        from orca import braille

        braille.refresh = test_context.Mock()

        braille.display_message("hello", flash_time=0)

        assert len(braille._STATE.lines) == 1
        line = braille._STATE.lines[0]
        regions = line.get_regions()
        assert len(regions) == 1
        assert braille._STATE.region_with_focus is regions[0]

    def test_kill_flash_restores_state(self, test_context: OrcaTestContext) -> None:
        """Kill flash should restore the saved state when present."""

        self._setup_dependencies(test_context)
        from orca import braille

        braille.refresh = test_context.Mock()

        region = braille.Region("restore", 0)
        saved_line = braille.Line(region)
        saved_state = braille._FlashState([saved_line], region, [3, 0], 500)
        braille._STATE.saved = saved_state
        braille._STATE.lines = []
        braille._STATE.region_with_focus = None
        braille._STATE.viewport = [0, 0]
        braille._STATE.flash_event_source_id = -1

        braille.kill_flash(restore_saved=True)

        assert braille._STATE.lines == saved_state.lines
        assert braille._STATE.region_with_focus is saved_state.region_with_focus
        assert braille._STATE.viewport == saved_state.viewport
        assert braille._STATE.flash_event_source_id == 0

    def test_setup_key_ranges_skips_when_constants_missing(
        self, test_context: OrcaTestContext
    ) -> None:
        """setup_key_ranges should no-op if required constants are missing."""

        self._setup_dependencies(test_context)
        from orca import braille

        original_range_all = braille.BRLAPI_RANGE_TYPE_ALL
        original_range_command = braille.BRLAPI_RANGE_TYPE_COMMAND
        original_key_type = braille.BRLAPI_KEY_TYPE_CMD
        original_key_route = braille.BRLAPI_KEY_CMD_ROUTE

        braille.BRLAPI_RANGE_TYPE_ALL = None
        braille.BRLAPI_RANGE_TYPE_COMMAND = None
        braille.BRLAPI_KEY_TYPE_CMD = None
        braille.BRLAPI_KEY_CMD_ROUTE = None
        braille._STATE.brlapi_running = True
        braille._STATE.brlapi = test_context.Mock()
        braille._STATE.brlapi.ignoreKeys = test_context.Mock()

        try:
            braille.setup_key_ranges([1, 2, 3])
            braille._STATE.brlapi.ignoreKeys.assert_not_called()
        finally:
            braille.BRLAPI_RANGE_TYPE_ALL = original_range_all
            braille.BRLAPI_RANGE_TYPE_COMMAND = original_range_command
            braille.BRLAPI_KEY_TYPE_CMD = original_key_type
            braille.BRLAPI_KEY_CMD_ROUTE = original_key_route

    def test_prepare_refresh_disabled_shuts_down(self, test_context: OrcaTestContext) -> None:
        """_prepare_refresh should shut down and reset state when braille is disabled."""

        self._setup_dependencies(test_context)
        from orca import braille, braille_presenter

        mock_presenter = braille_presenter.get_presenter.return_value  # type: ignore[attr-defined] # pylint: disable=no-member
        mock_presenter.use_braille.return_value = False
        braille._STATE.brlapi_running = True
        braille._STATE.last_text_info = braille._TextInfo(object(), 1, 2, 3)
        braille.shutdown = test_context.Mock()

        assert braille._prepare_refresh(stop_flash=False) is False
        braille.shutdown.assert_called_once()
        assert braille._STATE.last_text_info == braille._empty_text_info()

    def test_prepare_refresh_empty_lines_clears_braille(
        self, test_context: OrcaTestContext
    ) -> None:
        """_prepare_refresh should clear braille and reset state with no lines."""

        self._setup_dependencies(test_context)
        from orca import braille

        braille._STATE.lines = []
        braille._STATE.last_text_info = braille._TextInfo(object(), 1, 2, 3)
        braille._clear_braille = test_context.Mock()

        assert braille._prepare_refresh(stop_flash=False) is False
        braille._clear_braille.assert_called_once()
        assert braille._STATE.last_text_info == braille._empty_text_info()

    def test_set_contracted_braille_toggles_for_keyboard_event(
        self, test_context: OrcaTestContext
    ) -> None:
        """Non-braille events should toggle contracted braille."""

        self._setup_dependencies(test_context)
        from orca import braille

        braille._STATE.enable_contracted_braille = False
        braille.refresh = test_context.Mock()
        event = test_context.Mock()
        event.type = "keyboard"

        braille.toggle_contracted_braille(event)

        assert braille._STATE.enable_contracted_braille is True

    def test_set_contracted_braille_uses_braille_flags(self, test_context: OrcaTestContext) -> None:
        """Braille events should use the BrlAPI toggle flag."""

        self._setup_dependencies(test_context)
        from orca import braille

        original_toggle = braille.BRLAPI_KEY_FLG_TOGGLE_ON
        braille.refresh = test_context.Mock()
        braille.BRLAPI_KEY_FLG_TOGGLE_ON = 1
        event = test_context.Mock()
        event.type = "braille"
        event.event = {"flags": 1}

        try:
            braille.toggle_contracted_braille(event)
            assert braille._STATE.enable_contracted_braille is True
        finally:
            braille.BRLAPI_KEY_FLG_TOGGLE_ON = original_toggle
