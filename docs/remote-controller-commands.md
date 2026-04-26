# Orca D-Bus Service Commands Reference

The service can be accessed at:

- **Service Name:** `org.gnome.Orca1.Service`
- **Main Object Path:** `/org/gnome/Orca1/Service`
- **Module Object Paths:** `/org/gnome/Orca1/Service/ModuleName`
- **Module Interface Names:** `org.gnome.Orca1.<ModuleName>`

Additional information about using the remote controller can be found in [remote-controller.md](remote-controller.md).

---

## Service-Level Commands

These commands are available directly on the main service object at `/org/gnome/Orca1/Service`.

- **`GetVersion`**() → `s`: Returns Orca's version and revision if available.
- **`PresentMessage`**(`message` (s)) → `b`: Presents message to the user.
- **`Quit`**() → `b`: Quits Orca.
- **`ShowPreferences`**() → `b`: Shows Orca's preferences GUI.

---

## Modules

### ActionPresenter

**Object Path:** `/org/gnome/Orca1/Service/ActionPresenter`

**Interface:** `org.gnome.Orca1.ActionPresenter`

#### Commands

- **`ShowActionsList`:** Shows a list of all the accessible actions exposed by the focused object.

---

### BraillePresenter

**Object Path:** `/org/gnome/Orca1/Service/BraillePresenter`

**Interface:** `org.gnome.Orca1.BraillePresenter`

#### Commands

- **`ToggleMonitor`:** Toggles the braille monitor on and off.

#### Properties

- **`AvailableContractionTables`** (`as`, read-only): A list of available contraction table names.
- **`BrailleIsEnabled`** (`b`, read/write): Whether braille is enabled.
- **`BrailleProgressBarUpdates`** (`b`, read/write): Whether braille progress bar updates are enabled.
- **`ComputerBrailleAtCursorIsEnabled`** (`b`, read/write): Whether computer braille is used at the cursor position.
- **`ContractedBrailleIsEnabled`** (`b`, read/write): Whether contracted braille is enabled.
- **`ContractionTable`** (`s`, read/write): The current braille contraction table.
- **`DisplayAncestors`** (`b`, read/write): Whether ancestors of the current object will be displayed.
- **`EndOfLineIndicatorIsEnabled`** (`b`, read/write): Whether the end-of-line indicator is enabled.
- **`FlashMessageDuration`** (`u`, read/write): Flash message duration in milliseconds.
- **`FlashMessagesAreDetailed`** (`b`, read/write): Whether 'flash' messages are detailed (as opposed to brief).
- **`FlashMessagesAreEnabled`** (`b`, read/write): Whether 'flash' messages (i.e. announcements) are enabled.
- **`FlashMessagesArePersistent`** (`b`, read/write): Whether 'flash' messages are persistent (as opposed to temporary).
- **`LinkIndicator`** (`s`, read/write): The braille link indicator style.
- **`LogFile`** (`s`, write-only): Opens the given path for JSONL recording; an empty string closes any open file.
- **`MonitorBackground`** (`s`, read/write): The braille monitor background color.
- **`MonitorCellCount`** (`u`, read/write): The braille monitor cell count.
- **`MonitorForeground`** (`s`, read/write): The braille monitor foreground color.
- **`MonitorIsEnabled`** (`b`, read/write): Whether the braille monitor is enabled.
- **`MonitorShowDots`** (`b`, read/write): Whether the braille monitor shows Unicode braille dots.
- **`PresentMnemonics`** (`b`, read/write): Whether mnemonics are presented on the braille display.
- **`ProgressBarBrailleInterval`** (`u`, read/write): The braille progress bar update interval in seconds.
- **`ProgressBarBrailleVerbosity`** (`u`, read/write): The braille progress bar verbosity level.
- **`RolenameStyle`** (`s`, read/write): The current rolename style for object presentation.
- **`SelectorIndicator`** (`s`, read/write): The braille selector indicator style.
- **`TextAttributesIndicator`** (`s`, read/write): The braille text attributes indicator style.
- **`VerbosityLevel`** (`s`, read/write): The braille verbosity level for object presentation.
- **`WordWrapIsEnabled`** (`b`, read/write): Whether braille word wrap is enabled.

---

### CaretNavigator

**Object Path:** `/org/gnome/Orca1/Service/CaretNavigator`

**Interface:** `org.gnome.Orca1.CaretNavigator`

