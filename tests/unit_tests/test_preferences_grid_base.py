# Unit tests for preferences_grid_base.py.
#
# Copyright 2026 Igalia, S.L.
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
# pylint: disable=protected-access
# pylint: disable=import-outside-toplevel

"""Unit tests for preferences_grid_base.py."""

from __future__ import annotations

from typing import Any

import pytest

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from orca.preferences_grid_base import (
    AutoPreferencesGrid,
    BooleanPreferenceControl,
    CategoryListBoxRow,
    CommandListBoxRow,
    ControlType,
    EnumPreferenceControl,
    FloatRangePreferenceControl,
    FocusManagedListBox,
    IntRangePreferenceControl,
    PreferencesGridBase,
    RadioButtonWithActions,
    SelectionPreferenceControl,
    StackedPreferencesHelper,
)


@pytest.mark.unit
class TestPreferenceControlDataclasses:
    """Test preference control dataclass creation and properties."""

    def test_boolean_preference_control_creation(self) -> None:
        """Test BooleanPreferenceControl can be created with required fields."""

        getter_called: list[bool] = [False]
        setter_value: list[bool | None] = [None]

        def getter() -> bool:
            getter_called[0] = True
            return True

        def setter(value: bool) -> bool:
            setter_value[0] = value
            return True

        control = BooleanPreferenceControl(
            label="Test Label", getter=getter, setter=setter, prefs_key="testKey"
        )

        assert control.label == "Test Label"
        assert control.prefs_key == "testKey"
        assert control.getter() is True
        assert getter_called[0] is True
        control.setter(False)
        assert setter_value[0] is False

    def test_boolean_preference_control_optional_fields(self) -> None:
        """Test BooleanPreferenceControl optional fields have correct defaults."""

        control = BooleanPreferenceControl(label="Test", getter=lambda: True, setter=lambda x: True)

        assert control.prefs_key is None
        assert control.member_of is None
        assert control.determine_sensitivity is None
        assert control.apply_immediately is True

    def test_int_range_preference_control_creation(self) -> None:
        """Test IntRangePreferenceControl can be created with all fields."""

        control = IntRangePreferenceControl(
            label="Volume",
            minimum=0,
            maximum=100,
            getter=lambda: 50,
            setter=lambda x: True,
            prefs_key="volume",
        )

        assert control.label == "Volume"
        assert control.minimum == 0
        assert control.maximum == 100
        assert control.getter() == 50

    def test_float_range_preference_control_creation(self) -> None:
        """Test FloatRangePreferenceControl can be created with all fields."""

        control = FloatRangePreferenceControl(
            label="Rate", minimum=0.0, maximum=1.0, getter=lambda: 0.5, setter=lambda x: True
        )

        assert control.label == "Rate"
        assert control.minimum == 0.0
        assert control.maximum == 1.0
        assert control.getter() == 0.5

    def test_enum_preference_control_creation(self) -> None:
        """Test EnumPreferenceControl can be created with options and values."""

        control = EnumPreferenceControl(
            label="Style",
            options=["Option A", "Option B", "Option C"],
            values=[1, 2, 3],
            getter=lambda: 2,
            setter=lambda x: True,
        )

        assert control.label == "Style"
        assert len(control.options) == 3
        assert control.values == [1, 2, 3]
        assert control.getter() == 2

    def test_selection_preference_control_creation(self) -> None:
        """Test SelectionPreferenceControl can be created with actions callback."""

        def get_actions(_value: Any) -> list[tuple[str, str, Any]]:
            return [("Edit", "edit-symbolic", lambda: None)]

        control = SelectionPreferenceControl(
            label="Profile",
            options=["Default", "Custom"],
            getter=lambda: "Default",
            setter=lambda x: True,
            get_actions_for_option=get_actions,
        )

        assert control.label == "Profile"
        assert len(control.options) == 2
        assert control.get_actions_for_option is not None
        actions = control.get_actions_for_option("Default")
        assert len(actions) == 1
        assert actions[0][0] == "Edit"


