#!/usr/bin/python
# generate_gsettings_documentation.py
#
# Generate markdown documentation for Orca's GSettings schemas.
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

"""Generate markdown documentation for Orca's GSettings schemas."""

import argparse
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from generate_gsettings_schemas import _discover_schemas, generate_schema_xml


def _normalize_summary(summary: str | None) -> str:
    if summary is None:
        return "(No summary provided.)"
    summary = summary.strip()
    return summary or "(No summary provided.)"


def _escape_cell(value: str) -> str:
    """Escape markdown table cell content."""

    return value.replace("|", "\\|").replace("\n", " ")


def _format_key_row(
    key_el: ET.Element,
    enum_values: dict[str, list[tuple[str, str]]],
    include_enum_allowed: bool,
) -> str:
    key_name = key_el.get("name", "")
    enum_id = key_el.get("enum")
    key_type = key_el.get("type")
    default = key_el.findtext("default", default="")
    summary = _normalize_summary(key_el.findtext("summary"))

    if enum_id:
        enum_name = enum_id.rsplit(".", 1)[-1]
        if include_enum_allowed:
            values = enum_values.get(enum_id, [])
            allowed = ", ".join(f"`{nick}`" for nick, _ in values)
            if allowed:
                type_info = f"`enum`<br>`{enum_name}`<br>allowed: {allowed}"
            else:
                type_info = f"`enum`<br>`{enum_name}`"
        else:
            type_info = f"`enum`<br>`{enum_name}`"
    else:
        type_info = f"`{key_type or ''}`"

    return (
        f"| `{_escape_cell(key_name)}` | {_escape_cell(type_info)} | "
        f"`{_escape_cell(default)}` | {_escape_cell(summary)} |"
    )