#### Commands

- **`EndOfFile`:** Moves to the end of the file.
- **`EndOfLine`:** Moves to the end of the line.
- **`NextCharacter`:** Moves to the next character.
- **`NextLine`:** Moves to the next line.
- **`NextWord`:** Moves to the next word.
- **`PreviousCharacter`:** Moves to the previous character.
- **`PreviousLine`:** Moves to the previous line.
- **`PreviousWord`:** Moves to the previous word.
- **`StartOfFile`:** Moves to the start of the file.
- **`StartOfLine`:** Moves to the start of the line.
- **`ToggleEnabled`:** Toggles caret navigation.
- **`ToggleLayoutMode`:** Switches between object mode and layout mode for line presentation.

#### Properties

- **`IsEnabled`** (`b`, read/write): Whether caret navigation is enabled.
- **`LayoutMode`** (`b`, read/write): Whether layout mode is enabled.
- **`TriggersFocusMode`** (`b`, read/write): Whether caret navigation triggers focus mode.

---

### ChatPresenter

**Object Path:** `/org/gnome/Orca1/Service/ChatPresenter`

**Interface:** `org.gnome.Orca1.ChatPresenter`

#### Commands

- **`PresentNextMessage`:** Navigate to and present the next chat message in the history.
- **`PresentPreviousMessage`:** Navigate to and present the previous chat message in the history.
- **`ToggleBuddyTyping`:** Toggles whether we announce when our buddies are typing a message.
- **`ToggleMessageHistories`:** Toggles whether we provide chat room specific message histories.
- **`TogglePrefix`:** Toggles whether we prefix chat room messages with the name of the chat room.

#### Properties

- **`AnnounceBuddyTyping`** (`b`, read/write): Whether to announce when buddies are typing.
- **`MessageVerbosity`** (`u`, read/write): The chat message verbosity setting.
- **`RoomHistories`** (`b`, read/write): Whether to provide chat room specific message histories.
- **`SpeakRoomName`** (`b`, read/write): Whether to speak the chat room name.
- **`SpeakRoomNameLast`** (`b`, read/write): Whether to speak the chat room name after the message.

---

### ClipboardPresenter

**Object Path:** `/org/gnome/Orca1/Service/ClipboardPresenter`

**Interface:** `org.gnome.Orca1.ClipboardPresenter`

#### Commands

- **`PresentClipboardContents`:** Presents the clipboard contents.

---

### CommandManager

**Object Path:** `/org/gnome/Orca1/Service/CommandManager`

**Interface:** `org.gnome.Orca1.CommandManager`

#### Commands

- **`ToggleKeyboardLayout`:** Toggles between desktop and laptop keyboard layout.

#### Properties

- **`DesktopModifierKeys`** (`as`, read/write): The per-layout modifier keys for the desktop layout.
- **`KeyboardLayoutIsDesktop`** (`b`, read/write): Whether the keyboard layout is desktop (True) or laptop (False).
- **`LaptopModifierKeys`** (`as`, read/write): The per-layout modifier keys for the laptop layout.

---

### DocumentPresenter

**Object Path:** `/org/gnome/Orca1/Service/DocumentPresenter`

**Interface:** `org.gnome.Orca1.DocumentPresenter`

#### Commands

- **`EnableStickyBrowseMode`:** Enables sticky browse mode.
- **`EnableStickyFocusMode`:** Enables sticky focus mode.
- **`TogglePresentationMode`:** Switches between browse mode and focus mode (user-initiated).

#### Properties

- **`AutoStickyFocusModeForWebApps`** (`b`, read/write): Whether to auto-detect web apps and enable sticky focus mode.
- **`BrowseModeIsSticky`** (`b`, read-only): True if browse mode is active and 'sticky' (web content only).
- **`FindResultsMinimumLength`** (`u`, read/write): The minimum length for find results to be spoken.
- **`FocusModeIsSticky`** (`b`, read-only): True if focus mode is active and 'sticky' (web content only).
- **`InFocusMode`** (`b`, read-only): True if focus mode is active (web content only).
- **`NativeNavTriggersFocusMode`** (`b`, read/write): Whether native navigation triggers focus mode.
- **`OnlySpeakChangedLines`** (`b`, read/write): Whether to only speak changed lines during find.
- **`PageSummaryOnLoad`** (`b`, read/write): Whether to present a page summary when a document loads.
- **`SayAllOnLoad`** (`b`, read/write): Whether to perform say all when a document loads.
- **`SpeakFindResults`** (`b`, read/write): Whether to speak find results.

