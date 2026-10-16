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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA 02110-1301 USA.

"""Tests for generated help navigation and inline keys."""

from __future__ import annotations

import ast
import gettext
import json
import re
import runpy
import shutil
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_HELP_DIR = _ROOT / "help_ng"
_METADATA_PATH = _HELP_DIR / "generated_help_metadata.json"
_SCRIPT = _ROOT / "tools" / "generate_help_documentation.py"
_NS = {"m": "http://projectmallard.org/1.0/"}


def _parse_generated_page(content: str) -> ET.Element:
    """Parses trusted XML produced by the generator under test."""

    return ET.fromstring(content)  # noqa: S314


@pytest.fixture(scope="module")
def generator() -> dict[str, Any]:
    """Loads the standalone generator without Orca's runtime dependencies."""

    with pytest.MonkeyPatch.context() as patch:
        patch.syspath_prepend(str(_SCRIPT.parent))
        return runpy.run_path(str(_SCRIPT))


@pytest.mark.parametrize(
    ("text", "keys"),
    (
        ("Press Alt+Super+S.", ["Alt", "Super", "S"]),
        ("Press Orca Modifier+Space.", ["Orca Modifier", "Space"]),
        ("Press Shift+Tab.", ["Shift", "Tab"]),
        ("Press Orca Modifier+Z.", ["Orca Modifier", "Z"]),
        ("Choose Insert, Keypad Insert, or Caps Lock.", ["Insert", "Keypad Insert", "Caps Lock"]),
        ("Turn Num Lock off.", ["Num Lock"]),
        ("Press Shift+Insert.", ["Shift", "Insert"]),
        ("An S in prose is not a shortcut.", []),
    ),
)
def test_inline_key_markup(generator: dict[str, Any], text: str, keys: list[str]) -> None:
    """Marks up modifier combinations without treating ordinary letters as keys."""

    parent = ET.Element("test")
    generator["_add_text_paragraphs"](parent, text)
    assert [key.text for key in parent.findall(".//m:key", _NS)] == keys
    expected_text = text.replace("+", "") if keys else text
    assert "".join(parent.itertext()) == expected_text


@pytest.mark.parametrize(
    ("text", "codes", "keys"),
    (
        ("Run `orca --help`.", ["orca --help"], []),
        ("Run `orca` or press Alt+Super+S.", ["orca"], ["Alt", "Super", "S"]),
        ("Inspect `F2` then press F2.", ["F2"], ["F2"]),
        ("Read `<FILE> & NAME`.", ["<FILE> & NAME"], []),
        ("An unmatched ` remains literal.", [], []),
    ),
)
def test_inline_code_markup(
    generator: dict[str, Any], text: str, codes: list[str], keys: list[str]
) -> None:
    """Formats literal spans without treating their contents as keyboard shortcuts."""

    parent = ET.Element("test")
    generator["_add_text_paragraphs"](parent, text)
    assert [code.text for code in parent.findall(".//m:code", _NS)] == codes
    assert [key.text for key in parent.findall(".//m:key", _NS)] == keys
    expected = text
    for code in codes:
        expected = expected.replace(f"`{code}`", code)
    if keys:
        expected = expected.replace("+", "")
    assert "".join(parent.itertext()) == expected


def test_prose_bullet_lists(generator: dict[str, Any]) -> None:
    """Keeps paragraphs and list items distinct while formatting inline content."""

    parent = ET.Element("test")
    generator["_add_text_paragraphs"](
        parent,
        "Options:\n\n- `orca --help`: Display help.\n- Press Shift+Tab.\n\nMore information.",
    )
    assert [child.tag.rsplit("}", 1)[-1] for child in parent] == ["p", "list", "p"]
    items = parent.findall("m:list/m:item", _NS)
    assert len(items) == 2
    assert items[0].find("m:p/m:code", _NS).text == "orca --help"
    assert [key.text for key in items[1].findall(".//m:key", _NS)] == ["Shift", "Tab"]


def test_index_sections(generator: dict[str, Any]) -> None:
    """Preserves the guide destinations and two-column index layout."""

    metadata = json.loads(_METADATA_PATH.read_text())
    page = generator["_build_help_index_page"](metadata["index"]).getroot()
    assert page.get("type") == "guide"
    assert page.get("id") == "index"
    sections = page.findall("m:section", _NS)
    assert [section.get("id") for section in sections] == [
        "getting_started",
        "reading",
        "reviewing",
        "output",
        "interaction",
        "information",
        "troubleshooting",
    ]
    assert all(section.get("style") == "2column" for section in sections)


