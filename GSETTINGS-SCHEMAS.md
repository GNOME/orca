# Orca GSettings Schemas Reference

Orca stores settings under `/org/gnome/orca/`:
- Profile-level settings: `/org/gnome/orca/<profile>/<schema-name>/`
- App-specific overrides: `/org/gnome/orca/<profile>/apps/<app>/<schema-name>/`
- Voice settings: `/org/gnome/orca/<profile>/voices/<voice-type>/`
- App-specific voice overrides: `/org/gnome/orca/<profile>/apps/<app>/voices/<voice-type>/`

Path variables:
- `<profile>`: profile ID. `default` is the standard profile; users can add others (for example `italian`).
- `<schema-name>`: Orca schema name (for example `typing-echo`, `speech`, `braille`).
- `<app>`: app ID used for app-specific overrides.
- `<voice-type>`: voice type (`default`, `uppercase`, `hyperlink`, `system`).

Lookup precedence (highest to lowest):
- Scalars and enums: runtime override -> app override -> active profile -> `default` profile (if active profile is not `default`) -> schema default
- Dict settings (`a{ss}`, `a{saas}`): runtime override -> profile dictionary with app dictionary overlaid on top -> schema default

Why dict settings do not inherit from `default` profile:
- New profiles copy dict entries from the source profile when created.
- Primary use case: pronunciation dictionaries should be independently editable per profile. Entries in `default` that do not apply to another profile should be removable there without runtime fallback to `default`.
- This also applies to keybinding overrides: each profile/app layer should use only its own override dictionary instead of inheriting override entries from `default`.

Migration paths:
- Automatic startup migration: Orca runs JSON -> GSettings migration at startup if migration has not been stamped yet.
- Manual import at startup: `orca -i DIR` / `orca --import-dir DIR` imports settings from `DIR` into dconf. WARNING: this replaces current `/org/gnome/orca/` settings.
  - Most users should not need this; automatic migration handles normal upgrades.
  - Backup first: `dconf dump /org/gnome/orca/ > backup.ini`
  - Restore backup: `dconf reset -f /org/gnome/orca/ && dconf load /org/gnome/orca/ < backup.ini`
- Stand-alone import/export/diff tool: `python tools/gsettings_import_export.py <import|export|roundtrip|diff> ...`
  - `import DIR`: import JSON settings from `DIR` into dconf.
  - `export DIR`: export dconf settings to JSON files in `DIR`.
  - `diff SRC_DIR OUT_DIR`: export dconf to `OUT_DIR` and diff against `SRC_DIR`.
  - `roundtrip SRC_DIR OUT_DIR`: import from `SRC_DIR`, export to `OUT_DIR`, then diff.
  - Use `import --dry-run` to preview writes without changing dconf.
  - Use `--prefix <orca-prefix>` if schemas are installed in a non-default prefix.

---

## Schemas

### `org.gnome.Orca.Braille` (schema-name: `braille`)

| Key | Type | Default | Summary |
| --- | --- | --- | --- |
| `braille-progress-bar-updates` | `b` | `false` | Show progress bar updates in braille |
| `computer-braille-at-cursor` | `b` | `true` | Use computer braille at cursor position |
| `contracted-braille` | `b` | `false` | Enable contracted braille |
| `contraction-table` | `s` | `''` | Braille contraction table name |
| `display-ancestors` | `b` | `true` | Display ancestors of current object |
| `enabled` | `b` | `true` | Enable braille output |
| `end-of-line-indicator` | `b` | `true` | Show end-of-line indicator |
| `flash-message-duration` | `i` | `5000` | Flash message duration in milliseconds |
| `flash-messages` | `b` | `true` | Enable braille flash messages |
| `flash-messages-detailed` | `b` | `true` | Use detailed flash messages |
| `flash-messages-persistent` | `b` | `false` | Make flash messages persistent |
| `link-indicator` | `enum`<br>`BrailleIndicator` | `'dots78'` | Braille link indicator style (none, dot7, dot8, dots78) |
| `monitor-background` | `s` | `'#ffffff'` | Braille monitor background color |
| `monitor-cell-count` | `i` | `32` | Braille monitor cell count |
| `monitor-foreground` | `s` | `'#000000'` | Braille monitor foreground color |
| `monitor-show-dots` | `b` | `false` | Show Unicode braille dots in braille monitor |
| `present-mnemonics` | `b` | `true` | Present mnemonics on braille display |
| `progress-bar-braille-interval` | `i` | `10` | Progress bar braille update interval in seconds |
| `progress-bar-braille-verbosity` | `enum`<br>`ProgressBarVerbosity` | `'application'` | Progress bar braille verbosity (all, application, window) |
| `rolename-style` | `enum`<br>`VerbosityLevel` | `'verbose'` | Braille rolename style (brief, verbose) |
| `selector-indicator` | `enum`<br>`BrailleIndicator` | `'dots78'` | Braille selector indicator style (none, dot7, dot8, dots78) |
| `text-attributes-indicator` | `enum`<br>`BrailleIndicator` | `'none'` | Braille text attributes indicator style (none, dot7, dot8, dots78) |
| `verbosity-level` | `enum`<br>`VerbosityLevel` | `'verbose'` | Braille verbosity level (brief, verbose) |
| `word-wrap` | `b` | `false` | Enable braille word wrap |

