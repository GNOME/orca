# Unit tests for ax_event_synthesizer.py methods.
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

# pylint: disable=protected-access
# pylint: disable=wrong-import-order
# pylint: disable=wrong-import-position
# pylint: disable=import-outside-toplevel
# pylint: disable=too-many-public-methods

"""Unit tests for ax_event_synthesizer.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi
from gi.repository import GLib

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext
    from unittest.mock import MagicMock

@pytest.mark.unit
class TestAXEventSynthesizer:
    """Test AXEventSynthesizer class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for ax_event_synthesizer dependencies."""

        additional_modules = [
            "orca.ax_component",
            "orca.ax_object",
            "orca.ax_text",
            "orca.ax_utilities_debugging",
            "orca.ax_utilities_role",
        ]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        ax_component_mock = essential_modules["orca.ax_component"].AXComponent
        ax_component_mock.get_rect = test_context.Mock()
        ax_component_mock.get_position = test_context.Mock(return_value=(0, 0))
        ax_component_mock.get_rect_intersection = test_context.Mock()
        ax_component_mock.is_empty_rect = test_context.Mock(return_value=False)
        ax_component_mock.scroll_object_to_location = test_context.Mock()
        ax_component_mock.scroll_object_to_point = test_context.Mock()

        def mock_rect(x=0, y=0, width=100, height=50):
            rect = test_context.Mock()
            rect.x = x
            rect.y = y
            rect.width = width
            rect.height = height
            return rect

        ax_component_mock.get_rect.return_value = mock_rect()

        ax_text_mock = essential_modules["orca.ax_text"].AXText
        ax_text_mock.get_caret_offset = test_context.Mock(return_value=0)
        ax_text_mock.get_character_rect = test_context.Mock(return_value=mock_rect())
        ax_text_mock.set_caret_offset = test_context.Mock()
        ax_text_mock.scroll_substring_to_location = test_context.Mock()
        ax_text_mock.scroll_substring_to_point = test_context.Mock()

        ax_utilities_role_mock = essential_modules["orca.ax_utilities_role"].AXUtilitiesRole
        ax_utilities_role_mock.is_application = test_context.Mock(return_value=False)

        ax_utilities_debugging_mock = essential_modules["orca.ax_utilities_debugging"]
        ax_utilities_debugging_mock.AXUtilitiesDebugging = test_context.Mock()
        ax_utilities_debugging_mock.AXUtilitiesDebugging.actions_as_string = test_context.Mock(
            return_value="mock actions"
        )

        if "orca.debug" in essential_modules:
            debug_mock = essential_modules["orca.debug"]
            debug_mock.LEVEL_INFO = 800
            debug_mock.debugLevel = 2

        return essential_modules

    def _setup_successful_mouse_event_mocks(self, test_context, essential_modules) -> None:
        """Helper method to set up mocks for successful mouse event completion."""

        ax_text_mock = essential_modules["orca.ax_text"].AXText
        char_rect = test_context.Mock()
        char_rect.x = 50
        char_rect.y = 60
        char_rect.width = 10
        char_rect.height = 15
        ax_text_mock.get_character_rect.return_value = char_rect
        ax_component_mock = essential_modules["orca.ax_component"].AXComponent
        obj_rect = test_context.Mock()
        obj_rect.x = 40
        obj_rect.y = 50
        ax_component_mock.get_rect.return_value = obj_rect
        ax_component_mock.get_rect_intersection.return_value = test_context.Mock()
        ax_component_mock.is_empty_rect.return_value = False

    def test_highest_ancestor_true_when_parent_is_none(self, test_context: OrcaTestContext) -> None:
        """Test _highest_ancestor returns True when parent is None."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_event_synthesizer import AXEventSynthesizer

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        ax_object_mock = essential_modules["orca.ax_object"].AXObject
        ax_object_mock.get_parent.return_value = None
        result = AXEventSynthesizer._highest_ancestor(mock_accessible)
        assert result is True
        ax_object_mock.get_parent.assert_called_once_with(mock_accessible)

    def test_highest_ancestor_true_when_parent_is_application(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test _highest_ancestor returns True when parent is application."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_event_synthesizer import AXEventSynthesizer

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_parent = test_context.Mock(spec=Atspi.Accessible)
        ax_object_mock = essential_modules["orca.ax_object"].AXObject
        ax_object_mock.get_parent.return_value = mock_parent
        ax_utilities_role_mock = essential_modules["orca.ax_utilities_role"].AXUtilitiesRole
        ax_utilities_role_mock.is_application.return_value = True
        result = AXEventSynthesizer._highest_ancestor(mock_accessible)
        assert result is True
        ax_object_mock.get_parent.assert_called_once_with(mock_accessible)
        ax_utilities_role_mock.is_application.assert_called_once_with(mock_parent)

    def test_is_scrolled_off_screen_false_when_no_ancestor(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test _is_scrolled_off_screen returns False when no ancestor found."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_event_synthesizer import AXEventSynthesizer

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        ax_object_mock = essential_modules["orca.ax_object"].AXObject
        ax_object_mock.find_ancestor.return_value = None
        result = AXEventSynthesizer._is_scrolled_off_screen(mock_accessible)
        assert result is False

    def test_is_scrolled_off_screen_true_when_outside_ancestor(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test _is_scrolled_off_screen returns True when object is outside ancestor."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_event_synthesizer import AXEventSynthesizer

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_ancestor = test_context.Mock(spec=Atspi.Accessible)
        ax_object_mock = essential_modules["orca.ax_object"].AXObject
        ax_object_mock.find_ancestor.return_value = mock_ancestor
        ax_component_mock = essential_modules["orca.ax_component"].AXComponent
        obj_rect = test_context.Mock()
        obj_rect.x = 200
        obj_rect.y = 200
        obj_rect.width = 100
        obj_rect.height = 50
        ancestor_rect = test_context.Mock()
        ancestor_rect.x = 0
        ancestor_rect.y = 0
        ancestor_rect.width = 100
        ancestor_rect.height = 100
        ax_component_mock.get_rect.side_effect = [obj_rect, ancestor_rect]
        ax_component_mock.get_rect_intersection.return_value = test_context.Mock()
        ax_component_mock.is_empty_rect.return_value = True
        result = AXEventSynthesizer._is_scrolled_off_screen(mock_accessible)
        assert result is True

    def test_generate_mouse_event_success(self, test_context: OrcaTestContext) -> None:
        """Test _generate_mouse_event returns True on successful event generation."""

        self._setup_dependencies(test_context)
        from orca.ax_event_synthesizer import AXEventSynthesizer

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_device_new = test_context.Mock()
        test_context.patch("gi.repository.Atspi.Device.new", new=mock_device_new)
        mock_generate = test_context.Mock()
        test_context.patch(
            "gi.repository.Atspi.Device.generate_mouse_event", new=mock_generate
        )
        mock_device = test_context.Mock()
        mock_device_new.return_value = mock_device
        result = AXEventSynthesizer._generate_mouse_event(mock_accessible, 50, 25, "b1c")
        assert result is True
        mock_device_new.assert_called_once()
        mock_generate.assert_called_once_with(mock_device, mock_accessible, 50, 25, "b1c")

    def test_generate_mouse_event_exception_returns_false(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test _generate_mouse_event returns False on GLib.GError exception."""

        self._setup_dependencies(test_context)
        from orca.ax_event_synthesizer import AXEventSynthesizer

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_device_new = test_context.Mock()
        test_context.patch("gi.repository.Atspi.Device.new", new=mock_device_new)
        mock_generate = test_context.Mock()
        test_context.patch(
            "gi.repository.Atspi.Device.generate_mouse_event", new=mock_generate
        )
        mock_device = test_context.Mock()
        mock_device_new.return_value = mock_device
        mock_generate.side_effect = GLib.GError("Test error")
        result = AXEventSynthesizer._generate_mouse_event(mock_accessible, 50, 25, "b1c")
        assert result is False

    def test_mouse_event_on_character_uses_caret_offset_when_none(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test _mouse_event_on_character uses caret offset when offset is None."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_event_synthesizer import AXEventSynthesizer

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        ax_text_mock = essential_modules["orca.ax_text"].AXText
        ax_text_mock.get_caret_offset.return_value = 5
        self._setup_successful_mouse_event_mocks(test_context, essential_modules)
        mock_generate = test_context.Mock()
        test_context.patch_object(AXEventSynthesizer, "_generate_mouse_event", new=mock_generate)
        mock_generate.return_value = True
        result = AXEventSynthesizer._mouse_event_on_character(mock_accessible, None, "b1c")
        ax_text_mock.get_caret_offset.assert_called_once_with(mock_accessible)
        assert result is True

    def test_route_to_character_calls_mouse_event_with_abs(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test route_to_character calls _mouse_event_on_character with 'abs' event."""

        self._setup_dependencies(test_context)
        from orca.ax_event_synthesizer import AXEventSynthesizer

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_event = test_context.Mock()
        test_context.patch_object(
            AXEventSynthesizer, "_mouse_event_on_character", new=mock_event
        )
        mock_event.return_value = True
        result = AXEventSynthesizer.route_to_character(mock_accessible, 15)
        mock_event.assert_called_once_with(mock_accessible, 15, "abs")
        assert result is True

    def test_route_to_object_calls_mouse_event_with_abs(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test route_to_object calls _mouse_event_on_object with 'abs' event."""

        self._setup_dependencies(test_context)
        from orca.ax_event_synthesizer import AXEventSynthesizer

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_event = test_context.Mock()
        test_context.patch_object(AXEventSynthesizer, "_mouse_event_on_object", new=mock_event)
        mock_event.return_value = True
        result = AXEventSynthesizer.route_to_object(mock_accessible)
        mock_event.assert_called_once_with(mock_accessible, "abs")
        assert result is True

    def test_click_character_calls_mouse_event_with_button_click(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test click_character calls _mouse_event_on_character with button click event."""

        self._setup_dependencies(test_context)
        from orca.ax_event_synthesizer import AXEventSynthesizer

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_event = test_context.Mock()
        test_context.patch_object(
            AXEventSynthesizer, "_mouse_event_on_character", new=mock_event
        )
        mock_event.return_value = True
        result = AXEventSynthesizer.click_character(mock_accessible, 20, 2)
        mock_event.assert_called_once_with(mock_accessible, 20, "b2c")
        assert result is True

    def test_click_object_calls_mouse_event_with_button_click(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test click_object calls _mouse_event_on_object with button click event."""

        self._setup_dependencies(test_context)
        from orca.ax_event_synthesizer import AXEventSynthesizer

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_event = test_context.Mock()
        test_context.patch_object(AXEventSynthesizer, "_mouse_event_on_object", new=mock_event)
        mock_event.return_value = True
        result = AXEventSynthesizer.click_object(mock_accessible, 3)
        mock_event.assert_called_once_with(mock_accessible, "b3c")
        assert result is True

    def test_scroll_into_view_calls_scroll_to_location_anywhere(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test scroll_into_view calls _scroll_to_location with ANYWHERE."""

        self._setup_dependencies(test_context)
        from orca.ax_event_synthesizer import AXEventSynthesizer

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_scroll = test_context.Mock()
        test_context.patch_object(AXEventSynthesizer, "_scroll_to_location", new=mock_scroll)
        AXEventSynthesizer.scroll_into_view(mock_accessible, 5, 15)
        mock_scroll.assert_called_once_with(mock_accessible, Atspi.ScrollType.ANYWHERE, 5, 15)

    def test_scroll_to_center_calculates_center_coordinates(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test scroll_to_center calculates center coordinates of ancestor."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_event_synthesizer import AXEventSynthesizer

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_ancestor = test_context.Mock(spec=Atspi.Accessible)
        ax_object_mock = essential_modules["orca.ax_object"].AXObject
        ax_object_mock.find_ancestor.return_value = mock_ancestor
        ancestor_rect = test_context.Mock()
        ancestor_rect.x = 100
        ancestor_rect.y = 200
        ancestor_rect.width = 400
        ancestor_rect.height = 300
        ax_component_mock = essential_modules["orca.ax_component"].AXComponent
        ax_component_mock.get_rect.return_value = ancestor_rect
        mock_scroll = test_context.Mock()
        test_context.patch_object(AXEventSynthesizer, "_scroll_to_point", new=mock_scroll)
        AXEventSynthesizer.scroll_to_center(mock_accessible, 5, 15)

        mock_scroll.assert_called_once_with(mock_accessible, 300, 350, 5, 15)

    @pytest.mark.parametrize(
        "method_name,scroll_type",
        [
            pytest.param("scroll_to_top_edge", "Atspi.ScrollType.TOP_EDGE", id="top_edge"),
            pytest.param("scroll_to_top_left", "Atspi.ScrollType.TOP_LEFT", id="top_left"),
            pytest.param("scroll_to_left_edge", "Atspi.ScrollType.LEFT_EDGE", id="left_edge"),
            pytest.param("scroll_to_bottom_edge", "Atspi.ScrollType.BOTTOM_EDGE", id="bottom_edge"),
            pytest.param(
                "scroll_to_bottom_right", "Atspi.ScrollType.BOTTOM_RIGHT", id="bottom_right"
            ),
            pytest.param("scroll_to_right_edge", "Atspi.ScrollType.RIGHT_EDGE", id="right_edge"),
        ],
    )
    def test_scroll_direction_methods(self, test_context, method_name, scroll_type) -> None:
        """Test all directional scroll methods call _scroll_to_location with correct type."""

        self._setup_dependencies(test_context)
        from orca.ax_event_synthesizer import AXEventSynthesizer

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        scroll_type_value = getattr(Atspi.ScrollType, scroll_type.split(".")[-1])
        mock_scroll = test_context.Mock()
        test_context.patch_object(AXEventSynthesizer, "_scroll_to_location", new=mock_scroll)
        method = getattr(AXEventSynthesizer, method_name)
        method(mock_accessible, 10, 20)
        mock_scroll.assert_called_once_with(mock_accessible, scroll_type_value, 10, 20)

    def test_try_all_clickable_actions_success_on_first_action(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test try_all_clickable_actions returns True on first successful action."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_event_synthesizer import AXEventSynthesizer

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        ax_object_mock = essential_modules["orca.ax_object"].AXObject
        ax_object_mock.do_named_action.return_value = True
        result = AXEventSynthesizer.try_all_clickable_actions(mock_accessible)
        assert result is True
        ax_object_mock.do_named_action.assert_called_once_with(mock_accessible, "click")

    def test_try_all_clickable_actions_false_when_all_fail(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test try_all_clickable_actions returns False when all actions fail."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_event_synthesizer import AXEventSynthesizer

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        ax_object_mock = essential_modules["orca.ax_object"].AXObject
        ax_object_mock.do_named_action.return_value = False
        result = AXEventSynthesizer.try_all_clickable_actions(mock_accessible)
        assert result is False
        assert ax_object_mock.do_named_action.call_count == 5

    def test_get_synthesizer_returns_singleton(self, test_context: OrcaTestContext) -> None:
        """Test get_synthesizer returns the singleton instance."""

        self._setup_dependencies(test_context)
        from orca.ax_event_synthesizer import get_synthesizer

        synthesizer1 = get_synthesizer()
        synthesizer2 = get_synthesizer()
        assert synthesizer1 is synthesizer2

    def test_mouse_event_on_character_returns_false_when_empty_rect(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test _mouse_event_on_character returns False when character rect is empty."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.ax_event_synthesizer import AXEventSynthesizer

        mock_obj = test_context.Mock(spec=Atspi.Accessible)

        ax_text_mock = essential_modules["orca.ax_text"].AXText
        ax_text_mock.get_caret_offset.return_value = 5
        empty_rect = test_context.Mock()
        empty_rect.x = empty_rect.y = empty_rect.width = empty_rect.height = 0
        ax_text_mock.get_character_rect.return_value = empty_rect

        ax_component_mock = essential_modules["orca.ax_component"].AXComponent
        ax_component_mock.is_empty_rect.return_value = True

        test_context.patch_object(
            AXEventSynthesizer, "_is_scrolled_off_screen", side_effect=lambda obj, offset: False
        )

        result = AXEventSynthesizer._mouse_event_on_character(mock_obj, 5, "abs")
        assert result is False

    def test_mouse_event_on_character_returns_false_when_caret_outside_object(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test _mouse_event_on_character returns False when caret is outside object bounds."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.ax_event_synthesizer import AXEventSynthesizer

        mock_obj = test_context.Mock(spec=Atspi.Accessible)

        ax_text_mock = essential_modules["orca.ax_text"].AXText
        ax_text_mock.get_caret_offset.return_value = 10
        char_rect = test_context.Mock()
        char_rect.x, char_rect.y, char_rect.width, char_rect.height = 100, 100, 10, 10
        ax_text_mock.get_character_rect.return_value = char_rect

        ax_component_mock = essential_modules["orca.ax_component"].AXComponent
        obj_rect = test_context.Mock()
        obj_rect.x, obj_rect.y, obj_rect.width, obj_rect.height = 200, 200, 50, 50
        ax_component_mock.get_rect.return_value = obj_rect
        empty_intersection = test_context.Mock()
        empty_intersection.width = empty_intersection.height = 0
        ax_component_mock.get_rect_intersection.return_value = empty_intersection
        ax_component_mock.is_empty_rect.side_effect = lambda rect: rect.width == 0

        test_context.patch_object(
            AXEventSynthesizer, "_is_scrolled_off_screen", side_effect=lambda obj, offset: False
        )

        result = AXEventSynthesizer._mouse_event_on_character(mock_obj, 10, "abs")
        assert result is False
        essential_modules["orca.debug"].print_tokens.assert_called()

    @pytest.mark.parametrize(
        "method_name,args,position_changes,expected_text_method,expected_object_method",
        [
            pytest.param(
                "_scroll_to_location",
                ("Atspi.ScrollType.ANYWHERE", 5, 10),
                True,
                "scroll_substring_to_location",
                "scroll_object_to_location",
                id="location_success",
            ),
            pytest.param(
                "_scroll_to_location",
                ("Atspi.ScrollType.BOTTOM_EDGE", 15, 20),
                False,
                "scroll_substring_to_location",
                "scroll_object_to_location",
                id="location_fallback",
            ),
            pytest.param(
                "_scroll_to_point",
                (300, 400, 25, 30),
                False,
                "scroll_substring_to_point",
                "scroll_object_to_point",
                id="point_fallback",
            ),
        ],
    )
    def test_scroll_methods_with_fallback(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
        self,
        test_context: OrcaTestContext,
        method_name,
        args,
        position_changes,
        expected_text_method,
        expected_object_method,
    ) -> None:
        """Test scroll methods with success and fallback scenarios."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.ax_event_synthesizer import AXEventSynthesizer

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        ax_component_mock = essential_modules["orca.ax_component"].AXComponent
        ax_text_mock = essential_modules["orca.ax_text"].AXText
        ax_object_mock = essential_modules["orca.ax_object"].AXObject

        if position_changes:
            initial_pos = test_context.Mock()
            initial_pos.x, initial_pos.y = 100, 100
            changed_pos = test_context.Mock()
            changed_pos.x, changed_pos.y = 150, 120
            position_call_count = 0

            def mock_get_position(_obj):
                nonlocal position_call_count
                position_call_count += 1
                return initial_pos if position_call_count == 1 else changed_pos

            ax_component_mock.get_position.side_effect = mock_get_position
        else:
            same_pos = test_context.Mock()
            if "location" in method_name:
                same_pos.x, same_pos.y = 100, 100
            else:
                same_pos.x, same_pos.y = 75, 125
            ax_component_mock.get_position.return_value = same_pos

        final_args = []
        for arg in args:
            if isinstance(arg, str) and "Atspi.ScrollType" in arg:
                scroll_type = getattr(Atspi.ScrollType, arg.split(".")[-1])
                final_args.append(scroll_type)
            else:
                final_args.append(arg)

        method = getattr(AXEventSynthesizer, method_name)
        method(mock_obj, *final_args)

        text_method = getattr(ax_text_mock, expected_text_method)
        text_method.assert_called_once_with(mock_obj, *final_args)

        object_method = getattr(ax_component_mock, expected_object_method)
        if position_changes:
            object_method.assert_not_called()
            assert ax_object_mock.clear_cache.call_count == 1
            assert essential_modules["orca.debug"].print_tokens.call_count == 1
        else:
            if "location" in method_name:
                object_method.assert_called_once_with(mock_obj, final_args[0])
            else:
                object_method.assert_called_once_with(mock_obj, final_args[0], final_args[1])
            assert ax_object_mock.clear_cache.call_count == 2
            assert essential_modules["orca.debug"].print_tokens.call_count == 2

    def test_is_scrolled_off_screen_returns_false_when_no_ancestor_found(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test _is_scrolled_off_screen returns False when no ancestor is found."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.ax_event_synthesizer import AXEventSynthesizer

        mock_obj = test_context.Mock(spec=Atspi.Accessible)

        ax_component_mock = essential_modules["orca.ax_component"].AXComponent
        rect = test_context.Mock()
        rect.x, rect.y, rect.width, rect.height = 50, 50, 100, 100
        ax_component_mock.get_rect.return_value = rect

        ax_object_mock = essential_modules["orca.ax_object"].AXObject
        ax_object_mock.find_ancestor.return_value = None

        result = AXEventSynthesizer._is_scrolled_off_screen(mock_obj, 5)
        assert result is False
        essential_modules["orca.debug"].print_tokens.assert_called()

    def test_is_scrolled_off_screen_returns_true_when_object_outside_ancestor(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test _is_scrolled_off_screen returns True when object is outside ancestor bounds."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.ax_event_synthesizer import AXEventSynthesizer

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_ancestor = test_context.Mock(spec=Atspi.Accessible)

        ax_component_mock = essential_modules["orca.ax_component"].AXComponent
        obj_rect = test_context.Mock()
        obj_rect.x, obj_rect.y, obj_rect.width, obj_rect.height = 200, 200, 50, 50
        ancestor_rect = test_context.Mock()
        ancestor_rect.x, ancestor_rect.y, ancestor_rect.width, ancestor_rect.height = (
            100,
            100,
            50,
            50,
        )
        empty_intersection = test_context.Mock()
        empty_intersection.width = empty_intersection.height = 0

        ax_component_mock.get_rect.side_effect = [obj_rect, ancestor_rect]
        ax_component_mock.get_rect_intersection.return_value = empty_intersection
        ax_component_mock.is_empty_rect.return_value = True

        ax_object_mock = essential_modules["orca.ax_object"].AXObject
        ax_object_mock.find_ancestor.return_value = mock_ancestor

        result = AXEventSynthesizer._is_scrolled_off_screen(mock_obj, 10)
        assert result is True
        essential_modules["orca.debug"].print_tokens.assert_called()

    def test_is_scrolled_off_screen_returns_false_when_no_offset(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test _is_scrolled_off_screen returns False when offset is None and object in bounds."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.ax_event_synthesizer import AXEventSynthesizer

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_ancestor = test_context.Mock(spec=Atspi.Accessible)

        ax_component_mock = essential_modules["orca.ax_component"].AXComponent
        obj_rect = test_context.Mock()
        ancestor_rect = test_context.Mock()
        intersection = test_context.Mock()
        intersection.width = intersection.height = 50

        ax_component_mock.get_rect.side_effect = [obj_rect, ancestor_rect]
        ax_component_mock.get_rect_intersection.return_value = intersection
        ax_component_mock.is_empty_rect.return_value = False

        ax_object_mock = essential_modules["orca.ax_object"].AXObject
        ax_object_mock.find_ancestor.return_value = mock_ancestor

        result = AXEventSynthesizer._is_scrolled_off_screen(mock_obj, None)
        assert result is False
        essential_modules["orca.debug"].print_tokens.assert_called()

    def test_is_scrolled_off_screen_returns_false_when_empty_character_rect(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test _is_scrolled_off_screen returns False when character rect is empty."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.ax_event_synthesizer import AXEventSynthesizer

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_ancestor = test_context.Mock(spec=Atspi.Accessible)

        ax_component_mock = essential_modules["orca.ax_component"].AXComponent
        obj_rect = test_context.Mock()
        ancestor_rect = test_context.Mock()
        intersection = test_context.Mock()
        intersection.width = intersection.height = 50
        empty_char_rect = test_context.Mock()
        empty_char_rect.width = empty_char_rect.height = 0

        ax_component_mock.get_rect.side_effect = [obj_rect, ancestor_rect]
        ax_component_mock.get_rect_intersection.return_value = intersection
        ax_component_mock.is_empty_rect.side_effect = [False, True]

        ax_text_mock = essential_modules["orca.ax_text"].AXText
        ax_text_mock.get_character_rect.return_value = empty_char_rect

        ax_object_mock = essential_modules["orca.ax_object"].AXObject
        ax_object_mock.find_ancestor.return_value = mock_ancestor

        result = AXEventSynthesizer._is_scrolled_off_screen(mock_obj, 8)
        assert result is False
        essential_modules["orca.debug"].print_tokens.assert_called()

    def test_mouse_event_on_object_grabs_focus_when_still_offscreen(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test _mouse_event_on_object grabs focus when object remains offscreen after scroll."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.ax_event_synthesizer import AXEventSynthesizer

        mock_obj = test_context.Mock(spec=Atspi.Accessible)

        scroll_call_count = 0

        def mock_scroll_into_view(_obj):
            nonlocal scroll_call_count
            scroll_call_count += 1

        test_context.patch_object(
            AXEventSynthesizer, "scroll_into_view", new=mock_scroll_into_view
        )
        test_context.patch_object(
            AXEventSynthesizer, "_is_scrolled_off_screen", side_effect=lambda obj, offset=None: True
        )
        test_context.patch_object(
            AXEventSynthesizer, "_generate_mouse_event", side_effect=lambda obj, x, y, event: True
        )

        rect = test_context.Mock()
        rect.width = rect.height = 100
        ax_component_mock = essential_modules["orca.ax_component"].AXComponent
        ax_component_mock.get_rect.return_value = rect

        ax_object_mock = essential_modules["orca.ax_object"].AXObject

        result = AXEventSynthesizer._mouse_event_on_object(mock_obj, "click")
        assert result is True
        assert scroll_call_count == 1
        ax_object_mock.grab_focus.assert_called_once_with(mock_obj)
        essential_modules["orca.debug"].print_tokens.assert_called()
