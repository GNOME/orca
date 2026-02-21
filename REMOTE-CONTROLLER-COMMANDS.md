# Orca D-Bus Service Commands Reference

This document lists all commands (215), runtime getters (143), and runtime setters (133) available
via Orca's D-Bus Remote Controller interface.

The service can be accessed at:

- **Service Name:** `org.gnome.Orca.Service`
- **Main Object Path:** `/org/gnome/Orca/Service`
- **Module Object Paths:** `/org/gnome/Orca/Service/ModuleName`

Additional information about using the remote controller can be found in [README-REMOTE-CONTROLLER.md](README-REMOTE-CONTROLLER.md).

---

## Service-Level Commands

These commands are available directly on the main service object at `/org/gnome/Orca/Service`.

- **`GetVersion`:** Returns Orca's version and revision if available.
- **`ListCommands`:** Returns available commands on the main service interface.
- **`ListModules`:** Returns a list of registered module names.
- **`PresentMessage`:** Presents message to the user.
- **`Quit`:** Quits Orca. Returns True if the quit request was accepted.
- **`ShowPreferences`:** Shows Orca's preferences GUI.

---

## Modules

Each module exposes commands, getters, and setters on its object at `/org/gnome/Orca/Service/ModuleName`.

### ActionPresenter

**Object Path:** `/org/gnome/Orca/Service/ActionPresenter`

#### Commands

**Method:** `org.gnome.Orca.Module.ExecuteCommand`

