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
# pylint: disable=too-many-lines
# pylint: disable=wrong-import-order

"""Unit tests for ax_object.py object-related methods."""

import sys
from unittest.mock import Mock

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi
from gi.repository import GLib

from .conftest import clean_module_cache


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

    def test_is_bogus_normal_object(self, monkeypatch, mock_accessible, mock_orca_dependencies):
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

    def test_has_broken_ancestry_non_qt(self, monkeypatch, mock_accessible, mock_orca_dependencies):
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

        monkeypatch.setattr(Atspi.Accessible, "get_application", lambda obj: mock_app)
        monkeypatch.setattr(Atspi.Accessible, "get_toolkit_name", lambda app: "GTK")

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

        monkeypatch.setattr(Atspi.Accessible, "get_application", lambda obj: mock_app)
        monkeypatch.setattr(Atspi.Accessible, "get_toolkit_name", raise_glib_error_on_toolkit_name)
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

        monkeypatch.setattr(Atspi.Accessible, "get_application", lambda obj: mock_app)
        monkeypatch.setattr(Atspi.Accessible, "get_toolkit_name", lambda app: None)

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
        mock_orca_dependencies,
    ):
        """Test AXObject.supports_action."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(Atspi.Accessible, "get_action_iface", lambda obj: interface_result)

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
        mock_orca_dependencies,
    ):
        """Test AXObject.supports_component."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(Atspi.Accessible, "get_component_iface", lambda obj: interface_result)

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
        mock_orca_dependencies,
    ):
        """Test AXObject.supports_hypertext."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(Atspi.Accessible, "get_hypertext_iface", lambda obj: interface_result)

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
        mock_orca_dependencies,
    ):
        """Test AXObject.supports_text."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(Atspi.Accessible, "get_text_iface", lambda obj: interface_result)

        result = AXObject.supports_text(mock_accessible)
        assert result is expected_result

    def test_clear_all_dictionaries_with_reason(self, monkeypatch, mock_orca_dependencies):
        """Test AXObject._clear_all_dictionaries with reason provided."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        AXObject.KNOWN_DEAD[123] = True
        AXObject.OBJECT_ATTRIBUTES[456] = {"role": "button"}

        AXObject._clear_all_dictionaries("test reason")

        assert len(AXObject.KNOWN_DEAD) == 0
        assert len(AXObject.OBJECT_ATTRIBUTES) == 0

        # Verify debug message was called with reason
        mock_orca_dependencies["debug"].print_message.assert_called_with(
            mock_orca_dependencies["debug"].LEVEL_INFO,
            "AXObject: Clearing local cache. Reason: test reason",
            True,
        )

    def test_clear_all_dictionaries_without_reason(self, monkeypatch, mock_orca_dependencies):
        """Test AXObject._clear_all_dictionaries without reason."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        AXObject.KNOWN_DEAD[789] = False
        AXObject.OBJECT_ATTRIBUTES[101] = {"name": "test"}

        AXObject._clear_all_dictionaries()

        assert len(AXObject.KNOWN_DEAD) == 0
        assert len(AXObject.OBJECT_ATTRIBUTES) == 0

        # Verify debug message was called without reason
        mock_orca_dependencies["debug"].print_message.assert_called_with(
            mock_orca_dependencies["debug"].LEVEL_INFO, "AXObject: Clearing local cache.", True
        )

    def test_clear_cache_now_calls_clear_all_dictionaries(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXObject.clear_cache_now calls _clear_all_dictionaries."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        clear_mock = Mock()
        monkeypatch.setattr(AXObject, "_clear_all_dictionaries", clear_mock)

        AXObject.clear_cache_now("test reason")

        clear_mock.assert_called_once_with("test reason")

    def test_start_cache_clearing_thread(self, monkeypatch, mock_orca_dependencies):
        """Test AXObject.start_cache_clearing_thread creates and starts thread."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_thread = Mock()
        thread_constructor_mock = Mock(return_value=mock_thread)
        monkeypatch.setattr("threading.Thread", thread_constructor_mock)

        AXObject.start_cache_clearing_thread()

        thread_constructor_mock.assert_called_once_with(target=AXObject._clear_stored_data)
        assert mock_thread.daemon is True
        mock_thread.start.assert_called_once()

    def test_supports_collection_invalid_object(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.supports_collection with invalid object."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: False)

        result = AXObject.supports_collection(mock_accessible)
        assert result is False

    def test_supports_collection_get_application_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.supports_collection handles get_application GLib.GError."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        def raise_glib_error(obj):
            raise GLib.GError("Test application error")

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(Atspi.Accessible, "get_application", raise_glib_error)

        result = AXObject.supports_collection(mock_accessible)
        assert result is False

        # Check that debug.print_message was called with error info
        calls = mock_orca_dependencies["debug"].print_message.call_args_list
        assert len(calls) == 1
        call_args = calls[0][0]  # Get positional arguments
        assert call_args[0] == mock_orca_dependencies["debug"].LEVEL_INFO
        assert "AXObject: Exception in supports_collection:" in call_args[1]
        assert "Test application error" in call_args[1]
        assert call_args[2] is True

    def test_supports_collection_get_collection_iface_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.supports_collection handles get_collection_iface GLib.GError."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_app = Mock(spec=Atspi.Accessible)

        def raise_glib_error(obj):
            raise GLib.GError("Test collection iface error")

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "handle_error", Mock())
        monkeypatch.setattr(Atspi.Accessible, "get_application", lambda obj: mock_app)
        monkeypatch.setattr(Atspi.Accessible, "get_collection_iface", raise_glib_error)

        result = AXObject.supports_collection(mock_accessible)
        assert result is False
        AXObject.handle_error.assert_called_once()

    def test_supports_collection_non_soffice_with_interface(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.supports_collection with non-soffice app having collection interface."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_app = Mock(spec=Atspi.Accessible)
        mock_iface = Mock()

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "get_name", lambda obj: "firefox")
        monkeypatch.setattr(Atspi.Accessible, "get_application", lambda obj: mock_app)
        monkeypatch.setattr(Atspi.Accessible, "get_collection_iface", lambda obj: mock_iface)

        result = AXObject.supports_collection(mock_accessible)
        assert result is True

    def test_supports_collection_non_soffice_without_interface(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.supports_collection with non-soffice app without collection interface."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_app = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "get_name", lambda obj: "gedit")
        monkeypatch.setattr(Atspi.Accessible, "get_application", lambda obj: mock_app)
        monkeypatch.setattr(Atspi.Accessible, "get_collection_iface", lambda obj: None)

        result = AXObject.supports_collection(mock_accessible)
        assert result is False

    def test_supports_collection_soffice_with_document_text(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.supports_collection with soffice containing document text."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_app = Mock(spec=Atspi.Accessible)
        mock_ancestor = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "get_name", lambda obj: "soffice")
        monkeypatch.setattr(Atspi.Accessible, "get_application", lambda obj: mock_app)
        monkeypatch.setattr(Atspi.Accessible, "get_collection_iface", lambda obj: Mock())
        monkeypatch.setattr(
            AXObject,
            "find_ancestor_inclusive",
            lambda obj, func: mock_ancestor if func(mock_ancestor) else None,
        )
        monkeypatch.setattr(
            AXObject,
            "get_role",
            lambda obj: Atspi.Role.DOCUMENT_TEXT if obj == mock_ancestor else Atspi.Role.BUTTON,
        )

        result = AXObject.supports_collection(mock_accessible)
        assert result is True

    def test_supports_collection_soffice_with_spreadsheet(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.supports_collection with soffice containing spreadsheet."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_app = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "get_name", lambda obj: "soffice")
        monkeypatch.setattr(Atspi.Accessible, "get_application", lambda obj: mock_app)
        monkeypatch.setattr(Atspi.Accessible, "get_collection_iface", lambda obj: Mock())
        monkeypatch.setattr(AXObject, "find_ancestor_inclusive", lambda obj, func: None)
        monkeypatch.setattr(AXObject, "_has_document_spreadsheet", lambda obj: True)

        result = AXObject.supports_collection(mock_accessible)
        assert result is False
        mock_orca_dependencies["debug"].print_message.assert_called_with(
            mock_orca_dependencies["debug"].LEVEL_INFO,
            "AXObject: Treating soffice as not supporting collection due to spreadsheet.",
            True,
        )

    def test_supports_collection_soffice_without_text_or_spreadsheet(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.supports_collection with soffice without document text or spreadsheet."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_app = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "get_name", lambda obj: "soffice")
        monkeypatch.setattr(Atspi.Accessible, "get_application", lambda obj: mock_app)
        monkeypatch.setattr(Atspi.Accessible, "get_collection_iface", lambda obj: Mock())
        monkeypatch.setattr(AXObject, "find_ancestor_inclusive", lambda obj, func: None)
        monkeypatch.setattr(AXObject, "_has_document_spreadsheet", lambda obj: False)

        result = AXObject.supports_collection(mock_accessible)
        assert result is True

    def test_is_valid_with_none_object(self, monkeypatch, mock_orca_dependencies):
        """Test AXObject.is_valid with None object."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        result = AXObject.is_valid(None)
        assert result is False

    def test_is_valid_with_known_dead_object(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.is_valid with known dead object."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "object_is_known_dead", lambda obj: True)

        result = AXObject.is_valid(mock_accessible)
        assert result is False

    def test_is_valid_with_valid_object(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.is_valid with valid object."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "object_is_known_dead", lambda obj: False)

        result = AXObject.is_valid(mock_accessible)
        assert result is True

    def test_object_is_known_dead_with_none_object(self, monkeypatch, mock_orca_dependencies):
        """Test AXObject.object_is_known_dead with None object."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        result = AXObject.object_is_known_dead(None)
        assert result is False

    def test_object_is_known_dead_not_in_cache(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.object_is_known_dead with object not in cache."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        AXObject.KNOWN_DEAD.clear()

        result = AXObject.object_is_known_dead(mock_accessible)
        assert result is False

    def test_object_is_known_dead_in_cache_as_dead(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.object_is_known_dead with object marked as dead."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        AXObject.KNOWN_DEAD[hash(mock_accessible)] = True

        result = AXObject.object_is_known_dead(mock_accessible)
        assert result is True

    def test_object_is_known_dead_in_cache_as_alive(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.object_is_known_dead with object marked as alive."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        AXObject.KNOWN_DEAD[hash(mock_accessible)] = False

        result = AXObject.object_is_known_dead(mock_accessible)
        assert result is False

    def test_set_known_dead_status_with_none_object(self, monkeypatch, mock_orca_dependencies):
        """Test AXObject._set_known_dead_status with None object."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        # Should not raise exception
        AXObject._set_known_dead_status(None, True)

    def test_set_known_dead_status_same_status(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject._set_known_dead_status with same status."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        AXObject.KNOWN_DEAD[hash(mock_accessible)] = True
        AXObject._set_known_dead_status(mock_accessible, True)
        assert AXObject.KNOWN_DEAD[hash(mock_accessible)] is True

    def test_set_known_dead_status_mark_as_dead(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject._set_known_dead_status marking object as dead."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        AXObject.KNOWN_DEAD.clear()
        AXObject._set_known_dead_status(mock_accessible, True)
        assert AXObject.KNOWN_DEAD[hash(mock_accessible)] is True
        mock_orca_dependencies["debug"].print_message.assert_called()

    def test_set_known_dead_status_resurrect_object(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject._set_known_dead_status resurrecting previously dead object."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        AXObject.KNOWN_DEAD[hash(mock_accessible)] = True
        AXObject._set_known_dead_status(mock_accessible, False)
        assert AXObject.KNOWN_DEAD[hash(mock_accessible)] is False
        mock_orca_dependencies["debug"].print_tokens.assert_called()

    @pytest.mark.parametrize(
        "error_string, expected_msg_part",
        [
            pytest.param(
                "accessible/123 does not exist", "object no longer exists", id="object_not_exist"
            ),
            pytest.param(
                "The application no longer exists", "app no longer exists", id="app_not_exist"
            ),
            pytest.param("Some other error", "Some other error", id="other_error"),
        ],
    )
    def test_handle_error(
        self, monkeypatch, mock_accessible, error_string, expected_msg_part, mock_orca_dependencies
    ):
        """Test AXObject.handle_error with different error types."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        error = Exception(error_string)
        msg = f"AXObject: Error calling method: {error_string}"

        AXObject.handle_error(mock_accessible, error, msg)

        # Verify debug.print_message was called
        mock_orca_dependencies["debug"].print_message.assert_called_once()
        call_args = mock_orca_dependencies["debug"].print_message.call_args[0]
        assert expected_msg_part in call_args[1]

    def test_get_path_with_valid_object(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.get_path with valid object."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_parent = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)

        def mock_get_index(obj):
            if obj == mock_accessible:
                return 2
            if obj == mock_parent:
                return 1
            return 0

        monkeypatch.setattr(Atspi.Accessible, "get_index_in_parent", mock_get_index)

        def mock_get_parent_checked(obj):
            if obj == mock_accessible:
                return mock_parent
            return None

        monkeypatch.setattr(AXObject, "get_parent_checked", mock_get_parent_checked)

        result = AXObject.get_path(mock_accessible)
        assert result == [1, 2]

    def test_get_path_with_glib_error(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.get_path handles GLib.GError."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        def raise_glib_error(obj):
            raise GLib.GError("Test path error")

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(Atspi.Accessible, "get_index_in_parent", raise_glib_error)
        monkeypatch.setattr(AXObject, "handle_error", Mock())

        result = AXObject.get_path(mock_accessible)
        assert not result
        AXObject.handle_error.assert_called_once()

    def test_get_index_in_parent_with_valid_index(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_index_in_parent with valid index."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(Atspi.Accessible, "get_index_in_parent", lambda obj: 3)

        result = AXObject.get_index_in_parent(mock_accessible)
        assert result == 3

    def test_get_index_in_parent_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_index_in_parent handles GLib.GError."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        def raise_glib_error(obj):
            raise GLib.GError("Test index error")

        monkeypatch.setattr(Atspi.Accessible, "get_index_in_parent", raise_glib_error)
        monkeypatch.setattr(AXObject, "handle_error", Mock())

        result = AXObject.get_index_in_parent(mock_accessible)
        assert result == -1
        AXObject.handle_error.assert_called_once()

    def test_get_parent_with_valid_parent(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_parent with valid parent."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_parent = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(Atspi.Accessible, "get_parent", lambda obj: mock_parent)

        result = AXObject.get_parent(mock_accessible)
        assert result == mock_parent

    def test_get_parent_with_glib_error(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.get_parent handles GLib.GError."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        def raise_glib_error(obj):
            raise GLib.GError("Test parent error")

        monkeypatch.setattr(Atspi.Accessible, "get_parent", raise_glib_error)
        monkeypatch.setattr(AXObject, "handle_error", Mock())

        result = AXObject.get_parent(mock_accessible)
        assert result is None
        AXObject.handle_error.assert_called_once()

    def test_get_role_with_valid_object(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.get_role with valid object."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(Atspi.Accessible, "get_role", lambda obj: Atspi.Role.BUTTON)
        monkeypatch.setattr(AXObject, "_set_known_dead_status", Mock())

        result = AXObject.get_role(mock_accessible)
        assert result == Atspi.Role.BUTTON
        AXObject._set_known_dead_status.assert_called_once_with(mock_accessible, False)

    def test_get_role_with_invalid_object(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_role with invalid object."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: False)

        result = AXObject.get_role(mock_accessible)
        assert result == Atspi.Role.INVALID

    def test_get_role_with_glib_error(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.get_role handles GLib.GError."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        def raise_glib_error(obj):
            raise GLib.GError("Test role error")

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(Atspi.Accessible, "get_role", raise_glib_error)
        monkeypatch.setattr(AXObject, "handle_error", Mock())

        result = AXObject.get_role(mock_accessible)
        assert result == Atspi.Role.INVALID
        AXObject.handle_error.assert_called_once()

    def test_get_role_name_with_valid_object_not_localized(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_role_name with valid object not localized."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(Atspi.Accessible, "get_role_name", lambda obj: "button")

        result = AXObject.get_role_name(mock_accessible, localized=False)
        assert result == "button"

    def test_get_role_name_with_valid_object_localized(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_role_name with valid object localized."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(Atspi.Accessible, "get_localized_role_name", lambda obj: "botón")

        result = AXObject.get_role_name(mock_accessible, localized=True)
        assert result == "botón"

    def test_get_role_name_with_invalid_object(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_role_name with invalid object."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: False)

        result = AXObject.get_role_name(mock_accessible)
        assert result == ""

    def test_get_role_name_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_role_name handles GLib.GError."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        def raise_glib_error(obj):
            raise GLib.GError("Test role name error")

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(Atspi.Accessible, "get_role_name", raise_glib_error)
        monkeypatch.setattr(AXObject, "handle_error", Mock())

        result = AXObject.get_role_name(mock_accessible)
        assert result == ""
        AXObject.handle_error.assert_called_once()

    def test_get_role_description_with_invalid_object(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_role_description with invalid object."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: False)

        result = AXObject.get_role_description(mock_accessible)
        assert result == ""

    def test_get_role_description_with_role_description(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_role_description with role description attribute."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(
            AXObject, "get_attributes_dict", lambda obj: {"roledescription": "custom button"}
        )

        result = AXObject.get_role_description(mock_accessible)
        assert result == "custom button"

    def test_get_role_description_with_braille_description(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_role_description with braille role description."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(
            AXObject,
            "get_attributes_dict",
            lambda obj: {"roledescription": "custom button", "brailleroledescription": "btn"},
        )

        result = AXObject.get_role_description(mock_accessible, is_braille=True)
        assert result == "btn"

    def test_get_role_description_braille_fallback(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_role_description braille falls back to regular description."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(
            AXObject, "get_attributes_dict", lambda obj: {"roledescription": "custom button"}
        )

        result = AXObject.get_role_description(mock_accessible, is_braille=True)
        assert result == "custom button"

    def test_get_accessible_id_with_invalid_object(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_accessible_id with invalid object."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: False)

        result = AXObject.get_accessible_id(mock_accessible)
        assert result == ""

    def test_get_accessible_id_with_valid_object(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_accessible_id with valid object."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(Atspi.Accessible, "get_accessible_id", lambda obj: "button-123")

        result = AXObject.get_accessible_id(mock_accessible)
        assert result == "button-123"

    def test_get_accessible_id_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_accessible_id handles GLib.GError."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        def raise_glib_error(obj):
            raise GLib.GError("Test accessible id error")

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(Atspi.Accessible, "get_accessible_id", raise_glib_error)
        monkeypatch.setattr(AXObject, "handle_error", Mock())

        result = AXObject.get_accessible_id(mock_accessible)
        assert result == ""
        AXObject.handle_error.assert_called_once()

    def test_get_name_with_invalid_object(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_name with invalid object."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: False)

        result = AXObject.get_name(mock_accessible)
        assert result == ""

    def test_get_name_with_valid_object(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.get_name with valid object."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(Atspi.Accessible, "get_name", lambda obj: "Submit")

        result = AXObject.get_name(mock_accessible)
        assert result == "Submit"

    def test_get_name_with_glib_error(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.get_name handles GLib.GError."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        def raise_glib_error(obj):
            raise GLib.GError("Test name error")

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(Atspi.Accessible, "get_name", raise_glib_error)
        monkeypatch.setattr(AXObject, "handle_error", Mock())

        result = AXObject.get_name(mock_accessible)
        assert result == ""
        AXObject.handle_error.assert_called_once()

    def test_has_same_non_empty_name_both_empty(self, monkeypatch, mock_orca_dependencies):
        """Test AXObject.has_same_non_empty_name with both objects having empty names."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_obj1 = Mock(spec=Atspi.Accessible)
        mock_obj2 = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(AXObject, "get_name", lambda obj: "")

        result = AXObject.has_same_non_empty_name(mock_obj1, mock_obj2)
        assert result is False

    def test_has_same_non_empty_name_same_non_empty(self, monkeypatch, mock_orca_dependencies):
        """Test AXObject.has_same_non_empty_name with same non-empty names."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_obj1 = Mock(spec=Atspi.Accessible)
        mock_obj2 = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(AXObject, "get_name", lambda obj: "Submit")

        result = AXObject.has_same_non_empty_name(mock_obj1, mock_obj2)
        assert result is True

    def test_has_same_non_empty_name_different_names(self, monkeypatch, mock_orca_dependencies):
        """Test AXObject.has_same_non_empty_name with different names."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_obj1 = Mock(spec=Atspi.Accessible)
        mock_obj2 = Mock(spec=Atspi.Accessible)

        def mock_get_name(obj):
            if obj == mock_obj1:
                return "Submit"
            return "Cancel"

        monkeypatch.setattr(AXObject, "get_name", mock_get_name)

        result = AXObject.has_same_non_empty_name(mock_obj1, mock_obj2)
        assert result is False

    def test_get_state_set_with_invalid_object(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_state_set with invalid object."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: False)

        result = AXObject.get_state_set(mock_accessible)
        assert isinstance(result, type(Atspi.StateSet()))

    def test_get_state_set_with_valid_object(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_state_set with valid object."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_state_set = Mock()

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(Atspi.Accessible, "get_state_set", lambda obj: mock_state_set)
        monkeypatch.setattr(AXObject, "_set_known_dead_status", Mock())

        result = AXObject.get_state_set(mock_accessible)
        assert result == mock_state_set
        AXObject._set_known_dead_status.assert_called_once_with(mock_accessible, False)

    def test_get_state_set_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_state_set handles GLib.GError."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        def raise_glib_error(obj):
            raise GLib.GError("Test state set error")

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(Atspi.Accessible, "get_state_set", raise_glib_error)
        monkeypatch.setattr(AXObject, "handle_error", Mock())

        result = AXObject.get_state_set(mock_accessible)
        assert isinstance(result, type(Atspi.StateSet()))
        AXObject.handle_error.assert_called_once()

    def test_has_state_with_invalid_object(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.has_state with invalid object."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: False)

        result = AXObject.has_state(mock_accessible, Atspi.StateType.FOCUSED)
        assert result is False

    def test_has_state_with_valid_object(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.has_state with valid object."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_state_set = Mock()
        mock_state_set.contains.return_value = True

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "get_state_set", lambda obj: mock_state_set)

        result = AXObject.has_state(mock_accessible, Atspi.StateType.FOCUSED)
        assert result is True
        mock_state_set.contains.assert_called_once_with(Atspi.StateType.FOCUSED)

    def test_clear_cache_with_none_object(self, monkeypatch, mock_orca_dependencies):
        """Test AXObject.clear_cache with None object."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        # Should return early without errors
        AXObject.clear_cache(None)

    def test_clear_cache_non_recursive(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.clear_cache non-recursive."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(Atspi.Accessible, "clear_cache_single", Mock())

        AXObject.clear_cache(mock_accessible, recursive=False, reason="test")

        sys.modules["gi.repository"].Atspi.Accessible.clear_cache_single.assert_called_once_with(
            mock_accessible
        )
        mock_orca_dependencies["debug"].print_tokens.assert_called()

    def test_clear_cache_non_recursive_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.clear_cache non-recursive handles GLib.GError."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        def raise_glib_error(obj):
            raise GLib.GError("Test clear cache error")

        monkeypatch.setattr(Atspi.Accessible, "clear_cache_single", raise_glib_error)

        AXObject.clear_cache(mock_accessible, recursive=False)

        mock_orca_dependencies["debug"].print_message.assert_called()

    def test_clear_cache_recursive(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.clear_cache recursive."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(Atspi.Accessible, "clear_cache", Mock())

        AXObject.clear_cache(mock_accessible, recursive=True)

        sys.modules["gi.repository"].Atspi.Accessible.clear_cache.assert_called_once_with(
            mock_accessible
        )

    def test_clear_cache_recursive_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.clear_cache recursive handles GLib.GError."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        def raise_glib_error(obj):
            raise GLib.GError("Test clear cache recursive error")

        monkeypatch.setattr(Atspi.Accessible, "clear_cache", raise_glib_error)

        AXObject.clear_cache(mock_accessible, recursive=True)

        mock_orca_dependencies["debug"].print_message.assert_called()

    def test_get_attributes_dict_with_invalid_object(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_attributes_dict with invalid object."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: False)

        result = AXObject.get_attributes_dict(mock_accessible)
        assert result == {}

    def test_get_attributes_dict_with_cache_hit(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_attributes_dict with cache hit."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        cached_attrs = {"id": "button1", "class": "primary"}

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        AXObject.OBJECT_ATTRIBUTES[hash(mock_accessible)] = cached_attrs

        result = AXObject.get_attributes_dict(mock_accessible, use_cache=True)
        assert result == cached_attrs

    def test_get_attributes_dict_no_cache_valid_attributes(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_attributes_dict without cache with valid attributes."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        attrs = {"id": "button2", "class": "secondary"}

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(Atspi.Accessible, "get_attributes", lambda obj: attrs)

        AXObject.OBJECT_ATTRIBUTES.clear()

        result = AXObject.get_attributes_dict(mock_accessible, use_cache=False)
        assert result == attrs
        assert AXObject.OBJECT_ATTRIBUTES[hash(mock_accessible)] == attrs

    def test_get_attributes_dict_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_attributes_dict handles GLib.GError."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        def raise_glib_error(obj):
            raise GLib.GError("Test attributes error")

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(Atspi.Accessible, "get_attributes", raise_glib_error)
        monkeypatch.setattr(AXObject, "handle_error", Mock())

        AXObject.OBJECT_ATTRIBUTES.clear()

        result = AXObject.get_attributes_dict(mock_accessible, use_cache=False)
        assert result == {}
        AXObject.handle_error.assert_called_once()

    def test_get_attributes_dict_with_none_attributes(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_attributes_dict with None attributes."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(Atspi.Accessible, "get_attributes", lambda obj: None)

        AXObject.OBJECT_ATTRIBUTES.clear()

        result = AXObject.get_attributes_dict(mock_accessible, use_cache=False)
        assert result == {}

    def test_get_attribute_with_invalid_object(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_attribute with invalid object."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: False)

        result = AXObject.get_attribute(mock_accessible, "id")
        assert result == ""

    def test_get_attribute_with_existing_attribute(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_attribute with existing attribute."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        attrs = {"id": "button1", "class": "primary"}

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "get_attributes_dict", lambda obj, use_cache: attrs)

        result = AXObject.get_attribute(mock_accessible, "id")
        assert result == "button1"

    def test_get_attribute_with_missing_attribute(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_attribute with missing attribute."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        attrs = {"id": "button1"}

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "get_attributes_dict", lambda obj, use_cache: attrs)

        result = AXObject.get_attribute(mock_accessible, "class")
        assert result == ""

    def test_get_n_actions_with_unsupported_object(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_n_actions with object that doesn't support actions."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_action", lambda obj: False)

        result = AXObject.get_n_actions(mock_accessible)
        assert result == 0

    def test_get_n_actions_with_supported_object(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_n_actions with object that supports actions."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_action", lambda obj: True)
        monkeypatch.setattr(Atspi.Action, "get_n_actions", lambda obj: 3)

        result = AXObject.get_n_actions(mock_accessible)
        assert result == 3

    def test_get_n_actions_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_n_actions handles GLib.GError."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        def raise_glib_error(obj):
            raise GLib.GError("Test n actions error")

        monkeypatch.setattr(AXObject, "supports_action", lambda obj: True)
        monkeypatch.setattr(Atspi.Action, "get_n_actions", raise_glib_error)
        monkeypatch.setattr(AXObject, "handle_error", Mock())

        result = AXObject.get_n_actions(mock_accessible)
        assert result == 0
        AXObject.handle_error.assert_called_once()

    @pytest.mark.parametrize(
        "action_name, expected_result",
        [
            pytest.param("", "", id="empty_string"),
            pytest.param("click", "click", id="simple_name"),
            pytest.param("clickButton", "click-button", id="camel_case"),
            pytest.param("onClick", "on-click", id="mixed_case"),
            pytest.param("click!button", "click-button", id="with_punctuation"),
            pytest.param("click_button", "click-button", id="with_underscore"),
            pytest.param("CLICK", "click", id="uppercase"),
        ],
    )
    def test_normalize_action_name(self, action_name, expected_result, mock_orca_dependencies):
        """Test AXObject._normalize_action_name with various inputs."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        result = AXObject._normalize_action_name(action_name)
        assert result == expected_result

    def test_get_action_name_invalid_index_negative(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_action_name with negative index."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "get_n_actions", lambda obj: 2)

        result = AXObject.get_action_name(mock_accessible, -1)
        assert result == ""

    def test_get_action_name_invalid_index_too_high(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_action_name with index too high."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "get_n_actions", lambda obj: 2)

        result = AXObject.get_action_name(mock_accessible, 2)
        assert result == ""

    def test_get_action_name_valid_index(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_action_name with valid index."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "get_n_actions", lambda obj: 2)
        monkeypatch.setattr(Atspi.Action, "get_action_name", lambda obj, i: "clickButton")
        monkeypatch.setattr(AXObject, "_normalize_action_name", lambda name: "click-button")

        result = AXObject.get_action_name(mock_accessible, 1)
        assert result == "click-button"

    def test_get_action_name_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_action_name handles GLib.GError."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        def raise_glib_error(obj, i):
            raise GLib.GError("Test action name error")

        monkeypatch.setattr(AXObject, "get_n_actions", lambda obj: 2)
        monkeypatch.setattr(Atspi.Action, "get_action_name", raise_glib_error)
        monkeypatch.setattr(AXObject, "handle_error", Mock())

        result = AXObject.get_action_name(mock_accessible, 0)
        assert result == ""
        AXObject.handle_error.assert_called_once()

    def test_get_action_names_no_actions(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_action_names with no actions."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "get_n_actions", lambda obj: 0)

        result = AXObject.get_action_names(mock_accessible)
        assert not result

    def test_get_action_names_with_actions(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_action_names with multiple actions."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "get_n_actions", lambda obj: 3)

        def mock_get_action_name(obj, i):
            names = ["click", "", "press"]
            return names[i]

        monkeypatch.setattr(AXObject, "get_action_name", mock_get_action_name)

        result = AXObject.get_action_names(mock_accessible)
        assert result == ["click", "press"]

    def test_get_action_description_invalid_index_negative(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_action_description with negative index."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "get_n_actions", lambda obj: 2)

        result = AXObject.get_action_description(mock_accessible, -1)
        assert result == ""

    def test_get_action_description_invalid_index_too_high(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_action_description with index too high."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "get_n_actions", lambda obj: 2)

        result = AXObject.get_action_description(mock_accessible, 3)
        assert result == ""

    def test_get_action_description_valid_index(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_action_description with valid index."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "get_n_actions", lambda obj: 2)
        monkeypatch.setattr(
            Atspi.Action, "get_action_description", lambda obj, i: "Clicks the button"
        )

        result = AXObject.get_action_description(mock_accessible, 0)
        assert result == "Clicks the button"

    def test_get_action_description_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_action_description handles GLib.GError."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        def raise_glib_error(obj, i):
            raise GLib.GError("Test action description error")

        monkeypatch.setattr(AXObject, "get_n_actions", lambda obj: 2)
        monkeypatch.setattr(Atspi.Action, "get_action_description", raise_glib_error)
        monkeypatch.setattr(AXObject, "handle_error", Mock())

        result = AXObject.get_action_description(mock_accessible, 1)
        assert result == ""
        AXObject.handle_error.assert_called_once()

    def test_get_action_key_binding_invalid_index_negative(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_action_key_binding with negative index."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "get_n_actions", lambda obj: 2)

        result = AXObject.get_action_key_binding(mock_accessible, -1)
        assert result == ""

    def test_get_action_key_binding_invalid_index_too_high(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_action_key_binding with index too high."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "get_n_actions", lambda obj: 2)

        result = AXObject.get_action_key_binding(mock_accessible, 2)
        assert result == ""

    def test_get_action_key_binding_valid_index(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_action_key_binding with valid index."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "get_n_actions", lambda obj: 2)
        monkeypatch.setattr(Atspi.Action, "get_key_binding", lambda obj, i: "Ctrl+Enter")

        result = AXObject.get_action_key_binding(mock_accessible, 0)
        assert result == "Ctrl+Enter"

    def test_get_action_key_binding_with_void_symbol(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_action_key_binding with GTK4 VoidSymbol."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "get_n_actions", lambda obj: 2)
        monkeypatch.setattr(Atspi.Action, "get_key_binding", lambda obj, i: "<VoidSymbol>")

        result = AXObject.get_action_key_binding(mock_accessible, 0)
        assert result == ""

    def test_get_action_key_binding_with_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_action_key_binding handles GLib.GError."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        def raise_glib_error(obj, i):
            raise GLib.GError("Test key binding error")

        monkeypatch.setattr(AXObject, "get_n_actions", lambda obj: 2)
        monkeypatch.setattr(Atspi.Action, "get_key_binding", raise_glib_error)
        monkeypatch.setattr(AXObject, "handle_error", Mock())

        result = AXObject.get_action_key_binding(mock_accessible, 1)
        assert result == ""
        AXObject.handle_error.assert_called_once()

    def test_get_label_for_key_sequence_simple(self, monkeypatch, mock_orca_dependencies):
        """Test AXObject._get_label_for_key_sequence with empty string."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        result = AXObject._get_label_for_key_sequence("")
        assert result == ""

    def test_get_accelerator_with_invalid_object(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_accelerator with invalid object."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: False)

        result = AXObject.get_accelerator(mock_accessible)
        assert result == ""

    def test_get_accelerator_invalid_object(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_accelerator with invalid object."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: False)

        result = AXObject.get_accelerator(mock_accessible)
        assert result == ""

    def test_get_mnemonic_no_attributes(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.get_mnemonic with no keyshortcuts attribute."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "get_attributes_dict", lambda obj: {})
        monkeypatch.setattr(AXObject, "_find_first_action_with_keybinding", lambda obj: -1)

        result = AXObject.get_mnemonic(mock_accessible)
        assert result == ""

    def test_get_mnemonic_single_letter_shortcut(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_mnemonic with single letter keyshortcut."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "get_attributes_dict", lambda obj: {"keyshortcuts": "F"})
        monkeypatch.setattr(AXObject, "_get_label_for_key_sequence", lambda seq: "F")

        result = AXObject.get_mnemonic(mock_accessible)
        assert result == "F"

    def test_get_mnemonic_multiple_letter_shortcut(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_mnemonic with multi-letter keyshortcut."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "get_attributes_dict", lambda obj: {"keyshortcuts": "Ctrl+F"})
        monkeypatch.setattr(AXObject, "_get_label_for_key_sequence", lambda seq: "Ctrl+F")
        monkeypatch.setattr(AXObject, "_find_first_action_with_keybinding", lambda obj: -1)

        result = AXObject.get_mnemonic(mock_accessible)
        assert result == ""

    def test_get_mnemonic_from_action_keybinding(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_mnemonic from action key binding."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "get_attributes_dict", lambda obj: {})
        monkeypatch.setattr(AXObject, "_find_first_action_with_keybinding", lambda obj: 0)
        monkeypatch.setattr(AXObject, "get_action_key_binding", lambda obj, idx: "Alt+F;Alt+F")
        monkeypatch.setattr(AXObject, "_get_label_for_key_sequence", lambda seq: "Alt+F")

        result = AXObject.get_mnemonic(mock_accessible)
        assert result == "Alt+F"

    def test_get_mnemonic_with_ctrl_in_result(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_mnemonic with Ctrl in result."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "get_attributes_dict", lambda obj: {})
        monkeypatch.setattr(AXObject, "_find_first_action_with_keybinding", lambda obj: 0)
        monkeypatch.setattr(AXObject, "get_action_key_binding", lambda obj, idx: "Ctrl+F;Ctrl+F")
        monkeypatch.setattr(AXObject, "_get_label_for_key_sequence", lambda seq: "Ctrl+F")

        result = AXObject.get_mnemonic(mock_accessible)
        assert result == ""

    def test_get_mnemonic_with_space(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.get_mnemonic with space key."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "get_attributes_dict", lambda obj: {})
        monkeypatch.setattr(AXObject, "_find_first_action_with_keybinding", lambda obj: 0)
        monkeypatch.setattr(AXObject, "get_action_key_binding", lambda obj, idx: "space;space")
        monkeypatch.setattr(AXObject, "_get_label_for_key_sequence", lambda seq: "space")

        result = AXObject.get_mnemonic(mock_accessible)
        assert result == ""

    def test_find_first_action_with_keybinding_found(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject._find_first_action_with_keybinding found action."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "get_n_actions", lambda obj: 2)

        def mock_get_action_key_binding(obj, index):
            if index == 0:
                return ""
            return "Alt+F"

        monkeypatch.setattr(AXObject, "get_action_key_binding", mock_get_action_key_binding)

        result = AXObject._find_first_action_with_keybinding(mock_accessible)
        assert result == 1

    def test_find_first_action_with_keybinding_not_found(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject._find_first_action_with_keybinding not found."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "get_n_actions", lambda obj: 2)
        monkeypatch.setattr(AXObject, "get_action_key_binding", lambda obj, idx: "")

        result = AXObject._find_first_action_with_keybinding(mock_accessible)
        assert result == -1

    def test_has_action_true(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.has_action returns True."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "get_action_index", lambda obj, name: 0)

        result = AXObject.has_action(mock_accessible, "click")
        assert result is True

    def test_has_action_false(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.has_action returns False."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "get_action_index", lambda obj, name: -1)

        result = AXObject.has_action(mock_accessible, "click")
        assert result is False

    def test_get_action_index_found(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.get_action_index found action."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "_normalize_action_name", lambda name: name.lower())
        monkeypatch.setattr(AXObject, "get_n_actions", lambda obj: 2)

        def mock_get_action_name(obj, index):
            if index == 0:
                return "press"
            return "click"

        monkeypatch.setattr(AXObject, "get_action_name", mock_get_action_name)

        result = AXObject.get_action_index(mock_accessible, "click")
        assert result == 1

    def test_get_action_index_not_found(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.get_action_index not found."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "_normalize_action_name", lambda name: name.lower())
        monkeypatch.setattr(AXObject, "get_n_actions", lambda obj: 2)
        monkeypatch.setattr(AXObject, "get_action_name", lambda obj, idx: "press")

        result = AXObject.get_action_index(mock_accessible, "click")
        assert result == -1

    def test_do_action_success(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.do_action success."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "get_n_actions", lambda obj: 2)

        sys.modules["gi.repository"].Atspi.Action.do_action = Mock(return_value=True)

        result = AXObject.do_action(mock_accessible, 0)
        assert result is True

    def test_do_action_invalid_index(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.do_action invalid index."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "get_n_actions", lambda obj: 2)

        result = AXObject.do_action(mock_accessible, 5)
        assert result is False

    def test_do_action_glib_error(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.do_action handles GLib.GError."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "get_n_actions", lambda obj: 2)
        monkeypatch.setattr(AXObject, "handle_error", Mock())

        sys.modules["gi.repository"].Atspi.Action.do_action = Mock(
            side_effect=sys.modules["gi.repository"].GLib.GError("Test error")
        )

        result = AXObject.do_action(mock_accessible, 0)
        assert result is False

    def test_do_named_action_success(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.do_named_action success."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "get_action_index", lambda obj, name: 0)
        monkeypatch.setattr(AXObject, "do_action", lambda obj, idx: True)

        result = AXObject.do_named_action(mock_accessible, "click")
        assert result is True

    def test_do_named_action_not_found(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.do_named_action action not found."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "get_action_index", lambda obj, name: -1)
        debug_mock = Mock()
        debug_mock.print_tokens = Mock()
        sys.modules["orca.debug"] = debug_mock

        result = AXObject.do_named_action(mock_accessible, "click")
        assert result is False

    def test_grab_focus_no_component_support(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.grab_focus without component support."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "supports_component", lambda obj: False)

        result = AXObject.grab_focus(mock_accessible)
        assert result is False

    def test_grab_focus_basic_success(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.grab_focus basic success path."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "supports_component", lambda obj: True)

        def mock_grab_focus(obj):
            from orca import debug

            debug.LEVEL_INFO = 1
            debug.debugLevel = 2  # Skip debug logic
            return True

        monkeypatch.setattr("orca.ax_object.Atspi.Component.grab_focus", mock_grab_focus)

        result = AXObject.grab_focus(mock_accessible)
        assert result is True

    def test_is_ancestor_invalid_obj(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.is_ancestor with invalid obj."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: obj == mock_accessible)

        result = AXObject.is_ancestor(None, mock_accessible)
        assert result is False

    def test_is_ancestor_invalid_ancestor(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.is_ancestor with invalid ancestor."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: obj == mock_accessible)

        result = AXObject.is_ancestor(mock_accessible, None)
        assert result is False

    def test_is_ancestor_same_object_inclusive(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.is_ancestor with same object and inclusive=True."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)

        result = AXObject.is_ancestor(mock_accessible, mock_accessible, inclusive=True)
        assert result is True

    def test_is_ancestor_same_object_not_inclusive(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.is_ancestor with same object and inclusive=False."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "find_ancestor", lambda obj, pred: None)

        result = AXObject.is_ancestor(mock_accessible, mock_accessible, inclusive=False)
        assert result is False

    def test_is_ancestor_found(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.is_ancestor when ancestor is found."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_ancestor = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "find_ancestor", lambda obj, pred: mock_ancestor)

        result = AXObject.is_ancestor(mock_accessible, mock_ancestor)
        assert result is True

    def test_is_ancestor_not_found(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.is_ancestor when ancestor is not found."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_ancestor = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "find_ancestor", lambda obj, pred: None)

        result = AXObject.is_ancestor(mock_accessible, mock_ancestor)
        assert result is False

    def test_get_child_invalid_obj(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.get_child with invalid obj."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: False)

        result = AXObject.get_child(mock_accessible, 0)
        assert result is None

    def test_get_child_no_children(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.get_child with no children."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "get_child_count", lambda obj: 0)

        result = AXObject.get_child(mock_accessible, 0)
        assert result is None

    def test_get_child_negative_index(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.get_child with -1 index (last child)."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_child = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "get_child_count", lambda obj: 3)

        def mock_get_child_at_index(obj, index):
            if index == 2:  # 3-1 for last child
                return mock_child
            return None

        sys.modules["gi.repository"].Atspi.Accessible.get_child_at_index = mock_get_child_at_index

        result = AXObject.get_child(mock_accessible, -1)
        assert result == mock_child

    def test_get_child_valid_index(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.get_child with valid index."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_child = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "get_child_count", lambda obj: 3)
        sys.modules["gi.repository"].Atspi.Accessible.get_child_at_index = (
            lambda obj, idx: mock_child if idx == 1 else None
        )

        result = AXObject.get_child(mock_accessible, 1)
        assert result == mock_child

    def test_find_descendant_invalid_obj(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject._find_descendant with invalid obj."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: False)

        def always_true(obj):
            return True

        result = AXObject._find_descendant(mock_accessible, always_true)
        assert result is None

    def test_find_descendant_no_children(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject._find_descendant with no children."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "get_child_count", lambda obj: 0)

        def always_true(obj):
            return True

        result = AXObject._find_descendant(mock_accessible, always_true)
        assert result is None

    def test_find_descendant_found_direct_child(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject._find_descendant with direct child match."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_child = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "get_child_count", lambda obj: 1)
        monkeypatch.setattr(AXObject, "get_child_checked", lambda obj, idx: mock_child)

        def match_child(obj):
            return obj == mock_child

        result = AXObject._find_descendant(mock_accessible, match_child)
        assert result == mock_child

    def test_find_descendant_found_in_grandchild(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject._find_descendant with grandchild match."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_child = Mock(spec=Atspi.Accessible)
        mock_grandchild = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)

        def mock_get_child_count(obj):
            if obj == mock_accessible:
                return 1
            if obj == mock_child:
                return 1
            return 0

        def mock_get_child_checked(obj, idx):
            if obj == mock_accessible and idx == 0:
                return mock_child
            if obj == mock_child and idx == 0:
                return mock_grandchild
            return None

        monkeypatch.setattr(AXObject, "get_child_count", mock_get_child_count)
        monkeypatch.setattr(AXObject, "get_child_checked", mock_get_child_checked)

        def match_grandchild(obj):
            return obj == mock_grandchild

        result = AXObject._find_descendant(mock_accessible, match_grandchild)
        assert result == mock_grandchild

    def test_find_descendant_not_found(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject._find_descendant when predicate never matches."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "get_child_count", lambda obj: 0)

        def never_match(obj):
            return False

        result = AXObject._find_descendant(mock_accessible, never_match)
        assert result is None

    def test_find_descendant_with_timing(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.find_descendant includes timing."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_child = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "_find_descendant", lambda obj, pred: mock_child)

        debug_mock = Mock()
        debug_mock.print_tokens = Mock()
        sys.modules["orca.debug"] = debug_mock

        def always_true(obj):
            return True

        result = AXObject.find_descendant(mock_accessible, always_true)
        assert result == mock_child

    def test_find_deepest_descendant_invalid_obj(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.find_deepest_descendant with invalid obj."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: False)

        result = AXObject.find_deepest_descendant(mock_accessible)
        assert result is None

    def test_find_deepest_descendant_no_children(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.find_deepest_descendant with no children."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "get_child_count", lambda obj: 0)
        monkeypatch.setattr(AXObject, "get_child", lambda obj, idx: None)

        result = AXObject.find_deepest_descendant(mock_accessible)
        assert result == mock_accessible

    def test_find_deepest_descendant_with_children(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.find_deepest_descendant with nested children."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_child = Mock(spec=Atspi.Accessible)
        mock_grandchild = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)

        def mock_get_child_count(obj):
            if obj == mock_accessible:
                return 2
            if obj == mock_child:
                return 1
            return 0

        def mock_get_child(obj, idx):
            if obj == mock_accessible and idx == 1:  # Last child
                return mock_child
            if obj == mock_child and idx == 0:
                return mock_grandchild
            return None

        monkeypatch.setattr(AXObject, "get_child_count", mock_get_child_count)
        monkeypatch.setattr(AXObject, "get_child", mock_get_child)

        result = AXObject.find_deepest_descendant(mock_accessible)
        assert result == mock_grandchild

    def test_find_all_descendants_invalid_obj(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject._find_all_descendants with invalid obj."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: False)

        matches = []
        AXObject._find_all_descendants(mock_accessible, None, None, matches)
        assert not matches

    def test_find_all_descendants_with_include_filter(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject._find_all_descendants with include filter."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_child1 = Mock(spec=Atspi.Accessible)
        mock_child2 = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)

        def mock_get_child_count(obj):
            if obj == mock_accessible:
                return 2
            return 0

        def mock_get_child(obj, idx):
            if obj == mock_accessible:
                if idx == 0:
                    return mock_child1
                if idx == 1:
                    return mock_child2
            return None

        monkeypatch.setattr(AXObject, "get_child_count", mock_get_child_count)
        monkeypatch.setattr(AXObject, "get_child", mock_get_child)

        def include_child1(obj):
            return obj == mock_child1

        matches = []
        AXObject._find_all_descendants(mock_accessible, include_child1, None, matches)
        assert matches == [mock_child1]

    def test_find_all_descendants_with_exclude_filter(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject._find_all_descendants with exclude filter."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_child1 = Mock(spec=Atspi.Accessible)
        mock_child2 = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)

        def mock_get_child_count(obj):
            if obj == mock_accessible:
                return 2
            return 0

        def mock_get_child(obj, idx):
            if obj == mock_accessible:
                if idx == 0:
                    return mock_child1
                if idx == 1:
                    return mock_child2
            return None

        monkeypatch.setattr(AXObject, "get_child_count", mock_get_child_count)
        monkeypatch.setattr(AXObject, "get_child", mock_get_child)

        def include_all(obj):
            return True

        def exclude_child1(obj):
            return obj == mock_child1

        matches = []
        AXObject._find_all_descendants(mock_accessible, include_all, exclude_child1, matches)
        assert matches == [mock_child2]

    def test_find_all_descendants_public_method(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.find_all_descendants public method."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_child = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(
            AXObject,
            "_find_all_descendants",
            lambda root, incl, excl, matches: matches.append(mock_child),
        )

        debug_mock = Mock()
        debug_mock.print_message = Mock()
        sys.modules["orca.debug"] = debug_mock

        result = AXObject.find_all_descendants(mock_accessible)
        assert result == [mock_child]

    def test_get_role_name_invalid_obj(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.get_role_name with invalid obj."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: False)

        result = AXObject.get_role_name(mock_accessible)
        assert result == ""

    def test_get_role_name_non_localized(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_role_name non-localized."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)

        sys.modules["gi.repository"].Atspi.Accessible.get_role_name = Mock(return_value="button")

        result = AXObject.get_role_name(mock_accessible, localized=False)
        assert result == "button"

        sys.modules["gi.repository"].Atspi.Accessible.get_localized_role_name = Mock(
            return_value="botón"
        )

        result = AXObject.get_role_name(mock_accessible, localized=True)
        assert result == "botón"

    def test_get_role_name_glib_error(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.get_role_name handles GLib.GError."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "handle_error", Mock())

        sys.modules["gi.repository"].Atspi.Accessible.get_role_name = Mock(
            side_effect=GLib.GError("Test error")
        )

        result = AXObject.get_role_name(mock_accessible)
        assert result == ""

    def test_get_role_description_invalid_obj(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_role_description with invalid obj."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: False)

        result = AXObject.get_role_description(mock_accessible)
        assert result == ""

    def test_get_role_description_no_description(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_role_description with no description."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "get_attributes_dict", lambda obj: {})

        result = AXObject.get_role_description(mock_accessible)
        assert result == ""

    def test_get_role_description_with_description(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_role_description with description."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(
            AXObject, "get_attributes_dict", lambda obj: {"roledescription": "custom button"}
        )

        result = AXObject.get_role_description(mock_accessible)
        assert result == "custom button"

    def test_get_role_description_braille(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_role_description for braille."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(
            AXObject,
            "get_attributes_dict",
            lambda obj: {"roledescription": "custom button", "brailleroledescription": "btn"},
        )

        result = AXObject.get_role_description(mock_accessible, is_braille=True)
        assert result == "btn"

    def test_get_accessible_id_invalid_obj(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_accessible_id with invalid obj."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: False)

        result = AXObject.get_accessible_id(mock_accessible)
        assert result == ""

    def test_get_accessible_id_success(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.get_accessible_id success."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "_set_known_dead_status", Mock())

        sys.modules["gi.repository"].Atspi.Accessible.get_accessible_id = Mock(
            return_value="test-id"
        )

        result = AXObject.get_accessible_id(mock_accessible)
        assert result == "test-id"

    def test_get_accessible_id_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_accessible_id handles GLib.GError."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "handle_error", Mock())

        sys.modules["gi.repository"].Atspi.Accessible.get_accessible_id = Mock(
            side_effect=GLib.GError("Test error")
        )

        result = AXObject.get_accessible_id(mock_accessible)
        assert result == ""

    def test_has_same_non_empty_name_empty_name1(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.has_same_non_empty_name with empty first name."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_obj2 = Mock(spec=Atspi.Accessible)

        def mock_get_name(obj):
            if obj == mock_accessible:
                return ""
            return "test"

        monkeypatch.setattr(AXObject, "get_name", mock_get_name)

        result = AXObject.has_same_non_empty_name(mock_accessible, mock_obj2)
        assert result is False

    def test_has_same_non_empty_name_same_names(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.has_same_non_empty_name with same names."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_obj2 = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(AXObject, "get_name", lambda obj: "test")

        result = AXObject.has_same_non_empty_name(mock_accessible, mock_obj2)
        assert result is True

    def test_get_description_invalid_obj(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_description with invalid obj."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: False)

        result = AXObject.get_description(mock_accessible)
        assert result == ""

    def test_get_description_success(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.get_description."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)

        sys.modules["gi.repository"].Atspi.Accessible.get_description = Mock(
            return_value="Test description"
        )

        result = AXObject.get_description(mock_accessible)
        assert result == "Test description"

    def test_get_description_glib_error(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.get_description handles GLib.GError exceptions."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)

        monkeypatch.setattr(AXObject, "handle_error", Mock())

        glib_error = GLib.GError("Test error")
        sys.modules["gi.repository"].Atspi.Accessible.get_description = Mock(side_effect=glib_error)

        result = AXObject.get_description(mock_accessible)
        assert result == ""

    def test_get_child_count_invalid_object(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_child_count with invalid object."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: False)

        result = AXObject.get_child_count(mock_accessible)
        assert result == 0

    def test_get_child_count(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.get_child_count."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)

        sys.modules["gi.repository"].Atspi.Accessible.get_child_count = Mock(return_value=3)

        result = AXObject.get_child_count(mock_accessible)
        assert result == 3

    def test_get_child_count_glib_error(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.get_child_count handles GLib.GError exceptions."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)

        monkeypatch.setattr(AXObject, "handle_error", Mock())

        glib_error = GLib.GError("Test error")
        sys.modules["gi.repository"].Atspi.Accessible.get_child_count = Mock(side_effect=glib_error)

        result = AXObject.get_child_count(mock_accessible)
        assert result == 0

    def test_get_image_description_invalid_object(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_image_description with object not supporting image."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_image", lambda obj: False)

        result = AXObject.get_image_description(mock_accessible)
        assert result == ""

    def test_get_image_description(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.get_image_description."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_image", lambda obj: True)

        sys.modules["gi.repository"].Atspi.Image.get_image_description = Mock(
            return_value="Test image description"
        )

        result = AXObject.get_image_description(mock_accessible)
        assert result == "Test image description"

    def test_get_image_description_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_image_description handles GLib.GError exceptions."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "supports_image", lambda obj: True)

        monkeypatch.setattr(AXObject, "handle_error", Mock())

        glib_error = GLib.GError("Test error")
        sys.modules["gi.repository"].Atspi.Image.get_image_description = Mock(
            side_effect=glib_error
        )

        result = AXObject.get_image_description(mock_accessible)
        assert result == ""

    def test_supports_action_invalid_obj_path(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.supports_action error path with invalid obj."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: False)

        result = AXObject.supports_action(mock_accessible)
        assert result is False

    def test_supports_component_invalid_obj_path(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.supports_component error path with invalid obj."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: False)

        result = AXObject.supports_component(mock_accessible)
        assert result is False

    def test_supports_component_glib_error_path(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.supports_component GLib.GError path."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "handle_error", Mock())

        sys.modules["gi.repository"].Atspi.Accessible.get_component_iface = Mock(
            side_effect=GLib.GError("Test error")
        )

        result = AXObject.supports_component(mock_accessible)
        assert result is False

    def test_has_document_spreadsheet_import_path(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject._has_document_spreadsheet import path."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_ax_collection = Mock()
        mock_ax_collection.AXCollection = Mock()
        mock_ax_collection.AXCollection.create_match_rule = Mock(return_value=None)
        sys.modules["orca.ax_collection"] = mock_ax_collection

        result = AXObject._has_document_spreadsheet(mock_accessible)
        assert result is False

    def test_has_document_spreadsheet_no_frame_path(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject._has_document_spreadsheet no frame path."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_ax_collection = Mock()
        mock_ax_collection.AXCollection = Mock()
        mock_ax_collection.AXCollection.create_match_rule = Mock(return_value="mock_rule")
        sys.modules["orca.ax_collection"] = mock_ax_collection

        monkeypatch.setattr(AXObject, "find_ancestor_inclusive", lambda obj, pred: None)

        result = AXObject._has_document_spreadsheet(mock_accessible)
        assert result is False

    def test_has_document_spreadsheet_with_matches_path(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject._has_document_spreadsheet with matches path."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_frame = Mock(spec=Atspi.Accessible)

        mock_ax_collection = Mock()
        mock_ax_collection.AXCollection = Mock()
        mock_ax_collection.AXCollection.create_match_rule = Mock(return_value="mock_rule")
        sys.modules["orca.ax_collection"] = mock_ax_collection

        monkeypatch.setattr(AXObject, "find_ancestor_inclusive", lambda obj, pred: mock_frame)

        sys.modules["gi.repository"].Atspi.Collection.get_matches = Mock(return_value=["match1"])

        result = AXObject._has_document_spreadsheet(mock_accessible)
        assert result is True

    def test_supports_document_invalid_obj(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.supports_document with invalid obj."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: False)

        result = AXObject.supports_document(mock_accessible)
        assert result is False

    def test_supports_document_success(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.supports_document success."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)

        mock_iface = Mock()
        sys.modules["gi.repository"].Atspi.Accessible.get_document_iface = Mock(
            return_value=mock_iface
        )

        result = AXObject.supports_document(mock_accessible)
        assert result is True

    def test_supports_document_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.supports_document handles GLib.GError."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "handle_error", Mock())

        sys.modules["gi.repository"].Atspi.Accessible.get_document_iface = Mock(
            side_effect=GLib.GError("Test error")
        )

        result = AXObject.supports_document(mock_accessible)
        assert result is False

    def test_supports_editable_text_invalid_obj(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.supports_editable_text with invalid obj."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: False)

        result = AXObject.supports_editable_text(mock_accessible)
        assert result is False

    def test_supports_editable_text_success(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.supports_editable_text success."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)

        mock_iface = Mock()
        sys.modules["gi.repository"].Atspi.Accessible.get_editable_text_iface = Mock(
            return_value=mock_iface
        )

        result = AXObject.supports_editable_text(mock_accessible)
        assert result is True

    def test_supports_editable_text_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.supports_editable_text handles GLib.GError."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "handle_error", Mock())

        sys.modules["gi.repository"].Atspi.Accessible.get_editable_text_iface = Mock(
            side_effect=GLib.GError("Test error")
        )

        result = AXObject.supports_editable_text(mock_accessible)
        assert result is False

    def test_supports_hyperlink_invalid_obj(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.supports_hyperlink with invalid obj."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: False)

        result = AXObject.supports_hyperlink(mock_accessible)
        assert result is False

    def test_supports_hyperlink_success(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.supports_hyperlink success."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)

        mock_iface = Mock()
        sys.modules["gi.repository"].Atspi.Accessible.get_hyperlink = Mock(return_value=mock_iface)

        result = AXObject.supports_hyperlink(mock_accessible)
        assert result is True

    def test_supports_hyperlink_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.supports_hyperlink handles GLib.GError."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "handle_error", Mock())

        sys.modules["gi.repository"].Atspi.Accessible.get_hyperlink = Mock(
            side_effect=GLib.GError("Test error")
        )

        result = AXObject.supports_hyperlink(mock_accessible)
        assert result is False

    def test_clear_cache_none_obj(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.clear_cache with None obj."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        result = AXObject.clear_cache(None)
        assert result is None

    def test_clear_cache_non_recursive_success(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.clear_cache non-recursive success."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        debug_mock = Mock()
        debug_mock.print_tokens = Mock()
        sys.modules["orca.debug"] = debug_mock

        sys.modules["gi.repository"].Atspi.Accessible.clear_cache_single = Mock()

        AXObject.clear_cache(mock_accessible, recursive=False, reason="test")
        sys.modules["gi.repository"].Atspi.Accessible.clear_cache_single.assert_called_once()

    def test_clear_cache_recursive_success(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.clear_cache recursive success."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        debug_mock = Mock()
        debug_mock.print_tokens = Mock()
        sys.modules["orca.debug"] = debug_mock

        sys.modules["gi.repository"].Atspi.Accessible.clear_cache = Mock()

        AXObject.clear_cache(mock_accessible, recursive=True)
        sys.modules["gi.repository"].Atspi.Accessible.clear_cache.assert_called_once()

    def test_clear_cache_recursive_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.clear_cache recursive GLib.GError."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        debug_mock = Mock()
        debug_mock.print_tokens = Mock()
        sys.modules["orca.debug"] = debug_mock

        monkeypatch.setattr(AXObject, "handle_error", Mock())

        sys.modules["gi.repository"].Atspi.Accessible.clear_cache = Mock(
            side_effect=GLib.GError("Test error")
        )

        AXObject.clear_cache(mock_accessible, recursive=True)
        AXObject.handle_error.assert_called_once()

    def test_get_common_ancestor_with_none_objects(self, monkeypatch, mock_orca_dependencies):
        """Test AXObject.get_common_ancestor with None objects."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        result = AXObject.get_common_ancestor(None, None)
        assert result is None

    def test_get_common_ancestor_same_objects(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_common_ancestor with same objects."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)

        result = AXObject.get_common_ancestor(mock_accessible, mock_accessible)
        assert result == mock_accessible

    def test_get_parent_checked_invalid_obj(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_parent_checked with invalid obj."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: False)

        result = AXObject.get_parent_checked(mock_accessible)
        assert result is None

    def test_get_parent_checked_invalid_role(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_parent_checked with invalid role."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "get_role", lambda obj: Atspi.Role.INVALID)

        result = AXObject.get_parent_checked(mock_accessible)
        assert result is None

    def test_get_attributes_dict_invalid_obj(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_attributes_dict with invalid obj."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: False)

        result = AXObject.get_attributes_dict(mock_accessible)
        assert result == {}

    def test_get_attributes_dict_cached(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.get_attributes_dict with cached attributes."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        cached_attrs = {"role": "button", "name": "test"}

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)

        # Set up cached attributes
        AXObject.OBJECT_ATTRIBUTES[hash(mock_accessible)] = cached_attrs

        result = AXObject.get_attributes_dict(mock_accessible, use_cache=True)
        assert result == cached_attrs

    def test_get_attributes_dict_no_cache(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_attributes_dict without cache."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        attrs = {"role": "button", "name": "test"}

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)

        # Clear any cached attributes
        AXObject.OBJECT_ATTRIBUTES.clear()

        sys.modules["gi.repository"].Atspi.Accessible.get_attributes = Mock(return_value=attrs)

        result = AXObject.get_attributes_dict(mock_accessible, use_cache=False)
        assert result == attrs
        # Should cache the result
        assert AXObject.OBJECT_ATTRIBUTES[hash(mock_accessible)] == attrs

    def test_get_attributes_dict_glib_error(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_attributes_dict handles GLib.GError."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(AXObject, "handle_error", Mock())

        # Clear any cached attributes
        AXObject.OBJECT_ATTRIBUTES.clear()

        sys.modules["gi.repository"].Atspi.Accessible.get_attributes = Mock(
            side_effect=GLib.GError("Test error")
        )

        result = AXObject.get_attributes_dict(mock_accessible)
        assert result == {}
        AXObject.handle_error.assert_called_once()

    def test_get_attributes_dict_none_attributes(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.get_attributes_dict with None attributes."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)

        # Clear any cached attributes
        AXObject.OBJECT_ATTRIBUTES.clear()

        sys.modules["gi.repository"].Atspi.Accessible.get_attributes = Mock(return_value=None)

        result = AXObject.get_attributes_dict(mock_accessible)
        assert result == {}

    def test_find_ancestor_found_grandparent(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.find_ancestor found in parent."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_parent = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)

        def mock_get_parent_checked(obj):
            if obj == mock_accessible:
                return mock_parent
            return None

        monkeypatch.setattr(AXObject, "get_parent_checked", mock_get_parent_checked)

        def match_parent(obj):
            return obj == mock_parent

        result = AXObject.find_ancestor(mock_accessible, match_parent)
        assert result == mock_parent

    def test_find_ancestor_found_in_grandparent(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.find_ancestor found in grandparent."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_parent = Mock(spec=Atspi.Accessible)
        mock_grandparent = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)

        def mock_get_parent_checked(obj):
            if obj == mock_accessible:
                return mock_parent
            if obj == mock_parent:
                return mock_grandparent
            return None

        monkeypatch.setattr(AXObject, "get_parent_checked", mock_get_parent_checked)

        def match_grandparent(obj):
            return obj == mock_grandparent

        result = AXObject.find_ancestor(mock_accessible, match_grandparent)
        assert result == mock_grandparent

    def test_find_ancestor_not_found(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.find_ancestor not found."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        mock_parent = Mock(spec=Atspi.Accessible)

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)

        def mock_get_parent_checked(obj):
            if obj == mock_accessible:
                return mock_parent
            return None

        monkeypatch.setattr(AXObject, "get_parent_checked", mock_get_parent_checked)

        def never_match(obj):
            return False

        result = AXObject.find_ancestor(mock_accessible, never_match)
        assert result is None

    def test_find_ancestor_no_parent(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.find_ancestor with no parent."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)

        monkeypatch.setattr(AXObject, "get_parent_checked", lambda obj: None)

        def always_true(obj):
            return True

        result = AXObject.find_ancestor(mock_accessible, always_true)
        assert result is None

    def test_has_document_spreadsheet_with_invalid_obj(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject._has_document_spreadsheet with invalid object."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: False)

        result = AXObject._has_document_spreadsheet(mock_accessible)
        assert result is False

    def test_has_document_spreadsheet_with_valid_obj(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject._has_document_spreadsheet with valid object."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)

        mock_spreadsheet = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(AXObject, "find_ancestor_inclusive", lambda obj, pred: mock_spreadsheet)

        result = AXObject._has_document_spreadsheet(mock_accessible)
        assert result is True

    def test_has_document_spreadsheet_no_spreadsheet(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject._has_document_spreadsheet with no spreadsheet."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)

        monkeypatch.setattr(AXObject, "find_ancestor_inclusive", lambda obj, pred: None)

        result = AXObject._has_document_spreadsheet(mock_accessible)
        assert result is False

    def test_supports_document_with_interface(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.supports_document with document interface."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)

        mock_iface = Mock()
        sys.modules["gi.repository"].Atspi.Accessible.get_document_iface = Mock(
            return_value=mock_iface
        )

        result = AXObject.supports_document(mock_accessible)
        assert result is True

    def test_supports_document_without_interface(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.supports_document without document interface."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)

        sys.modules["gi.repository"].Atspi.Accessible.get_document_iface = Mock(return_value=None)

        result = AXObject.supports_document(mock_accessible)
        assert result is False

    def test_supports_editable_text_with_interface(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.supports_editable_text with editable text interface."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)

        mock_iface = Mock()
        sys.modules["gi.repository"].Atspi.Accessible.get_editable_text_iface = Mock(
            return_value=mock_iface
        )

        result = AXObject.supports_editable_text(mock_accessible)
        assert result is True

    def test_supports_editable_text_without_interface(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.supports_editable_text without editable text interface."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)

        sys.modules["gi.repository"].Atspi.Accessible.get_editable_text_iface = Mock(
            return_value=None
        )

        result = AXObject.supports_editable_text(mock_accessible)
        assert result is False

    def test_supports_hyperlink_with_interface(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.supports_hyperlink with hyperlink interface."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)

        mock_iface = Mock()
        sys.modules["gi.repository"].Atspi.Accessible.get_hyperlink = Mock(return_value=mock_iface)

        result = AXObject.supports_hyperlink(mock_accessible)
        assert result is True

    def test_supports_hyperlink_without_interface(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.supports_hyperlink without hyperlink interface."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)

        sys.modules["gi.repository"].Atspi.Accessible.get_hyperlink = Mock(return_value=None)

        result = AXObject.supports_hyperlink(mock_accessible)
        assert result is False

    def test_supports_image_invalid_obj(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.supports_image with invalid object."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: False)

        result = AXObject.supports_image(mock_accessible)
        assert result is False

    def test_supports_image_with_interface(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.supports_image with image interface."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)

        mock_iface = Mock()
        sys.modules["gi.repository"].Atspi.Accessible.get_image_iface = Mock(
            return_value=mock_iface
        )

        result = AXObject.supports_image(mock_accessible)
        assert result is True

    def test_supports_image_without_interface(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.supports_image without image interface."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)

        sys.modules["gi.repository"].Atspi.Accessible.get_image_iface = Mock(return_value=None)

        result = AXObject.supports_image(mock_accessible)
        assert result is False

    def test_supports_selection_invalid_obj(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.supports_selection with invalid object."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: False)

        result = AXObject.supports_selection(mock_accessible)
        assert result is False

    def test_supports_selection_with_interface(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.supports_selection with selection interface."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)

        mock_iface = Mock()
        sys.modules["gi.repository"].Atspi.Accessible.get_selection_iface = Mock(
            return_value=mock_iface
        )

        result = AXObject.supports_selection(mock_accessible)
        assert result is True

    def test_supports_selection_without_interface(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.supports_selection without selection interface."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)

        sys.modules["gi.repository"].Atspi.Accessible.get_selection_iface = Mock(return_value=None)

        result = AXObject.supports_selection(mock_accessible)
        assert result is False

    def test_supports_table_invalid_obj(self, monkeypatch, mock_accessible, mock_orca_dependencies):
        """Test AXObject.supports_table with invalid object."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: False)

        result = AXObject.supports_table(mock_accessible)
        assert result is False

    def test_supports_table_with_interface(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.supports_table with table interface."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)

        mock_iface = Mock()
        sys.modules["gi.repository"].Atspi.Accessible.get_table_iface = Mock(
            return_value=mock_iface
        )

        result = AXObject.supports_table(mock_accessible)
        assert result is True

    def test_supports_table_without_interface(
        self, monkeypatch, mock_accessible, mock_orca_dependencies
    ):
        """Test AXObject.supports_table without table interface."""

        clean_module_cache("orca.ax_object")
        from orca.ax_object import AXObject

        monkeypatch.setattr(AXObject, "is_valid", lambda obj: True)

        sys.modules["gi.repository"].Atspi.Accessible.get_table_iface = Mock(return_value=None)

        result = AXObject.supports_table(mock_accessible)
        assert result is False
