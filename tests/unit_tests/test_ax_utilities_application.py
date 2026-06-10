# Unit tests for ax_utilities_application.py methods.
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
# pylint: disable=too-many-lines
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=import-outside-toplevel
# pylint: disable=protected-access

"""Unit tests for ax_utilities_application.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import mock_open

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi, GLib

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext


@pytest.mark.unit
class TestAXUtilitiesApplication:
    """Test AXUtilitiesApplication class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext):
        """Set up mocks for ax_utilities_application dependencies."""

        essential_modules = test_context.setup_shared_dependencies()

        debug_mock = essential_modules["orca.debug"]
        debug_mock.print_message = test_context.Mock()
        debug_mock.print_tokens = test_context.Mock()
        debug_mock.LEVEL_INFO = 800
        debug_mock.LEVEL_SEVERE = 1000
        debug_mock.debugLevel = debug_mock.LEVEL_SEVERE

        ax_object_class_mock = test_context.Mock()
        ax_object_class_mock.is_valid = test_context.Mock(side_effect=lambda obj: obj is not None)
        ax_object_class_mock.get_name = test_context.Mock(return_value="")
        ax_object_class_mock.get_child_count = test_context.Mock(return_value=0)
        ax_object_class_mock.get_parent = test_context.Mock(return_value=None)
        ax_object_class_mock.iter_children = test_context.Mock(return_value=[])
        essential_modules["orca.ax_object"].AXObject = ax_object_class_mock

        return essential_modules

    def test_import_registers_application_cache_namespace(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test importing application utilities registers its cache namespace."""

        self._setup_dependencies(test_context)
        from orca import ax_cache_manager

        manager = ax_cache_manager.get_manager()
        register = test_context.patch_object(
            manager,
            "register_cache",
            wraps=manager.register_cache,
        )

        from orca.ax_utilities_application import AXUtilitiesApplication

        register.assert_called_once_with(
            AXUtilitiesApplication._CACHE,
            AXUtilitiesApplication._CACHE.APP_FOR_OBJECT,
            lifetime=ax_cache_manager.Lifetime.PROCESS,
            clear_on_demand=ax_cache_manager.ClearPolicy.PRESERVE,
            clear_interval_seconds=AXUtilitiesApplication._CACHE._CACHE_CLEAR_INTERVAL_SECONDS,
        )
        assert AXUtilitiesApplication._CACHE._CACHE_CLEAR_INTERVAL_SECONDS == 120

    def test_manager_clear_cache_now_preserves_application_cache(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test routine manager clearing preserves cached application lookups."""

        self._setup_dependencies(test_context)
        from orca import ax_cache_manager
        from orca.ax_utilities_application import AXUtilitiesApplication

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_app = test_context.Mock(spec=Atspi.Accessible)
        AXUtilitiesApplication._CACHE.set_application(mock_obj, mock_app)

        ax_cache_manager.get_manager().clear_cache_now("test reason")

        assert AXUtilitiesApplication._CACHE.get_application(mock_obj) == mock_app

    @pytest.mark.parametrize(
        "method_name, atspi_method_name, success_value",
        [
            pytest.param(
                "get_application_toolkit_name",
                "get_toolkit_name",
                "Gtk",
                id="toolkit_name",
            ),
            pytest.param(
                "get_application_toolkit_version",
                "get_toolkit_version",
                "3.0",
                id="toolkit_version",
            ),
        ],
    )
    def test_toolkit_info_methods(
        self,
        test_context,
        method_name,
        atspi_method_name,
        success_value,
    ) -> None:
        """Test AXUtilitiesApplication toolkit methods."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_application import AXUtilitiesApplication

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_app = test_context.Mock(spec=Atspi.Accessible)
        method = getattr(AXUtilitiesApplication, method_name)

        test_context.patch_object(AXUtilitiesApplication, "get_application", return_value=None)
        result = method(mock_obj)
        assert result == ""

        test_context.patch_object(AXUtilitiesApplication, "get_application", return_value=mock_app)
        test_context.patch_object(Atspi.Accessible, atspi_method_name, return_value=success_value)
        result = method(mock_obj)
        assert result == success_value

        def raise_glib_error(self):
            raise GLib.GError("Test error")

        test_context.patch_object(Atspi.Accessible, atspi_method_name, side_effect=raise_glib_error)
        result = method(mock_obj)
        assert result == ""

    @pytest.mark.parametrize(
        "method_name, atspi_method, mock_method_name, success_return, error_return",
        [
            pytest.param("get_desktop", Atspi, "get_desktop", "mock_desktop", None, id="desktop"),
            pytest.param(
                "get_process_id",
                Atspi.Accessible,
                "get_process_id",
                1234,
                -1,
                id="process_id",
            ),
        ],
    )
    def test_glib_error_handling_methods(
        self,
        test_context,
        method_name,
        atspi_method,
        mock_method_name,
        success_return,
        error_return,
    ) -> None:
        """Test AXUtilitiesApplication GLib error handling."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_application import AXUtilitiesApplication

        if method_name == "get_desktop":
            mock_desktop = test_context.Mock(spec=Atspi.Accessible)

            test_context.patch_object(atspi_method, mock_method_name, return_value=mock_desktop)
            result = AXUtilitiesApplication.get_desktop()
            assert result == mock_desktop

            def raise_glib_error(self):
                raise GLib.GError("Test error")

            test_context.patch_object(atspi_method, mock_method_name, side_effect=raise_glib_error)
            result = AXUtilitiesApplication.get_desktop()
            assert result is error_return
        else:
            mock_obj = test_context.Mock(spec=Atspi.Accessible)
            method = getattr(AXUtilitiesApplication, method_name)

            test_context.patch_object(atspi_method, mock_method_name, return_value=success_return)
            result = method(mock_obj)
            assert result == success_return

            def raise_glib_error(self):
                raise GLib.GError("Test error")

            test_context.patch_object(atspi_method, mock_method_name, side_effect=raise_glib_error)
            result = method(mock_obj)
            assert result == error_return

    @pytest.mark.parametrize(
        "app_exists,app_name,toolkit_name,toolkit_version,expected",
        [
            (True, "Firefox", "Gtk", "3.0", "Firefox (Gtk 3.0)"),
            (False, "", "", "", ""),
        ],
    )
    def test_application_as_string(
        self,
        test_context: OrcaTestContext,
        app_exists: bool,
        app_name: str,
        toolkit_name: str,
        toolkit_version: str,
        expected: str,
    ) -> None:
        """Test AXUtilitiesApplication.application_as_string with different scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities_application import AXUtilitiesApplication

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        if app_exists:
            mock_app = test_context.Mock(spec=Atspi.Accessible)
            test_context.patch_object(
                AXUtilitiesApplication,
                "get_application",
                return_value=mock_app,
            )
            test_context.patch_object(AXObject, "get_name", return_value=app_name)
            test_context.patch_object(
                AXUtilitiesApplication,
                "get_application_toolkit_name",
                return_value=toolkit_name,
            )
            test_context.patch_object(
                AXUtilitiesApplication,
                "get_application_toolkit_version",
                return_value=toolkit_version,
            )
        else:
            test_context.patch_object(AXUtilitiesApplication, "get_application", return_value=None)
        result = AXUtilitiesApplication.application_as_string(mock_obj)
        assert result == expected

    def test_get_all_applications_no_desktop(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesApplication.get_all_applications with no desktop."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_application import AXUtilitiesApplication

        test_context.patch_object(AXUtilitiesApplication, "get_desktop", return_value=None)
        result = AXUtilitiesApplication.get_all_applications()
        assert not result

    def test_get_all_applications(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesApplication.get_all_applications."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities_application import AXUtilitiesApplication

        mock_desktop = test_context.Mock(spec=Atspi.Accessible)
        mock_app1 = test_context.Mock(spec=Atspi.Accessible)
        mock_app2 = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXUtilitiesApplication, "get_desktop", return_value=mock_desktop)
        test_context.patch_object(
            AXObject,
            "iter_children",
            side_effect=lambda parent, pred: filter(pred, [mock_app1, mock_app2]),
        )
        test_context.patch_object(
            AXObject,
            "get_name",
            side_effect=lambda obj: "App1" if obj == mock_app1 else "App2",
        )
        result = AXUtilitiesApplication.get_all_applications()
        assert result == [mock_app1, mock_app2]

    def test_get_all_applications_excludes_unresponsive(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test AXUtilitiesApplication.get_all_applications excludes unresponsive."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities_application import AXUtilitiesApplication

        mock_desktop = test_context.Mock(spec=Atspi.Accessible)
        mock_app1 = test_context.Mock(spec=Atspi.Accessible)
        mock_app2 = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXUtilitiesApplication, "get_desktop", return_value=mock_desktop)
        test_context.patch_object(
            AXObject,
            "iter_children",
            side_effect=lambda parent, pred: filter(pred, [mock_app1, mock_app2]),
        )
        test_context.patch_object(
            AXObject,
            "get_name",
            side_effect=lambda obj: "App1" if obj == mock_app1 else "App2",
        )
        test_context.patch_object(
            AXUtilitiesApplication,
            "is_application_unresponsive",
            side_effect=lambda obj: obj == mock_app2,
        )
        result = AXUtilitiesApplication.get_all_applications(exclude_unresponsive=True)
        assert result == [mock_app1]

    def test_get_all_applications_excludes_mutter_x11_frames(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test AXUtilitiesApplication.get_all_applications excludes mutter-x11-frames."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities_application import AXUtilitiesApplication

        mock_desktop = test_context.Mock(spec=Atspi.Accessible)
        mock_app1 = test_context.Mock(spec=Atspi.Accessible)
        mock_app2 = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXUtilitiesApplication, "get_desktop", return_value=mock_desktop)
        test_context.patch_object(
            AXObject,
            "iter_children",
            side_effect=lambda parent, pred: filter(pred, [mock_app1, mock_app2]),
        )
        test_context.patch_object(
            AXObject,
            "get_name",
            side_effect=lambda obj: "mutter-x11-frames" if obj == mock_app1 else "App2",
        )
        result = AXUtilitiesApplication.get_all_applications()
        assert result == [mock_app2]

    def test_get_all_applications_includes_mutter_x11_frames_in_debug(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test AXUtilitiesApplication.get_all_applications includes mutter-x11-frames in debug."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities_application import AXUtilitiesApplication

        mock_desktop = test_context.Mock(spec=Atspi.Accessible)
        mock_app1 = test_context.Mock(spec=Atspi.Accessible)
        mock_app2 = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXUtilitiesApplication, "get_desktop", return_value=mock_desktop)
        test_context.patch_object(
            AXObject,
            "iter_children",
            side_effect=lambda parent, pred: filter(pred, [mock_app1, mock_app2]),
        )
        test_context.patch_object(
            AXObject,
            "get_name",
            side_effect=lambda obj: "mutter-x11-frames" if obj == mock_app1 else "App2",
        )
        result = AXUtilitiesApplication.get_all_applications(is_debug=True)
        assert result == [mock_app1, mock_app2]

    def test_get_all_applications_must_have_window(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesApplication.get_all_applications filters without windows."""

        self._setup_dependencies(test_context)
        from orca.ax_object import AXObject
        from orca.ax_utilities_application import AXUtilitiesApplication

        mock_desktop = test_context.Mock(spec=Atspi.Accessible)
        mock_app1 = test_context.Mock(spec=Atspi.Accessible)
        mock_app2 = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXUtilitiesApplication, "get_desktop", return_value=mock_desktop)
        test_context.patch_object(
            AXObject,
            "iter_children",
            side_effect=lambda parent, pred: filter(pred, [mock_app1, mock_app2]),
        )
        test_context.patch_object(
            AXObject,
            "get_name",
            side_effect=lambda obj: "App1" if obj == mock_app1 else "App2",
        )
        test_context.patch_object(
            AXObject,
            "get_child_count",
            side_effect=lambda obj: 1 if obj == mock_app1 else 0,
        )
        result = AXUtilitiesApplication.get_all_applications(must_have_window=True)
        assert result == [mock_app1]

    def test_get_application_with_none(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesApplication.get_application with None."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_application import AXUtilitiesApplication

        result = AXUtilitiesApplication.get_application(None)
        assert result is None

    def test_get_application_with_valid_object(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesApplication.get_application."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_application import AXUtilitiesApplication

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_app = test_context.Mock(spec=Atspi.Accessible)
        getter = test_context.patch_object(
            Atspi.Accessible, "get_application", return_value=mock_app
        )
        result = AXUtilitiesApplication.get_application(mock_obj)
        assert result == mock_app
        assert AXUtilitiesApplication.get_application(mock_obj) == mock_app
        getter.assert_called_once_with(mock_obj)

    def test_get_application_with_glib_error(self, test_context: OrcaTestContext) -> None:
        """Test AXUtilitiesApplication.get_application handles GLib.GError."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_application import AXUtilitiesApplication

        mock_obj = test_context.Mock(spec=Atspi.Accessible)

        def raise_glib_error(self):
            raise GLib.GError("Test error")

        test_context.patch_object(Atspi.Accessible, "get_application", side_effect=raise_glib_error)
        result = AXUtilitiesApplication.get_application(mock_obj)
        assert result is None

    @pytest.mark.parametrize(
        "search_pid,expected_found",
        [
            (1234, True),
            (9999, False),
        ],
    )
    def test_get_application_with_pid(
        self,
        test_context: OrcaTestContext,
        search_pid: int,
        expected_found: bool,
    ) -> None:
        """Test AXUtilitiesApplication.get_application_with_pid with different scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_application import AXUtilitiesApplication

        mock_app1 = test_context.Mock(spec=Atspi.Accessible)
        mock_app2 = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXUtilitiesApplication,
            "get_all_applications",
            return_value=[mock_app1, mock_app2],
        )
        test_context.patch_object(
            AXUtilitiesApplication,
            "get_process_id",
            side_effect=lambda obj: 1234 if obj == mock_app1 else 5678,
        )
        result = AXUtilitiesApplication.get_application_with_pid(search_pid)
        if expected_found:
            assert result == mock_app1
        else:
            assert result is None

    @pytest.mark.parametrize(
        "parent_is_desktop,expected_found",
        [
            (True, True),
            (False, False),
        ],
    )
    def test_is_application_in_desktop(
        self,
        test_context: OrcaTestContext,
        parent_is_desktop: bool,
        expected_found: bool,
    ) -> None:
        """Test AXUtilitiesApplication.is_application_in_desktop with different scenarios."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.ax_utilities_application import AXUtilitiesApplication

        mock_desktop = test_context.Mock(spec=Atspi.Accessible)
        mock_app = test_context.Mock(spec=Atspi.Accessible)
        mock_other_parent = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXUtilitiesApplication, "get_desktop", return_value=mock_desktop)
        parent = mock_desktop if parent_is_desktop else mock_other_parent
        essential_modules["orca.ax_object"].AXObject.get_parent = test_context.Mock(
            return_value=parent
        )
        result = AXUtilitiesApplication.is_application_in_desktop(mock_app)
        assert result is expected_found

    @pytest.mark.parametrize(
        "file_content,expected_unresponsive",
        [
            ("Name:\tbash\nState:\tZ (zombie)\n", True),
            ("Name:\tbash\nState:\tT (stopped)\n", True),
            ("Name:\tbash\nState:\tR (running)\n", False),
            ("", False),
        ],
    )
    def test_is_application_unresponsive(
        self,
        test_context: OrcaTestContext,
        file_content: str,
        expected_unresponsive: bool,
    ) -> None:
        """Test AXUtilitiesApplication.is_application_unresponsive with different process states."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_application import AXUtilitiesApplication

        mock_app = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXUtilitiesApplication, "get_process_id", return_value=1234)
        test_context.patch("builtins.open", new=mock_open(read_data=file_content))
        result = AXUtilitiesApplication.is_application_unresponsive(mock_app)
        assert result is expected_unresponsive