# pylint: disable-next=too-many-locals, too-many-statements
def generate_documentation(
    src_dir: Path,
    include_enum_allowed: bool = False,
) -> str:
    """Generate markdown documentation from generated schema XML."""

    with tempfile.TemporaryDirectory(prefix="orca-gsettings-") as tmpdir:
        xml_path = Path(tmpdir) / "org.gnome.Orca.gschema.xml"
        generate_schema_xml(src_dir, str(xml_path))
        root = ET.parse(xml_path).getroot()

    schemas, _settings, _enums = _discover_schemas(src_dir)
    schema_names_by_id = {schema_id: schema_name for schema_name, schema_id in schemas.items()}

    enum_values: dict[str, list[tuple[str, str]]] = {}
    for enum_el in sorted(root.findall("enum"), key=lambda el: el.get("id", "")):
        enum_id = enum_el.get("id", "")
        pairs = []
        for value_el in enum_el.findall("value"):
            nick = value_el.get("nick", "")
            value = value_el.get("value", "")
            pairs.append((nick, value))
        enum_values[enum_id] = pairs

    schema_els = sorted(root.findall("schema"), key=lambda el: el.get("id", ""))
    lines: list[str] = []
    lines.append("# Orca GSettings Schemas Reference")
    lines.append("")
    lines.append("Orca stores settings under `/org/gnome/orca/`:")
    lines.append("- Profile-level settings: `/org/gnome/orca/<profile>/<schema-name>/`")
    lines.append("- App-specific overrides: `/org/gnome/orca/<profile>/apps/<app>/<schema-name>/`")
    lines.append("- Voice settings: `/org/gnome/orca/<profile>/voices/<voice-type>/`")
    lines.append(
        "- App-specific voice overrides: "
        "`/org/gnome/orca/<profile>/apps/<app>/voices/<voice-type>/`"
    )
    lines.append("")
    lines.append("Path variables:")
    lines.append(
        "- `<profile>`: profile ID. `default` is the standard profile; "
        "users can add others (for example `italian`)."
    )
    lines.append(
        "- `<schema-name>`: Orca schema name (for example `typing-echo`, `speech`, `braille`)."
    )
    lines.append("- `<app>`: app ID used for app-specific overrides.")
    lines.append("- `<voice-type>`: voice type (`default`, `uppercase`, `hyperlink`, `system`).")
    lines.append("")
    lines.append("Lookup precedence (highest to lowest):")
    lines.append(
        "- Scalars and enums: runtime override -> app override -> active profile -> "
        "`default` profile (if active profile is not `default`) -> schema default"
    )
    lines.append(
        "- Dictionary settings (for example pronunciation entries and keybinding overrides): "
        "runtime override -> profile dictionary with app dictionary overlaid on top -> "
        "schema default"
    )
    lines.append("")
    lines.append("Why dict settings do not inherit from `default` profile:")
    lines.append("- New profiles copy dict entries from the source profile when created.")
    lines.append(
        "- Primary use case: pronunciation dictionaries should be independently editable per "
        "profile. Entries in `default` that do not apply to another profile should be removable "
        "there without runtime fallback to `default`."
    )
    lines.append(
        "- This also applies to keybinding overrides: each profile/app layer should use only its "
        "own override dictionary instead of inheriting override entries from `default`."
    )
    lines.append("")
    lines.append("Migration paths:")
    lines.append(
        "- Automatic startup migration: Orca runs JSON -> GSettings migration at startup if "
        "migration has not been stamped yet."
    )
    lines.append(
        "- Manual import at startup: `orca -i DIR` / `orca --import-dir DIR` imports "
        "settings from `DIR` into dconf. WARNING: this replaces current "
        "`/org/gnome/orca/` settings."
    )
    lines.append(
        "  - Most users should not need this; automatic migration handles normal upgrades."
    )
    lines.append("  - Backup first: `dconf dump /org/gnome/orca/ > backup.ini`")
    lines.append(
        "  - Restore backup: "
        "`dconf reset -f /org/gnome/orca/ && dconf load /org/gnome/orca/ < backup.ini`"
    )
    lines.append(
        "- Stand-alone import/export/diff tool: "
        "`python tools/gsettings_import_export.py <import|export|roundtrip|diff> ...`"
    )
    lines.append("  - `import DIR`: import JSON settings from `DIR` into dconf.")
    lines.append("  - `export DIR`: export dconf settings to JSON files in `DIR`.")
    lines.append(
        "  - `diff SRC_DIR OUT_DIR`: export dconf to `OUT_DIR` and diff against `SRC_DIR`."
    )
    lines.append(
        "  - `roundtrip SRC_DIR OUT_DIR`: import from `SRC_DIR`, export to `OUT_DIR`, then diff."
    )
    lines.append("  - Use `import --dry-run` to preview writes without changing dconf.")
    lines.append(
        "  - Use `--prefix <orca-prefix>` if schemas are installed in a non-default prefix."
    )
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Schemas")
    lines.append("")

    for schema_el in schema_els:
        schema_id = schema_el.get("id", "")
        schema_name = schema_names_by_id.get(schema_id, "")
        keys_all = sorted(
            schema_el.findall("key"),
            key=lambda el: (el.get("name", "") != "version", el.get("name", "")),
        )
        keys = [key for key in keys_all if key.get("name", "") != "version"]

        lines.append(f"### `{schema_id}` (schema-name: `{schema_name}`)")
        lines.append("")

        lines.append("| Key | Type | Default | Summary |")
        lines.append("| --- | --- | --- | --- |")
        for key_el in keys:
            lines.append(_format_key_row(key_el, enum_values, include_enum_allowed))

        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    """Parse arguments and write generated documentation."""

    parser = argparse.ArgumentParser(description="Generate Orca GSettings markdown docs")
    parser.add_argument(
        "src_dir",
        nargs="?",
        default=str(Path(__file__).resolve().parent.parent / "src"),
        help="Path to src directory (default: ../src)",
    )
    parser.add_argument(
        "output",
        nargs="?",
        default=str(Path(__file__).resolve().parent.parent / "GSETTINGS-SCHEMAS.md"),
        help="Output markdown path (default: ../GSETTINGS-SCHEMAS.md)",
    )
    parser.add_argument(
        "--enum-allowed",
        action="store_true",
        help="Include inline enum allowed-value lists in the Type column.",
    )
    args = parser.parse_args()

    try:
        content = generate_documentation(
            Path(args.src_dir),
            include_enum_allowed=args.enum_allowed,
        )
    except Exception as error:  # pylint: disable=broad-exception-caught
        print(f"Error generating GSettings documentation: {error}", file=sys.stderr)
        return 1

    try:
        with open(args.output, "w", encoding="utf-8") as output_file:
            output_file.write(content)
            output_file.write("\n")
    except OSError as error:
        print(f"Error writing {args.output}: {error}", file=sys.stderr)
        return 1

    print(f"Documentation written to {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
