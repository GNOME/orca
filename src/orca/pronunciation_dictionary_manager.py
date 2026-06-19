# Orca
#
# Copyright 2006-2008 Sun Microsystems Inc.
# Copyright 2011-2026 Igalia, S.L.
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

# pylint: disable=too-many-branches

"""Manager for user's pronunciation dictionary that maps words to what they sound like."""

from __future__ import annotations

from typing import TYPE_CHECKING

from . import gsettings_registry

if TYPE_CHECKING:
    from .pronunciation_dictionary_manager_preferences_grid import (
        PronunciationDictionaryPreferencesGrid,
    )
    from .scripts import default


@gsettings_registry.get_registry().gsettings_schema(
    "org.gnome.Orca.Pronunciations",
    name="pronunciations",
)
class PronunciationDictionaryManager:
    """Manager for the pronunciation dictionary."""

    def __init__(self) -> None:
        self._dictionary: dict[str, str] | None = None
        self._cached_app: str | None = None
        self._cached_profile: str = "default"
        self._suppressed: bool = False

    def create_preferences_grid(
        self,
        script: default.Script,
    ) -> PronunciationDictionaryPreferencesGrid:
        """Returns the GtkGrid containing the pronunciation dictionary UI."""

        # pylint: disable-next=import-outside-toplevel
        from .pronunciation_dictionary_manager_preferences_grid import (
            PronunciationDictionaryPreferencesGrid,
        )

        return PronunciationDictionaryPreferencesGrid(self, script)

    def suppress(self) -> None:
        """Suppresses pronunciation substitution without changing the user's preference."""

        self._suppressed = True

    def unsuppress(self) -> None:
        """Restores pronunciation substitution after a prior suppress call."""

        self._suppressed = False

    def _ensure_dictionary_current(self) -> dict[str, str]:
        """Reloads the pronunciation dictionary if the app or profile has changed."""

        registry = gsettings_registry.get_registry()
        current_app = registry.get_active_app()
        current_profile = registry.get_active_profile()
        if self._cached_app != current_app or self._cached_profile != current_profile:
            self._dictionary = None
            self._cached_app = current_app
            self._cached_profile = current_profile

        if self._dictionary is None:
            self._dictionary = registry.layered_lookup(
                "pronunciations",
                "entries",
                "a{ss}",
                default={},
            )

        return self._dictionary

    def get_pronunciation(self, word: str) -> str:
        """Returns the pronunciation for word, or word if not found."""

        if self._suppressed:
            return word
        dictionary = self._ensure_dictionary_current()
        return dictionary.get(word.lower(), word) or word

    def apply_to_words(self, words: list[str]) -> str:
        """Applies pronunciation dictionary to a list of words and joins the result."""

        if self._suppressed:
            return "".join(words)
        dictionary = self._ensure_dictionary_current()
        return "".join(dictionary.get(w.lower(), w) or w for w in words)

    def set_pronunciation(self, word: str, replacement: str) -> None:
        """Adds word/replacement pair."""

        # TODO - JD: Storing the words as lowercase is what we've done historically.
        # However, this means that on occasions where case sensitivity matters, there
        # will be a false positive (e.g., "US" vs "us"). Consider adding a checkbox
        # to the UI to allow users to choose case sensitivity for individual entries.

        key = word.lower()
        if self._dictionary is None:
            self._dictionary = {}
        self._dictionary[key] = replacement

    @gsettings_registry.get_registry().gsetting(
        key="entries",
        schema="pronunciations",
        gtype="a{ss}",
        default={},
        summary="Pronunciation dictionary entries",
    )
    def get_dictionary(self) -> dict[str, str]:
        """Returns the pronunciation dictionary."""

        if self._dictionary is None:
            return {}
        return self._dictionary

    def set_dictionary(self, value: dict[str, str]) -> None:
        """Sets the pronunciation dictionary, or invalidates the cache if empty."""

        self._dictionary = value or None


_manager = PronunciationDictionaryManager()


def get_manager() -> PronunciationDictionaryManager:
    """Returns the pronunciation-dictionary-manager singleton."""

    return _manager
