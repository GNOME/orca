# User Extensions

## Status

This feature is early and experimental. The following are still pending:

- Preferences UI for extension-specific settings (user extensions can be
  approved, revoked, enabled, and disabled in Orca's Preferences window, but
  cannot yet provide their own settings pages)
- Fixing bugs and improving the API based on user feedback.

## Overview

User extensions allow you to add custom behavior to Orca, including keyboard
commands and speech output hooks. An extension contains a class that subclasses
`Extension`.

Extensions live in `~/.local/share/orca/extensions/`. Orca supports both
single-file extensions and package extensions:

```text
~/.local/share/orca/extensions/hello_world.py
~/.local/share/orca/extensions/reverse_words/__init__.py
```

Each `.py` file or package directory with an `__init__.py` file containing an
`Extension` subclass is a potential extension.

## Approving Extensions

For security, extensions must be approved before Orca will load them. When Orca
discovers an unapproved extension, it logs the extension's SHA256 hash.

Use the User Extensions page in Orca's Preferences window to approve,
re-approve, or revoke user extensions. The page computes the extension's SHA256
hash and persists the approval in dconf. This is the recommended way to manage
approval.

Approval and revocation can also be done via the command line:

```sh
# Approve an extension:
orca --approve-extension my_extension.py
orca --approve-extension my_package

# Revoke approval:
orca --revoke-extension my_extension.py
orca --revoke-extension my_package
```

These commands compute the extension's SHA256 hash and persist the approval in
dconf. For package extensions, Orca computes the hash from the package contents.
Extensions approved from the command line will be loaded on the next Orca
startup.

If you edit an approved extension, its hash changes and Orca will not load it
until you re-approve it from the User Extensions preferences page or the command
line. If you delete an extension file or package directory, its approval entry
remains but has no effect. There is currently no automatic cleanup of stale
approvals.

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

- `DESCRIPTION`: A short description shown in Orca's User Extensions
  preferences page and extension information dialog.
- `VERSION`: Version string shown in the extension information dialog.
- `AUTHOR`: Author string shown in the extension information dialog.
- `ORGANIZATION`: Organization string shown in the extension information
  dialog.
- `COPYRIGHT`: Copyright holder or notice shown in the extension information
  dialog.
- `WEBSITE`: Website shown in the extension information dialog.

Metadata is read from the extension class without executing the extension.
Simple string constants are supported. The User Extensions page includes an
Info button for each extension that displays this metadata.

### Command Functions

Command functions take no arguments (other than `self`) and return `True` when
handled. The base class automatically wraps them to be compatible with Orca's
internal command dispatch.

### Shutdown Hook

Override `on_shutdown()` if your extension needs to clean up when Orca exits:

```python
def on_shutdown(self) -> None:
    self._stop_background_worker()
```

Shutdown hooks must return quickly. Orca starts all loaded user-extension
shutdown hooks, waits up to half a second total for them to finish, then
continues shutting down so an extension cannot block shutdown.
Shutdown hooks should only do local cleanup, such as stopping background
workers or closing files. They should not present messages, invoke speech or
braille commands, start services, or do network work. Orca has already
presented "Screen reader off" before calling these hooks and is in the process
of shutting down.

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

## Extension Settings

User extensions can store simple settings using `self.settings`. This is the
supported API for extension settings; extensions should not use Orca's
`gsettings_registry` module directly. Settings belong to the extension that
creates them and are stored in Orca's active profile.

Supported setting values are booleans, integers, floats, strings, lists of
strings, and dictionaries whose keys are strings and whose values are booleans,
integers, floats, or strings. Setting keys must be simple names containing only
letters, numbers, underscores, hyphens, or periods.

Use `get()` when deciding what your extension should do. Always pass a default
unless `None` is meaningful for that setting:

```python
scope = self.settings.get("scope", default="objects")
```

Extension settings do not have registered per-key defaults. If a stored value
does not exist, `get()` returns the default passed by the caller, or `None` if no
default is provided.

Use `set()` and `reset()` from extension code when the extension needs to change
its own settings:

```python
self.settings.set("scope", "both")
self.settings.reset("scope")
```

`reset()` removes the stored value; it does not write the default.

### Testing Settings With dconf

Until preferences UI support for extension settings is available, extension
authors may find it useful to test settings with `dconf`. Orca stores each user
extension's settings in its own path:

```sh
dconf read /org/gnome/orca/default/extensions/hello-world/settings
```

When using `dconf write`, include any existing values for that extension that
you want to keep. The command replaces the settings dictionary for the extension
path being written.

For example, to test the command example below with alternative messages and rates:

```sh
dconf write /org/gnome/orca/default/extensions/hello-world/settings \
    "{'greeting-message': <'Very slow hello'>, 'goodbye-message': <'Very fast goodbye'>, 'slow-rate': <5>, 'fast-rate': <90>}"
```

And to test the reverse-words example with messages only:

```sh
dconf write /org/gnome/orca/default/extensions/reverse-words/settings \
    "{'scope': <'messages'>}"
```

Because message speech has no accessible object, application and role filters
are not relevant when `scope` is `"messages"` and can thus be left out.

To reset an extension's settings:

```sh
dconf reset /org/gnome/orca/default/extensions/reverse-words/settings
```

## The Controller API

Command extensions can use the remote controller, available as
`self.controller` on the `Extension` base class. The controller provides access
to all of Orca's settings and its commands, both bound and unbound.

The following in-process "internal" wrappers should be used in user extensions
to avoid making actual D-Bus calls:

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
    DESCRIPTION = "Adds greeting and voice-info commands."
    VERSION = "1.0"
    AUTHOR = "Extension Author"
    ORGANIZATION = "Example, Inc."
    COPYRIGHT = "2026 Example, Inc."
    WEBSITE = "https://example.com/hello-world"

    def _get_greeting_message(self) -> str:
        return self.settings.get("greeting-message", default="Hello, world!")

    def _get_goodbye_message(self) -> str:
        return self.settings.get("goodbye-message", default="Goodbye, world!")

    def _get_slow_rate(self) -> int:
        return self.settings.get("slow-rate", default=20)

    def _get_fast_rate(self) -> int:
        return self.settings.get("fast-rate", default=90)

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
        self.controller.set_value_internal(
            "SpeechManager", "Rate", self._get_slow_rate()
        )
        self.controller.present_message_internal(self._get_greeting_message())
        self.controller.set_value_internal("SpeechManager", "Rate", original_rate)
        return True

    def say_goodbye_fast(self):
        """Increases the speech rate, says goodbye, then restores it."""

        original_rate = self.controller.get_value_internal("SpeechManager", "Rate")
        self.controller.set_value_internal(
            "SpeechManager", "Rate", self._get_fast_rate()
        )
        self.controller.present_message_internal(self._get_goodbye_message())
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
            f"Greeting message: {self._get_greeting_message()}",
            f"Goodbye message: {self._get_goodbye_message()}",
            f"Slow rate: {self._get_slow_rate()}",
            f"Fast rate: {self._get_fast_rate()}",
        ]
        self.controller.present_message_internal(". ".join(parts))
        return True
```

## Modal Input Handling

Extensions can temporarily observe input events for which Orca has a key grab
by becoming Orca's modal input handler. This is useful when an extension has a
mode in which it needs to observe, consume, or pass through Orca commands before
they are executed.

User extensions must not grab the keyboard. Keyboard grabs are difficult to get
right and can prevent the user from controlling their session. Instead, register
normal commands for keys your extension needs. Use modal input handling only for
events bound to another Orca command that your extension temporarily needs to
override.

If a modal input handler is active, when Orca receives an input event for which
there is a key grab, Orca calls two methods on the handler:

- `will_handle_event(script, event, command)`: Return `True` to claim the
  event, or `False` to leave it to Orca's normal event processing. The
  `command` argument is the Orca command matched to the event, or `None` if no
  command matched.
- `handle_event(script, event, command)`: Handle an event that was claimed by
  `will_handle_event()`.

Only one modal input handler can be active at a time. User extension modal
handlers cannot replace another active modal handler. Orca's own modal handlers
can replace a user extension modal handler when needed, for instance when an
Orca command starts a built-in modal feature. When your mode starts, call
`command_manager.get_manager().set_modal_handler(self)`. If it returns `False`,
another modal handler is active and your extension should not enter its mode.
When your mode ends, call `clear_modal_handler(self)`. Orca only clears the
handler if it still belongs to your extension.

To pass a command through after observing it, call `command.execute(script,
event)`. To consume a command, return `True` without executing the command.

### Modal Command Observer Example

This example toggles a modal command observer with Orca+Shift+F2. When enabled,
it consumes Orca+E regardless of the command currently bound to that keystroke.
It presents other commands it sees and then passes them through.

```python
"""Example extension demonstrating modal command observation."""

from orca import command_manager, keybindings
from orca.command import Command, KeyboardCommand
from orca.extension import Extension