---

### `org.gnome.Orca.CaretNavigation` (schema-name: `caret-navigation`)

| Key | Type | Default | Summary |
| --- | --- | --- | --- |
| `enabled` | `b` | `true` | Enable caret navigation |
| `layout-mode` | `b` | `true` | Use document layout mode |
| `triggers-focus-mode` | `b` | `false` | Caret navigation triggers focus mode |

---

### `org.gnome.Orca.Chat` (schema-name: `chat`)

| Key | Type | Default | Summary |
| --- | --- | --- | --- |
| `announce-buddy-typing` | `b` | `false` | Announce when buddies are typing |
| `message-verbosity` | `enum`<br>`ChatMessageVerbosity` | `'all'` | Chat message verbosity (all, all-if-focused, focused-channel, active-channel) |
| `room-histories` | `b` | `false` | Provide chat room specific message histories |
| `speak-room-name` | `b` | `false` | Speak chat room name |
| `speak-room-name-last` | `b` | `false` | Speak chat room name after message |

---

### `org.gnome.Orca.Document` (schema-name: `document`)

| Key | Type | Default | Summary |
| --- | --- | --- | --- |
| `auto-sticky-focus-mode` | `b` | `true` | Auto-detect sticky focus mode for web apps |
| `find-results-minimum-length` | `i` | `4` | Minimum length for find results to be spoken |
| `find-results-verbosity` | `enum`<br>`FindResultsVerbosity` | `'all'` | Find results verbosity (none, if-line-changed, all) |
| `native-nav-triggers-focus-mode` | `b` | `true` | Native navigation triggers focus mode |
| `page-summary-on-load` | `b` | `true` | Present page summary when document loads |
| `say-all-on-load` | `b` | `true` | Perform say all when document loads |

---

### `org.gnome.Orca.FlatReview` (schema-name: `flat-review`)

| Key | Type | Default | Summary |
| --- | --- | --- | --- |
| `restricted` | `b` | `false` | Restrict flat review to current object |

---

### `org.gnome.Orca.Keybindings` (schema-name: `keybindings`)

| Key | Type | Default | Summary |
| --- | --- | --- | --- |
| `entries` | `a{saas}` | `@a{saas} {}` | User keybinding overrides |
| `keyboard-layout` | `enum`<br>`KeyboardLayout` | `'desktop'` | Keyboard layout (desktop, laptop) |
| `orca-modifier-keys` | `as` | `['Insert', 'KP_Insert']` | Keys used as the Orca modifier |

---

### `org.gnome.Orca.LiveRegions` (schema-name: `live-regions`)

| Key | Type | Default | Summary |
| --- | --- | --- | --- |
| `enabled` | `b` | `true` | Enable live region support |
| `present-from-inactive-tab` | `b` | `false` | Present live regions from inactive tabs |

---

### `org.gnome.Orca.MouseReview` (schema-name: `mouse-review`)

| Key | Type | Default | Summary |
| --- | --- | --- | --- |
| `enabled` | `b` | `false` | Enable mouse review |
| `present-tooltips` | `b` | `false` | Present tooltips on mouse hover |

---

### `org.gnome.Orca.ProfileMetadata` (schema-name: `metadata`)

| Key | Type | Default | Summary |
| --- | --- | --- | --- |
| `display-name` | `s` | `''` | Original display name (label) of the profile or app |
| `internal-name` | `s` | `''` | Original internal name (JSON dict key) of the profile |

---

### `org.gnome.Orca.Pronunciations` (schema-name: `pronunciations`)

| Key | Type | Default | Summary |
| --- | --- | --- | --- |
| `entries` | `a{ss}` | `@a{ss} {}` | Pronunciation dictionary entries |

