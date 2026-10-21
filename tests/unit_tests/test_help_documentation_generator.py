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

"""Tests for help generation, metadata validation, and documentation coverage."""

from __future__ import annotations

import ast
import gettext
import json
import re
import runpy
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import replace
from html import unescape
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


@pytest.fixture(scope="module", name="generator")
def generator_fixture() -> dict[str, Any]:
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
        ('Choose "Delete" or press Delete.', ["Delete"]),
        ('The "Enter and exit flat review mode" command.', []),
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


@pytest.mark.parametrize("title", ("Orca Find", "Find visible text", "Enter & Exit"))
def test_prose_topic_titles_follow_metadata(generator: dict[str, Any], title: str) -> None:
    """Topic references become quoted inline links using the referenced title."""

    topic = generator["FeaturePageDoc"](
        page_id="features_target",
        title=title,
        link_title=title,
        description="Target topic.",
        guide_xref="",
        target="example.topic",
    )
    referring = generator["FeaturePageDoc"](
        page_id="features_referring",
        title="Referring topic",
        link_title="Referring topic",
        description="See [[example.topic]].",
        guide_xref="",
        intro="See [[example.topic]] and [[example.topic]].",
        details=(
            "Press Enter, then see [[example.topic]].\n\n"
            "- See [[example.topic]].\n\nRun `[[literal]]`, then see [[example.topic]]."
        ),
    )
    pages = [topic, referring]
    rendered = generator["build_feature_pages"](
        pages,
        generator["_feature_target_registry"](pages, {}),
        generator["_feature_link_text_registry"](pages, {}),
        {},
        [page.page_id for page in pages],
    )
    root = _parse_generated_page(rendered["features_referring.page"])
    assert root.findtext("m:info/m:desc", namespaces=_NS).strip() == f'See "{title}".'
    assert "".join(root.itertext()).count(f'"{title}"') == 6
    links = root.findall(".//m:link[@xref='features_target']", _NS)
    assert len(links) == 5
    assert all(link.text == title for link in links)
    assert root.find("m:info/m:desc/m:link", _NS) is None
    assert [key.text for key in root.findall(".//m:key", _NS)] == ["Enter"]
    assert root.findtext("m:p/m:code", namespaces=_NS) == "[[literal]]"


@pytest.mark.parametrize("missing_registry", ("targets", "titles"))
def test_missing_prose_topic_is_rejected(generator: dict[str, Any], missing_registry: str) -> None:
    """A removed target or title cannot silently leave a stale prose reference."""

    page = generator["FeaturePageDoc"](
        page_id="features_referring",
        title="Referring topic",
        link_title="Referring topic",
        description="Example.",
        guide_xref="",
        intro="See [[removed.topic]].",
    )
    targets = {} if missing_registry == "targets" else {"removed.topic": "removed"}
    titles = (
        {}
        if missing_registry == "titles"
        else {"removed.topic": generator["LinkTextDoc"]("Old title", "")}
    )
    with pytest.raises(ValueError, match=r"Unknown prose topic target: 'removed\.topic'"):
        generator["build_feature_pages"]([page], targets, titles, {}, [page.page_id])


def test_inline_topic_links_replace_duplicate_related_entries(
    generator: dict[str, Any],
) -> None:
    """Inline destinations have no duplicate related entries or empty navigation sections."""

    page = generator["FeaturePageDoc"](
        page_id="features_test",
        title="Test",
        link_title="Test",
        description="Test",
        guide_xref="",
        sections=(
            generator["FeatureSectionDoc"](
                title="Example",
                intro="See [[example.topic]].",
                links=(generator["FeatureLinkDoc"]("example.topic"),),
            ),
        ),
    )
    rendered = generator["build_feature_pages"](
        [page],
        {"example.topic": "example"},
        {"example.topic": generator["LinkTextDoc"]("Example")},
        {},
        [page.page_id],
    )
    root = _parse_generated_page(rendered["features_test.page"])
    assert len(root.findall(".//m:link[@xref='example']", _NS)) == 1
    assert root.find("m:section/m:p/m:link[@xref='example']", _NS) is not None
    assert root.find(".//m:list", _NS) is None
    assert "See also:" not in "".join(root.itertext())


def test_index_sections_follow_metadata(generator: dict[str, Any]) -> None:
    """Index sections use the identifiers and order declared in metadata."""

    metadata = json.loads(_METADATA_PATH.read_text())
    page = generator["_build_help_index_page"](metadata["index"]).getroot()
    assert page.get("type") == "guide"
    assert page.get("id") == "index"
    sections = page.findall("m:section", _NS)
    assert [section.get("id") for section in sections] == [
        section["id"] for section in metadata["index"]["sections"]
    ]


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


