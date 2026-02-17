# Unit tests for pronunciation_dictionary_manager.py.
#
# Copyright 2026 Igalia, S.L.
# Author: Joanmarie Diggs <jdiggs@igalia.com>
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

# pylint: disable=wrong-import-position
# pylint: disable=protected-access
# pylint: disable=import-outside-toplevel

"""Unit tests for pronunciation_dictionary_manager.py."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext


@pytest.mark.unit
class TestPronunciationDictionaryManager:
    """Test PronunciationDictionaryManager class."""

    def _setup_manager(self, test_context: OrcaTestContext):
        """Set up mocks for pronunciation_dictionary_manager dependencies."""

        additional_modules = [
            "orca.guilabels",
            "orca.messages",
            "orca.preferences_grid_base",
            "orca.script_manager",
            "orca.settings_manager",
            "orca.speech_manager",
        ]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        # Set up guilabels with required constants
        guilabels = essential_modules["orca.guilabels"]
        guilabels.PRONUNCIATION = "Pronunciation"
        guilabels.PRONUNCIATION_DICTIONARY = "Pronunciation Dictionary"
        guilabels.PRONUNCIATION_DICTIONARY_INFO = "Add custom pronunciations."
        guilabels.DICTIONARY_NEW_ENTRY = "New Entry"
        guilabels.DICTIONARY_DELETE = "Delete"
        guilabels.DICTIONARY_EMPTY = "No entries"
        guilabels.DICTIONARY_ACTUAL_STRING = "Actual String"
        guilabels.DICTIONARY_REPLACEMENT_STRING = "Replacement String"
        guilabels.ADD_NEW_PRONUNCIATION = "Add New Pronunciation"
        guilabels.EDIT_PRONUNCIATION = "Edit Pronunciation"
        guilabels.DIALOG_CANCEL = "Cancel"
        guilabels.DIALOG_ADD = "Add"
        guilabels.DIALOG_EDIT = "Edit"

        # Set up messages
        messages = essential_modules["orca.messages"]
        messages.PRONUNCIATION_DELETED = "Pronunciation %s deleted"

        # Set up settings_manager
        settings_manager = essential_modules["orca.settings_manager"]
        manager_instance = settings_manager.get_manager.return_value
        manager_instance.get_pronunciations.return_value = {}
        manager_instance.get_general_settings.return_value = {"profile": ["Default", "default"]}

        # Set up speech_manager
        speech_manager_mock = essential_modules["orca.speech_manager"]
        speech_instance = speech_manager_mock.get_manager.return_value
        speech_instance.get_use_pronunciation_dictionary.return_value = True
        speech_instance.set_use_pronunciation_dictionary.return_value = True

        # Import and return the module
        from orca import pronunciation_dictionary_manager

        return pronunciation_dictionary_manager, essential_modules

    def test_get_manager_returns_singleton(self, test_context: OrcaTestContext) -> None:
        """Test get_manager returns the same instance."""

        module, _mocks = self._setup_manager(test_context)
        manager1 = module.get_manager()
        manager2 = module.get_manager()

        assert manager1 is manager2

    def test_manager_initial_state(self, test_context: OrcaTestContext) -> None:
        """Test manager initializes with empty dictionary."""

        module, _mocks = self._setup_manager(test_context)
        manager = module.get_manager()

        # Reset the dictionary to ensure clean state
        manager.set_dictionary({})

        assert manager.get_dictionary() == {}

    def test_get_pronunciation_returns_word_when_not_found(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test get_pronunciation returns the original word when not in dictionary."""

        module, _mocks = self._setup_manager(test_context)
        manager = module.get_manager()
        manager.set_dictionary({})

        result = manager.get_pronunciation("hello")

        assert result == "hello"

    def test_get_pronunciation_returns_replacement_when_found(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test get_pronunciation returns replacement when word is in dictionary."""

        module, _mocks = self._setup_manager(test_context)
        manager = module.get_manager()
        manager.set_dictionary({})

        manager.set_pronunciation("hello", "hi there")
        result = manager.get_pronunciation("hello")

        assert result == "hi there"

    def test_get_pronunciation_is_case_insensitive(self, test_context: OrcaTestContext) -> None:
        """Test get_pronunciation lookup is case insensitive."""

        module, _mocks = self._setup_manager(test_context)
        manager = module.get_manager()
        manager.set_dictionary({})

        manager.set_pronunciation("HELLO", "hi there")

        assert manager.get_pronunciation("hello") == "hi there"
        assert manager.get_pronunciation("Hello") == "hi there"
        assert manager.get_pronunciation("HELLO") == "hi there"

    def test_set_pronunciation_stores_lowercase_key(self, test_context: OrcaTestContext) -> None:
        """Test set_pronunciation stores key as lowercase."""

        module, _mocks = self._setup_manager(test_context)
        manager = module.get_manager()
        manager.set_dictionary({})

        manager.set_pronunciation("MixedCase", "replacement")

        dictionary = manager.get_dictionary()
        assert "mixedcase" in dictionary
        assert "MixedCase" not in dictionary

    def test_set_dictionary_replaces_entire_dictionary(self, test_context: OrcaTestContext) -> None:
        """Test set_dictionary replaces the entire dictionary."""

        module, _mocks = self._setup_manager(test_context)
        manager = module.get_manager()

        manager.set_pronunciation("old", "old replacement")
        manager.set_dictionary({"new": "new replacement"})

        dictionary = manager.get_dictionary()
        assert "old" not in dictionary
        assert dictionary.get("new") == "new replacement"

    def test_multiple_pronunciations(self, test_context: OrcaTestContext) -> None:
        """Test manager handles multiple pronunciations correctly."""

        module, _mocks = self._setup_manager(test_context)
        manager = module.get_manager()
        manager.set_dictionary({})

        manager.set_pronunciation("word1", "replacement1")
        manager.set_pronunciation("word2", "replacement2")
        manager.set_pronunciation("word3", "replacement3")

        assert manager.get_pronunciation("word1") == "replacement1"
        assert manager.get_pronunciation("word2") == "replacement2"
        assert manager.get_pronunciation("word3") == "replacement3"
        assert len(manager.get_dictionary()) == 3

    def test_set_pronunciation_overwrites_existing(self, test_context: OrcaTestContext) -> None:
        """Test set_pronunciation overwrites existing entry for same word."""

        module, _mocks = self._setup_manager(test_context)
        manager = module.get_manager()
        manager.set_dictionary({})

        manager.set_pronunciation("word", "first replacement")
        manager.set_pronunciation("word", "second replacement")

        assert manager.get_pronunciation("word") == "second replacement"
        assert len(manager.get_dictionary()) == 1


@pytest.mark.unit
class TestPronunciationDictionaryManagerIntegration:
    """Integration tests for pronunciation dictionary manager."""

    def _setup_manager(self, test_context: OrcaTestContext):
        """Set up mocks for pronunciation_dictionary_manager dependencies."""

        additional_modules = [
            "orca.guilabels",
            "orca.messages",
            "orca.preferences_grid_base",
            "orca.script_manager",
            "orca.settings_manager",
            "orca.speech_manager",
        ]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        # Set up guilabels with required constants
        guilabels = essential_modules["orca.guilabels"]
        guilabels.PRONUNCIATION = "Pronunciation"
        guilabels.PRONUNCIATION_DICTIONARY = "Pronunciation Dictionary"
        guilabels.PRONUNCIATION_DICTIONARY_INFO = "Add custom pronunciations."
        guilabels.DICTIONARY_NEW_ENTRY = "New Entry"
        guilabels.DICTIONARY_DELETE = "Delete"
        guilabels.DICTIONARY_EMPTY = "No entries"
        guilabels.DICTIONARY_ACTUAL_STRING = "Actual String"
        guilabels.DICTIONARY_REPLACEMENT_STRING = "Replacement String"
        guilabels.ADD_NEW_PRONUNCIATION = "Add New Pronunciation"
        guilabels.EDIT_PRONUNCIATION = "Edit Pronunciation"
        guilabels.DIALOG_CANCEL = "Cancel"
        guilabels.DIALOG_ADD = "Add"
        guilabels.DIALOG_EDIT = "Edit"

        # Set up messages
        messages = essential_modules["orca.messages"]
        messages.PRONUNCIATION_DELETED = "Pronunciation %s deleted"

        # Set up settings_manager
        settings_manager = essential_modules["orca.settings_manager"]
        manager_instance = settings_manager.get_manager.return_value
        manager_instance.get_pronunciations.return_value = {}
        manager_instance.get_general_settings.return_value = {"profile": ["Default", "default"]}

        # Set up speech_manager
        speech_manager_mock = essential_modules["orca.speech_manager"]
        speech_instance = speech_manager_mock.get_manager.return_value
        speech_instance.get_use_pronunciation_dictionary.return_value = True
        speech_instance.set_use_pronunciation_dictionary.return_value = True

        # Import and return the module
        from orca import pronunciation_dictionary_manager

        return pronunciation_dictionary_manager, essential_modules

    def test_pronunciation_application_to_text(self, test_context: OrcaTestContext) -> None:
        """Test that pronunciation dictionary can be used to process text."""

        module, _mocks = self._setup_manager(test_context)
        manager = module.get_manager()
        manager.set_dictionary({})

        manager.set_pronunciation("github", "git hub")
        manager.set_pronunciation("cli", "command line interface")

        # Simulate applying pronunciations to a sentence
        words = ["Check", " ", "out", " ", "the", " ", "GitHub", " ", "CLI"]
        result = "".join(map(manager.get_pronunciation, words))

        # GitHub becomes "git hub" because lookup is case insensitive
        assert "git hub" in result
        # CLI becomes "command line interface"
        assert "command line interface" in result

    def test_empty_dictionary_returns_original_words(self, test_context: OrcaTestContext) -> None:
        """Test that empty dictionary returns all original words unchanged."""

        module, _mocks = self._setup_manager(test_context)
        manager = module.get_manager()
        manager.set_dictionary({})

        words = ["Hello", " ", "world", "!"]
        result = "".join(map(manager.get_pronunciation, words))

        assert result == "Hello world!"