---

### `org.gnome.Orca.SayAll` (schema-name: `say-all`)

| Key | Type | Default | Summary |
| --- | --- | --- | --- |
| `announce-blockquote` | `b` | `true` | Announce blockquotes |
| `announce-form` | `b` | `true` | Announce non-landmark forms |
| `announce-grouping` | `b` | `true` | Announce groupings |
| `announce-landmark` | `b` | `true` | Announce landmarks |
| `announce-list` | `b` | `true` | Announce lists |
| `announce-table` | `b` | `true` | Announce tables |
| `rewind-and-fast-forward` | `b` | `false` | Enable rewind and fast forward in Say All |
| `structural-navigation` | `b` | `false` | Enable structural navigation in Say All |
| `style` | `enum`<br>`SayAllStyle` | `'sentence'` | Say All style (line, sentence) |

---

### `org.gnome.Orca.Sound` (schema-name: `sound`)

| Key | Type | Default | Summary |
| --- | --- | --- | --- |
| `beep-progress-bar-updates` | `b` | `false` | Beep progress bar updates |
| `enabled` | `b` | `true` | Enable sound output |
| `progress-bar-beep-interval` | `i` | `0` | Progress bar beep interval in seconds |
| `progress-bar-beep-verbosity` | `enum`<br>`ProgressBarVerbosity` | `'application'` | Progress bar beep verbosity (all, application, window) |
| `volume` | `d` | `0.5` | Sound volume (0.0-1.0) |

---

### `org.gnome.Orca.Speech` (schema-name: `speech`)

| Key | Type | Default | Summary |
| --- | --- | --- | --- |
| `always-announce-selected-range-in-spreadsheet` | `b` | `false` | Always announce selected range in spreadsheets |
| `announce-blockquote` | `b` | `true` | Announce blockquotes |
| `announce-cell-coordinates` | `b` | `true` | Announce cell coordinates |
| `announce-cell-headers` | `b` | `true` | Announce cell headers |
| `announce-cell-span` | `b` | `true` | Announce cell span |
| `announce-form` | `b` | `true` | Announce forms |
| `announce-grouping` | `b` | `true` | Announce groupings/panels |
| `announce-landmark` | `b` | `true` | Announce landmarks |
| `announce-list` | `b` | `true` | Announce lists |
| `announce-spreadsheet-cell-coordinates` | `b` | `true` | Announce spreadsheet cell coordinates |
| `announce-table` | `b` | `true` | Announce tables |
| `auto-language-switching` | `b` | `true` | Automatically switch voice based on text language |
| `capitalization-style` | `enum`<br>`CapitalizationStyle` | `'none'` | Capitalization style (none, spell, icon) |
| `enable` | `b` | `true` | Enable speech output |
| `insert-pauses-between-utterances` | `b` | `true` | Insert pauses between utterances |
| `messages-are-detailed` | `b` | `true` | Use detailed informative messages |
| `monitor-background` | `s` | `'#000000'` | Speech monitor background color |
| `monitor-font-size` | `i` | `14` | Speech monitor font size |
| `monitor-foreground` | `s` | `'#ffffff'` | Speech monitor foreground color |
| `only-speak-displayed-text` | `b` | `false` | Only speak displayed text |
| `progress-bar-speech-interval` | `i` | `10` | Progress bar speech update interval in seconds |
| `progress-bar-speech-verbosity` | `enum`<br>`ProgressBarVerbosity` | `'application'` | Progress bar speech verbosity (all, application, window) |
| `punctuation-level` | `enum`<br>`PunctuationStyle` | `'most'` | Punctuation verbosity level (none, some, most, all) |
| `repeated-character-limit` | `i` | `4` | Threshold for repeated character compression |
| `speak-blank-lines` | `b` | `true` | Speak blank lines |
| `speak-description` | `b` | `true` | Speak object descriptions |
| `speak-indentation-and-justification` | `b` | `false` | Speak indentation and justification |
| `speak-indentation-only-if-changed` | `b` | `false` | Speak indentation only if changed |
| `speak-misspelled-indicator` | `b` | `true` | Speak misspelled word indicator |
| `speak-numbers-as-digits` | `b` | `false` | Speak numbers as individual digits |
| `speak-position-in-set` | `b` | `false` | Speak position in set |
| `speak-progress-bar-updates` | `b` | `true` | Speak progress bar updates |
| `speak-row-in-document-table` | `b` | `true` | Speak full row in document tables |
| `speak-row-in-gui-table` | `b` | `true` | Speak full row in GUI tables |
| `speak-row-in-spreadsheet` | `b` | `false` | Speak full row in spreadsheets |
| `speak-tutorial-messages` | `b` | `true` | Speak tutorial messages |
| `speak-widget-mnemonic` | `b` | `true` | Speak widget mnemonics |
| `speech-server` | `s` | `''` | Speech server name |
| `speech-server-factory` | `s` | `'speechdispatcherfactory'` | Speech server factory module |
| `synthesizer` | `s` | `''` | Speech synthesizer |
| `use-color-names` | `b` | `true` | Use color names instead of values |
| `use-pronunciation-dictionary` | `b` | `true` | Apply user pronunciation dictionary |
| `verbosity-level` | `enum`<br>`VerbosityLevel` | `'verbose'` | Speech verbosity level (brief, verbose) |

