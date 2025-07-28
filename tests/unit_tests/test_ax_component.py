# Unit tests for ax_component.py component-related methods.
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

# pylint: disable=too-many-public-methods
# pylint: disable=wrong-import-position
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=unused-argument
# pylint: disable=import-outside-toplevel
# pylint: disable=too-many-locals
# pylint: disable=wrong-import-order

"""Unit tests for ax_component.py component-related methods."""

from unittest.mock import Mock

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi
from gi.repository import GLib

from .conftest import clean_module_cache


@pytest.mark.unit
class TestAXComponent:
    """Test component-related methods."""

    @pytest.fixture
    def mock_accessible(self):
        """Create a mock Atspi.Accessible object."""
        return Mock(spec=Atspi.Accessible)

    @pytest.fixture
    def mock_rect(self):
        """Create a mock Atspi.Rect with default values."""
        rect = Atspi.Rect()
        rect.x = 10
        rect.y = 20
        rect.width = 100
        rect.height = 50
        return rect

    @pytest.mark.parametrize(
        "supports_component, position_result, expected_x, expected_y",
        [
            pytest.param(False, None, -1, -1, id="no_component_support"),
            pytest.param(True, Mock(x=25, y=35), 25, 35, id="valid_position"),
        ],
    )
    def test_get_position(
        self,
        mock_accessible,
        monkeypatch,
        supports_component,
        position_result,
        expected_x,
        expected_y,
        mock_orca_dependencies,
    ):
        """Test AXComponent.get_position."""

        monkeypatch.setattr(
            mock_orca_dependencies.ax_object, "supports_component", lambda obj: supports_component
        )

        clean_module_cache("orca.ax_component")
        from orca.ax_component import AXComponent

        if supports_component and position_result:
            monkeypatch.setattr(
                Atspi.Component, "get_position", lambda obj, coord_type: position_result
            )
        else:
            # Mock the method to avoid TypeError when called with Mock object
            monkeypatch.setattr(
                Atspi.Component, "get_position", lambda obj, coord_type: Mock(x=-1, y=-1)
            )

        result = AXComponent.get_position(mock_accessible)
        assert result == (expected_x, expected_y)

    def test_get_position_glib_error(self, mock_accessible, monkeypatch, mock_orca_dependencies):
        """Test AXComponent.get_position handles GLib.GError exceptions."""

        monkeypatch.setattr(
            mock_orca_dependencies["ax_object"], "supports_component", lambda obj: True
        )

        clean_module_cache("orca.ax_component")
        from orca.ax_component import AXComponent

        def raise_glib_error(obj, coord_type):
            raise GLib.GError("Component error")

        monkeypatch.setattr(Atspi.Component, "get_position", raise_glib_error)
        result = AXComponent.get_position(mock_accessible)
        assert result == (-1, -1)

    @pytest.mark.parametrize(
        "supports_component, size_result, expected_width, expected_height",
        [
            pytest.param(False, None, -1, -1, id="no_component_support"),
            pytest.param(True, Mock(x=150, y=75), 150, 75, id="valid_size"),
        ],
    )
    def test_get_size(
        self,
        mock_accessible,
        monkeypatch,
        supports_component,
        size_result,
        expected_width,
        expected_height,
        mock_orca_dependencies,
    ):
        """Test AXComponent.get_size."""

        monkeypatch.setattr(
            mock_orca_dependencies.ax_object, "supports_component", lambda obj: supports_component
        )

        clean_module_cache("orca.ax_component")
        from orca.ax_component import AXComponent

        if supports_component and size_result:
            monkeypatch.setattr(Atspi.Component, "get_size", lambda obj, coord_type: size_result)
        else:
            # Mock the method to avoid TypeError when called with Mock object
            monkeypatch.setattr(
                Atspi.Component, "get_size", lambda obj, coord_type: Mock(x=-1, y=-1)
            )

        result = AXComponent.get_size(mock_accessible)
        assert result == (expected_width, expected_height)

    def test_get_size_glib_error(self, mock_accessible, monkeypatch, mock_orca_dependencies):
        """Test AXComponent.get_size handles GLib.GError exceptions."""

        monkeypatch.setattr(
            mock_orca_dependencies["ax_object"], "supports_component", lambda obj: True
        )

        clean_module_cache("orca.ax_component")
        from orca.ax_component import AXComponent

        def raise_glib_error(obj, coord_type):
            raise GLib.GError("Size error")

        monkeypatch.setattr(Atspi.Component, "get_size", raise_glib_error)
        result = AXComponent.get_size(mock_accessible)
        assert result == (-1, -1)

    @pytest.mark.parametrize(
        "supports_component",
        [
            pytest.param(False, id="no_component_support"),
            pytest.param(True, id="valid_rect"),
        ],
    )
    def test_get_rect(
        self, mock_accessible, mock_rect, monkeypatch, supports_component, mock_orca_dependencies
    ):
        """Test AXComponent.get_rect."""

        # Create a mock AXObject class with required methods
        mock_ax_object_class = Mock()
        mock_ax_object_class.supports_component = Mock(return_value=supports_component)
        mock_orca_dependencies["ax_object"].AXObject = mock_ax_object_class

        clean_module_cache("orca.ax_component")
        from orca.ax_component import AXComponent

        if supports_component:
            monkeypatch.setattr(Atspi.Component, "get_extents", lambda obj, coord_type: mock_rect)
        else:
            # Create a properly configured mock for the non-component case
            def mock_get_extents(obj, coord_type):
                # This should not be called for unsupported components, but provide fallback
                return None

            monkeypatch.setattr(Atspi.Component, "get_extents", mock_get_extents)

        result = AXComponent.get_rect(mock_accessible)

        if supports_component:
            assert result == mock_rect
        else:
            assert isinstance(result, Atspi.Rect)
            assert result.x == result.y == result.width == result.height == 0

    def test_get_rect_glib_error(self, mock_accessible, monkeypatch, mock_orca_dependencies):
        """Test AXComponent.get_rect handles GLib.GError exceptions."""

        monkeypatch.setattr(
            mock_orca_dependencies["ax_object"], "supports_component", lambda obj: True
        )

        clean_module_cache("orca.ax_component")
        from orca.ax_component import AXComponent

        def raise_glib_error(obj, coord_type):
            raise GLib.GError("Extents error")

        monkeypatch.setattr(Atspi.Component, "get_extents", raise_glib_error)
        result = AXComponent.get_rect(mock_accessible)

        assert isinstance(result, Atspi.Rect)
        assert result.x == result.y == result.width == result.height == 0

    def test_get_center_point(self, mock_accessible, monkeypatch, mock_orca_dependencies):
        """Test AXComponent.get_center_point."""

        clean_module_cache("orca.ax_component")
        from orca.ax_component import AXComponent

        mock_rect = Atspi.Rect()
        mock_rect.x = 10
        mock_rect.y = 20
        mock_rect.width = 100
        mock_rect.height = 60

        monkeypatch.setattr(AXComponent, "get_rect", lambda obj: mock_rect)
        result = AXComponent.get_center_point(mock_accessible)

        assert result == (60.0, 50.0)

    @pytest.mark.parametrize(
        "width, height, expected_result",
        [
            pytest.param(0, 0, True, id="zero_width_and_height"),
            pytest.param(100, 0, False, id="zero_height_only"),
            pytest.param(0, 50, False, id="zero_width_only"),
            pytest.param(100, 50, False, id="non_zero_dimensions"),
        ],
    )
    def test_has_no_size(
        self, mock_accessible, monkeypatch, width, height, expected_result, mock_orca_dependencies
    ):
        """Test AXComponent.has_no_size."""

        clean_module_cache("orca.ax_component")
        from orca.ax_component import AXComponent

        mock_rect = Atspi.Rect()
        mock_rect.width = width
        mock_rect.height = height

        monkeypatch.setattr(AXComponent, "get_rect", lambda obj: mock_rect)
        result = AXComponent.has_no_size(mock_accessible)
        assert result is expected_result

    @pytest.mark.parametrize(
        "x, y, width, height, expected_result",
        [
            pytest.param(0, 0, 0, 0, True, id="all_zero_dimensions"),
            pytest.param(10, 20, 0, 0, True, id="zero_size_non_zero_position"),
            pytest.param(-1, -1, -1, -1, True, id="all_negative_one"),
            pytest.param(10, 20, 100, 50, False, id="valid_dimensions"),
            pytest.param(10, 20, -2, 50, True, id="invalid_negative_width"),
            pytest.param(10, 20, 100, -5, True, id="invalid_negative_height"),
        ],
    )
    def test_has_no_size_or_invalid_rect(
        self,
        mock_accessible,
        monkeypatch,
        x,
        y,
        width,
        height,
        expected_result,
        mock_orca_dependencies,
    ):
        """Test AXComponent.has_no_size_or_invalid_rect."""

        clean_module_cache("orca.ax_component")
        from orca.ax_component import AXComponent

        mock_rect = Atspi.Rect()
        mock_rect.x = x
        mock_rect.y = y
        mock_rect.width = width
        mock_rect.height = height

        monkeypatch.setattr(mock_orca_dependencies["ax_object"], "clear_cache", lambda obj: None)
        monkeypatch.setattr(AXComponent, "get_rect", lambda obj: mock_rect)

        result = AXComponent.has_no_size_or_invalid_rect(mock_accessible)
        assert result is expected_result

    @pytest.mark.parametrize(
        "x, y, width, height, expected_result",
        [
            pytest.param(0, 0, 0, 0, True, id="all_zeros"),
            pytest.param(0, 0, 100, 50, False, id="zero_position_valid_size"),
            pytest.param(10, 20, 0, 0, False, id="valid_position_zero_size"),
            pytest.param(10, 20, 100, 50, False, id="all_non_zero"),
        ],
    )
    def test_is_empty_rect(
        self, monkeypatch, x, y, width, height, expected_result, mock_orca_dependencies
    ):
        """Test AXComponent.is_empty_rect."""

        clean_module_cache("orca.ax_component")
        from orca.ax_component import AXComponent

        rect = Atspi.Rect()
        rect.x = x
        rect.y = y
        rect.width = width
        rect.height = height

        result = AXComponent.is_empty_rect(rect)
        assert result is expected_result

    def test_is_same_rect(self, monkeypatch, mock_orca_dependencies):
        """Test AXComponent.is_same_rect."""

        clean_module_cache("orca.ax_component")
        from orca.ax_component import AXComponent

        rect1 = Atspi.Rect()
        rect1.x = 10
        rect1.y = 20
        rect1.width = 100
        rect1.height = 50

        # Scenario: Identical rectangles
        rect2 = Atspi.Rect()
        rect2.x = 10
        rect2.y = 20
        rect2.width = 100
        rect2.height = 50
        assert AXComponent.is_same_rect(rect1, rect2) is True

        # Scenario: Different x coordinate
        rect2.x = 15
        assert AXComponent.is_same_rect(rect1, rect2) is False

        # Scenario: Different width
        rect2.x = 10  # Reset
        rect2.width = 200
        assert AXComponent.is_same_rect(rect1, rect2) is False

    def test_get_rect_intersection(self, monkeypatch, mock_orca_dependencies):
        """Test AXComponent.get_rect_intersection."""

        clean_module_cache("orca.ax_component")
        from orca.ax_component import AXComponent

        rect1 = Atspi.Rect()
        rect1.x = 10
        rect1.y = 20
        rect1.width = 100
        rect1.height = 50

        rect2 = Atspi.Rect()
        rect2.x = 50
        rect2.y = 30
        rect2.width = 80
        rect2.height = 60

        result = AXComponent.get_rect_intersection(rect1, rect2)

        assert result.x == 50
        assert result.y == 30
        assert result.width == 60
        assert result.height == 40

    def test_get_rect_intersection_no_overlap(self, monkeypatch, mock_orca_dependencies):
        """Test AXComponent.get_rect_intersection when rectangles don't overlap."""

        clean_module_cache("orca.ax_component")
        from orca.ax_component import AXComponent

        rect1 = Atspi.Rect()
        rect1.x = 10
        rect1.y = 20
        rect1.width = 50
        rect1.height = 30

        rect2 = Atspi.Rect()
        rect2.x = 100
        rect2.y = 200
        rect2.width = 50
        rect2.height = 30

        result = AXComponent.get_rect_intersection(rect1, rect2)

        assert result.x == result.y == result.width == result.height == 0

    def test_get_rect_intersection_huge_rect(self, monkeypatch, mock_orca_dependencies):
        """Test AXComponent.get_rect_intersection with extremely large rectangle."""

        clean_module_cache("orca.ax_component")
        from orca.ax_component import AXComponent

        rect1 = Atspi.Rect()
        rect1.x = 100
        rect1.y = 100
        rect1.width = 200
        rect1.height = 150

        rect2 = Atspi.Rect()
        rect2.x = 50
        rect2.y = 50
        rect2.width = 2147483647
        rect2.height = 2147483647

        result = AXComponent.get_rect_intersection(rect1, rect2)

        assert result.x == 100
        assert result.y == 100
        assert result.width == 200
        assert result.height == 150

    @pytest.mark.parametrize(
        "supports_component, is_bogus, contains_result, expected_result",
        [
            pytest.param(False, False, None, False, id="no_component_support"),
            pytest.param(True, True, None, False, id="bogus_object"),
            pytest.param(True, False, True, True, id="point_contained"),
            pytest.param(True, False, False, False, id="point_not_contained"),
        ],
    )
    def test_object_contains_point(
        self,
        mock_accessible,
        monkeypatch,
        supports_component,
        is_bogus,
        contains_result,
        expected_result,
        mock_orca_dependencies,
    ):
        """Test AXComponent.object_contains_point."""

        # Configure mock classes BEFORE importing the module
        mock_ax_object_class = Mock()
        mock_ax_object_class.supports_component = Mock(return_value=supports_component)
        mock_ax_object_class.is_bogus = Mock(return_value=is_bogus)
        mock_orca_dependencies["ax_object"].AXObject = mock_ax_object_class

        monkeypatch.setattr(mock_orca_dependencies["debug"], "print_tokens", Mock())

        clean_module_cache("orca.ax_component")
        from orca.ax_component import AXComponent

        # Always provide a mock for contains, regardless of conditions
        def contains_func(obj, x, y, coord_type):
            if supports_component and not is_bogus and contains_result is not None:
                return contains_result
            return False

        monkeypatch.setattr(Atspi.Component, "contains", contains_func)

        result = AXComponent.object_contains_point(mock_accessible, 50, 75)
        assert result is expected_result

    def test_object_contains_point_glib_error(
        self, mock_accessible, monkeypatch, mock_orca_dependencies
    ):
        """Test AXComponent.object_contains_point handles GLib.GError exceptions."""

        clean_module_cache("orca.ax_component")
        from orca.ax_component import AXComponent

        monkeypatch.setattr(
            mock_orca_dependencies["ax_object"], "supports_component", lambda obj: True
        )
        monkeypatch.setattr(mock_orca_dependencies["ax_object"], "is_bogus", lambda obj: False)

        def raise_glib_error(obj, x, y, coord_type):
            raise GLib.GError("Contains error")

        monkeypatch.setattr(Atspi.Component, "contains", raise_glib_error)
        result = AXComponent.object_contains_point(mock_accessible, 50, 75)
        assert result is False

    def test_object_intersects_rect_with_intersection(
        self, mock_accessible, monkeypatch, mock_orca_dependencies
    ):
        """Test AXComponent.object_intersects_rect when rectangles intersect."""

        clean_module_cache("orca.ax_component")
        from orca.ax_component import AXComponent

        obj_rect = Atspi.Rect()
        obj_rect.x = 10
        obj_rect.y = 20
        obj_rect.width = 100
        obj_rect.height = 50

        test_rect = Atspi.Rect()
        test_rect.x = 50
        test_rect.y = 30
        test_rect.width = 80
        test_rect.height = 60

        monkeypatch.setattr(AXComponent, "get_rect", lambda obj: obj_rect)

        result = AXComponent.object_intersects_rect(mock_accessible, test_rect)
        assert result is True

    def test_object_intersects_rect_no_intersection(
        self, mock_accessible, monkeypatch, mock_orca_dependencies
    ):
        """Test AXComponent.object_intersects_rect when rectangles don't intersect."""

        clean_module_cache("orca.ax_component")
        from orca.ax_component import AXComponent

        obj_rect = Atspi.Rect()
        obj_rect.x = 10
        obj_rect.y = 20
        obj_rect.width = 50
        obj_rect.height = 30

        test_rect = Atspi.Rect()
        test_rect.x = 100
        test_rect.y = 200
        test_rect.width = 50
        test_rect.height = 30

        monkeypatch.setattr(AXComponent, "get_rect", lambda obj: obj_rect)

        result = AXComponent.object_intersects_rect(mock_accessible, test_rect)
        assert result is False

    @pytest.mark.parametrize(
        "x, y, width, height, child_count, is_menu, expected_result",
        [
            pytest.param(15000, 20, 100, 50, 0, False, True, id="extreme_x_position"),
            pytest.param(20, 15000, 100, 50, 0, False, True, id="extreme_y_position"),
            pytest.param(20, 30, 0, 0, 0, False, True, id="zero_size_no_children"),
            pytest.param(20, 30, 0, 0, 2, False, False, id="zero_size_has_children"),
            pytest.param(20, 30, 0, 0, 0, True, True, id="zero_size_menu_role"),
            pytest.param(-50, -60, 40, 30, 0, False, True, id="completely_offscreen"),
            pytest.param(20, 30, 100, 50, 0, False, False, id="normal_onscreen_object"),
        ],
    )
    def test_object_is_off_screen(
        self,
        mock_accessible,
        monkeypatch,
        x,
        y,
        width,
        height,
        child_count,
        is_menu,
        expected_result,
        mock_orca_dependencies,
    ):
        """Test AXComponent.object_is_off_screen."""

        # Configure mock classes BEFORE importing the module
        mock_ax_object_class = Mock()
        mock_ax_object_class.get_child_count = Mock(return_value=child_count)
        mock_orca_dependencies["ax_object"].AXObject = mock_ax_object_class

        mock_utilities_role_class = Mock()
        mock_utilities_role_class.is_menu = Mock(return_value=is_menu)
        mock_orca_dependencies["ax_utilities_role"].AXUtilitiesRole = mock_utilities_role_class

        monkeypatch.setattr(mock_orca_dependencies["debug"], "print_tokens", Mock())

        clean_module_cache("orca.ax_component")
        from orca.ax_component import AXComponent

        mock_rect = Atspi.Rect()
        mock_rect.x = x
        mock_rect.y = y
        mock_rect.width = width
        mock_rect.height = height

        monkeypatch.setattr(AXComponent, "get_rect", lambda obj: mock_rect)

        result = AXComponent.object_is_off_screen(mock_accessible)
        assert result is expected_result

    def test_objects_have_same_rect(self, monkeypatch, mock_orca_dependencies):
        """Test AXComponent.objects_have_same_rect."""

        clean_module_cache("orca.ax_component")
        from orca.ax_component import AXComponent

        obj1 = Mock(spec=Atspi.Accessible)
        obj2 = Mock(spec=Atspi.Accessible)

        rect1 = Atspi.Rect()
        rect1.x = 10
        rect1.y = 20
        rect1.width = 100
        rect1.height = 50

        rect2 = Atspi.Rect()
        rect2.x = 10
        rect2.y = 20
        rect2.width = 100
        rect2.height = 50

        def get_rect_for_obj(obj):
            return rect1 if obj == obj1 else rect2

        monkeypatch.setattr(AXComponent, "get_rect", get_rect_for_obj)

        # Scenario: Same rectangles
        result = AXComponent.objects_have_same_rect(obj1, obj2)
        assert result is True

        # Scenario: Different rectangles
        rect2.width = 200
        result = AXComponent.objects_have_same_rect(obj1, obj2)
        assert result is False

    def test_objects_overlap(self, monkeypatch, mock_orca_dependencies):
        """Test AXComponent.objects_overlap."""

        clean_module_cache("orca.ax_component")
        from orca.ax_component import AXComponent

        obj1 = Mock(spec=Atspi.Accessible)
        obj2 = Mock(spec=Atspi.Accessible)

        rect1 = Atspi.Rect()
        rect1.x = 10
        rect1.y = 20
        rect1.width = 100
        rect1.height = 50

        rect2 = Atspi.Rect()
        rect2.x = 50
        rect2.y = 30
        rect2.width = 80
        rect2.height = 60

        def get_rect_for_obj(obj):
            return rect1 if obj == obj1 else rect2

        monkeypatch.setattr(AXComponent, "get_rect", get_rect_for_obj)

        result = AXComponent.objects_overlap(obj1, obj2)
        assert result is True

    def test_on_same_line(self, monkeypatch, mock_orca_dependencies):
        """Test AXComponent.on_same_line."""

        clean_module_cache("orca.ax_component")
        from orca.ax_component import AXComponent

        obj1 = Mock(spec=Atspi.Accessible)
        obj2 = Mock(spec=Atspi.Accessible)

        # Scenario: Objects with similar vertical center points
        rect1 = Atspi.Rect()
        rect1.x = 10
        rect1.y = 20
        rect1.width = 50
        rect1.height = 30

        rect2 = Atspi.Rect()
        rect2.x = 100
        rect2.y = 22
        rect2.width = 60
        rect2.height = 26

        def get_rect_for_obj(obj):
            return rect1 if obj == obj1 else rect2

        monkeypatch.setattr(AXComponent, "get_rect", get_rect_for_obj)

        result = AXComponent.on_same_line(obj1, obj2)
        assert result is True

        # Scenario: Objects with very different heights (height ratio > 2.0)
        rect2.height = 200
        result = AXComponent.on_same_line(obj1, obj2)
        assert result is False

    def test_on_same_line_with_delta(self, monkeypatch, mock_orca_dependencies):
        """Test AXComponent.on_same_line with delta parameter."""

        clean_module_cache("orca.ax_component")
        from orca.ax_component import AXComponent

        obj1 = Mock(spec=Atspi.Accessible)
        obj2 = Mock(spec=Atspi.Accessible)

        rect1 = Atspi.Rect()
        rect1.x = 10
        rect1.y = 20
        rect1.width = 50
        rect1.height = 20

        rect2 = Atspi.Rect()
        rect2.x = 100
        rect2.y = 30
        rect2.width = 60
        rect2.height = 20

        def get_rect_for_obj(obj):
            return rect1 if obj == obj1 else rect2

        monkeypatch.setattr(AXComponent, "get_rect", get_rect_for_obj)

        # Scenario: Centers differ by 10, delta=5 should return False
        result = AXComponent.on_same_line(obj1, obj2, delta=5)
        assert result is False

        # Scenario: Centers differ by 10, delta=15 should return True
        result = AXComponent.on_same_line(obj1, obj2, delta=15)
        assert result is True

    @pytest.mark.parametrize(
        "supports_component, scroll_result, expected_result",
        [
            pytest.param(False, None, False, id="no_component_support"),
            pytest.param(True, True, True, id="scroll_successful"),
            pytest.param(True, False, False, id="scroll_failed"),
        ],
    )
    def test_scroll_object_to_point(
        self,
        mock_accessible,
        monkeypatch,
        supports_component,
        scroll_result,
        expected_result,
        mock_orca_dependencies,
    ):
        """Test AXComponent.scroll_object_to_point."""

        clean_module_cache("orca.ax_component")
        from orca.ax_component import AXComponent

        monkeypatch.setattr(
            mock_orca_dependencies["ax_object"],
            "supports_component",
            lambda obj: supports_component,
        )

        if supports_component and scroll_result is not None:
            monkeypatch.setattr(
                Atspi.Component, "scroll_to_point", lambda obj, coord_type, x, y: scroll_result
            )
        else:
            monkeypatch.setattr(
                Atspi.Component, "scroll_to_point", lambda obj, coord_type, x, y: False
            )

        result = AXComponent.scroll_object_to_point(mock_accessible, 100, 200)
        assert result is expected_result

    def test_scroll_object_to_point_glib_error(
        self, mock_accessible, monkeypatch, mock_orca_dependencies
    ):
        """Test AXComponent.scroll_object_to_point handles GLib.GError exceptions."""

        clean_module_cache("orca.ax_component")
        from orca.ax_component import AXComponent

        monkeypatch.setattr(
            mock_orca_dependencies["ax_object"], "supports_component", lambda obj: True
        )

        def raise_glib_error(obj, coord_type, x, y):
            raise GLib.GError("Scroll error")

        monkeypatch.setattr(Atspi.Component, "scroll_to_point", raise_glib_error)
        result = AXComponent.scroll_object_to_point(mock_accessible, 100, 200)
        assert result is False

    @pytest.mark.parametrize(
        "supports_component, scroll_result, expected_result",
        [
            pytest.param(False, None, False, id="no_component_support"),
            pytest.param(True, True, True, id="scroll_successful"),
            pytest.param(True, False, False, id="scroll_failed"),
        ],
    )
    def test_scroll_object_to_location(
        self,
        mock_accessible,
        monkeypatch,
        supports_component,
        scroll_result,
        expected_result,
        mock_orca_dependencies,
    ):
        """Test AXComponent.scroll_object_to_location."""

        clean_module_cache("orca.ax_component")
        from orca.ax_component import AXComponent

        monkeypatch.setattr(
            mock_orca_dependencies["ax_object"],
            "supports_component",
            lambda obj: supports_component,
        )

        if supports_component and scroll_result is not None:
            monkeypatch.setattr(Atspi.Component, "scroll_to", lambda obj, location: scroll_result)
        else:
            monkeypatch.setattr(Atspi.Component, "scroll_to", lambda obj, location: False)

        result = AXComponent.scroll_object_to_location(mock_accessible, Atspi.ScrollType.TOP_LEFT)
        assert result is expected_result

    def test_scroll_object_to_location_glib_error(
        self, mock_accessible, monkeypatch, mock_orca_dependencies
    ):
        """Test AXComponent.scroll_object_to_location handles GLib.GError exceptions."""

        clean_module_cache("orca.ax_component")
        from orca.ax_component import AXComponent

        monkeypatch.setattr(
            mock_orca_dependencies["ax_object"], "supports_component", lambda obj: True
        )

        def raise_glib_error(obj, location):
            raise GLib.GError("Scroll location error")

        monkeypatch.setattr(Atspi.Component, "scroll_to", raise_glib_error)
        result = AXComponent.scroll_object_to_location(mock_accessible, Atspi.ScrollType.TOP_LEFT)
        assert result is False

    def test_sort_objects_by_size(self, monkeypatch, mock_orca_dependencies):
        """Test AXComponent.sort_objects_by_size."""

        clean_module_cache("orca.ax_component")
        from orca.ax_component import AXComponent

        obj_small = Mock(spec=Atspi.Accessible)
        obj_medium = Mock(spec=Atspi.Accessible)
        obj_large = Mock(spec=Atspi.Accessible)

        # Create rectangles with different areas
        rect_small = Atspi.Rect()
        rect_small.width = 10
        rect_small.height = 10

        rect_medium = Atspi.Rect()
        rect_medium.width = 20
        rect_medium.height = 15

        rect_large = Atspi.Rect()
        rect_large.width = 30
        rect_large.height = 20

        def get_rect_for_obj(obj):
            if obj == obj_small:
                return rect_small
            if obj == obj_medium:
                return rect_medium
            return rect_large

        monkeypatch.setattr(AXComponent, "get_rect", get_rect_for_obj)

        objects = [obj_large, obj_small, obj_medium]
        result = AXComponent.sort_objects_by_size(objects)

        assert result == [obj_small, obj_medium, obj_large]

    def test_sort_objects_by_position(self, monkeypatch, mock_orca_dependencies):
        """Test AXComponent.sort_objects_by_position."""

        clean_module_cache("orca.ax_component")
        from orca.ax_component import AXComponent

        obj_top_left = Mock(spec=Atspi.Accessible)
        obj_top_right = Mock(spec=Atspi.Accessible)
        obj_bottom_left = Mock(spec=Atspi.Accessible)

        rect_top_left = Atspi.Rect()
        rect_top_left.x = 10
        rect_top_left.y = 10

        rect_top_right = Atspi.Rect()
        rect_top_right.x = 100
        rect_top_right.y = 10

        rect_bottom_left = Atspi.Rect()
        rect_bottom_left.x = 10
        rect_bottom_left.y = 100

        def get_rect_for_obj(obj):
            if obj == obj_top_left:
                return rect_top_left
            if obj == obj_top_right:
                return rect_top_right
            return rect_bottom_left

        monkeypatch.setattr(AXComponent, "get_rect", get_rect_for_obj)

        objects = [obj_bottom_left, obj_top_right, obj_top_left]
        result = AXComponent.sort_objects_by_position(objects)

        assert result == [obj_top_left, obj_top_right, obj_bottom_left]

    def test_sort_objects_by_position_same_coordinates(self, monkeypatch, mock_orca_dependencies):
        """Test AXComponent.sort_objects_by_position when objects have same coordinates."""

        # Configure mock dependencies BEFORE importing the module
        obj1 = Mock(spec=Atspi.Accessible)
        obj2 = Mock(spec=Atspi.Accessible)
        parent = Mock(spec=Atspi.Accessible)

        # Create a mock AXObject class with proper return values
        mock_ax_object_class = Mock()
        mock_ax_object_class.get_parent = Mock(return_value=parent)
        mock_ax_object_class.get_index_in_parent = Mock(
            side_effect=lambda obj: 0 if obj == obj1 else 1
        )
        mock_orca_dependencies["ax_object"].AXObject = mock_ax_object_class

        monkeypatch.setattr(mock_orca_dependencies["debug"], "print_tokens", Mock())

        clean_module_cache("orca.ax_component")
        from orca.ax_component import AXComponent

        same_rect = Atspi.Rect()
        same_rect.x = 50
        same_rect.y = 50

        monkeypatch.setattr(AXComponent, "get_rect", lambda obj: same_rect)

        objects = [obj2, obj1]
        result = AXComponent.sort_objects_by_position(objects)

        assert result == [obj1, obj2]
