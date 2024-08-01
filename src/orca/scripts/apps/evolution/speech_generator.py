# Orca
#
# Copyright (C) 2015 Igalia, S.L.
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

"""Produces speech presentation for accessible objects."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2015 Igalia, S.L."
__license__   = "LGPL"

from orca import speech_generator
from orca.ax_object import AXObject
from orca.ax_utilities import AXUtilities
from orca.scripts import web

class SpeechGenerator(web.SpeechGenerator, speech_generator.SpeechGenerator):
    """Produces speech presentation for accessible objects."""

    def __init__(self, script):
        super().__init__(script)
        self._cache = {}

    def _is_message_list_status_cell(self, obj):
        cached = self._cache.get(hash(obj), {})
        rv = cached.get("isMessageListStatusCell")
        if rv is None:
            rv = self._script.utilities.isMessageListStatusCell(obj)
            cached["isMessageListStatusCell"] = rv
            self._cache[hash(obj)] = cached

        return rv

    def _is_message_list_toggle_cell(self, obj):
        cached = self._cache.get(hash(obj), {})
        rv = cached.get("isMessageListToggleCell")
        if rv is None:
            rv = self._script.utilities.isMessageListToggleCell(obj)
            cached["isMessageListToggleCell"] = rv
            self._cache[hash(obj)] = cached

        return rv

    def _is_in_new_row(self, obj):
        cached = self._cache.get(hash(obj), {})
        rv = cached.get("isInNewRow")
        if rv is None:
            rv = self._script.utilities.cellRowChanged(obj)
            cached["isInNewRow"] = rv
            self._cache[hash(obj)] = cached

        return rv

    def _generate_state_checked_for_cell(self, obj, **args):
        if self._is_message_list_status_cell(obj):
            return []

        if self._is_message_list_toggle_cell(obj):
            if self._is_in_new_row(obj) or not AXUtilities.is_focused(obj):
                return []

        return super()._generate_state_checked_for_cell(obj, **args)

    def _generate_accessible_label(self, obj, **args):
        if self._is_message_list_toggle_cell(obj):
            return []

        return super()._generate_accessible_label(obj, **args)

    def _generate_accessible_name(self, obj, **args):
        if self._is_message_list_toggle_cell(obj) and not self._is_message_list_status_cell(obj):
            return []

        return super()._generate_accessible_name(obj, **args)

    def _generate_real_active_descendant_displayed_text(self, obj, **args):
        if self._is_message_list_toggle_cell(obj) and not self._is_message_list_status_cell(obj):
            if not AXUtilities.is_checked(obj):
                return []
            if AXUtilities.is_focused(obj) and not self._is_in_new_row(obj):
                return []

        return super()._generate_real_active_descendant_displayed_text(obj, **args)

    def _generate_accessible_role(self, obj, **args):
        if self._is_message_list_toggle_cell(obj) and not AXUtilities.is_focused(obj):
            return []

        return super()._generate_accessible_role(obj, **args)

    def _generate_state_unselected(self, obj, **args):
        if self._is_message_list_toggle_cell(obj) \
           or AXUtilities.is_tree_table(AXObject.get_parent(obj)):
            return []

        return super()._generate_state_unselected(obj, **args)

    def generate_speech(self, obj, **args):
        self._cache = {}
        results = super().generate_speech(obj, **args)
        self._cache = {}

        return results
