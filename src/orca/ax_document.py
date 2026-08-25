# Orca
#
# Copyright 2024 Igalia, S.L.
# Copyright 2024 GNOME Foundation Inc.
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

"""Wrapper for the Atspi.Document interface."""

from __future__ import annotations

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi, GLib

from . import debug
from .ax_object import AXObject


class AXDocument:
    """Wrapper for the Atspi.Document interface."""

    @staticmethod
    def get_text_selections(
        document: Atspi.Accessible,
    ) -> tuple[bool, list[Atspi.TextSelection]]:
        """Returns whether the getter succeeded and the document's text selections."""

        if not AXObject.supports_document(document):
            return False, []

        atspi_version = Atspi.get_version()  # pylint: disable=no-value-for-parameter
        getter_is_safe = (
            atspi_version >= (2, 61, 2)
            or (atspi_version[:2] == (2, 60) and atspi_version[2] >= 7)
            or (atspi_version[:2] == (2, 58) and atspi_version[2] >= 9)
        )
        if getter_is_safe:
            try:
                result = Atspi.Document.get_text_selections(document)
            except GLib.GError as error:
                tokens = ["AXDocument: Exception in get_text_selections:", error]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                return False, []

            selections = list(result or [])
            tokens = ["AXDocument:", document, "reports", len(selections), "text selection(s)."]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return True, selections

        # Older versions can return dangling accessible pointers:
        # https://gitlab.gnome.org/GNOME/at-spi2-core/-/work_items/243
        version_string = ".".join(str(part) for part in atspi_version)
        tokens = [
            "AXDocument: Not getting text selections due to at-spi2-core issue 243. Version:",
            version_string,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return False, []

    @staticmethod
    def set_text_selection(
        document: Atspi.Accessible,
        start_object: Atspi.Accessible,
        start_offset: int,
        end_object: Atspi.Accessible,
        end_offset: int,
        start_is_active: bool,
    ) -> bool:
        """Sets a single document text selection."""

        if not AXObject.supports_document(document):
            return False

        selection = Atspi.TextSelection()
        selection.start_object = start_object
        selection.start_offset = start_offset
        selection.end_object = end_object
        selection.end_offset = end_offset
        selection.start_is_active = start_is_active

        try:
            result = Atspi.Document.set_text_selections(document, [selection])
        except GLib.GError as error:
            tokens = ["AXDocument: Exception in set_text_selection:", error]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return False

        tokens = [
            "AXDocument: Set text selection in",
            document,
            "from",
            start_object,
            start_offset,
            "to",
            end_object,
            end_offset,
            "with start active:",
            start_is_active,
            ". Result:",
            result,
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def get_page_count(document: Atspi.Accessible) -> int:
        """Returns the page count of document."""

        if not AXObject.supports_document(document):
            return 0

        try:
            count = Atspi.Document.get_page_count(document)
        except GLib.GError as error:
            tokens = ["AXDocument: Exception in get_page_count:", error]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return 0

        tokens = ["AXDocument: Page count of", document, "is", count]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return count

    @staticmethod
    def get_locale(document: Atspi.Accessible) -> str:
        """Returns the locale of document."""

        if not AXObject.supports_document(document):
            return ""

        try:
            result = Atspi.Document.get_locale(document)
        except GLib.GError as error:
            tokens = ["AXDocument: Exception in get_locale:", error]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return ""

        if result is None:
            tokens = ["AXDocument: get_locale failed for", document]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return ""

        tokens = ["AXDocument: Locale of", document, "is '", result, "'"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def get_attributes_dict(document: Atspi.Accessible) -> dict[str, str]:
        """Returns a dict with the document-attributes of document."""

        if not AXObject.supports_document(document):
            return {}

        try:
            result = Atspi.Document.get_document_attributes(document)
        except GLib.GError as error:
            tokens = ["AXDocument: Exception in get_attributes_dict:", error]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return {}

        tokens = ["AXDocument: Attributes of", document, "are:", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result or {}