@pytest.mark.unit
class TestHelperClasses:
    """Test helper classes in preferences_grid_base."""

    def test_category_list_box_row_stores_category(self) -> None:
        """Test CategoryListBoxRow stores and returns category identifier."""

        row = CategoryListBoxRow("speech_settings")
        assert row.category == "speech_settings"

    def test_category_list_box_row_is_gtk_list_box_row(self) -> None:
        """Test CategoryListBoxRow inherits from Gtk.ListBoxRow."""

        row = CategoryListBoxRow("test")
        assert isinstance(row, Gtk.ListBoxRow)

    def test_command_list_box_row_properties(self) -> None:
        """Test CommandListBoxRow property getters and setters."""

        row = CommandListBoxRow()
        assert row.command is None
        assert row.vbox is None
        assert row.binding_label is None

        mock_command = object()
        mock_vbox = Gtk.Box()
        mock_label = Gtk.Label()

        row.command = mock_command
        row.vbox = mock_vbox
        row.binding_label = mock_label

        assert row.command is mock_command
        assert row.vbox is mock_vbox
        assert row.binding_label is mock_label

    def test_radio_button_with_actions_stores_buttons(self) -> None:
        """Test RadioButtonWithActions stores action buttons list."""

        radio = RadioButtonWithActions(label="Test Option")
        assert not radio.action_buttons

        button1 = Gtk.Button()
        button2 = Gtk.Button()
        radio.action_buttons = [button1, button2]

        assert len(radio.action_buttons) == 2
        assert radio.action_buttons[0] is button1

    def test_radio_button_with_actions_is_gtk_radio_button(self) -> None:
        """Test RadioButtonWithActions inherits from Gtk.RadioButton."""

        radio = RadioButtonWithActions(label="Test")
        assert isinstance(radio, Gtk.RadioButton)

    def test_stacked_preferences_helper_initial_state(self) -> None:
        """Test StackedPreferencesHelper initializes with None values."""

        helper = StackedPreferencesHelper()
        assert helper.stack is None
        assert helper.categories_listbox is None
        assert helper.detail_listbox is None
        assert not helper.disable_widgets
        assert helper.on_category_activated_callback is None

    def test_stacked_preferences_helper_register_widgets(self) -> None:
        """Test StackedPreferencesHelper can register widgets to disable."""

        helper = StackedPreferencesHelper()
        button1 = Gtk.Button()
        button2 = Gtk.Button()

        helper.register_disable_widgets(button1, button2)
        assert len(helper.disable_widgets) == 2
        assert button1 in helper.disable_widgets

    def test_stacked_preferences_helper_show_categories(self) -> None:
        """Test StackedPreferencesHelper show_categories enables registered widgets."""

        helper = StackedPreferencesHelper()
        helper.stack = Gtk.Stack()
        cat_label = Gtk.Label(label="Categories")
        det_label = Gtk.Label(label="Detail")
        helper.stack.add_named(cat_label, "categories")
        helper.stack.add_named(det_label, "detail")

        # Show the stack to ensure children are realized
        helper.stack.show_all()  # pylint: disable=no-member
        helper.stack.set_visible_child_name("detail")

        button = Gtk.Button()
        button.set_sensitive(False)
        helper.register_disable_widgets(button)

        helper.show_categories()
        assert button.get_sensitive() is True
        # Verify the visible child is the categories child
        assert helper.stack.get_visible_child() is cat_label

    def test_stacked_preferences_helper_show_detail(self) -> None:
        """Test StackedPreferencesHelper show_detail disables registered widgets."""

        helper = StackedPreferencesHelper()
        helper.stack = Gtk.Stack()
        cat_label = Gtk.Label(label="Categories")
        det_label = Gtk.Label(label="Detail")
        helper.stack.add_named(cat_label, "categories")
        helper.stack.add_named(det_label, "detail")

        # Show the stack to ensure children are realized
        helper.stack.show_all()  # pylint: disable=no-member
        helper.stack.set_visible_child_name("categories")

        button = Gtk.Button()
        button.set_sensitive(True)
        helper.register_disable_widgets(button)

        helper.show_detail()
        assert button.get_sensitive() is False
        # Verify the visible child is the detail child
        assert helper.stack.get_visible_child() is det_label


