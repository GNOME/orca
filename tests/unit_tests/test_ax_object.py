# Unit tests for ax_object.py object-related methods.
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
# pylint: disable=protected-access
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=import-outside-toplevel
# pylint: disable=unused-argument

"""Unit tests for ax_object.py object-related methods."""

from unittest.mock import Mock

import gi
import pytest

from conftest import clean_module_cache

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi
from gi.repository import GLib



@pytest.mark.unit
class TestAXObject:
    """Test object-related methods."""

    @pytest.fixture
    def mock_accessible(self):
        """Create a mock Atspi.Accessible object."""
        return Mock(spec=Atspi.Accessible)


    def test_is_bogus_gecko_section_hack(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.is_bogus with Gecko section hack."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_parent = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(
            AXObject,
            "get_role",
            lambda obj: Atspi.Role.SECTION if obj == mock_accessible else Atspi.Role.FRAME,
        )
        monkeypatch.setattr(AXObject, "get_parent", lambda obj: mock_parent)
        monkeypatch.setattr(AXObject, "_get_toolkit_name", lambda obj: "gecko")

        result = AXObject.is_bogus(mock_accessible)
        assert result is True
        mock_orca_dependencies["debug"].print_tokens.assert_called()

    def test_is_bogus_normal_object(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.is_bogus with normal object."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "get_role", lambda obj: Atspi.Role.BUTTON)
        monkeypatch.setattr(AXObject, "get_parent", lambda obj: None)
        monkeypatch.setattr(AXObject, "_get_toolkit_name", lambda obj: "gtk")

        result = AXObject.is_bogus(mock_accessible)
        assert result is False

    def test_has_broken_ancestry_with_qt_bug(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.has_broken_ancestry with Qt bug scenario."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_parent = Mock(spec=Atspi.Accessible)

        def mock_get_parent(obj):
            if obj == mock_accessible:
                return mock_parent
            return None

        def mock_get_role(obj):
            if obj == mock_parent:
                return Atspi.Role.WINDOW
            return Atspi.Role.BUTTON

        monkeypatch.setattr(AXObject, "get_parent", mock_get_parent)
        monkeypatch.setattr(AXObject, "get_role", mock_get_role)
        monkeypatch.setattr(AXObject, "_get_toolkit_name", lambda obj: "qt")

        result = AXObject.has_broken_ancestry(mock_accessible)
        assert result is True
        mock_orca_dependencies["debug"].print_tokens.assert_called()

    def test_has_broken_ancestry_with_good_qt_ancestry(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.has_broken_ancestry with good Qt ancestry."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_parent = Mock(spec=Atspi.Accessible)
        mock_app = Mock(spec=Atspi.Accessible)

        def mock_get_parent(obj):
            if obj == mock_accessible:
                return mock_parent
            if obj == mock_parent:
                return mock_app
            return None

        def mock_get_role(obj):
            if obj == mock_app:
                return Atspi.Role.APPLICATION
            return Atspi.Role.BUTTON

        monkeypatch.setattr(AXObject, "get_parent", mock_get_parent)
        monkeypatch.setattr(AXObject, "get_role", mock_get_role)
        monkeypatch.setattr(AXObject, "_get_toolkit_name", lambda obj: "qt")

        result = AXObject.has_broken_ancestry(mock_accessible)
        assert result is False

    def test_has_broken_ancestry_non_qt(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.has_broken_ancestry with non-Qt toolkit."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "_get_toolkit_name", lambda obj: "gtk")

        result = AXObject.has_broken_ancestry(mock_accessible)
        assert result is False

    def test_has_broken_ancestry_none_object(self, monkeypatch, mock_orca_dependencies):
        """Test AXObject.has_broken_ancestry with None object."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        result = AXObject.has_broken_ancestry(None)
        assert result is False

    def test_get_toolkit_name_successful(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject._get_toolkit_name successful case."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_app = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(
            Atspi.Accessible, "get_application", lambda obj: mock_app
        )
        monkeypatch.setattr(
            Atspi.Accessible, "get_toolkit_name", lambda app: "GTK"
        )

        result = AXObject._get_toolkit_name(mock_accessible)
        assert result == "gtk"

    def test_get_toolkit_name_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject._get_toolkit_name handles GLib.GError."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject
        from orca import debug

        mock_app = Mock(spec=Atspi.Accessible)

        def raise_glib_error_on_toolkit_name(app):
            raise GLib.GError("Test error")

        monkeypatch.setattr(
            Atspi.Accessible, "get_application", lambda obj: mock_app
        )
        monkeypatch.setattr(
            Atspi.Accessible, "get_toolkit_name", raise_glib_error_on_toolkit_name
        )
        monkeypatch.setattr(debug, "print_tokens", mock_orca_dependencies["debug"].print_tokens)

        result = AXObject._get_toolkit_name(mock_accessible)
        assert result == ""
        mock_orca_dependencies["debug"].print_tokens.assert_called()

    def test_get_toolkit_name_with_none_result(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject._get_toolkit_name with None toolkit name."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_app = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(
            Atspi.Accessible, "get_application", lambda obj: mock_app
        )
        monkeypatch.setattr(
            Atspi.Accessible, "get_toolkit_name", lambda app: None
        )

        result = AXObject._get_toolkit_name(mock_accessible)
        assert result == ""

    @pytest.mark.parametrize(
        "interface_result, expected_result",
        [
            pytest.param(Mock(), True, id="supports_action"),
            pytest.param(None, False, id="no_action_interface"),
        ],
    )
    def test_supports_action(
        self,
        monkeypatch,
        mock_accessible,
        interface_result,
        expected_result,
        mock_orca_dependencies
    ):
        """Test AXObject.supports_action."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(
            Atspi.Accessible, "get_action_iface", lambda obj: interface_result
        )

        result = AXObject.supports_action(mock_accessible)
        assert result is expected_result

    def test_supports_action_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.supports_action handles GLib.GError."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        def raise_glib_error(obj):
            raise GLib.GError("Test error")

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "handle_error", Mock())
        monkeypatch.setattr(Atspi.Accessible, "get_action_iface", raise_glib_error)

        result = AXObject.supports_action(mock_accessible)
        assert result is False
        AXObject.handle_error.assert_called_once()

    @pytest.mark.parametrize(
        "interface_result, expected_result",
        [
            pytest.param(Mock(), True, id="supports_component"),
            pytest.param(None, False, id="no_component_interface"),
        ],
    )
    def test_supports_component(
        self,
        monkeypatch,
        mock_accessible,
        interface_result,
        expected_result,
        mock_orca_dependencies
    ):
        """Test AXObject.supports_component."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(
            Atspi.Accessible, "get_component_iface", lambda obj: interface_result
        )

        result = AXObject.supports_component(mock_accessible)
        assert result is expected_result

    @pytest.mark.parametrize(
        "interface_result, expected_result",
        [
            pytest.param(Mock(), True, id="supports_hypertext"),
            pytest.param(None, False, id="no_hypertext_interface"),
        ],
    )
    def test_supports_hypertext(
        self,
        monkeypatch,
        mock_accessible,
        interface_result,
        expected_result,
        mock_orca_dependencies
    ):
        """Test AXObject.supports_hypertext."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(
            Atspi.Accessible, "get_hypertext_iface", lambda obj: interface_result
        )

        result = AXObject.supports_hypertext(mock_accessible)
        assert result is expected_result

    @pytest.mark.parametrize(
        "interface_result, expected_result",
        [
            pytest.param(Mock(), True, id="supports_text"),
            pytest.param(None, False, id="no_text_interface"),
        ],
    )
    def test_supports_text(
        self,
        monkeypatch,
        mock_accessible,
        interface_result,
        expected_result,
        mock_orca_dependencies
    ):
        """Test AXObject.supports_text."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(
            Atspi.Accessible, "get_text_iface", lambda obj: interface_result
        )

        result = AXObject.supports_text(mock_accessible)
        assert result is expected_result
