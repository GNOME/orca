# Orca
#
# Copyright 2025 Valve Corporation
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

# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
# pylint: disable=too-many-return-statements
# pylint: disable=too-many-lines

"""Integration tests for Orca's D-Bus service."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

import pytest

from dasbus.error import DBusError
from gi.repository import GLib

if TYPE_CHECKING:
    from collections.abc import Callable
    from dasbus.client.proxy import ObjectProxy as DBusProxy

# Get configurable timeout values from environment variables
DEFAULT_MODULE_TIMEOUT = 15
FLAT_REVIEW_TIMEOUT = int(os.environ.get("ORCA_FLAT_REVIEW_TIMEOUT", DEFAULT_MODULE_TIMEOUT))
STRUCTURAL_NAVIGATOR_TIMEOUT = int(
    os.environ.get("ORCA_STRUCTURAL_NAVIGATOR_TIMEOUT", DEFAULT_MODULE_TIMEOUT)
)
SPEECH_AND_VERBOSITY_TIMEOUT = int(os.environ.get("ORCA_SPEECH_AND_VERBOSITY_TIMEOUT", 30))

MODULE_TIMEOUTS = {
    "FlatReviewPresenter": FLAT_REVIEW_TIMEOUT,
    "StructuralNavigator": STRUCTURAL_NAVIGATOR_TIMEOUT,
    "SpeechAndVerbosityManager": SPEECH_AND_VERBOSITY_TIMEOUT,
}

# Modules that may not be present in all environments (e.g., X11 vs Wayland)
OPTIONAL_MODULES = {"MouseReviewer"}

MODULE_CONFIG = {
    "ActionPresenter": {
        "commands": ["ShowActionsList"],
        "parameterized_commands": [],
        "getters": [],
        "setters": [],
        "ui_commands": ["ShowActionsList"],
        "toggle_commands": [],
        "skip": [],
    },
    "ClipboardPresenter": {
        "commands": ["PresentClipboardContents"],
        "parameterized_commands": [],
        "getters": [],
        "setters": [],
        "ui_commands": [],
        "toggle_commands": [],
        "skip": [],
    },
    "FocusManager": {
        "commands": [
            "EnableStickyBrowseMode",
            "EnableStickyFocusMode",
            "ToggleLayoutMode",
            "TogglePresentationMode",
        ],
        "parameterized_commands": [],
        "getters": [
            "BrowseModeIsSticky",
            "FocusModeIsSticky",
            "InFocusMode",
            "InLayoutMode",
        ],
        "setters": [],
        "ui_commands": [],
        "toggle_commands": ["ToggleLayoutMode", "TogglePresentationMode"],
        "skip": [],
    },
    "MouseReviewer": {
        "commands": ["Toggle"],
        "parameterized_commands": [],
        "getters": ["IsEnabled"],
        "setters": ["IsEnabled"],
        "ui_commands": [],
        "toggle_commands": ["Toggle"],
        "skip": [],
    },
    "FlatReviewPresenter": {
        "commands": [
            "AppendToClipboard",
            "CopyToClipboard",
            "GetCurrentObject",
            "GoAbove",
            "GoBelow",
            "GoBottomLeft",
            "GoEnd",
            "GoEndOfLine",
            "GoHome",
            "GoNextCharacter",
            "GoNextItem",
            "GoNextLine",
            "GoPreviousCharacter",
            "GoPreviousItem",
            "GoPreviousLine",
            "GoStartOfLine",
            "LeftClickOnObject",
            "PhoneticItem",
            "PhoneticLine",
            "PresentCharacter",
            "PresentItem",
            "PresentLine",
            "PresentObject",
            "RightClickOnObject",
            "RoutePointerToObject",
            "SayAll",
            "ShowContents",
            "SpellCharacter",
            "SpellItem",
            "SpellLine",
            "ToggleFlatReviewMode",
            "ToggleRestrict",
            "UnicodeCurrentCharacter",
        ],
        "parameterized_commands": [],
        "getters": ["IsRestricted"],
        "setters": ["IsRestricted"],
        "ui_commands": [
            "ShowContents",
            "LeftClickOnObject",
            "RightClickOnObject",
            "RoutePointerToObject",
        ],
        "toggle_commands": ["ToggleFlatReviewMode", "ToggleRestrict"],
        "skip": [],
    },
    "ObjectNavigator": {
        "commands": [
            "MoveToFirstChild",
            "MoveToNextSibling",
            "MoveToParent",
            "MoveToPreviousSibling",
            "PerformAction",
            "ToggleSimplify",
        ],
        "parameterized_commands": [],
        "getters": [],
        "setters": [],
        "ui_commands": ["PerformAction"],
        "toggle_commands": ["ToggleSimplify"],
        "skip": [],
    },
    "NotificationPresenter": {
        "commands": [
            "PresentLastNotification",
            "PresentNextNotification",
            "PresentPreviousNotification",
            "ShowNotificationList",
        ],
        "parameterized_commands": [],
        "getters": [],
        "setters": [],
        "ui_commands": ["ShowNotificationList"],
        "toggle_commands": [],
        "skip": [],
    },
    "SleepModeManager": {
        "commands": ["ToggleSleepMode"],
        "parameterized_commands": [],
        "getters": [],
        "setters": [],
        "ui_commands": [],
        "toggle_commands": ["ToggleSleepMode"],
        "skip": [],
    },
    "SpeechAndVerbosityManager": {
        "commands": [
            "ChangeNumberStyle",
            "CycleCapitalizationStyle",
            "CyclePunctuationLevel",
            "CycleSynthesizer",
            "DecreasePitch",
            "DecreaseRate",
            "DecreaseVolume",
            "IncreasePitch",
            "IncreaseRate",
            "IncreaseVolume",
            "InterruptSpeech",
            "RefreshSpeech",
            "ShutdownSpeech",
            "StartSpeech",
            "ToggleIndentationAndJustification",
            "ToggleSpeech",
            "ToggleTableCellReadingMode",
            "ToggleVerbosity",
        ],
        "parameterized_commands": ["GetVoicesForLanguage"],
        "getters": [
            "AlwaysAnnounceSelectedRangeInSpreadsheet",
            "AnnounceBlockquote",
            "AnnounceCellCoordinates",
            "AnnounceCellHeaders",
            "AnnounceCellSpan",
            "AnnounceForm",
            "AnnounceGrouping",
            "AnnounceLandmark",
            "AnnounceList",
            "AnnounceSpreadsheetCellCoordinates",
            "AnnounceTable",
            "AvailableServers",
            "AvailableSynthesizers",
            "AvailableVoices",
            "CapitalizationStyle",
            "CurrentServer",
            "CurrentSynthesizer",
            "CurrentVoice",
            "InsertPausesBetweenUtterances",
            "MessagesAreDetailed",
            "OnlySpeakDisplayedText",
            "Pitch",
            "PunctuationLevel",
            "Rate",
            "RepeatedCharacterLimit",
            "SpeakBlankLines",
            "SpeakDescription",
            "SpeakIndentationAndJustification",
            "SpeakIndentationOnlyIfChanged",
            "SpeakMisspelledIndicator",
            "SpeakNumbersAsDigits",
            "SpeakPositionInSet",
            "SpeakRowInDocumentTable",
            "SpeakRowInGuiTable",
            "SpeakRowInSpreadsheet",
            "SpeakTutorialMessages",
            "SpeakWidgetMnemonic",
            "SpeechIsEnabled",
            "SpeechIsMuted",
            "UseColorNames",
            "UsePronunciationDictionary",
            "VerbosityLevel",
            "Volume",
        ],
        "setters": [
            "AlwaysAnnounceSelectedRangeInSpreadsheet",
            "AnnounceBlockquote",
            "AnnounceCellCoordinates",
            "AnnounceCellHeaders",
            "AnnounceCellSpan",
            "AnnounceForm",
            "AnnounceGrouping",
            "AnnounceLandmark",
            "AnnounceList",
            "AnnounceSpreadsheetCellCoordinates",
            "AnnounceTable",
            "CapitalizationStyle",
            "CurrentServer",
            "CurrentSynthesizer",
            "CurrentVoice",
            "InsertPausesBetweenUtterances",
            "MessagesAreDetailed",
            "OnlySpeakDisplayedText",
            "Pitch",
            "PunctuationLevel",
            "Rate",
            "RepeatedCharacterLimit",
            "SpeakBlankLines",
            "SpeakDescription",
            "SpeakIndentationAndJustification",
            "SpeakIndentationOnlyIfChanged",
            "SpeakMisspelledIndicator",
            "SpeakNumbersAsDigits",
            "SpeakPositionInSet",
            "SpeakRowInDocumentTable",
            "SpeakRowInGuiTable",
            "SpeakRowInSpreadsheet",
            "SpeakTutorialMessages",
            "SpeakWidgetMnemonic",
            "SpeechIsEnabled",
            "SpeechIsMuted",
            "UseColorNames",
            "UsePronunciationDictionary",
            "VerbosityLevel",
            "Volume",
        ],
        "ui_commands": [],
        "toggle_commands": [
            "ToggleIndentationAndJustification",
            "ToggleSpeech",
            "ToggleTableCellReadingMode",
            "ToggleVerbosity",
        ],
        "skip": [],
    },
    "StructuralNavigator": {
        "commands": [
            "ContainerEnd",
            "ContainerStart",
            "CycleMode",
            "ListBlockquotes",
            "ListButtons",
            "ListCheckboxes",
            "ListClickables",
            "ListComboboxes",
            "ListEntries",
            "ListFormFields",
            "ListHeadings",
            "ListHeadingsLevel1",
            "ListHeadingsLevel2",
            "ListHeadingsLevel3",
            "ListHeadingsLevel4",
            "ListHeadingsLevel5",
            "ListHeadingsLevel6",
            "ListIframes",
            "ListImages",
            "ListLandmarks",
            "ListLargeObjects",
            "ListLinks",
            "ListListItems",
            "ListLists",
            "ListParagraphs",
            "ListRadioButtons",
            "ListTables",
            "ListUnvisitedLinks",
            "ListVisitedLinks",
            "NextBlockquote",
            "NextButton",
            "NextCheckbox",
            "NextClickable",
            "NextCombobox",
            "NextEntry",
            "NextFormField",
            "NextHeading",
            "NextHeadingLevel1",
            "NextHeadingLevel2",
            "NextHeadingLevel3",
            "NextHeadingLevel4",
            "NextHeadingLevel5",
            "NextHeadingLevel6",
            "NextIframe",
            "NextImage",
            "NextLandmark",
            "NextLargeObject",
            "NextLink",
            "NextList",
            "NextListItem",
            "NextLiveRegion",
            "NextParagraph",
            "NextRadioButton",
            "NextSeparator",
            "NextTable",
            "NextUnvisitedLink",
            "NextVisitedLink",
            "PreviousBlockquote",
            "PreviousButton",
            "PreviousCheckbox",
            "PreviousClickable",
            "PreviousCombobox",
            "PreviousEntry",
            "PreviousFormField",
            "PreviousHeading",
            "PreviousHeadingLevel1",
            "PreviousHeadingLevel2",
            "PreviousHeadingLevel3",
            "PreviousHeadingLevel4",
            "PreviousHeadingLevel5",
            "PreviousHeadingLevel6",
            "PreviousIframe",
            "PreviousImage",
            "PreviousLandmark",
            "PreviousLargeObject",
            "PreviousLink",
            "PreviousList",
            "PreviousListItem",
            "PreviousLiveRegion",
            "PreviousParagraph",
            "PreviousRadioButton",
            "PreviousSeparator",
            "PreviousTable",
            "PreviousUnvisitedLink",
            "PreviousVisitedLink",
        ],
        "parameterized_commands": [],
        "getters": [
            "IsEnabled",
            "LargeObjectTextLength",
            "NavigationWraps",
            "TriggersFocusMode",
        ],
        "setters": [
            "IsEnabled",
            "LargeObjectTextLength",
            "NavigationWraps",
            "TriggersFocusMode",
        ],
        "ui_commands": [
            "ListBlockquotes",
            "ListButtons",
            "ListCheckboxes",
            "ListClickables",
            "ListComboboxes",
            "ListEntries",
            "ListFormFields",
            "ListHeadings",
            "ListHeadingsLevel1",
            "ListHeadingsLevel2",
            "ListHeadingsLevel3",
            "ListHeadingsLevel4",
            "ListHeadingsLevel5",
            "ListHeadingsLevel6",
            "ListIframes",
            "ListImages",
            "ListLandmarks",
            "ListLargeObjects",
            "ListLinks",
            "ListListItems",
            "ListLists",
            "ListParagraphs",
            "ListRadioButtons",
            "ListTables",
            "ListUnvisitedLinks",
            "ListVisitedLinks",
        ],
        "toggle_commands": [],
        "skip": ["CycleMode"],  # Test flakiness depending on app and focus.
    },
    "SystemInformationPresenter": {
        "commands": [
            "PresentBatteryStatus",
            "PresentCpuAndMemoryUsage",
            "PresentDate",
            "PresentTime",
        ],
        "parameterized_commands": [],
        "getters": [
            "DateFormat",
            "TimeFormat",
            "AvailableDateFormats",
            "AvailableTimeFormats",
        ],
        "setters": [
            "DateFormat",
            "TimeFormat",
        ],
        "ui_commands": [],
        "toggle_commands": [],
        "skip": ["PresentBatteryStatus"],  # Can timeout on systems without battery
    },
    "TableNavigator": {
        "commands": [
            "ClearDynamicColumnHeadersRow",
            "ClearDynamicRowHeadersColumn",
            "MoveDown",
            "MoveLeft",
            "MoveRight",
            "MoveToBeginningOfRow",
            "MoveToBottomOfColumn",
            "MoveToEndOfRow",
            "MoveToFirstCell",
            "MoveToLastCell",
            "MoveToTopOfColumn",
            "MoveUp",
            "SetDynamicColumnHeadersRow",
            "SetDynamicRowHeadersColumn",
            "ToggleEnabled",
        ],
        "parameterized_commands": [],
        "getters": ["SkipBlankCells"],
        "setters": ["SkipBlankCells"],
        "ui_commands": [],
        "toggle_commands": ["ToggleEnabled"],
        "skip": [],
    },
    "TypingEchoPresenter": {
        "commands": ["CycleKeyEcho"],
        "parameterized_commands": [],
        "getters": [
            "KeyEchoEnabled",
            "CharacterEchoEnabled",
            "WordEchoEnabled",
            "SentenceEchoEnabled",
            "AlphabeticKeysEnabled",
            "NumericKeysEnabled",
            "PunctuationKeysEnabled",
            "SpaceEnabled",
            "ModifierKeysEnabled",
            "FunctionKeysEnabled",
            "ActionKeysEnabled",
            "NavigationKeysEnabled",
            "DiacriticalKeysEnabled",
            "LockingKeysPresented",
        ],
        "setters": [
            "KeyEchoEnabled",
            "CharacterEchoEnabled",
            "WordEchoEnabled",
            "SentenceEchoEnabled",
            "AlphabeticKeysEnabled",
            "NumericKeysEnabled",
            "PunctuationKeysEnabled",
            "SpaceEnabled",
            "ModifierKeysEnabled",
            "FunctionKeysEnabled",
            "ActionKeysEnabled",
            "NavigationKeysEnabled",
            "DiacriticalKeysEnabled",
            "LockingKeysPresented",
        ],
        "ui_commands": [],
        "toggle_commands": [],
        "skip": [],
    },
    "CaretNavigator": {
        "commands": [
            "ToggleEnabled",
            "NextCharacter",
            "PreviousCharacter",
            "NextWord",
            "PreviousWord",
            "NextLine",
            "PreviousLine",
            "StartOfLine",
            "EndOfLine",
            "StartOfFile",
            "EndOfFile",
        ],
        "parameterized_commands": [],
        "getters": ["IsEnabled", "TriggersFocusMode"],
        "setters": ["IsEnabled", "TriggersFocusMode"],
        "ui_commands": [],
        "toggle_commands": ["ToggleEnabled"],
        "skip": [],
    },
    "SayAllPresenter": {
        "commands": ["SayAll", "Rewind", "FastForward"],
        "parameterized_commands": [],
        "getters": [
            "AnnounceBlockquote",
            "AnnounceForm",
            "AnnounceGrouping",
            "AnnounceLandmark",
            "AnnounceList",
            "AnnounceTable",
            "Style",
            "StructuralNavigationEnabled",
            "RewindAndFastForwardEnabled",
        ],
        "setters": [
            "AnnounceBlockquote",
            "AnnounceForm",
            "AnnounceGrouping",
            "AnnounceLandmark",
            "AnnounceList",
            "AnnounceTable",
            "Style",
            "StructuralNavigationEnabled",
            "RewindAndFastForwardEnabled",
        ],
        "ui_commands": [],
        "toggle_commands": [],
        "skip": [],
    },
    "WhereAmIPresenter": {
        "commands": [
            "PresentCharacterAttributes",
            "PresentDefaultButton",
            "PresentLink",
            "PresentSelectedText",
            "PresentSelection",
            "PresentSizeAndPosition",
            "PresentStatusBar",
            "PresentTitle",
            "WhereAmIBasic",
            "WhereAmIDetailed",
        ],
        "parameterized_commands": [],
        "getters": [],
        "setters": [],
        "ui_commands": [],
        "toggle_commands": [],
        "skip": [],
    },
    "BraillePresenter": {
        "commands": [],
        "parameterized_commands": [],
        "getters": [
            "BrailleIsEnabled",
            "VerbosityLevel",
            "RolenameStyle",
            "DisplayAncestors",
            "ContractedBrailleIsEnabled",
            "ContractionTable",
            "AvailableContractionTables",
            "EndOfLineIndicatorIsEnabled",
            "WordWrapIsEnabled",
            "FlashMessagesAreEnabled",
            "FlashMessageDuration",
            "FlashMessagesArePersistent",
            "FlashMessagesAreDetailed",
            "SelectorIndicator",
            "LinkIndicator",
            "TextAttributesIndicator",
        ],
        "setters": [
            "BrailleIsEnabled",
            "VerbosityLevel",
            "RolenameStyle",
            "DisplayAncestors",
            "ContractedBrailleIsEnabled",
            "ContractionTable",
            "EndOfLineIndicatorIsEnabled",
            "WordWrapIsEnabled",
            "FlashMessagesAreEnabled",
            "FlashMessageDuration",
            "FlashMessagesArePersistent",
            "FlashMessagesAreDetailed",
            "SelectorIndicator",
            "LinkIndicator",
            "TextAttributesIndicator",
        ],
        "ui_commands": [],
        "toggle_commands": [],
        "skip": [],
    },
}

PARAMETERIZED_TEST_PARAMS = {
    "GetVoicesForLanguage": {"language": "en", "variant": "", "notify_user": False}
}


def safe_call(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any | None:
    """Safely call a function, returning result or None on error."""

    try:
        return func(*args, **kwargs)
    except (DBusError, AttributeError, TypeError, ValueError):
        return None


def extract_names(items: list[Any] | None) -> list[str]:
    """Extract first element from list of tuples/lists, return empty list if None."""

    return [item[0] for item in items] if items else []


def is_context_error(error_str: str) -> bool:
    """Check if error indicates missing context (script/runtime).

    This function checks for common error patterns that indicate the Orca
    service is running but lacks the proper context (e.g., no active script
    or application context) to execute the requested operation.
    """

    context_error_patterns = [
        # NoneType attribute errors indicate missing objects/context
        ("NoneType" in error_str and "attribute" in error_str),
        # Script-related None errors indicate missing script context
        ("script" in error_str and "None" in error_str),
        # AT-SPI context missing
        ("context" in error_str.lower() and "none" in error_str.lower()),
        # Missing application object
        ("application" in error_str.lower() and "none" in error_str.lower()),
    ]

    return any(pattern for pattern in context_error_patterns)


def is_timeout_error(error_str: str) -> bool:
    """Check if error indicates a timeout condition."""

    timeout_patterns = [
        "timed out" in error_str.lower(),
        "timeout" in error_str.lower(),
        "deadline exceeded" in error_str.lower(),
        "connection timeout" in error_str.lower(),
    ]

    return any(pattern for pattern in timeout_patterns)


def unpack_variant(value: Any) -> Any:
    """Unpack a GLib.Variant if needed."""

    return value.unpack() if hasattr(value, "unpack") else value


def get_alternative_value(
    proxy: DBusProxy, prop_name: str, current_value: str | int | float | bool
) -> str | int | float | bool:
    """Get an alternative value for testing setters, avoiding defaults when possible."""

    try:
        if prop_name == "CurrentServer":
            servers = proxy.ExecuteRuntimeGetter("AvailableServers")
            servers = unpack_variant(servers)
            assert isinstance(current_value, str)
            non_default = [s for s in servers if s != current_value and "default" not in s.lower()]
            if non_default:
                return non_default[0]
            return next((s for s in servers if s != current_value), current_value)
        if prop_name == "CurrentSynthesizer":
            synths = proxy.ExecuteRuntimeGetter("AvailableSynthesizers")
            synths = unpack_variant(synths)
            assert isinstance(current_value, str)
            non_default = [s for s in synths if s != current_value and "default" not in s.lower()]
            if non_default:
                return non_default[0]
            return next((s for s in synths if s != current_value), current_value)
        if prop_name == "CurrentVoice":
            voices = proxy.ExecuteRuntimeGetter("AvailableVoices")
            voices = unpack_variant(voices)
            if voices and len(voices) > 1:
                assert isinstance(current_value, str)
                current_voice_name = current_value.split()[0] if current_value else ""
                non_default = [
                    v[0]
                    for v in voices
                    if v[0] != current_voice_name and "default" not in v[0].lower()
                ]
                if non_default:
                    return non_default[0]
                return next((v[0] for v in voices if v[0] != current_voice_name), current_value)
            return current_value
        return current_value
    except (DBusError, AttributeError, TypeError, ValueError):
        return current_value


def get_test_value(
    proxy: DBusProxy, prop_name: str, current_value: str | int | float | bool
) -> str | int | float | bool:
    """Generate an appropriate test value for a property."""

    if isinstance(current_value, (int, float)):
        return current_value + 1 if current_value < 100 else current_value - 1
    if isinstance(current_value, str):
        return get_alternative_value(proxy, prop_name, current_value)
    if isinstance(current_value, bool):
        return not current_value
    return current_value


def to_variant(value: str | bool | int | float) -> Any:
    """Convert a Python value to GLib.Variant."""

    if isinstance(value, str):
        return GLib.Variant("s", value)
    if isinstance(value, bool):
        return GLib.Variant("b", value)
    if isinstance(value, int):
        return GLib.Variant("i", value)
    if isinstance(value, float):
        return GLib.Variant("d", value)
    return GLib.Variant("s", str(value))


@pytest.mark.dbus
class TestOrcaDBusIntegration:
    """Integration tests for Orca D-Bus service using pytest features."""

    @pytest.mark.dbus
    def test_orca_dbus_service_running(self, dbus_service_proxy):
        """Test that Orca D-Bus service is running and accessible."""

        version = dbus_service_proxy.GetVersion()
        assert version is not None
        assert len(str(version)) > 0

    @pytest.mark.dbus
    def test_list_modules(self, dbus_service_proxy):
        """Test listing available modules."""

        modules = list(dbus_service_proxy.ListModules())
        assert isinstance(modules, list)

        expected_modules = set(MODULE_CONFIG.keys())
        actual_modules = set(modules)
        missing_modules = expected_modules - actual_modules

        assert not missing_modules, f"Missing expected modules: {missing_modules}"

    @pytest.mark.dbus
    def test_present_message(self, dbus_service_proxy):
        """Test the PresentMessage service command."""

        dbus_service_proxy.PresentMessage("Integration test message")

        # TODO - JD: What we really want to do is verify that the message was presented.
        # That will require we have a way to capture the speech and braille. Until then,
        # verify service is still responsive after presentation.
        version = dbus_service_proxy.GetVersion()
        assert version is not None

    @pytest.mark.dbus
    def test_error_handling(self, dbus_service_proxy):
        """Test error handling for invalid D-Bus calls."""

        with pytest.raises((DBusError, AttributeError, TypeError)):
            dbus_service_proxy.NonExistentMethod()

    @pytest.mark.parametrize(
        "module_name,config", MODULE_CONFIG.items(), ids=list(MODULE_CONFIG.keys())
    )
    @pytest.mark.dbus
    def test_module_capabilities(self, module_proxy_factory, run_with_timeout, module_name, config):
        """Test that each module reports correct capabilities."""
        print(f"\n  Testing {module_name} capabilities:")
        for cap_type in ["commands", "parameterized_commands", "getters", "setters"]:
            items = config.get(cap_type, [])
            if items:
                print(f"    • {cap_type}: {len(items)} items")
                for item in sorted(items)[:5]:  # Show first 5 items
                    print(f"      - {item}")
                if len(items) > 5:
                    print(f"      - ... and {len(items) - 5} more")

        def get_capabilities():
            proxy = module_proxy_factory(module_name)
            return {
                "commands": extract_names(safe_call(proxy.ListCommands)),
                "parameterized_commands": extract_names(safe_call(proxy.ListParameterizedCommands)),
                "getters": extract_names(safe_call(proxy.ListRuntimeGetters)),
                "setters": extract_names(safe_call(proxy.ListRuntimeSetters)),
            }

        timeout = MODULE_TIMEOUTS.get(module_name)
        result = run_with_timeout(get_capabilities, timeout)
        assert result["success"], f"Failed to get {module_name} capabilities: {result['error']}"

        for cap_type in ["commands", "parameterized_commands", "getters", "setters"]:
            expected = set(config.get(cap_type, []))
            actual = set(result["result"].get(cap_type, []))
            missing = expected - actual
            unexpected = actual - expected

            assert not missing, f"{module_name} missing {cap_type}: {sorted(missing)}"
            assert not unexpected, f"{module_name} unexpected {cap_type}: {sorted(unexpected)}"

    @pytest.mark.parametrize(
        "module_name,config",
        [(name, config) for name, config in MODULE_CONFIG.items() if config.get("commands")],
        ids=[name for name, config in MODULE_CONFIG.items() if config.get("commands")],
    )
    @pytest.mark.dbus
    def test_module_commands(self, module_proxy_factory, run_with_timeout, module_name, config):
        """Test that module commands execute without errors."""
        commands = config["commands"]
        ui_commands = config.get("ui_commands", [])
        toggle_commands = config.get("toggle_commands", [])
        skip_commands = config.get("skip", [])
        print(f"\n  Testing {module_name} commands ({len(commands)} total):")
        for cmd in sorted(commands):
            status_parts = []
            if cmd in ui_commands:
                status_parts.append("UI - skipped")
            if cmd in skip_commands:
                status_parts.append("skipped")
            if cmd in toggle_commands:
                status_parts.append("toggle - restore state")
            status = f"({', '.join(status_parts)})" if status_parts else ""
            print(f"    • {cmd} {status}")

        def test_single_command(proxy, cmd_name, ui_commands, toggle_commands, skip_commands):
            if cmd_name in ui_commands or cmd_name in skip_commands:
                return {"success": True, "skipped": True}
            try:
                proxy.ExecuteCommand(cmd_name, False)
                if cmd_name in toggle_commands:
                    print(f"      → Restoring {cmd_name} to original state")
                    proxy.ExecuteCommand(cmd_name, False)
                return {"success": True}
            except (DBusError, AttributeError, TypeError, ValueError) as error:
                error_str = str(error)
                if is_context_error(error_str) or is_timeout_error(error_str):
                    return {"success": True, "context_required": True}
                return {"success": False, "error": error_str}

        def test_commands():
            proxy = module_proxy_factory(module_name)
            ui_commands = config.get("ui_commands", [])
            toggle_commands = config.get("toggle_commands", [])
            skip_commands = config.get("skip", [])
            return {
                cmd: test_single_command(proxy, cmd, ui_commands, toggle_commands, skip_commands)
                for cmd in config["commands"]
            }

        timeout = MODULE_TIMEOUTS.get(module_name)
        result = run_with_timeout(test_commands, timeout)
        assert result["success"], f"Failed to test {module_name} commands: {result['error']}"

        failed = [
            f"{cmd}: {res['error']}"
            for cmd, res in result["result"].items()
            if not res["success"] and not res.get("skipped")
        ]
        assert not failed, f"{module_name} command failures: {failed}"

    @pytest.mark.parametrize(
        "module_name,config",
        [
            (name, config)
            for name, config in MODULE_CONFIG.items()
            if config.get("parameterized_commands")
        ],
        ids=[
            name for name, config in MODULE_CONFIG.items() if config.get("parameterized_commands")
        ],
    )
    @pytest.mark.dbus
    def test_module_parameterized_commands(
        self, module_proxy_factory, run_with_timeout, module_name, config
    ):
        """Test that module parameterized commands execute with proper parameters."""
        param_commands = config["parameterized_commands"]
        print(f"\n  Testing {module_name} parameterized commands ({len(param_commands)} total):")
        for cmd in sorted(param_commands):
            params = PARAMETERIZED_TEST_PARAMS.get(cmd, {})
            param_str = ", ".join(f"{k}={v}" for k, v in params.items())
            print(f"    • {cmd}({param_str})")

        def test_single_param_command(proxy, cmd_name):
            params = PARAMETERIZED_TEST_PARAMS.get(cmd_name, {})
            if not params:
                return {"success": False, "error": "No test parameters"}

            try:
                variant_params = {k: to_variant(v) for k, v in params.items() if k != "notify_user"}
                notify_user = params.get("notify_user", False)
                result = proxy.ExecuteParameterizedCommand(cmd_name, variant_params, notify_user)
                return {"success": True, "result": result}
            except (DBusError, AttributeError, TypeError, ValueError) as error:
                if is_context_error(str(error)):
                    return {"success": True, "context_required": True}
                return {"success": False, "error": str(error)}

        def test_parameterized_commands():
            if GLib is None:
                pytest.skip("GLib not available")
            proxy = module_proxy_factory(module_name)
            return {
                cmd: test_single_param_command(proxy, cmd)
                for cmd in config["parameterized_commands"]
            }

        timeout = MODULE_TIMEOUTS.get(module_name)
        result = run_with_timeout(test_parameterized_commands, timeout)
        error_msg = f"Failed to test {module_name} parameterized commands: {result['error']}"
        assert result["success"], error_msg

        failed = [
            f"{cmd}: {res['error']}"
            for cmd, res in result["result"].items()
            if not res["success"] and not res.get("context_required")
        ]
        assert not failed, f"{module_name} parameterized command failures: {failed}"

    @pytest.mark.parametrize(
        "module_name,config",
        [
            (name, config)
            for name, config in MODULE_CONFIG.items()
            if config.get("getters") or config.get("setters")
        ],
        ids=[
            name
            for name, config in MODULE_CONFIG.items()
            if config.get("getters") or config.get("setters")
        ],
    )
    @pytest.mark.dbus
    def test_module_getters_setters(
        self, module_proxy_factory, run_with_timeout, module_name, config
    ):
        """Test that module getter/setter pairs work correctly."""
        all_props = sorted(set(config.get("getters", []) + config.get("setters", [])))
        print(f"\n  Testing {module_name} properties ({len(all_props)} total):")
        for prop in all_props:
            has_getter = prop in config.get("getters", [])
            has_setter = prop in config.get("setters", [])
            status_parts = []
            if has_getter:
                status_parts.append("get")
            if has_setter:
                status_parts.append("set")
            status = f"({'/'.join(status_parts)})" if status_parts else ""
            print(f"    • {prop} {status}")

        def test_single_property(proxy, prop_name, is_setter=False):
            try:
                current_value = unpack_variant(proxy.ExecuteRuntimeGetter(prop_name))
                if is_setter:
                    test_value = get_test_value(proxy, prop_name, current_value)
                    proxy.ExecuteRuntimeSetter(prop_name, to_variant(test_value))
                    new_value = unpack_variant(proxy.ExecuteRuntimeGetter(prop_name))
                    proxy.ExecuteRuntimeSetter(prop_name, to_variant(current_value))
                    return {
                        "success": True,
                        "original_value": current_value,
                        "test_value": test_value,
                        "actual_new_value": new_value,
                    }
                return {"success": True, "value": current_value}
            except (DBusError, AttributeError, TypeError, ValueError) as error:
                return {"success": False, "error": str(error)}

        def test_getters_setters():
            proxy = module_proxy_factory(module_name)
            results = {}

            for prop in config.get("getters", []):
                results[f"get_{prop}"] = test_single_property(proxy, prop, is_setter=False)

            for prop in config.get("setters", []):
                results[f"set_{prop}"] = test_single_property(proxy, prop, is_setter=True)

            return results

        timeout = MODULE_TIMEOUTS.get(module_name)
        result = run_with_timeout(test_getters_setters, timeout)
        assert result["success"], f"Failed to test {module_name} getters/setters: {result['error']}"

        if result["result"]:
            getter_results = {k: v for k, v in result["result"].items() if k.startswith("get_")}
            setter_results = {k: v for k, v in result["result"].items() if k.startswith("set_")}

            if getter_results:
                print("    Getter values:")
                for prop_key, res in getter_results.items():
                    prop = prop_key[4:]
                    if res["success"]:
                        print(f"      - {prop}: {res['value']}")
                    else:
                        print(f"      - {prop}: ERROR - {res['error']}")

            if setter_results:
                print("    Setter tests:")
                for prop_key, res in setter_results.items():
                    prop = prop_key[4:]
                    if res["success"]:
                        original = res["original_value"]
                        test_val = res["test_value"]
                        actual = res["actual_new_value"]
                        print(f"      - {prop}: {original} → {test_val} (got: {actual})")
                    else:
                        print(f"      - {prop}: ERROR - {res['error']}")

        failed = [
            f"{prop}: {res['error']}"
            for prop, res in result["result"].items()
            if not res["success"]
        ]
        assert not failed, f"{module_name} getter/setter failures: {failed}"

    @pytest.mark.dbus
    def test_parameterized_command_signatures(self, module_proxy_factory, run_with_timeout):
        """Test that parameterized commands have correct parameter signatures."""

        def get_signatures():
            proxy = module_proxy_factory("SpeechAndVerbosityManager")
            commands = proxy.ListParameterizedCommands()
            return {cmd[0]: [list(p[:2]) for p in cmd[2]] for cmd in commands}

        result = run_with_timeout(get_signatures)
        error_msg = f"Could not get parameterized command signatures: {result['error']}"
        assert result["success"], error_msg

        signatures = result["result"]
        if "GetVoicesForLanguage" in signatures:
            expected = [["language", "str"], ["variant", "str"], ["notify_user", "bool"]]
            actual = signatures["GetVoicesForLanguage"]
            error_msg = (
                f"GetVoicesForLanguage signature mismatch: expected {expected}, got {actual}"
            )
            assert actual == expected, error_msg

    @pytest.mark.dbus
    def test_no_unexpected_modules(self, dbus_service_proxy):
        """Test that no unexpected modules exist - ensures test coverage for all modules."""

        actual_modules = set(dbus_service_proxy.ListModules())
        expected_modules = set(MODULE_CONFIG.keys())
        unexpected_modules = actual_modules - expected_modules - OPTIONAL_MODULES

        if unexpected_modules:
            module_list = sorted(unexpected_modules)
            error_msg = (
                f"Found {len(unexpected_modules)} unexpected modules that lack test coverage: "
                f"{module_list}\n"
                f"Please add configuration for these modules to MODULE_CONFIG in the test file."
            )
            assert False, error_msg