---

### FlatReviewPresenter

**Object Path:** `/org/gnome/Orca1/Service/FlatReviewPresenter`

**Interface:** `org.gnome.Orca1.FlatReviewPresenter`

#### Commands

- **`AppendToClipboard`:** Appends the string just presented to the clipboard.
- **`CopyToClipboard`:** Copies the string just presented to the clipboard.
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

#### Properties

- **`IsRestricted`** (`b`, read/write): Whether flat review is restricted to the current object.

---

### MathNavigator

**Object Path:** `/org/gnome/Orca1/Service/MathNavigator`

**Interface:** `org.gnome.Orca1.MathNavigator`

#### Commands

- **`CopyToClipboard`:** Copies the current math navigation node to the clipboard.
- **`EnterMathModeCommand`:** Enters math navigation mode if the current focus is on math.
- **`ExitMathMode`:** Exits math navigation mode.

#### Parameterized Commands

- **`ExecuteMathcatCommand`** → `b`: Executes a MathCAT navigation command. Use get_supported_commands for valid values. Parameters: `mathcat_command` (s).

#### Properties

- **`IsActive`** (`b`, read-only): True if currently navigating a math expression.
- **`SupportedCommands`** (`as`, read-only): The MathCAT navigation commands supported by this navigator.

---

### MathPresenter

**Object Path:** `/org/gnome/Orca1/Service/MathPresenter`

**Interface:** `org.gnome.Orca1.MathPresenter`

#### Properties

- **`AutoZoomOut`** (`b`, read/write): Whether auto zoom out is enabled.
- **`BrailleCode`** (`s`, read/write): The math braille code.
- **`BrailleNavHighlight`** (`s`, read/write): The braille navigation highlight style.
- **`CopyFormat`** (`s`, read/write): The format used when copying math content.
- **`Language`** (`s`, read/write): The math language.
- **`NavMode`** (`s`, read/write): The math navigation mode.
- **`SpeechStyle`** (`s`, read/write): The math speech style.
- **`Verbosity`** (`s`, read/write): The math speech verbosity.

---

### MouseReviewer

**Object Path:** `/org/gnome/Orca1/Service/MouseReviewer`

**Interface:** `org.gnome.Orca1.MouseReviewer`

#### Commands

- **`Toggle`:** Toggle mouse reviewing on or off (requires Wnck).

#### Properties

- **`IsEnabled`** (`b`, read/write): Whether mouse review is enabled (requires Wnck).
- **`PresentTooltips`** (`b`, read/write): Whether tooltips displayed due to mouse hover are spoken (requires X11).

---

### NotificationPresenter

**Object Path:** `/org/gnome/Orca1/Service/NotificationPresenter`

**Interface:** `org.gnome.Orca1.NotificationPresenter`

#### Commands

- **`PresentLastNotification`:** Presents the last notification.
- **`PresentNextNotification`:** Presents the next notification.
- **`PresentPreviousNotification`:** Presents the previous notification.
- **`ShowNotificationList`:** Opens a dialog with a list of the notifications.

---

### ObjectNavigator

**Object Path:** `/org/gnome/Orca1/Service/ObjectNavigator`

**Interface:** `org.gnome.Orca1.ObjectNavigator`

#### Commands

- **`MoveToFirstChild`:** Moves the navigator focus to the first child of the current focus.
- **`MoveToNextSibling`:** Moves the navigator focus to the next sibling of the current focus.
- **`MoveToParent`:** Moves the navigator focus to the parent of the current focus.
- **`MoveToPreviousSibling`:** Moves the navigator focus to the previous sibling of the current focus.
- **`PerformAction`:** Attempts to click on the current focus.
- **`ToggleSimplify`:** Toggles simplified navigation.

---

### ProfileManager

**Object Path:** `/org/gnome/Orca1/Service/ProfileManager`

**Interface:** `org.gnome.Orca1.ProfileManager`

#### Commands

- **`CycleSettingsProfile`:** Cycle through the user's existing settings profiles.
- **`PresentCurrentProfile`:** Present the name of the currently active profile.

#### Properties

