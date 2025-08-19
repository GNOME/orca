# Unit tests for ax_component.py methods.
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

# pylint: disable=wrong-import-position
# pylint: disable=import-outside-toplevel
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-public-methods

"""Unit tests for ax_component.py methods."""

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
class TestAXComponent:
    """Test AXComponent class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for ax_component dependencies."""

        additional_modules = ["orca.ax_utilities_role"]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        debug_mock = essential_modules["orca.debug"]
        debug_mock.print_message = test_context.Mock()
        debug_mock.print_tokens = test_context.Mock()
        debug_mock.LEVEL_INFO = 800

        ax_object_class_mock = test_context.Mock()
        ax_object_class_mock.supports_component = test_context.Mock(return_value=True)
        ax_object_class_mock.is_bogus = test_context.Mock(return_value=False)
        ax_object_class_mock.get_child_count = test_context.Mock(return_value=0)
        ax_object_class_mock.get_parent = test_context.Mock(return_value=None)
        ax_object_class_mock.get_index_in_parent = test_context.Mock(return_value=0)
        ax_object_class_mock.clear_cache = test_context.Mock()
        essential_modules["orca.ax_object"].AXObject = ax_object_class_mock

        role_class_mock = test_context.Mock()
        role_class_mock.is_menu = test_context.Mock(return_value=False)
        essential_modules["orca.ax_utilities_role"].AXUtilitiesRole = role_class_mock

        return essential_modules

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "no_component_support",
                "supports_component": False,
                "position_result": None,
                "expected_x": -1,
                "expected_y": -1,
            },
            {
                "id": "valid_position",
                "supports_component": True,
                "position_result": "mock_position",
                "expected_x": 25,
                "expected_y": 35,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_position(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXComponent.get_position."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        test_context.patch_object(
            essential_modules["orca.ax_object"].AXObject,
            "supports_component",
            side_effect=lambda obj: case["supports_component"],
        )
        from orca.ax_component import AXComponent

        if case["supports_component"] and case["position_result"] == "mock_position":
            mock_position = test_context.Mock(x=25, y=35)
            test_context.patch_object(
                Atspi.Component, "get_position", return_value=mock_position
            )
        elif case["supports_component"] and case["position_result"]:
            test_context.patch_object(
                Atspi.Component, "get_position", return_value=case["position_result"]
            )
        else:
            mock_negative_position = test_context.Mock(x=-1, y=-1)
            test_context.patch_object(
                Atspi.Component,
                "get_position",
                return_value=mock_negative_position,
            )
        result = AXComponent.get_position(mock_accessible)
        assert result == (case["expected_x"], case["expected_y"])

    @pytest.mark.parametrize(
        "method_name, atspi_method_name, expected_result",
        [
            pytest.param("get_position", "get_position", (-1, -1), id="get_position"),
            pytest.param("get_size", "get_size", (-1, -1), id="get_size"),
            pytest.param("get_rect", "get_extents", "empty_rect", id="get_rect"),
            pytest.param("object_contains_point", "contains", False, id="object_contains_point"),
            pytest.param(
                "scroll_object_to_point", "scroll_to_point", False, id="scroll_object_to_point"
            ),
            pytest.param(
                "scroll_object_to_location", "scroll_to", False, id="scroll_object_to_location"
            ),
        ],
    )
    def test_glib_error_scenarios(
        self,
        test_context: OrcaTestContext,
        method_name: str,
        atspi_method_name: str,
        expected_result,
    ) -> None:
        """Test AXComponent methods handle GLib.GError exceptions."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        test_context.patch_object(
            essential_modules["orca.ax_object"].AXObject, "supports_component", return_value=True
        )
        from orca.ax_component import AXComponent

        def raise_glib_error(*args, **kwargs):
            raise GLib.GError(f"{method_name} error")

        test_context.patch_object(Atspi.Component, atspi_method_name, side_effect=raise_glib_error)

        method = getattr(AXComponent, method_name)
        if method_name in ["object_contains_point", "scroll_object_to_point"]:
            result = method(mock_accessible, 10, 10)
        elif method_name == "scroll_object_to_location":
            result = method(mock_accessible, Atspi.ScrollType.TOP_LEFT)
        else:
            result = method(mock_accessible)

        if expected_result == "empty_rect":
            assert isinstance(result, Atspi.Rect)
            assert result.x == result.y == result.width == result.height == 0
        else:
            assert result == expected_result

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "no_component_support",
                "supports_component": False,
                "size_result": None,
                "expected_width": -1,
                "expected_height": -1,
            },
            {
                "id": "valid_size",
                "supports_component": True,
                "size_result": "mock_size",
                "expected_width": 150,
                "expected_height": 75,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_size(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXComponent.get_size."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        test_context.patch_object(
            essential_modules["orca.ax_object"].AXObject,
            "supports_component",
            side_effect=lambda obj: case["supports_component"],
        )
        from orca.ax_component import AXComponent

        if case["supports_component"] and case["size_result"] == "mock_size":
            mock_size = test_context.Mock(x=150, y=75)
            test_context.patch_object(
                Atspi.Component, "get_size", return_value=mock_size
            )
        elif case["supports_component"] and case["size_result"]:
            test_context.patch_object(
                Atspi.Component, "get_size", return_value=case["size_result"]
            )
        else:
            mock_negative_size = test_context.Mock(x=-1, y=-1)
            test_context.patch_object(
                Atspi.Component, "get_size", return_value=mock_negative_size
            )
        result = AXComponent.get_size(mock_accessible)
        assert result == (case["expected_width"], case["expected_height"])

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "no_component_support", "supports_component": False},
            {"id": "valid_rect", "supports_component": True},
        ],
        ids=lambda case: case["id"],
    )
    def test_get_rect(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test AXComponent.get_rect."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        mock_rect = Atspi.Rect()
        mock_rect.x = 10
        mock_rect.y = 20
        mock_rect.width = 100
        mock_rect.height = 50
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)

        essential_modules["orca.ax_object"].AXObject.supports_component = test_context.Mock(
            return_value=case["supports_component"]
        )
        from orca.ax_component import AXComponent

        if case["supports_component"]:
            test_context.patch_object(
                Atspi.Component, "get_extents", return_value=mock_rect
            )
        else:

            def mock_get_extents(obj, coord_type):  # pylint: disable=unused-argument
                return Atspi.Rect()

            test_context.patch_object(Atspi.Component, "get_extents", side_effect=mock_get_extents)
        result = AXComponent.get_rect(mock_accessible)
        if case["supports_component"]:
            assert result == mock_rect
        else:
            assert isinstance(result, Atspi.Rect)
            assert result.x == result.y == result.width == result.height == 0

    def test_get_center_point(self, test_context: OrcaTestContext) -> None:
        """Test AXComponent.get_center_point."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_component import AXComponent

        mock_rect = Atspi.Rect()
        mock_rect.x = 10
        mock_rect.y = 20
        mock_rect.width = 100
        mock_rect.height = 60
        test_context.patch_object(AXComponent, "get_rect", return_value=mock_rect)
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
        self, test_context: OrcaTestContext, width: int, height: int, expected_result: bool
    ) -> None:
        """Test AXComponent.has_no_size."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_component import AXComponent

        mock_rect = Atspi.Rect()
        mock_rect.width = width
        mock_rect.height = height
        test_context.patch_object(AXComponent, "get_rect", return_value=mock_rect)
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
        test_context: OrcaTestContext,
        x: int,
        y: int,
        width: int,
        height: int,
        expected_result: bool,
    ) -> None:
        """Test AXComponent.has_no_size_or_invalid_rect."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_component import AXComponent

        mock_rect = Atspi.Rect()
        mock_rect.x = x
        mock_rect.y = y
        mock_rect.width = width
        mock_rect.height = height
        test_context.patch_object(
            essential_modules["orca.ax_object"].AXObject, "clear_cache", return_value=None
        )
        test_context.patch_object(AXComponent, "get_rect", return_value=mock_rect)
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
        self,
        test_context: OrcaTestContext,
        x: int,
        y: int,
        width: int,
        height: int,
        expected_result: bool,
    ) -> None:
        """Test AXComponent.is_empty_rect."""

        self._setup_dependencies(test_context)
        from orca.ax_component import AXComponent

        rect = Atspi.Rect()
        rect.x = x
        rect.y = y
        rect.width = width
        rect.height = height
        result = AXComponent.is_empty_rect(rect)
        assert result is expected_result

    def test_is_same_rect(self, test_context: OrcaTestContext) -> None:
        """Test AXComponent.is_same_rect."""

        self._setup_dependencies(test_context)
        from orca.ax_component import AXComponent

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
        assert AXComponent.is_same_rect(rect1, rect2) is True

        rect2.x = 15
        assert AXComponent.is_same_rect(rect1, rect2) is False

        rect2.x = 10
        rect2.width = 200
        assert AXComponent.is_same_rect(rect1, rect2) is False

    def test_get_rect_intersection(self, test_context: OrcaTestContext) -> None:
        """Test AXComponent.get_rect_intersection."""

        self._setup_dependencies(test_context)
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

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "no_overlap",
                "rect1_coords": (10, 20, 50, 30),
                "rect2_coords": (100, 200, 50, 30),
                "expected_result": (0, 0, 0, 0),
            },
            {
                "id": "huge_rect",
                "rect1_coords": (100, 100, 200, 150),
                "rect2_coords": (50, 50, 2147483647, 2147483647),
                "expected_result": (100, 100, 200, 150),
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_rect_intersection_scenarios(
        self, test_context: OrcaTestContext, case: dict
    ) -> None:
        """Test AXComponent.get_rect_intersection with different rectangle scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_component import AXComponent

        rect1 = Atspi.Rect()
        rect1.x, rect1.y, rect1.width, rect1.height = case["rect1_coords"]
        rect2 = Atspi.Rect()
        rect2.x, rect2.y, rect2.width, rect2.height = case["rect2_coords"]

        result = AXComponent.get_rect_intersection(rect1, rect2)
        expected_x, expected_y, expected_width, expected_height = case["expected_result"]

        assert result.x == expected_x
        assert result.y == expected_y
        assert result.width == expected_width
        assert result.height == expected_height

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "no_component_support",
                "supports_component": False,
                "is_bogus": False,
                "contains_result": None,
                "expected_result": False,
            },
            {
                "id": "bogus_object",
                "supports_component": True,
                "is_bogus": True,
                "contains_result": None,
                "expected_result": False,
            },
            {
                "id": "point_contained",
                "supports_component": True,
                "is_bogus": False,
                "contains_result": True,
                "expected_result": True,
            },
            {
                "id": "point_not_contained",
                "supports_component": True,
                "is_bogus": False,
                "contains_result": False,
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_object_contains_point(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXComponent.object_contains_point."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)

        essential_modules["orca.ax_object"].AXObject.supports_component = test_context.Mock(
            return_value=case["supports_component"]
        )
        essential_modules["orca.ax_object"].AXObject.is_bogus = test_context.Mock(
            return_value=case["is_bogus"]
        )
        from orca.ax_component import AXComponent

        def contains_func(obj, x, y, coord_type):  # pylint: disable=unused-argument
            if (
                case["supports_component"]
                and not case["is_bogus"]
                and case["contains_result"] is not None
            ):
                return case["contains_result"]
            return False

        test_context.patch_object(Atspi.Component, "contains", side_effect=contains_func)
        result = AXComponent.object_contains_point(mock_accessible, 50, 75)
        assert result is case["expected_result"]

    @pytest.mark.parametrize(
        "obj_coords,test_coords,expected_result",
        [
            pytest.param((10, 20, 100, 50), (50, 30, 80, 60), True, id="with_intersection"),
            pytest.param((10, 20, 50, 30), (100, 200, 50, 30), False, id="no_intersection"),
        ],
    )
    def test_object_intersects_rect(
        self, test_context: OrcaTestContext, obj_coords, test_coords, expected_result
    ) -> None:
        """Test AXComponent.object_intersects_rect intersection scenarios."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_component import AXComponent

        obj_rect = Atspi.Rect()
        obj_rect.x, obj_rect.y, obj_rect.width, obj_rect.height = obj_coords
        test_rect = Atspi.Rect()
        test_rect.x, test_rect.y, test_rect.width, test_rect.height = test_coords

        test_context.patch_object(AXComponent, "get_rect", return_value=obj_rect)
        result = AXComponent.object_intersects_rect(mock_accessible, test_rect)
        assert result is expected_result

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
        test_context: OrcaTestContext,
        x: int,
        y: int,
        width: int,
        height: int,
        child_count: int,
        is_menu: bool,
        expected_result: bool,
    ) -> None:
        """Test AXComponent.object_is_off_screen."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)

        essential_modules["orca.ax_object"].AXObject.get_child_count = test_context.Mock(
            return_value=child_count
        )
        essential_modules["orca.ax_utilities_role"].AXUtilitiesRole.is_menu = test_context.Mock(
            return_value=is_menu
        )
        from orca.ax_component import AXComponent

        mock_rect = Atspi.Rect()
        mock_rect.x = x
        mock_rect.y = y
        mock_rect.width = width
        mock_rect.height = height
        test_context.patch_object(AXComponent, "get_rect", return_value=mock_rect)
        result = AXComponent.object_is_off_screen(mock_accessible)
        assert result is expected_result

    def test_objects_have_same_rect(self, test_context: OrcaTestContext) -> None:
        """Test AXComponent.objects_have_same_rect."""

        self._setup_dependencies(test_context)
        from orca.ax_component import AXComponent

        obj1 = test_context.Mock(spec=Atspi.Accessible)
        obj2 = test_context.Mock(spec=Atspi.Accessible)
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

        test_context.patch_object(AXComponent, "get_rect", side_effect=get_rect_for_obj)

        result = AXComponent.objects_have_same_rect(obj1, obj2)
        assert result is True

        rect2.width = 200
        result = AXComponent.objects_have_same_rect(obj1, obj2)
        assert result is False

    def test_objects_overlap(self, test_context: OrcaTestContext) -> None:
        """Test AXComponent.objects_overlap."""

        self._setup_dependencies(test_context)
        from orca.ax_component import AXComponent

        obj1 = test_context.Mock(spec=Atspi.Accessible)
        obj2 = test_context.Mock(spec=Atspi.Accessible)
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

        test_context.patch_object(AXComponent, "get_rect", side_effect=get_rect_for_obj)
        result = AXComponent.objects_overlap(obj1, obj2)
        assert result is True

    def test_on_same_line(self, test_context: OrcaTestContext) -> None:
        """Test AXComponent.on_same_line."""

        self._setup_dependencies(test_context)
        from orca.ax_component import AXComponent

        obj1 = test_context.Mock(spec=Atspi.Accessible)
        obj2 = test_context.Mock(spec=Atspi.Accessible)

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

        test_context.patch_object(AXComponent, "get_rect", side_effect=get_rect_for_obj)
        result = AXComponent.on_same_line(obj1, obj2)
        assert result is True

        rect2.height = 200
        result = AXComponent.on_same_line(obj1, obj2)
        assert result is False

    def test_on_same_line_with_delta(self, test_context: OrcaTestContext) -> None:
        """Test AXComponent.on_same_line with delta parameter."""

        self._setup_dependencies(test_context)
        from orca.ax_component import AXComponent

        obj1 = test_context.Mock(spec=Atspi.Accessible)
        obj2 = test_context.Mock(spec=Atspi.Accessible)
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

        test_context.patch_object(AXComponent, "get_rect", side_effect=get_rect_for_obj)

        result = AXComponent.on_same_line(obj1, obj2, delta=5)
        assert result is False

        result = AXComponent.on_same_line(obj1, obj2, delta=15)
        assert result is True

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "no_component_support",
                "supports_component": False,
                "scroll_result": None,
                "expected_result": False,
            },
            {
                "id": "scroll_successful",
                "supports_component": True,
                "scroll_result": True,
                "expected_result": True,
            },
            {
                "id": "scroll_failed",
                "supports_component": True,
                "scroll_result": False,
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_scroll_object_to_point(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXComponent.scroll_object_to_point."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_component import AXComponent

        test_context.patch_object(
            essential_modules["orca.ax_object"].AXObject,
            "supports_component",
            side_effect=lambda obj: case["supports_component"],
        )
        if case["supports_component"] and case["scroll_result"] is not None:
            test_context.patch_object(
                Atspi.Component,
                "scroll_to_point",
                return_value=case["scroll_result"],
            )
        else:
            test_context.patch_object(
                Atspi.Component, "scroll_to_point", return_value=False
            )
        result = AXComponent.scroll_object_to_point(mock_accessible, 100, 200)
        assert result is case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "no_component_support",
                "supports_component": False,
                "scroll_result": None,
                "expected_result": False,
            },
            {
                "id": "scroll_successful",
                "supports_component": True,
                "scroll_result": True,
                "expected_result": True,
            },
            {
                "id": "scroll_failed",
                "supports_component": True,
                "scroll_result": False,
                "expected_result": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_scroll_object_to_location(
        self,
        test_context: OrcaTestContext,
        case: dict,
    ) -> None:
        """Test AXComponent.scroll_object_to_location."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)
        from orca.ax_component import AXComponent

        test_context.patch_object(
            essential_modules["orca.ax_object"].AXObject,
            "supports_component",
            side_effect=lambda obj: case["supports_component"],
        )
        if case["supports_component"] and case["scroll_result"] is not None:
            test_context.patch_object(
                Atspi.Component, "scroll_to", return_value=case["scroll_result"]
            )
        else:
            test_context.patch_object(
                Atspi.Component, "scroll_to", return_value=False
            )
        result = AXComponent.scroll_object_to_location(mock_accessible, Atspi.ScrollType.TOP_LEFT)
        assert result is case["expected_result"]

    def test_sort_objects_by_size(self, test_context: OrcaTestContext) -> None:
        """Test AXComponent.sort_objects_by_size."""

        self._setup_dependencies(test_context)
        from orca.ax_component import AXComponent

        obj_small = test_context.Mock(spec=Atspi.Accessible)
        obj_medium = test_context.Mock(spec=Atspi.Accessible)
        obj_large = test_context.Mock(spec=Atspi.Accessible)

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

        test_context.patch_object(AXComponent, "get_rect", side_effect=get_rect_for_obj)
        objects = [obj_large, obj_small, obj_medium]
        result = AXComponent.sort_objects_by_size(objects)
        assert result == [obj_small, obj_medium, obj_large]

    def test_sort_objects_by_position(self, test_context: OrcaTestContext) -> None:
        """Test AXComponent.sort_objects_by_position."""

        self._setup_dependencies(test_context)
        from orca.ax_component import AXComponent

        obj_top_left = test_context.Mock(spec=Atspi.Accessible)
        obj_top_right = test_context.Mock(spec=Atspi.Accessible)
        obj_bottom_left = test_context.Mock(spec=Atspi.Accessible)
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

        test_context.patch_object(AXComponent, "get_rect", side_effect=get_rect_for_obj)
        objects = [obj_bottom_left, obj_top_right, obj_top_left]
        result = AXComponent.sort_objects_by_position(objects)
        assert result == [obj_top_left, obj_top_right, obj_bottom_left]

    def test_sort_objects_by_position_same_coordinates(self, test_context: OrcaTestContext) -> None:
        """Test AXComponent.sort_objects_by_position when objects have same coordinates."""

        essential_modules: dict[str, MagicMock] = self._setup_dependencies(test_context)

        obj1 = test_context.Mock(spec=Atspi.Accessible)
        obj2 = test_context.Mock(spec=Atspi.Accessible)
        parent = test_context.Mock(spec=Atspi.Accessible)

        essential_modules["orca.ax_object"].AXObject.get_parent = test_context.Mock(
            return_value=parent
        )
        essential_modules["orca.ax_object"].AXObject.get_index_in_parent = test_context.Mock(
            side_effect=lambda obj: 0 if obj == obj1 else 1
        )
        from orca.ax_component import AXComponent

        same_rect = Atspi.Rect()
        same_rect.x = 50
        same_rect.y = 50
        test_context.patch_object(AXComponent, "get_rect", return_value=same_rect)
        objects = [obj2, obj1]
        result = AXComponent.sort_objects_by_position(objects)
        assert result == [obj1, obj2]
