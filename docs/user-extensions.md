# User Extensions

## Status

This feature is early and experimental. The following are still pending:

- A page in Orca's Preferences dialog for managing approval and enabling/disabling
  user extensions (currently done manually via `dconf`).
- GSettings support for user extension settings (user extensions cannot yet
  define their own configurable options)
- Preferences UI for user extensions (built-in extensions have their own pages
  in the Preferences dialog; user extensions cannot yet provide one)
- Fixing bugs and improving the API based on user feedback.

## Overview

User extensions allow you to add custom commands to Orca. An extension is a
Python file containing a class that subclasses `Extension`. Each extension can
register keyboard commands that are available while Orca is running.

Extensions live in `~/.local/share/orca/extensions/`. Each `.py` file in that
directory that contains an `Extension` subclass is a potential extension.

## The Controller API

The only supported API for user extensions comes from the remote controller, available
as `self.controller` on the Extension base class. These are in-process "internal" wrappers
around Orca's D-Bus remote controller interface so that no actual D-Bus calls are made.

### `present_message_internal(message)`

Presents a message via speech and/or braille:

```python
self.controller.present_message_internal("Text to speak and braille")
```

### `execute_command_internal(module_name, command_name)`

Executes a command registered by an Orca module. The module and command names
correspond to those listed in [remote-controller-commands.md](remote-controller-commands.md).

```python
self.controller.execute_command_internal("SpeechManager", "DecreaseRate")
self.controller.execute_command_internal("SpeechManager", "ToggleSpeech")
self.controller.execute_command_internal("WhereAmIPresenter", "WhereAmIBasic")
self.controller.execute_command_internal("StructuralNavigator", "NextHeading")
```

### `get_value_internal(module_name, property_name)`

Reads a runtime value from an Orca module. The property names correspond to the getter names in
[remote-controller-commands.md](remote-controller-commands.md).

```python
rate = self.controller.get_value_internal("SpeechManager", "Rate")
pitch = self.controller.get_value_internal("SpeechManager", "Pitch")
volume = self.controller.get_value_internal("SpeechManager", "Volume")
voice = self.controller.get_value_internal("SpeechManager", "CurrentVoice")
synth = self.controller.get_value_internal("SpeechManager", "CurrentSynthesizer")
muted = self.controller.get_value_internal("SpeechManager", "SpeechIsMuted")
layout = self.controller.get_value_internal("CommandManager", "KeyboardLayoutIsDesktop")
```

### `set_value_internal(module_name, property_name, value)`

Sets a runtime value on an Orca module. The property names follow the same convention as
`get_value_internal`:

```python
self.controller.set_value_internal("SpeechManager", "Rate", 50)
self.controller.set_value_internal("SpeechManager", "Pitch", 5.0)
self.controller.set_value_internal("SpeechManager", "Volume", 8.0)
```

## Example

```python
"""Example extension demonstrating custom Orca commands."""

from orca import keybindings
from orca.command import Command, KeyboardCommand
from orca.extension import Extension


class HelloWorld(Extension):
    """Example extension with greeting and voice-info commands."""

    GROUP_LABEL = "Hello World"

    def _get_commands(self) -> list[Command]:
        return [
            KeyboardCommand(
                "say_hello_slowly",
                self.say_hello_slowly,
                self.GROUP_LABEL,
                "Says hello slowly",
                desktop_keybinding=keybindings.KeyBinding(
                    "F9", keybindings.ORCA_MODIFIER_MASK,
                ),
                laptop_keybinding=keybindings.KeyBinding(
                    "F9", keybindings.ORCA_MODIFIER_MASK,
                ),
            ),
            KeyboardCommand(
                "say_goodbye_fast",
                self.say_goodbye_fast,
                self.GROUP_LABEL,
                "Says goodbye fast",
                desktop_keybinding=keybindings.KeyBinding(
                    "F10", keybindings.ORCA_MODIFIER_MASK,
                ),
                laptop_keybinding=keybindings.KeyBinding(
                    "F10", keybindings.ORCA_MODIFIER_MASK,
                ),
            ),
            KeyboardCommand(
                "get_voice_settings",
                self.get_voice_settings,
                self.GROUP_LABEL,
                "Reports current voice settings",
                desktop_keybinding=keybindings.KeyBinding(
                    "F8", keybindings.ORCA_MODIFIER_MASK,
                ),
                laptop_keybinding=keybindings.KeyBinding(
                    "F8", keybindings.ORCA_MODIFIER_MASK,
                ),
            ),
        ]

    def say_hello_slowly(self):
        """Decreases the speech rate, says hello, then restores it."""

        original_rate = self.controller.get_value_internal("SpeechManager", "Rate")
        self.controller.set_value_internal("SpeechManager", "Rate", 20)
        self.controller.present_message_internal("Hello, world!")
        self.controller.set_value_internal("SpeechManager", "Rate", original_rate)
        return True

    def say_goodbye_fast(self):
        """Increases the speech rate 5 times, says goodbye, then restores it."""

        original_rate = self.controller.get_value_internal("SpeechManager", "Rate")
        for _i in range(5):
            self.controller.execute_command_internal(
                "SpeechManager", "IncreaseRate",
            )
        self.controller.present_message_internal("Goodbye, world!")
        self.controller.set_value_internal("SpeechManager", "Rate", original_rate)
        return True

    def get_voice_settings(self):
        """Reports the current voice settings."""

        rate = self.controller.get_value_internal("SpeechManager", "Rate")
        volume = self.controller.get_value_internal("SpeechManager", "Volume")
        pitch = self.controller.get_value_internal("SpeechManager", "Pitch")
        pitch_range = self.controller.get_value_internal(
            "SpeechManager", "PitchRange",
        )
        voice = self.controller.get_value_internal(
            "SpeechManager", "CurrentVoice",
        )
        synthesizer = self.controller.get_value_internal(
            "SpeechManager", "CurrentSynthesizer",
        )

        parts = [
            f"Voice: {voice}",
            f"Synthesizer: {synthesizer}",
            f"Rate: {rate}",
            f"Pitch: {pitch}",
            f"Pitch range: {pitch_range}",
            f"Volume: {volume}",
        ]
        self.controller.present_message_internal(". ".join(parts))
        return True
```