- **`ActiveProfile`** (`s`, read/write): The active profile by internal name.
- **`AvailableProfiles`** (`aas`, read-only): List of available profiles as [display_name, internal_name] pairs.
- **`StartingProfile`** (`as`, read/write): No-op for backwards compatibility. Starting profile is always Default.

---

### SayAllPresenter

**Object Path:** `/org/gnome/Orca1/Service/SayAllPresenter`

**Interface:** `org.gnome.Orca1.SayAllPresenter`

#### Commands

- **`FastForward`:** Jumps forward in the current Say All.
- **`Rewind`:** Jumps back in the current Say All.
- **`SayAll`:** Speaks the entire document or text, starting from the current position.

#### Properties

- **`AnnounceArticle`** (`b`, read/write): Whether articles are announced when entered.
- **`AnnounceBlockquote`** (`b`, read/write): Whether blockquotes are announced when entered.
- **`AnnounceCodeBlock`** (`b`, read/write): Whether code blocks are announced when entered.
- **`AnnounceForm`** (`b`, read/write): Whether non-landmark forms are announced when entered.
- **`AnnounceGrouping`** (`b`, read/write): Whether groupings are announced when entered.
- **`AnnounceLandmark`** (`b`, read/write): Whether landmarks are announced when entered.
- **`AnnounceList`** (`b`, read/write): Whether lists are announced when entered.
- **`AnnounceTable`** (`b`, read/write): Whether tables are announced when entered.
- **`AnnounceTrackedChanges`** (`b`, read/write): Whether tracked changes are announced when entered.
- **`OnlySpeakDisplayedText`** (`b`, read/write): Whether Say All only speaks displayed text.
- **`RewindAndFastForwardEnabled`** (`b`, read/write): Whether Up and Down can be used in Say All.
- **`StructuralNavigationEnabled`** (`b`, read/write): Whether structural navigation keys can be used in Say All.
- **`Style`** (`s`, read/write): The current Say All style.
- **`TextAttributeChangeModeAsString`** (`s`, read/write): When text attribute changes are spoken during Say All.

---

### SleepModeManager

**Object Path:** `/org/gnome/Orca1/Service/SleepModeManager`

**Interface:** `org.gnome.Orca1.SleepModeManager`

#### Commands

- **`ToggleSleepMode`:** Toggles sleep mode for the active application.

#### Properties

- **`SleepModeApps`** (`as`, read/write): The list of apps that should automatically use sleep mode.

---

### SoundPresenter

**Object Path:** `/org/gnome/Orca1/Service/SoundPresenter`

**Interface:** `org.gnome.Orca1.SoundPresenter`

#### Properties

- **`BeepProgressBarUpdates`** (`b`, read/write): Whether beep progress bar updates are enabled.
- **`ProgressBarBeepInterval`** (`u`, read/write): The beep progress bar update interval in seconds.
- **`ProgressBarBeepVerbosity`** (`u`, read/write): The beep progress bar verbosity level.
- **`SoundIsEnabled`** (`b`, read/write): Whether sound is enabled.
- **`SoundVolume`** (`d`, read/write): The sound volume (0.0 to 1.0).

---

### SpeechManager

**Object Path:** `/org/gnome/Orca1/Service/SpeechManager`

**Interface:** `org.gnome.Orca1.SpeechManager`

#### Commands

- **`CycleCapitalizationStyle`:** Cycle through the speech-dispatcher capitalization styles.
- **`CyclePunctuationLevel`:** Cycles through punctuation levels for speech.
- **`CycleSynthesizer`:** Cycles through available speech synthesizers.
- **`DecreasePitch`:** Decreases the speech pitch
- **`DecreasePitchRange`:** Decreases the speech inflection (pitch range).
- **`DecreaseRate`:** Decreases the speech rate.
- **`DecreaseVolume`:** Decreases the speech volume
- **`IncreasePitch`:** Increase the speech pitch
- **`IncreasePitchRange`:** Increases the speech inflection (pitch range).
- **`IncreaseRate`:** Increases the speech rate.
- **`IncreaseVolume`:** Increases the speech volume
- **`InterruptSpeech`:** Interrupts the speech server.
- **`RefreshSpeech`:** Shuts down and re-initializes speech.
- **`ShutdownSpeech`:** Shuts down the speech server.
- **`StartSpeech`:** Starts the speech server.
- **`ToggleSpeech`:** Toggles speech on and off.

#### Parameterized Commands

- **`GetVoicesForLanguage`** → `a(sss)`: Returns a list of available voices for the specified language. Parameters: `language` (s), `variant` (s).

