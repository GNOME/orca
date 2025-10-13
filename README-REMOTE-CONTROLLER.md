# Orca Remote Controller (D-Bus Interface)

> **⚠️⚠️ WORK IN PROGRESS**: This D-Bus interface is brand new and not yet feature complete.
Low-risk feature additions will continue to be made in version 49 point releases. More involved
features will be added only in version 50 and later. The API present in version 49.0 may be
modified beyond bug fixes in version 50 or later based on feedback from consumers of this support.
Such changes will be documented here.

[TOC]

## Overview

Orca exposes a D-Bus service at:

- **Service Name**: `org.gnome.Orca.Service`
- **Main Object Path**: `/org/gnome/Orca/Service`
- **Module Object Paths**: `/org/gnome/Orca/Service/ModuleName`
  (e.g., `/org/gnome/Orca/Service/SpeechAndVerbosityManager`)

See [REMOTE-CONTROLLER-COMMANDS.md](REMOTE-CONTROLLER-COMMANDS.md) for a complete
list of available commands.

## Dependencies

The D-Bus interface requires:

- **dasbus** - Python D-Bus library used by Orca for the remote controller implementation.
  ([Installation instructions](https://dasbus.readthedocs.io/en/latest/index.html))

## Service-Level Commands

Commands available directly on the main service (`/org/gnome/Orca/Service`):

### Get Orca's Version

```bash
gdbus call --session --dest org.gnome.Orca.Service \
    --object-path /org/gnome/Orca/Service \
    --method org.gnome.Orca.Service.GetVersion
```

**Returns:** String containing the version (and revision if available)

### Present a Custom Message in Speech and/or Braille

```bash
gdbus call --session --dest org.gnome.Orca.Service \
    --object-path /org/gnome/Orca/Service \
    --method org.gnome.Orca.Service.PresentMessage "Your message here"
```

**Parameters:**

- `message` (string): The message to present to the user

**Returns:** Boolean indicating success

### Show Orca's Preferences GUI

```bash
gdbus call --session --dest org.gnome.Orca.Service \
    --object-path /org/gnome/Orca/Service \
    --method org.gnome.Orca.Service.ShowPreferences
```

**Returns:** Boolean indicating success

### Quit Orca

```bash
gdbus call --session --dest org.gnome.Orca.Service \
    --object-path /org/gnome/Orca/Service \
    --method org.gnome.Orca.Service.Quit
```

**Returns:** Boolean indicating if the quit request was accepted

### List Available Service Commands

```bash
gdbus call --session --dest org.gnome.Orca.Service \
    --object-path /org/gnome/Orca/Service \
    --method org.gnome.Orca.Service.ListCommands
```

**Returns:** List of (command_name, description) tuples

### List Registered Modules

```bash
gdbus call --session --dest org.gnome.Orca.Service \
    --object-path /org/gnome/Orca/Service \
    --method org.gnome.Orca.Service.ListModules
```

**Returns:** List of module names

## Interacting with Modules

Each registered module exposes its own set of operations. Based on the underlying Orca code, these
are categorized as **Commands**, **Runtime Getters**, and **Runtime Setters**:

- **Commands**: Actions that perform a task. These typically correspond to Orca commands bound
  to a keystroke (e.g., `IncreaseRate`).
- **Runtime Getters**: Operations that retrieve the current value of an item, often a setting
  (e.g., `GetRate`).
- **Runtime Setters**: Operations that set the current value of an item, often a setting
  (e.g., `SetRate`). Note that setting a value does NOT cause it to become permanently saved.

You can discover and execute these for each module.

### Discovering Module Capabilities

#### List Commands for a Module

```bash
gdbus call --session --dest org.gnome.Orca.Service \
    --object-path /org/gnome/Orca/Service/ModuleName \
    --method org.gnome.Orca.Module.ListCommands
```

Replace `ModuleName` with an actual module name from `ListModules`.

**Returns:** List of (command_name, description) tuples.

#### List Parameterized Commands for a Module

```bash
gdbus call --session --dest org.gnome.Orca.Service \
    --object-path /org/gnome/Orca/Service/ModuleName \
    --method org.gnome.Orca.Module.ListParameterizedCommands
```

Replace `ModuleName` with an actual module name from `ListModules`.

**Returns:** List of (command_name, description, parameters) tuples, where `parameters` is a
list of (parameter_name, parameter_type) tuples.

**Example output:**

```bash
([('GetVoicesForLanguage',
   'Returns a list of available voices for the specified language.',
   [('language', 'str'), ('variant', 'str'), ('notify_user', 'bool')])],)
```

#### List Runtime Getters for a Module

```bash
gdbus call --session --dest org.gnome.Orca.Service \
    --object-path /org/gnome/Orca/Service/ModuleName \
    --method org.gnome.Orca.Module.ListRuntimeGetters
```

Replace `ModuleName` with an actual module name from `ListModules`.

**Returns:** List of (getter_name, description) tuples.

#### List Runtime Setters for a Module

```bash
gdbus call --session --dest org.gnome.Orca.Service \
    --object-path /org/gnome/Orca/Service/ModuleName \
    --method org.gnome.Orca.Module.ListRuntimeSetters
```

Replace `ModuleName` with an actual module name from `ListModules`.

**Returns:** List of (setter_name, description) tuples.

### Executing Module Operations

#### Execute a Runtime Getter

```bash
gdbus call --session --dest org.gnome.Orca.Service \
    --object-path /org/gnome/Orca/Service/ModuleName \
    --method org.gnome.Orca.Module.ExecuteRuntimeGetter 'PropertyName'
```

**Parameters:**

- `PropertyName` (string): The name of the runtime getter to execute.

**Returns:** The value returned by the getter as a GLib variant (type depends on the getter).

##### Example: Get the current speech rate

```bash
gdbus call --session --dest org.gnome.Orca.Service \
    --object-path /org/gnome/Orca/Service/SpeechAndVerbosityManager \
    --method org.gnome.Orca.Module.ExecuteRuntimeGetter 'Rate'

```

This will return the rate as a GLib Variant.

#### Execute a Runtime Setter

```bash
gdbus call --session --dest org.gnome.Orca.Service \
    --object-path /org/gnome/Orca/Service/ModuleName \
    --method org.gnome.Orca.Module.ExecuteRuntimeSetter 'PropertyName' <value>
```

**Parameters:**

- `PropertyName` (string): The name of the runtime setter to execute.
- `<value>`: The value to set, as a GLib variant (type depends on the setter).

**Returns:** Boolean indicating success.

##### Example: Set the current speech rate

```bash
gdbus call --session --dest org.gnome.Orca.Service \
    --object-path /org/gnome/Orca/Service/SpeechAndVerbosityManager \
    --method org.gnome.Orca.Module.ExecuteRuntimeSetter 'Rate' '<90>'
```

#### Execute a Module Command

```bash
# With user notification
gdbus call --session --dest org.gnome.Orca.Service \
    --object-path /org/gnome/Orca/Service/ModuleName \
    --method org.gnome.Orca.Module.ExecuteCommand 'CommandName' true

# Without user notification (silent)
gdbus call --session --dest org.gnome.Orca.Service \
    --object-path /org/gnome/Orca/Service/ModuleName \
    --method org.gnome.Orca.Module.ExecuteCommand 'CommandName' false
```

**Parameters (both required):**

- `CommandName` (string): The name of the command to execute
- `notify_user` (boolean): Whether to notify the user of the action (see section below)

**Returns:** Boolean indicating success

#### Execute a Parameterized Command

```bash
gdbus call --session --dest org.gnome.Orca.Service \
    --object-path /org/gnome/Orca/Service/ModuleName \
    --method org.gnome.Orca.Module.ExecuteParameterizedCommand 'CommandName' \
    '{"param1": <"value1">, "param2": <"value2">}' false
```

**Parameters:**

- `CommandName` (string): The name of the parameterized command to execute
- `parameters` (dict): Dictionary of parameter names and values as GLib variants
- `notify_user` (boolean): Whether to notify the user of the action

**Returns:** The result returned by the command as a GLib variant (type depends on the command)

##### Example: Get voices for a specific language

```bash
gdbus call --session --dest org.gnome.Orca.Service \
    --object-path /org/gnome/Orca/Service/SpeechAndVerbosityManager \
    --method org.gnome.Orca.Module.ExecuteParameterizedCommand 'GetVoicesForLanguage' \
    '{"language": <"en-us">, "variant": <"">}' false
```

This will return a list of available voices for US English.

### User Notification Applicability

**Setting `notify_user=true` is not a guarantee that feedback will be presented.**

Some commands inherently don't make sense to announce. For example:

```bash
# This command should simply stop speech, not announce that it is stopping speech.
gdbus call --session --dest org.gnome.Orca.Service \
    --object-path /org/gnome/Orca/Service/SpeechAndVerbosityManager \
    --method org.gnome.Orca.Module.ExecuteCommand 'InterruptSpeech' true
```

In those cases Orca will ingore the value of `notify_user`.

**Setting `notify_user=false` is not a guarantee that Orca will remain silent**, though for the
most part Orca will try to respect this value. The exceptions are:

1. If excecuting the command has resulted in UI being shown, such as a dialog or menu, the
   newly-shown UI will be presented in speech and/or braille based on the user's settings.
   Failure to announce that the user has been removed from one window and placed in another
   could be extremely confusing.
2. If the *sole* purpose of the command is to announce something without making any other
   changes, e.g. `PresentTime`, executing it with `notify_user=false` makes no sense. Adding
   checks and early returns to handle this possibility does not seem worth doing. If you
   don't want Orca to present the time, don't ask Orca to present the time. 😃

### Navigator Module "Enabled" State Applicability

**In the Remote Controller, Navigator commands are expected to work even when not "enabled."**

Some of Orca's Navigator modules, namely Table Navigator, Caret Navigator, and Structural Navigator,
have an "enabled" state. The reason for this is very much tied to the keyboard-centric nature of
Orca's commands. For instance, if Orca always grabbed "H" (for heading navigation) and the arrow
keys (for caret navigation), normal interaction with applications would be completely broken. For
this reason, Navigator modules whose commands will prevent normal, native interaction with
applications are typically not enabled by default and can be easily disabled.

In contrast, performing Navigator commands via D-Bus does not prevent native interaction with
applications. For instance, one could use the Remote Controller to move to the next heading without
causing H to stop functioning in editable fields. For this reason, and to avoid a performance hit,
the decision was made to not check if (keyboard-centric) navigation commands were enabled. As a
result, it should be possible to use Remote Controller navigation even in "focus mode" or other
cases where Orca is not controlling the caret. This is by design.

Given the keyboard-centric nature of Orca's commands, there may be instances in which one uses the
Remote Controller for navigation and Orca fails to correctly update its location in response. If
Orca correctly updates its location when the same navigation command is executed via keyboard,
please report the Remote Controller failure as a new bug in Orca's gitlab.

### The "Stickiness" (or Lack Thereof) of On-The-Fly Settings Changes

Orca has a number of keyboard commands to temporarily change settings such as speech rate, pitch,
volume; capitalization style; punctuation level; etc., etc. The question is: how long should
on-the-fly modifications to settings persist?

Early on in Orca's development, the conclusion was that on-the-fly settings changes should be
seen as quite temporary, presumed to be used to address a specific one-time need. For instance,
if reading some difficult-to-understand text, one might want to reduce the speed just for that text.
If one were doing a final proofread of some content, one might want to briefly set the punctuation
level to all. If one needs slow speed and/or verbose punctuation all the time, those should be set
in Orca's Preferences dialogs -- either globally or on a per-app basis. Orca also has a profile
feature through which the user can save settings and quickly load/unload them by switching profiles*.

Whether or not that historical decision was the right decision goes beyond the scope of the
Remote Controller. The primary purpose of the Remote Controller is to provide D-Bus access to
commands and runtime settings as if they were performed by the user via keyboard command. Thus if
a setting changed via Remote Controller persists (or fails to persist) in the same way as when
changed via keyboard command, it is not a Remote Controller bug. (It may be a general Orca
bug or feature request, and you are encouraged to file it as such.) On the other hand, if the
behavior of the Remote Controller differs from that of the corresponding or related keyboard
command, please report that Remote Controller failure as a new bug in Orca's gitlab.

\* *Note: Remote Controller support for profile management is still pending.*
