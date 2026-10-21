# Generated Help

The generator creates Mallard documentation in `help_ng/` from source metadata.
Edit the source metadata, not the generated pages. For now, this preview is
deliberately excluded from translation and installation; `help/` remains unchanged.

## Generate and View

From the source root:

```sh
python tools/generate_help_documentation.py
yelp help_ng/index.page
```

To view the help in a web browser, install `yelp-tools` and generate HTML:

```sh
python tools/generate_help_documentation.py --html
```

This command regenerates the Mallard pages and then renders them as HTML.
Open `help_ng/html/index.html` in your preferred browser. Rerun the command after
editing the documentation and reload the page to review your changes. The HTML
preview is ignored by Git.

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

Keep topic introductions focused on what the feature does. Put instructions for
individual commands in their `CommandDoc` metadata and explanations of individual
settings in their `PreferenceControlDoc` metadata. Refer to other topics rather
than repeating their command or setting instructions. When removing a command or
setting, remove its documentation metadata too.

Use `CommandDoc.summary` for a short description and `CommandDoc.details` for
usage instructions. Put explanations of individual choices and list actions in
`PreferenceValueDoc` and `PreferenceActionDoc`, respectively.

## Add a Feature

1. Copy a similar `*_feature_documentation.py` file. Import documentation classes
   from `.help_metadata`.
2. Write a brief introduction and general usage details in its `FeatureSectionDoc`.
   Use `command_groups` to include command groups, or `command_names` for individual
   commands. Use `preference_categories` to include settings categories, or
   `preference_panels` for individual panels. Copy these identifiers from their
   command definitions or preferences metadata.
3. Choose an index section using `guide_xref`, following the existing examples.
   Give each topic one parent guide. Guide page IDs end in `_guide`, except for `index`.
   Add each generated page ID to `feature_order` in `help_ng/generated_help_metadata.json`.
   For a new settings category, also define its `PreferenceCategoryDoc` in the
   preferences grid and add its category ID to `preference_order`.

## Release Availability

Most documentation objects support `since`, which names the major release that
introduces the documented content. Put it on the highest-level documentation
object whose contents were all introduced in that release. For an entirely new
feature introduced in Orca 53, set `since="53"` on its `FeaturePageDoc` and leave it
unset on the feature's sections, settings, and commands. For a new setting in an
existing feature, put it on that setting instead.

## Labels, Shortcuts, and Links

Use UI constants, not copies of their text, so renaming a label updates the docs:

```python
from . import guilabels

intro = f'Use "{guilabels.VOICE_GLOBAL_VOICE_SETTINGS}" preferences.'
```

Enclose command names and UI labels in double quotes when mentioning them in prose.

For a topic name in prose, use its logical target in double brackets, for example
`See [[reviewing.orca-find]].` The generator turns this into an inline link using
the topic's current title in double quotes. Do not add quotes or copy the title.
This works in feature prose and command and preference descriptions. Do not repeat
an inline link in the related topics.

Keep command shortcuts in the command definitions. The generated command lists
show their current bindings; do not repeat them in introductory prose.

For additional related topics, use
`FeatureLinkDoc("documents.structural-navigation")` in the section's `links`.
The string is the destination's `target`, declared in its metadata, not a
filename. The generator supplies the title and description.
For external links, use a full HTTP or HTTPS URL as the target and supply a
`label`, for example `FeatureLinkDoc("https://www.freelists.org/list/orca",
label="Orca mailing list")`. You can also supply a `summary`.

Use backticks around terminal commands and filenames.