@pytest.fixture(scope="module", name="topic_commands")
def topic_commands_fixture(generator: dict[str, Any]) -> dict[str, Any]:
    """Collects metadata and renders help once for tests using the current source."""

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
def test_invalid_topic_order_is_rejected(
    generator: dict[str, Any], topic_commands: dict[str, Any], change: str
) -> None:
    """Topic order must include every topic exactly once and contain no unknown topics."""

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


def test_topic_order_follows_metadata(
    generator: dict[str, Any], topic_commands: dict[str, Any]
) -> None:
    """Generated sort titles follow the topic order declared in metadata."""

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


def test_every_command_is_rendered_once(topic_commands: dict[str, Any]) -> None:
    """Preserves each logical command and all braille bindings without duplicate listings."""

    expected = Counter(
        {
            (
                topic_commands["targets"][f"command:{command.command_type}:{command.name}"],
                command.name,
            ): command.label
            for _page, group in topic_commands["groups"]
            for command in group.commands
        }.values()
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
    expected_bindings = Counter(
        binding
        for _page, group in topic_commands["groups"]
        for command in group.commands
        for binding in command.braille_bindings
    )
    actual_bindings = Counter(
        binding
        for root in roots
        for paragraph in root.findall(".//m:p", _NS)
        if (text := " ".join("".join(paragraph.itertext()).split())).startswith("Braille: ")
        for binding in text.removeprefix("Braille: ").split(", ")
    )
    assert actual_bindings == expected_bindings


def test_different_commands_with_the_same_label_remain_separate(
    generator: dict[str, Any],
) -> None:
    """Command identity, rather than a shared label, determines whether bindings combine."""

    commands = [
        generator["CollectedCommandDoc"](
            name=kind,
            label="Example",
            command_type=kind,
            braille_bindings=["ROUTE"] if kind == "braille" else [],
        )
        for kind in ("keyboard", "braille")
    ]
    parent = ET.Element("test")
    group = generator["CollectedCommandGroupDoc"](title="Example")
    generator["_add_feature_command_group"](parent, group, commands)
    items = parent.findall("m:section/m:list/m:item", _NS)
    assert len(items) == 2
    assert "Unbound by default." in "".join(items[0].itertext())
    assert items[1].findtext("m:list/m:item/m:p", namespaces=_NS) == "Braille: ROUTE"


@pytest.mark.parametrize("bindings", ("different", "same", "unbound", "desktop-only"))
def test_keyboard_and_braille_bindings_share_the_command(
    generator: dict[str, Any], bindings: str
) -> None:
    """Combined entries preserve bindings and details without mutating collected commands."""

    desktop = generator["KeyBindingDoc"]("F1", 0) if bindings != "unbound" else None
    laptop = (
        generator["KeyBindingDoc"]("F2", 0, click_count=2)
        if bindings == "different"
        else desktop
        if bindings == "same"
        else None
    )
    commands = [
        generator["CollectedCommandDoc"](
            name="example",
            label="Example",
            desktop_keybinding=desktop,
            laptop_keybinding=laptop,
            details="Run `example`.",
        ),
        generator["CollectedCommandDoc"](
            name="example",
            label="Example",
            command_type="braille",
            braille_bindings=["Freeze", "Other binding"],
            details="Run `example`.",
        ),
    ]
    group = generator["CollectedCommandGroupDoc"](
        title="Test",
        sections=(generator["CommandSectionDoc"]("Example", command_names=("example",)),),
    )
    parent = ET.Element("test")
    generator["_add_feature_command_group"](parent, group, commands)
    assert [label.text for label in parent.findall(".//m:gui", _NS)] == ["Example"]
    assert [code.text for code in parent.findall(".//m:code", _NS)] == ["example"]
    paragraphs = parent.findall(".//m:list/m:item/m:list/m:item/m:p", _NS)
    assert paragraphs[-1].text == "Braille: Freeze, Other binding"
    keyboard_paragraphs = paragraphs[:-1]
    if bindings in {"same", "unbound"}:
        assert [p.text.split(":", 1)[0] for p in keyboard_paragraphs] == ["Keyboard"]
        expected_keys = [["F1"]] if bindings == "same" else [[]]
    else:
        assert [p.text.split(":", 1)[0] for p in keyboard_paragraphs] == ["Desktop", "Laptop"]
        expected_keys = [["F1"], ["F2"] if bindings == "different" else []]
    assert [
        [key.text for key in p.findall("m:keyseq/m:key", _NS)] for p in keyboard_paragraphs
    ] == expected_keys
    assert commands[0].braille_bindings == []
    assert commands[1].braille_bindings == ["Freeze", "Other binding"]


def test_missing_command_topic_is_rejected(
    generator: dict[str, Any],
    topic_commands: dict[str, Any],
) -> None:
    """Commands without a documentation topic cause generation to fail."""

    with pytest.raises(ValueError, match="without a feature topic"):
        generator["_feature_command_targets"]([], {}, topic_commands["groups"])


def test_duplicate_command_topic_is_rejected(
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


def test_feature_embeds_command_subsets_and_preference_categories(
    generator: dict[str, Any],
) -> None:
    """A topic can include a command subset and a preference category."""

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


@pytest.mark.parametrize(
    ("field", "references"),
    (
        ("preference_categories", ("unknown",)),
        ("preference_categories", ("sleep-mode", "sleep-mode")),
        ("preference_controls", ("unknown",)),
        ("preference_controls", ("speech.language-switching", "speech.language-switching")),
    ),
)
def test_invalid_preference_placements_are_rejected(
    generator: dict[str, Any],
    topic_commands: dict[str, Any],
    field: str,
    references: tuple[str, ...],
) -> None:
    """Rejects unknown and repeated settings placements instead of dropping or duplicating them."""

    feature = generator["FeaturePageDoc"](
        page_id="features_test",
        title="Test",
        link_title="Test",
        description="Test",
        guide_xref="index",
        sections=(generator["FeatureSectionDoc"]("Test", **{field: references}),),
    )
    with pytest.raises(ValueError, match=r"feature preference (category|placement|control)"):
        generator["_preference_target_registry"](topic_commands["preferences"], [feature], {})


def test_documented_settings_have_rendered_destinations(
    generator: dict[str, Any], topic_commands: dict[str, Any]
) -> None:
    """Every panel and separately documented control has a rendered destination."""

    placements = generator["_feature_preference_placements"](
        topic_commands["pages"], topic_commands["reusable"], topic_commands["preferences"]
    )
    assert set(placements) == {
        panel.panel_id for page in topic_commands["preferences"] for panel in page.panels
    } | {
        target
        for page in topic_commands["pages"]
        for section in generator["_resolve_feature_sections"](page, topic_commands["reusable"])
        for target in section.preference_controls
    }
    for destination in placements.values():
        page_id, _, anchor = destination.partition("#")
        root = _parse_generated_page(topic_commands["all_rendered"][f"{page_id}.page"])
        if anchor:
            settings = root.find(f".//m:section[@id='{anchor}']", _NS)
            assert settings is not None


def test_settings_without_a_topic_are_rejected(
    generator: dict[str, Any], topic_commands: dict[str, Any]
) -> None:
    """Preference panels without a documentation topic cause generation to fail."""

    with pytest.raises(ValueError, match="Preference panels without a feature topic"):
        generator["_preference_target_registry"](topic_commands["preferences"], [], {})


def test_html_generation_preserves_topic_navigation(tmp_path: Path) -> None:
    """The HTML option preserves topic links, descriptions, and a single parent footer."""

    executable = shutil.which("yelp-build")
    if executable is None:
        pytest.skip("HTML rendering requires yelp-build")
    source = tmp_path / "source"
    output = source / "html"
    result = subprocess.run(
        [sys.executable, str(_SCRIPT), "--output-dir", str(source), "--html"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert (output / "index.html").is_file()
    for path in source.glob("*.page"):
        topic = _parse_generated_page(path.read_text())
        parent = topic.find("m:info/m:link[@type='guide']", _NS)
        if parent is None:
            continue
        parent_id = parent.attrib["xref"].split("#", 1)[0]
        content = (output / f"{parent_id}.html").read_text()
        link = re.search(
            rf'<a[^>]+href="{re.escape(path.stem)}\.html"[^>]*>(.*?)</a>',
            content,
            re.DOTALL,
        )
        assert link is not None, path.name
        description = topic.findtext("m:info/m:desc", namespaces=_NS)
        assert description is not None and description.strip() in unescape(link.group(1))
        assert (output / f"{path.stem}.html").read_text().count("More Information") == 1


def test_generated_help_is_valid_and_current(
    generator: dict[str, Any], topic_commands: dict[str, Any]
) -> None:
    """Generated pages are valid and match the complete set of checked-in pages."""

    generator["validate_generated_pages"](topic_commands["all_rendered"])
    assert set(topic_commands["all_rendered"]) == {page.name for page in _HELP_DIR.glob("*.page")}
    for name, content in topic_commands["all_rendered"].items():
        assert (_HELP_DIR / name).read_text() == content


def test_page_ids_and_types_match_filenames(topic_commands: dict[str, Any]) -> None:
    """Page identifiers match filenames, and the guide suffix matches the page type."""

    for filename, content in topic_commands["all_rendered"].items():
        root = _parse_generated_page(content)
        if root.get("type") == "guide":
            assert filename == "index.page" or filename.endswith("_guide.page")
        else:
            assert not filename.endswith("_guide.page")
        assert root.get("id") == filename.removesuffix(".page")


def test_guide_ids_without_the_required_suffix_are_rejected(generator: dict[str, Any]) -> None:
    """Guide identifiers other than index must end with _guide."""

    with pytest.raises(ValueError, match="Guide page id must end in _guide"):
        generator["validate_generated_pages"](
            {
                "example.page": f'<page xmlns="{_NS["m"]}" type="guide" id="example">'
                "<title>Example</title></page>"
            }
        )


@pytest.mark.parametrize("second_parent", ("backlink", "guide", "section", None))
def test_topics_have_at_most_one_parent_guide(
    generator: dict[str, Any], second_parent: str | None
) -> None:
    """Rejects extra parents while allowing reciprocal declarations of the same parent."""

    backlink = '<link type="guide" xref="other_guide"/>' if second_parent == "backlink" else ""
    topic_link = '<info><link type="topic" xref="example"/></info>'
    other_content = "<title>Other</title>"
    if second_parent == "guide":
        other_content = topic_link + other_content
    elif second_parent == "section":
        other_content += f'<section id="more">{topic_link}<title>More</title></section>'
    pages = {
        "index.page": (
            f'<page xmlns="{_NS["m"]}" type="guide" id="index"><title>Index</title>'
            f'<section id="reading">{topic_link}<title>Reading</title></section></page>'
        ),
        "example.page": (
            f'<page xmlns="{_NS["m"]}" type="topic" id="example"><info>'
            f'<link type="guide" xref="index#reading"/>{backlink}</info>'
            "<title>Example</title></page>"
        ),
        "other_guide.page": (
            f'<page xmlns="{_NS["m"]}" type="guide" id="other_guide">{other_content}</page>'
        ),
    }
    if second_parent:
        with pytest.raises(ValueError, match="Multiple parent guides for example"):
            generator["validate_generated_pages"](pages)
    else:
        generator["validate_generated_pages"](pages)


def test_generated_help_conforms_to_mallard_schema(
    topic_commands: dict[str, Any], tmp_path: Path
) -> None:
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


def test_unknown_link_target_is_rejected(generator: dict[str, Any]) -> None:
    """A mistyped logical target must not become a visible broken link."""

    link = generator["FeatureLinkDoc"]("speech.voice-setz")
    with pytest.raises(ValueError, match="Unknown help link target"):
        generator["_add_feature_links"](ET.Element("test"), (link,), {}, {}, "See also:")


@pytest.mark.parametrize("scheme", ("http", "https"))
def test_external_feature_links(generator: dict[str, Any], scheme: str) -> None:
    """External resources use href and retain their author-supplied descriptions."""

    target = f"{scheme}://example.org/help"
    link = generator["FeatureLinkDoc"](target, label="Community help", summary="Ask questions.")
    parent = ET.Element("test")
    generator["_add_feature_links"](parent, (link,), {}, {}, "See also:")
    rendered = parent.find(".//m:link", _NS)
    assert rendered is not None
    assert rendered.attrib == {"href": target}
    assert rendered.text == "Community help"
    assert rendered.tail == ": Ask questions."


@pytest.mark.parametrize("section_count", (0, 2))
def test_commands_matching_zero_or_multiple_sections_are_rejected(
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


def test_block_content_after_sections_is_rejected(generator: dict[str, Any]) -> None:
    """Validation rejects paragraphs placed after sections, as required by Mallard."""

    content = (
        '<page xmlns="http://projectmallard.org/1.0/" id="test" type="topic">'
        '<title>Test</title><section id="part"><title>Part</title></section>'
        "<p>Misplaced content</p></page>"
    )
    with pytest.raises(ValueError, match="Block content follows a section"):
        generator["validate_generated_pages"]({"test.page": content})


def test_duplicate_help_target_owners_are_rejected(generator: dict[str, Any]) -> None:
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


def test_orca_shortcuts_stay_with_their_commands(
    generator: dict[str, Any],
    topic_commands: dict[str, Any],
) -> None:
    """Shortcut instructions belong to generated command entries."""

    for page in topic_commands["pages"]:
        assert "Orca Modifier+" not in page.intro + page.details
        sections = generator["_resolve_feature_sections"](page, topic_commands["reusable"])
        for section in sections:
            assert not section.shortcuts, section.title
            for match in generator["_KEY_SEQUENCE_PATTERN"].finditer(
                section.intro + section.details + section.after_commands
            ):
                assert not match.group(0).startswith("Orca Modifier+"), (
                    section.title,
                    match.group(0),
                )


def test_related_links_are_not_duplicated(topic_commands: dict[str, Any]) -> None:
    """Each related-topic list contains unique destinations."""

    for content in topic_commands["rendered"].values():
        page = _parse_generated_page(content)
        for section in page.findall(".//m:section", _NS):
            if not section.get("id", "").endswith("-related"):
                continue
            destinations = [link.get("xref") for link in section.findall(".//m:link", _NS)]
            assert len(destinations) == len(set(destinations))


def test_metadata_parser_validates_field_arguments(generator: dict[str, Any]) -> None:
    """The parser resolves positional fields and rejects unknown keyword arguments."""

    call = ast.parse('PreferenceControlDoc("Test", "switch")', mode="eval").body
    assert generator["_find_keyword"](call, "label").value == "Test"
    bad = ast.parse('PreferenceControlDoc(label="Test", typo=True)', mode="eval").body
    with pytest.raises(ValueError, match="Unknown PreferenceControlDoc fields"):
        generator["_find_keyword"](bad, "kind")


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


def test_unlisted_preference_panels_are_rejected(generator: dict[str, Any]) -> None:
    """Panels missing from the preference categories cause generation to fail."""

    panel = generator["PanelDoc"](panel_id="new.panel", title="New", schema="")
    with pytest.raises(ValueError, match="inventory mismatch"):
        generator["_page_docs_from_groups"]([panel], {"preference_order": []})


def test_preference_categories_come_from_providers(topic_commands: dict[str, Any]) -> None:
    """Collected categories use provider descriptions and panels in the configured order."""

    metadata = json.loads(_METADATA_PATH.read_text())
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
def test_invalid_preference_categories_are_rejected(
    generator: dict[str, Any], arguments: str
) -> None:
    """Rejects missing descriptions and malformed category metadata during collection."""

    node = ast.parse(f"PreferenceCategoryDoc({arguments})", mode="eval").body
    evaluator = generator["SourceEvaluator"]({}, {}, {})
    with pytest.raises(ValueError):
        generator["_extract_category_doc"](node, evaluator)


@pytest.mark.parametrize("panels", (("test.panel", "test.panel"), ("test.panel", "unknown")))
def test_invalid_preference_panel_references_are_rejected(
    generator: dict[str, Any], panels: tuple[str, ...]
) -> None:
    """Rejects repeated and nonexistent panel memberships."""

    category = generator["PreferenceCategoryDoc"]("test", "Test", "Test settings", panels)
    panel = generator["PanelDoc"]("test.panel", "Test", "", category=category)
    with pytest.raises(ValueError, match=r"more than once|inventory mismatch"):
        generator["_page_docs_from_groups"]([panel], {"preference_order": ["test"]})


def test_global_only_preferences_match_the_ui(topic_commands: dict[str, Any]) -> None:
    """Documentation marks the same categories as global only as the preferences window."""

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


@pytest.mark.parametrize("change", ("missing", "unknown", "duplicate"))
def test_invalid_preference_category_order_is_rejected(
    generator: dict[str, Any], topic_commands: dict[str, Any], change: str
) -> None:
    """Category order must include every category exactly once and no unknown categories."""

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


def test_command_topics_link_to_associated_preferences(topic_commands: dict[str, Any]) -> None:
    """Command topics link to associated preferences when those appear on another page."""

    for command, links in topic_commands["associations"].by_command.items():
        filename = topic_commands["targets"][command].split("#", 1)[0] + ".page"
        page = _parse_generated_page(topic_commands["all_rendered"][filename])
        destinations = {
            link.get("xref", "").split("#", 1)[0] for link in page.findall(".//m:link", _NS)
        }
        assert {
            destination.split("#", 1)[0]
            for destination, _label in links
            if destination.split("#", 1)[0] + ".page" != filename
        } <= destinations


@pytest.mark.parametrize("field", ("command_groups", "command_names"))
def test_unknown_preference_commands_are_rejected(
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


def test_settings_have_documentation_or_an_explicit_exemption(generator: dict[str, Any]) -> None:
    """Every schema key has preference metadata or a recorded exemption."""

    exceptions = {
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


def test_command_definitions_are_in_discoverable_files() -> None:
    """Built-in command definitions stay in files searched by the documentation collector."""

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


@pytest.mark.parametrize("field", ("details", "after_commands"))
def test_prose_shortcut_tracks_binding_changes(generator: dict[str, Any], field: str) -> None:
    """Inline shortcut references follow changes to the command binding."""

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


def test_ui_label_changes_update_generated_help(
    generator: dict[str, Any], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """UI label changes are reflected in generated help."""

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

    pages = [_parse_generated_page(path.read_text()) for path in output.glob("*.page")]
    prose = " ".join("".join(p.itertext()) for page in pages for p in page.findall(".//m:p", _NS))
    text = " ".join("".join(page.itertext()) for page in pages)
    labels = [gui.text for page in pages for gui in page.findall(".//m:gui", _NS)]
    assert '"Global Speech Settings"' in prose
    assert '"Shared"' in prose
    assert "Global speech settings" in [page.findtext("m:title", namespaces=_NS) for page in pages]
    assert "Global Voice Settings" not in text
    assert "Global Speech Settings" in labels
    assert "Screen Reader Modifier Buttons" in labels
    assert "Screen Reader Modifier Keys" not in text
    assert "Toggle announcements for this page" in labels
    assert "Set default live region politeness level to off" not in text


def test_braille_indicators_follow_source_definitions(
    generator: dict[str, Any], tmp_path: Path
) -> None:
    """Changed indicator definitions reach help as literal code, without losing punctuation."""

    source = _ROOT / "src/orca"
    feature = tmp_path / "braille_presenter_feature_documentation.py"
    shutil.copyfile(source / feature.name, feature)
    replacements = {
        "CHECK_BOX_INDICATORS_BRAILLE": ["<_&>", "<checked>", "<partial>"],
        "RADIO_BUTTON_INDICATORS_BRAILLE": ["radio-off", "radio-on"],
        "SWITCH_INDICATORS_BRAILLE": ["switch-off", "switch-on"],
        "TOGGLE_BUTTON_INDICATORS_BRAILLE": ["toggle-off", "toggle-on"],
    }
    definitions = (source / "object_properties.py").read_text()
    definitions += "\n" + "\n".join(f"{name} = {value!r}" for name, value in replacements.items())
    definitions += '\nSTATE_READ_ONLY_BRAILLE = C_("text", "read_only_test")\n'
    (tmp_path / "object_properties.py").write_text(definitions)

    doc = generator["_execute_feature_documentation_module"](feature, {}, {})
    section = next(
        section
        for section in doc.sections
        if replacements["CHECK_BOX_INDICATORS_BRAILLE"][0] in section.details
    )
    parent = ET.Element("test")
    generator["_add_text_paragraphs"](parent, section.details)
    rendered = ET.tostring(parent, encoding="unicode")
    parsed = _parse_generated_page(rendered)
    assert [code.text for code in parsed.findall(".//m:code", _NS)] == [
        *(value for values in replacements.values() for value in values),
        "read_only_test",
    ]


def test_feature_collection_does_not_use_runtime_translations(
    generator: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Feature collection succeeds without calling runtime gettext functions."""

    def unexpected_translation(*_args: Any, **_kwargs: Any) -> Any:
        pytest.fail("Documentation generation must not call gettext")

    monkeypatch.setenv("LANGUAGE", "fr_FR")
    monkeypatch.setenv("LC_MESSAGES", "fr_FR.UTF-8")
    for name in ("gettext", "dgettext", "pgettext", "translation"):
        monkeypatch.setattr(gettext, name, unexpected_translation)
    pages, _sections = generator["collect_feature_documentation"](_ROOT / "src")
    assert pages


def test_missing_ui_label_in_feature_prose_is_rejected(generator: dict[str, Any]) -> None:
    """A removed source constant cannot leave a stale label in feature explanations."""

    source = _ROOT / "src"
    labels = generator["_collect_labels"](source)
    commands = generator["_collect_command_names"](source)
    name = "VOICE_GLOBAL_VOICE_SETTINGS"
    del labels[name]
    with pytest.raises(AttributeError, match=name):
        generator["_execute_feature_documentation_module"](
            source / "orca/speech_manager_feature_documentation.py",
            labels,
            commands,
        )


@pytest.mark.parametrize(
    "expression", ("guilabels.MISSING_LABEL", 'f"Use {guilabels.MISSING_LABEL}."')
)
def test_unresolved_preference_prose_is_rejected(
    generator: dict[str, Any], expression: str
) -> None:
    """Missing label references cannot silently erase a settings description."""

    evaluator = generator["SourceEvaluator"]({}, {}, {})
    with pytest.raises(ValueError, match="Cannot resolve documentation text"):
        evaluator.text(ast.parse(expression, mode="eval").body)


def test_feature_prose_keeps_command_and_setting_details_with_their_owners(
    generator: dict[str, Any],
) -> None:
    """Feature prose leaves individual command and setting instructions with their owners."""

    commands = generator["_collect_command_names"](_ROOT / "src")
    # Short names such as Read and Describe are also ordinary prose.
    names = {label for label in commands.values() if len(label) >= 12}
    control_labels = set()
    for path in (_ROOT / "src/orca").glob("*_preferences_grid.py"):
        for node in ast.walk(ast.parse(path.read_text())):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
                continue
            if node.func.id not in {"PreferenceControlDoc", "PreferenceActionDoc"}:
                continue
            fields = {field.arg: field.value for field in node.keywords}
            kind = fields.get("kind")
            if isinstance(kind, ast.Constant) and kind.value in {"group", "page"}:
                continue
            label = fields.get("label") or (node.args[0] if node.args else None)
            if label is not None:
                control_labels.update(
                    part.attr
                    for part in ast.walk(label)
                    if isinstance(part, ast.Attribute)
                    and isinstance(part.value, ast.Name)
                    and part.value.id == "guilabels"
                )

    for path in (_ROOT / "src/orca").glob("*_feature_documentation.py"):
        for node in ast.walk(ast.parse(path.read_text())):
            if not isinstance(node, ast.keyword) or node.arg not in {
                "intro",
                "details",
                "after_commands",
                "description",
            }:
                continue
            for part in ast.walk(node.value):
                if isinstance(part, ast.Attribute) and isinstance(part.value, ast.Name):
                    assert not (
                        part.value.id == "cmdnames"
                        or (part.value.id == "guilabels" and part.attr in control_labels)
                    ), (
                        f"{path}:{part.lineno}: move instructions for {ast.unparse(part)} "
                        "to its command or preference metadata"
                    )
                if not isinstance(part, ast.Constant) or not isinstance(part.value, str):
                    continue
                for name in names:
                    assert name not in part.value, (
                        f"{path}:{part.lineno}: move {name!r} instructions to command metadata"
                    )


@pytest.mark.parametrize("kind", ("keyboard", "braille"))
def test_command_details_follow_the_command(generator: dict[str, Any], kind: str) -> None:
    """Command details retain formatting and disappear when the command is removed."""

    command = generator["CollectedCommandDoc"](
        name="present",
        label="Present",
        command_type=kind,
        braille_bindings=["ROUTE"] if kind == "braille" else [],
        details="Press Enter.\n\nRun `example`.",
    )
    group = generator["CollectedCommandGroupDoc"](title="Example")
    parent = ET.Element("test")
    generator["_add_feature_command_group"](parent, group, [command])
    item = parent.find(".//m:item", _NS)
    assert item is not None
    assert item.findtext("m:p/m:key", namespaces=_NS) == "Enter"
    assert item.findtext("m:p/m:code", namespaces=_NS) == "example"

    without_command = ET.Element("test")
    generator["_add_feature_command_group"](without_command, group, [])
    assert len(without_command) == 0


@pytest.mark.parametrize("standalone", (False, True))
def test_command_section_instructions_preserve_formatting(
    generator: dict[str, Any], standalone: bool
) -> None:
    """Command section instructions keep their formatting when shown alone or with their group."""

    command = generator["CollectedCommandDoc"](name="example", label="Example")
    section = generator["CommandSectionDoc"](
        title="Example",
        target="example.commands",
        command_names=(command.name,),
        instructions="Use `example`.",
    )
    group = generator["CollectedCommandGroupDoc"](
        title="Test", commands=[command], sections=(section,)
    )
    if standalone:
        group = generator["_command_content_registry"]([("commands_test", group)])[section.target]
    parent = ET.Element("test")
    generator["_add_feature_command_group"](parent, group, group.commands)
    lists = parent.findall(".//m:list", _NS)
    assert len(lists) == 1
    container = next(node for node in parent.iter() if lists[0] in node)
    paragraph = container.find("m:p", _NS)
    assert paragraph is not None
    assert paragraph.findtext("m:code", namespaces=_NS) == "example"
    assert list(container).index(paragraph) < list(container).index(lists[0])


@pytest.mark.parametrize("since", (52, None, "v52", "52.1", "52..1", "52.alpha"))
def test_invalid_since_values_are_rejected(generator: dict[str, Any], since: Any) -> None:
    """Rejects malformed release annotations and point releases."""

    with pytest.raises(ValueError, match="Invalid Orca introduction release"):
        generator["_add_since_notice"](ET.Element("test"), since)


def test_since_metadata_generates_availability_notices(
    generator: dict[str, Any], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Source version annotations produce availability notices in generated help."""

    source = tmp_path / "src"
    shutil.copytree(
        _ROOT / "src/orca", source / "orca", ignore=shutil.ignore_patterns("__pycache__")
    )
    clipboard = source / "orca/clipboard_command_definitions.py"
    original = clipboard.read_text()
    clipboard.write_text(
        original.replace(
            "from .help_metadata import CommandGroupDoc",
            "from .help_metadata import CommandDoc, CommandGroupDoc, CommandSectionDoc",
        ).replace(
            'summary="Present the contents of the system clipboard.",',
            """summary="Present the contents of the system clipboard.",
        since="51",
        sections=(CommandSectionDoc(
            title="Clipboard commands",
            command_names=("present_clipboard_contents",),
            since="52",
        ),),
        commands=(
            CommandDoc("present_clipboard_contents", since="52"),
        ),""",
        )
    )
    (source / "orca/version_preferences_grid.py").write_text("""
class VersionPreferencesGrid(PreferencesGridBase):
    @classmethod
    def get_documentation(cls):
        return PreferencePanelDoc(
            title="Version settings", panel_id="versioned.panel",
            since="52",
            category=PreferenceCategoryDoc(
                "versioned", "Version settings", "Configure versioned settings.",
                ("versioned.panel",), since="52",
            ),
            controls=(
                PreferenceControlDoc(
                    "Mode", "choice", since="52",
                    value_docs=(
                        PreferenceValueDoc("New", since="53"),
                    ),
                    controls=(PreferenceControlDoc(
                        "Nested", "switch", since="52",
                    ),),
                ),
            ),
        )
""")
    (source / "orca/version_feature_documentation.py").write_text("""
from .help_metadata import FeatureDocumentationDoc, FeaturePageDoc, FeatureSectionDoc


def get_feature_documentation():
    return FeatureDocumentationDoc(
        pages=(FeaturePageDoc(
            "features_versions", "Versions", "Versions", "Versioned help.", "index",
            since="52",
            sections=(
                FeatureSectionDoc(title="Versions", include_target="versions.section"),
                FeatureSectionDoc(
                    title="Additional behavior", intro="Some additional behavior.", since="54",
                ),
            ),
        ),),
        sections=(FeatureSectionDoc(
            title="Versions", target="versions.section", intro="Some versioned behavior.",
            preference_categories=("versioned",), since="53",
        ),),
    )
""")
    metadata = json.loads(_METADATA_PATH.read_text())
    metadata["preference_order"].append("versioned")
    metadata["feature_order"].append("features_versions")
    metadata_path = tmp_path / "metadata.json"
    metadata_path.write_text(json.dumps(metadata))
    shutil.copytree(_HELP_DIR / "figures", tmp_path / "figures")
    output = tmp_path / "help"
    monkeypatch.setattr(
        "sys.argv",
        [
            str(_SCRIPT),
            "--src-dir",
            str(source),
            "--output-dir",
            str(output),
            "--metadata",
            str(metadata_path),
        ],
    )
    assert generator["main"]() == 0

    page = _parse_generated_page((output / "features_versions.page").read_text())
    notices = page.findall("m:note/m:p", _NS)
    assert ["".join(p.itertext()).strip() for p in notices] == [
        "Available in Orca 52 and later.",
    ]
    section = page.find("m:section[@id='versions']", _NS)
    assert section is not None
    assert section.find("m:note/m:p", _NS).text.strip() == "Available in Orca 53 and later."
    additional = page.find("m:section[@id='additional-behavior']", _NS)
    assert additional is not None
    assert additional.find("m:note/m:p", _NS).text.strip() == "Available in Orca 54 and later."
    settings = section.find("m:section[@id='settings-versions']", _NS)
    assert settings is not None
    assert len(settings.findall("m:note", _NS)) == 2  # Category and panel.
    items = {
        item.find("m:p/m:gui", _NS).text: item
        for item in page.findall(".//m:item", _NS)
        if item.find("m:p/m:gui", _NS) is not None
    }
    for label, version in (("Mode", "52"), ("New", "53"), ("Nested", "52")):
        assert items[label].find("m:note", _NS) is None, label
        paragraph = items[label].find("m:p", _NS)
        text = " ".join("".join(paragraph.itertext()).split())
        assert f"Available in Orca {version} and later." in text, label

    page = _parse_generated_page((output / "features_clipboard.page").read_text())
    assert "Available in Orca 51 and later." in "".join(page.itertext())
    assert "Available in Orca 52 and later." in "".join(page.itertext())
    items = {
        item.find("m:p/m:gui", _NS).text: item
        for item in page.findall(".//m:item", _NS)
        if item.find("m:p/m:gui", _NS) is not None
    }
    assert len(items) == 1
    command = next(iter(items.values()))
    assert command.find("m:note", _NS) is None
    text = " ".join("".join(command.find("m:p", _NS).itertext()).split())
    assert "Available in Orca 52 and later." in text

    executable = shutil.which("xmllint")
    schema = Path("/usr/share/xml/mallard/1.1/mallard-1.1.rng")
    if executable and schema.exists():
        result = subprocess.run(
            [
                executable,
                "--noout",
                "--relaxng",
                str(schema),
                str(output / "features_versions.page"),
                str(output / "features_clipboard.page"),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