def test_preview_index_is_generated_and_checked(
    generator: dict[str, Any],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Generates a complete fresh preview and detects stale index content."""

    argv = [str(_SCRIPT), "--output-dir", str(tmp_path)]
    monkeypatch.setattr("sys.argv", argv)
    assert generator["main"]() == 0
    index = tmp_path / "index.page"
    assert "This file is generated" in index.read_text()
    assert (tmp_path / "introduction.page").exists()
    assert (tmp_path / "figures/orca-logo.svg").exists()

    index.write_text("out of date\n")
    monkeypatch.setattr("sys.argv", [*argv, "--check"])
    assert generator["main"]() == 1


def test_default_generation_preserves_installed_help(
    generator: dict[str, Any], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Default generation and freshness checks use only the uninstalled preview."""

    shutil.copytree(_HELP_DIR, tmp_path / "help_ng", ignore=shutil.ignore_patterns("*.page"))
    installed_help = tmp_path / "help/C/index.page"
    installed_help.parent.mkdir(parents=True)
    installed_help.write_text("Installed help must remain unchanged.\n")
    namespace = generator["main"].__globals__
    script = tmp_path / "tools/generate_help_documentation.py"
    monkeypatch.setitem(namespace, "__file__", str(script))
    argv = [str(script), "--src-dir", str(_ROOT / "src")]
    monkeypatch.setattr("sys.argv", argv)
    assert generator["main"]() == 0
    assert (tmp_path / "help_ng/index.page").exists()
    assert installed_help.read_text() == "Installed help must remain unchanged.\n"
    monkeypatch.setattr("sys.argv", [*argv, "--check"])
    assert generator["main"]() == 0


@pytest.fixture(scope="module")
def topic_commands(generator: dict[str, Any]) -> dict[str, Any]:
    """Collects source metadata once for command-consolidation tests."""

    source = _ROOT / "src"
    groups = generator["collect_command_page_groups"](source)
    pages, reusable = generator["collect_feature_documentation"](source)
    preferences = generator["collect_preference_page_docs"](
        source,
        _METADATA_PATH,
    )
    targets = {
        **generator["_preference_target_registry"](preferences, pages, reusable),
        **generator["_feature_target_registry"](pages, reusable),
        **generator["_feature_command_targets"](pages, reusable, groups),
    }
    link_text = {
        **generator["_preference_link_text_registry"](preferences),
        **generator["_feature_link_text_registry"](pages, reusable),
        **generator["_command_link_text_registry"](groups),
    }
    metadata = json.loads(_METADATA_PATH.read_text())
    associations = generator["_preference_command_links"](preferences, groups, targets, link_text)
    rendered = generator["build_feature_pages"](
        pages,
        targets,
        link_text,
        reusable,
        metadata["feature_order"],
        groups,
        associations,
        preferences,
    )
    all_rendered = dict(rendered)
    all_rendered["index.page"] = generator["_serialize"](
        generator["_build_help_index_page"](metadata["index"])
    )
    return {
        "groups": groups,
        "pages": pages,
        "reusable": reusable,
        "targets": targets,
        "link_text": link_text,
        "feature_order": metadata["feature_order"],
        "preferences": preferences,
        "associations": associations,
        "rendered": rendered,
        "all_rendered": all_rendered,
    }


@pytest.mark.parametrize("change", ("missing", "unknown", "duplicate"))
def test_feature_order_inventory(
    generator: dict[str, Any], topic_commands: dict[str, Any], change: str
) -> None:
    """Requires an explicit, unique central position for every feature page."""

    order = list(topic_commands["feature_order"])
    if change == "missing":
        order.pop()
    elif change == "unknown":
        order.append("features_unknown")
    else:
        order.append(order[0])
    with pytest.raises(ValueError, match="feature_order"):
        generator["build_feature_pages"](
            topic_commands["pages"],
            topic_commands["targets"],
            topic_commands["link_text"],
            topic_commands["reusable"],
            order,
            topic_commands["groups"],
        )


def test_feature_order_is_central(
    generator: dict[str, Any], topic_commands: dict[str, Any]
) -> None:
    """Reorders generated topics without changing feature definitions."""

    order = list(reversed(topic_commands["feature_order"]))
    rendered = generator["build_feature_pages"](
        topic_commands["pages"],
        topic_commands["targets"],
        topic_commands["link_text"],
        topic_commands["reusable"],
        order,
        topic_commands["groups"],
        preference_pages=topic_commands["preferences"],
    )
    for index, page_id in enumerate(order, start=1):
        filename = f"{page_id}.page"
        page = _parse_generated_page(rendered[filename])
        sort_title = page.find("m:info/m:title[@type='sort']", _NS)
        assert sort_title is not None
        assert sort_title.text.startswith(f"{index:02d}. ")


def test_preferences_opening_workflow(topic_commands: dict[str, Any]) -> None:
    """Explains opening preferences before listing commands, without redundant related links."""

    page = _parse_generated_page(topic_commands["rendered"]["preferences_guide.page"])
    section = page.find("m:section[@id='opening-preferences']", _NS)
    assert section is not None
    assert [child.tag.rsplit("}", 1)[-1] for child in section] == [
        "title",
        "p",
        "p",
        "p",
        "section",
    ]
    paragraphs = section.findall("m:p", _NS)
    assert "Use the commands below" in "".join(paragraphs[0].itertext())
    assert "orca --setup" in "".join(paragraphs[1].itertext())
    assert section.find("m:section/m:title[.='Commands']", _NS) is not None
    assert section.find(".//m:link", _NS) is None
    saving = page.find("m:section[@id='changing-and-saving-settings']", _NS)
    assert saving is not None
    assert saving.find(".//m:link", _NS) is None
    assert "F10" in [key.text for key in saving.findall(".//m:key", _NS)]
    assert "Escape" in [key.text for key in saving.findall(".//m:key", _NS)]
    sequences = [
        [key.text for key in sequence.findall("m:key", _NS)]
        for sequence in saving.findall(".//m:keyseq", _NS)
    ]
    assert ["Alt", "F4"] in sequences
    assert "close without saving" in "".join(saving.itertext())
    assert "The links below describe" not in "".join(saving.itertext())
    heading = page.find("m:section[@id='settings-categories']/m:title", _NS)
    assert heading is not None
    assert heading.text == "Settings categories"


def test_every_command_rendered_once(topic_commands: dict[str, Any]) -> None:
    """Preserves every keyboard and braille command without duplicate topic listings."""

    expected = Counter(
        command.label for _page, group in topic_commands["groups"] for command in group.commands
    )
    roots = [_parse_generated_page(content) for content in topic_commands["rendered"].values()]
    for root in roots:
        for section in root.findall(".//m:section", _NS):
            if section.get("id", "").startswith("settings-"):
                section.clear()
    actual = Counter(
        label.text for root in roots for label in root.findall(".//m:item/m:p/m:gui", _NS)
    )
    assert actual == expected


def test_old_command_pages_are_not_generated(
    topic_commands: dict[str, Any],
) -> None:
    """Topics never link to obsolete command pages or the retired index."""

    assert "commands.page" not in topic_commands["rendered"]
    for content in topic_commands["rendered"].values():
        page = _parse_generated_page(content)
        for link in page.findall(".//m:link", _NS):
            xref = link.get("xref", "")
            assert not xref.startswith("commands_")
            assert xref.split("#", 1)[0] != "commands"


def test_command_context_is_preserved(topic_commands: dict[str, Any]) -> None:
    """Retains explanations, restrictions, subsections, and display bindings."""

    pages = topic_commands["rendered"]
    assert "python3-psutil" in pages["features_system_information.page"]
    assert "Wayland" in pages["features_clipboard.page"]
    assert "Wayland" in pages["features_reviewing_objects_mouse_review.page"]
    assert "Dynamic headers" in pages["features_reading_documents_table_navigation.page"]
    assert "To set column headers" in pages["features_reading_documents_table_navigation.page"]
    for topic in ("output", "display_settings"):
        assert "Standard keyboard commands" in pages[f"features_braille_{topic}.page"]
        assert "Braille display commands" in pages[f"features_braille_{topic}.page"]
    assert "unbound command" in pages["features_speech_and_voices_voice_sets.page"]


def test_missing_command_topic_is_an_error(
    generator: dict[str, Any],
    topic_commands: dict[str, Any],
) -> None:
    """New commands cannot silently disappear from the help."""

    with pytest.raises(ValueError, match="without a feature topic"):
        generator["_feature_command_targets"]([], {}, topic_commands["groups"])


def test_duplicate_command_topic_is_an_error(
    generator: dict[str, Any],
    topic_commands: dict[str, Any],
) -> None:
    """A command cannot be explicitly documented in two feature sections."""

    pages = topic_commands["pages"]
    with pytest.raises(ValueError, match="included more than once"):
        generator["_feature_command_targets"](
            [*pages, *pages],
            topic_commands["reusable"],
            topic_commands["groups"],
        )


def test_help_preview_is_not_installed_or_translated(topic_commands: dict[str, Any]) -> None:
    """The English preview leaves installed help and translation inputs separate."""

    manifest = (_ROOT / "help/meson.build").read_text()
    installed = set(re.findall(r"'([^']+\.page)'", manifest.split("media:", 1)[0]))
    assert installed == {page.name for page in (_ROOT / "help/C").glob("*.page")}
    assert set(topic_commands["all_rendered"]) == {page.name for page in _HELP_DIR.glob("*.page")}
    for path in ("meson.build", "help/meson.build", "po/POTFILES.in"):
        assert "help_ng" not in (_ROOT / path).read_text()
    for filename in installed:
        assert "This file is generated" not in (_ROOT / "help/C" / filename).read_text()
    source_manifest = (_ROOT / "src/orca/meson.build").read_text()
    for module in (_ROOT / "src/orca").glob("*_feature_documentation.py"):
        assert f"'{module.name}'" not in source_manifest


def test_preferences_has_one_landing_page(topic_commands: dict[str, Any]) -> None:
    """Combines the shared preferences workflow with the settings directory."""

    pages = topic_commands["rendered"]
    assert "features_configuring_orca.page" not in pages
    assert topic_commands["targets"]["screen-reader.configuration"] == "preferences_guide"
    preferences = _parse_generated_page(pages["preferences_guide.page"])
    assert preferences.get("type") == "guide"
    assert (
        preferences.find(
            "m:section[@id='settings-categories']/m:links[@type='topic'][@style='2column']", _NS
        )
        is not None
    )
    labels = [label.text for label in preferences.findall(".//m:item/m:p/m:gui", _NS)]
    assert labels == [
        "Display the preferences window",
        "Display the application preferences window",
    ]


def test_startup_does_not_repeat_other_topics(topic_commands: dict[str, Any]) -> None:
    """Leaves keyboard, learning, and configuration explanations in their own topics."""

    intro = topic_commands["rendered"]["introduction.page"]
    assert "Starting and stopping Orca" in intro
    assert "Keyboard Layout" not in intro
    assert "Learn mode" not in intro
    assert "orca --profile NAME" in intro
    assert "orca --setup" in intro
    assert "Use the following commands to open" not in intro


def test_troubleshooting_stays_on_topic(topic_commands: dict[str, Any]) -> None:
    """Keeps automation and startup cross-references out of troubleshooting."""

    content = topic_commands["rendered"]["features_debugging.page"]
    assert "Remote control" not in content
    assert "org.gnome.Orca1.Service" not in content
    assert 'xref="introduction' not in content
    assert "verbose debugging" in content


def test_preferences_workflow_has_one_owner(topic_commands: dict[str, Any]) -> None:
    """Keeps setup examples in startup and preferences, and saving details in preferences."""

    matches = [
        filename for filename, content in topic_commands["rendered"].items() if "orca -s" in content
    ]
    assert sorted(matches) == ["introduction.page", "preferences_guide.page"]
    for filename in ("features_keyboard_layout.page", "features_profiles.page"):
        content = topic_commands["all_rendered"][filename]
        assert "without closing" not in content
        assert "Preferences location:" in content


def test_profiles_are_consolidated_in_feature(topic_commands: dict[str, Any]) -> None:
    """Preserves profile instructions and commands without a separate Getting Started topic."""

    assert "preferences_profiles.page" not in topic_commands["all_rendered"]
    assert topic_commands["targets"]["profiles.feature"] == "features_profiles"
    content = topic_commands["all_rendered"]["features_profiles.page"]
    for text in (
        "orca --profile NAME",
        "unsaved changes are not copied",
        "Default profile cannot be renamed",
        "Default profile cannot be renamed or removed",
        "select an existing profile",
        "Writer-specific settings",
    ):
        assert text in " ".join("".join(_parse_generated_page(content).itertext()).split())
    page = _parse_generated_page(content)
    commands = page.find("m:section[@id='commands-profiles']", _NS)
    assert commands is not None
    assert len(commands.findall("m:list/m:item", _NS)) == 2
    assert not any(
        link.get("xref", "").startswith("preferences_profiles")
        for link in page.findall(".//m:link", _NS)
    )
    for name in ("cycleSettingsProfileHandler", "presentCurrentProfileHandler"):
        assert topic_commands["targets"][f"command:keyboard:{name}"] == (
            "features_profiles#commands-profiles"
        )


def test_feature_can_embed_individual_commands_and_settings(generator: dict[str, Any]) -> None:
    """Explicit command subsets and settings share a feature topic."""

    category = generator["PreferenceCategoryDoc"]("test", "Test", "Test settings", ("test.panel",))
    panel = generator["PanelDoc"](
        "test.panel", "Test", "", category=category, command_names=("test_command",)
    )
    page = generator["PageDoc"](
        "preferences_test",
        "preferences_test.page",
        "Test Preferences",
        "Test",
        "Test",
        "Test settings",
        [panel],
    )
    command = generator["CollectedCommandDoc"]("test_command", label="Test command")
    groups = [("commands_test", generator["CollectedCommandGroupDoc"]("Test", commands=[command]))]
    feature = generator["FeaturePageDoc"](
        page_id="features_test",
        title="Test",
        link_title="Test",
        description="Test",
        guide_xref="index",
        sections=(
            generator["FeatureSectionDoc"](
                title="Test", command_names=("test_command",), preference_categories=("test",)
            ),
        ),
    )
    targets = generator["_feature_command_targets"]([feature], {}, groups)
    assert targets["command:keyboard:test_command"] == "features_test"
    targets.update(generator["_preference_target_registry"]([page], [feature], {}))
    rendered = generator["build_feature_pages"](
        [feature], targets, {}, {}, ["features_test"], groups, preference_pages=[page]
    )
    root = _parse_generated_page(rendered["features_test.page"])
    label = root.find("m:section[@id='commands-test']/m:list/m:item/m:p/m:gui", _NS)
    assert label is not None and label.text == "Test command"
    assert root.find("m:section[@id='settings-test']", _NS) is not None
    with pytest.raises(ValueError, match="included more than once"):
        generator["_feature_command_targets"]([feature, feature], {}, groups)


def test_sleep_mode_has_one_feature_page(topic_commands: dict[str, Any]) -> None:
    """Consolidates settings and commands without losing category navigation or UI labels."""

    assert "preferences_sleep_mode.page" not in topic_commands["all_rendered"]
    targets = topic_commands["targets"]
    destination = "features_sleep_mode"
    for reference in ("preferences.sleep-mode", "preferences_sleep_mode"):
        assert targets[reference] == destination
    page = _parse_generated_page(topic_commands["rendered"]["features_sleep_mode.page"])
    sections = page.findall("m:section", _NS)
    assert [section.findtext("m:title", namespaces=_NS) for section in sections] == [
        "Settings",
        "Commands",
    ]
    settings, commands = sections
    assert settings.find("m:info", _NS) is None
    assert settings.findtext("m:p/m:gui", namespaces=_NS) == "Sleep mode"
    assert [label.text for label in commands.findall("m:p/m:gui", _NS)] == [
        "Commands",
        "Commands",
        "Sleep mode",
    ]
    text = " ".join("".join(page.itertext()).split())
    assert text.count("Sleep mode temporarily disables Orca") == 1
    assert "Preferences location: Sleep mode category (global only)." in text
    assert "Preferences location: Commands category, Commands section, Sleep mode group." in text
    assert "only in the global preferences window" not in text
    assert "saved applications remain listed" in text
    assert len(page.findall(".//m:keyseq", _NS)) == 1
    assert not any(
        link.get("xref", "").startswith("features_sleep_mode")
        for link in page.findall(".//m:link", _NS)
    )
    directory = _parse_generated_page(topic_commands["all_rendered"]["preferences_guide.page"])
    assert directory.find(".//m:info/m:link[@xref='features_sleep_mode']", _NS) is not None
    available = settings.find("m:p/m:em[.='Available settings:']", _NS)
    assert available is not None and available.get("style") == "strong"


@pytest.mark.parametrize("global_only", (False, True))
def test_preferences_location_supports_groups(generator: dict[str, Any], global_only: bool) -> None:
    """Uses the same compact path format for category and subgroup settings."""

    parent = ET.Element("test")
    generator["_add_preferences_location"](
        parent, (("Foo", "category"), ("Bar", "group")), global_only=global_only
    )
    text = "".join(parent.itertext())
    suffix = " (global only)." if global_only else "."
    assert text == f"Preferences location: Foo category, Bar group{suffix}"
    preface = parent.find("m:p/m:em[@style='strong']", _NS)
    assert preface is not None
    assert preface.text == "Preferences location:"
    assert [label.text for label in parent.findall("m:p/m:gui", _NS)] == ["Foo", "Bar"]


def test_speech_settings_follow_the_preferences_ui(topic_commands: dict[str, Any]) -> None:
    """Speech support belongs to Speech; Global Voice Settings contains two groups."""

    pages = topic_commands["rendered"]
    guide = _parse_generated_page(pages["features_speech_and_voices_guide.page"])
    assert guide.find("m:section", _NS) is None
    output = _parse_generated_page(pages["features_speech_and_voices_output.page"])
    settings = output.find("m:section[@id='settings-speech-output']", _NS)
    assert settings is not None
    assert settings.find(".//m:gui[.='Speech support']", _NS) is not None
    assert guide.find("m:links[@type='topic'][@style='2column']", _NS) is not None
    page = _parse_generated_page(pages["features_speech_and_voices_global_voice_settings.page"])
    assert page.find(".//m:gui[.='Speech support']", _NS) is None
    groups = page.findall(
        "m:section[@id='settings-global-voice-settings']/m:list/m:item/m:p/m:gui", _NS
    )
    assert [group.text for group in groups] == ["Global Voice Settings", "Language Switching"]
    assert topic_commands["targets"]["speech.global-voice-settings"] == (
        "features_speech_and_voices_global_voice_settings#settings-global-voice-settings"
    )


def test_braille_guide_combines_settings_and_applicable_commands(
    topic_commands: dict[str, Any],
) -> None:
    """Each braille settings area has its own topic, with related bindings alongside it."""

    pages = topic_commands["rendered"]
    guide = _parse_generated_page(pages["features_braille_guide.page"])
    assert guide.get("type") == "guide"
    assert guide.find("m:links[@type='topic'][@style='2column']", _NS) is not None
    assert guide.find(".//m:list", _NS) is None
    topics = (
        "output",
        "verbosity",
        "display_settings",
        "flash_messages",
        "progress_bars",
        "on_screen_display",
    )
    for topic in topics:
        page = _parse_generated_page(pages[f"features_braille_{topic}.page"])
        assert (
            page.find("m:info/m:link[@type='guide'][@xref='features_braille_guide']", _NS)
            is not None
        )
        assert page.find("m:section/m:title[.='Settings']", _NS) is not None
    targets = topic_commands["targets"]
    assert targets["command:keyboard:toggle_braille_monitor"].startswith(
        "features_braille_on_screen_display#"
    )
    for kind in ("keyboard", "braille"):
        assert targets[f"command:{kind}:contractedBrailleHandler"].startswith(
            "features_braille_display_settings#"
        )
        assert targets[f"command:{kind}:panBrailleLeftHandler"].startswith(
            "features_braille_output#"
        )


def test_braille_output_does_not_reference_flat_review(topic_commands: dict[str, Any]) -> None:
    """Braille Output stays focused on its own settings and commands."""

    page = _parse_generated_page(topic_commands["rendered"]["features_braille_output.page"])
    assert "flat review" not in "".join(page.itertext()).lower()
    assert page.find(".//m:link[@xref='features_reviewing_objects_flat_review']", _NS) is None


def test_echo_topic_distinguishes_key_and_typing_echo(topic_commands: dict[str, Any]) -> None:
    """Echo is the overall feature; key echo and typing echo are distinct kinds of feedback."""

    page = _parse_generated_page(topic_commands["rendered"]["features_typing_echo.page"])
    assert page.findtext("m:info/m:title[@type='link']", namespaces=_NS) == "Echo"
    title = page.find("m:title", _NS)
    assert title is not None and "".join(title.itertext()).strip() == "Echo"
    paragraphs = [" ".join("".join(p.itertext()).split()) for p in page.findall("m:p", _NS)]
    assert paragraphs[0].startswith("Key echo announces the keys you press.")
    assert paragraphs[1].startswith("Typing echo announces text inserted into an editable field.")
    assert "completed sentences" in paragraphs[1]
    assert "same character twice" in paragraphs[1]


def test_orca_find_does_not_reference_mouse_commands(topic_commands: dict[str, Any]) -> None:
    """Find documentation stays about searching and the resulting flat review location."""

    page = _parse_generated_page(
        topic_commands["rendered"]["features_reviewing_objects_orca_find.page"]
    )
    assert "mouse commands" not in "".join(page.itertext()).lower()
    assert (
        page.find(".//m:link[@xref='features_reviewing_objects_mouse_review#commands-mouse']", _NS)
        is None
    )
    assert page.find(".//m:link[@xref='features_reviewing_objects_flat_review']", _NS) is not None


def test_where_am_i_has_one_command_location(topic_commands: dict[str, Any]) -> None:
    """Common command locations belong to the page; formatting has its own related topic."""

    page = _parse_generated_page(topic_commands["rendered"]["features_where_am_i.page"])
    labels = page.findall(".//m:em[.='Preferences location:']", _NS)
    assert len(labels) == 1
    assert page.find("m:p/m:em[.='Preferences location:']", _NS) is not None
    other = page.find("m:section[@id='other-ways-to-get-details']", _NS)
    assert other is not None
    assert "Text Attributes" not in "".join(other.itertext())
    assert (
        page.find("m:section[@id='related-topics']//m:link[@xref='features_text_attributes']", _NS)
        is not None
    )


def test_document_guide_links_existing_math_topic(topic_commands: dict[str, Any]) -> None:
    """Includes math without generating a second copy of its settings and commands."""

    page = _parse_generated_page(
        topic_commands["rendered"]["features_reading_documents_guide.page"]
    )
    assert (
        page.find("m:info/m:link[@type='topic'][@xref='features_math_navigation']", _NS) is not None
    )
    introduction = page.find("m:p", _NS)
    assert introduction is not None
    assert "tables" not in "".join(introduction.itertext())
    assert "live regions" not in "".join(introduction.itertext())


def test_keyboard_layout_explanation_and_keys(topic_commands: dict[str, Any]) -> None:
    """Explains the modifier options and layouts using individual key markup."""

    page = _parse_generated_page(topic_commands["rendered"]["features_keyboard_layout.page"])
    text = " ".join("".join(page.itertext()).split())
    assert "In this documentation" in text
    assert "twice quickly" in text
    assert "Laptop does not use keypad keys" in text
    assert "Num Lock must be off to use Desktop keypad shortcuts." in text
    paragraphs = [" ".join("".join(p.itertext()).split()) for p in page.findall("m:p", _NS)]
    assert any(
        paragraph.startswith("Orca takes over the normal behavior of configured modifier keys.")
        and "Press a configured modifier key twice quickly" in paragraph
        for paragraph in paragraphs
    )
    assert "To switch layouts without opening preferences" not in text
    assert "Choose a group from the list" not in text
    assert [
        section.findtext("m:title", namespaces=_NS) for section in page.findall("m:section", _NS)
    ] == ["Settings", "Commands", "Related topics"]
    keys = {key.text for key in page.findall(".//m:key", _NS)}
    assert {"Insert", "Keypad Insert", "Caps Lock", "Num Lock"} <= keys


def test_preferences_window_capitalization(topic_commands: dict[str, Any]) -> None:
    """Keeps prose capitalization consistent without rewriting command labels."""

    for content in topic_commands["rendered"].values():
        page = _parse_generated_page(content)
        for label in page.findall(".//m:gui", _NS):
            label.text = ""
        assert "preferences window" not in " ".join("".join(page.itertext()).split())


@pytest.mark.parametrize("categories", (("unknown",), ("sleep-mode", "sleep-mode")))
def test_invalid_feature_preference_placements(
    generator: dict[str, Any], topic_commands: dict[str, Any], categories: tuple[str, ...]
) -> None:
    """Rejects unknown and repeated settings placements instead of dropping or duplicating them."""

    feature = generator["FeaturePageDoc"](
        page_id="features_test",
        title="Test",
        link_title="Test",
        description="Test",
        guide_xref="index",
        sections=(generator["FeatureSectionDoc"]("Test", preference_categories=categories),),
    )
    with pytest.raises(ValueError, match=r"feature preference (category|panel)"):
        generator["_preference_target_registry"](topic_commands["preferences"], [feature], {})


def test_every_settings_panel_has_one_feature_topic(
    generator: dict[str, Any], topic_commands: dict[str, Any]
) -> None:
    """All settings use combined topics, including category overviews and split categories."""

    placements = generator["_feature_preference_placements"](
        topic_commands["pages"], topic_commands["reusable"], topic_commands["preferences"]
    )
    assert set(placements) == {
        panel.panel_id for page in topic_commands["preferences"] for panel in page.panels
    }
    assert {name for name in topic_commands["all_rendered"] if name.startswith("preferences_")} == {
        "preferences_guide.page"
    }
    for destination in placements.values():
        page_id, _, anchor = destination.partition("#")
        root = _parse_generated_page(topic_commands["all_rendered"][f"{page_id}.page"])
        if anchor:
            settings = root.find(f".//m:section[@id='{anchor}']", _NS)
            assert settings is not None
            assert settings.find("m:info", _NS) is None
    for category in ("speech", "documents"):
        assert topic_commands["targets"][f"preferences.{category}"] != (
            topic_commands["targets"][f"preferences.{category}.tables"]
            if category == "speech"
            else topic_commands["targets"]["documents.caret-navigation"]
        )


def test_unplaced_settings_fail_generation(
    generator: dict[str, Any], topic_commands: dict[str, Any]
) -> None:
    """A new or accidentally disconnected category cannot silently regain a separate page."""

    pages = [
        replace(page, sections=()) if page.page_id == "features_sleep_mode" else page
        for page in topic_commands["pages"]
    ]
    with pytest.raises(ValueError, match="Preference panels without a feature topic"):
        generator["_preference_target_registry"](
            topic_commands["preferences"], pages, topic_commands["reusable"]
        )


def test_embedded_settings_keep_native_guide_links(
    topic_commands: dict[str, Any], tmp_path: Path
) -> None:
    """Yelp includes the category description in its ordered, focusable topic link."""

    executable = shutil.which("yelp-build")
    if executable is None:
        pytest.skip("HTML rendering requires yelp-build")
    source = tmp_path / "source"
    output = tmp_path / "html"
    source.mkdir()
    output.mkdir()
    for name, content in topic_commands["all_rendered"].items():
        (source / name).write_text(content)
    result = subprocess.run(
        [executable, "html", "--ignore", "-o", str(output), str(source)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    content = (output / "preferences_guide.html").read_text()
    link = re.search(
        r'<a[^>]+href="features_sleep_mode.html"[^>]*>(.*?)</a>',
        content,
        re.DOTALL,
    )
    assert link is not None
    assert "Configure which" in link.group(1)
    assert content.index('href="features_profiles.html"') < link.start()
    assert link.end() < content.index('href="features_speech_and_voices_guide.html"')
    assert 'href="preferences_sleep_mode.html"' not in content
    sleep_mode = (output / "features_sleep_mode.html").read_text()
    assert sleep_mode.count("More Information") == 1
    assert sleep_mode.index("More Information") > sleep_mode.index('id="commands-sleep-mode"')


def test_generated_xml_and_targets(
    generator: dict[str, Any], topic_commands: dict[str, Any]
) -> None:
    """Rejects empty headings and dangling links, including section fragments."""

    generator["validate_generated_pages"](topic_commands["all_rendered"])
    for name, content in topic_commands["all_rendered"].items():
        assert (_HELP_DIR / name).read_text() == content


def test_guide_names_and_topic_names(topic_commands: dict[str, Any]) -> None:
    """Guide names identify their page type without renaming their child topics."""

    guides = set()
    for filename, content in topic_commands["all_rendered"].items():
        root = _parse_generated_page(content)
        if root.get("type") == "guide":
            assert filename == "index.page" or filename.endswith("_guide.page")
            guides.add(filename)
        else:
            assert not filename.endswith("_guide.page")
        assert root.get("id") == filename.removesuffix(".page")
    assert guides == {
        "index.page",
        "preferences_guide.page",
        "features_braille_guide.page",
        "features_speech_and_voices_guide.page",
        "features_reading_documents_guide.page",
    }
    for old in (
        "preferences",
        "features_braille",
        "features_speech_and_voices",
        "features_reading_documents",
    ):
        assert not (_HELP_DIR / f"{old}.page").exists()
    assert "features_braille_output.page" in topic_commands["all_rendered"]
    assert "features_speech_and_voices_output.page" in topic_commands["all_rendered"]


def test_guide_name_validation(generator: dict[str, Any]) -> None:
    """New guide definitions must follow the naming convention too."""

    with pytest.raises(ValueError, match="Guide page id must end in _guide"):
        generator["validate_generated_pages"](
            {
                "example.page": f'<page xmlns="{_NS["m"]}" type="guide" id="example">'
                "<title>Example</title></page>"
            }
        )


def test_mallard_schema(topic_commands: dict[str, Any], tmp_path: Path) -> None:
    """Checks the actual Mallard grammar when the XML toolchain is installed."""

    executable = shutil.which("xmllint")
    schema = Path("/usr/share/xml/mallard/1.1/mallard-1.1.rng")
    if executable is None or not schema.exists():
        pytest.skip("Mallard schema validation requires xmllint and mallard-rng")
    paths = []
    for name, content in topic_commands["all_rendered"].items():
        path = tmp_path / name
        path.write_text(content)
        paths.append(str(path))
    result = subprocess.run(
        [executable, "--noout", "--relaxng", str(schema), *paths],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_unknown_link_is_an_error(generator: dict[str, Any]) -> None:
    """A mistyped logical target must not become a visible broken link."""

    link = generator["FeatureLinkDoc"]("speech.voice-setz")
    with pytest.raises(ValueError, match="Unknown help link target"):
        generator["_add_feature_links"](ET.Element("test"), (link,), {}, {}, "See also:")


def test_preference_links_have_one_qualifier(topic_commands: dict[str, Any]) -> None:
    """Link labels remain meaningful without repeated preference qualifiers."""

    for content in topic_commands["all_rendered"].values():
        page = _parse_generated_page(content)
        for link in page.findall(".//m:link", _NS):
            assert not re.search(
                r"\bpreferences\s+preferences\b", "".join(link.itertext()), re.IGNORECASE
            )


def test_math_marker_section_has_only_numbered_markers(topic_commands: dict[str, Any]) -> None:
    """Reading and describing an expression must not be classified as marker commands."""

    group = next(
        group
        for _page, group in topic_commands["groups"]
        if group.title.casefold() == "math navigation"
    )
    marker_section = next(section for section in group.sections if section.title == "Place markers")
    assert len(marker_section.command_names) == 40
    assert all(
        re.fullmatch(r"math_(moveto|setplacemarker|read|describe)_\d", name)
        for name in marker_section.command_names
    )
    assert "math_read_current" not in marker_section.command_names


@pytest.mark.parametrize("section_count", (0, 2))
def test_ambiguous_or_unplaced_commands_are_errors(
    generator: dict[str, Any],
    section_count: int,
) -> None:
    """A sectioned command group must assign each command exactly once."""

    section_type = generator["CommandSectionDoc"]
    sections = (
        (section_type("Other", command_names=("other",)),)
        if section_count == 0
        else (
            section_type("First", command_prefixes=("test",)),
            section_type("Second", command_prefixes=("test",)),
        )
    )
    group = generator["CollectedCommandGroupDoc"](title="Test", sections=sections)
    command = generator["CollectedCommandDoc"](name="test_command", label="Test command")
    with pytest.raises(ValueError, match=f"matches {section_count} command sections"):
        generator["_add_feature_command_group"](ET.Element("test"), group, [command])


def test_block_after_section_is_invalid(generator: dict[str, Any]) -> None:
    """Core structure checks run even without the optional external schema tools."""

    content = (
        '<page xmlns="http://projectmallard.org/1.0/" id="test" type="topic">'
        '<title>Test</title><section id="part"><title>Part</title></section>'
        "<p>Misplaced content</p></page>"
    )
    with pytest.raises(ValueError, match="Block content follows a section"):
        generator["validate_generated_pages"]({"test.page": content})


def test_help_registry_owners_cannot_collide(generator: dict[str, Any]) -> None:
    """A second owner cannot silently replace another feature's destination."""

    with pytest.raises(ValueError, match="multiple owners"):
        generator["_merge_registries"]({"feature.target": "first"}, {"feature.target": "second"})


def test_feature_links_require_logical_targets(generator: dict[str, Any]) -> None:
    """Even a registered page filename is not an author-facing logical target."""

    target = "preferences_speech"
    with pytest.raises(ValueError, match="logical help target"):
        generator["_add_feature_links"](
            ET.Element("test"),
            (generator["FeatureLinkDoc"](target),),
            {target: target},
            {target: generator["LinkTextDoc"]("Speech")},
            "See also:",
        )


def test_orca_shortcuts_in_prose_have_command_references(
    generator: dict[str, Any],
    topic_commands: dict[str, Any],
) -> None:
    """New Orca shortcut literals must track their owning command definitions."""

    for page in topic_commands["pages"]:
        assert "Orca Modifier+" not in page.intro + page.details
        sections = generator["_resolve_feature_sections"](page, topic_commands["reusable"])
        for section in sections:
            references = {shortcut.text for shortcut in section.shortcuts}
            for match in generator["_KEY_SEQUENCE_PATTERN"].finditer(
                section.intro + section.details
            ):
                if match.group(0).startswith("Orca Modifier+"):
                    assert match.group(0) in references, (section.title, match.group(0))


def test_learn_mode_explanation_precedes_commands(topic_commands: dict[str, Any]) -> None:
    """Learn Mode explains presentation and its special keys before listing commands."""

    page = _parse_generated_page(topic_commands["rendered"]["features_learn_mode.page"])
    paragraphs = " ".join("".join(p.itertext()) for p in page.findall("m:p", _NS))
    assert "in speech and braille" in paragraphs
    assert "hear" not in paragraphs
    assert {key.text for key in page.findall("m:p//m:key", _NS)} >= {"F1", "F2", "Escape"}
    assert page.find("m:section[@id='commands-learn-mode']", _NS) is not None


def test_commands_sections_do_not_contain_feature_narrative(topic_commands: dict[str, Any]) -> None:
    """Feature explanations cannot drift below Settings into a Commands section."""

    checked = 0
    for filename, content in topic_commands["rendered"].items():
        page = _parse_generated_page(content)
        for section in page.findall(".//m:section", _NS):
            section_id = section.get("id", "")
            if section_id != "commands" and not section_id.startswith("commands-"):
                continue
            checked += 1
            for container in (section, *section.findall(".//m:section", _NS)):
                for paragraph in container.findall("m:p", _NS):
                    assert paragraph.findtext("m:em[@style='strong']", namespaces=_NS) == (
                        "Preferences location:"
                    ), (filename, section_id, "".join(paragraph.itertext()))
    assert checked > 0


@pytest.mark.parametrize("class_name", ("CommandGroupDoc", "CommandSectionDoc"))
def test_command_groups_reject_feature_details(generator: dict[str, Any], class_name: str) -> None:
    """New feature prose must use feature metadata rather than command-group details."""

    metadata_class = getattr(generator["_HELP_METADATA"], class_name)
    with pytest.raises(TypeError, match="details"):
        metadata_class(title="Test", details="Feature explanation")


def test_each_command_list_has_a_commands_heading(topic_commands: dict[str, Any]) -> None:
    """Named subsets and multiple groups are discoverable beneath a Commands heading."""

    labels = {
        command.label for _page, group in topic_commands["groups"] for command in group.commands
    }
    for filename, content in topic_commands["rendered"].items():
        page = _parse_generated_page(content)
        parents = {child: parent for parent in page.iter() for child in parent}
        for label in page.findall(".//m:item/m:p/m:gui", _NS):
            if label.text not in labels:
                continue
            ancestor = parents[label]
            while ancestor is not page:
                if ancestor.findtext("m:title", namespaces=_NS) == "Commands":
                    break
                ancestor = parents[ancestor]
            else:
                pytest.fail(f"{filename}: command {label.text!r} lacks a Commands heading")


def test_related_links_have_a_neutral_preface(topic_commands: dict[str, Any]) -> None:
    """Topic links are not mislabeled as commands or split into duplicate lists."""

    for content in topic_commands["rendered"].values():
        assert "Commands and preferences:" not in content
        assert "Preferences and related topics" not in content
        page = _parse_generated_page(content)
        for section in page.findall(".//m:section", _NS):
            if not section.get("id", "").endswith("-related"):
                continue
            destinations = [link.get("xref") for link in section.findall(".//m:link", _NS)]
            assert len(destinations) == len(set(destinations))


def test_progress_bar_settings_use_consistent_explanations(topic_commands: dict[str, Any]) -> None:
    """Equivalent controls use the same definitions, including the zero interval."""

    explanations = []
    for filename in (
        "features_speech_and_voices_progress_bars.page",
        "features_braille_progress_bars.page",
        "features_sound.page",
    ):
        page = _parse_generated_page(topic_commands["rendered"][filename])
        frequency = page.find(".//m:p[m:gui='Frequency (secs):']", _NS)
        assert frequency is not None
        text = " ".join("".join(frequency.itertext()).split()).split("Default:")[0]
        assert "Zero removes this minimum delay." in text
        explanations.append(text)
    assert len(set(explanations)) == 1


def test_table_speech_commands_belong_with_table_speech_settings(
    topic_commands: dict[str, Any],
) -> None:
    """The row/cell toggle is not stranded among general verbosity commands."""

    target = topic_commands["targets"]["command:keyboard:toggleTableCellReadModeHandler"]
    assert target.startswith("features_speech_and_voices_tables#")


@pytest.mark.parametrize("topic", ("verbosity", "voice_sets", "global_voice_settings"))
def test_speech_command_subgroups_share_their_location(
    topic_commands: dict[str, Any], topic: str
) -> None:
    """One Commands group path is sufficient when all subgroups share it."""

    page = _parse_generated_page(
        topic_commands["rendered"][f"features_speech_and_voices_{topic}.page"]
    )
    commands = page.find("m:section[m:title='Commands']", _NS)
    assert commands is not None
    locations = commands.findall(".//m:p/m:em[@style='strong']", _NS)
    assert [label.text for label in locations] == ["Preferences location:"]


def test_progress_links_identify_their_output_type(topic_commands: dict[str, Any]) -> None:
    """Links to speech and braille progress-bar topics remain distinguishable out of context."""

    page = _parse_generated_page(topic_commands["rendered"]["features_sound.page"])
    labels = [link.text for link in page.findall(".//m:link", _NS)]
    assert "Speech progress bars" in labels
    assert "Braille progress bars" in labels


def test_settings_omit_generic_introductions(topic_commands: dict[str, Any]) -> None:
    """Settings sections do not repeat that settings control their own feature."""

    for filename, content in topic_commands["all_rendered"].items():
        page = _parse_generated_page(content)
        for paragraph in page.findall(".//m:section[m:title='Settings']/m:p", _NS):
            text = " ".join("".join(paragraph.itertext()).split())
            assert re.search(r"\bsettings (?:control|let you)\b", text) is None, (filename, text)


@pytest.mark.parametrize(
    ("filename", "detail"),
    (
        ("features_sound.page", "~/.local/share/orca/sounds"),
        (
            "features_speech_and_voices_tables.page",
            "speaking the full row can provide useful context",
        ),
        ("features_spell_check.page", "Orca needs to identify the misspelled word"),
    ),
)
def test_feature_details_are_outside_settings(
    topic_commands: dict[str, Any], filename: str, detail: str
) -> None:
    """Feature behavior remains documented before its settings, without duplication."""

    page = _parse_generated_page(topic_commands["rendered"][filename])
    paragraphs = page.findall("m:p", _NS)
    text = " ".join(" ".join("".join(p.itertext()).split()) for p in paragraphs)
    assert detail in text
    settings = page.find("m:section[m:title='Settings']", _NS)
    assert settings is not None
    assert detail not in " ".join("".join(settings.itertext()).split())


def test_settings_keep_configuration_instructions(topic_commands: dict[str, Any]) -> None:
    """Useful configuration guidance stays alongside the controls it describes."""

    for filename, instruction in (
        ("features_keyboard_layout.page", "To bind or change a command shortcut"),
        ("features_speech_and_voices_tables.page", "configure row presentation separately"),
    ):
        page = _parse_generated_page(topic_commands["rendered"][filename])
        settings = page.find("m:section[m:title='Settings']", _NS)
        assert settings is not None
        assert instruction in " ".join("".join(settings.itertext()).split())


def test_mouse_review_has_one_platform_caveat(topic_commands: dict[str, Any]) -> None:
    """A single overview caveat covers Mouse review and its pointer-related commands."""

    page = _parse_generated_page(
        topic_commands["rendered"]["features_reviewing_objects_mouse_review.page"]
    )
    assert "".join(page.itertext()).count("Wayland") == 1


def test_math_start_instruction_uses_its_command_shortcut(topic_commands: dict[str, Any]) -> None:
    """The verb for entering math navigation cannot be mistaken for the Enter key."""

    page = _parse_generated_page(topic_commands["rendered"]["features_math_navigation.page"])
    keys = [key.text for key in page.findall("m:p//m:key", _NS)]
    assert "Enter" not in keys
    assert ["Orca Modifier", "Alt", "M"] in [
        [key.text for key in sequence.findall("m:key", _NS)]
        for sequence in page.findall("m:p/m:keyseq", _NS)
    ]


def test_metadata_schema_is_shared(generator: dict[str, Any]) -> None:
    """Collection and providers use exactly the same public schema."""

    public = generator["_HELP_METADATA"]
    assert generator["FeatureSectionDoc"] is public.FeatureSectionDoc
    assert generator["CommandSectionDoc"] is public.CommandSectionDoc
    call = ast.parse('PreferenceControlDoc("Test", "switch")', mode="eval").body
    assert generator["_find_keyword"](call, "label").value == "Test"
    bad = ast.parse('PreferenceControlDoc(label="Test", typo=True)', mode="eval").body
    with pytest.raises(ValueError, match="Unknown PreferenceControlDoc fields"):
        generator["_find_keyword"](bad, "kind")


@pytest.mark.parametrize("field", ("description", "summary"))
def test_ambiguous_panel_fields_are_rejected(generator: dict[str, Any], field: str) -> None:
    """Contributors must choose instructions or link text rather than an ambiguous field."""

    with pytest.raises(TypeError):
        generator["_HELP_METADATA"].PreferencePanelDoc("Test", **{field: "Old text"})
    call = ast.parse(f'PreferencePanelDoc(title="Test", {field}="Old text")', mode="eval").body
    with pytest.raises(ValueError, match="Unknown PreferencePanelDoc fields"):
        generator["_find_keyword"](call, "title")


def test_panel_instructions_and_link_summary_are_independent(generator: dict[str, Any]) -> None:
    """Settings and links each use their explicit text, without cross-field fallbacks."""

    source = """
class TestGrid(PreferencesGridBase):
    @classmethod
    def get_documentation(cls):
        return PreferencePanelDoc(
            title="Test", panel_id="test.panel", target="test.settings",
            instructions="Activate a row to configure it.",
            link_summary="Configure test settings.",
            controls=(PreferenceControlDoc(label="Enabled", kind="switch"),),
        )
"""
    panel = generator["_extract_protocol_panel"](
        ast.parse(source).body[0], generator["SourceEvaluator"]({}, {}, {}), {}, "test.py"
    )
    assert panel.instructions == "Activate a row to configure it."
    assert panel.link_summary == "Configure test settings."
    for instructions, summary in (
        (panel.instructions, panel.link_summary),
        (panel.instructions, ""),
        ("", panel.link_summary),
    ):
        current = replace(panel, instructions=instructions, link_summary=summary)
        page = generator["PageDoc"](
            "preferences_test",
            "preferences_test.page",
            "Test",
            "Test",
            "Test",
            "Category overview",
            [current],
        )
        links = generator["_preference_link_text_registry"]([page])
        assert links["test.settings"].summary == summary
        parent = ET.Element("test")
        generator["_add_panel_contents"](parent, current)
        text = " ".join(parent.itertext())
        assert (panel.instructions in text) == bool(instructions)
        assert panel.link_summary not in text


def test_unlisted_preferences_are_an_error(generator: dict[str, Any]) -> None:
    """New panels cannot be silently dropped from the preferences directory."""

    panel = generator["PanelDoc"](panel_id="new.panel", title="New", schema="")
    with pytest.raises(ValueError, match="inventory mismatch"):
        generator["_page_docs_from_groups"]([panel], {"preference_order": []})


def test_preference_categories_come_from_providers(topic_commands: dict[str, Any]) -> None:
    """Category explanations and membership are not duplicated in the central index."""

    metadata = json.loads(_METADATA_PATH.read_text())
    assert "groups" not in metadata
    pages = topic_commands["preferences"]
    assert [page.page_id for page in pages] == [
        f"preferences_{category.replace('-', '_')}" for category in metadata["preference_order"]
    ]
    for page in pages:
        owners = [panel for panel in page.panels if panel.category is not None]
        assert len(owners) == 1
        category = owners[0].category
        assert page.description == category.description
        assert [panel.panel_id for panel in page.panels] == list(category.panels)
    descriptions = {page.page_id: page.description for page in pages}
    assert "named collections" in descriptions["preferences_profiles"]
    assert "without moving focus or the caret" in descriptions["preferences_flat_review"]


@pytest.mark.parametrize(
    "arguments",
    (
        'category_id="test", title="Test", description="", panels=("test.panel",)',
        'category_id="test", title="Test", description="Test settings", panels=()',
        (
            'category_id="test", title="Test", description="Test settings", '
            'panels=("test.panel",), application_preferences="yes"'
        ),
        (
            'category_id="test", title="Test", description="Test settings", '
            'panels=("test.panel",), typo=True'
        ),
    ),
)
def test_invalid_preference_category_is_an_error(generator: dict[str, Any], arguments: str) -> None:
    """Rejects missing descriptions and malformed category metadata during collection."""

    node = ast.parse(f"PreferenceCategoryDoc({arguments})", mode="eval").body
    evaluator = generator["SourceEvaluator"]({}, {}, {})
    with pytest.raises(ValueError):
        generator["_extract_category_doc"](node, evaluator)


@pytest.mark.parametrize("panels", (("test.panel", "test.panel"), ("test.panel", "unknown")))
def test_preference_category_panel_inventory(
    generator: dict[str, Any], panels: tuple[str, ...]
) -> None:
    """Rejects repeated and nonexistent panel memberships."""

    category = generator["PreferenceCategoryDoc"]("test", "Test", "Test settings", panels)
    panel = generator["PanelDoc"]("test.panel", "Test", "", category=category)
    with pytest.raises(ValueError, match=r"more than once|inventory mismatch"):
        generator["_page_docs_from_groups"]([panel], {"preference_order": ["test"]})


def test_application_availability_matches_window(topic_commands: dict[str, Any]) -> None:
    """Checks documented exclusions against the window's global-only sidebar entries."""

    tree = ast.parse((_ROOT / "src/orca/preferences_window.py").read_text())
    excluded = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.If) or ast.unparse(node.test) != "not self._app_name":
            continue
        for statement in node.body:
            for call in ast.walk(statement):
                if (
                    isinstance(call, ast.Call)
                    and isinstance(call.func, ast.Attribute)
                    and call.func.attr == "_add_navigation_row"
                ):
                    excluded.add(ast.literal_eval(call.args[0]))
    documented = {
        panel.category.category_id.replace("-", "_")
        for page in topic_commands["preferences"]
        for panel in page.panels
        if panel.category and not panel.category.application_preferences
    }
    assert documented == excluded
    profile_page = topic_commands["all_rendered"]["features_profiles.page"]
    assert "read-only" not in profile_page
    assert "select an existing profile" in profile_page


@pytest.mark.parametrize("change", ("missing", "unknown", "duplicate"))
def test_preference_category_order_inventory(
    generator: dict[str, Any], topic_commands: dict[str, Any], change: str
) -> None:
    """New or removed categories require an explicit display-order decision."""

    panels = [panel for page in topic_commands["preferences"] for panel in page.panels]
    metadata = json.loads(_METADATA_PATH.read_text())
    if change == "missing":
        metadata["preference_order"].pop()
    elif change == "unknown":
        metadata["preference_order"].append("unknown")
    else:
        metadata["preference_order"].append(metadata["preference_order"][0])
    with pytest.raises(ValueError, match=r"(?i)category"):
        generator["_page_docs_from_groups"](panels, metadata)


def test_preference_command_references(topic_commands: dict[str, Any]) -> None:
    """Links preferences directly to commands without copying command lists."""

    links = topic_commands["associations"].by_panel["flat_review_presenter.flat-review"]
    assert links == (
        ("features_reviewing_objects_flat_review#commands-flat-review", "Flat review commands"),
    )
    for page in topic_commands["preferences"]:
        for panel in page.panels:
            if not panel.command_groups and not panel.command_names:
                assert not topic_commands["associations"].by_panel[panel.panel_id]


def test_reciprocal_preference_references(topic_commands: dict[str, Any]) -> None:
    """Every associated command topic links back to its related preferences."""

    for command, links in topic_commands["associations"].by_command.items():
        filename = topic_commands["targets"][command].split("#", 1)[0] + ".page"
        page = _parse_generated_page(topic_commands["all_rendered"][filename])
        destinations = {link.get("xref") for link in page.findall(".//m:link", _NS)}
        assert {
            destination
            for destination, _label in links
            if destination.split("#", 1)[0] + ".page" != filename
        } <= destinations


def test_preference_pages_omit_ui_subcategory_navigation(topic_commands: dict[str, Any]) -> None:
    """Settings sections replace UI-only page selectors and repeated navigation instructions."""

    for page_doc in topic_commands["preferences"]:
        destination = topic_commands["targets"][page_doc.page_id].split("#", 1)[0]
        page = _parse_generated_page(topic_commands["all_rendered"][destination + ".page"])
        for link in page.findall(".//m:link", _NS):
            assert not link.get("xref", "").startswith(f"{page_doc.page_id}#")
        text = "".join(page.itertext())
        assert "Activate a row, or press" not in text
        for list_el in page.findall(".//m:list", _NS):
            assert list_el.find("m:item", _NS) is not None
    documents = _parse_generated_page(
        topic_commands["all_rendered"]["features_reading_documents_guide.page"]
    )
    assert documents.find("m:list", _NS) is None


def test_group_association_omits_commands_documented_elsewhere(
    topic_commands: dict[str, Any],
) -> None:
    """Structural preferences link to structural commands, not relocated live-region commands."""

    links = topic_commands["associations"].by_panel["document_presenter.structural-navigation"]
    assert [destination for destination, _label in links] == [
        "features_reading_documents_structural_navigation#commands-structural-navigation"
    ]
    for name in ("previous_live_region", "next_live_region", "last_live_region"):
        assert topic_commands["targets"][f"command:keyboard:{name}"] == (
            "features_reading_documents_live_regions"
        )
        assert f"command:keyboard:{name}" not in topic_commands["associations"].by_command


@pytest.mark.parametrize("field", ("command_groups", "command_names"))
def test_unknown_preference_command_is_an_error(
    generator: dict[str, Any], topic_commands: dict[str, Any], field: str
) -> None:
    """Stale associations cannot silently disappear when a command is removed."""

    panel = generator["PanelDoc"](panel_id="test", title="Test", schema="", **{field: ("unknown",)})
    page = generator["PageDoc"]("test", "test.page", "Test", "Test", "Test", "Test", [panel])
    with pytest.raises(ValueError, match="Unknown preference command"):
        generator["_preference_command_links"](
            [page], topic_commands["groups"], topic_commands["targets"], topic_commands["link_text"]
        )


def test_wrap_preserves_hyphenated_words(generator: dict[str, Any]) -> None:
    """Line wrapping must not insert spaces into words or protocol names."""

    page = ET.Element("test")
    generator["_add_text_paragraphs"](page, ("Orca-controlled AT-SPI user-interface " * 20).strip())
    result = generator["_serialize"](ET.ElementTree(page))
    text = " ".join("".join(_parse_generated_page(result).itertext()).split())
    assert text == ("Orca-controlled AT-SPI user-interface " * 20).strip()


def test_settings_inventory(generator: dict[str, Any]) -> None:
    """New schema keys require documentation or an explicit coverage decision."""

    exceptions = {
        ("caret-navigation", "selection-enabled"): "Hidden, disabled selection feature",
        ("extensions", "approved-user-extensions"): "Approval editor, not a direct preference",
        ("extensions", "disabled-extensions"): "Extension switches",
        ("extensions", "settings"): "Extension-owned dynamic settings",
        ("keybindings", "desktop-modifier-keys"): "Separate modifier switches",
        ("keybindings", "laptop-modifier-keys"): "Separate modifier switches",
        ("keybindings", "entries"): "Command shortcut editor",
        ("live-regions", "enabled"): "Command-controlled, no preferences control",
        ("live-regions", "present-from-inactive-tab"): "No preferences control",
        ("metadata", "display-name"): "Internal profile metadata",
        ("metadata", "internal-name"): "Internal profile metadata",
        ("pronunciations", "entries"): "Pronunciation dictionary editor",
        ("speech", "repeated-character-limit"): "No preferences control",
        ("speech", "speech-server-factory"): "Speech system chooser",
        ("text-attributes", "attributes-to-braille"): "Attribute list editor",
        ("text-attributes", "attributes-to-speak"): "Attribute list editor",
        ("voice", "established"): "Internal customization flag",
        ("voice", "family-dialect"): "Dynamic voice chooser",
        ("voice", "family-gender"): "Dynamic voice chooser",
        ("voice", "family-lang"): "Dynamic voice chooser",
        ("voice", "family-variant"): "Dynamic voice chooser",
    }
    panels = generator["collect_preference_panels"](_ROOT / "src")
    controls = [control for panel in panels for control in panel.controls]
    documented = set()
    while controls:
        control = controls.pop()
        if control.schema and control.key:
            documented.add((control.schema, control.key))
        controls.extend(control.controls)
    settings = generator["_collect_settings"](_ROOT / "src")
    assert settings.keys() - documented == exceptions.keys()


def test_source_discovery_covers_command_factories() -> None:
    """New command constructors cannot hide outside the collected definition files."""

    for path in (_ROOT / "src/orca").rglob("*.py"):
        tree = ast.parse(path.read_text())
        extension_factory_calls = {
            id(item)
            for method in ast.walk(tree)
            if path.name == "command_manager.py"
            and isinstance(method, ast.FunctionDef)
            and method.name == "register_command"
            for item in ast.walk(method)
            if isinstance(item, ast.Call)
        }
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if id(node) in extension_factory_calls:
                continue
            name = (
                node.func.id
                if isinstance(node.func, ast.Name)
                else (node.func.attr if isinstance(node.func, ast.Attribute) else "")
            )
            if name in {"KeyboardCommand", "BrailleCommand"}:
                assert path.parent == _ROOT / "src/orca", str(path)
                assert path.name.endswith("_command_definitions.py"), str(path)


def test_internal_features_have_documentation(topic_commands: dict[str, Any]) -> None:
    """Internal extensions have a feature topic or an explicitly consolidated preferences page."""

    shared_owners = {
        "flat_review_finder": "flat_review_presenter",
        "speech_presenter": "speech_manager",
        "math_presenter": "math_navigator",
    }
    source = _ROOT / "src/orca"
    preference_owners = {
        Path(panel.source_file).stem.removesuffix("_preferences_grid")
        for page in topic_commands["preferences"]
        for panel in page.panels
        if panel.category and panel.category.target
    }
    for path in source.glob("*.py"):
        tree = ast.parse(path.read_text())
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            if not any(
                isinstance(base, ast.Name) and base.id == "Extension" for base in node.bases
            ):
                continue
            owner = shared_owners.get(path.stem, path.stem)
            assert (
                source / f"{owner}_feature_documentation.py"
            ).exists() or owner in preference_owners, str(path)


@pytest.mark.parametrize("field", ("details", "after_commands"))
def test_prose_shortcut_tracks_binding_changes(generator: dict[str, Any], field: str) -> None:
    """A changed default updates inline prose, not just command lists."""

    shortcut = generator["_HELP_METADATA"].CommandShortcutDoc("Orca Modifier+F12", "toggle")
    section = generator["FeatureSectionDoc"](
        title="Test", shortcuts=(shortcut,), **{field: "Press Orca Modifier+F12."}
    )
    binding = generator["KeyBindingDoc"](
        "F11", generator["_FAKE_KEYBINDING_CONSTANTS"]["ORCA_MODIFIER_MASK"]
    )
    command = generator["CollectedCommandDoc"](
        name="toggle", desktop_keybinding=binding, laptop_keybinding=binding
    )
    assert generator["_feature_prose"](getattr(section, field), section, {"toggle": command}) == (
        "Press Orca Modifier+F11."
    )


def test_ui_renames_update_generated_explanations(
    generator: dict[str, Any], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Changing only UI constants updates prose, settings, commands, and link labels."""

    source = tmp_path / "src"
    shutil.copytree(
        _ROOT / "src/orca", source / "orca", ignore=shutil.ignore_patterns("__pycache__")
    )
    renames = (
        ("guilabels.py", '_("Global Voice Settings")', '_("Global Speech Settings")'),
        (
            "guilabels.py",
            '\nVOICE_SET_GLOBAL = C_("VoiceSet", "Global")',
            '\nVOICE_SET_GLOBAL = C_("VoiceSet", "Shared")',
        ),
        (
            "guilabels.py",
            '_("Screen Reader Modifier Keys")',
            '_("Screen Reader Modifier Buttons")',
        ),
        (
            "cmdnames.py",
            '_("Set default live region politeness level to off")',
            '_("Toggle announcements for this page")',
        ),
    )
    for filename, old, new in renames:
        path = source / "orca" / filename
        text = path.read_text()
        assert text.count(old) == 1
        path.write_text(text.replace(old, new))

    output = tmp_path / "help"
    monkeypatch.setattr(
        "sys.argv", [str(_SCRIPT), "--src-dir", str(source), "--output-dir", str(output)]
    )
    assert generator["main"]() == 0

    speech = _parse_generated_page(
        (output / "features_speech_and_voices_global_voice_settings.page").read_text()
    )
    prose = " ".join("".join(p.itertext()) for p in speech.findall("m:p", _NS))
    assert "Use Global Speech Settings preferences" in prose
    assert "Shared voice set holds" in prose
    assert speech.find("m:title", _NS).text == "Global speech settings"
    assert "Global Voice Settings" not in "".join(speech.itertext())
    assert "Global Speech Settings" in [gui.text for gui in speech.findall(".//m:gui", _NS)]

    language = (output / "features_speech_and_voices_language_switching.page").read_text()
    assert "Global Speech Settings preferences" in language
    assert "The Shared voice set normally applies" in language
    assert "Global Voice Settings" not in language

    voices = " ".join(
        "".join(
            _parse_generated_page(
                (output / "features_speech_and_voices_voice_sets.page").read_text()
            ).itertext()
        ).split()
    )
    assert "Lists the Shared voice set" in voices
    assert "Global Voice Settings" not in voices

    keyboard = (output / "features_keyboard_layout.page").read_text()
    assert "Screen Reader Modifier Buttons is" in keyboard
    assert "Screen Reader Modifier Keys" not in keyboard

    live_regions = _parse_generated_page(
        (output / "features_reading_documents_live_regions.page").read_text()
    )
    prose = " ".join("".join(p.itertext()) for p in live_regions.findall("m:p", _NS))
    assert "Toggle announcements for this page turns announcements" in prose
    assert "Toggle announcements for this page" in [
        gui.text for gui in live_regions.findall(".//m:gui", _NS)
    ]
    assert "Set default live region politeness level to off" not in "".join(live_regions.itertext())


def test_feature_ui_names_are_not_translated(
    generator: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Generation uses English source strings, never the runtime gettext translations."""

    def unexpected_translation(*_args: Any, **_kwargs: Any) -> Any:
        pytest.fail("Documentation generation must not call gettext")

    monkeypatch.setenv("LANGUAGE", "fr_FR")
    monkeypatch.setenv("LC_MESSAGES", "fr_FR.UTF-8")
    for name in ("gettext", "dgettext", "pgettext", "translation"):
        monkeypatch.setattr(gettext, name, unexpected_translation)
    pages, sections = generator["collect_feature_documentation"](_ROOT / "src")
    speech = next(page for page in pages if page.page_id == "features_speech_and_voices_guide")
    assert "Use Global Voice Settings preferences" in speech.sections[1].intro
    assert (
        "Set default live region politeness level to off"
        in sections["documents.live-regions.feature"].details
    )


@pytest.mark.parametrize(
    ("module", "name"),
    (("guilabels", "VOICE_GLOBAL_VOICE_SETTINGS"), ("cmdnames", "TOGGLE_SPEECH")),
)
def test_removed_prose_ui_name_fails_collection(
    generator: dict[str, Any], module: str, name: str
) -> None:
    """A removed source constant cannot leave a stale label in feature explanations."""

    source = _ROOT / "src"
    labels = generator["_collect_labels"](source)
    commands = generator["_collect_command_names"](source)
    del (labels if module == "guilabels" else commands)[name]
    with pytest.raises(AttributeError, match=name):
        generator["_execute_feature_documentation_module"](
            source / "orca/speech_manager_feature_documentation.py",
            labels,
            commands,
        )


@pytest.mark.parametrize(
    "expression", ("guilabels.MISSING_LABEL", 'f"Use {guilabels.MISSING_LABEL}."')
)
def test_unresolved_preference_prose_is_an_error(
    generator: dict[str, Any], expression: str
) -> None:
    """Missing label references cannot silently erase a settings description."""

    evaluator = generator["SourceEvaluator"]({}, {}, {})
    with pytest.raises(ValueError, match="Cannot resolve documentation text"):
        evaluator.text(ast.parse(expression, mode="eval").body)


def test_command_names_are_not_copied_into_feature_prose(generator: dict[str, Any]) -> None:
    """Use source constants for command names rather than maintaining a second copy."""

    commands = generator["_collect_command_names"](_ROOT / "src")
    # Short names such as Read and Describe are also ordinary prose.
    names = {label for label in commands.values() if len(label) >= 12}
    for path in (_ROOT / "src/orca").glob("*_feature_documentation.py"):
        for node in ast.walk(ast.parse(path.read_text())):
            if not isinstance(node, ast.keyword) or node.arg not in {
                "intro",
                "details",
                "after_commands",
            }:
                continue
            for part in ast.walk(node.value):
                if not isinstance(part, ast.Constant) or not isinstance(part.value, str):
                    continue
                for name in names:
                    assert name not in part.value, (
                        f"{path}:{part.lineno}: use cmdnames instead of copying {name!r}"
                    )
