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
    def get_page_count(document: Atspi.Accessible) -> int:
        """Returns the page count of document."""

        if not AXObject.supports_document(document):
            return 0

        try:
            count = Atspi.Document.get_page_count(document)
        except GLib.GError as error:
            msg = f"AXDocument: Exception in get_page_count: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return 0

        tokens = ["AXDocument: Page count of", document, f"is {count}"]
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
            msg = f"AXDocument: Exception in get_locale: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return ""

        if result is None:
            tokens = ["AXDocument: get_locale failed for", document]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)
            return ""

        tokens = ["AXDocument: Locale of", document, f"is '{result}'"]
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
            msg = f"AXDocument: Exception in get_attributes_dict: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return {}

        tokens = ["AXDocument: Attributes of", document, "are:", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result or {}
