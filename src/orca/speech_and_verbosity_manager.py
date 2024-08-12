# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
# Copyright 2011-2023 Igalia, S.L.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

# pylint: disable=unused-argument

"""Configures speech and verbosity settings and adjusts strings accordingly."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc." \
                "Copyright (c) 2016-2023 Igalia, S.L."
__license__   = "LGPL"

import re

from . import cmdnames
from . import debug
from . import focus_manager
from . import input_event
from . import keybindings
from . import messages
from . import settings
from . import settings_manager
from . import speech
from .ax_hypertext import AXHypertext
from .ax_table import AXTable

class SpeechAndVerbosityManager:
    """Configures speech and verbosity settings and adjusts strings accordingly."""

    def __init__(self):
        self._handlers = self.get_handlers(True)
        self._bindings = keybindings.KeyBindings()

    def get_bindings(self, refresh=False, is_desktop=True):
        """Returns the speech and verbosity manager keybindings."""

        if refresh:
            msg = f"SPEECH AND VERBOSITY MANAGER: Refreshing bindings.  Is desktop: {is_desktop}"
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self._setup_bindings()
        elif self._bindings.is_empty():
            self._setup_bindings()

        return self._bindings

    def get_handlers(self, refresh=False):
        """Returns the speech and verbosity manager handlers."""

        if refresh:
            msg = "SPEECH AND VERBOSITY MANAGER: Refreshing handlers."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            self._setup_handlers()

        return self._handlers

    def _setup_handlers(self):
        """Sets up the speech and verbosity input event handlers."""

        self._handlers = {}

        self._handlers["cycleCapitalizationStyleHandler"] = \
            input_event.InputEventHandler(
                self.cycle_capitalization_style,
                cmdnames.CYCLE_CAPITALIZATION_STYLE)

        self._handlers["cycleSpeakingPunctuationLevelHandler"] = \
            input_event.InputEventHandler(
                self.cycle_punctuation_level,
                cmdnames.CYCLE_PUNCTUATION_LEVEL)

        self._handlers["cycleSynthesizerHandler"] = \
            input_event.InputEventHandler(
                self.cycle_synthesizer,
                cmdnames.CYCLE_SYNTHESIZER)

        self._handlers["cycleKeyEchoHandler"] = \
            input_event.InputEventHandler(
                self.cycle_key_echo,
                cmdnames.CYCLE_KEY_ECHO)

        self._handlers["changeNumberStyleHandler"] = \
            input_event.InputEventHandler(
                self.change_number_style,
                cmdnames.CHANGE_NUMBER_STYLE)

        self._handlers["toggleSilenceSpeechHandler"] = \
            input_event.InputEventHandler(
                self.toggle_speech,
                cmdnames.TOGGLE_SPEECH)

        self._handlers["toggleSpeechVerbosityHandler"] = \
            input_event.InputEventHandler(
                self.toggle_verbosity,
                cmdnames.TOGGLE_SPEECH_VERBOSITY)

        self._handlers["toggleSpeakingIndentationJustificationHandler"] = \
            input_event.InputEventHandler(
                self.toggle_indentation_and_justification,
                cmdnames.TOGGLE_SPOKEN_INDENTATION_AND_JUSTIFICATION)

        self._handlers["toggleTableCellReadModeHandler"] = \
            input_event.InputEventHandler(
                self.toggle_table_cell_reading_mode,
                cmdnames.TOGGLE_TABLE_CELL_READ_MODE)

        self._handlers["decreaseSpeechRateHandler"] = \
            input_event.InputEventHandler(
                self.decrease_rate,
                cmdnames.DECREASE_SPEECH_RATE)

        self._handlers["increaseSpeechRateHandler"] = \
            input_event.InputEventHandler(
                self.increase_rate,
                cmdnames.INCREASE_SPEECH_RATE)

        self._handlers["decreaseSpeechPitchHandler"] = \
            input_event.InputEventHandler(
                self.decrease_pitch,
                cmdnames.DECREASE_SPEECH_PITCH)

        self._handlers["increaseSpeechPitchHandler"] = \
            input_event.InputEventHandler(
                self.increase_pitch,
                cmdnames.INCREASE_SPEECH_PITCH)

        self._handlers["decreaseSpeechVolumeHandler"] = \
            input_event.InputEventHandler(
                self.decrease_volume,
                cmdnames.DECREASE_SPEECH_VOLUME)

        self._handlers["increaseSpeechVolumeHandler"] = \
            input_event.InputEventHandler(
                self.increase_volume,
                cmdnames.INCREASE_SPEECH_VOLUME)

        msg = "SPEECH AND VERBOSITY MANAGER: Handlers set up."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def _setup_bindings(self):
        """Sets up the speech and verbosity key bindings."""

        self._bindings = keybindings.KeyBindings()

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("cycleCapitalizationStyleHandler")))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("cycleSpeakingPunctuationLevelHandler")))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("cycleSynthesizerHandler")))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("cycleKeyEchoHandler")))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("changeNumberStyleHandler")))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("decreaseSpeechRateHandler")))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("increaseSpeechRateHandler")))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("decreaseSpeechPitchHandler")))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("increaseSpeechPitchHandler")))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("decreaseSpeechVolumeHandler")))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("increaseSpeechVolumeHandler")))

        self._bindings.add(
            keybindings.KeyBinding(
                "",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.NO_MODIFIER_MASK,
                self._handlers.get("toggleSpeakingIndentationJustificationHandler")))

        self._bindings.add(
            keybindings.KeyBinding(
                "s",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("toggleSilenceSpeechHandler")))

        self._bindings.add(
            keybindings.KeyBinding(
                "v",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("toggleSpeechVerbosityHandler")))

        self._bindings.add(
            keybindings.KeyBinding(
                "F11",
                keybindings.DEFAULT_MODIFIER_MASK,
                keybindings.ORCA_MODIFIER_MASK,
                self._handlers.get("toggleTableCellReadModeHandler")))

        msg = "SPEECH AND VERBOSITY MANAGER: Bindings set up."
        debug.printMessage(debug.LEVEL_INFO, msg, True)

    def _get_server(self):
        return speech.get_speech_server()

    def decrease_rate(self, script, event=None):
        """Decreases the speech rate"""

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        server.decreaseSpeechRate()
        return True

    def increase_rate(self, script, event=None):
        """Increases the speech rate"""

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        server.increaseSpeechRate()
        return True

    def decrease_pitch(self, script, event=None):
        """Decreases the speech pitch"""

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        server.decreaseSpeechPitch()
        return True

    def increase_pitch(self, script, event=None):
        """Increase the speech pitch"""

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        server.increaseSpeechPitch()
        return True

    def decrease_volume(self, script, event=None):
        """Decreases the speech volume"""

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        server.decreaseSpeechVolume()
        return True

    def increase_volume(self, script, event=None):
        """Increases the speech volume"""

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        server.increaseSpeechVolume()
        return True

    def update_capitalization_style(self):
        """Updates the capitalization style based on the value in settings."""

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        server.updateCapitalizationStyle()
        return True

    def update_punctuation_level(self):
        """Updates the punctuation level based on the value in settings."""

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        server.updatePunctuationLevel()
        return True

    def cycle_synthesizer(self, script, event=None):
        """Cycle through the speech-dispatcher's available output modules."""

        server = self._get_server()
        if server is None:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get speech server."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        available = server.list_output_modules()
        if not available:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get output modules."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        current = server.getOutputModule()
        if not current:
            msg = "SPEECH AND VERBOSITY MANAGER: Cannot get current output module."
            debug.printMessage(debug.LEVEL_INFO, msg, True)
            return True

        index = available.index(current) + 1
        if index == len(available):
            index = 0

        server.setOutputModule(available[index])
        script.presentMessage(available[index])
        return True

    def cycle_capitalization_style(self, script, event=None):
        """Cycle through the speech-dispatcher capitalization styles."""

        manager = settings_manager.get_manager()
        current_style = manager.get_setting('capitalizationStyle')
        if current_style == settings.CAPITALIZATION_STYLE_NONE:
            new_style = settings.CAPITALIZATION_STYLE_SPELL
            full = messages.CAPITALIZATION_SPELL_FULL
            brief = messages.CAPITALIZATION_SPELL_BRIEF
        elif current_style == settings.CAPITALIZATION_STYLE_SPELL:
            new_style = settings.CAPITALIZATION_STYLE_ICON
            full = messages.CAPITALIZATION_ICON_FULL
            brief = messages.CAPITALIZATION_ICON_BRIEF
        else:
            new_style = settings.CAPITALIZATION_STYLE_NONE
            full = messages.CAPITALIZATION_NONE_FULL
            brief = messages.CAPITALIZATION_NONE_BRIEF

        manager.set_setting('capitalizationStyle', new_style)
        script.presentMessage(full, brief)
        self.update_capitalization_style()
        return True

    def cycle_punctuation_level(self, script, event=None):
        """Cycle through the punctuation levels for speech."""

        manager = settings_manager.get_manager()
        current_level = manager.get_setting('verbalizePunctuationStyle')
        if current_level == settings.PUNCTUATION_STYLE_NONE:
            new_level = settings.PUNCTUATION_STYLE_SOME
            full = messages.PUNCTUATION_SOME_FULL
            brief = messages.PUNCTUATION_SOME_BRIEF
        elif current_level == settings.PUNCTUATION_STYLE_SOME:
            new_level = settings.PUNCTUATION_STYLE_MOST
            full = messages.PUNCTUATION_MOST_FULL
            brief = messages.PUNCTUATION_MOST_BRIEF
        elif current_level == settings.PUNCTUATION_STYLE_MOST:
            new_level = settings.PUNCTUATION_STYLE_ALL
            full = messages.PUNCTUATION_ALL_FULL
            brief = messages.PUNCTUATION_ALL_BRIEF
        else:
            new_level = settings.PUNCTUATION_STYLE_NONE
            full = messages.PUNCTUATION_NONE_FULL
            brief = messages.PUNCTUATION_NONE_BRIEF

        manager.set_setting('verbalizePunctuationStyle', new_level)
        script.presentMessage(full, brief)
        self.update_punctuation_level()
        return True

    def cycle_key_echo(self, script, event=None):
        """Cycle through the key echo levels."""

        manager = settings_manager.get_manager()
        (new_key, new_word, new_sentence) = (False, False, False)
        key = manager.get_setting('enableKeyEcho')
        word = manager.get_setting('enableEchoByWord')
        sentence = manager.get_setting('enableEchoBySentence')

        if (key, word, sentence) == (False, False, False):
            (new_key, new_word, new_sentence) = (True, False, False)
            full = messages.KEY_ECHO_KEY_FULL
            brief = messages.KEY_ECHO_KEY_BRIEF
        elif (key, word, sentence) == (True, False, False):
            (new_key, new_word, new_sentence) = (False, True, False)
            full = messages.KEY_ECHO_WORD_FULL
            brief = messages.KEY_ECHO_WORD_BRIEF
        elif (key, word, sentence) == (False, True, False):
            (new_key, new_word, new_sentence) = (False, False, True)
            full = messages.KEY_ECHO_SENTENCE_FULL
            brief = messages.KEY_ECHO_SENTENCE_BRIEF
        elif (key, word, sentence) == (False, False, True):
            (new_key, new_word, new_sentence) = (True, True, False)
            full = messages.KEY_ECHO_KEY_AND_WORD_FULL
            brief = messages.KEY_ECHO_KEY_AND_WORD_BRIEF
        elif (key, word, sentence) == (True, True, False):
            (new_key, new_word, new_sentence) = (False, True, True)
            full = messages.KEY_ECHO_WORD_AND_SENTENCE_FULL
            brief = messages.KEY_ECHO_WORD_AND_SENTENCE_BRIEF
        else:
            (new_key, new_word, new_sentence) = (False, False, False)
            full = messages.KEY_ECHO_NONE_FULL
            brief = messages.KEY_ECHO_NONE_BRIEF

        manager.set_setting('enableKeyEcho', new_key)
        manager.set_setting('enableEchoByWord', new_word)
        manager.set_setting('enableEchoBySentence', new_sentence)
        script.presentMessage(full, brief)
        return True

    def change_number_style(self, script, event=None):
        """Changes spoken number style between digits and words."""

        manager = settings_manager.get_manager()
        speak_digits = manager.get_setting('speakNumbersAsDigits')
        if speak_digits:
            brief = messages.NUMBER_STYLE_WORDS_BRIEF
            full = messages.NUMBER_STYLE_WORDS_FULL
        else:
            brief = messages.NUMBER_STYLE_DIGITS_BRIEF
            full = messages.NUMBER_STYLE_DIGITS_FULL

        manager.set_setting('speakNumbersAsDigits', not speak_digits)
        script.presentMessage(full, brief)
        return True

    def toggle_speech(self, script, event=None):
        """Toggles speech."""

        manager = settings_manager.get_manager()
        script.presentationInterrupt()
        if manager.get_setting('silenceSpeech'):
            manager.set_setting('silenceSpeech', False)
            script.presentMessage(messages.SPEECH_ENABLED)
        elif not manager.get_setting('enableSpeech'):
            manager.set_setting('enableSpeech', True)
            speech.init()
            script.presentMessage(messages.SPEECH_ENABLED)
        else:
            script.presentMessage(messages.SPEECH_DISABLED)
            manager.set_setting('silenceSpeech', True)
        return True

    def toggle_verbosity(self, script, event=None):
        """Toggles speech verbosity level between verbose and brief."""

        manager = settings_manager.get_manager()
        value = manager.get_setting('speechVerbosityLevel')
        if value == settings.VERBOSITY_LEVEL_BRIEF:
            script.presentMessage(messages.SPEECH_VERBOSITY_VERBOSE)
            manager.set_setting('speechVerbosityLevel', settings.VERBOSITY_LEVEL_VERBOSE)
        else:
            script.presentMessage(messages.SPEECH_VERBOSITY_BRIEF)
            manager.set_setting('speechVerbosityLevel', settings.VERBOSITY_LEVEL_BRIEF)
        return True

    def toggle_indentation_and_justification(self, script, event=None):
        """Toggles the speaking of indentation and justification."""

        manager = settings_manager.get_manager()
        value = manager.get_setting('enableSpeechIndentation')
        manager.set_setting('enableSpeechIndentation', not value)
        if manager.get_setting('enableSpeechIndentation'):
            full = messages.INDENTATION_JUSTIFICATION_ON_FULL
            brief = messages.INDENTATION_JUSTIFICATION_ON_BRIEF
        else:
            full = messages.INDENTATION_JUSTIFICATION_OFF_FULL
            brief = messages.INDENTATION_JUSTIFICATION_OFF_BRIEF
        script.presentMessage(full, brief)
        return True

    def toggle_table_cell_reading_mode(self, script, event=None):
        """Toggles between speak cell and speak row."""

        table = AXTable.get_table(focus_manager.get_manager().get_locus_of_focus())
        if table is None:
            script.presentMessage(messages.TABLE_NOT_IN_A)
            return True

        if not script.utilities.getDocumentForObject(table):
            setting_name = 'readFullRowInGUITable'
        elif script.utilities.isSpreadSheetTable(table):
            setting_name = 'readFullRowInSpreadSheet'
        else:
            setting_name = 'readFullRowInDocumentTable'

        manager = settings_manager.get_manager()
        speak_row = manager.get_setting(setting_name)
        manager.set_setting(setting_name, not speak_row)

        if not speak_row:
            msg = messages.TABLE_MODE_ROW
        else:
            msg = messages.TABLE_MODE_CELL

        script.presentMessage(msg)
        return True

    @staticmethod
    def adjust_for_links(obj, line, start_offset):
        """Adjust line to include the word "link" after any hypertext links."""

        end_offset = start_offset + len(line)
        links = AXHypertext.get_all_links_in_range(obj, start_offset, end_offset)
        offsets = [AXHypertext.get_link_end_offset(link) for link in links]
        offsets = sorted([offset - start_offset for offset in offsets], reverse=True)
        tokens = list(line)
        for o in offsets:
            string = f" {messages.LINK}"
            if o < len(tokens) and tokens[o].isalnum():
                string += " "
            tokens[o:o] = string
        return "".join(tokens)

    @staticmethod
    def adjust_for_repeats(string):
        """Adjust line to include a description of repeated symbols."""

        def replacement(match):
            char = match.group(1)
            count = len(match.group(0))
            if match.start() > 0 and string[match.start() - 1].isalnum():
                return f" {messages.repeatedCharCount(char, count)}"
            return messages.repeatedCharCount(char, count)

        if len(string) < 4 or settings.repeatCharacterLimit < 4:
            return string

        pattern = re.compile(r"([^a-zA-Z0-9\s])\1{" + str(settings.repeatCharacterLimit - 1) + ",}")
        return re.sub(pattern, replacement, string)

_manager = SpeechAndVerbosityManager()
def get_manager():
    """Returns the Speech and Verbosity Manager"""

    return _manager