#### Properties

- **`AutoLanguageSwitching`** (`b`, read/write): Whether automatic language switching for document content is enabled.
- **`AutoLanguageSwitchingUi`** (`b`, read/write): Whether automatic language switching for UI elements is enabled.
- **`AvailableServers`** (`as`, read-only): A list of available servers.
- **`AvailableSynthesizers`** (`as`, read-only): A list of available synthesizers of the speech server.
- **`AvailableVoices`** (`as`, read-only): A list of available voices for the current synthesizer.
- **`CapitalizationStyle`** (`s`, read/write): The capitalization style.
- **`CurrentServer`** (`s`, read/write): The current speech server (e.g. Speech Dispatcher or Spiel).
- **`CurrentSynthesizer`** (`s`, read/write): The current synthesizer of the active speech server.
- **`CurrentVoice`** (`s`, read/write): The current voice for the active synthesizer.
- **`InsertPausesBetweenUtterances`** (`b`, read/write): Whether pauses are inserted between utterances, e.g. between name and role.
- **`OnlySwitchConfiguredLanguages`** (`b`, read/write): Whether language switching is limited to configured voice sets.
- **`Pitch`** (`d`, read/write): The current speech pitch (0.0-10.0, default: 5.0).
- **`PitchRange`** (`d`, read/write): The current speech inflection / pitch range (0.0-10.0, default: 5.0).
- **`PunctuationLevel`** (`s`, read/write): The punctuation level.
- **`Rate`** (`u`, read/write): The current speech rate (0-100, default: 50).
- **`SpeakNumbersAsDigits`** (`b`, read/write): Whether numbers are spoken as digits.
- **`SpeechIsEnabled`** (`b`, read/write): Whether the speech server is enabled. See also is-muted.
- **`SpeechIsMuted`** (`b`, read/write): Whether speech output is temporarily muted.
- **`UseColorNames`** (`b`, read/write): Whether colors are announced by name or as RGB values.
- **`UsePronunciationDictionary`** (`b`, read/write): Whether the user's pronunciation dictionary should be applied.
- **`Volume`** (`d`, read/write): The current speech volume (0.0-10.0, default: 10.0).

---

### SpeechPresenter

**Object Path:** `/org/gnome/Orca1/Service/SpeechPresenter`

**Interface:** `org.gnome.Orca1.SpeechPresenter`

#### Commands

- **`ChangeNumberStyle`:** Changes spoken number style between digits and words.
- **`CycleTextAttributeChangeMode`:** Cycles through text attribute change announcement modes.
- **`ToggleIndentation`:** Toggles spoken indentation.
- **`ToggleMonitor`:** Toggles the speech monitor on and off.
- **`ToggleTableCellReadingMode`:** Toggles between speak cell and speak row.
- **`ToggleVerbosity`:** Toggles speech verbosity level between verbose and brief.

#### Properties

