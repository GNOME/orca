# Unit tests for ax_value.py value-related methods.
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

"""Unit tests for ax_value.py value-related methods."""

from unittest.mock import Mock

import gi
import pytest

from conftest import clean_module_cache

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi
from gi.repository import GLib


@pytest.mark.unit
class TestAXValue:
    """Test value-related methods."""

    @pytest.fixture
    def mock_accessible(self):
        """Create a mock Atspi.Accessible object."""
        return Mock(spec=Atspi.Accessible)

    @pytest.mark.parametrize(
        "supports_value, current_value, last_known_value, expected_result, setup_last_known",
        [
            pytest.param(False, None, None, False, False, id="no_value_support"),
            pytest.param(True, 50.0, None, True, False, id="first_time_value"),
            pytest.param(True, 50.0, 50.0, False, True, id="same_value"),
            pytest.param(True, 75.0, 50.0, True, True, id="value_changed"),
        ],
    )
    def test_did_value_change(
        self,
        mock_accessible,
        monkeypatch,
        mock_orca_dependencies,
        supports_value,
        current_value,
        last_known_value,
        expected_result,
        setup_last_known
    ):
        """Test AXValue.did_value_change."""

        clean_module_cache("orca.ax_value")
        from orca.ax_value import AXValue
        from orca.ax_object import AXObject
        monkeypatch.setattr(AXObject, "supports_value", lambda obj: supports_value)

        if current_value is not None:
            monkeypatch.setattr(AXValue, "_get_current_value", lambda obj: current_value)

        if setup_last_known:
            AXValue.LAST_KNOWN_VALUE[hash(mock_accessible)] = last_known_value
        else:
            AXValue.LAST_KNOWN_VALUE.clear()

        result = AXValue.did_value_change(mock_accessible)
        assert result is expected_result

    @pytest.mark.parametrize(
        "supports_value, atspi_return_value, should_raise_error, expected_result",
        [
            pytest.param(False, None, False, 0.0, id="no_value_support"),
            pytest.param(True, 42.5, False, 42.5, id="success_case"),
            pytest.param(True, None, True, 0.0, id="glib_error"),
        ],
    )
    def test_get_current_value_private(
        self,
        monkeypatch,
        mock_orca_dependencies,
        supports_value,
        atspi_return_value,
        should_raise_error,
        expected_result
    ):
        """Test AXValue._get_current_value."""

        clean_module_cache("orca.ax_value")
        from orca.ax_value import AXValue
        from orca.ax_object import AXObject

        mock_obj = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(AXObject, "supports_value", lambda obj: supports_value)

        if should_raise_error:
            def raise_glib_error(obj):
                raise GLib.GError("Test error")
            monkeypatch.setattr(Atspi.Value, "get_current_value", raise_glib_error)
        elif atspi_return_value is not None:
            monkeypatch.setattr(Atspi.Value, "get_current_value", lambda obj: atspi_return_value)
        else:
            # For the no_value_support case, we shouldn't reach this call
            monkeypatch.setattr(Atspi.Value, "get_current_value", lambda obj: 0.0)

        result = AXValue._get_current_value(mock_obj)
        assert result == expected_result

    def test_get_current_value_with_no_value_support(self, monkeypatch, mock_orca_dependencies):
        """Test AXValue.get_current_value when object doesn't support value."""

        clean_module_cache("orca.ax_value")
        from orca.ax_value import AXValue
        from orca.ax_object import AXObject

        mock_obj = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(AXObject, "supports_value", lambda obj: False)
        result = AXValue.get_current_value(mock_obj)
        assert result == 0.0

    def test_get_current_value_stores_value(self, monkeypatch, mock_orca_dependencies):
        """Test AXValue.get_current_value stores the value in LAST_KNOWN_VALUE."""

        clean_module_cache("orca.ax_value")
        from orca.ax_value import AXValue
        from orca.ax_object import AXObject

        mock_obj = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(AXObject, "supports_value", lambda obj: True)
        monkeypatch.setattr(AXValue, "_get_current_value", lambda obj: 75.0)
        AXValue.LAST_KNOWN_VALUE.clear()
        result = AXValue.get_current_value(mock_obj)
        assert result == 75.0
        assert AXValue.LAST_KNOWN_VALUE[hash(mock_obj)] == 75.0

    def test_get_current_value_text_with_valuetext_attribute(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXValue.get_current_value_text with valuetext attribute."""

        clean_module_cache("orca.ax_value")
        from orca.ax_value import AXValue
        from orca.ax_object import AXObject

        mock_obj = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(AXObject, "get_attribute", lambda obj, name, check_computed: "75%")
        result = AXValue.get_current_value_text(mock_obj)
        assert result == "75%"

    def test_get_current_value_text_no_value_support_no_attribute(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXValue.get_current_value_text when no value support."""

        clean_module_cache("orca.ax_value")
        from orca.ax_value import AXValue
        from orca.ax_object import AXObject

        mock_obj = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(AXObject, "get_attribute", lambda obj, name, check_computed: "")
        monkeypatch.setattr(AXObject, "supports_value", lambda obj: False)
        result = AXValue.get_current_value_text(mock_obj)
        assert result == ""

    def test_get_current_value_text_from_atspi(self, monkeypatch, mock_orca_dependencies):
        """Test AXValue.get_current_value_text from Atspi.Value.get_text."""

        clean_module_cache("orca.ax_value")
        from orca.ax_value import AXValue
        from orca.ax_object import AXObject

        mock_obj = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(AXObject, "get_attribute", lambda obj, name, check_computed: "")
        monkeypatch.setattr(AXObject, "supports_value", lambda obj: True)
        monkeypatch.setattr(Atspi.Value, "get_text", lambda self: "50 percent")
        result = AXValue.get_current_value_text(mock_obj)
        assert result == "50 percent"

    def test_get_current_value_text_with_glib_error(self, monkeypatch, mock_orca_dependencies):
        """Test AXValue.get_current_value_text handles GLib.GError."""

        clean_module_cache("orca.ax_value")
        from orca.ax_value import AXValue
        from orca.ax_object import AXObject

        mock_obj = Mock(spec=Atspi.Accessible)

        def raise_glib_error(self):
            raise GLib.GError("Test error")

        monkeypatch.setattr(AXObject, "get_attribute", lambda obj, name, check_computed: "")
        monkeypatch.setattr(AXObject, "supports_value", lambda obj: True)
        monkeypatch.setattr(Atspi.Value, "get_text", raise_glib_error)
        monkeypatch.setattr(AXValue, "get_current_value", lambda obj: 42.0)
        result = AXValue.get_current_value_text(mock_obj)
        assert result == "42"

    def test_get_current_value_text_formats_decimal_places(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXValue.get_current_value_text preserves decimal places."""

        clean_module_cache("orca.ax_value")
        from orca.ax_value import AXValue
        from orca.ax_object import AXObject

        mock_obj = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(AXObject, "get_attribute", lambda obj, name, check_computed: "")
        monkeypatch.setattr(AXObject, "supports_value", lambda obj: True)
        monkeypatch.setattr(Atspi.Value, "get_text", lambda self: "")
        monkeypatch.setattr(AXValue, "get_current_value", lambda obj: 0.125)
        result = AXValue.get_current_value_text(mock_obj)
        assert result == "0.125"

    @pytest.mark.parametrize(
        "supports_value, current_value, is_indeterminate, min_val, max_val, expected_result",
        [
            pytest.param(False, None, False, None, None, None, id="no_value_support"),
            pytest.param(True, 0.0, True, None, None, None, id="indeterminate_state"),
            pytest.param(True, 50.0, False, 100.0, 100.0, None, id="min_equals_max"),
            pytest.param(True, 75.0, False, 0.0, 100.0, 75, id="normal_calculation"),
        ],
    )
    def test_get_value_as_percent(
        self,
        monkeypatch,
        mock_orca_dependencies,
        supports_value,
        current_value,
        is_indeterminate,
        min_val,
        max_val,
        expected_result
    ):
        """Test AXValue.get_value_as_percent."""

        clean_module_cache("orca.ax_value")
        from orca.ax_value import AXValue
        from orca.ax_object import AXObject
        from orca.ax_utilities_state import AXUtilitiesState
        from orca.ax_utilities import AXUtilities

        # Add missing method to AXUtilities for cross-contamination prevention
        if not hasattr(AXUtilities, "is_indeterminate"):
            setattr(
                AXUtilities, "is_indeterminate", staticmethod(AXUtilitiesState.is_indeterminate)
            )

        mock_obj = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(AXObject, "supports_value", lambda obj: supports_value)

        if current_value is not None:
            monkeypatch.setattr(AXValue, "get_current_value", lambda obj: current_value)

        if supports_value:
            monkeypatch.setattr(AXUtilities, "is_indeterminate", lambda obj: is_indeterminate)

            if min_val is not None:
                monkeypatch.setattr(AXValue, "get_minimum_value", lambda obj: min_val)
            if max_val is not None:
                monkeypatch.setattr(AXValue, "get_maximum_value", lambda obj: max_val)

        result = AXValue.get_value_as_percent(mock_obj)
        assert result == expected_result