---

### `org.gnome.Orca.Spellcheck` (schema-name: `spellcheck`)

| Key | Type | Default | Summary |
| --- | --- | --- | --- |
| `present-context` | `b` | `true` | Present context/surrounding sentence |
| `spell-error` | `b` | `true` | Spell misspelled word |
| `spell-suggestion` | `b` | `true` | Spell suggested correction |

---

### `org.gnome.Orca.StructuralNavigation` (schema-name: `structural-navigation`)

| Key | Type | Default | Summary |
| --- | --- | --- | --- |
| `enabled` | `b` | `true` | Enable structural navigation |
| `large-object-text-length` | `i` | `75` | Minimum text length for large objects |
| `triggers-focus-mode` | `b` | `false` | Structural navigation triggers focus mode |
| `wraps` | `b` | `true` | Wrap when reaching top/bottom |

---

### `org.gnome.Orca.SystemInformation` (schema-name: `system-information`)

| Key | Type | Default | Summary |
| --- | --- | --- | --- |
| `date-format` | `s` | `'%x'` | Date format string |
| `time-format` | `s` | `'%X'` | Time format string |

---

### `org.gnome.Orca.TableNavigation` (schema-name: `table-navigation`)

| Key | Type | Default | Summary |
| --- | --- | --- | --- |
| `enabled` | `b` | `true` | Enable table navigation |
| `skip-blank-cells` | `b` | `false` | Skip blank cells during navigation |

---

### `org.gnome.Orca.TextAttributes` (schema-name: `text-attributes`)

| Key | Type | Default | Summary |
| --- | --- | --- | --- |
| `attributes-to-braille` | `as` | `@as []` | Text attributes to mark in braille |
| `attributes-to-speak` | `as` | `@as []` | Text attributes to speak |

---

### `org.gnome.Orca.TypingEcho` (schema-name: `typing-echo`)

| Key | Type | Default | Summary |
| --- | --- | --- | --- |
| `action-keys` | `b` | `true` | Echo action keys |
| `alphabetic-keys` | `b` | `true` | Echo alphabetic keys |
| `character-echo` | `b` | `false` | Echo inserted characters |
| `diacritical-keys` | `b` | `false` | Echo diacritical keys |
| `function-keys` | `b` | `true` | Echo function keys |
| `key-echo` | `b` | `true` | Enable key echo |
| `modifier-keys` | `b` | `true` | Echo modifier keys |
| `navigation-keys` | `b` | `false` | Echo navigation keys |
| `numeric-keys` | `b` | `true` | Echo numeric keys |
| `punctuation-keys` | `b` | `true` | Echo punctuation keys |
| `sentence-echo` | `b` | `false` | Echo completed sentences |
| `space` | `b` | `true` | Echo space key |
| `word-echo` | `b` | `false` | Echo completed words |

---

### `org.gnome.Orca.Voice` (schema-name: `voice`)

| Key | Type | Default | Summary |
| --- | --- | --- | --- |
| `established` | `b` | `false` | Whether this voice type has been user-customized |
| `family-dialect` | `s` | `''` | Voice family dialect |
| `family-gender` | `s` | `''` | Voice family gender |
| `family-lang` | `s` | `''` | Voice family language |
| `family-name` | `s` | `''` | Voice family name |
| `family-variant` | `s` | `''` | Voice family variant |
| `pitch` | `d` | `5.0` | Speech pitch (0.0-10.0) |
| `rate` | `i` | `50` | Speech rate (0-100) |
| `volume` | `d` | `10.0` | Speech volume (0.0-10.0) |

---