- **`AlwaysAnnounceSelectedRangeInSpreadsheet`** (`b`, read/write): Whether the selected range in spreadsheets is always announced.
- **`AnnounceArticle`** (`b`, read/write): Whether articles are announced when entered.
- **`AnnounceBlockquote`** (`b`, read/write): Whether blockquotes are announced when entered.
- **`AnnounceCellCoordinates`** (`b`, read/write): Whether (non-spreadsheet) cell coordinates are announced.
- **`AnnounceCellHeaders`** (`b`, read/write): Whether cell headers are announced.
- **`AnnounceCellSpan`** (`b`, read/write): Whether cell spans are announced when greater than 1.
- **`AnnounceCodeBlock`** (`b`, read/write): Whether code blocks are announced when entered.
- **`AnnounceForm`** (`b`, read/write): Whether non-landmark forms are announced when entered.
- **`AnnounceGrouping`** (`b`, read/write): Whether groupings are announced when entered.
- **`AnnounceLandmark`** (`b`, read/write): Whether landmarks are announced when entered.
- **`AnnounceList`** (`b`, read/write): Whether lists are announced when entered.
- **`AnnounceSpreadsheetCellCoordinates`** (`b`, read/write): Whether spreadsheet cell coordinates are announced.
- **`AnnounceTable`** (`b`, read/write): Whether tables are announced when entered.
- **`AnnounceTrackedChanges`** (`b`, read/write): Whether tracked changes are announced when entered.
- **`LogFile`** (`s`, write-only): Opens the given path for JSONL recording; an empty string closes any open file.
- **`MessagesAreDetailed`** (`b`, read/write): Whether informative messages will be detailed or brief.
- **`MonitorBackground`** (`s`, read/write): The speech monitor background color.
- **`MonitorFontSize`** (`u`, read/write): The speech monitor font size.
- **`MonitorForeground`** (`s`, read/write): The speech monitor foreground color.
- **`MonitorIsEnabled`** (`b`, read/write): Whether the speech monitor is enabled.
- **`OnlySpeakDisplayedText`** (`b`, read/write): Whether only displayed text should be spoken.
- **`ProgressBarSpeechInterval`** (`u`, read/write): The speech progress bar update interval in seconds.
- **`ProgressBarSpeechVerbosity`** (`u`, read/write): The speech progress bar verbosity level.
- **`RepeatedCharacterLimit`** (`u`, read/write): The count at which repeated, non-alphanumeric symbols will be described.
- **`SpeakBlankLines`** (`b`, read/write): Whether blank lines will be spoken.
- **`SpeakDescription`** (`b`, read/write): Whether object descriptions are spoken.
- **`SpeakIndentation`** (`b`, read/write): Whether spoken indentation is enabled.
- **`SpeakIndentationOnlyIfChanged`** (`b`, read/write): Whether indentation will be announced only if it has changed.
- **`SpeakMisspelledIndicator`** (`b`, read/write): Whether the misspelled indicator is spoken.
- **`SpeakPositionInSet`** (`b`, read/write): Whether the position and set size of objects are spoken.
- **`SpeakProgressBarUpdates`** (`b`, read/write): Whether speech progress bar updates are enabled.
- **`SpeakRowInDocumentTable`** (`b`, read/write): Whether Up/Down in text-document tables speaks the row or just the cell.
- **`SpeakRowInGuiTable`** (`b`, read/write): Whether Up/Down in GUI tables speaks the row or just the cell.
- **`SpeakRowInSpreadsheet`** (`b`, read/write): Whether Up/Down in spreadsheets speaks the row or just the cell.
- **`SpeakTextAttributeChanges`** (`s`, read/write): When text attribute changes are spoken during navigation.
- **`SpeakTutorialMessages`** (`b`, read/write): Whether tutorial messages are spoken.
- **`SpeakWidgetMnemonic`** (`b`, read/write): Whether widget mnemonics are spoken.
- **`VerbosityLevel`** (`s`, read/write): The speech verbosity level for object presentation.

---

### SpellCheckPresenter

**Object Path:** `/org/gnome/Orca1/Service/SpellCheckPresenter`

**Interface:** `org.gnome.Orca1.SpellCheckPresenter`

#### Properties

- **`PresentContext`** (`b`, read/write): Whether to present the context/surrounding sentence.
- **`SpellError`** (`b`, read/write): Whether misspelled word should be spelled.
- **`SpellSuggestion`** (`b`, read/write): Whether the suggested correction should be spelled.

---

### StructuralNavigator

**Object Path:** `/org/gnome/Orca1/Service/StructuralNavigator`

**Interface:** `org.gnome.Orca1.StructuralNavigator`

#### Commands