@pytest.mark.unit
class TestFocusManagedListBox:
    """Test FocusManagedListBox focus management."""

    def test_focus_managed_listbox_initial_state(self) -> None:
        """Test FocusManagedListBox initializes with correct settings."""

        listbox = FocusManagedListBox()
        assert listbox.get_selection_mode() == Gtk.SelectionMode.NONE
        assert listbox.get_can_focus() is False

    def test_focus_managed_listbox_add_row_with_widget(self) -> None:
        """Test FocusManagedListBox tracks added rows and widgets."""

        listbox = FocusManagedListBox()
        row = Gtk.ListBoxRow()
        switch = Gtk.Switch()

        listbox.add_row_with_widget(row, switch)

        assert len(listbox._widgets) == 1
        assert len(listbox._rows) == 1
        assert listbox._widgets[0] is switch
        assert listbox._rows[0] is row

    def test_focus_managed_listbox_get_last_row(self) -> None:
        """Test FocusManagedListBox.get_last_row returns last added row."""

        listbox = FocusManagedListBox()
        assert listbox.get_last_row() is None

        row1 = Gtk.ListBoxRow()
        row2 = Gtk.ListBoxRow()
        listbox.add_row_with_widget(row1, Gtk.Switch())
        listbox.add_row_with_widget(row2, Gtk.Switch())

        assert listbox.get_last_row() is row2

    def test_focus_managed_listbox_multiple_rows(self) -> None:
        """Test FocusManagedListBox handles multiple rows correctly."""

        listbox = FocusManagedListBox()

        for _i in range(5):
            row = Gtk.ListBoxRow()
            switch = Gtk.Switch()
            listbox.add_row_with_widget(row, switch)

        assert len(listbox._widgets) == 5
        assert len(listbox._rows) == 5


@pytest.mark.unit
class TestPreferencesGridBase:
    """Test PreferencesGridBase UI helper methods."""

    def test_preferences_grid_base_initialization(self) -> None:
        """Test PreferencesGridBase initializes with correct properties."""

        grid = PreferencesGridBase("Test Tab")
        assert grid._tab_label == "Test Tab"
        assert grid._has_unsaved_changes is False
        assert grid.get_border_width() == 24  # pylint: disable=no-member

    def test_preferences_grid_base_get_label(self) -> None:
        """Test PreferencesGridBase.get_label returns Gtk.Label."""

        grid = PreferencesGridBase("My Tab")
        label = grid.get_label()

        assert isinstance(label, Gtk.Label)
        assert label.get_text() == "My Tab"

    def test_preferences_grid_base_has_changes(self) -> None:
        """Test PreferencesGridBase.has_changes tracks unsaved changes."""

        grid = PreferencesGridBase("Test")
        assert grid.has_changes() is False

        grid._has_unsaved_changes = True
        assert grid.has_changes() is True

    def test_create_frame_returns_frame_and_grid(self) -> None:
        """Test _create_frame returns Gtk.Frame and content Gtk.Grid."""

        grid = PreferencesGridBase("Test")
        frame, content = grid._create_frame("Section Label")

        assert isinstance(frame, Gtk.Frame)
        assert isinstance(content, Gtk.Grid)
        assert frame.get_child() is content

    def test_create_label_with_mnemonic(self) -> None:
        """Test _create_label creates label with mnemonic support."""

        grid = PreferencesGridBase("Test")
        label = grid._create_label("_Test Label")

        assert isinstance(label, Gtk.Label)
        # Label should use underline for mnemonic
        assert label.get_use_underline() is True

    def test_create_switch_row(self) -> None:
        """Test _create_switch_row creates row with label and switch."""

        grid = PreferencesGridBase("Test")
        handler_called = [False]

        def handler(_switch, _param):
            handler_called[0] = True

        row, switch, label = grid._create_switch_row("Enable Feature", handler, state=True)

        assert isinstance(row, Gtk.ListBoxRow)
        assert isinstance(switch, Gtk.Switch)
        assert isinstance(label, Gtk.Label)
        assert switch.get_active() is True

    def test_create_slider_row(self) -> None:
        """Test _create_slider_row creates row with label and scale."""

        grid = PreferencesGridBase("Test")
        adjustment = Gtk.Adjustment(
            value=50, lower=0, upper=100, step_increment=1, page_increment=10
        )

        row, scale, label = grid._create_slider_row("Volume", adjustment)

        assert isinstance(row, Gtk.ListBoxRow)
        assert isinstance(scale, Gtk.Scale)
        assert isinstance(label, Gtk.Label)
        assert scale.get_value() == 50

    def test_create_info_listbox(self) -> None:
        """Test _create_info_listbox creates listbox with info message."""

        grid = PreferencesGridBase("Test")
        listbox = grid._create_info_listbox("This is an informational message.")

        assert isinstance(listbox, Gtk.ListBox)
        assert listbox.get_selection_mode() == Gtk.SelectionMode.NONE

    def test_create_scrolled_window(self) -> None:
        """Test _create_scrolled_window wraps widget in scrolled container."""

        grid = PreferencesGridBase("Test")
        label = Gtk.Label(label="Content")
        scrolled = grid._create_scrolled_window(label)

        assert isinstance(scrolled, Gtk.ScrolledWindow)
        assert scrolled.get_hexpand() is True
        assert scrolled.get_vexpand() is True


