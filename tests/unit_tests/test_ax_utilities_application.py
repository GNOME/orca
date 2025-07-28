# Unit tests for ax_utilities_application.py application-related methods.
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
# pylint: disable=unused-argument

"""Unit tests for ax_utilities_application.py application-related methods."""

import subprocess
from unittest.mock import Mock

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi
from gi.repository import GLib

from .conftest import clean_module_cache

@pytest.mark.unit
class TestAXUtilitiesApplication:
    """Test application-related methods."""

    @pytest.mark.parametrize(
        "method_name, atspi_method_name, success_value",
        [
            pytest.param(
                "get_application_toolkit_name", "get_toolkit_name", "Gtk", id="toolkit_name"
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
        self, monkeypatch, method_name, atspi_method_name, success_value, mock_orca_dependencies
    ):
        """Test AXUtilitiesApplication toolkit methods."""

        clean_module_cache("orca.ax_utilities_application")
        from orca.ax_utilities_application import AXUtilitiesApplication

        mock_obj = Mock(spec=Atspi.Accessible)
        mock_app = Mock(spec=Atspi.Accessible)
        method = getattr(AXUtilitiesApplication, method_name)

        # Scenario: Application is None
        monkeypatch.setattr(AXUtilitiesApplication, "get_application", lambda obj: None)
        result = method(mock_obj)
        assert result == ""

        # Scenario: Valid application returns expected value
        monkeypatch.setattr(AXUtilitiesApplication, "get_application", lambda obj: mock_app)
        monkeypatch.setattr(Atspi.Accessible, atspi_method_name, lambda self: success_value)
        result = method(mock_obj)
        assert result == success_value

        # Scenario: GLib error occurs during method call
        def raise_glib_error(self):
            raise GLib.GError("Test error")

        monkeypatch.setattr(Atspi.Accessible, atspi_method_name, raise_glib_error)
        result = method(mock_obj)
        assert result == ""

    @pytest.mark.parametrize(
        "method_name, atspi_method, mock_method_name, success_return, error_return",
        [
            pytest.param("get_desktop", Atspi, "get_desktop", "mock_desktop", None, id="desktop"),
            pytest.param(
                "get_process_id", Atspi.Accessible, "get_process_id", 1234, -1, id="process_id"
            ),
        ],
    )
    def test_glib_error_handling_methods(
        self,
        monkeypatch,
        method_name,
        atspi_method,
        mock_method_name,
        success_return,
        error_return,
        mock_orca_dependencies,
    ):
        """Test AXUtilitiesApplication GLib error handling."""

        clean_module_cache("orca.ax_utilities_application")
        from orca.ax_utilities_application import AXUtilitiesApplication

        if method_name == "get_desktop":
            mock_desktop = Mock(spec=Atspi.Accessible)

            # Scenario: Desktop method succeeds
            monkeypatch.setattr(atspi_method, mock_method_name, lambda index: mock_desktop)
            result = AXUtilitiesApplication.get_desktop()
            assert result == mock_desktop

            # Scenario: Desktop method raises GLib error
            def raise_glib_error(index):
                raise GLib.GError("Test error")

            monkeypatch.setattr(atspi_method, mock_method_name, raise_glib_error)
            result = AXUtilitiesApplication.get_desktop()
            assert result is error_return
        else:
            mock_obj = Mock(spec=Atspi.Accessible)
            method = getattr(AXUtilitiesApplication, method_name)

            # Scenario: Method call succeeds
            monkeypatch.setattr(atspi_method, mock_method_name, lambda self: success_return)
            result = method(mock_obj)
            assert result == success_return

            # Scenario: Method call raises GLib error
            def raise_glib_error(self):
                raise GLib.GError("Test error")

            monkeypatch.setattr(atspi_method, mock_method_name, raise_glib_error)
            result = method(mock_obj)
            assert result == error_return

    def test_application_as_string(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesApplication.application_as_string."""

        clean_module_cache("orca.ax_utilities_application")
        from orca.ax_utilities_application import AXUtilitiesApplication
        from orca.ax_object import AXObject

        mock_app = Mock(spec=Atspi.Accessible)
        mock_obj = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(AXUtilitiesApplication, "get_application", lambda obj: mock_app)
        monkeypatch.setattr(AXObject, "get_name", lambda obj: "Firefox")
        monkeypatch.setattr(
            AXUtilitiesApplication,
            "get_application_toolkit_name",
            lambda obj: "Gtk",
        )
        monkeypatch.setattr(
            AXUtilitiesApplication,
            "get_application_toolkit_version",
            lambda obj: "3.0",
        )
        result = AXUtilitiesApplication.application_as_string(mock_obj)
        assert result == "Firefox (Gtk 3.0)"

    def test_application_as_string_none_app(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesApplication.application_as_string with None."""

        clean_module_cache("orca.ax_utilities_application")
        from orca.ax_utilities_application import AXUtilitiesApplication

        mock_obj = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(AXUtilitiesApplication, "get_application", lambda obj: None)
        result = AXUtilitiesApplication.application_as_string(mock_obj)
        assert result == ""

    def test_get_all_applications_no_desktop(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesApplication.get_all_applications with no desktop."""

        clean_module_cache("orca.ax_utilities_application")
        from orca.ax_utilities_application import AXUtilitiesApplication

        monkeypatch.setattr(AXUtilitiesApplication, "get_desktop", lambda: None)
        result = AXUtilitiesApplication.get_all_applications()
        assert not result

    def test_get_all_applications(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesApplication.get_all_applications."""

        clean_module_cache("orca.ax_utilities_application")
        from orca.ax_utilities_application import AXUtilitiesApplication
        from orca.ax_object import AXObject

        mock_desktop = Mock(spec=Atspi.Accessible)
        mock_app1 = Mock(spec=Atspi.Accessible)
        mock_app2 = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(AXUtilitiesApplication, "get_desktop", lambda: mock_desktop)
        monkeypatch.setattr(
            AXObject,
            "iter_children",
            lambda parent, pred: filter(pred, [mock_app1, mock_app2]),
        )
        monkeypatch.setattr(
            AXObject,
            "get_name",
            lambda obj: "App1" if obj == mock_app1 else "App2",
        )

        result = AXUtilitiesApplication.get_all_applications()
        assert result == [mock_app1, mock_app2]

    def test_get_all_applications_excludes_unresponsive(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesApplication.get_all_applications excludes unresponsive."""

        clean_module_cache("orca.ax_utilities_application")
        from orca.ax_utilities_application import AXUtilitiesApplication
        from orca.ax_object import AXObject

        mock_desktop = Mock(spec=Atspi.Accessible)
        mock_app1 = Mock(spec=Atspi.Accessible)
        mock_app2 = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(AXUtilitiesApplication, "get_desktop", lambda: mock_desktop)
        monkeypatch.setattr(
            AXObject,
            "iter_children",
            lambda parent, pred: filter(pred, [mock_app1, mock_app2]),
        )
        monkeypatch.setattr(
            AXObject,
            "get_name",
            lambda obj: "App1" if obj == mock_app1 else "App2",
        )
        monkeypatch.setattr(
            AXUtilitiesApplication,
            "is_application_unresponsive",
            lambda obj: obj == mock_app2,
        )

        result = AXUtilitiesApplication.get_all_applications(exclude_unresponsive=True)
        assert result == [mock_app1]

    def test_get_all_applications_excludes_mutter_x11_frames(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesApplication.get_all_applications excludes mutter-x11-frames."""

        clean_module_cache("orca.ax_utilities_application")
        from orca.ax_utilities_application import AXUtilitiesApplication
        from orca.ax_object import AXObject

        mock_desktop = Mock(spec=Atspi.Accessible)
        mock_app1 = Mock(spec=Atspi.Accessible)
        mock_app2 = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(AXUtilitiesApplication, "get_desktop", lambda: mock_desktop)
        monkeypatch.setattr(
            AXObject,
            "iter_children",
            lambda parent, pred: filter(pred, [mock_app1, mock_app2]),
        )
        monkeypatch.setattr(
            AXObject, "get_name", lambda obj: "mutter-x11-frames" if obj == mock_app1 else "App2"
        )

        result = AXUtilitiesApplication.get_all_applications()
        assert result == [mock_app2]

    def test_get_all_applications_includes_mutter_x11_frames_in_debug(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesApplication.get_all_applications includes mutter-x11-frames in debug."""

        clean_module_cache("orca.ax_utilities_application")
        from orca.ax_utilities_application import AXUtilitiesApplication
        from orca.ax_object import AXObject

        mock_desktop = Mock(spec=Atspi.Accessible)
        mock_app1 = Mock(spec=Atspi.Accessible)
        mock_app2 = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(AXUtilitiesApplication, "get_desktop", lambda: mock_desktop)
        monkeypatch.setattr(
            AXObject,
            "iter_children",
            lambda parent, pred: filter(pred, [mock_app1, mock_app2]),
        )
        monkeypatch.setattr(
            AXObject, "get_name", lambda obj: "mutter-x11-frames" if obj == mock_app1 else "App2"
        )

        result = AXUtilitiesApplication.get_all_applications(is_debug=True)
        assert result == [mock_app1, mock_app2]

    def test_get_all_applications_must_have_window(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesApplication.get_all_applications filters without windows."""

        clean_module_cache("orca.ax_utilities_application")
        from orca.ax_utilities_application import AXUtilitiesApplication
        from orca.ax_object import AXObject

        mock_desktop = Mock(spec=Atspi.Accessible)
        mock_app1 = Mock(spec=Atspi.Accessible)
        mock_app2 = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(AXUtilitiesApplication, "get_desktop", lambda: mock_desktop)
        monkeypatch.setattr(
            AXObject,
            "iter_children",
            lambda parent, pred: filter(pred, [mock_app1, mock_app2]),
        )
        monkeypatch.setattr(
            AXObject,
            "get_name",
            lambda obj: "App1" if obj == mock_app1 else "App2",
        )
        monkeypatch.setattr(AXObject, "get_child_count", lambda obj: 1 if obj == mock_app1 else 0)
        result = AXUtilitiesApplication.get_all_applications(must_have_window=True)
        assert result == [mock_app1]

    def test_get_application_with_none(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesApplication.get_application with None."""

        clean_module_cache("orca.ax_utilities_application")
        from orca.ax_utilities_application import AXUtilitiesApplication

        result = AXUtilitiesApplication.get_application(None)
        assert result is None

    def test_get_application_with_valid_object(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesApplication.get_application."""

        clean_module_cache("orca.ax_utilities_application")
        from orca.ax_utilities_application import AXUtilitiesApplication

        mock_obj = Mock(spec=Atspi.Accessible)
        mock_app = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(Atspi.Accessible, "get_application", lambda self: mock_app)
        result = AXUtilitiesApplication.get_application(mock_obj)
        assert result == mock_app

    def test_get_application_with_glib_error(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesApplication.get_application handles GLib.GError."""

        clean_module_cache("orca.ax_utilities_application")
        from orca.ax_utilities_application import AXUtilitiesApplication

        mock_obj = Mock(spec=Atspi.Accessible)

        def raise_glib_error(self):
            raise GLib.GError("Test error")

        monkeypatch.setattr(Atspi.Accessible, "get_application", raise_glib_error)
        result = AXUtilitiesApplication.get_application(mock_obj)
        assert result is None

    def test_get_application_with_pid_found(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesApplication.get_application_with_pid."""

        clean_module_cache("orca.ax_utilities_application")
        from orca.ax_utilities_application import AXUtilitiesApplication

        mock_app1 = Mock(spec=Atspi.Accessible)
        mock_app2 = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(
            AXUtilitiesApplication,
            "get_all_applications",
            lambda: [mock_app1, mock_app2],
        )
        monkeypatch.setattr(
            AXUtilitiesApplication,
            "get_process_id",
            lambda obj: 1234 if obj == mock_app1 else 5678,
        )

        result = AXUtilitiesApplication.get_application_with_pid(1234)
        assert result == mock_app1

    def test_get_application_with_pid_not_found(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesApplication.get_application_with_pid with no match."""

        clean_module_cache("orca.ax_utilities_application")
        from orca.ax_utilities_application import AXUtilitiesApplication

        mock_app1 = Mock(spec=Atspi.Accessible)
        mock_app2 = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(
            AXUtilitiesApplication,
            "get_all_applications",
            lambda: [mock_app1, mock_app2],
        )
        monkeypatch.setattr(
            AXUtilitiesApplication,
            "get_process_id",
            lambda obj: 1234 if obj == mock_app1 else 5678,
        )

        result = AXUtilitiesApplication.get_application_with_pid(9999)
        assert result is None

    def test_is_application_in_desktop_found(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesApplication.is_application_in_desktop."""

        clean_module_cache("orca.ax_utilities_application")
        from orca.ax_utilities_application import AXUtilitiesApplication

        mock_app1 = Mock(spec=Atspi.Accessible)
        mock_app2 = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(
            AXUtilitiesApplication,
            "get_all_applications",
            lambda: [mock_app1, mock_app2],
        )

        result = AXUtilitiesApplication.is_application_in_desktop(mock_app1)
        assert result is True

    def test_is_application_in_desktop_not_found(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesApplication.is_application_in_desktop with no match."""

        clean_module_cache("orca.ax_utilities_application")
        from orca.ax_utilities_application import AXUtilitiesApplication

        mock_app1 = Mock(spec=Atspi.Accessible)
        mock_app2 = Mock(spec=Atspi.Accessible)
        mock_app3 = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(
            AXUtilitiesApplication,
            "get_all_applications",
            lambda: [mock_app1, mock_app2],
        )

        result = AXUtilitiesApplication.is_application_in_desktop(mock_app3)
        assert result is False

    def test_is_application_unresponsive_zombie_process(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesApplication.is_application_unresponsive with zombie."""

        clean_module_cache("orca.ax_utilities_application")
        from orca.ax_utilities_application import AXUtilitiesApplication

        mock_app = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(AXUtilitiesApplication, "get_process_id", lambda obj: 1234)
        monkeypatch.setattr(
            subprocess,
            "getoutput",
            lambda cmd: "State: Z (zombie)",
        )

        result = AXUtilitiesApplication.is_application_unresponsive(mock_app)
        assert result is True

    def test_is_application_unresponsive_stopped_process(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesApplication.is_application_unresponsive with stopped."""

        clean_module_cache("orca.ax_utilities_application")
        from orca.ax_utilities_application import AXUtilitiesApplication

        mock_app = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(AXUtilitiesApplication, "get_process_id", lambda obj: 1234)
        monkeypatch.setattr(
            subprocess,
            "getoutput",
            lambda cmd: "State: T (stopped)",
        )

        result = AXUtilitiesApplication.is_application_unresponsive(mock_app)
        assert result is True

    def test_is_application_unresponsive_running_process(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesApplication.is_application_unresponsive with running."""

        clean_module_cache("orca.ax_utilities_application")
        from orca.ax_utilities_application import AXUtilitiesApplication

        mock_app = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(AXUtilitiesApplication, "get_process_id", lambda obj: 1234)
        monkeypatch.setattr(
            subprocess,
            "getoutput",
            lambda cmd: "State: R (running)",
        )

        result = AXUtilitiesApplication.is_application_unresponsive(mock_app)
        assert result is False

    def test_is_application_unresponsive_with_exception(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesApplication.is_application_unresponsive handles exceptions."""

        clean_module_cache("orca.ax_utilities_application")
        from orca.ax_utilities_application import AXUtilitiesApplication

        mock_app = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(AXUtilitiesApplication, "get_process_id", lambda obj: 1234)
        monkeypatch.setattr(subprocess, "getoutput", lambda cmd: "")
        result = AXUtilitiesApplication.is_application_unresponsive(mock_app)
        assert result is False