- **`ContainerEnd`:** Moves to the end of the current container.
- **`ContainerStart`:** Moves to the start of the current container.
- **`CycleMode`:** Cycles among the structural navigation modes.
- **`ListAnnotations`:** Displays a list of annotations.
- **`ListBlockquotes`:** Displays a list of blockquotes.
- **`ListButtons`:** Displays a list of buttons.
- **`ListCheckboxes`:** Displays a list of checkboxes.
- **`ListClickables`:** Displays a list of clickables.
- **`ListComboboxes`:** Displays a list of combo boxes.
- **`ListEntries`:** Displays a list of entries.
- **`ListFormFields`:** Displays a list of form fields.
- **`ListHeadings`:** Displays a list of headings.
- **`ListHeadingsLevel1`:** Displays a list of level 1 headings.
- **`ListHeadingsLevel2`:** Displays a list of level 2 headings.
- **`ListHeadingsLevel3`:** Displays a list of level 3 headings.
- **`ListHeadingsLevel4`:** Displays a list of level 4 headings.
- **`ListHeadingsLevel5`:** Displays a list of level 5 headings.
- **`ListHeadingsLevel6`:** Displays a list of level 6 headings.
- **`ListIframes`:** Displays a list of iframes.
- **`ListImages`:** Displays a list of images.
- **`ListLandmarks`:** Displays a list of landmarks.
- **`ListLargeObjects`:** Displays a list of large objects.
- **`ListLinks`:** Displays a list of links.
- **`ListListItems`:** Displays a list of list items.
- **`ListLists`:** Displays a list of lists.
- **`ListParagraphs`:** Displays a list of paragraphs.
- **`ListRadioButtons`:** Displays a list of radio buttons.
- **`ListTables`:** Displays a list of tables.
- **`ListUnvisitedLinks`:** Displays a list of unvisited links.
- **`ListVisitedLinks`:** Displays a list of visited links.
- **`NextAnnotation`:** Goes to the next annotation.
- **`NextBlockquote`:** Goes to the next blockquote.
- **`NextButton`:** Goes to the next button.
- **`NextCheckbox`:** Goes to the next checkbox.
- **`NextClickable`:** Goes to the next clickable.
- **`NextCombobox`:** Goes to the next combo box.
- **`NextEntry`:** Goes to the next entry.
- **`NextFormField`:** Goes to the next form field.
- **`NextHeading`:** Goes to the next heading.
- **`NextHeadingLevel1`:** Goes to the next level 1 heading.
- **`NextHeadingLevel2`:** Goes to the next level 2 heading.
- **`NextHeadingLevel3`:** Goes to the next level 3 heading.
- **`NextHeadingLevel4`:** Goes to the next level 4 heading.
- **`NextHeadingLevel5`:** Goes to the next level 5 heading.
- **`NextHeadingLevel6`:** Goes to the next level 6 heading.
- **`NextIframe`:** Goes to the next iframe.
- **`NextImage`:** Goes to the next image.
- **`NextLandmark`:** Goes to the next landmark.
- **`NextLargeObject`:** Goes to the next large object.
- **`NextLink`:** Goes to the next link.
- **`NextList`:** Goes to the next list.
- **`NextListItem`:** Goes to the next list item.
- **`NextLiveRegion`:** Goes to the next live region.
- **`NextParagraph`:** Goes to the next paragraph.
- **`NextRadioButton`:** Goes to the next radio button.
- **`NextSeparator`:** Goes to the next separator.
- **`NextTable`:** Goes to the next table.
- **`NextUnvisitedLink`:** Goes to the next unvisited link.
- **`NextVisitedLink`:** Goes to the next visited link.
- **`PreviousAnnotation`:** Goes to the previous annotation.
- **`PreviousBlockquote`:** Goes to the previous blockquote.
- **`PreviousButton`:** Goes to the previous button.
- **`PreviousCheckbox`:** Goes to the previous checkbox.
- **`PreviousClickable`:** Goes to the previous clickable.
- **`PreviousCombobox`:** Goes to the previous combo box.
- **`PreviousEntry`:** Goes to the previous entry.
- **`PreviousFormField`:** Goes to the previous form field.
- **`PreviousHeading`:** Goes to the previous heading.
- **`PreviousHeadingLevel1`:** Goes to the previous level 1 heading.
- **`PreviousHeadingLevel2`:** Goes to the previous level 2 heading.
- **`PreviousHeadingLevel3`:** Goes to the previous level 3 heading.
- **`PreviousHeadingLevel4`:** Goes to the previous level 4 heading.
- **`PreviousHeadingLevel5`:** Goes to the previous level 5 heading.
- **`PreviousHeadingLevel6`:** Goes to the previous level 6 heading.
- **`PreviousIframe`:** Goes to the previous iframe.
- **`PreviousImage`:** Goes to the previous image.
- **`PreviousLandmark`:** Goes to the previous landmark.
- **`PreviousLargeObject`:** Goes to the previous large object.
- **`PreviousLink`:** Goes to the previous link.
- **`PreviousList`:** Goes to the previous list.
- **`PreviousListItem`:** Goes to the previous list item.
- **`PreviousLiveRegion`:** Goes to the previous live region.
- **`PreviousParagraph`:** Goes to the previous paragraph.
- **`PreviousRadioButton`:** Goes to the previous radio button.
- **`PreviousSeparator`:** Goes to the previous separator.
- **`PreviousTable`:** Goes to the previous table.
- **`PreviousUnvisitedLink`:** Goes to the previous unvisited link.
- **`PreviousVisitedLink`:** Goes to the previous visited link.

