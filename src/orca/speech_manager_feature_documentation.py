# Orca
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

"""Feature documentation for speech management."""

from __future__ import annotations

from . import cmdnames, guilabels
from .help_metadata import FeatureLinkDoc, FeaturePageDoc, FeatureSectionDoc


def get_feature_documentation() -> FeaturePageDoc:
    """Returns feature documentation for speech and voices."""

    return FeaturePageDoc(
        page_id="features_speech_and_voices",
        title="Speech and voices",
        link_title="Speech and voices",
        description="Configure speech output, voices, and voice sets.",
        guide_xref="index#output",
        sections_as_pages=True,
        preference_category="speech",
        intro=(
            "These topics describe speech output, voices, voice sets, language switching, "
            "pronunciation, and verbosity."
        ),
        sections=(
            FeatureSectionDoc(
                title="Speech output",
                topic_id="output",
                target="speech.output.feature",
                intro="Turn Orca's spoken output on or off.",
                details=(
                    f"Use {guilabels.SPEECH_ENABLE_SPEECH} to configure whether Orca speaks. "
                    f"The {cmdnames.TOGGLE_SPEECH} command temporarily turns speech off or back on "
                    "without changing your saved preference."
                ),
                preference_panels=("speech_manager.speech",),
                command_groups=("speech.commands.support",),
            ),
            FeatureSectionDoc(
                title=guilabels.VOICE_GLOBAL_VOICE_SETTINGS.capitalize(),
                preference_panels=("speech_manager.global-voice-settings",),
                topic_id="global_voice_settings",
                command_groups=(
                    "speech.commands.output",
                    "speech.commands.system-and-synthesizer",
                ),
                intro=(
                    f"Use {guilabels.VOICE_GLOBAL_VOICE_SETTINGS} preferences for speech "
                    "settings that always "
                    "apply, regardless of which voice type Orca is using. Examples include "
                    "the speech system and synthesizer, capitalization style, punctuation "
                    "level, how numbers and colors are spoken, whether the pronunciation "
                    "dictionary is used, and language switching. To choose the voices Orca "
                    f"uses, use {guilabels.LANGUAGE_VOICE_SETTINGS} preferences. "
                    f"The {guilabels.VOICE_SET_GLOBAL} voice set holds the voices "
                    f"Orca normally uses; {guilabels.VOICE_GLOBAL_VOICE_SETTINGS} controls "
                    "behavior that applies "
                    "regardless of the voice set or voice type."
                ),
                settings_and_commands=(
                    FeatureLinkDoc(
                        "speech.global-voice-settings",
                        "",
                        "Configure speech settings that are not tied to a voice type.",
                    ),
                    FeatureLinkDoc(
                        "speech.commands.system-and-synthesizer",
                        "Speech system and synthesizer commands",
                        "Change the synthesizer from the keyboard.",
                    ),
                    FeatureLinkDoc(
                        "preferences.pronunciation",
                        "",
                        "Customize how words are spoken.",
                    ),
                ),
            ),
            FeatureSectionDoc(
                title=guilabels.LANGUAGE_VOICE_SETTINGS.capitalize(),
                preference_panels=("speech_manager.voice-sets",),
                topic_id="voice_sets",
                command_groups=("speech.commands.voice-sets", "speech.commands.voice-parameters"),
                intro=(
                    "A voice set contains four voice types: default, uppercase, hyperlink, "
                    "and system. You can configure these voice types for the "
                    f"{guilabels.VOICE_SET_GLOBAL} voice "
                    "set, which normally applies. You can also create additional voice sets "
                    "for the languages you frequently use and configure the language, "
                    "person, rate, pitch, inflection, and volume for each voice type in "
                    "those voice sets."
                ),
                details=(
                    "The default voice reads ordinary text. The uppercase voice identifies "
                    "capital letters, the hyperlink voice identifies links, and the system "
                    "voice presents information supplied by Orca, such as object roles. "
                    "These voice choices are separate from "
                    f"{guilabels.VOICE_GLOBAL_VOICE_SETTINGS}, which "
                    "controls behavior shared by all voice types.\n\n"
                    "Each configured voice set also has an unbound command for switching "
                    "directly to that voice set. The voice parameter commands temporarily "
                    "adjust the active voice set. To save changes or configure individual "
                    "voice types, use the settings below."
                ),
                settings_and_commands=(
                    FeatureLinkDoc(
                        "speech.voice-sets",
                        "",
                        "Configure voices and voice parameters for each voice type.",
                    ),
                    FeatureLinkDoc(
                        "speech.commands.voice-sets",
                        "Voice set commands",
                        "Switch among configured voice sets.",
                    ),
                    FeatureLinkDoc(
                        "speech.commands.voice-parameters",
                        "Voice parameter commands",
                        "Change speech rate, pitch, inflection, and volume.",
                    ),
                ),
            ),
            FeatureSectionDoc(
                title="Language switching",
                topic_id="language_switching",
                intro=(
                    "Language switching can automatically change voices for document "
                    "content and/or user-interface elements when spoken content has "
                    "language information. You can also use commands to switch manually to "
                    "a configured voice set."
                ),
                settings_and_commands=(
                    FeatureLinkDoc(
                        "speech.global-voice-settings",
                        "",
                        "Configure when Orca switches voices based on language.",
                    ),
                    FeatureLinkDoc(
                        "speech.voice-sets",
                        "",
                        "Create language-specific voice sets.",
                    ),
                    FeatureLinkDoc(
                        "speech.commands.voice-sets",
                        "Voice set commands",
                        "Switch voice sets manually.",
                    ),
                ),
                details=(
                    f"The {guilabels.VOICE_SET_GLOBAL} voice set normally applies. "
                    "When language switching is "
                    "enabled, Orca can use a matching language-specific voice set. "
                    f"If {guilabels.ONLY_SWITCH_CONFIGURED_LANGUAGES} is enabled, "
                    "Orca switches only to "
                    "languages for which you have configured a voice set. Language switching "
                    f"settings are part of {guilabels.VOICE_GLOBAL_VOICE_SETTINGS} preferences, "
                    "the shared "
                    "speech-behavior settings rather than a voice set. With that limit "
                    "off, Orca can use any language supported by the synthesizer, even without "
                    "a matching voice set. Selecting a language-specific voice set manually "
                    "suspends automatic language switching until you return to the "
                    f"{guilabels.VOICE_SET_GLOBAL} "
                    "voice set."
                ),
            ),
            FeatureSectionDoc(
                title="Pronunciation dictionary",
                preference_categories=("pronunciation",),
                topic_id="pronunciation_dictionary",
                intro=(
                    "The pronunciation dictionary lets you replace how Orca speaks specific "
                    f"words. {guilabels.VOICE_GLOBAL_VOICE_SETTINGS} preferences include "
                    "a switch for whether "
                    f"Orca uses the dictionary; {guilabels.PRONUNCIATION} preferences are "
                    "where you add, "
                    "edit, and remove dictionary entries."
                ),
                details=(
                    "For example, replace an abbreviation with its expanded form or use a "
                    "phonetic spelling for a name. Matching is case-insensitive and applies "
                    "to whole words. Application-specific pronunciation entries let you use "
                    "different replacements in different applications."
                ),
                settings_and_commands=(
                    FeatureLinkDoc(
                        "preferences.pronunciation",
                        "",
                        "Add, edit, and remove pronunciation dictionary entries.",
                    ),
                    FeatureLinkDoc(
                        "speech.global-voice-settings",
                        "",
                        "Configure whether Orca uses the pronunciation dictionary.",
                    ),
                ),
            ),
            FeatureSectionDoc(
                title="Verbosity",
                preference_panels=("speech_presenter.verbosity",),
                topic_id="verbosity",
                command_groups=(
                    "speech.commands.verbosity-and-details",
                    "speech.commands.indentation",
                ),
                intro=(
                    "Use verbosity settings and commands to control how much information Orca "
                    "includes in spoken output."
                ),
                details=(
                    f"{cmdnames.TOGGLE_SPEECH_VERBOSITY} switches between brief and verbose "
                    "object presentation. Other settings control individual details "
                    "independently."
                ),
                settings_and_commands=(
                    FeatureLinkDoc(
                        "speech.verbosity",
                        "",
                        "Configure how much information Orca speaks.",
                    ),
                    FeatureLinkDoc(
                        "speech.commands.verbosity-and-details",
                        "Verbosity commands",
                        "Change speech verbosity and spoken details from the keyboard.",
                    ),
                ),
            ),
            FeatureSectionDoc(
                title="Tables", topic_id="tables", include_target="speech.tables.feature"
            ),
            FeatureSectionDoc(
                title="Progress bars",
                topic_id="progress_bars",
                include_target="speech.progress-bars.feature",
            ),
            FeatureSectionDoc(
                title="Container announcements",
                topic_id="container_announcements",
                include_target="speech.container-announcements.feature",
            ),
            FeatureSectionDoc(
                title="On-screen speech display",
                topic_id="on_screen_display",
                include_target="speech.on-screen-display.feature",
            ),
        ),
    )
