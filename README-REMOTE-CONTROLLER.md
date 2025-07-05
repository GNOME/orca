# Orca Remote Controller (D-Bus Interface)

> **⚠️⚠️ WORK IN PROGRESS**: This D-Bus interface is in its very early stages, and under active
development. It should be considered **highly unstable**. The API may change significantly
before the final release. **Do not rely on this interface for production applications until
Orca v49.0 is released.**

[TOC]

## Overview

Orca exposes a D-Bus service at:

- **Service Name**: `org.gnome.Orca.Service`
- **Main Object Path**: `/org/gnome/Orca/Service`
- **Module Object Paths**: `/org/gnome/Orca/Service/ModuleName`
  (e.g., `/org/gnome/Orca/Service/SpeechAndVerbosityManager`)

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

### Please Note

**Setting `notify_user=true` is not a guarantee that feedback will be presented.** Some commands
inherently don't make sense to announce. For example:

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

## TODO

- Add support for more commands, getters, and setters.
- Fix bugs, of which there are undoubtedly many.