@pytest.mark.unit
class TestAutoPreferencesGrid:
    """Test AutoPreferencesGrid automatic UI building."""

    def _create_test_grid(self) -> tuple:
        """Create a test grid with various controls for testing."""

        values: dict[str, Any] = {
            "bool_setting": True,
            "int_setting": 5,
            "float_setting": 0.5,
            "enum_setting": "Option B",
        }

        def set_bool(x: bool) -> bool:
            values["bool_setting"] = x
            return True

        def set_int(x: int) -> bool:
            values["int_setting"] = x
            return True

        def set_float(x: float) -> bool:
            values["float_setting"] = x
            return True

        def set_enum(x: str) -> bool:
            values["enum_setting"] = x
            return True

        controls: list[ControlType] = [
            BooleanPreferenceControl(
                label="Enable Feature",
                getter=lambda: values["bool_setting"],
                setter=set_bool,
                prefs_key="boolSetting",
            ),
            IntRangePreferenceControl(
                label="Count",
                minimum=0,
                maximum=10,
                getter=lambda: values["int_setting"],
                setter=set_int,
                prefs_key="intSetting",
            ),
            FloatRangePreferenceControl(
                label="Rate",
                minimum=0.0,
                maximum=1.0,
                getter=lambda: values["float_setting"],
                setter=set_float,
                prefs_key="floatSetting",
            ),
            EnumPreferenceControl(
                label="Style",
                options=["Option A", "Option B", "Option C"],
                getter=lambda: values["enum_setting"],
                setter=set_enum,
                prefs_key="enumSetting",
            ),
        ]

        grid = AutoPreferencesGrid("Test Tab", controls)
        return grid, values, controls

    def test_auto_preferences_grid_builds_widgets(self) -> None:
        """Test AutoPreferencesGrid creates widgets for all controls."""

        grid, _values, controls = self._create_test_grid()

        assert len(grid._widgets) == len(controls)
        assert len(grid._controls) == len(controls)

    def test_auto_preferences_grid_boolean_control_creates_switch(self) -> None:
        """Test AutoPreferencesGrid creates Switch for boolean control."""

        grid, _values, _controls = self._create_test_grid()

        # First control is boolean, should create a Switch
        widget = grid.get_widget(0)
        assert isinstance(widget, Gtk.Switch)
        assert widget.get_active() is True

    def test_auto_preferences_grid_int_range_creates_spinbutton(self) -> None:
        """Test AutoPreferencesGrid creates SpinButton for int range control."""

        grid, _values, _controls = self._create_test_grid()

        widget = grid.get_widget(1)
        assert isinstance(widget, Gtk.SpinButton)
        assert int(widget.get_value()) == 5

    def test_auto_preferences_grid_float_range_creates_scale(self) -> None:
        """Test AutoPreferencesGrid creates Scale for float range control."""

        grid, _values, _controls = self._create_test_grid()

        widget = grid.get_widget(2)
        assert isinstance(widget, Gtk.Scale)
        assert widget.get_value() == pytest.approx(0.5, abs=0.01)

    def test_auto_preferences_grid_enum_creates_combobox(self) -> None:
        """Test AutoPreferencesGrid creates ComboBoxText for enum control."""

        grid, _values, _controls = self._create_test_grid()

        widget = grid.get_widget(3)
        assert isinstance(widget, Gtk.ComboBoxText)
        # Option B is at index 1
        assert widget.get_active() == 1

    def test_auto_preferences_grid_refresh_updates_widgets(self) -> None:
        """Test AutoPreferencesGrid.refresh updates widget values from getters."""

        current_value = [True]

        controls = [
            BooleanPreferenceControl(
                label="Test", getter=lambda: current_value[0], setter=lambda x: True
            ),
        ]

        grid = AutoPreferencesGrid("Test", controls)
        switch = grid.get_widget(0)
        assert switch and switch.get_active()

        current_value[0] = False
        grid.refresh()
        assert switch and not switch.get_active()

    def test_auto_preferences_grid_save_settings_calls_setters(self) -> None:
        """Test AutoPreferencesGrid.save_settings calls all setters."""

        grid, values, _controls = self._create_test_grid()

        switch = grid.get_widget(0)
        switch.set_active(False)
        spin = grid.get_widget(1)
        spin.set_value(8)
        result = grid.save_settings()

        assert values["bool_setting"] is False
        assert values["int_setting"] == 8
        assert "boolSetting" in result
        assert result["boolSetting"] is False

    def test_auto_preferences_grid_save_returns_prefs_dict(self) -> None:
        """Test AutoPreferencesGrid.save_settings returns dict with prefs_keys."""

        grid, _values, _controls = self._create_test_grid()

        result = grid.save_settings()

        assert "boolSetting" in result
        assert "intSetting" in result
        assert "floatSetting" in result
        assert "enumSetting" in result

    def test_auto_preferences_grid_reload_clears_changes_flag(self) -> None:
        """Test AutoPreferencesGrid.reload clears unsaved changes flag."""

        grid, _values, _controls = self._create_test_grid()

        grid._has_unsaved_changes = True
        grid.reload()

        assert grid._has_unsaved_changes is False

    def test_auto_preferences_grid_get_widget_returns_none_for_invalid_index(self) -> None:
        """Test AutoPreferencesGrid.get_widget returns None for out-of-range index."""

        grid, _values, controls = self._create_test_grid()

        assert grid.get_widget(-1) is None
        assert grid.get_widget(len(controls)) is None
        assert grid.get_widget(100) is None

    def test_auto_preferences_grid_get_widget_for_control(self) -> None:
        """Test AutoPreferencesGrid.get_widget_for_control finds correct widget."""

        grid, _values, controls = self._create_test_grid()

        widget = grid.get_widget_for_control(controls[0])
        assert widget is not None
        assert isinstance(widget, Gtk.Switch)

        # Non-existent control should return None
        other_control = BooleanPreferenceControl(
            label="Other", getter=lambda: True, setter=lambda x: True
        )
        assert grid.get_widget_for_control(other_control) is None

    def test_auto_preferences_grid_with_grouped_controls(self) -> None:
        """Test AutoPreferencesGrid groups controls by member_of field."""

        controls = [
            BooleanPreferenceControl(label="Ungrouped", getter=lambda: True, setter=lambda x: True),
            BooleanPreferenceControl(
                label="Group A Item 1",
                getter=lambda: True,
                setter=lambda x: True,
                member_of="Group A",
            ),
            BooleanPreferenceControl(
                label="Group A Item 2",
                getter=lambda: False,
                setter=lambda x: True,
                member_of="Group A",
            ),
            BooleanPreferenceControl(
                label="Group B Item",
                getter=lambda: True,
                setter=lambda x: True,
                member_of="Group B",
            ),
        ]

        grid = AutoPreferencesGrid("Test", controls)

        assert "Group A" in grid._group_labels
        assert "Group B" in grid._group_labels
        assert len(grid._widgets) == 4

    def test_auto_preferences_grid_sensitivity_callback(self) -> None:
        """Test AutoPreferencesGrid updates sensitivity based on callback."""

        primary_enabled = [True]

        def set_primary(x: bool) -> bool:
            primary_enabled[0] = x
            return True

        controls = [
            BooleanPreferenceControl(
                label="Primary",
                getter=lambda: primary_enabled[0],
                setter=set_primary,
                apply_immediately=True,
            ),
            BooleanPreferenceControl(
                label="Dependent",
                getter=lambda: True,
                setter=lambda x: True,
                determine_sensitivity=lambda: primary_enabled[0],
            ),
        ]

        grid = AutoPreferencesGrid("Test", controls)

        primary_switch = grid.get_widget(0)
        dependent_switch = grid.get_widget(1)

        assert dependent_switch and dependent_switch.get_sensitive()

        grid._initializing = False  # Allow change handlers to run
        assert primary_switch
        primary_switch.set_active(False)

        assert dependent_switch and not dependent_switch.get_sensitive()

    def test_auto_preferences_grid_with_info_message(self) -> None:
        """Test AutoPreferencesGrid displays info message when provided."""

        controls = [
            BooleanPreferenceControl(label="Test", getter=lambda: True, setter=lambda x: True),
        ]

        grid = AutoPreferencesGrid("Test", controls, info_message="This is helpful information.")

        assert grid._info_listbox is not None


