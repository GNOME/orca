# Orca
#
# Copyright 2015 Igalia, S.L.
#
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


"""Customized support for spellcheck in LibreOffice."""

from __future__ import annotations

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2015 Igalia, S.L."
__license__   = "LGPL"

from typing import TYPE_CHECKING

from orca import debug
from orca import messages
from orca import spellcheck
from orca.ax_object import AXObject
from orca.ax_text import AXText
from orca.ax_utilities import AXUtilities

if TYPE_CHECKING:
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi

    from orca.scripts import default

class SpellCheck(spellcheck.SpellCheck):
    """Customized support for spellcheck in LibreOffice."""

    def __init__(self, script: default.Script) -> None:
        super().__init__(script, has_change_to_entry=False)
        self._windows: dict[int, bool] = {}

    def _find_child_dialog(self, root: Atspi.Accessible | None) -> Atspi.Accessible | None:
        if root is None:
            return None

        if AXUtilities.is_dialog(root):
            return root

        return self._find_child_dialog(AXObject.get_child(root, 0))

    def _is_candidate_window(self, window: Atspi.Accessible) -> bool:
        if AXObject.is_dead(window):
            tokens = ["SOFFICE SPELL CHECK:", window, "is not spellcheck window because it's dead."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        rv = self._windows.get(hash(window))
        if rv is not None:
            tokens = ["SOFFICE SPELL CHECK:", window, "is spellcheck window:", rv]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return rv

        dialog = self._find_child_dialog(window)
        if not dialog:
            self._windows[hash(window)] = False
            tokens = ["SOFFICE SPELL CHECK:", window,
                      "is not spellcheck window because the dialog was not found."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        if AXObject.find_descendant(dialog, AXUtilities.is_page_tab_list) is not None:
            self._windows[hash(window)] = False
            self._windows[hash(dialog)] = False
            tokens = ["SOFFICE SPELL CHECK:", dialog,
                      "is not spellcheck dialog because a page tab list was found."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        rv = AXObject.find_descendant(dialog, AXUtilities.is_combo_box) is not None
        tokens = ["SOFFICE SPELL CHECK:", dialog,
                  "is spellcheck dialog based on combobox descendant:", rv]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        self._windows[hash(dialog)] = rv
        return rv

    def _is_error_widget(self, obj: Atspi.Accessible) -> bool:
        obj_id = AXObject.get_accessible_id(obj)
        if obj_id.lower().startswith("error"):
            tokens = ["SPELL CHECK:", obj, f"with id: '{obj_id}' is the error widget"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True

        if not AXObject.supports_editable_text(obj):
            return False
        return AXUtilities.is_focusable(obj) and AXUtilities.is_multi_line(obj)

    def get_misspelled_word(self) -> str:
        length = AXText.get_character_count(self._error_widget)
        offset, string = 0, ""
        while 0 <= offset < length:
            attrs, start, end = AXText.get_text_attributes_at_offset(self._error_widget, offset)
            if attrs.get("fg-color", "").replace(" ", "") == "255,0,0":
                return AXText.get_substring(self._error_widget, start, end)
            offset = max(end, offset + 1)

        return string

    def present_context(self) -> bool:
        if not self.is_active():
            return False

        string = AXText.get_all_text(self._error_widget)
        if not string:
            return False

        msg = messages.MISSPELLED_WORD_CONTEXT % string
        voice = self._script.speech_generator.voice(string=msg)
        self._script.speak_message(msg, voice=voice)
        return True