class ModalCommandObserver(Extension):
    """Observes and optionally consumes Orca commands while enabled."""

    GROUP_LABEL = "Modal Command Observer"
    DESCRIPTION = "Demonstrates observing, passing through, and consuming commands."
    VERSION = "1.0"
    AUTHOR = "Extension Author"
    ORGANIZATION = "Example, Inc."
    COPYRIGHT = "2026 Example, Inc."
    WEBSITE = "https://example.com/modal-command-observer"

    def __init__(self) -> None:
        self._enabled = False
        super().__init__()

    def _get_commands(self) -> list[Command]:
        return [
            KeyboardCommand(
                "toggle_modal_command_observer",
                self.toggle_observer,
                self.GROUP_LABEL,
                "Toggles modal command observation",
                desktop_keybinding=keybindings.KeyBinding(
                    "F2", keybindings.ORCA_SHIFT_MODIFIER_MASK,
                ),
                laptop_keybinding=keybindings.KeyBinding(
                    "F2", keybindings.ORCA_SHIFT_MODIFIER_MASK,
                ),
            ),
        ]

    def toggle_observer(self) -> bool:
        manager = command_manager.get_manager()

        if not self._enabled:
            if not manager.set_modal_handler(self):
                self.controller.present_message_internal(
                    "Another modal input handler is active."
                )
                return True
            self._enabled = True
            self.controller.present_message_internal("Modal command observer enabled.")
            return True

        manager.clear_modal_handler(self)
        self._enabled = False
        self.controller.present_message_internal("Modal command observer disabled.")
        return True

    def will_handle_event(self, script, event, command=None) -> bool:
        if not self._enabled:
            return False

        if not event.is_pressed_key():
            return False

        if self._is_consumed_event(event):
            return True

        return command is not None and command.get_name() != (
            "toggle_modal_command_observer"
        )

    def handle_event(self, script, event, command=None) -> bool:
        if self._is_consumed_event(event):
            self.controller.present_message_internal("I am consuming Orca+E.")
            return True

        if command is None:
            return False

        description = command.get_description() or command.get_name()
        self.controller.present_message_internal(
            f"I see you want to use {description}. Ok."
        )
        return command.execute(script, event)

    def _is_consumed_event(self, event) -> bool:
        return keybindings.KeyBinding("e", keybindings.ORCA_MODIFIER_MASK).matches(
            event.id, event.hw_code, event.modifiers
        )
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

This silly example lets you test the hook locally. It reverses what Orca speaks
based on extension settings. By default it applies to speech associated with
accessible objects, skips messages, skips terminals, and skips gnome-shell.
The `scope` setting can be `"objects"`, `"messages"`, `"both"`, or `"none"`.
The `excluded-applications` setting is a list of application names. The
`excluded-roles` setting is a dictionary whose values are integer-backed AT-SPI
roles. Application and role filters are only used for speech associated with an
accessible object; messages do not have an object.

Create this as a package extension in
`~/.local/share/orca/extensions/reverse_words/__init__.py`.

```python
"""Example extension that reverses the order of spoken words."""

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from orca.extension import Extension, SpeechOutput, SpeechOutputResult


class ReverseWords(Extension):
    """Reverses word order before Orca sends speech to the synthesizer."""

    GROUP_LABEL = "Reverse Words"
    DESCRIPTION = "Reverses spoken word order for testing speech hooks."
    VERSION = "1.0"
    AUTHOR = "Extension Author"
    ORGANIZATION = "Example, Inc."
    COPYRIGHT = "2026 Example, Inc."
    WEBSITE = "https://example.com/reverse-words"

    def _applies_to_message(self) -> bool:
        scope = self.settings.get("scope", default="objects")
        return scope in ("messages", "both")

    def _applies_to_object(self, obj: Atspi.Accessible | None) -> bool:
        if obj is None:
            return False

        scope = self.settings.get("scope", default="objects")
        if scope not in ("objects", "both"):
            return False

        app = Atspi.Accessible.get_application(obj)
        app_name = Atspi.Accessible.get_name(app) if app else ""
        excluded_apps = self.settings.get(
            "excluded-applications",
            default=["gnome-shell"],
        )
        if app_name in excluded_apps:
            return False

        role = Atspi.Accessible.get_role(obj)
        excluded_roles = self.settings.get(
            "excluded-roles",
            default={"terminal": int(Atspi.Role.TERMINAL)},
        )
        role_values = {int(value) for value in excluded_roles.values()}
        if int(role) in role_values:
            return False

        return True

    def _should_process(self, output: SpeechOutput) -> bool:
        if output.obj is None:
            return self._applies_to_message()
        return self._applies_to_object(output.obj)

    def on_speech_output(self, output: SpeechOutput) -> SpeechOutputResult | None:
        if not self._should_process(output):
            return None

        words = output.text.split()
        if len(words) < 2:
            return None

        return SpeechOutputResult.replace(" ".join(reversed(words)))
```