@pytest.mark.unit
class TestAutoPreferencesGridSelectionControl:
    """Test AutoPreferencesGrid with SelectionPreferenceControl."""

    def test_selection_control_creates_combobox_without_actions(self) -> None:
        """Test SelectionPreferenceControl without actions creates ComboBoxText."""

        controls = [
            SelectionPreferenceControl(
                label="Choose", options=["A", "B", "C"], getter=lambda: "B", setter=lambda x: True
            ),
        ]

        grid = AutoPreferencesGrid("Test", controls)
        widget = grid.get_widget(0)

        assert isinstance(widget, Gtk.ComboBoxText)
        assert widget.get_active() == 1

    def test_selection_control_creates_radio_buttons_with_actions(self) -> None:
        """Test SelectionPreferenceControl with actions creates RadioButtons."""

        def get_actions(_value):
            return [("Edit", "edit-symbolic", lambda: None)]

        controls = [
            SelectionPreferenceControl(
                label="Profile",
                options=["Default", "Custom"],
                getter=lambda: "Default",
                setter=lambda x: True,
                get_actions_for_option=get_actions,
            ),
        ]

        grid = AutoPreferencesGrid("Test", controls)
        widget = grid.get_widget(0)

        assert isinstance(widget, RadioButtonWithActions)

    def test_selection_control_with_values_mapping(self) -> None:
        """Test SelectionPreferenceControl maps display options to values."""

        current_value = [100]

        def set_level(x: int) -> bool:
            current_value[0] = x
            return True

        controls = [
            SelectionPreferenceControl(
                label="Level",
                options=["Low", "Medium", "High"],
                values=[50, 100, 150],
                getter=lambda: current_value[0],
                setter=set_level,
                prefs_key="level",
            ),
        ]

        grid = AutoPreferencesGrid("Test", controls)
        widget = grid.get_widget(0)

        assert widget and widget.get_active() == 1

        widget.set_active(2)
        result = grid.save_settings()

        assert current_value[0] == 150
        assert result["level"] == 150


