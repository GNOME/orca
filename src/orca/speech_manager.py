# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
# Copyright 2011-2026 Igalia, S.L.
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
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=wrong-import-position
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
# pylint: disable=too-many-lines

"""Manages the speech engine: server, synthesizer, voice, and output parameters."""

from __future__ import annotations

import importlib
import locale
import queue
import threading
from enum import Enum
from typing import Any, TYPE_CHECKING

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GObject
from gi.repository import Gtk

from . import cmdnames
from . import command_manager
from . import dbus_service
from . import debug
from . import guilabels
from . import input_event
from . import keybindings
from . import messages
from . import preferences_grid_base
from . import presentation_manager
from . import settings
from . import settings_manager
from . import speech
from . import speechserver
from .acss import ACSS
from . import gsettings_registry

if TYPE_CHECKING:
    from .scripts import default
    from .speechserver import SpeechServer


@gsettings_registry.get_registry().gsettings_enum(
    "org.gnome.Orca.CapitalizationStyle",
    values={"none": 0, "spell": 1, "icon": 2},
)
class CapitalizationStyle(Enum):
    """Capitalization style enumeration with string values from settings."""

    NONE = settings.CAPITALIZATION_STYLE_NONE
    SPELL = settings.CAPITALIZATION_STYLE_SPELL
    ICON = settings.CAPITALIZATION_STYLE_ICON

    @property
    def string_name(self) -> str:
        """Returns the lowercase string name for this enum value."""

        return self.name.lower()


@gsettings_registry.get_registry().gsettings_enum(
    "org.gnome.Orca.PunctuationStyle",
    values={"all": 0, "most": 1, "some": 2, "none": 3},
)
class PunctuationStyle(Enum):
    """Punctuation style enumeration with int values from settings."""

    NONE = settings.PUNCTUATION_STYLE_NONE
    SOME = settings.PUNCTUATION_STYLE_SOME
    MOST = settings.PUNCTUATION_STYLE_MOST
    ALL = settings.PUNCTUATION_STYLE_ALL

    @property
    def string_name(self) -> str:
        """Returns the lowercase string name for this enum value."""

        return self.name.lower()


