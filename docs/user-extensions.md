# User Extensions

## Status

This feature is early and experimental. The following are still pending:

- GSettings support for user extension settings (user extensions cannot yet
  define their own configurable options)
- Preferences UI for extension-specific settings (user extensions can be
  approved, revoked, enabled, and disabled in Orca's Preferences window, but
  cannot yet provide their own settings pages)
- Fixing bugs and improving the API based on user feedback.

## Overview

User extensions allow you to add custom behavior to Orca, including keyboard
commands and speech output hooks. An extension is a Python file containing a
class that subclasses `Extension`.

Extensions live in `~/.local/share/orca/extensions/`. Each `.py` file in that
directory that contains an `Extension` subclass is a potential extension.

## Approving Extensions

For security, extensions must be approved before Orca will load them. When Orca
discovers an unapproved extension, it logs the file's SHA256 hash.

Use the User Extensions page in Orca's Preferences window to approve,
re-approve, or revoke user extensions. The page computes the file's SHA256 hash
and persists the approval in dconf. This is the recommended way to manage
approval.

Approval and revocation can also be done via the command line:

```sh
# Approve an extension:
orca --approve-extension my_extension.py

# Revoke approval:
orca --revoke-extension my_extension.py
```

These commands compute the file's SHA256 hash and persist the approval in dconf.
Extensions approved from the command line will be loaded on the next Orca
startup.

If you edit an approved extension, its hash changes and Orca will not load it
until you re-approve it from the User Extensions preferences page or the command
line. If you delete an extension file, its approval entry remains but has no
effect. There is currently no automatic cleanup of stale approvals.

## Disabling Extensions

Use the User Extensions page in Orca's Preferences window to enable or disable
user extensions. This is the recommended way to manage enabled state for user
extensions.

User extensions can also be disabled via `dconf`, primarily for testing or
scripting. Note that `dconf write` replaces the entire list:

```sh
# Disable one extension:
dconf write /org/gnome/orca/default/extensions/disabled-extensions \
    "['HelloWorld']"

# Disable multiple extensions:
dconf write /org/gnome/orca/default/extensions/disabled-extensions \
    "['HelloWorld', 'ReverseWords']"

# Re-enable all:
dconf reset /org/gnome/orca/default/extensions/disabled-extensions
```

Disabling a user extension does not revoke its approval. Re-enabling a user
extension is just a matter of removing it from the disabled list.

## Extension Class Basics

### Required Class Attributes

- `GROUP_LABEL`: The user-visible label for this extension. It is also used to
  group the extension's commands in Orca's keybindings list.

Optional class attributes:

- `GROUP_DESCRIPTION`: A short description shown in Orca's User Extensions
  preferences page.

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

## The Controller API

Command extensions can use the remote controller, available as
`self.controller` on the `Extension` base class. The controller provides access
to all of Orca's settings and its commands, both bound and unbound.

The following in-process "internal" wrappers should be used in user extensions to avoid
making actual D-Bus calls:

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

## Command Example

```python
"""Example extension demonstrating custom Orca commands."""

from orca import keybindings
from orca.command import Command, KeyboardCommand
from orca.extension import Extension


class HelloWorld(Extension):
    """Example extension with greeting and voice-info commands."""

    GROUP_LABEL = "Hello World"
    GROUP_DESCRIPTION = "Adds greeting and voice-info commands."

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

## Speech Output Hooks

Extensions can observe, replace, or consume speech immediately before Orca sends
it to the active speech provider. This enables features such as translating
Orca's generated speech, or routing speech through a provider that Orca does not
support directly.

Override `on_speech_output(output)` in your extension. It receives a
`SpeechOutput` instance with:

- `text`: The text Orca is about to speak.
- `obj`: The accessible object associated with the speech, or `None` for
  messages and other speech that is not tied to an accessible object.

When `obj` is not `None`, extensions can use standard AT-SPI calls on it to
determine the application, role, state, attributes, and other details that might
be relevant to whether they wish to modify or consume the speech.

Return `None` to observe without changing speech. Return
`SpeechOutputResult.replace(text)` to replace what Orca will speak. Return
`SpeechOutputResult.consume_output()` if the extension has handled the speech
itself and Orca should not send it to its configured speech provider.

Speech hooks are called in extension load order. Replacements are chained, so
later hooks receive the text returned by earlier hooks. If an extension consumes
the output, hook processing stops and that extension owns the speech. Orca does
not try to coordinate multiple consumers yet; the current model keeps ownership
simple until there is a compelling use case for more orchestration.

Speech hooks are latency-sensitive. Slow work, including network calls to AI or
translation services, can make Orca feel unresponsive. If your extension needs
to do slow work, consider consuming the output and speaking asynchronously
through your own provider.

Speech hooks can receive anything Orca is about to speak, including typed text,
document contents, chat messages, and notifications. Only approve extensions
you trust.

### Reverse Word Order Example

This silly example lets you test the hook locally. It reverses what Orca speaks,
as long as there is an associated accessible object (i.e. not a system message),
and that object is not a terminal nor is it from gnome-shell.

```python
"""Example extension that reverses the order of spoken words."""

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from orca.extension import Extension, SpeechOutput, SpeechOutputResult


class ReverseWords(Extension):
    """Reverses word order before Orca sends speech to the synthesizer."""

    GROUP_LABEL = "Reverse Words"
    GROUP_DESCRIPTION = "Reverses spoken word order for testing speech hooks."

    @staticmethod
    def _should_ignore_object(obj: Atspi.Accessible | None) -> bool:
        if obj is None:
            return True

        if Atspi.Accessible.get_role(obj) == Atspi.Role.TERMINAL:
            return True

        app = Atspi.Accessible.get_application(obj)
        if app and Atspi.Accessible.get_name(app) == "gnome-shell":
            return True

        return False

    def on_speech_output(self, output: SpeechOutput) -> SpeechOutputResult | None:
        if self._should_ignore_object(output.obj):
            return None

        words = output.text.split()
        if len(words) < 2:
            return None

        return SpeechOutputResult.replace(" ".join(reversed(words)))
```