@pytest.mark.unit
class TestPreferencesGridBaseMultiPageStack:
    """Test PreferencesGridBase multi-page stack functionality."""

    def test_create_multi_page_stack_basic(self) -> None:
        """Test _create_multi_page_stack creates stack with categories."""

        class TestGrid(PreferencesGridBase):
            """Test grid."""

            def __init__(self):
                super().__init__("Test")
                self._initializing = True

                child1 = PreferencesGridBase("Child 1")
                child2 = PreferencesGridBase("Child 2")

                enable_listbox, stack, categories = self._create_multi_page_stack(
                    enable_label="Enable",
                    enable_getter=lambda: True,
                    enable_setter=lambda x: True,
                    categories=[
                        ("General", "general", child1),
                        ("Advanced", "advanced", child2),
                    ],
                    main_title="Test Settings",
                )

                self.my_enable_listbox = enable_listbox
                self.my_stack = stack
                self.my_categories = categories
                self._initializing = False

        grid = TestGrid()

        assert grid.my_stack is not None
        assert grid.my_categories is not None
        assert grid.my_enable_listbox is not None

    def test_create_multi_page_stack_without_enable(self) -> None:
        """Test _create_multi_page_stack without enable switch."""

        class TestGrid(PreferencesGridBase):
            """Test grid."""

            def __init__(self):
                super().__init__("Test")
                self._initializing = True

                child = PreferencesGridBase("Child")

                enable_listbox, stack, _categories = self._create_multi_page_stack(
                    enable_label=None,
                    enable_getter=None,
                    enable_setter=None,
                    categories=[("General", "general", child)],
                    main_title="Test",
                )

                self.my_enable_listbox = enable_listbox
                self.my_stack = stack
                self._initializing = False

        grid = TestGrid()

        assert grid.my_enable_listbox is None
        assert grid.my_stack is not None