**Parameters:** `CommandName` (string), [`NotifyUser`](README-REMOTE-CONTROLLER.md#user-notification-applicability) (boolean)

- **`ShowActionsList`:** Shows a list of all the accessible actions exposed by the focused object.

---

### BraillePresenter

**Object Path:** `/org/gnome/Orca/Service/BraillePresenter`

#### Commands

**Method:** `org.gnome.Orca.Module.ExecuteCommand`

**Parameters:** `CommandName` (string), [`NotifyUser`](README-REMOTE-CONTROLLER.md#user-notification-applicability) (boolean)

- **`ToggleMonitor`:** Toggles the braille monitor on and off.

#### Settings

**Methods:** `org.gnome.Orca.Module.ExecuteRuntimeGetter` / `org.gnome.Orca.Module.ExecuteRuntimeSetter`

**Parameters:** `PropertyName` (string), `Value` (variant, setter only)

- **`AvailableContractionTables`:** Returns a list of available contraction table names. (getter only)
- **`BrailleIsEnabled`:** Gets/Sets whether braille is enabled.
- **`BrailleProgressBarUpdates`:** Gets/Sets whether braille progress bar updates are enabled.
- **`ComputerBrailleAtCursorIsEnabled`:** Gets/Sets whether computer braille is used at the cursor position.
- **`ContractedBrailleIsEnabled`:** Gets/Sets whether contracted braille is enabled.
- **`ContractionTable`:** Gets/Sets the current braille contraction table.
- **`DisplayAncestors`:** Gets/Sets whether ancestors of the current object will be displayed.
- **`EndOfLineIndicatorIsEnabled`:** Gets/Sets whether the end-of-line indicator is enabled.
- **`FlashMessageDuration`:** Gets/Sets flash message duration in milliseconds.
- **`FlashMessagesAreDetailed`:** Gets/Sets whether 'flash' messages are detailed (as opposed to brief).
- **`FlashMessagesAreEnabled`:** Gets/Sets whether 'flash' messages (i.e. announcements) are enabled.
- **`FlashMessagesArePersistent`:** Gets/Sets whether 'flash' messages are persistent (as opposed to temporary).
- **`LinkIndicator`:** Gets/Sets the braille link indicator style.
- **`MonitorBackground`:** Gets/Sets the braille monitor background color.
- **`MonitorCellCount`:** Gets/Sets the braille monitor cell count.
- **`MonitorForeground`:** Gets/Sets the braille monitor foreground color.
- **`MonitorIsEnabled`:** Gets/Sets whether the braille monitor is enabled.
- **`MonitorShowDots`:** Gets/Sets whether the braille monitor shows Unicode braille dots.
- **`PresentMnemonics`:** Gets/Sets whether mnemonics are presented on the braille display.
- **`ProgressBarBrailleInterval`:** Gets/Sets the braille progress bar update interval in seconds.
- **`ProgressBarBrailleVerbosity`:** Gets/Sets the braille progress bar verbosity level.
- **`RolenameStyle`:** Gets/Sets the current rolename style for object presentation.
- **`SelectorIndicator`:** Gets/Sets the braille selector indicator style.
- **`TextAttributesIndicator`:** Gets/Sets the braille text attributes indicator style.
- **`VerbosityLevel`:** Gets/Sets the braille verbosity level for object presentation.
- **`WordWrapIsEnabled`:** Gets/Sets whether braille word wrap is enabled.

---

### CaretNavigator

**Object Path:** `/org/gnome/Orca/Service/CaretNavigator`

#### Commands

**Method:** `org.gnome.Orca.Module.ExecuteCommand`

**Parameters:** `CommandName` (string), [`NotifyUser`](README-REMOTE-CONTROLLER.md#user-notification-applicability) (boolean)

- **`NextCharacter`:** Moves to the next character.
- **`PreviousCharacter`:** Moves to the previous character.
- **`NextWord`:** Moves to the next word.
- **`PreviousWord`:** Moves to the previous word.
- **`NextLine`:** Moves to the next line.
- **`StartOfLine`:** Moves to the start of the line.
- **`EndOfLine`:** Moves to the end of the line.
- **`PreviousLine`:** Moves to the previous line.
- **`StartOfFile`:** Moves to the start of the file.
- **`EndOfFile`:** Moves to the end of the file.
- **`ToggleEnabled`:** Toggles caret navigation.
- **`ToggleLayoutMode`:** Switches between object mode and layout mode for line presentation.

#### Settings

**Methods:** `org.gnome.Orca.Module.ExecuteRuntimeGetter` / `org.gnome.Orca.Module.ExecuteRuntimeSetter`

**Parameters:** `PropertyName` (string), `Value` (variant, setter only)

- **`IsEnabled`:** Gets/Sets whether caret navigation is enabled.
- **`LayoutMode`:** Gets/Sets whether layout mode is enabled.
- **`TriggersFocusMode`:** Gets/Sets whether caret navigation triggers focus mode.

---

### ChatPresenter

**Object Path:** `/org/gnome/Orca/Service/ChatPresenter`

#### Commands

**Method:** `org.gnome.Orca.Module.ExecuteCommand`

**Parameters:** `CommandName` (string), [`NotifyUser`](README-REMOTE-CONTROLLER.md#user-notification-applicability) (boolean)

- **`PresentNextMessage`:** Navigate to and present the next chat message in the history.
- **`PresentPreviousMessage`:** Navigate to and present the previous chat message in the history.
- **`ToggleBuddyTyping`:** Toggles whether we announce when our buddies are typing a message.
- **`ToggleMessageHistories`:** Toggles whether we provide chat room specific message histories.
- **`TogglePrefix`:** Toggles whether we prefix chat room messages with the name of the chat room.

#### Settings

**Methods:** `org.gnome.Orca.Module.ExecuteRuntimeGetter` / `org.gnome.Orca.Module.ExecuteRuntimeSetter`

**Parameters:** `PropertyName` (string), `Value` (variant, setter only)

- **`AnnounceBuddyTyping`:** Gets/Sets whether to announce when buddies are typing.
- **`MessageVerbosity`:** Gets/Sets the chat message verbosity setting.
- **`RoomHistories`:** Gets/Sets whether to provide chat room specific message histories.
- **`SpeakRoomName`:** Gets/Sets whether to speak the chat room name.
- **`SpeakRoomNameLast`:** Gets/Sets whether to speak the chat room name after the message.

---

### ClipboardPresenter

**Object Path:** `/org/gnome/Orca/Service/ClipboardPresenter`

#### Commands

**Method:** `org.gnome.Orca.Module.ExecuteCommand`

**Parameters:** `CommandName` (string), [`NotifyUser`](README-REMOTE-CONTROLLER.md#user-notification-applicability) (boolean)

- **`PresentClipboardContents`:** Presents the clipboard contents.

---

### CommandManager

**Object Path:** `/org/gnome/Orca/Service/CommandManager`

#### Commands

**Method:** `org.gnome.Orca.Module.ExecuteCommand`

**Parameters:** `CommandName` (string), [`NotifyUser`](README-REMOTE-CONTROLLER.md#user-notification-applicability) (boolean)

- **`ToggleKeyboardLayout`:** Toggles between desktop and laptop keyboard layout.

#### Settings

**Methods:** `org.gnome.Orca.Module.ExecuteRuntimeGetter` / `org.gnome.Orca.Module.ExecuteRuntimeSetter`

**Parameters:** `PropertyName` (string), `Value` (variant, setter only)

- **`KeyboardLayoutIsDesktop`:** Gets/Sets whether the keyboard layout is desktop (True) or laptop (False).

---

### DocumentPresenter

**Object Path:** `/org/gnome/Orca/Service/DocumentPresenter`

#### Commands

**Method:** `org.gnome.Orca.Module.ExecuteCommand`

**Parameters:** `CommandName` (string), [`NotifyUser`](README-REMOTE-CONTROLLER.md#user-notification-applicability) (boolean)

- **`EnableStickyBrowseMode`:** Enables sticky browse mode.
- **`EnableStickyFocusMode`:** Enables sticky focus mode.
- **`TogglePresentationMode`:** Switches between browse mode and focus mode (user-initiated).

#### Settings

**Methods:** `org.gnome.Orca.Module.ExecuteRuntimeGetter` / `org.gnome.Orca.Module.ExecuteRuntimeSetter`

**Parameters:** `PropertyName` (string), `Value` (variant, setter only)

- **`AutoStickyFocusModeForWebApps`:** Gets/Sets whether to auto-detect web apps and enable sticky focus mode.
- **`BrowseModeIsSticky`:** Returns True if browse mode is active and 'sticky' (web content only). (getter only)
- **`FindResultsMinimumLength`:** Gets/Sets the minimum length for find results to be spoken.
- **`FocusModeIsSticky`:** Returns True if focus mode is active and 'sticky' (web content only). (getter only)
- **`InFocusMode`:** Returns True if focus mode is active (web content only). (getter only)
- **`NativeNavTriggersFocusMode`:** Gets/Sets whether native navigation triggers focus mode.
- **`OnlySpeakChangedLines`:** Gets/Sets whether to only speak changed lines during find.
- **`PageSummaryOnLoad`:** Gets/Sets whether to present a page summary when a document loads.
- **`SayAllOnLoad`:** Gets/Sets whether to perform say all when a document loads.
- **`SpeakFindResults`:** Gets/Sets whether to speak find results.

---

### FlatReviewPresenter

**Object Path:** `/org/gnome/Orca/Service/FlatReviewPresenter`

#### Commands

**Method:** `org.gnome.Orca.Module.ExecuteCommand`

**Parameters:** `CommandName` (string), [`NotifyUser`](README-REMOTE-CONTROLLER.md#user-notification-applicability) (boolean)

- **`GoAbove`:** Moves to the character above.
- **`GoBelow`:** Moves to the character below.
- **`GoBottomLeft`:** Moves to the bottom left of the current window.
- **`GoEnd`:** Moves to the bottom right of the current window.
- **`GoEndOfLine`:** Moves to the end of the line.
- **`GoHome`:** Moves to the top left of the current window.
- **`GoNextCharacter`:** Moves to the next character.
- **`GoNextItem`:** Moves to the next item or word.
- **`GoNextLine`:** Moves to the next line.
- **`GoPreviousCharacter`:** Moves to the previous character.
- **`GoPreviousItem`:** Moves to the previous item or word.
- **`GoPreviousLine`:** Moves to the previous line.
- **`GoStartOfLine`:** Moves to the beginning of the current line.
- **`AppendToClipboard`:** Appends the string just presented to the clipboard.
- **`CopyToClipboard`:** Copies the string just presented to the clipboard.
- **`GetCurrentObject`:** Returns the current accessible object.
- **`LeftClickOnObject`:** Attempts to synthesize a left click on the current accessible.
- **`PhoneticItem`:** Presents the current word letter by letter phonetically.
- **`PhoneticLine`:** Presents the current line letter by letter phonetically.
- **`PresentCharacter`:** Presents the current character.
- **`PresentItem`:** Presents the current item/word.
- **`PresentLine`:** Presents the current line.
- **`PresentObject`:** Presents the current accessible object.
- **`RightClickOnObject`:** Attempts to synthesize a right click on the current accessible.
- **`RoutePointerToObject`:** Routes the mouse pointer to the current accessible.
- **`SayAll`:** Speaks the contents of the entire window.
- **`ShowContents`:** Displays the entire flat review contents in a text view.
- **`SpellCharacter`:** Presents the current character phonetically.
- **`SpellItem`:** Presents the current item/word letter by letter.
- **`SpellLine`:** Presents the current line letter by letter.
- **`ToggleFlatReviewMode`:** Toggles between flat review mode and focus tracking mode.
- **`ToggleRestrict`:** Toggles the restricting of flat review to the current object.
- **`UnicodeCurrentCharacter`:** Presents the current character's unicode value.

#### Settings

**Methods:** `org.gnome.Orca.Module.ExecuteRuntimeGetter` / `org.gnome.Orca.Module.ExecuteRuntimeSetter`

**Parameters:** `PropertyName` (string), `Value` (variant, setter only)

- **`IsRestricted`:** Gets/Sets whether flat review is restricted to the current object.

---

### NotificationPresenter

**Object Path:** `/org/gnome/Orca/Service/NotificationPresenter`

#### Commands

**Method:** `org.gnome.Orca.Module.ExecuteCommand`

**Parameters:** `CommandName` (string), [`NotifyUser`](README-REMOTE-CONTROLLER.md#user-notification-applicability) (boolean)

- **`PresentLastNotification`:** Presents the last notification.
- **`PresentNextNotification`:** Presents the next notification.
- **`PresentPreviousNotification`:** Presents the previous notification.
- **`ShowNotificationList`:** Opens a dialog with a list of the notifications.

---

### ObjectNavigator

**Object Path:** `/org/gnome/Orca/Service/ObjectNavigator`

#### Commands

**Method:** `org.gnome.Orca.Module.ExecuteCommand`

**Parameters:** `CommandName` (string), [`NotifyUser`](README-REMOTE-CONTROLLER.md#user-notification-applicability) (boolean)

- **`MoveToFirstChild`:** Moves the navigator focus to the first child of the current focus.
- **`MoveToNextSibling`:** Moves the navigator focus to the next sibling of the current focus.
- **`MoveToParent`:** Moves the navigator focus to the parent of the current focus.
- **`MoveToPreviousSibling`:** Moves the navigator focus to the previous sibling of the current focus.
- **`PerformAction`:** Attempts to click on the current focus.
- **`ToggleSimplify`:** Toggles simplified navigation.

---

### ProfileManager

**Object Path:** `/org/gnome/Orca/Service/ProfileManager`

#### Commands

**Method:** `org.gnome.Orca.Module.ExecuteCommand`

**Parameters:** `CommandName` (string), [`NotifyUser`](README-REMOTE-CONTROLLER.md#user-notification-applicability) (boolean)

- **`CycleSettingsProfile`:** Cycle through the user's existing settings profiles.
- **`PresentCurrentProfile`:** Present the name of the currently active profile.

#### Settings

**Methods:** `org.gnome.Orca.Module.ExecuteRuntimeGetter` / `org.gnome.Orca.Module.ExecuteRuntimeSetter`

**Parameters:** `PropertyName` (string), `Value` (variant, setter only)

- **`ActiveProfile`:** Gets/Sets the active profile by internal name.
- **`AvailableProfiles`:** Returns list of available profiles as [display_name, internal_name] pairs. (getter only)
- **`StartingProfile`:** No-op for backwards compatibility. Starting profile is always Default.

---

### SayAllPresenter

**Object Path:** `/org/gnome/Orca/Service/SayAllPresenter`

#### Commands

**Method:** `org.gnome.Orca.Module.ExecuteCommand`

**Parameters:** `CommandName` (string), [`NotifyUser`](README-REMOTE-CONTROLLER.md#user-notification-applicability) (boolean)

- **`FastForward`:** Jumps forward in the current Say All.
- **`Rewind`:** Jumps back in the current Say All.
- **`SayAll`:** Speaks the entire document or text, starting from the current position.

#### Settings

**Methods:** `org.gnome.Orca.Module.ExecuteRuntimeGetter` / `org.gnome.Orca.Module.ExecuteRuntimeSetter`

**Parameters:** `PropertyName` (string), `Value` (variant, setter only)

- **`AnnounceBlockquote`:** Gets/Sets whether blockquotes are announced when entered.
- **`AnnounceForm`:** Gets/Sets whether non-landmark forms are announced when entered.
- **`AnnounceGrouping`:** Gets/Sets whether groupings are announced when entered.
- **`AnnounceLandmark`:** Gets/Sets whether landmarks are announced when entered.
- **`AnnounceList`:** Gets/Sets whether lists are announced when entered.
- **`AnnounceTable`:** Gets/Sets whether tables are announced when entered.
- **`RewindAndFastForwardEnabled`:** Gets/Sets whether Up and Down can be used in Say All.
- **`StructuralNavigationEnabled`:** Gets/Sets whether structural navigation keys can be used in Say All.
- **`Style`:** Gets/Sets the current Say All style.

---

### SleepModeManager

**Object Path:** `/org/gnome/Orca/Service/SleepModeManager`

#### Commands

**Method:** `org.gnome.Orca.Module.ExecuteCommand`

**Parameters:** `CommandName` (string), [`NotifyUser`](README-REMOTE-CONTROLLER.md#user-notification-applicability) (boolean)

- **`ToggleSleepMode`:** Toggles sleep mode for the active application.

---

### SoundPresenter

**Object Path:** `/org/gnome/Orca/Service/SoundPresenter`

#### Settings

**Methods:** `org.gnome.Orca.Module.ExecuteRuntimeGetter` / `org.gnome.Orca.Module.ExecuteRuntimeSetter`

**Parameters:** `PropertyName` (string), `Value` (variant, setter only)

- **`BeepProgressBarUpdates`:** Gets/Sets whether beep progress bar updates are enabled.
- **`ProgressBarBeepInterval`:** Gets/Sets the beep progress bar update interval in seconds.
- **`ProgressBarBeepVerbosity`:** Gets/Sets the beep progress bar verbosity level.
- **`SoundIsEnabled`:** Gets/Sets whether sound is enabled.
- **`SoundVolume`:** Gets/Sets the sound volume (0.0 to 1.0).

---

### SpeechManager

**Object Path:** `/org/gnome/Orca/Service/SpeechManager`

#### Commands

**Method:** `org.gnome.Orca.Module.ExecuteCommand`

**Parameters:** `CommandName` (string), [`NotifyUser`](README-REMOTE-CONTROLLER.md#user-notification-applicability) (boolean)

- **`CycleCapitalizationStyle`:** Cycle through the speech-dispatcher capitalization styles.
- **`CyclePunctuationLevel`:** Cycles through punctuation levels for speech.
- **`CycleSynthesizer`:** Cycles through available speech synthesizers.
- **`DecreasePitch`:** Decreases the speech pitch
- **`DecreaseRate`:** Decreases the speech rate.
- **`DecreaseVolume`:** Decreases the speech volume
- **`IncreasePitch`:** Increase the speech pitch
- **`IncreaseRate`:** Increases the speech rate.
- **`IncreaseVolume`:** Increases the speech volume
- **`InterruptSpeech`:** Interrupts the speech server.
- **`RefreshSpeech`:** Shuts down and re-initializes speech.
- **`ShutdownSpeech`:** Shuts down the speech server.
- **`StartSpeech`:** Starts the speech server.
- **`ToggleSpeech`:** Toggles speech on and off.

#### Parameterized Commands

**Method:** `org.gnome.Orca.Module.ExecuteParameterizedCommand`

- **`GetVoicesForLanguage`:** Returns a list of available voices for the specified language. Parameters: `language` (str), `variant` (str), `notify_user` (bool)

#### Settings

**Methods:** `org.gnome.Orca.Module.ExecuteRuntimeGetter` / `org.gnome.Orca.Module.ExecuteRuntimeSetter`

**Parameters:** `PropertyName` (string), `Value` (variant, setter only)

- **`AutoLanguageSwitching`:** Gets/Sets whether automatic language switching is enabled.
- **`AvailableServers`:** Returns a list of available servers. (getter only)
- **`AvailableSynthesizers`:** Returns a list of available synthesizers of the speech server. (getter only)
- **`AvailableVoices`:** Returns a list of available voices for the current synthesizer. (getter only)
- **`CapitalizationStyle`:** Gets/Sets the capitalization style.
- **`CurrentServer`:** Gets/Sets the current speech server (e.g. Speech Dispatcher or Spiel).
- **`CurrentSynthesizer`:** Gets/Sets the current synthesizer of the active speech server.
- **`CurrentVoice`:** Gets/Sets the current voice for the active synthesizer.
- **`InsertPausesBetweenUtterances`:** Gets/Sets whether pauses are inserted between utterances, e.g. between name and role.
- **`Pitch`:** Gets/Sets the current speech pitch (0.0-10.0, default: 5.0).
- **`PunctuationLevel`:** Gets/Sets the punctuation level.
- **`Rate`:** Gets/Sets the current speech rate (0-100, default: 50).
- **`SpeakNumbersAsDigits`:** Gets/Sets whether numbers are spoken as digits.
- **`SpeechIsEnabled`:** Gets/Sets whether the speech server is enabled. See also is-muted.
- **`SpeechIsMuted`:** Gets/Sets whether speech output is temporarily muted.
- **`UseColorNames`:** Gets/Sets whether colors are announced by name or as RGB values.
- **`UsePronunciationDictionary`:** Gets/Sets whether the user's pronunciation dictionary should be applied.
- **`Volume`:** Gets/Sets the current speech volume (0.0-10.0, default: 10.0).

---

### SpeechPresenter

**Object Path:** `/org/gnome/Orca/Service/SpeechPresenter`

#### Commands

**Method:** `org.gnome.Orca.Module.ExecuteCommand`

**Parameters:** `CommandName` (string), [`NotifyUser`](README-REMOTE-CONTROLLER.md#user-notification-applicability) (boolean)

- **`ChangeNumberStyle`:** Changes spoken number style between digits and words.
- **`ToggleIndentationAndJustification`:** Toggles the speaking of indentation and justification.
- **`ToggleMonitor`:** Toggles the speech monitor on and off.
- **`ToggleTableCellReadingMode`:** Toggles between speak cell and speak row.
- **`ToggleVerbosity`:** Toggles speech verbosity level between verbose and brief.

#### Settings

**Methods:** `org.gnome.Orca.Module.ExecuteRuntimeGetter` / `org.gnome.Orca.Module.ExecuteRuntimeSetter`

**Parameters:** `PropertyName` (string), `Value` (variant, setter only)

- **`AlwaysAnnounceSelectedRangeInSpreadsheet`:** Gets/Sets whether the selected range in spreadsheets is always announced.
- **`AnnounceBlockquote`:** Gets/Sets whether blockquotes are announced when entered.
- **`AnnounceCellCoordinates`:** Gets/Sets whether (non-spreadsheet) cell coordinates are announced.
- **`AnnounceCellHeaders`:** Gets/Sets whether cell headers are announced.
- **`AnnounceCellSpan`:** Gets/Sets whether cell spans are announced when greater than 1.
- **`AnnounceForm`:** Gets/Sets whether non-landmark forms are announced when entered.
- **`AnnounceGrouping`:** Gets/Sets whether groupings are announced when entered.
- **`AnnounceLandmark`:** Gets/Sets whether landmarks are announced when entered.
- **`AnnounceList`:** Gets/Sets whether lists are announced when entered.
- **`AnnounceSpreadsheetCellCoordinates`:** Gets/Sets whether spreadsheet cell coordinates are announced.
- **`AnnounceTable`:** Gets/Sets whether tables are announced when entered.
- **`MessagesAreDetailed`:** Gets/Sets whether informative messages will be detailed or brief.
- **`MonitorBackground`:** Gets/Sets the speech monitor background color.
- **`MonitorFontSize`:** Gets/Sets the speech monitor font size.
- **`MonitorForeground`:** Gets/Sets the speech monitor foreground color.
- **`MonitorIsEnabled`:** Gets/Sets whether the speech monitor is enabled.
- **`OnlySpeakDisplayedText`:** Gets/Sets whether only displayed text should be spoken.
- **`ProgressBarSpeechInterval`:** Gets/Sets the speech progress bar update interval in seconds.
- **`ProgressBarSpeechVerbosity`:** Gets/Sets the speech progress bar verbosity level.
- **`RepeatedCharacterLimit`:** Gets/Sets the count at which repeated, non-alphanumeric symbols will be described.
- **`SpeakBlankLines`:** Gets/Sets whether blank lines will be spoken.
- **`SpeakDescription`:** Gets/Sets whether object descriptions are spoken.
- **`SpeakIndentationAndJustification`:** Gets/Sets whether speaking of indentation and justification is enabled.
- **`SpeakIndentationOnlyIfChanged`:** Gets/Sets whether indentation will be announced only if it has changed.
- **`SpeakMisspelledIndicator`:** Gets/Sets whether the misspelled indicator is spoken.
- **`SpeakPositionInSet`:** Gets/Sets whether the position and set size of objects are spoken.
- **`SpeakProgressBarUpdates`:** Gets/Sets whether speech progress bar updates are enabled.
- **`SpeakRowInDocumentTable`:** Gets/Sets whether Up/Down in text-document tables speaks the row or just the cell.
- **`SpeakRowInGuiTable`:** Gets/Sets whether Up/Down in GUI tables speaks the row or just the cell.
- **`SpeakRowInSpreadsheet`:** Gets/Sets whether Up/Down in spreadsheets speaks the row or just the cell.
- **`SpeakTutorialMessages`:** Gets/Sets whether tutorial messages are spoken.
- **`SpeakWidgetMnemonic`:** Gets/Sets whether widget mnemonics are spoken.
- **`VerbosityLevel`:** Gets/Sets the speech verbosity level for object presentation.

---

### SpellCheckPresenter

**Object Path:** `/org/gnome/Orca/Service/SpellCheckPresenter`

#### Settings

**Methods:** `org.gnome.Orca.Module.ExecuteRuntimeGetter` / `org.gnome.Orca.Module.ExecuteRuntimeSetter`

**Parameters:** `PropertyName` (string), `Value` (variant, setter only)

- **`PresentContext`:** Gets/Sets whether to present the context/surrounding sentence.
- **`SpellError`:** Gets/Sets whether misspelled word should be spelled.
- **`SpellSuggestion`:** Gets/Sets whether the suggested correction should be spelled.

---

### StructuralNavigator

**Object Path:** `/org/gnome/Orca/Service/StructuralNavigator`

#### Commands

**Method:** `org.gnome.Orca.Module.ExecuteCommand`

**Parameters:** `CommandName` (string), [`NotifyUser`](README-REMOTE-CONTROLLER.md#user-notification-applicability) (boolean)

##### Blockquotes

- **`NextBlockquote`:** Goes to the next blockquote.
- **`PreviousBlockquote`:** Goes to the previous blockquote.
- **`ListBlockquotes`:** Displays a list of blockquotes.

##### Buttons

- **`NextButton`:** Goes to the next button.
- **`PreviousButton`:** Goes to the previous button.
- **`ListButtons`:** Displays a list of buttons.

##### Checkboxes

- **`NextCheckbox`:** Goes to the next checkbox.
- **`PreviousCheckbox`:** Goes to the previous checkbox.
- **`ListCheckboxes`:** Displays a list of checkboxes.

##### Clickables

- **`NextClickable`:** Goes to the next clickable.
- **`PreviousClickable`:** Goes to the previous clickable.
- **`ListClickables`:** Displays a list of clickables.

##### Comboboxes

- **`NextCombobox`:** Goes to the next combo box.
- **`PreviousCombobox`:** Goes to the previous combo box.
- **`ListComboboxes`:** Displays a list of combo boxes.

##### Entries

- **`NextEntry`:** Goes to the next entry.
- **`PreviousEntry`:** Goes to the previous entry.
- **`ListEntries`:** Displays a list of entries.

##### FormFields

- **`NextFormField`:** Goes to the next form field.
- **`PreviousFormField`:** Goes to the previous form field.
- **`ListFormFields`:** Displays a list of form fields.

##### Headings

- **`NextHeading`:** Goes to the next heading.
- **`PreviousHeading`:** Goes to the previous heading.
- **`ListHeadings`:** Displays a list of headings.
- **`NextHeadingLevel1`:** Goes to the next level 1 heading.
- **`PreviousHeadingLevel1`:** Goes to the previous level 1 heading.
- **`ListHeadingsLevel1`:** Displays a list of level 1 headings.
- **`NextHeadingLevel2`:** Goes to the next level 2 heading.
- **`PreviousHeadingLevel2`:** Goes to the previous level 2 heading.
- **`ListHeadingsLevel2`:** Displays a list of level 2 headings.
- **`NextHeadingLevel3`:** Goes to the next level 3 heading.
- **`PreviousHeadingLevel3`:** Goes to the previous level 3 heading.
- **`ListHeadingsLevel3`:** Displays a list of level 3 headings.
- **`NextHeadingLevel4`:** Goes to the next level 4 heading.
- **`PreviousHeadingLevel4`:** Goes to the previous level 4 heading.
- **`ListHeadingsLevel4`:** Displays a list of level 4 headings.
- **`NextHeadingLevel5`:** Goes to the next level 5 heading.
- **`PreviousHeadingLevel5`:** Goes to the previous level 5 heading.
- **`ListHeadingsLevel5`:** Displays a list of level 5 headings.
- **`NextHeadingLevel6`:** Goes to the next level 6 heading.
- **`PreviousHeadingLevel6`:** Goes to the previous level 6 heading.
- **`ListHeadingsLevel6`:** Displays a list of level 6 headings.

##### Iframes

- **`NextIframe`:** Goes to the next iframe.
- **`PreviousIframe`:** Goes to the previous iframe.
- **`ListIframes`:** Displays a list of iframes.

##### Images

- **`NextImage`:** Goes to the next image.
- **`PreviousImage`:** Goes to the previous image.
- **`ListImages`:** Displays a list of images.

##### Landmarks

- **`NextLandmark`:** Goes to the next landmark.
- **`PreviousLandmark`:** Goes to the previous landmark.
- **`ListLandmarks`:** Displays a list of landmarks.

##### LargeObjects

- **`NextLargeObject`:** Goes to the next large object.
- **`PreviousLargeObject`:** Goes to the previous large object.
- **`ListLargeObjects`:** Displays a list of large objects.

##### Links

- **`NextLink`:** Goes to the next link.
- **`PreviousLink`:** Goes to the previous link.
- **`ListLinks`:** Displays a list of links.
- **`NextUnvisitedLink`:** Goes to the next unvisited link.
- **`PreviousUnvisitedLink`:** Goes to the previous unvisited link.
- **`ListUnvisitedLinks`:** Displays a list of unvisited links.
- **`NextVisitedLink`:** Goes to the next visited link.
- **`PreviousVisitedLink`:** Goes to the previous visited link.
- **`ListVisitedLinks`:** Displays a list of visited links.

##### Lists

- **`NextList`:** Goes to the next list.
- **`PreviousList`:** Goes to the previous list.
- **`ListLists`:** Displays a list of lists.

##### ListItems

- **`NextListItem`:** Goes to the next list item.
- **`PreviousListItem`:** Goes to the previous list item.
- **`ListListItems`:** Displays a list of list items.

##### LiveRegions

- **`NextLiveRegion`:** Goes to the next live region.
- **`PreviousLiveRegion`:** Goes to the previous live region.

##### Paragraphs

- **`NextParagraph`:** Goes to the next paragraph.
- **`PreviousParagraph`:** Goes to the previous paragraph.
- **`ListParagraphs`:** Displays a list of paragraphs.

##### RadioButtons

- **`NextRadioButton`:** Goes to the next radio button.
- **`PreviousRadioButton`:** Goes to the previous radio button.
- **`ListRadioButtons`:** Displays a list of radio buttons.

##### Separators

- **`NextSeparator`:** Goes to the next separator.
- **`PreviousSeparator`:** Goes to the previous separator.

##### Tables

- **`NextTable`:** Goes to the next table.
- **`PreviousTable`:** Goes to the previous table.
- **`ListTables`:** Displays a list of tables.

##### Other

- **`ContainerEnd`:** Moves to the end of the current container.
- **`ContainerStart`:** Moves to the start of the current container.
- **`CycleMode`:** Cycles among the structural navigation modes.

#### Settings

**Methods:** `org.gnome.Orca.Module.ExecuteRuntimeGetter` / `org.gnome.Orca.Module.ExecuteRuntimeSetter`

**Parameters:** `PropertyName` (string), `Value` (variant, setter only)

- **`IsEnabled`:** Gets/Sets whether structural navigation is enabled.
- **`LargeObjectTextLength`:** Gets/Sets the minimum number of characters to be considered a 'large object'.
- **`NavigationWraps`:** Gets/Sets whether navigation wraps when reaching the top/bottom of the document.
- **`TriggersFocusMode`:** Gets/Sets whether structural navigation triggers focus mode.

---

### SystemInformationPresenter

**Object Path:** `/org/gnome/Orca/Service/SystemInformationPresenter`

#### Commands

**Method:** `org.gnome.Orca.Module.ExecuteCommand`

**Parameters:** `CommandName` (string), [`NotifyUser`](README-REMOTE-CONTROLLER.md#user-notification-applicability) (boolean)

- **`PresentBatteryStatus`:** Presents the battery status.
- **`PresentCpuAndMemoryUsage`:** Presents the cpu and memory usage.
- **`PresentDate`:** Presents the current date.
- **`PresentTime`:** Presents the current time.

#### Settings

**Methods:** `org.gnome.Orca.Module.ExecuteRuntimeGetter` / `org.gnome.Orca.Module.ExecuteRuntimeSetter`

**Parameters:** `PropertyName` (string), `Value` (variant, setter only)

- **`AvailableDateFormats`:** Returns a list of available date format names. (getter only)
- **`AvailableTimeFormats`:** Returns a list of available time format names. (getter only)
- **`DateFormat`:** Gets/Sets the date format.
- **`TimeFormat`:** Gets/Sets the time format.

---

### TableNavigator

**Object Path:** `/org/gnome/Orca/Service/TableNavigator`

#### Commands

**Method:** `org.gnome.Orca.Module.ExecuteCommand`

**Parameters:** `CommandName` (string), [`NotifyUser`](README-REMOTE-CONTROLLER.md#user-notification-applicability) (boolean)

- **`ClearDynamicColumnHeadersRow`:** Clears the row for the dynamic column headers.
- **`ClearDynamicRowHeadersColumn`:** Clears the column for the dynamic row headers.
- **`MoveDown`:** Moves to the cell below.
- **`MoveLeft`:** Moves to the cell on the left.
- **`MoveRight`:** Moves to the cell on the right.
- **`MoveToBeginningOfRow`:** Moves to the beginning of the row.
- **`MoveToBottomOfColumn`:** Moves to the bottom of the column.
- **`MoveToEndOfRow`:** Moves to the end of the row.
- **`MoveToFirstCell`:** Moves to the first cell.
- **`MoveToLastCell`:** Moves to the last cell.
- **`MoveToTopOfColumn`:** Moves to the top of the column.
- **`MoveUp`:** Moves to the cell above.
- **`SetDynamicColumnHeadersRow`:** Sets the row for the dynamic header columns to the current row.
- **`SetDynamicRowHeadersColumn`:** Sets the column for the dynamic row headers to the current column.
- **`ToggleEnabled`:** Toggles table navigation.

#### Settings

**Methods:** `org.gnome.Orca.Module.ExecuteRuntimeGetter` / `org.gnome.Orca.Module.ExecuteRuntimeSetter`

**Parameters:** `PropertyName` (string), `Value` (variant, setter only)

- **`IsEnabled`:** Gets/Sets whether table navigation is enabled.
- **`SkipBlankCells`:** Gets/Sets whether blank cells should be skipped during navigation.

---

### TextAttributeManager

**Object Path:** `/org/gnome/Orca/Service/TextAttributeManager`

#### Settings

**Methods:** `org.gnome.Orca.Module.ExecuteRuntimeGetter` / `org.gnome.Orca.Module.ExecuteRuntimeSetter`

**Parameters:** `PropertyName` (string), `Value` (variant, setter only)

- **`AttributesToBraille`:** Gets/Sets the list of text attributes to mark in braille.
- **`AttributesToSpeak`:** Gets/Sets the list of text attributes to speak.

---

### TypingEchoPresenter

**Object Path:** `/org/gnome/Orca/Service/TypingEchoPresenter`

#### Commands

**Method:** `org.gnome.Orca.Module.ExecuteCommand`

**Parameters:** `CommandName` (string), [`NotifyUser`](README-REMOTE-CONTROLLER.md#user-notification-applicability) (boolean)

- **`CycleKeyEcho`:** Cycle through the key echo levels.

#### Settings

**Methods:** `org.gnome.Orca.Module.ExecuteRuntimeGetter` / `org.gnome.Orca.Module.ExecuteRuntimeSetter`

**Parameters:** `PropertyName` (string), `Value` (variant, setter only)

- **`ActionKeysEnabled`:** Gets/Sets whether action keys will be echoed when key echo is enabled.
- **`AlphabeticKeysEnabled`:** Gets/Sets whether alphabetic keys will be echoed when key echo is enabled.
- **`CharacterEchoEnabled`:** Gets/Sets whether echo of inserted characters is enabled.
- **`DiacriticalKeysEnabled`:** Gets/Sets whether diacritical keys will be echoed when key echo is enabled.
- **`FunctionKeysEnabled`:** Gets/Sets whether function keys will be echoed when key echo is enabled.
- **`KeyEchoEnabled`:** Gets/Sets whether echo of key presses is enabled. See also set_character_echo_enabled.
- **`LockingKeysPresented`:** Gets/Sets whether locking keys are presented.
- **`ModifierKeysEnabled`:** Gets/Sets whether modifier keys will be echoed when key echo is enabled.
- **`NavigationKeysEnabled`:** Gets/Sets whether navigation keys will be echoed when key echo is enabled.
- **`NumericKeysEnabled`:** Gets/Sets whether numeric keys will be echoed when key echo is enabled.
- **`PunctuationKeysEnabled`:** Gets/Sets whether punctuation keys will be echoed when key echo is enabled.
- **`SentenceEchoEnabled`:** Gets/Sets whether sentence echo is enabled.
- **`SpaceEnabled`:** Gets/Sets whether space key will be echoed when key echo is enabled.
- **`WordEchoEnabled`:** Gets/Sets whether word echo is enabled.

---

### WhereAmIPresenter

**Object Path:** `/org/gnome/Orca/Service/WhereAmIPresenter`

#### Commands

**Method:** `org.gnome.Orca.Module.ExecuteCommand`

**Parameters:** `CommandName` (string), [`NotifyUser`](README-REMOTE-CONTROLLER.md#user-notification-applicability) (boolean)

- **`PresentCellFormula`:** Presents the formula associated with the current spreadsheet cell.
- **`PresentCharacterAttributes`:** Presents the font and formatting details for the current character.
- **`PresentDefaultButton`:** Presents the default button of the current dialog.
- **`PresentLink`:** Presents details about the current link.
- **`PresentSelectedText`:** Presents the selected text.
- **`PresentSelection`:** Presents the selected text or selected objects.
- **`PresentSizeAndPosition`:** Presents the size and position of the current object.
- **`PresentStatusBar`:** Presents the status bar and info bar of the current window.
- **`PresentTitle`:** Presents the title of the current window.
- **`WhereAmIBasic`:** Presents basic information about the current location.
- **`WhereAmIDetailed`:** Presents detailed information about the current location.

---