class VoicesPreferencesGrid(preferences_grid_base.PreferencesGridBase):
    """GtkGrid containing the Voice settings page."""

    class VoiceType(Enum):
        """Voice type enumeration for voice settings."""

        DEFAULT = 0
        UPPERCASE = 1
        HYPERLINK = 2
        SYSTEM = 3

    def __init__(self, manager: SpeechManager) -> None:
        super().__init__(guilabels.SPEECH)
        self._manager = manager
        self._initializing = True

        voices = settings.voices
        self._default_voice = ACSS(voices.get(settings.DEFAULT_VOICE, {}))
        self._uppercase_voice = ACSS(voices.get(settings.UPPERCASE_VOICE, {}))
        self._hyperlink_voice = ACSS(voices.get(settings.HYPERLINK_VOICE, {}))
        self._system_voice = ACSS(voices.get(settings.SYSTEM_VOICE, {}))

        # All voice family dicts from server
        self._voice_families: list[speechserver.VoiceFamily] = []
        # Filtered families for each voice type
        self._default_family_choices: list[speechserver.VoiceFamily] = []
        self._hyperlink_family_choices: list[speechserver.VoiceFamily] = []
        self._uppercase_family_choices: list[speechserver.VoiceFamily] = []
        self._system_family_choices: list[speechserver.VoiceFamily] = []

        self._speech_systems_combo: Gtk.ComboBox
        self._speech_synthesizers_combo: Gtk.ComboBox
        self._punctuation_combo: Gtk.ComboBox
        self._capitalization_combo: Gtk.ComboBox
        self._global_frame: Gtk.Frame | None = None
        self._voice_types_frame: Gtk.Frame | None = None

        # Default voice widgets (created on-demand in dialogs)
        self._default_languages_combo: Gtk.ComboBox | None = None
        self._default_families_combo: Gtk.ComboBox | None = None
        self._default_rate_scale: Gtk.Scale | None = None
        self._default_pitch_scale: Gtk.Scale | None = None
        self._default_volume_scale: Gtk.Scale | None = None

        # Hyperlink voice widgets (created on-demand in dialogs)
        self._hyperlink_languages_combo: Gtk.ComboBox | None = None
        self._hyperlink_families_combo: Gtk.ComboBox | None = None
        self._hyperlink_rate_scale: Gtk.Scale | None = None
        self._hyperlink_pitch_scale: Gtk.Scale | None = None
        self._hyperlink_volume_scale: Gtk.Scale | None = None

        # Uppercase voice widgets (created on-demand in dialogs)
        self._uppercase_languages_combo: Gtk.ComboBox | None = None
        self._uppercase_families_combo: Gtk.ComboBox | None = None
        self._uppercase_rate_scale: Gtk.Scale | None = None
        self._uppercase_pitch_scale: Gtk.Scale | None = None
        self._uppercase_volume_scale: Gtk.Scale | None = None

        # System voice widgets (created on-demand in dialogs)
        self._system_languages_combo: Gtk.ComboBox | None = None
        self._system_families_combo: Gtk.ComboBox | None = None
        self._system_rate_scale: Gtk.Scale | None = None
        self._system_pitch_scale: Gtk.Scale | None = None
        self._system_volume_scale: Gtk.Scale | None = None

        self._families_sorted: bool = False

        self._build()
        self._populate_speech_systems()
        self.refresh()

    def _build(self) -> None:
        """Create the Gtk widgets composing the grid."""

        row = 0

        self._global_frame, global_content = self._create_frame(
            guilabels.VOICE_GLOBAL_VOICE_SETTINGS, margin_top=12
        )

        punctuation_model = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_INT)
        punctuation_model.append(
            [guilabels.PUNCTUATION_STYLE_NONE, settings.PUNCTUATION_STYLE_NONE]
        )
        punctuation_model.append(
            [guilabels.PUNCTUATION_STYLE_SOME, settings.PUNCTUATION_STYLE_SOME]
        )
        punctuation_model.append(
            [guilabels.PUNCTUATION_STYLE_MOST, settings.PUNCTUATION_STYLE_MOST]
        )
        punctuation_model.append([guilabels.PUNCTUATION_STYLE_ALL, settings.PUNCTUATION_STYLE_ALL])

        capitalization_model = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_STRING)
        capitalization_model.append(
            [guilabels.CAPITALIZATION_STYLE_NONE, settings.CAPITALIZATION_STYLE_NONE]
        )
        capitalization_model.append(
            [guilabels.CAPITALIZATION_STYLE_ICON, settings.CAPITALIZATION_STYLE_ICON]
        )
        capitalization_model.append(
            [guilabels.CAPITALIZATION_STYLE_SPELL, settings.CAPITALIZATION_STYLE_SPELL]
        )

        global_listbox = preferences_grid_base.FocusManagedListBox()
        combo_size_group = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)

        row_data = [
            (
                guilabels.VOICE_SPEECH_SYSTEM,
                Gtk.ListStore(GObject.TYPE_STRING),
                self._on_speech_system_changed,
            ),
            (
                guilabels.VOICE_SPEECH_SYNTHESIZER,
                Gtk.ListStore(GObject.TYPE_STRING),
                self._on_speech_synthesizer_changed,
            ),
            (guilabels.PUNCTUATION_STYLE, punctuation_model, self._on_punctuation_changed),
            (
                guilabels.VOICE_CAPITALIZATION_STYLE,
                capitalization_model,
                self._on_capitalization_changed,
            ),
        ]

        global_combos = []
        for label_text, model, changed_handler in row_data:
            row_widget, combo, _label = self._create_combo_box_row(
                label_text, model, changed_handler, include_top_separator=False
            )
            combo_size_group.add_widget(combo)
            global_listbox.add_row_with_widget(row_widget, combo)
            global_combos.append(combo)

        self._speech_systems_combo = global_combos[0]
        self._speech_synthesizers_combo = global_combos[1]
        self._punctuation_combo = global_combos[2]
        self._capitalization_combo = global_combos[3]

        switch_data = [
            (
                guilabels.VOICE_SPEAK_NUMBERS_AS_DIGITS,
                self._on_speak_numbers_toggled,
                self._manager.get_speak_numbers_as_digits(),
            ),
            (
                guilabels.SPEECH_SPEAK_COLORS_AS_NAMES,
                self._on_use_color_names_toggled,
                self._manager.get_use_color_names(),
            ),
            (
                guilabels.SPEECH_BREAK_INTO_CHUNKS,
                self._on_enable_pause_breaks_toggled,
                self._manager.get_insert_pauses_between_utterances(),
            ),
            (
                guilabels.SPEECH_USE_PRONUNCIATION_DICTIONARY,
                self._on_use_pronunciation_dict_toggled,
                self._manager.get_use_pronunciation_dictionary(),
            ),
            (
                guilabels.AUTO_LANGUAGE_SWITCHING,
                self._on_auto_language_switching_toggled,
                self._manager.get_auto_language_switching(),
            ),
        ]

        switches = []
        for label_text, handler, state in switch_data:
            row_widget, switch, _label = self._create_switch_row(
                label_text, handler, state, include_top_separator=False
            )
            global_listbox.add_row_with_widget(row_widget, switch)
            switches.append(switch)

        self._speak_numbers_switch = switches[0]
        self._use_color_names_switch = switches[1]
        self._enable_pause_breaks_switch = switches[2]
        self._use_pronunciation_dict_switch = switches[3]
        self._auto_language_switching_switch = switches[4]

        global_content.add(global_listbox)  # pylint: disable=no-member
        self.attach(self._global_frame, 0, row, 1, 1)
        row += 1

        self._voice_types_frame, voice_types_content = self._create_frame(
            guilabels.VOICE_VOICE_TYPE_SETTINGS, margin_top=12
        )

        voice_types_listbox, voice_buttons = self._create_button_listbox(
            [
                (
                    guilabels.SPEECH_VOICE_TYPE_DEFAULT,
                    "applications-system-symbolic",
                    lambda _btn: self._show_voice_settings_dialog(self.VoiceType.DEFAULT),
                ),
                (
                    guilabels.SPEECH_VOICE_TYPE_HYPERLINK,
                    "applications-system-symbolic",
                    lambda _btn: self._show_voice_settings_dialog(self.VoiceType.HYPERLINK),
                ),
                (
                    guilabels.SPEECH_VOICE_TYPE_UPPERCASE,
                    "applications-system-symbolic",
                    lambda _btn: self._show_voice_settings_dialog(self.VoiceType.UPPERCASE),
                ),
                (
                    guilabels.SPEECH_VOICE_TYPE_SYSTEM,
                    "applications-system-symbolic",
                    lambda _btn: self._show_voice_settings_dialog(self.VoiceType.SYSTEM),
                ),
            ]
        )

        voice_type_labels = [
            guilabels.SPEECH_VOICE_TYPE_DEFAULT,
            guilabels.SPEECH_VOICE_TYPE_HYPERLINK,
            guilabels.SPEECH_VOICE_TYPE_UPPERCASE,
            guilabels.SPEECH_VOICE_TYPE_SYSTEM,
        ]
        for button, voice_label in zip(voice_buttons, voice_type_labels):
            accessible_name = guilabels.VOICE_TYPE_SETTINGS % voice_label
            button.set_tooltip_text(accessible_name)
            accessible = button.get_accessible()
            if accessible:
                accessible.set_name(accessible_name)

        voice_types_content.add(voice_types_listbox)  # pylint: disable=no-member
        self.attach(self._voice_types_frame, 0, row, 1, 1)

        self.show_all()

    def _show_voice_settings_dialog(self, voice_type: VoicesPreferencesGrid.VoiceType) -> None:
        """Show a dialog for editing settings for a specific voice type."""

        voice_type_labels = {
            self.VoiceType.DEFAULT: guilabels.SPEECH_VOICE_TYPE_DEFAULT,
            self.VoiceType.HYPERLINK: guilabels.SPEECH_VOICE_TYPE_HYPERLINK,
            self.VoiceType.UPPERCASE: guilabels.SPEECH_VOICE_TYPE_UPPERCASE,
            self.VoiceType.SYSTEM: guilabels.SPEECH_VOICE_TYPE_SYSTEM,
        }
        title = voice_type_labels.get(voice_type, "Voice Settings")

        # Save current ACSS state in case user cancels
        voice_acss = self._get_acss_for_voice_type(voice_type)
        saved_acss = ACSS(dict(voice_acss))

        dialog, ok_button = self._create_header_bar_dialog(
            title, guilabels.BTN_CANCEL, guilabels.BTN_OK
        )

        content_area = dialog.get_content_area()

        voice_listbox = preferences_grid_base.FocusManagedListBox()
        combo_size_group = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)

        def on_language_changed(widget: Gtk.ComboBox) -> None:
            self._on_speech_language_changed(widget, voice_type)

        lang_row, lang_combo, _lang_label = self._create_combo_box_row(
            guilabels.VOICE_LANGUAGE,
            Gtk.ListStore(GObject.TYPE_STRING),
            on_language_changed,
            include_top_separator=False,
        )
        combo_size_group.add_widget(lang_combo)
        voice_listbox.add_row_with_widget(lang_row, lang_combo)

        def on_family_changed(widget: Gtk.ComboBox) -> None:
            self._on_speech_family_changed(widget, voice_type)

        person_row, person_combo, _person_label = self._create_combo_box_row(
            guilabels.VOICE_PERSON,
            Gtk.ListStore(GObject.TYPE_STRING),
            on_family_changed,
            include_top_separator=False,
        )
        combo_size_group.add_widget(person_combo)
        voice_listbox.add_row_with_widget(person_row, person_combo)

        def on_rate_changed(widget: Gtk.Scale) -> None:
            self._on_rate_changed(widget, voice_type)

        rate_adj = Gtk.Adjustment(value=50, lower=0, upper=100, step_increment=1, page_increment=10)
        rate_row, rate_scale, _rate_label = self._create_slider_row(
            guilabels.VOICE_RATE,
            rate_adj,
            changed_handler=on_rate_changed,
            include_top_separator=False,
        )
        voice_listbox.add_row_with_widget(rate_row, rate_scale)

        def on_pitch_changed(widget: Gtk.Scale) -> None:
            self._on_pitch_changed(widget, voice_type)

        pitch_adj = Gtk.Adjustment(
            value=5.0, lower=0, upper=10, step_increment=0.1, page_increment=1
        )
        pitch_row, pitch_scale, _pitch_label = self._create_slider_row(
            guilabels.VOICE_PITCH,
            pitch_adj,
            changed_handler=on_pitch_changed,
            include_top_separator=False,
        )
        voice_listbox.add_row_with_widget(pitch_row, pitch_scale)

        def on_volume_changed(widget: Gtk.Scale) -> None:
            self._on_volume_changed(widget, voice_type)

        volume_adj = Gtk.Adjustment(
            value=10.0, lower=0, upper=10, step_increment=0.1, page_increment=1
        )
        volume_row, volume_scale, _volume_label = self._create_slider_row(
            guilabels.VOICE_VOLUME,
            volume_adj,
            changed_handler=on_volume_changed,
            include_top_separator=False,
        )
        voice_listbox.add_row_with_widget(volume_row, volume_scale)

        languages_combo = lang_combo
        families_combo = person_combo

        if voice_type == self.VoiceType.DEFAULT:
            self._default_languages_combo = languages_combo
            self._default_families_combo = families_combo
            self._default_rate_scale = rate_scale
            self._default_pitch_scale = pitch_scale
            self._default_volume_scale = volume_scale
        elif voice_type == self.VoiceType.HYPERLINK:
            self._hyperlink_languages_combo = languages_combo
            self._hyperlink_families_combo = families_combo
            self._hyperlink_rate_scale = rate_scale
            self._hyperlink_pitch_scale = pitch_scale
            self._hyperlink_volume_scale = volume_scale
        elif voice_type == self.VoiceType.UPPERCASE:
            self._uppercase_languages_combo = languages_combo
            self._uppercase_families_combo = families_combo
            self._uppercase_rate_scale = rate_scale
            self._uppercase_pitch_scale = pitch_scale
            self._uppercase_volume_scale = volume_scale
        elif voice_type == self.VoiceType.SYSTEM:
            self._system_languages_combo = languages_combo
            self._system_families_combo = families_combo
            self._system_rate_scale = rate_scale
            self._system_pitch_scale = pitch_scale
            self._system_volume_scale = volume_scale

        self._populate_languages_for_voice_type(voice_type)
        self._populate_families_for_voice_type(voice_type, apply_changes=False)

        self._initializing = True
        self._refresh_voice_widgets(voice_type, rate_scale, pitch_scale, volume_scale)
        self._initializing = False

        def on_response(dlg, response_id):
            if response_id in (Gtk.ResponseType.CANCEL, Gtk.ResponseType.DELETE_EVENT):
                # User cancelled - revert local copy and sync to settings.voices
                voice_acss.clear()
                voice_acss.update(saved_acss)
                self._sync_voice_to_settings(voice_type)
            else:
                # User clicked OK - changes already applied and synced
                self._has_unsaved_changes = True

            dlg.destroy()

        dialog.connect("response", on_response)

        parent = self.get_toplevel()  # pylint: disable=no-member

        def on_parent_destroy(*_args):
            if not dialog.get_property("visible"):
                return
            # Trigger cancel response which will clean up and destroy the dialog
            dialog.response(Gtk.ResponseType.DELETE_EVENT)

        parent.connect("destroy", on_parent_destroy)

        content_area.pack_start(voice_listbox, True, True, 0)
        dialog.show_all()  # pylint: disable=no-member
        ok_button.grab_default()

    # TODO - JD: Remove this function if it continues to prove unnecessary
    # pylint: disable-next=useless-parent-delegation
    def has_changes(self) -> bool:
        """Return True if there are unsaved changes."""

        return super().has_changes()

    def reload(self) -> None:
        """Reload settings from manager and refresh the UI."""

        voices = settings.voices
        self._default_voice = ACSS(voices.get(settings.DEFAULT_VOICE, {}))
        self._uppercase_voice = ACSS(voices.get(settings.UPPERCASE_VOICE, {}))
        self._hyperlink_voice = ACSS(voices.get(settings.HYPERLINK_VOICE, {}))
        self._system_voice = ACSS(voices.get(settings.SYSTEM_VOICE, {}))

        self._voice_families = self._manager.get_voice_families()
        self._families_sorted = False

        self._has_unsaved_changes = False
        self.refresh()

    def save_settings(self) -> dict[str, dict | list | int | str | bool]:
        """Save settings and return a dictionary of the current values for those settings."""

        result: dict[str, dict | list | int | str | bool] = {
            "voices": {
                settings.DEFAULT_VOICE: dict(self._default_voice),
                settings.UPPERCASE_VOICE: dict(self._uppercase_voice),
                settings.HYPERLINK_VOICE: dict(self._hyperlink_voice),
                settings.SYSTEM_VOICE: dict(self._system_voice),
            }
        }

        server_name = self._manager.get_current_server()
        synthesizer_id = self._manager.get_current_synthesizer()
        result["speechServerInfo"] = [server_name, synthesizer_id]
        result["speechServerFactory"] = settings.speechServerFactory

        result["verbalizePunctuationStyle"] = settings.verbalizePunctuationStyle
        result["capitalizationStyle"] = settings.capitalizationStyle

        result["speakNumbersAsDigits"] = self._manager.get_speak_numbers_as_digits()
        result["useColorNames"] = self._manager.get_use_color_names()
        result["enablePauseBreaks"] = self._manager.get_insert_pauses_between_utterances()
        result["usePronunciationDictionary"] = self._manager.get_use_pronunciation_dictionary()
        result["enableAutoLanguageSwitching"] = self._manager.get_auto_language_switching()

        self._has_unsaved_changes = False
        return result

    def refresh(self) -> None:
        """Update widget states to reflect current settings."""

        self._initializing = True

        self._populate_speech_systems()

        model = self._punctuation_combo.get_model()
        if model:
            for i, row in enumerate(model):
                if row[1] == settings.verbalizePunctuationStyle:
                    self._punctuation_combo.set_active(i)
                    break

        model = self._capitalization_combo.get_model()
        if model:
            for i, row in enumerate(model):
                if row[1] == settings.capitalizationStyle:
                    self._capitalization_combo.set_active(i)
                    break

        self._speak_numbers_switch.set_active(self._manager.get_speak_numbers_as_digits())
        self._use_color_names_switch.set_active(self._manager.get_use_color_names())
        self._enable_pause_breaks_switch.set_active(
            self._manager.get_insert_pauses_between_utterances()
        )
        self._use_pronunciation_dict_switch.set_active(
            self._manager.get_use_pronunciation_dictionary()
        )
        self._auto_language_switching_switch.set_active(self._manager.get_auto_language_switching())

        # Note: Voice type widgets are created on-demand in dialogs, so no need to refresh them here

        self._initializing = False

    def _refresh_voice_widgets(
        self,
        voice_type: VoicesPreferencesGrid.VoiceType,
        rate_scale: Gtk.Scale,
        pitch_scale: Gtk.Scale,
        volume_scale: Gtk.Scale,
    ) -> None:
        """Update widgets for a specific voice type."""

        voice_acss = self._get_acss_for_voice_type(voice_type)

        rate = voice_acss.get(ACSS.RATE, 50)
        rate_scale.set_value(rate)

        pitch = voice_acss.get(ACSS.AVERAGE_PITCH, 5.0)
        pitch_scale.set_value(pitch)

        volume = voice_acss.get(ACSS.GAIN, 10.0)
        volume_scale.set_value(volume)

    def _get_acss_for_voice_type(self, voice_type: VoicesPreferencesGrid.VoiceType) -> ACSS:
        """Return the local ACSS copy for the given voice type."""

        if voice_type == self.VoiceType.DEFAULT:
            return self._default_voice
        if voice_type == self.VoiceType.UPPERCASE:
            return self._uppercase_voice
        if voice_type == self.VoiceType.HYPERLINK:
            return self._hyperlink_voice
        if voice_type == self.VoiceType.SYSTEM:
            return self._system_voice
        return self._default_voice

    def _get_widgets_for_voice_type(
        self, voice_type: VoicesPreferencesGrid.VoiceType
    ) -> tuple[Gtk.ComboBox, Gtk.ComboBox, list[speechserver.VoiceFamily]]:
        """Return the widgets and family choices for a given voice type."""

        if voice_type == self.VoiceType.DEFAULT:
            return (
                self._default_languages_combo,
                self._default_families_combo,
                self._default_family_choices,
            )
        if voice_type == self.VoiceType.HYPERLINK:
            return (
                self._hyperlink_languages_combo,
                self._hyperlink_families_combo,
                self._hyperlink_family_choices,
            )
        if voice_type == self.VoiceType.UPPERCASE:
            return (
                self._uppercase_languages_combo,
                self._uppercase_families_combo,
                self._uppercase_family_choices,
            )
        if voice_type == self.VoiceType.SYSTEM:
            return (
                self._system_languages_combo,
                self._system_families_combo,
                self._system_family_choices,
            )
        return (
            self._default_languages_combo,
            self._default_families_combo,
            self._default_family_choices,
        )

    def _set_family_choices_for_voice_type(
        self, voice_type: VoicesPreferencesGrid.VoiceType, choices: list[speechserver.VoiceFamily]
    ) -> None:
        """Set the family choices for a given voice type."""

        if voice_type == self.VoiceType.DEFAULT:
            self._default_family_choices = choices
        elif voice_type == self.VoiceType.HYPERLINK:
            self._hyperlink_family_choices = choices
        elif voice_type == self.VoiceType.UPPERCASE:
            self._uppercase_family_choices = choices
        elif voice_type == self.VoiceType.SYSTEM:
            self._system_family_choices = choices

    def _populate_speech_systems(self) -> None:
        """Populate the speech systems combo."""

        self._initializing = True

        model = self._speech_systems_combo.get_model()
        if not model:
            model = Gtk.ListStore(str)
        self._speech_systems_combo.set_model(None)
        model.clear()

        available = self._manager.get_available_servers()
        for server_name in available:
            model.append([server_name])

        self._speech_systems_combo.set_model(model)

        current = self._manager.get_current_server()
        found = False
        selected_server = None
        for i, row in enumerate(model):
            if row[0] == current:
                self._speech_systems_combo.set_active(i)
                selected_server = current
                found = True
                break

        if not found and len(model) > 0:
            self._speech_systems_combo.set_active(0)
            tree_iter = model.get_iter_first()
            if tree_iter:
                selected_server = model.get_value(tree_iter, 0)

        if selected_server:
            self._manager.set_current_server(selected_server)

        self._initializing = False
        self._populate_speech_synthesizers()

    def _populate_speech_synthesizers(self) -> None:
        """Populate the speech synthesizers combo."""

        self._initializing = True

        model = self._speech_synthesizers_combo.get_model()
        if not model:
            model = Gtk.ListStore(str)
        self._speech_synthesizers_combo.set_model(None)
        model.clear()

        available = self._manager.get_available_synthesizers()
        for synth_name in available:
            model.append([synth_name])

        self._speech_synthesizers_combo.set_model(model)

        current = self._manager.get_current_synthesizer()
        found = False
        selected_synth = None
        for i, row in enumerate(model):
            if row[0] == current:
                self._speech_synthesizers_combo.set_active(i)
                selected_synth = current
                found = True
                break

        if not found and len(model) > 0:
            self._speech_synthesizers_combo.set_active(0)
            tree_iter = model.get_iter_first()
            if tree_iter:
                selected_synth = model.get_value(tree_iter, 0)

        if selected_synth:
            self._manager.set_current_synthesizer(selected_synth)

        self._voice_families = self._manager.get_voice_families()
        self._initializing = False
        # Note: Voice widgets are created on-demand in dialogs, so we don't populate them here

    def _populate_languages_for_voice_type(
        self, voice_type: VoicesPreferencesGrid.VoiceType
    ) -> None:
        """Populate the languages combo for a specific voice type."""

        languages_combo, _, _ = self._get_widgets_for_voice_type(voice_type)

        self._initializing = True

        model = languages_combo.get_model()
        if not model:
            model = Gtk.ListStore(str, str)
        languages_combo.set_model(None)
        model.clear()

        if len(self._voice_families) == 0:
            languages_combo.set_model(model)
            self._initializing = False
            return

        if not self._families_sorted:
            default_marker = guilabels.SPEECH_DEFAULT_VOICE.replace("%s", "").strip().lower()

            def _get_sort_key(family):
                variant = family.get(speechserver.VoiceFamily.VARIANT)
                name = family.get(speechserver.VoiceFamily.NAME, "")
                if default_marker in name.lower() or "default" in name.lower():
                    return (0, "")
                if variant not in (None, "none", "None"):
                    return (1, variant.lower())
                return (1, name.lower())

            self._voice_families.sort(key=_get_sort_key)
            self._families_sorted = True

        done = {}
        languages = []
        for family in self._voice_families:
            lang = family.get(speechserver.VoiceFamily.LANG, "")
            dialect = family.get(speechserver.VoiceFamily.DIALECT, "")

            if (lang, dialect) in done:
                continue
            done[(lang, dialect)] = True

            if dialect:
                language = f"{lang}-{dialect}"
            else:
                language = lang

            msg = language if language else "default language"
            languages.append(language)
            model.append([msg])

        languages_combo.set_model(model)

        voice_acss = self._get_acss_for_voice_type(voice_type)
        saved_family: speechserver.VoiceFamily | None = voice_acss.get(ACSS.FAMILY)
        selected_index = 0
        saved_language = ""

        if saved_family:
            lang = saved_family.get(speechserver.VoiceFamily.LANG, "")
            dialect = saved_family.get(speechserver.VoiceFamily.DIALECT, "")
            if dialect:
                saved_language = f"{lang}-{dialect}"
            else:
                saved_language = lang
        elif voice_type == self.VoiceType.DEFAULT:
            family_locale, _encoding = locale.getlocale(locale.LC_MESSAGES)
            if family_locale:
                locale_parts = family_locale.split("_")
                lang = locale_parts[0]
                dialect = locale_parts[1] if len(locale_parts) > 1 else ""
                saved_language = f"{lang}-{dialect}" if dialect else lang

        if saved_language:
            lang_only = saved_language.partition("-")[0]
            partial_match = -1
            for i, language in enumerate(languages):
                if language == saved_language:
                    selected_index = i
                    break
                if partial_match < 0:
                    if language == lang_only or language.startswith(f"{lang_only}-"):
                        partial_match = i
            else:
                if partial_match >= 0:
                    selected_index = partial_match

        if len(languages) > 0:
            languages_combo.set_active(selected_index)

        self._initializing = False

    def _populate_families_for_voice_type(
        self, voice_type: VoicesPreferencesGrid.VoiceType, apply_changes: bool = True
    ) -> None:
        """Populate the families/persons combo for a specific voice type."""

        languages_combo, families_combo, _ = self._get_widgets_for_voice_type(voice_type)

        self._initializing = True

        families_model = families_combo.get_model()
        if not families_model:
            families_model = Gtk.ListStore(str, str)
        families_combo.set_model(None)
        families_model.clear()

        active = languages_combo.get_active()
        if active < 0:
            families_combo.set_model(families_model)
            self._initializing = False
            return

        languages_model = languages_combo.get_model()
        tree_iter = languages_model.get_iter(active)
        current_language = languages_model.get_value(tree_iter, 0)

        family_choices = []
        for family in self._voice_families:
            lang = family.get(speechserver.VoiceFamily.LANG, "")
            dialect = family.get(speechserver.VoiceFamily.DIALECT, "")

            if dialect:
                language = f"{lang}-{dialect}"
            else:
                language = lang

            if language != current_language:
                continue

            name = family.get(speechserver.VoiceFamily.NAME, "")
            variant = family.get(speechserver.VoiceFamily.VARIANT, "")

            # Show variant if it exists and is not "none", otherwise show name
            display_name = name
            if variant and variant not in ("none", "None"):
                display_name = variant

            family_choices.append(family)
            families_model.append([display_name])

        families_combo.set_model(families_model)

        self._set_family_choices_for_voice_type(voice_type, family_choices)

        voice_acss = self._get_acss_for_voice_type(voice_type)
        saved_family: speechserver.VoiceFamily | None = voice_acss.get(ACSS.FAMILY)
        selected_index = 0

        if saved_family and len(family_choices) > 0:
            saved_name = saved_family.get(speechserver.VoiceFamily.NAME, "")

            for i, family in enumerate(family_choices):
                family_name = family.get(speechserver.VoiceFamily.NAME, "")
                if family_name == saved_name:
                    selected_index = i
                    break

        if len(family_choices) > 0:
            families_combo.set_active(selected_index)

            if apply_changes:
                family = family_choices[selected_index]
                voice_name = family.get(speechserver.VoiceFamily.NAME, "")

                voice_acss[ACSS.FAMILY] = family
                voice_acss["established"] = True

                # Sync to settings.voices so the voice change is heard immediately
                self._sync_voice_to_settings(voice_type)

                # Only set as current voice if this is the default voice type
                if voice_type == self.VoiceType.DEFAULT:
                    self._manager.set_current_voice(voice_name)

        self._initializing = False

    def _sync_voice_to_settings(self, voice_type: VoicesPreferencesGrid.VoiceType) -> None:
        """Sync local voice copy to settings.voices for immediate preview."""

        voice_map = {
            self.VoiceType.DEFAULT: (self._default_voice, settings.DEFAULT_VOICE),
            self.VoiceType.UPPERCASE: (self._uppercase_voice, settings.UPPERCASE_VOICE),
            self.VoiceType.HYPERLINK: (self._hyperlink_voice, settings.HYPERLINK_VOICE),
            self.VoiceType.SYSTEM: (self._system_voice, settings.SYSTEM_VOICE),
        }

        local_voice, settings_key = voice_map[voice_type]
        settings.voices[settings_key] = ACSS(local_voice)

        server = self._manager.get_server()
        if server is not None:
            if settings_key == settings.DEFAULT_VOICE:
                server.set_default_voice(settings.voices[settings_key])
            server.clear_cached_voice_properties()

    def _on_rate_changed(
        self, widget: Gtk.Scale, voice_type: VoicesPreferencesGrid.VoiceType
    ) -> None:
        """Handle rate slider change for a specific voice type."""

        if self._initializing:
            return

        rate = widget.get_value()
        voice_acss = self._get_acss_for_voice_type(voice_type)
        voice_acss[ACSS.RATE] = rate
        voice_acss["established"] = True
        self._sync_voice_to_settings(voice_type)
        self._has_unsaved_changes = True

    def _on_pitch_changed(
        self, widget: Gtk.Scale, voice_type: VoicesPreferencesGrid.VoiceType
    ) -> None:
        """Handle pitch slider change for a specific voice type."""

        if self._initializing:
            return

        pitch = widget.get_value()
        voice_acss = self._get_acss_for_voice_type(voice_type)
        voice_acss[ACSS.AVERAGE_PITCH] = pitch
        voice_acss["established"] = True
        self._sync_voice_to_settings(voice_type)
        self._has_unsaved_changes = True

    def _on_volume_changed(
        self, widget: Gtk.Scale, voice_type: VoicesPreferencesGrid.VoiceType
    ) -> None:
        """Handle volume slider change for a specific voice type."""

        if self._initializing:
            return

        volume = widget.get_value()
        voice_acss = self._get_acss_for_voice_type(voice_type)
        voice_acss[ACSS.GAIN] = volume
        voice_acss["established"] = True
        self._sync_voice_to_settings(voice_type)
        self._has_unsaved_changes = True

    def _on_punctuation_changed(self, widget: Gtk.ComboBox) -> None:
        """Handle punctuation combo box change."""

        if self._initializing:
            return

        active = widget.get_active()
        if active < 0:
            return

        model = widget.get_model()
        tree_iter = model.get_iter(active)
        level = model.get_value(tree_iter, 1)

        settings.verbalizePunctuationStyle = level
        gsettings_registry.get_registry().set_runtime_value(
            "speech", "punctuation-level", PunctuationStyle(level).string_name
        )
        self._manager.update_punctuation_level()
        self._has_unsaved_changes = True

    def _on_capitalization_changed(self, widget: Gtk.ComboBox) -> None:
        """Handle capitalization combo box change."""

        if self._initializing:
            return

        active = widget.get_active()
        if active < 0:
            return

        model = widget.get_model()
        tree_iter = model.get_iter(active)
        style = model.get_value(tree_iter, 1)

        settings.capitalizationStyle = style
        gsettings_registry.get_registry().set_runtime_value(
            "speech", "capitalization-style", CapitalizationStyle(style).string_name
        )
        self._manager.update_capitalization_style()
        self._has_unsaved_changes = True

    def _on_speak_numbers_toggled(self, switch: Gtk.Switch, _state: Any) -> None:
        """Handle speak numbers as digits switch change."""
        if self._initializing:
            return
        self._manager.set_speak_numbers_as_digits(switch.get_active())
        self._has_unsaved_changes = True

    def _on_use_color_names_toggled(self, switch: Gtk.Switch, _state: Any) -> None:
        """Handle use color names switch change."""
        if self._initializing:
            return
        self._manager.set_use_color_names(switch.get_active())
        self._has_unsaved_changes = True

    def _on_enable_pause_breaks_toggled(self, switch: Gtk.Switch, _state: Any) -> None:
        """Handle enable pause breaks switch change."""
        if self._initializing:
            return
        self._manager.set_insert_pauses_between_utterances(switch.get_active())
        self._has_unsaved_changes = True

    def _on_use_pronunciation_dict_toggled(self, switch: Gtk.Switch, _state: Any) -> None:
        """Handle use pronunciation dictionary switch change."""
        if self._initializing:
            return
        self._manager.set_use_pronunciation_dictionary(switch.get_active())
        self._has_unsaved_changes = True

    def _on_auto_language_switching_toggled(self, switch: Gtk.Switch, _state: Any) -> None:
        """Handle auto language switching switch change."""
        if self._initializing:
            return
        self._manager.set_auto_language_switching(switch.get_active())
        self._has_unsaved_changes = True

    def _on_speech_system_changed(self, widget: Gtk.ComboBox) -> None:
        """Handle speech system combo change."""

        if self._initializing:
            return

        active = widget.get_active()
        if active < 0:
            return

        model = widget.get_model()
        tree_iter = model.get_iter(active)
        server_name = model.get_value(tree_iter, 0)

        self._manager.set_current_server(server_name)

        self._populate_speech_synthesizers()
        self._has_unsaved_changes = True

    def _on_speech_synthesizer_changed(self, widget: Gtk.ComboBox) -> None:
        """Handle speech synthesizer combo change."""

        if self._initializing:
            return

        active = widget.get_active()
        if active < 0:
            return

        model = widget.get_model()
        tree_iter = model.get_iter(active)
        synth_name = model.get_value(tree_iter, 0)

        self._manager.set_current_synthesizer(synth_name)

        self._voice_families = self._manager.get_voice_families()
        self._families_sorted = False

        # Clear family for all voice types when synthesizer changes
        for voice_type in [
            self.VoiceType.DEFAULT,
            self.VoiceType.HYPERLINK,
            self.VoiceType.UPPERCASE,
            self.VoiceType.SYSTEM,
        ]:
            voice_acss = self._get_acss_for_voice_type(voice_type)
            if ACSS.FAMILY in voice_acss:
                del voice_acss[ACSS.FAMILY]

        self._has_unsaved_changes = True

    def _on_speech_language_changed(
        self, widget: Gtk.ComboBox, voice_type: VoicesPreferencesGrid.VoiceType
    ) -> None:
        """Handle speech language combo change for a specific voice type."""

        if self._initializing:
            return

        self._populate_families_for_voice_type(voice_type)
        self._has_unsaved_changes = True

        if voice_type == self.VoiceType.DEFAULT:
            self._propagate_language_to_other_voices(widget)

    def _propagate_language_to_other_voices(self, _language_combo: Gtk.ComboBox) -> None:
        """Update other voice types to use the same voice family as the Default voice."""

        default_voice = self._get_acss_for_voice_type(self.VoiceType.DEFAULT)
        default_family = default_voice.get(ACSS.FAMILY)
        if not default_family:
            return

        voice_types = [self.VoiceType.HYPERLINK, self.VoiceType.UPPERCASE, self.VoiceType.SYSTEM]
        for voice_type in voice_types:
            voice_acss = self._get_acss_for_voice_type(voice_type)
            voice_acss[ACSS.FAMILY] = default_family
            voice_acss["established"] = True
            self._sync_voice_to_settings(voice_type)

    def _on_speech_family_changed(
        self, widget: Gtk.ComboBox, voice_type: VoicesPreferencesGrid.VoiceType
    ) -> None:
        """Handle speech family combo change for a specific voice type."""

        if self._initializing:
            return

        _, _, family_choices = self._get_widgets_for_voice_type(voice_type)

        active = widget.get_active()
        if active < 0 or active >= len(family_choices):
            return

        family = family_choices[active]
        voice_name = family.get(speechserver.VoiceFamily.NAME, "")

        voice_acss = self._get_acss_for_voice_type(voice_type)
        voice_acss[ACSS.FAMILY] = family
        voice_acss["established"] = True
        self._sync_voice_to_settings(voice_type)

        # Only set as current voice if this is the default voice type
        if voice_type == self.VoiceType.DEFAULT:
            self._manager.set_current_voice(voice_name)

        self._has_unsaved_changes = True