@pytest.mark.unit
class TestPreferencesGridBaseStackedPreferences:
    """Test PreferencesGridBase stacked drill-down preferences."""

    def test_create_stacked_preferences(self) -> None:
        """Test _create_stacked_preferences creates stack with categories and detail."""

        class TestGrid(PreferencesGridBase):
            """Test grid."""

            def __init__(self):
                super().__init__("Test")
                self.activated_row = None

                stack, categories, detail = self._create_stacked_preferences(
                    on_category_activated=self._on_category, on_detail_row_activated=None
                )
                self.my_stack = stack
                self.my_categories = categories
                self.my_detail = detail

            def _on_category(self, row):
                self.activated_row = row

        grid = TestGrid()

        assert grid.my_stack is not None
        assert grid.my_categories is not None
        assert grid.my_detail is not None
        assert isinstance(grid.my_stack, Gtk.Stack)
        assert isinstance(grid.my_categories, Gtk.ListBox)
        assert isinstance(grid.my_detail, Gtk.ListBox)

    def test_add_stack_category_row(self) -> None:
        """Test _add_stack_category_row adds category with correct properties."""

        class TestGrid(PreferencesGridBase):
            """Test grid."""

            def __init__(self):
                super().__init__("Test")
                _stack, categories, _detail = self._create_stacked_preferences(
                    on_category_activated=lambda r: None
                )
                self.my_categories = categories

        grid = TestGrid()

        row = grid._add_stack_category_row(grid.my_categories, "Speech Settings", category="speech")

        assert isinstance(row, CategoryListBoxRow)
        assert row.category == "speech"

    def test_add_stack_category_row_chevron_accessible_role(self) -> None:
        """Test _add_stack_category_row chevron has PUSH_BUTTON accessible role."""

        gi.require_version("Atk", "1.0")
        from gi.repository import Atk

        class TestGrid(PreferencesGridBase):
            """Test grid."""

            def __init__(self):
                super().__init__("Test")
                _stack, categories, _detail = self._create_stacked_preferences(
                    on_category_activated=lambda r: None
                )
                self.my_categories = categories

        grid = TestGrid()
        row = grid._add_stack_category_row(grid.my_categories, "Test Category", category="test")

        # Find the chevron image in the row's hbox
        hbox = row.get_child()
        chevron = None
        for child in hbox.get_children():
            if isinstance(child, Gtk.Image):
                chevron = child
                break

        assert chevron is not None, "Chevron image not found in category row"

        chevron_accessible = chevron.get_accessible()
        assert chevron_accessible is not None
        assert chevron_accessible.get_role() == Atk.Role.BUTTON
        assert chevron_accessible.get_name() == ""

    def test_show_stack_categories_and_detail(self) -> None:
        """Test _show_stack_categories and _show_stack_detail switch views."""

        class TestGrid(PreferencesGridBase):
            """Test grid."""

            def __init__(self):
                super().__init__("Test")
                stack, categories, detail = self._create_stacked_preferences(
                    on_category_activated=lambda r: None
                )
                self.my_stack = stack
                self.my_categories = categories
                self.my_detail = detail

        grid = TestGrid()

        grid.my_stack.show_all()  # pylint: disable=no-member

        cat_scrolled = grid.my_stack.get_child_by_name("categories")
        det_scrolled = grid.my_stack.get_child_by_name("detail")

        grid._show_stack_detail()
        assert grid.my_stack.get_visible_child() is det_scrolled

        grid._show_stack_categories()
        assert grid.my_stack.get_visible_child() is cat_scrolled