### Required Class Attributes

- `GROUP_LABEL`: The label used to group this extension's commands in Orca's
  keybindings list.

### Command Functions

Command functions take no arguments (other than `self`) and return `True` when
handled. The base class automatically wraps them to be compatible with Orca's
internal command dispatch.

### Keybindings

Each command needs a `KeyboardCommand` with a name, function, group label,
description, and optional keybindings for desktop and laptop layouts. If no
keybinding is provided, the user can assign one in preferences.

Available modifier masks:

- `keybindings.NO_MODIFIER_MASK`
- `keybindings.ORCA_MODIFIER_MASK` (Insert or Caps Lock, depending on layout)
- `keybindings.SHIFT_MODIFIER_MASK`
- `keybindings.CTRL_MODIFIER_MASK`
- `keybindings.ALT_MODIFIER_MASK`
- `keybindings.ORCA_SHIFT_MODIFIER_MASK`
- `keybindings.ORCA_CTRL_MODIFIER_MASK`

## Approving Extensions

For security, extensions must be approved before Orca will load them. When Orca
discovers an unapproved extension, it logs the file's SHA256 hash and a `dconf`
command to approve it.

Until the extension management UI is implemented, approval is done manually
via `dconf`. Note that `dconf write` replaces the entire value, so when
approving or revoking individual extensions, you must include all other entries.
To add a new approval without losing existing ones, read the current value first:

```sh
# See what's currently approved:
dconf read /org/gnome/orca/default/extensions/approved-user-extensions
# Then write it back with the new entry added.
```

```sh
# Check your debug log for the approval command, or compute the hash:
sha256sum ~/.local/share/orca/extensions/my_extension.py

# Approve a single extension (replace HASH with the actual SHA256 hash):
dconf write /org/gnome/orca/default/extensions/approved-user-extensions \
    "{'my_extension.py': 'HASH'}"

# Approve multiple extensions (all entries must be included):
dconf write /org/gnome/orca/default/extensions/approved-user-extensions \
    "{'my_extension.py': 'HASH1', 'another.py': 'HASH2'}"

# Revoke one extension while keeping others (rewrite without it):
dconf write /org/gnome/orca/default/extensions/approved-user-extensions \
    "{'another.py': 'HASH2'}"

# Revoke all approvals:
dconf reset /org/gnome/orca/default/extensions/approved-user-extensions
```

If you edit an approved extension, its hash changes and Orca will not load it
until you re-approve it with the new hash. The old hash remains in dconf until
you update it.

If you delete an extension file, its approval entry remains in dconf but has no
effect. There is currently no automatic cleanup of stale approvals.

## Disabling Extensions

Any extension (built-in or user) can be disabled by adding its class name to
the `disabled-extensions` list. As with approvals, `dconf write` replaces the
entire list:

```sh
# Disable one extension:
dconf write /org/gnome/orca/default/extensions/disabled-extensions \
    "['HelloWorld']"

# Disable multiple extensions:
dconf write /org/gnome/orca/default/extensions/disabled-extensions \
    "['HelloWorld', 'StructuralNavigator']"

# Re-enable all:
dconf reset /org/gnome/orca/default/extensions/disabled-extensions
```

Disabling a user extension does not revoke its approval. Re-enabling it is just
a matter of removing it from the disabled list.