@gsettings_registry.get_registry().gsettings_schema("org.gnome.Orca.Speech", name="speech")
@gsettings_registry.get_registry().gsettings_schema("org.gnome.Orca.Voice", name="voice")
class SpeechManager:
    """Manages the speech engine: server, synthesizer, voice, and output parameters."""

    _SPEECH_SCHEMA = "speech"
    _VOICE_SCHEMA = "voice"

    def _get_setting(self, key: str, gtype: str, fallback: Any) -> Any:
        """Returns the dconf value for key, or fallback if not in dconf."""

        return gsettings_registry.get_registry().layered_lookup(
            self._SPEECH_SCHEMA, key, gtype, fallback=fallback
        )

    def __init__(self) -> None:
        self._families_sorted: bool = False
        self._initialized: bool = False
        self._server: SpeechServer | None = None

        msg = "SPEECH MANAGER: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("SpeechManager", self)

    def set_up_commands(self) -> None:
        """Sets up commands with CommandManager."""

        if self._initialized:
            return
        self._initialized = True

        manager = command_manager.get_manager()
        group_label = guilabels.KB_GROUP_SPEECH_VERBOSITY

        # Common keybindings (same for desktop and laptop)
        kb_s = keybindings.KeyBinding("s", keybindings.ORCA_MODIFIER_MASK)

        # (name, function, description, desktop_kb, laptop_kb)
        commands_data = [
            (
                "cycleCapitalizationStyleHandler",
                self.cycle_capitalization_style,
                cmdnames.CYCLE_CAPITALIZATION_STYLE,
                None,
                None,
            ),
            (
                "cycleSpeakingPunctuationLevelHandler",
                self.cycle_punctuation_level,
                cmdnames.CYCLE_PUNCTUATION_LEVEL,
                None,
                None,
            ),
            (
                "cycleSynthesizerHandler",
                self.cycle_synthesizer,
                cmdnames.CYCLE_SYNTHESIZER,
                None,
                None,
            ),
            ("toggleSilenceSpeechHandler", self.toggle_speech, cmdnames.TOGGLE_SPEECH, kb_s, kb_s),
            (
                "decreaseSpeechRateHandler",
                self.decrease_rate,
                cmdnames.DECREASE_SPEECH_RATE,
                None,
                None,
            ),
            (
                "increaseSpeechRateHandler",
                self.increase_rate,
                cmdnames.INCREASE_SPEECH_RATE,
                None,
                None,
            ),
            (
                "decreaseSpeechPitchHandler",
                self.decrease_pitch,
                cmdnames.DECREASE_SPEECH_PITCH,
                None,
                None,
            ),
            (
                "increaseSpeechPitchHandler",
                self.increase_pitch,
                cmdnames.INCREASE_SPEECH_PITCH,
                None,
                None,
            ),
            (
                "decreaseSpeechVolumeHandler",
                self.decrease_volume,
                cmdnames.DECREASE_SPEECH_VOLUME,
                None,
                None,
            ),
            (
                "increaseSpeechVolumeHandler",
                self.increase_volume,
                cmdnames.INCREASE_SPEECH_VOLUME,
                None,
                None,
            ),
        ]

        for name, function, description, desktop_kb, laptop_kb in commands_data:
            manager.add_command(
                command_manager.KeyboardCommand(
                    name,
                    function,
                    group_label,
                    description,
                    desktop_keybinding=desktop_kb,
                    laptop_keybinding=laptop_kb,
                )
            )

        msg = "SPEECH MANAGER: Commands set up."
        debug.print_message(debug.LEVEL_INFO, msg, True)

    def get_server(self) -> SpeechServer | None:
        """Returns the speech server instance, or None if not initialized."""

        return self._server

    def _get_server(self) -> SpeechServer | None:
        """Returns the speech server if it is responsive.."""

        result = self._server
        if result is None:
            msg = "SPEECH MANAGER: Speech server is None."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return None

        result_queue: queue.Queue[bool] = queue.Queue()

        def health_check_thread():
            result.get_output_module()
            result_queue.put(True)

        thread = threading.Thread(target=health_check_thread, daemon=True)
        thread.start()

        try:
            result_queue.get(timeout=2.0)
        except queue.Empty:
            msg = "SPEECH MANAGER: Speech server health check timed out"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return None

        tokens = ["SPEECH MANAGER: Speech server is", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    def _get_available_servers(self) -> list[str]:
        """Returns a list of available speech servers."""

        return list(self._get_server_module_map().keys())

    def _get_server_module_map(self) -> dict[str, str]:
        """Returns a mapping of server names to module names."""

        result = {}
        for module_name in settings.speechFactoryModules:
            try:
                factory = importlib.import_module(f"orca.{module_name}")
            except ImportError:
                try:
                    factory = importlib.import_module(module_name)
                except ImportError:
                    continue

            try:
                speech_server_class = factory.SpeechServer
                if server_name := speech_server_class.get_factory_name():
                    result[server_name] = module_name

            except (AttributeError, TypeError, ImportError) as error:
                tokens = [f"SPEECH MANAGER: {module_name} not available:", error]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return result

    def _switch_server(self, target_server: str) -> bool:
        """Switches to the specified server."""

        server_module_map = self._get_server_module_map()
        target_module = server_module_map.get(target_server)
        if not target_module:
            return False

        self.shutdown_speech()
        settings.speechServerFactory = target_module
        gsettings_registry.get_registry().set_runtime_value(
            "speech", "speech-server-factory", target_module
        )
        self.start_speech()
        return self.get_current_server() == target_server

    @dbus_service.getter
    def get_available_servers(self) -> list[str]:
        """Returns a list of available servers."""

        result = self._get_available_servers()
        msg = f"SPEECH MANAGER: Available servers: {result}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    @gsettings_registry.get_registry().gsetting(
        key="speech-server",
        schema="speech",
        gtype="s",
        default="",
        summary="Speech server name",
    )
    @dbus_service.getter
    def get_current_server(self) -> str:
        """Returns the name of the current speech server (Speech Dispatcher or Spiel)."""

        server = self._get_server()
        if server is None:
            msg = "SPEECH MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return ""

        name = server.get_factory_name()
        msg = f"SPEECH MANAGER: Server is: {name}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return name

    @dbus_service.setter
    def set_current_server(self, value: str) -> bool:
        """Sets the current speech server (e.g. Speech Dispatcher or Spiel)."""

        return self._switch_server(value)

    @gsettings_registry.get_registry().gsetting(
        key="speech-server-factory",
        schema="speech",
        gtype="s",
        default="speechdispatcherfactory",
        summary="Speech server factory module",
        settings_key="speechServerFactory",
    )
    def get_speech_server_factory(self) -> str:
        """Returns the speech server factory module name."""

        return self._get_setting("speech-server-factory", "s", settings.speechServerFactory)

    @gsettings_registry.get_registry().gsetting(
        key="synthesizer", schema="speech", gtype="s", default="", summary="Speech synthesizer"
    )
    @dbus_service.getter
    def get_current_synthesizer(self) -> str:
        """Returns the current synthesizer of the speech server."""

        server = self._get_server()
        if server is None:
            msg = "SPEECH MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return ""

        result = server.get_output_module()
        msg = f"SPEECH MANAGER: Synthesizer is: {result}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    @dbus_service.setter
    def set_current_synthesizer(self, value: str) -> bool:
        """Sets the current synthesizer of the active speech server."""

        server = self._get_server()
        if server is None:
            msg = "SPEECH MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        available = self.get_available_synthesizers()
        if value not in available:
            tokens = [f"SPEECH MANAGER: '{value}' is not in", available]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        msg = f"SPEECH MANAGER: Setting synthesizer to: {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        server.set_output_module(value)
        return server.get_output_module() == value

    @dbus_service.getter
    def get_available_synthesizers(self) -> list[str]:
        """Returns a list of available synthesizers of the speech server."""

        server = self._get_server()
        if server is None:
            msg = "SPEECH MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return []

        synthesizers = server.get_speech_servers()
        result = [s.get_info()[1] for s in synthesizers]
        msg = f"SPEECH MANAGER: Available synthesizers: {result}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    @dbus_service.getter
    def get_available_voices(self) -> list[str]:
        """Returns a list of available voices for the current synthesizer."""

        server = self._get_server()
        if server is None:
            return []

        voices = server.get_voice_families()
        if not voices:
            return []

        result = []
        for voice in voices:
            if voice_name := voice.get(speechserver.VoiceFamily.NAME, ""):
                result.append(voice_name)
        result = sorted(set(result))
        return result

    def get_voice_families(self) -> list[speechserver.VoiceFamily]:
        """Returns the full list of voice family dictionaries for the current synthesizer.
        Each dictionary contains NAME, LANG, DIALECT, and VARIANT fields."""

        server = self._get_server()
        if server is None:
            return []

        return server.get_voice_families() or []

    @dbus_service.parameterized_command
    def get_voices_for_language(
        self,
        language: str,
        variant: str = "",
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = False,
    ) -> list[tuple[str, str, str]]:
        """Returns a list of available voices for the specified language."""

        tokens = [
            "SPEECH MANAGER: get_voices_for_language. Language:",
            language,
            "Variant:",
            variant,
            "Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = self._get_server()
        if server is None:
            return []

        voices = server.get_voice_families_for_language(language=language, variant=variant)
        result = []
        for name, lang, var in voices:
            result.append((name, lang or "", var or ""))

        msg = f"SPEECH MANAGER: Found {len(result)} voice(s) for '{language}'."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    @gsettings_registry.get_registry().gsetting(
        key="family-name", schema="voice", gtype="s", default="", summary="Voice family name"
    )
    @dbus_service.getter
    def get_current_voice(self) -> str:
        """Returns the current voice name."""

        server = self._get_server()
        if server is None:
            return ""

        result = ""
        if voice_family := server.get_voice_family():
            result = voice_family.get(speechserver.VoiceFamily.NAME, "")

        return result

    @gsettings_registry.get_registry().gsetting(
        key="family-lang", schema="voice", gtype="s", default="", summary="Voice family language"
    )
    def get_current_voice_lang(self) -> str:
        """Returns the language of the current voice."""

        server = self._get_server()
        if server is None:
            return ""

        if voice_family := server.get_voice_family():
            return voice_family.get(speechserver.VoiceFamily.LANG, "") or ""

        return ""

    @gsettings_registry.get_registry().gsetting(
        key="family-dialect", schema="voice", gtype="s", default="", summary="Voice family dialect"
    )
    def get_current_voice_dialect(self) -> str:
        """Returns the dialect of the current voice."""

        server = self._get_server()
        if server is None:
            return ""

        if voice_family := server.get_voice_family():
            return voice_family.get(speechserver.VoiceFamily.DIALECT, "") or ""

        return ""

    @gsettings_registry.get_registry().gsetting(
        key="family-gender", schema="voice", gtype="s", default="", summary="Voice family gender"
    )
    def get_current_voice_gender(self) -> str:
        """Returns the gender of the current voice."""

        server = self._get_server()
        if server is None:
            return ""

        if voice_family := server.get_voice_family():
            return voice_family.get(speechserver.VoiceFamily.GENDER, "") or ""

        return ""

    @gsettings_registry.get_registry().gsetting(
        key="family-variant", schema="voice", gtype="s", default="", summary="Voice family variant"
    )
    def get_current_voice_variant(self) -> str:
        """Returns the variant of the current voice."""

        server = self._get_server()
        if server is None:
            return ""

        if voice_family := server.get_voice_family():
            return voice_family.get(speechserver.VoiceFamily.VARIANT, "") or ""

        return ""

    @dbus_service.setter
    def set_current_voice(self, voice_name: str) -> bool:
        """Sets the current voice for the active synthesizer."""

        server = self._get_server()
        if server is None:
            return False

        available = self.get_available_voices()
        if voice_name not in available:
            msg = f"SPEECH MANAGER: '{voice_name}' is not in {available}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return False

        voices = server.get_voice_families()
        if not voices:
            return False

        result = False
        for voice_family in voices:
            family_name = voice_family.get(speechserver.VoiceFamily.NAME, "")
            if family_name == voice_name:
                server.set_voice_family(voice_family)
                result = True
                break

        msg = f"SPEECH MANAGER: Set voice to '{voice_name}': {result}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    def get_current_speech_server_info(self) -> tuple[str, str]:
        """Returns the name and ID of the current speech server."""

        # TODO - JD: The result is not in sync with the current output module. Should it be?
        # TODO - JD: The only caller is the preferences dialog. And the useful functionality is in
        # the methods to get (and set) the output module. So why exactly do we need this?
        server = self._get_server()
        if server is None:
            return ("", "")

        server_name, server_id = server.get_info()
        msg = f"SPEECH MANAGER: Speech server info: {server_name}, {server_id}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return server_name, server_id

    def check_speech_setting(self) -> None:
        """Checks the speech setting and initializes speech if necessary."""

        if not self.get_speech_is_enabled():
            msg = "SPEECH MANAGER: Speech is not enabled. Shutting down speech."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            self.shutdown_speech()
            return

        msg = "SPEECH MANAGER: Speech is enabled."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        self.start_speech()

    @dbus_service.command
    def start_speech(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = False,
    ) -> bool:
        """Starts the speech server."""

        tokens = [
            "SPEECH MANAGER: start_speech. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        self._init_server()
        return True

    def _init_server(self) -> None:
        """Initializes the speech server."""

        debug.print_message(debug.LEVEL_INFO, "SPEECH MANAGER: Initializing server", True)
        if self._server:
            debug.print_message(debug.LEVEL_INFO, "SPEECH MANAGER: Already initialized", True)
            return

        # HACK: Orca goes to incredible lengths to avoid a broken configuration, so this
        #       last-chance override exists to get the speech system loaded, without risking
        #       it being written to disk unintentionally.
        if settings.speechSystemOverride:
            setattr(settings, "speechServerFactory", settings.speechSystemOverride)
            setattr(settings, "speechServerInfo", ["Default Synthesizer", "default"])

        module_name = settings.speechServerFactory
        self._server = self._init_server_from_module(module_name, settings.speechServerInfo)

        if not self._server:
            for module_name in settings.speechFactoryModules:
                if module_name != settings.speechServerFactory:
                    self._server = self._init_server_from_module(module_name, None)
                    if self._server:
                        break

        if self._server:
            tokens = ["SPEECH MANAGER: Using speech server factory:", module_name]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            default_voice: dict[str, Any] = settings.voices.get(settings.DEFAULT_VOICE, {})
            self._server.set_default_voice(default_voice)
            self._server.update_punctuation_level(settings.verbalizePunctuationStyle)
            self._server.update_capitalization_style(self.get_capitalization_style())
        else:
            msg = "SPEECH MANAGER: Speech not available"
            debug.print_message(debug.LEVEL_INFO, msg, True)

        speech.set_server(self._server)
        speech.set_mute_speech(self.get_speech_is_muted())
        debug.print_message(debug.LEVEL_INFO, "SPEECH MANAGER: Server initialized", True)

    @staticmethod
    def _init_server_from_module(
        module_name: str, speech_server_info: list[str] | None
    ) -> SpeechServer | None:
        """Attempts to initialize a speech server from the given module."""

        if not module_name:
            return None

        factory = None
        try:
            factory = importlib.import_module(f"orca.{module_name}")
        except ImportError:
            try:
                factory = importlib.import_module(module_name)
            except ImportError:
                debug.print_exception(debug.LEVEL_SEVERE)

        if not factory:
            msg = f"SPEECH MANAGER: Failed to import module: {module_name}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return None

        speech_server_info = settings.speechServerInfo
        server = None
        if speech_server_info:
            server = factory.SpeechServer.get_speech_server(speech_server_info)

        if not server:
            server = factory.SpeechServer.get_speech_server()
            if speech_server_info:
                tokens = ["SPEECH MANAGER: Invalid speechServerInfo:", speech_server_info]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if not server:
            msg = f"SPEECH MANAGER: No speech server for factory: {module_name}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)

        return server

    @dbus_service.command
    def interrupt_speech(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = False,
    ) -> bool:
        """Interrupts the speech server."""

        tokens = [
            "SPEECH MANAGER: interrupt_speech. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if server := self._get_server():
            server.stop()

        return True

    @dbus_service.command
    def shutdown_speech(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = False,
    ) -> bool:
        """Shuts down the speech server."""

        tokens = [
            "SPEECH MANAGER: shutdown_speech. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if server := self._get_server():
            server.shutdown_active_servers()
            self._server = None
            speech.set_server(None)

        return True

    @dbus_service.command
    def refresh_speech(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = False,
    ) -> bool:
        """Shuts down and re-initializes speech."""

        tokens = [
            "SPEECH MANAGER: refresh_speech. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        self.shutdown_speech()
        self.start_speech()
        return True

    @gsettings_registry.get_registry().gsetting(
        key="established",
        schema="voice",
        gtype="b",
        default=False,
        settings_key="established",
        summary="Whether this voice type has been user-customized",
    )
    def get_established(self) -> bool:
        """Returns whether the current voice type has been customized."""

        return False

    @gsettings_registry.get_registry().gsetting(
        key="rate", schema="voice", gtype="i", default=50, summary="Speech rate (0-100)"
    )
    @dbus_service.getter
    def get_rate(self) -> int:
        """Returns the current speech rate."""

        value = gsettings_registry.get_registry().layered_lookup(self._VOICE_SCHEMA, "rate", "i")
        if value is not None:
            msg = f"SPEECH MANAGER: Current rate is: {value}."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return value

        result = 50
        default_voice = settings.voices.get(settings.DEFAULT_VOICE)
        if default_voice and ACSS.RATE in default_voice:
            result = default_voice[ACSS.RATE]

        msg = f"GSETTINGS REGISTRY: voice/rate using in-memory fallback = {result!r}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        msg = f"SPEECH MANAGER: Current rate is: {result}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    @dbus_service.setter
    def set_rate(self, value: int) -> bool:
        """Sets the current speech rate (0-100, default: 50)."""

        if not isinstance(value, (int, float)):
            return False

        gsettings_registry.get_registry().set_runtime_value(self._VOICE_SCHEMA, "rate", value)

        msg = f"SPEECH MANAGER: Set rate to: {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    @dbus_service.command
    def decrease_rate(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Decreases the speech rate."""

        tokens = [
            "SPEECH MANAGER: decrease_rate. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = self._get_server()
        if server is None:
            msg = "SPEECH MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        server.decrease_speech_rate()
        if notify_user and script is not None:
            presentation_manager.get_manager().present_message(messages.SPEECH_SLOWER)

        return True

    @dbus_service.command
    def increase_rate(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Increases the speech rate."""

        tokens = [
            "SPEECH MANAGER: increase_rate. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = self._get_server()
        if server is None:
            msg = "SPEECH MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        server.increase_speech_rate()
        if notify_user and script is not None:
            presentation_manager.get_manager().present_message(messages.SPEECH_FASTER)

        return True

    @gsettings_registry.get_registry().gsetting(
        key="pitch", schema="voice", gtype="d", default=5.0, summary="Speech pitch (0.0-10.0)"
    )
    @dbus_service.getter
    def get_pitch(self) -> float:
        """Returns the current speech pitch."""

        value = gsettings_registry.get_registry().layered_lookup(self._VOICE_SCHEMA, "pitch", "d")
        if value is not None:
            msg = f"SPEECH MANAGER: Current pitch is: {value}."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return value

        result = 5.0
        default_voice = settings.voices.get(settings.DEFAULT_VOICE)
        if default_voice and ACSS.AVERAGE_PITCH in default_voice:
            result = default_voice[ACSS.AVERAGE_PITCH]

        msg = f"GSETTINGS REGISTRY: voice/pitch using in-memory fallback = {result!r}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        msg = f"SPEECH MANAGER: Current pitch is: {result}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    @dbus_service.setter
    def set_pitch(self, value: float) -> bool:
        """Sets the current speech pitch (0.0-10.0, default: 5.0)."""

        if not isinstance(value, (int, float)):
            return False

        gsettings_registry.get_registry().set_runtime_value(self._VOICE_SCHEMA, "pitch", value)

        msg = f"SPEECH MANAGER: Set pitch to: {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    @dbus_service.command
    def decrease_pitch(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Decreases the speech pitch"""

        tokens = [
            "SPEECH MANAGER: decrease_pitch. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = self._get_server()
        if server is None:
            msg = "SPEECH MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        server.decrease_speech_pitch()
        if notify_user and script is not None:
            presentation_manager.get_manager().present_message(messages.SPEECH_LOWER)

        return True

    @dbus_service.command
    def increase_pitch(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Increase the speech pitch"""

        tokens = [
            "SPEECH MANAGER: increase_pitch. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = self._get_server()
        if server is None:
            msg = "SPEECH MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        server.increase_speech_pitch()
        if notify_user and script is not None:
            presentation_manager.get_manager().present_message(messages.SPEECH_HIGHER)

        return True

    @gsettings_registry.get_registry().gsetting(
        key="volume", schema="voice", gtype="d", default=10.0, summary="Speech volume (0.0-10.0)"
    )
    @dbus_service.getter
    def get_volume(self) -> float:
        """Returns the current speech volume."""

        value = gsettings_registry.get_registry().layered_lookup(self._VOICE_SCHEMA, "volume", "d")
        if value is not None:
            msg = f"SPEECH MANAGER: Current volume is: {value}."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return value

        result = 10.0
        default_voice = settings.voices.get(settings.DEFAULT_VOICE)
        if default_voice and ACSS.GAIN in default_voice:
            result = default_voice[ACSS.GAIN]

        msg = f"GSETTINGS REGISTRY: voice/volume using in-memory fallback = {result!r}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        msg = f"SPEECH MANAGER: Current volume is: {result}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    @dbus_service.setter
    def set_volume(self, value: float) -> bool:
        """Sets the current speech volume (0.0-10.0, default: 10.0)."""

        if not isinstance(value, (int, float)):
            return False

        gsettings_registry.get_registry().set_runtime_value(self._VOICE_SCHEMA, "volume", value)

        msg = f"SPEECH MANAGER: Set volume to: {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return True

    @dbus_service.command
    def decrease_volume(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Decreases the speech volume"""

        tokens = [
            "SPEECH MANAGER: decrease_volume. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = self._get_server()
        if server is None:
            msg = "SPEECH MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        server.decrease_speech_volume()
        if notify_user and script is not None:
            presentation_manager.get_manager().present_message(messages.SPEECH_SOFTER)

        return True

    @dbus_service.command
    def increase_volume(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Increases the speech volume"""

        tokens = [
            "SPEECH MANAGER: increase_volume. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = self._get_server()
        if server is None:
            msg = "SPEECH MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        server.increase_speech_volume()
        if notify_user and script is not None:
            presentation_manager.get_manager().present_message(messages.SPEECH_LOUDER)

        return True

    @gsettings_registry.get_registry().gsetting(
        key="capitalization-style",
        schema="speech",
        genum="org.gnome.Orca.CapitalizationStyle",
        default="none",
        summary="Capitalization style (none, spell, icon)",
        settings_key="capitalizationStyle",
    )
    @dbus_service.getter
    def get_capitalization_style(self) -> str:
        """Returns the current capitalization style."""

        value = gsettings_registry.get_registry().layered_lookup(
            self._SPEECH_SCHEMA,
            "capitalization-style",
            "",
            genum="org.gnome.Orca.CapitalizationStyle",
        )
        if value is not None:
            return value
        result = settings.capitalizationStyle
        msg = (
            f"GSETTINGS REGISTRY: speech/capitalization-style using in-memory fallback = {result!r}"
        )
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    @dbus_service.setter
    def set_capitalization_style(self, value: str) -> bool:
        """Sets the capitalization style."""

        try:
            style = CapitalizationStyle[value.upper()]
        except KeyError:
            msg = f"SPEECH MANAGER: Invalid capitalization style: {value}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        msg = f"SPEECH MANAGER: Setting capitalization style to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SPEECH_SCHEMA, "capitalization-style", style.string_name
        )
        self.update_capitalization_style()
        return True

    @dbus_service.command
    def cycle_capitalization_style(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Cycle through the speech-dispatcher capitalization styles."""

        tokens = [
            "SPEECH MANAGER: cycle_capitalization_style. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        current_style = self.get_capitalization_style()
        if current_style == "none":
            self.set_capitalization_style("spell")
            full = messages.CAPITALIZATION_SPELL_FULL
            brief = messages.CAPITALIZATION_SPELL_BRIEF
        elif current_style == "spell":
            self.set_capitalization_style("icon")
            full = messages.CAPITALIZATION_ICON_FULL
            brief = messages.CAPITALIZATION_ICON_BRIEF
        else:
            self.set_capitalization_style("none")
            full = messages.CAPITALIZATION_NONE_FULL
            brief = messages.CAPITALIZATION_NONE_BRIEF

        if script is not None and notify_user:
            presentation_manager.get_manager().present_message(full, brief)
        return True

    def update_capitalization_style(self) -> bool:
        """Updates the capitalization style on the speech server."""

        server = self._get_server()
        if server is None:
            msg = "SPEECH MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        server.update_capitalization_style(self.get_capitalization_style())
        return True

    @gsettings_registry.get_registry().gsetting(
        key="punctuation-level",
        schema="speech",
        genum="org.gnome.Orca.PunctuationStyle",
        default="most",
        summary="Punctuation verbosity level (none, some, most, all)",
        settings_key="verbalizePunctuationStyle",
    )
    @dbus_service.getter
    def get_punctuation_level(self) -> str:
        """Returns the current punctuation level."""

        value = gsettings_registry.get_registry().layered_lookup(
            self._SPEECH_SCHEMA,
            "punctuation-level",
            "",
            genum="org.gnome.Orca.PunctuationStyle",
        )
        if value is not None:
            return value
        result = PunctuationStyle(settings.verbalizePunctuationStyle).string_name
        msg = f"GSETTINGS REGISTRY: speech/punctuation-level using in-memory fallback = {result!r}"
        debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    @dbus_service.setter
    def set_punctuation_level(self, value: str) -> bool:
        """Sets the punctuation level."""

        try:
            style = PunctuationStyle[value.upper()]
        except KeyError:
            msg = f"SPEECH MANAGER: Invalid punctuation level: {value}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        msg = f"SPEECH MANAGER: Setting punctuation level to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SPEECH_SCHEMA, "punctuation-level", style.string_name
        )
        self.update_punctuation_level()
        return True

    @dbus_service.command
    def cycle_punctuation_level(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Cycles through punctuation levels for speech."""

        tokens = [
            "SPEECH MANAGER: cycle_punctuation_level. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        current_level = self.get_punctuation_level()
        if current_level == "none":
            self.set_punctuation_level("some")
            full = messages.PUNCTUATION_SOME_FULL
            brief = messages.PUNCTUATION_SOME_BRIEF
        elif current_level == "some":
            self.set_punctuation_level("most")
            full = messages.PUNCTUATION_MOST_FULL
            brief = messages.PUNCTUATION_MOST_BRIEF
        elif current_level == "most":
            self.set_punctuation_level("all")
            full = messages.PUNCTUATION_ALL_FULL
            brief = messages.PUNCTUATION_ALL_BRIEF
        else:
            self.set_punctuation_level("none")
            full = messages.PUNCTUATION_NONE_FULL
            brief = messages.PUNCTUATION_NONE_BRIEF

        if script is not None and notify_user:
            presentation_manager.get_manager().present_message(full, brief)
        return True

    def update_punctuation_level(self) -> bool:
        """Updates the punctuation level on the speech server."""

        server = self._get_server()
        if server is None:
            msg = "SPEECH MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        server.update_punctuation_level(settings.verbalizePunctuationStyle)
        return True

    def update_synthesizer(self, server_id: str | None = "") -> None:
        """Updates the synthesizer to the specified id or value from settings."""

        server = self._get_server()
        if server is None:
            msg = "SPEECH MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return

        active_id = server.get_output_module()
        info = settings.speechServerInfo or ["", ""]
        if not server_id and len(info) == 2:
            server_id = info[1]

        if server_id and server_id != active_id:
            msg = f"SPEECH MANAGER: Updating synthesizer from {active_id} to {server_id}."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            server.set_output_module(server_id)

    @dbus_service.command
    def cycle_synthesizer(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Cycles through available speech synthesizers."""

        tokens = [
            "SPEECH MANAGER: cycle_synthesizer. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        server = self._get_server()
        if server is None:
            msg = "SPEECH MANAGER: Cannot get speech server."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        available = server.list_output_modules()
        if not available:
            msg = "SPEECH MANAGER: Cannot get output modules."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        current = server.get_output_module()
        if not current:
            msg = "SPEECH MANAGER: Cannot get current output module."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return True

        try:
            index = available.index(current) + 1
            if index == len(available):
                index = 0
        except ValueError:
            index = 0

        server.set_output_module(available[index])
        if script is not None and notify_user:
            presentation_manager.get_manager().present_message(available[index])
        return True

    def get_speech_is_enabled_and_not_muted(self) -> bool:
        """Returns whether speech is enabled and not muted."""

        return self.get_speech_is_enabled() and not self.get_speech_is_muted()

    @dbus_service.getter
    def get_speech_is_muted(self) -> bool:
        """Returns whether speech output is temporarily muted."""

        return speech.get_mute_speech()

    @dbus_service.setter
    def set_speech_is_muted(self, value: bool) -> bool:
        """Sets whether speech output is temporarily muted."""

        msg = f"SPEECH MANAGER: Setting speech muted to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        speech.set_mute_speech(value)
        return True

    @gsettings_registry.get_registry().gsetting(
        key="enable",
        schema="speech",
        gtype="b",
        default=True,
        summary="Enable speech output",
        settings_key="enableSpeech",
    )
    @dbus_service.getter
    def get_speech_is_enabled(self) -> bool:
        """Returns whether the speech server is enabled. See also is-muted."""

        return self._get_setting("enable", "b", settings.enableSpeech)

    @dbus_service.setter
    def set_speech_is_enabled(self, value: bool) -> bool:
        """Sets whether the speech server is enabled. See also is-muted."""

        msg = f"SPEECH MANAGER: Setting speech enabled to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)

        gsettings_registry.get_registry().set_runtime_value(self._SPEECH_SCHEMA, "enable", value)
        if value:
            self.start_speech()
            presentation_manager.get_manager().present_message(messages.SPEECH_ENABLED)
        else:
            presentation_manager.get_manager().present_message(messages.SPEECH_DISABLED)
            self.shutdown_speech()

        return True

    @gsettings_registry.get_registry().gsetting(
        key="speak-numbers-as-digits",
        schema="speech",
        gtype="b",
        default=False,
        summary="Speak numbers as individual digits",
        settings_key="speakNumbersAsDigits",
    )
    @dbus_service.getter
    def get_speak_numbers_as_digits(self) -> bool:
        """Returns whether numbers are spoken as digits."""

        return self._get_setting("speak-numbers-as-digits", "b", settings.speakNumbersAsDigits)

    @dbus_service.setter
    def set_speak_numbers_as_digits(self, value: bool) -> bool:
        """Sets whether numbers are spoken as digits."""

        msg = f"SPEECH MANAGER: Setting speak numbers as digits to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SPEECH_SCHEMA, "speak-numbers-as-digits", value
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key="use-color-names",
        schema="speech",
        gtype="b",
        default=True,
        summary="Use color names instead of values",
        settings_key="useColorNames",
    )
    @dbus_service.getter
    def get_use_color_names(self) -> bool:
        """Returns whether colors are announced by name or as RGB values."""

        return self._get_setting("use-color-names", "b", settings.useColorNames)

    @dbus_service.setter
    def set_use_color_names(self, value: bool) -> bool:
        """Sets whether colors are announced by name or as RGB values."""

        msg = f"SPEECH MANAGER: Setting use color names to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SPEECH_SCHEMA, "use-color-names", value
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key="insert-pauses-between-utterances",
        schema="speech",
        gtype="b",
        default=True,
        summary="Insert pauses between utterances",
        settings_key="enablePauseBreaks",
    )
    @dbus_service.getter
    def get_insert_pauses_between_utterances(self) -> bool:
        """Returns whether pauses are inserted between utterances, e.g. between name and role."""

        return self._get_setting(
            "insert-pauses-between-utterances", "b", settings.enablePauseBreaks
        )

    @dbus_service.setter
    def set_insert_pauses_between_utterances(self, value: bool) -> bool:
        """Sets whether pauses are inserted between utterances, e.g. between name and role."""

        msg = f"SPEECH MANAGER: Setting insert pauses to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SPEECH_SCHEMA, "insert-pauses-between-utterances", value
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key="use-pronunciation-dictionary",
        schema="speech",
        gtype="b",
        default=True,
        summary="Apply user pronunciation dictionary",
        settings_key="usePronunciationDictionary",
    )
    @dbus_service.getter
    def get_use_pronunciation_dictionary(self) -> bool:
        """Returns whether the user's pronunciation dictionary should be applied."""

        return self._get_setting(
            "use-pronunciation-dictionary", "b", settings.usePronunciationDictionary
        )

    @dbus_service.setter
    def set_use_pronunciation_dictionary(self, value: bool) -> bool:
        """Sets whether the user's pronunciation dictionary should be applied."""

        msg = f"SPEECH MANAGER: Setting use pronunciation dictionary to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SPEECH_SCHEMA, "use-pronunciation-dictionary", value
        )
        return True

    @gsettings_registry.get_registry().gsetting(
        key="auto-language-switching",
        schema="speech",
        gtype="b",
        default=True,
        summary="Automatically switch voice based on text language",
        settings_key="enableAutoLanguageSwitching",
    )
    @dbus_service.getter
    def get_auto_language_switching(self) -> bool:
        """Returns whether automatic language switching is enabled."""

        return self._get_setting(
            "auto-language-switching", "b", settings.enableAutoLanguageSwitching
        )

    @dbus_service.setter
    def set_auto_language_switching(self, value: bool) -> bool:
        """Sets whether automatic language switching is enabled."""

        msg = f"SPEECH MANAGER: Setting auto language switching to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        gsettings_registry.get_registry().set_runtime_value(
            self._SPEECH_SCHEMA, "auto-language-switching", value
        )
        return True

    @dbus_service.command
    def toggle_speech(
        self,
        script: default.Script | None = None,
        event: input_event.InputEvent | None = None,
        notify_user: bool = True,
    ) -> bool:
        """Toggles speech on and off."""

        tokens = [
            "SPEECH MANAGER: toggle_speech. Script:",
            script,
            "Event:",
            event,
            "notify_user:",
            notify_user,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        if script is not None:
            presentation_manager.get_manager().interrupt_presentation()
        if self.get_speech_is_muted():
            self.set_speech_is_muted(False)
            if script is not None and notify_user:
                presentation_manager.get_manager().present_message(messages.SPEECH_ENABLED)
        elif not self.get_speech_is_enabled():
            gsettings_registry.get_registry().set_runtime_value(self._SPEECH_SCHEMA, "enable", True)
            self._init_server()
            if script is not None and notify_user:
                presentation_manager.get_manager().present_message(messages.SPEECH_ENABLED)
        else:
            if script is not None and notify_user:
                presentation_manager.get_manager().present_message(messages.SPEECH_DISABLED)
            app = script.app if script is not None else None
            app_enable = settings_manager.get_manager().get_app_setting(app, "enableSpeech")
            if app_enable is False:
                gsettings_registry.get_registry().set_runtime_value(
                    self._SPEECH_SCHEMA, "enable", False
                )
                self.shutdown_speech()
            else:
                self.set_speech_is_muted(True)
        return True

    def create_voices_preferences_grid(self) -> VoicesPreferencesGrid:
        """Returns the GtkGrid containing the voices preferences UI."""

        return VoicesPreferencesGrid(self)


_manager: SpeechManager = SpeechManager()


def get_manager() -> SpeechManager:
    """Returns the Speech Manager"""

    return _manager
