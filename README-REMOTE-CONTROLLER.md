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

## Module Commands

Each registered module exposes its own set of commands:

### List Commands for a Module

```bash
gdbus call --session --dest org.gnome.Orca.Service \
    --object-path /org/gnome/Orca/Service/ModuleName \
    --method org.gnome.Orca.Module.ListCommands
```

Replace `ModuleName` with an actual module name from `ListModules`.

**Returns:** List of (command_name, description) tuples

### Execute a Module Command

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

**Setting `notify_user=false` is a guarantee that Orca will remain silent.** If Orca provides any
feedback when `notify_user=false`, it should be considered a bug.

## TODO

- Add more speech configuration commands to the SpeechAndVerbosityManager module.
- Progressively expose all of Orca's commands via the remote controller interface.
- Fix bugs, of which there are undoubtedly many.
