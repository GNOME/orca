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

# pylint: disable=import-outside-toplevel

"""Unit tests for ax_component.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi, GLib

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from .orca_test_context import OrcaTestContext


@pytest.mark.unit
class TestAXComponent:
    """Test AXComponent class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for ax_component dependencies."""

        essential_modules = test_context.setup_shared_dependencies()

        debug_mock = essential_modules["orca.debug"]
        debug_mock.print_message = test_context.Mock()
        debug_mock.print_tokens = test_context.Mock()
        debug_mock.LEVEL_INFO = 800

        ax_object_class_mock = test_context.Mock()
        ax_object_class_mock.supports_component = test_context.Mock(return_value=True)
        ax_object_class_mock.is_bogus = test_context.Mock(return_value=False)
        ax_object_class_mock.get_child_count = test_context.Mock(return_value=0)
        essential_modules["orca.ax_object"].AXObject = ax_object_class_mock

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
            test_context.patch_object(Atspi.Component, "get_position", return_value=mock_position)
        elif case["supports_component"] and case["position_result"]:
            test_context.patch_object(
                Atspi.Component,
                "get_position",
                return_value=case["position_result"],
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
                "scroll_object_to_point",
                "scroll_to_point",
                False,
                id="scroll_object_to_point",
            ),
            pytest.param(
                "scroll_object_to_location",
                "scroll_to",
                False,
                id="scroll_object_to_location",
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
            essential_modules["orca.ax_object"].AXObject,
            "supports_component",
            return_value=True,
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
            test_context.patch_object(Atspi.Component, "get_size", return_value=mock_size)
        elif case["supports_component"] and case["size_result"]:
            test_context.patch_object(Atspi.Component, "get_size", return_value=case["size_result"])
        else:
            mock_negative_size = test_context.Mock(x=-1, y=-1)
            test_context.patch_object(Atspi.Component, "get_size", return_value=mock_negative_size)
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
            return_value=case["supports_component"],
        )
        from orca.ax_component import AXComponent

        if case["supports_component"]:
            test_context.patch_object(Atspi.Component, "get_extents", return_value=mock_rect)
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
            return_value=case["supports_component"],
        )
        essential_modules["orca.ax_object"].AXObject.is_bogus = test_context.Mock(
            return_value=case["is_bogus"],
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
            test_context.patch_object(Atspi.Component, "scroll_to_point", return_value=False)
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
                Atspi.Component,
                "scroll_to",
                return_value=case["scroll_result"],
            )
        else:
            test_context.patch_object(Atspi.Component, "scroll_to", return_value=False)
        result = AXComponent.scroll_object_to_location(mock_accessible, Atspi.ScrollType.TOP_LEFT)
        assert result is case["expected_result"]
