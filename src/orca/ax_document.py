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

# pylint: disable=wrong-import-position

"""Utilities for obtaining document-related information about accessible objects."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2024 Igalia, S.L." \
                "Copyright (c) 2024 GNOME Foundation Inc."
__license__   = "LGPL"

import threading
import time
import urllib.parse

import gi
gi.require_version("Atspi", "2.0")
from gi.repository import Atspi
from gi.repository import GLib

from . import debug
from . import messages
from .ax_collection import AXCollection
from .ax_object import AXObject
from .ax_table import AXTable
from .ax_utilities_role import AXUtilitiesRole
from .ax_utilities_state import AXUtilitiesState

class AXDocument:
    """Utilities for obtaining document-related information about accessible objects."""

    LAST_KNOWN_PAGE: dict[int, int] = {}
    _lock = threading.Lock()

    @staticmethod
    def _clear_stored_data() -> None:
        """Clears any data we have cached for objects"""

        while True:
            time.sleep(60)
            msg = "AXDocument: Clearing local cache."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            AXDocument.LAST_KNOWN_PAGE.clear()

    @staticmethod
    def start_cache_clearing_thread() -> None:
        """Starts thread to periodically clear cached details."""

        thread = threading.Thread(target=AXDocument._clear_stored_data)
        thread.daemon = True
        thread.start()

    @staticmethod
    def did_page_change(document: Atspi.Accessible) -> bool:
        """Returns True if the current page changed."""

        if not AXObject.supports_document(document):
            return False

        old_page = AXDocument.LAST_KNOWN_PAGE.get(hash(document))
        result = old_page != AXDocument._get_current_page(document)
        if result:
            tokens = ["AXDocument: Previous page of", document, f"was {old_page}"]
            debug.print_tokens(debug.LEVEL_INFO, tokens, True)

        return result

    @staticmethod
    def _get_current_page(document: Atspi.Accessible) -> int:
        """Returns the current page of document."""

        if not AXObject.supports_document(document):
            return 0

        try:
            page = Atspi.Document.get_current_page_number(document)
        except GLib.GError as error:
            msg = f"AXDocument: Exception in _get_current_page: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return 0

        tokens = ["AXDocument: Current page of", document, f"is {page}"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return page

    @staticmethod
    def get_current_page(document: Atspi.Accessible) -> int:
        """Returns the current page of document."""

        if not AXObject.supports_document(document):
            return 0

        page = AXDocument._get_current_page(document)
        AXDocument.LAST_KNOWN_PAGE[hash(document)] = page
        return page

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

        tokens = ["AXDocument: Locale of", document, f"is '{result}'"]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result

    @staticmethod
    def _get_attributes_dict(document: Atspi.Accessible) -> dict[str, str]:
        """Returns a dict with the document-attributes of document."""

        if not AXObject.supports_document(document):
            return {}

        try:
            result = Atspi.Document.get_document_attributes(document)
        except GLib.GError as error:
            msg = f"AXDocument: Exception in _get_attributes_dict: {error}"
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return {}

        tokens = ["AXDocument: Attributes of", document, "are:", result]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return result or {}

    @staticmethod
    def get_uri(document: Atspi.Accessible) -> str:
        """Returns the uri of document."""

        if not AXObject.supports_document(document):
            return ""

        attributes = AXDocument._get_attributes_dict(document)
        return attributes.get("DocURL", attributes.get("URI", ""))

    @staticmethod
    def get_mime_type(document: Atspi.Accessible) -> str:
        """Returns the uri of document."""

        if not AXObject.supports_document(document):
            return ""

        attributes = AXDocument._get_attributes_dict(document)
        return attributes.get("MimeType", "")

    @staticmethod
    def is_plain_text(document: Atspi.Accessible) -> bool:
        """Returns True if document is a plain-text document."""

        return AXDocument.get_mime_type(document) == "text/plain"

    @staticmethod
    def is_pdf(document: Atspi.Accessible) -> bool:
        """Returns True if document is a PDF document."""

        mime_type = AXDocument.get_mime_type(document)
        if mime_type == "application/pdf":
            return True
        if mime_type == "text/html":
            return AXDocument.get_uri(document).endswith(".pdf")
        return False

    @staticmethod
    def get_document_uri_fragment(document: Atspi.Accessible) -> str:
        """Returns the fragment portion of document's uri."""

        result = urllib.parse.urlparse(AXDocument.get_uri(document))
        return result.fragment

    @staticmethod
    def _get_object_counts(document: Atspi.Accessible) -> dict[str, int]:
        """Returns a dictionary of object counts used in a document summary."""

        result = {"forms": 0,
                  "landmarks": 0,
                  "headings": 0,
                  "tables": 0,
                  "unvisited_links": 0,
                  "visited_links": 0}

        roles = [Atspi.Role.HEADING,
                 Atspi.Role.LINK,
                 Atspi.Role.TABLE,
                 Atspi.Role.FORM,
                 Atspi.Role.LANDMARK]

        rule = AXCollection.create_match_rule(roles=roles)
        matches = AXCollection.get_all_matches(document, rule)

        for obj in matches:
            if AXUtilitiesRole.is_heading(obj):
                result["headings"] += 1
            elif AXUtilitiesRole.is_form(obj):
                result["forms"] += 1
            elif AXUtilitiesRole.is_table(obj) and not AXTable.is_layout_table(obj):
                result["tables"] += 1
            elif AXUtilitiesRole.is_link(obj):
                if AXUtilitiesState.is_visited(obj):
                    result["visited_links"] += 1
                else:
                    result["unvisited_links"] += 1
            elif AXUtilitiesRole.is_landmark(obj):
                result["landmarks"] += 1

        return result

    @staticmethod
    def get_document_summary(document: Atspi.Accessible, only_if_found: bool = True) -> str:
        """Returns a string summarizing the document's structure and objects of interest."""

        result = []
        counts = AXDocument._get_object_counts(document)
        result.append(messages.landmark_count(counts.get("landmarks", 0), only_if_found))
        result.append(messages.heading_count(counts.get("headings", 0), only_if_found))
        result.append(messages.form_count(counts.get("forms", 0), only_if_found))
        result.append(messages.table_count(counts.get("tables", 0), only_if_found))
        result.append(messages.visited_link_count(counts.get("visited_links", 0), only_if_found))
        result.append(messages.unvisited_link_count(
            counts.get("unvisited_links", 0), only_if_found))
        result = list(filter(lambda x: x, result))
        if not result:
            return ""

        return messages.PAGE_SUMMARY_PREFIX % ", ".join(result)
