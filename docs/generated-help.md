# Generated Help

Documentation is generated into `help_ng/`. Edit the source metadata, not the
generated pages. For now, this preview is deliberately excluded from translation
and installation; `help/` remains unchanged.

## Generate and View

From the source root:

```sh
python tools/generate_help_documentation.py
yelp help_ng/index.page
```

Regenerate after changing documentation, commands, or preferences, and include the
generated changes in your commit.

## Update an Existing Feature

- **Feature documentation:** Edit `intro` and `details` in
  `*_feature_documentation.py`.
- **Commands:** Add or change commands in `*_command_definitions.py`.
  Labels and bindings are collected automatically. Use `get_documentation()` for
  command descriptions and grouping.
- **Settings:** Update `get_documentation()` in `*_preferences_grid.py` alongside
  the UI. Use schema/key references for defaults rather than copying their values.
  Put configuration guidance in `instructions` and text for links in `link_summary`.
  Feature behavior belongs in the feature documentation, not in either field.

## Add a Feature

1. Copy a similar `*_feature_documentation.py` file.
2. Write a brief introduction and any usage details in its `FeatureSectionDoc`.
   Use `command_groups` to include command groups, or `command_names` for individual
   commands. Use `preference_categories` to include settings categories, or
   `preference_panels` for individual panels. Copy these identifiers from their
   command definitions or preferences metadata.
3. Choose an index section using `guide_xref`, following the existing examples.
   Guide page IDs end in `_guide`, except for `index`.
   Add the page ID to `feature_order` in `help_ng/generated_help_metadata.json`.
   For a new settings category, also define its `PreferenceCategoryDoc` in the
   preferences grid and add its category ID to `preference_order`.

## Labels, Shortcuts, and Links

Use UI constants, not copies of their text, so renaming a label updates the docs:

```python
from . import cmdnames, guilabels

intro = f"Use {guilabels.VOICE_GLOBAL_VOICE_SETTINGS} preferences."
details = f"{cmdnames.WHERE_AM_I_SELECTION} presents selected text."
```

When mentioning a shortcut, add a `CommandShortcutDoc` to the section's `shortcuts`.
The generator uses the command's current default binding.

For links, use `FeatureLinkDoc("documents.structural-navigation")` in the section's
`links`. The string is the destination's `target`, declared in its metadata, not a
filename. The generator supplies the destination, title, and description.

Import documentation classes from `.help_metadata`. Use backticks around terminal
commands and filenames; no Mallard markup is needed.
