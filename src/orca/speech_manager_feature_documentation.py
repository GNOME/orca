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

from . import guilabels
from .help_metadata import FeatureLinkDoc, FeaturePageDoc, FeatureSectionDoc


def get_feature_documentation() -> FeaturePageDoc:
    """Returns feature documentation for speech and voices."""

    return FeaturePageDoc(
        page_id="features_speech_and_voices_guide",
        title="Speech and voices",
        link_title="Speech and voices",
        description="Spoken presentation of on-screen content and Orca messages.",
        guide_xref="index#output",
        sections_as_pages=True,
        preference_category="speech",
        sections=(
            FeatureSectionDoc(
                title="Speech output",
                topic_id="output",
                target="speech.output.feature",
                intro="Turn Orca's spoken output on or off.",
                preference_panels=("speech_manager.speech",),
                command_groups=("speech.commands.support",),
            ),
            FeatureSectionDoc(
                title=guilabels.VOICE_GLOBAL_VOICE_SETTINGS.capitalize(),
                target="speech.global-voice-settings.feature",
                preference_panels=("speech_manager.global-voice-settings",),
                topic_id="global_voice_settings",
                command_groups=(
                    "speech.commands.output",
                    "speech.commands.system-and-synthesizer",
                ),
                intro=(
                    f'Use "{guilabels.VOICE_GLOBAL_VOICE_SETTINGS}" preferences to configure '
                    "speech behavior shared by all voice types and voice sets."
                ),
                details=(
                    "To configure the voices Orca "
                    f'uses, use the separate "{guilabels.LANGUAGE_VOICE_SETTINGS}" preferences '
                    "subgroup. "
                    f'The "{guilabels.VOICE_SET_GLOBAL}" voice set holds the voices '
                    "Orca normally uses. You can add voice sets for other languages "
                    "to use when switching languages.\n\n"
                    "Each voice set consists of four voice types: the default voice is "
                    "used for presenting on-screen objects and text, "
                    "the uppercase voice identifies capital letters, the hyperlink voice "
                    "identifies links, and the system voice presents information supplied "
                    "by Orca, such as roles, states, and messages. All four initially sound "
                    "the same. "
                    "Any voice type you have not explicitly configured uses the default "
                    "voice's settings. To make the uppercase, hyperlink, or system voice "
                    f'sound different, configure it in "{guilabels.LANGUAGE_VOICE_SETTINGS}" '
                    "preferences."
                ),
                links=(
                    FeatureLinkDoc("speech.voice-sets.feature"),
                    FeatureLinkDoc("speech.language-switching.feature"),
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
                links=(
                    FeatureLinkDoc("speech.global-voice-settings"),
                    FeatureLinkDoc("speech.language-switching.feature"),
                ),
                title=guilabels.LANGUAGE_VOICE_SETTINGS.capitalize(),
                preference_panels=("speech_manager.voice-sets",),
                topic_id="voice_sets",
                target="speech.voice-sets.feature",
                command_groups=("speech.commands.voice-parameters",),
                intro=(
                    "A voice set contains four voice types: default, uppercase, hyperlink, and "
                    "system. "
                    f'The "{guilabels.VOICE_SET_GLOBAL}" voice set normally applies. You can also '
                    "create voice sets for other languages and configure each voice type "
                    "separately."
                ),
                details=(
                    "The default voice is used for presenting on-screen objects and text. The "
                    "uppercase voice identifies capital letters, the hyperlink voice identifies "
                    "links, and the system voice presents information supplied by Orca, such as "
                    "roles, states, and messages. See [[speech.global-voice-settings.feature]] "
                    "for behavior shared by all voice types and "
                    "[[speech.language-switching.feature]] for automatic and manual switching "
                    "between voice sets."
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
                target="speech.language-switching.feature",
                preference_controls=("speech.language-switching",),
                command_groups=("speech.commands.voice-sets",),
                intro=(
                    "Language switching lets you change the voice used for different "
                    "languages. Orca can switch automatically based on language information "
                    "provided by the application, or you can switch manually using keyboard "
                    "commands."
                ),
                settings_and_commands=(
                    FeatureLinkDoc(
                        "speech.voice-sets",
                        "",
                        "Create language-specific voice sets.",
                    ),
                ),
                details=(
                    "Manual language selection takes precedence over automatic switching. "
                    "Returning to the global voice set restores automatic switching. The "
                    "settings and commands below control these options; see "
                    "[[speech.voice-sets.feature]] to configure the voices themselves."
                ),
            ),
            FeatureSectionDoc(
                title="Pronunciation dictionary",
                preference_categories=("pronunciation",),
                preference_controls=("speech.use-pronunciation-dictionary",),
                topic_id="pronunciation_dictionary",
                target="speech.pronunciation.feature",
                intro=(
                    "The pronunciation dictionary lets you replace how Orca speaks specific "
                    "words. The settings below control its use and its entries."
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
                ),
            ),
            FeatureSectionDoc(
                title="Verbosity",
                preference_panels=("speech_presenter.verbosity",),
                topic_id="verbosity",
                command_names=(
                    "toggleSpeechVerbosityHandler",
                    "toggleSpeakingIndentationHandler",
                ),
                intro=(
                    "Use verbosity settings and commands to control how much information Orca "
                    "includes in spoken output."
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
