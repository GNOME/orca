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

# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-statements
# pylint: disable=too-many-locals
# pylint: disable=too-many-lines

"""Preferences grids for speech voices and voice types."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk

from . import gsettings_registry, guilabels, language_utilities, preferences_grid_base, speechserver
from .acss import ACSS
from .speechserver import CapitalizationStyle, PunctuationStyle

if TYPE_CHECKING:
    from collections.abc import Callable

    from .speech_manager import SpeechManager


# pylint: disable-next=too-many-instance-attributes
class VoicesPreferencesGrid(preferences_grid_base.PreferencesGridBase):
    """GtkGrid containing the Voice settings page."""

    _VOICE_SCHEMA = "voice"

    @classmethod
    def get_documentation(cls) -> preferences_grid_base.PreferencePanelDoc:
        """Return documentation metadata for speech output preferences."""

        return preferences_grid_base.PreferencePanelDoc(
            title=guilabels.VOICE_GLOBAL_VOICE_SETTINGS,
            panel_id="manual.global-voice-settings",
            summary="Use these settings to enable speech, select the speech backend, and "
            "configure global speech behavior.",
            description=(
                "Global voice settings apply to Orca's spoken output overall, including "
                "which speech system and synthesizer are used and how numbers, "
                "punctuation, capitalization, and languages are handled."
            ),
            schema="speech",
            controls=(
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.VOICE_SPEECH_SYSTEM,
                    kind="choice",
                    summary="Selects the speech system Orca uses. Supported systems include "
                    "Speech Dispatcher and Spiel.",
                    schema="speech",
                    key="speech-server",
                    dynamic_values=True,
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.VOICE_SPEECH_SYNTHESIZER,
                    kind="choice",
                    summary="Selects the speech synthesizer. Examples include espeak-ng and Voxin.",
                    schema="speech",
                    key="synthesizer",
                    dynamic_values=True,
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.PUNCTUATION_STYLE,
                    kind="choice",
                    summary="Controls how much punctuation Orca speaks.",
                    schema="speech",
                    key="punctuation-level",
                    values=(
                        guilabels.PUNCTUATION_STYLE_NONE,
                        guilabels.PUNCTUATION_STYLE_SOME,
                        guilabels.PUNCTUATION_STYLE_MOST,
                        guilabels.PUNCTUATION_STYLE_ALL,
                    ),
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.VOICE_CAPITALIZATION_STYLE,
                    kind="choice",
                    summary="Controls how Orca indicates uppercase letters.",
                    schema="speech",
                    key="capitalization-style",
                    values=(
                        guilabels.CAPITALIZATION_STYLE_VOICE_ONLY,
                        guilabels.CAPITALIZATION_STYLE_ICON,
                        guilabels.CAPITALIZATION_STYLE_SPELL,
                    ),
                    value_docs=(
                        preferences_grid_base.PreferenceValueDoc(
                            label=guilabels.CAPITALIZATION_STYLE_VOICE_ONLY,
                            summary="Uses the configured uppercase voice without adding "
                            "another indication.",
                        ),
                        preferences_grid_base.PreferenceValueDoc(
                            label=guilabels.CAPITALIZATION_STYLE_ICON,
                            summary="Plays a tone before speaking an uppercase letter.",
                        ),
                        preferences_grid_base.PreferenceValueDoc(
                            label=guilabels.CAPITALIZATION_STYLE_SPELL,
                            summary="Says capital before speaking an uppercase letter.",
                        ),
                    ),
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.VOICE_SPEAK_NUMBERS_AS_DIGITS,
                    kind="switch",
                    summary="When enabled, Orca speaks 123 as 1 2 3. When disabled, "
                    "Orca sends the number to the synthesizer, which likely speaks it "
                    "as one hundred and twenty three.",
                    schema="speech",
                    key="speak-numbers-as-digits",
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.SPEECH_SPEAK_COLORS_AS_NAMES,
                    kind="switch",
                    summary="Controls whether Orca speaks colors by name, such as light "
                    "blue, instead of as RGB values.",
                    schema="speech",
                    key="use-color-names",
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.SPEECH_BREAK_INTO_CHUNKS,
                    kind="switch",
                    summary="Controls whether Orca inserts brief pauses between parts "
                    "of a spoken presentation.",
                    schema="speech",
                    key="insert-pauses-between-utterances",
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.SPEECH_USE_PRONUNCIATION_DICTIONARY,
                    kind="switch",
                    schema="speech",
                    key="use-pronunciation-dictionary",
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.LANGUAGE_SWITCHING,
                    kind="group",
                    summary="Controls when Orca switches voices based on language.",
                    controls=(
                        preferences_grid_base.PreferenceControlDoc(
                            label=guilabels.AUTO_LANGUAGE_SWITCHING,
                            kind="switch",
                            schema="speech",
                            key="auto-language-switching",
                        ),
                        preferences_grid_base.PreferenceControlDoc(
                            label=guilabels.AUTO_LANGUAGE_SWITCHING_UI,
                            kind="switch",
                            schema="speech",
                            key="auto-language-switching-ui",
                        ),
                        preferences_grid_base.PreferenceControlDoc(
                            label=guilabels.ONLY_SWITCH_CONFIGURED_LANGUAGES,
                            kind="switch",
                            schema="speech",
                            key="only-switch-configured-languages",
                        ),
                    ),
                ),
            ),
        )

    def __init__(self, manager: SpeechManager, app_name: str = "") -> None:
        super().__init__(guilabels.SPEECH)
        self._manager = manager
        self._app_name: str = app_name
        self._initializing = True

        self._voices: dict[str, ACSS] = {}
        for vt in speechserver.VoiceType:
            self._voices[vt] = manager.get_voice_properties(vt, app_name=self._app_name)

        self._voice_families: list[speechserver.VoiceFamily] = []

        self._speech_systems_combo: Gtk.ComboBox
        self._speech_synthesizers_combo: Gtk.ComboBox
        self._punctuation_combo: Gtk.ComboBox
        self._capitalization_combo: Gtk.ComboBox
        self._global_frame: Gtk.Frame | None = None
        self._voice_types_frame: Gtk.Frame | None = None

        self._families_sorted: bool = False

        self._build()
        self._populate_speech_systems()
        self.refresh()

    def _build(self) -> None:
        """Create the Gtk widgets composing the grid."""

        row = 0

        self._global_frame, global_content = self._create_frame(
            guilabels.VOICE_GLOBAL_VOICE_SETTINGS,
            margin_top=12,
        )

        punctuation_model = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_INT)
        punctuation_model.append([guilabels.PUNCTUATION_STYLE_NONE, PunctuationStyle.NONE.value])
        punctuation_model.append([guilabels.PUNCTUATION_STYLE_SOME, PunctuationStyle.SOME.value])
        punctuation_model.append([guilabels.PUNCTUATION_STYLE_MOST, PunctuationStyle.MOST.value])
        punctuation_model.append([guilabels.PUNCTUATION_STYLE_ALL, PunctuationStyle.ALL.value])

        capitalization_model = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_STRING)
        capitalization_model.append(
            [guilabels.CAPITALIZATION_STYLE_VOICE_ONLY, CapitalizationStyle.NONE.value],
        )
        capitalization_model.append(
            [guilabels.CAPITALIZATION_STYLE_ICON, CapitalizationStyle.ICON.value],
        )
        capitalization_model.append(
            [guilabels.CAPITALIZATION_STYLE_SPELL, CapitalizationStyle.SPELL.value],
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
                label_text,
                model,
                changed_handler,
                include_top_separator=False,
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
        ]

        switches = []
        for label_text, handler, state in switch_data:
            row_widget, switch, _label = self._create_switch_row(
                label_text,
                handler,
                state,
                include_top_separator=False,
            )
            global_listbox.add_row_with_widget(row_widget, switch)
            switches.append(switch)

        self._speak_numbers_switch = switches[0]
        self._use_color_names_switch = switches[1]
        self._enable_pause_breaks_switch = switches[2]
        self._use_pronunciation_dict_switch = switches[3]

        global_content.add(global_listbox)  # pylint: disable=no-member
        self.attach(self._global_frame, 0, row, 1, 1)
        row += 1

        lang_switch_frame, lang_switch_content = self._create_frame(
            guilabels.LANGUAGE_SWITCHING,
            margin_top=12,
        )

        lang_switch_data = [
            (
                guilabels.AUTO_LANGUAGE_SWITCHING,
                self._on_auto_language_switching_content_toggled,
                self._manager.get_auto_language_switching(),
            ),
            (
                guilabels.AUTO_LANGUAGE_SWITCHING_UI,
                self._on_auto_language_switching_ui_toggled,
                self._manager.get_auto_language_switching_ui(),
            ),
            (
                guilabels.ONLY_SWITCH_CONFIGURED_LANGUAGES,
                self._on_only_switch_configured_languages_toggled,
                self._manager.get_only_switch_configured_languages(),
            ),
        ]

        lang_switch_listbox = preferences_grid_base.FocusManagedListBox()
        lang_switches = []
        for label_text, handler, state in lang_switch_data:
            row_widget, switch, _label = self._create_switch_row(
                label_text,
                handler,
                state,
                include_top_separator=False,
            )
            lang_switch_listbox.add_row_with_widget(row_widget, switch)
            lang_switches.append(switch)

        self._auto_language_switching_content_switch = lang_switches[0]
        self._auto_language_switching_ui_switch = lang_switches[1]
        self._only_switch_configured_languages_switch = lang_switches[2]

        lang_switch_content.add(lang_switch_listbox)  # pylint: disable=no-member
        self.attach(lang_switch_frame, 0, row, 1, 1)

        self.show_all()  # pylint: disable=no-member

    # TODO - JD: Remove this function if it continues to prove unnecessary
    # pylint: disable-next=useless-parent-delegation
    def has_changes(self) -> bool:
        """Return True if there are unsaved changes."""

        return super().has_changes()

    def reload(self) -> None:
        """Reload settings from manager and refresh the UI."""

        app = self._app_name
        for vt in speechserver.VoiceType:
            self._voices[vt] = self._manager.get_voice_properties(vt, app_name=app)

        self._voice_families = self._manager.get_voice_families()
        self._families_sorted = False

        self._has_unsaved_changes = False
        self.refresh()

    def save_settings(self) -> dict[str, dict | list | int | str | bool]:
        """Save settings and return a dictionary of the current values for those settings."""

        result: dict[str, dict | list | int | str | bool] = {
            "voices": {vt: dict(acss) for vt, acss in self._voices.items()},
        }

        result[self._manager.KEY_SPEECH_SERVER] = self._manager.get_speech_server()
        result[self._manager.KEY_SYNTHESIZER] = self._manager.get_synthesizer()
        result[self._manager.KEY_SPEECH_SERVER_FACTORY] = self._manager.get_speech_server_factory()
        result[self._manager.KEY_PUNCTUATION_LEVEL] = self._manager.get_punctuation_level()
        result[self._manager.KEY_CAPITALIZATION_STYLE] = self._manager.get_capitalization_style()

        result[self._manager.KEY_SPEAK_NUMBERS_AS_DIGITS] = self._speak_numbers_switch.get_active()
        result[self._manager.KEY_USE_COLOR_NAMES] = self._use_color_names_switch.get_active()
        result[self._manager.KEY_INSERT_PAUSES_BETWEEN_UTTERANCES] = (
            self._enable_pause_breaks_switch.get_active()
        )
        result[self._manager.KEY_USE_PRONUNCIATION_DICTIONARY] = (
            self._use_pronunciation_dict_switch.get_active()
        )
        result[self._manager.KEY_AUTO_LANGUAGE_SWITCHING] = (
            self._auto_language_switching_content_switch.get_active()
        )
        result[self._manager.KEY_AUTO_LANGUAGE_SWITCHING_UI] = (
            self._auto_language_switching_ui_switch.get_active()
        )
        result[self._manager.KEY_ONLY_SWITCH_CONFIGURED_LANGUAGES] = (
            self._only_switch_configured_languages_switch.get_active()
        )

        self._has_unsaved_changes = False
        return result

    def refresh(self) -> None:
        """Update widget states to reflect current settings."""

        self._initializing = True

        self._populate_speech_systems()
        self._initializing = True

        app = self._app_name
        model = self._punctuation_combo.get_model()
        if model:
            current_level = PunctuationStyle[
                self._manager.get_punctuation_level(app_name=app).upper()
            ].value
            for i, row in enumerate(model):
                if row[1] == current_level:
                    self._punctuation_combo.set_active(i)
                    break

        model = self._capitalization_combo.get_model()
        if model:
            for i, row in enumerate(model):
                if row[1] == self._manager.get_capitalization_style(app_name=app):
                    self._capitalization_combo.set_active(i)
                    break

        self._speak_numbers_switch.set_active(
            self._manager.get_speak_numbers_as_digits(app_name=app),
        )
        self._use_color_names_switch.set_active(
            self._manager.get_use_color_names(app_name=app),
        )
        self._enable_pause_breaks_switch.set_active(
            self._manager.get_insert_pauses_between_utterances(app_name=app),
        )
        self._use_pronunciation_dict_switch.set_active(
            self._manager.get_use_pronunciation_dictionary(app_name=app),
        )
        self._auto_language_switching_content_switch.set_active(
            self._manager.get_auto_language_switching(app_name=app),
        )
        self._auto_language_switching_ui_switch.set_active(
            self._manager.get_auto_language_switching_ui(app_name=app),
        )
        self._only_switch_configured_languages_switch.set_active(
            self._manager.get_only_switch_configured_languages(app_name=app),
        )

        # Note: Voice type widgets are created on-demand in dialogs, so no need to refresh them here

        self._initializing = False

    def _get_acss_for_voice_type(self, voice_type: str) -> ACSS:
        """Return the local ACSS copy for the given voice type."""

        return self._voices.get(voice_type, self._voices[speechserver.VoiceType.DEFAULT])

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

    # pylint: disable-next=too-many-branches
    # pylint: disable-next=too-many-branches
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

        gsettings_registry.get_registry().set_runtime_value(
            self._manager.SPEECH_SCHEMA,
            self._manager.KEY_PUNCTUATION_LEVEL,
            PunctuationStyle(level).string_name,
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

        gsettings_registry.get_registry().set_runtime_value(
            self._manager.SPEECH_SCHEMA,
            self._manager.KEY_CAPITALIZATION_STYLE,
            CapitalizationStyle(style).string_name,
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

    def _on_auto_language_switching_content_toggled(self, switch: Gtk.Switch, _state: Any) -> None:
        """Handle auto language switching for document content switch change."""
        if self._initializing:
            return
        self._manager.set_auto_language_switching(switch.get_active())
        self._has_unsaved_changes = True

    def _on_auto_language_switching_ui_toggled(self, switch: Gtk.Switch, _state: Any) -> None:
        """Handle auto language switching for UI elements switch change."""
        if self._initializing:
            return
        self._manager.set_auto_language_switching_ui(switch.get_active())
        self._has_unsaved_changes = True

    def _on_only_switch_configured_languages_toggled(self, switch: Gtk.Switch, _state: Any) -> None:
        """Handle only-switch-configured-languages switch change."""
        if self._initializing:
            return
        self._manager.set_only_switch_configured_languages(switch.get_active())
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

        gsettings_registry.get_registry().set_runtime_value(
            self._manager.SPEECH_SCHEMA,
            self._manager.KEY_SPEECH_SERVER,
            server_name,
        )
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

        # Without the override, update_synthesizer() on script activation reverts
        # the live module to the dconf value before the user has clicked save.
        gsettings_registry.get_registry().set_runtime_value(
            self._manager.SPEECH_SCHEMA,
            self._manager.KEY_SYNTHESIZER,
            synth_name,
        )
        self._manager.set_current_synthesizer(synth_name)

        self._voice_families = self._manager.get_voice_families()
        self._families_sorted = False

        # When synthesizer changes, replace the old family with a default
        # from the new synthesizer. Without this, import_voice only writes
        # keys present in the ACSS dict, so old family values persist in dconf.
        default_family = self._voice_families[0] if self._voice_families else None
        for voice_type in speechserver.VoiceType:
            voice_acss = self._get_acss_for_voice_type(voice_type)
            if ACSS.FAMILY in voice_acss:
                del voice_acss[ACSS.FAMILY]
            if default_family is not None:
                voice_acss[ACSS.FAMILY] = default_family

        self._has_unsaved_changes = True

    def get_voice_for_type(self, voice_type: str) -> ACSS:
        """Returns a copy of the primary voice currently configured for voice_type."""

        return ACSS(self._voices.get(voice_type, self._voices[speechserver.VoiceType.DEFAULT]))

    def set_voice_for_type(self, voice_type: str, voice: ACSS) -> None:
        """Updates the primary voice for voice_type and marks the grid as changed."""

        configured = ACSS(voice)
        configured["established"] = True
        self._voices[voice_type] = configured
        self._has_unsaved_changes = True

    def get_all_voices(self) -> dict[str, ACSS]:
        """Returns copies of the staged primary voices keyed by voice type."""

        return {voice_type: ACSS(voice) for voice_type, voice in self._voices.items()}

    def get_voice_families(self) -> list[speechserver.VoiceFamily]:
        """Returns the full list of voice families from the current synthesizer."""

        return list(self._voice_families)

    def get_primary_voice_family(self) -> dict[str, str]:
        """Returns the family dict of the primary default voice."""

        return self._voices.get(speechserver.VoiceType.DEFAULT, ACSS({})).get(ACSS.FAMILY, {})

    def get_primary_language_codes(self) -> list[str]:
        """Returns the language codes of the primary default voice."""

        family = self._voices.get(speechserver.VoiceType.DEFAULT, ACSS({})).get(ACSS.FAMILY, {})
        lang = family.get(speechserver.VoiceFamily.LANG, "")
        if not lang:
            return []
        dialect = family.get(speechserver.VoiceFamily.DIALECT, "")
        full = f"{lang}-{dialect}" if dialect else ""
        codes = [lang]
        if lang.lower() != lang:
            codes.append(lang.lower())
        if full:
            codes.append(full)
            if full.lower() != full:
                codes.append(full.lower())
        return codes

    def get_available_languages(self) -> list[tuple[str, str]]:
        """Returns (lang_code, display_name) pairs from available voice families."""

        done: set[tuple[str, str]] = set()
        languages: list[tuple[str, str]] = []
        for family in self._voice_families:
            lang = family.get(speechserver.VoiceFamily.LANG, "")
            dialect = family.get(speechserver.VoiceFamily.DIALECT, "")
            if not lang or (lang, dialect) in done:
                continue
            if dialect and not language_utilities.is_standard_locale(lang, dialect):
                continue
            done.add((lang, dialect))
            code = f"{lang}-{dialect}" if dialect else lang
            display = language_utilities.get_language_display_name(lang, dialect)
            languages.append((code, display))
        return sorted(languages, key=lambda x: x[1])


# pylint: disable=no-member
# pylint: disable-next=too-many-instance-attributes
class VoiceTypesPreferencesGrid(preferences_grid_base.PreferencesGridBase):
    """GtkGrid containing voice set selector and voice type buttons."""

    _PRIMARY_LABEL = guilabels.VOICE_SET_GLOBAL

    @classmethod
    def get_documentation(cls) -> preferences_grid_base.PreferencePanelDoc:
        """Return documentation metadata for voice type preferences."""

        return preferences_grid_base.PreferencePanelDoc(
            title=guilabels.LANGUAGE_VOICE_SETTINGS,
            panel_id="manual.voice-sets",
            summary="Use these settings to configure voice sets and the voice used for each "
            "kind of spoken content.",
            description=guilabels.VOICE_SET_INFO,
            schema="voice",
            controls=(
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.LANGUAGE_VOICE_SETTINGS,
                    kind="group",
                    summary="Lists the global voice set and any language-specific voice sets.",
                    controls=(
                        preferences_grid_base.PreferenceControlDoc(
                            label=guilabels.VOICE_SET,
                            kind="choice",
                            summary="Selects the voice set to review or change.",
                            dynamic_values=True,
                        ),
                        preferences_grid_base.PreferenceControlDoc(
                            label=guilabels.VOICE_SET_CREATE_NEW,
                            kind="button",
                            summary="Creates a voice set for a specific language.",
                        ),
                        preferences_grid_base.PreferenceControlDoc(
                            label="Delete Voice Set",
                            kind="button",
                            summary="Removes the selected language-specific voice set.",
                        ),
                    ),
                ),
                preferences_grid_base.PreferenceControlDoc(
                    label=guilabels.VOICE_VOICE_TYPE_SETTINGS,
                    kind="group",
                    summary="Lists the voice types in the selected voice set. Activate the "
                    "settings button for a voice type to change how that voice sounds.",
                    controls=(
                        preferences_grid_base.PreferenceControlDoc(
                            label=guilabels.VOICE_LANGUAGE,
                            kind="choice",
                            summary="Selects the language for the selected voice type.",
                            dynamic_values=True,
                        ),
                        preferences_grid_base.PreferenceControlDoc(
                            label=guilabels.VOICE_PERSON,
                            kind="choice",
                            summary="Selects the synthesizer voice for the selected voice type.",
                            schema="voice",
                            key="family-name",
                            dynamic_values=True,
                        ),
                        preferences_grid_base.PreferenceControlDoc(
                            label=guilabels.VOICE_RATE,
                            kind="integer",
                            schema="voice",
                            key="rate",
                        ),
                        preferences_grid_base.PreferenceControlDoc(
                            label=guilabels.VOICE_PITCH,
                            kind="number",
                            schema="voice",
                            key="pitch",
                        ),
                        preferences_grid_base.PreferenceControlDoc(
                            label=guilabels.VOICE_INFLECTION,
                            kind="number",
                            schema="voice",
                            key="pitch-range",
                        ),
                        preferences_grid_base.PreferenceControlDoc(
                            label=guilabels.VOICE_VOLUME,
                            kind="number",
                            schema="voice",
                            key="volume",
                        ),
                    ),
                ),
            ),
        )

    def __init__(self, voices_grid: VoicesPreferencesGrid) -> None:
        super().__init__(guilabels.VOICE_TYPES)
        self._voices_grid = voices_grid
        self._manager = voices_grid._manager
        self._staged_configs: dict[str, dict[str, ACSS | None]] = {}
        self._deleted_sets: set[str] = set()
        self._voice_set_combo: Gtk.ComboBoxText
        self._delete_button: Gtk.Button
        self._buttons_listbox: preferences_grid_base.FocusManagedListBox
        self._build()

    def _get_voice_set_items(self) -> list[tuple[str, str]]:
        """Returns (id, label) pairs for the voice set combo."""

        primary_family = self._voices_grid.get_primary_voice_family()
        primary_lang_display = ""
        if primary_family:
            lang = primary_family.get(speechserver.VoiceFamily.LANG, "")
            dialect = primary_family.get(speechserver.VoiceFamily.DIALECT, "")
            if lang:
                primary_lang_display = language_utilities.get_language_display_name(lang, dialect)
        if primary_lang_display:
            primary_label = f"{self._PRIMARY_LABEL}: {primary_lang_display}"
        else:
            primary_label = self._PRIMARY_LABEL
        items = [(gsettings_registry.PRIMARY_VOICE_SET, primary_label)]
        names = set(self._manager.get_voice_set_names())
        names.update(self._staged_configs.keys())
        names -= self._deleted_sets
        items.extend(
            (name, language_utilities.get_language_display_name(name)) for name in sorted(names)
        )
        return items

    def _build(self) -> None:
        row = 0

        msg = f"{guilabels.VOICE_SET_INFO} {guilabels.VOICE_SET_INFO_COMMANDS}"
        info_listbox = self._create_info_listbox(msg)
        info_listbox.set_margin_bottom(12)
        self.attach(info_listbox, 0, row, 1, 1)
        row += 1

        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        header_box.set_margin_bottom(6)

        title_label = Gtk.Label(label=guilabels.LANGUAGE_VOICE_SETTINGS)
        title_label.set_halign(Gtk.Align.START)
        title_label.get_style_context().add_class("heading")
        header_box.pack_start(title_label, True, True, 0)

        self._add_button = Gtk.Button.new_from_icon_name("list-add-symbolic", Gtk.IconSize.BUTTON)
        self._add_button.get_accessible().set_name(guilabels.VOICE_SET_CREATE_NEW)
        self._add_button.connect("clicked", self._on_add_voice_set)
        header_box.pack_end(self._add_button, False, False, 0)

        self.attach(header_box, 0, row, 1, 1)
        row += 1

        items = self._get_voice_set_items()
        self._voice_set_combo = Gtk.ComboBoxText()
        for item_id, display in items:
            self._voice_set_combo.append(item_id, display)
        if items:
            self._voice_set_combo.set_active(0)

        self._delete_button = Gtk.Button.new_from_icon_name(
            "edit-delete-symbolic", Gtk.IconSize.BUTTON
        )
        self._delete_button.set_valign(Gtk.Align.CENTER)
        self._delete_button.set_sensitive(False)
        self._delete_button.connect("clicked", self._on_delete_voice_set)

        combo_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        combo_box.pack_start(self._voice_set_combo, False, False, 0)
        combo_box.pack_start(self._delete_button, False, False, 0)

        selector_row, _hbox, _label = self._create_row_structure(
            False, guilabels.VOICE_SET, combo_box, label_halign=Gtk.Align.START
        )

        selector_listbox = preferences_grid_base.FocusManagedListBox()
        selector_listbox.add_row_with_widget(selector_row, self._voice_set_combo)
        self.attach(selector_listbox, 0, row, 1, 1)
        row += 1

        self._buttons_frame, buttons_content = self._create_frame(
            guilabels.VOICE_VOICE_TYPE_SETTINGS,
            margin_top=12,
        )
        self._buttons_listbox = preferences_grid_base.FocusManagedListBox()
        buttons_content.add(self._buttons_listbox)  # pylint: disable=no-member
        self.attach(self._buttons_frame, 0, row, 1, 1)

        self._voice_set_combo.connect("changed", self._on_voice_set_changed)
        self._rebuild_buttons()
        self.show_all()  # pylint: disable=no-member

    def _rebuild_buttons(self) -> None:
        """Rebuild voice type buttons for the selected voice set."""

        for child in self._buttons_listbox.get_children():
            self._buttons_listbox.remove(child)

        voice_set = self._voice_set_combo.get_active_id()
        is_primary = voice_set == gsettings_registry.PRIMARY_VOICE_SET
        self._delete_button.set_sensitive(not is_primary)

        button_items: list[tuple[str, str | None, Callable[[Gtk.Button], None]]] = []
        for vt in speechserver.VoiceType:
            label = guilabels.VOICE_TYPE_LABELS.get(vt, vt)

            def _make_handler(voice_type: str = vt):
                return lambda _btn: self._show_voice_dialog(voice_type, voice_set)

            button_items.append((label, "applications-system-symbolic", _make_handler()))

        _listbox, voice_buttons = self._create_button_listbox(button_items)

        for voice_type, button in zip(speechserver.VoiceType, voice_buttons, strict=True):
            label = guilabels.VOICE_TYPE_LABELS.get(voice_type, voice_type)
            accessible_name = guilabels.VOICE_TYPE_SETTINGS % label
            button.set_tooltip_text(accessible_name)
            accessible = button.get_accessible()
            if accessible:
                accessible.set_name(accessible_name)

        for child in _listbox.get_children():
            _listbox.remove(child)
            self._buttons_listbox.add(child)  # pylint: disable=no-member

        self._buttons_listbox.show_all()  # pylint: disable=no-member

    def _on_voice_set_changed(self, _combo: Gtk.ComboBoxText) -> None:
        """Handle voice set combo selection change."""
        self._rebuild_buttons()

    def _get_addable_languages(self) -> list[tuple[str, str]]:
        """Returns languages not yet configured as voice sets."""

        existing = set(self._manager.get_voice_set_names()) - self._deleted_sets
        existing.update(self._staged_configs.keys())

        existing.update(self._voices_grid.get_primary_language_codes())

        languages: dict[str, str] = {}
        seen_display_names: set[str] = set()
        for lang, dialect in language_utilities.get_known_language_codes():
            code = f"{lang}-{dialect}" if dialect else lang
            if code in existing or code in languages:
                continue
            display = language_utilities.get_language_display_name(lang, dialect)
            if display == code:
                continue
            if dialect and not language_utilities.is_standard_locale(lang, dialect):
                continue
            if display in seen_display_names:
                continue
            seen_display_names.add(display)
            languages[code] = display

        return sorted(languages.items(), key=lambda x: x[1])

    def _families_for_language(self, lang_code: str) -> list[speechserver.VoiceFamily]:
        """Returns the voice families matching lang_code, in synthesizer order."""

        match_lang, _sep, match_dialect = lang_code.lower().partition("-")
        families = []
        for family in self._voices_grid.get_voice_families():
            lang = family.get(speechserver.VoiceFamily.LANG, "").lower()
            dialect = family.get(speechserver.VoiceFamily.DIALECT, "").lower()
            if lang == match_lang and (not match_dialect or dialect == match_dialect):
                families.append(family)
        return families

    def _default_voice_set_config(self, lang_code: str) -> ACSS:
        """Returns a complete default voice config for a newly created voice set."""

        props: dict[str, Any] = {
            ACSS.RATE: ACSS.settings[ACSS.RATE],
            ACSS.AVERAGE_PITCH: ACSS.settings[ACSS.AVERAGE_PITCH],
            ACSS.PITCH_RANGE: ACSS.settings[ACSS.PITCH_RANGE],
            ACSS.GAIN: ACSS.settings[ACSS.GAIN],
        }
        if families := self._families_for_language(lang_code):
            props[ACSS.FAMILY] = dict(families[0])
        return ACSS(props)

    def _on_add_voice_set(self, _button: Gtk.Button) -> None:
        """Handle add voice set button click."""

        available = self._get_addable_languages()
        if not available:
            return

        dialog, ok_button = self._create_header_bar_dialog(
            guilabels.LANGUAGE_VOICE_SETTINGS,
            guilabels.BTN_CANCEL,
            guilabels.BTN_OK,
            width=400,
        )
        content_area = dialog.get_content_area()
        lang_row, lang_combo, _label = self._create_combo_box_text_row(
            guilabels.VOICE_LANGUAGE,
            available,
            include_top_separator=False,
        )

        listbox = preferences_grid_base.FocusManagedListBox()
        listbox.add_row_with_widget(lang_row, lang_combo)
        content_area.pack_start(listbox, False, False, 0)

        def on_response(dlg: Gtk.Dialog, response_id: int) -> None:
            if response_id not in (Gtk.ResponseType.CANCEL, Gtk.ResponseType.DELETE_EVENT):
                lang_code = lang_combo.get_active_id()
                if lang_code:
                    self._staged_configs.setdefault(lang_code, {})[
                        speechserver.VoiceType.DEFAULT
                    ] = self._default_voice_set_config(lang_code)
                    self._deleted_sets.discard(lang_code)
                    self._refresh_voice_set_combo()
                    self._select_voice_set(lang_code)
                    self._has_unsaved_changes = True
            dlg.destroy()

        dialog.connect("response", on_response)
        dialog.show_all()  # pylint: disable=no-member
        ok_button.grab_default()

    def _on_delete_voice_set(self, _button: Gtk.Button) -> None:
        """Handle delete voice set button click."""

        voice_set = self._voice_set_combo.get_active_id()
        if not voice_set or voice_set == gsettings_registry.PRIMARY_VOICE_SET:
            return

        parent = self.get_toplevel()  # pylint: disable=no-member
        dialog = Gtk.MessageDialog(
            transient_for=parent if parent.is_toplevel() else None,
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text=guilabels.VOICE_SET_DELETE_CONFIRMATION
            % language_utilities.get_language_display_name(voice_set),
        )
        response = dialog.run()
        dialog.destroy()

        if response != Gtk.ResponseType.YES:
            return

        self._deleted_sets.add(voice_set)
        self._staged_configs.pop(voice_set, None)
        self._has_unsaved_changes = True

        self._refresh_voice_set_combo()
        self._voice_set_combo.set_active(0)

    def _refresh_voice_set_combo(self) -> None:
        """Refresh the voice set combo with current voice sets."""

        self._voice_set_combo.remove_all()
        items = self._get_voice_set_items()
        for item_id, display in items:
            self._voice_set_combo.append(item_id, display)
        if items:
            self._voice_set_combo.set_active(0)

    def _select_voice_set(self, voice_set: str) -> None:
        """Select a voice set in the combo by id."""

        model = self._voice_set_combo.get_model()
        for i, row in enumerate(model):
            if row[1] == voice_set:
                self._voice_set_combo.set_active(i)
                return

    def _show_voice_dialog(self, voice_type: str, voice_set: str) -> None:
        """Show a dialog for editing a voice type within a voice set, with live preview."""

        label = guilabels.VOICE_TYPE_LABELS.get(voice_type, voice_type)
        is_primary = voice_set == gsettings_registry.PRIMARY_VOICE_SET
        if is_primary:
            title = label
            config = self._voices_grid.get_voice_for_type(voice_type)
        else:
            voice_set_display = language_utilities.get_language_display_name(voice_set)
            title = f"{label} ({voice_set_display})"
            staged = self._staged_configs.get(voice_set, {}).get(voice_type)
            config = staged or self._manager.get_voice_properties(voice_type, voice_set=voice_set)

        # Edits are applied to the live voice so they can be heard while the dialog is open;
        # the configured voice is restored when it closes.

        dialog, ok_button = self._create_header_bar_dialog(
            title,
            guilabels.BTN_CANCEL,
            guilabels.BTN_OK,
            width=500,
        )

        content_area = dialog.get_content_area()
        voice_listbox = preferences_grid_base.FocusManagedListBox()
        combo_size_group = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)

        available_languages = self._voices_grid.get_available_languages()
        person_choices: list[dict[str, Any]] = []

        voice_lang_row, voice_lang_combo, _vl_label = self._create_combo_box_text_row(
            guilabels.VOICE_LANGUAGE,
            available_languages,
            include_top_separator=False,
        )
        combo_size_group.add_widget(voice_lang_combo)
        voice_listbox.add_row_with_widget(voice_lang_row, voice_lang_combo)

        person_row, person_combo, _pl = self._create_combo_box_text_row(
            guilabels.VOICE_PERSON, [], include_top_separator=False
        )
        combo_size_group.add_widget(person_combo)
        voice_listbox.add_row_with_widget(person_row, person_combo)

        def populate_persons(voice_language: str) -> None:
            person_choices.clear()
            person_combo.remove_all()
            for family in self._families_for_language(voice_language):
                name = family.get(speechserver.VoiceFamily.NAME, "")
                variant = family.get(speechserver.VoiceFamily.VARIANT, "")
                display = variant if variant and variant not in ("none", "None") else name
                person_combo.append_text(display)
                person_choices.append(family)
            if person_choices:
                person_combo.set_active(0)

        def on_voice_lang_changed(_combo: Gtk.ComboBoxText) -> None:
            lang_id = voice_lang_combo.get_active_id() or ""
            populate_persons(lang_id)

        voice_lang_combo.connect("changed", on_voice_lang_changed)

        # Select the language that matches the config, or the voice set's language
        config_family = config.get(ACSS.FAMILY, {})
        config_lang = config_family.get(speechserver.VoiceFamily.LANG, "")
        config_dialect = config_family.get(speechserver.VoiceFamily.DIALECT, "")
        if config_lang:
            target = (
                f"{config_lang}-{config_dialect}".lower() if config_dialect else config_lang.lower()
            )
        else:
            target = voice_set.lower()

        partial_match = -1
        for i, (lc, _ld) in enumerate(available_languages):
            if lc.lower() == target:
                voice_lang_combo.set_active(i)
                break
            if partial_match < 0 and lc.lower().split("-")[0] == target.split("-")[0]:
                partial_match = i
        else:
            if partial_match >= 0:
                voice_lang_combo.set_active(partial_match)

        populate_persons(voice_lang_combo.get_active_id() or "")
        config_name = config_family.get(speechserver.VoiceFamily.NAME, "")
        for i, fam in enumerate(person_choices):
            if fam.get(speechserver.VoiceFamily.NAME, "") == config_name:
                person_combo.set_active(i)
                break

        current_rate = config.get(ACSS.RATE, 50)
        rate_adj = Gtk.Adjustment(
            value=current_rate, lower=0, upper=100, step_increment=1, page_increment=10
        )
        rate_row, rate_scale, _rl = self._create_slider_row(
            guilabels.VOICE_RATE, rate_adj, include_top_separator=False
        )
        voice_listbox.add_row_with_widget(rate_row, rate_scale)

        current_pitch = config.get(ACSS.AVERAGE_PITCH, 5.0)
        pitch_adj = Gtk.Adjustment(
            value=current_pitch, lower=0, upper=10, step_increment=0.1, page_increment=1
        )
        pitch_row, pitch_scale, _pl = self._create_slider_row(
            guilabels.VOICE_PITCH, pitch_adj, include_top_separator=False, digits=1
        )
        voice_listbox.add_row_with_widget(pitch_row, pitch_scale)

        current_pr = config.get(ACSS.PITCH_RANGE, 5.0)
        pr_adj = Gtk.Adjustment(
            value=current_pr, lower=0, upper=10, step_increment=0.1, page_increment=1
        )
        pr_row, pr_scale, _prl = self._create_slider_row(
            guilabels.VOICE_INFLECTION, pr_adj, include_top_separator=False, digits=1
        )
        voice_listbox.add_row_with_widget(pr_row, pr_scale)

        current_vol = config.get(ACSS.GAIN, 10.0)
        vol_adj = Gtk.Adjustment(
            value=current_vol, lower=0, upper=10, step_increment=0.1, page_increment=1
        )
        vol_row, vol_scale, _vl = self._create_slider_row(
            guilabels.VOICE_VOLUME, vol_adj, include_top_separator=False, digits=1
        )
        voice_listbox.add_row_with_widget(vol_row, vol_scale)

        def update_live_voice(*_args: Any) -> None:
            active = person_combo.get_active()
            if not 0 <= active < len(person_choices):
                return
            self._manager.apply_live_voice(
                ACSS(
                    {
                        ACSS.FAMILY: dict(person_choices[active]),
                        ACSS.RATE: int(rate_scale.get_value()),
                        ACSS.AVERAGE_PITCH: pitch_scale.get_value(),
                        ACSS.PITCH_RANGE: pr_scale.get_value(),
                        ACSS.GAIN: vol_scale.get_value(),
                    }
                )
            )

        person_combo.connect("changed", update_live_voice)
        for scale in (rate_scale, pitch_scale, pr_scale, vol_scale):
            scale.connect("value-changed", update_live_voice)

        # Apply the configured voice immediately so it is heard on entry, not only on edit.
        # This matters for sets whose voice differs from the global one.
        update_live_voice()

        def on_response(dlg: Gtk.Dialog, response_id: int) -> None:
            confirmed = response_id not in (Gtk.ResponseType.CANCEL, Gtk.ResponseType.DELETE_EVENT)
            if confirmed:
                props: dict[str, Any] = {
                    ACSS.RATE: int(rate_scale.get_value()),
                    ACSS.AVERAGE_PITCH: pitch_scale.get_value(),
                    ACSS.PITCH_RANGE: pr_scale.get_value(),
                    ACSS.GAIN: vol_scale.get_value(),
                }
                active = person_combo.get_active()
                if 0 <= active < len(person_choices):
                    props[ACSS.FAMILY] = dict(person_choices[active])
                if is_primary:
                    self._voices_grid.set_voice_for_type(voice_type, ACSS(props))
                else:
                    self._staged_configs.setdefault(voice_set, {})[voice_type] = ACSS(props)
                    self._has_unsaved_changes = True
            # Make the staged global voices live (each by type), replacing the audition
            # override. So an OK'd default/system/etc. voice stays in effect; a set's voice
            # was staged separately and only applies when that set is active.
            self._manager.restore_live_voices(self._voices_grid.get_all_voices())
            dlg.destroy()

        def on_parent_destroy(*_args: Any) -> None:
            if dialog.get_property("visible"):
                dialog.response(Gtk.ResponseType.DELETE_EVENT)

        dialog.connect("response", on_response)
        self.get_toplevel().connect("destroy", on_parent_destroy)  # pylint: disable=no-member
        content_area.pack_start(voice_listbox, True, True, 0)
        dialog.show_all()  # pylint: disable=no-member
        ok_button.grab_default()

    def save_settings(self) -> dict[str, dict | list | int | str | bool]:
        """Writes staged voice set changes to dconf."""

        registry = gsettings_registry.get_registry()
        profile = registry.get_active_profile()

        for voice_set in self._deleted_sets:
            for vt in speechserver.VoiceType:
                sub = gsettings_registry.get_registry().voice_set_sub_path(vt, voice_set)
                gs = registry.get_settings("voice", profile, sub)
                if gs is not None:
                    for key in gs.list_keys():
                        if gs.get_user_value(key) is not None:
                            gs.reset(key)

        for voice_set, voice_types in self._staged_configs.items():
            for voice_type, config in voice_types.items():
                if config is not None:
                    self._manager.set_voice_set_properties(voice_type, voice_set, config)

        self._staged_configs.clear()
        self._deleted_sets.clear()
        self._has_unsaved_changes = False
        self._manager.refresh_voice_set_commands()
        return {}

    def has_changes(self) -> bool:
        """Return True if there are unsaved voice set changes."""

        return self._has_unsaved_changes

    def reload(self) -> None:
        """Reload voice set state and refresh UI."""

        self._has_unsaved_changes = False
        self.refresh()

    def refresh(self) -> None:
        """Refresh voice set combo to reflect current state."""

        self._staged_configs.clear()
        self._deleted_sets.clear()
        if self._voice_set_combo is not None:
            self._refresh_voice_set_combo()
            self._rebuild_buttons()


# pylint: enable=no-member