#### Properties

- **`IsEnabled`** (`b`, read/write): Whether structural navigation is enabled.
- **`LargeObjectTextLength`** (`u`, read/write): The minimum number of characters to be considered a 'large object'.
- **`NavigationWraps`** (`b`, read/write): Whether navigation wraps when reaching the top/bottom of the document.
- **`SkipUnlabeledImages`** (`b`, read/write): Whether unlabeled images are skipped during navigation.
- **`TriggersFocusMode`** (`b`, read/write): Whether structural navigation triggers focus mode.

---

### SystemInformationPresenter

**Object Path:** `/org/gnome/Orca1/Service/SystemInformationPresenter`

**Interface:** `org.gnome.Orca1.SystemInformationPresenter`

#### Commands

- **`PresentBatteryStatus`:** Presents the battery status.
- **`PresentCpuAndMemoryUsage`:** Presents the cpu and memory usage.
- **`PresentDate`:** Presents the current date.
- **`PresentModifierKeysState`:** Presents the state of locked modifier keys. Requires AT-SPI 2.59.0 or later.
- **`PresentTime`:** Presents the current time.

#### Properties

- **`AvailableDateFormats`** (`as`, read-only): A list of available date format names.
- **`AvailableTimeFormats`** (`as`, read-only): A list of available time format names.
- **`DateFormat`** (`s`, read/write): The date format.
- **`TimeFormat`** (`s`, read/write): The time format.

---

### TableNavigator

**Object Path:** `/org/gnome/Orca1/Service/TableNavigator`

**Interface:** `org.gnome.Orca1.TableNavigator`

#### Commands

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

#### Properties

- **`IsEnabled`** (`b`, read/write): Whether table navigation is enabled.
- **`SkipBlankCells`** (`b`, read/write): Whether blank cells should be skipped during navigation.

---

### TextAttributeManager

**Object Path:** `/org/gnome/Orca1/Service/TextAttributeManager`

**Interface:** `org.gnome.Orca1.TextAttributeManager`

#### Properties

- **`AttributesToBraille`** (`as`, read/write): The list of text attributes to mark in braille.
- **`AttributesToSpeak`** (`as`, read/write): The list of text attributes to speak.

---

### TypingEchoPresenter

**Object Path:** `/org/gnome/Orca1/Service/TypingEchoPresenter`

**Interface:** `org.gnome.Orca1.TypingEchoPresenter`

#### Commands

- **`CycleKeyEcho`:** Cycle through the key echo levels.

#### Properties

- **`ActionKeysEnabled`** (`b`, read/write): Whether action keys will be echoed when key echo is enabled.
- **`AlphabeticKeysEnabled`** (`b`, read/write): Whether alphabetic keys will be echoed when key echo is enabled.
- **`CharacterEchoEnabled`** (`b`, read/write): Whether echo of inserted characters is enabled.
- **`DiacriticalKeysEnabled`** (`b`, read/write): Whether diacritical keys will be echoed when key echo is enabled.
- **`FunctionKeysEnabled`** (`b`, read/write): Whether function keys will be echoed when key echo is enabled.
- **`KeyEchoEnabled`** (`b`, read/write): Whether echo of key presses is enabled. See also set_character_echo_enabled.
- **`LockingKeysPresented`** (`b`, read/write): Whether locking keys are presented.
- **`ModifierKeysEnabled`** (`b`, read/write): Whether modifier keys will be echoed when key echo is enabled.
- **`NavigationKeysEnabled`** (`b`, read/write): Whether navigation keys will be echoed when key echo is enabled.
- **`NumericKeysEnabled`** (`b`, read/write): Whether numeric keys will be echoed when key echo is enabled.
- **`PunctuationKeysEnabled`** (`b`, read/write): Whether punctuation keys will be echoed when key echo is enabled.
- **`SentenceEchoEnabled`** (`b`, read/write): Whether sentence echo is enabled.
- **`SpaceEnabled`** (`b`, read/write): Whether space key will be echoed when key echo is enabled.
- **`WordEchoEnabled`** (`b`, read/write): Whether word echo is enabled.

---

### WhereAmIPresenter

**Object Path:** `/org/gnome/Orca1/Service/WhereAmIPresenter`

**Interface:** `org.gnome.Orca1.WhereAmIPresenter`

#### Commands

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
