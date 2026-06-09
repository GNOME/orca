# Orca
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

"""Utilities for accessible documents."""

from __future__ import annotations

import urllib.parse

import gi

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

from . import messages
from .ax_collection import AXCollection
from .ax_document import AXDocument
from .ax_utilities_role import AXUtilitiesRole
from .ax_utilities_state import AXUtilitiesState
from .ax_utilities_table import AXUtilitiesTable


class AXUtilitiesDocument:
    """Utilities for accessible documents."""

    @staticmethod
    def get_uri(document: Atspi.Accessible) -> str:
        """Returns the uri of document."""

        attributes = AXDocument.get_attributes_dict(document)
        return attributes.get("DocURL", attributes.get("URI", ""))

    @staticmethod
    def get_mime_type(document: Atspi.Accessible) -> str:
        """Returns the mime type of document."""

        return AXDocument.get_attributes_dict(document).get("MimeType", "")

    @staticmethod
    def get_document_uri_fragment(document: Atspi.Accessible) -> str:
        """Returns the fragment portion of document's uri."""

        return urllib.parse.urlparse(AXUtilitiesDocument.get_uri(document)).fragment

    @staticmethod
    def is_plain_text(document: Atspi.Accessible) -> bool:
        """Returns True if document is a plain-text document."""

        return AXUtilitiesDocument.get_mime_type(document) == "text/plain"

    @staticmethod
    def is_pdf(document: Atspi.Accessible) -> bool:
        """Returns True if document is a PDF document."""

        mime_type = AXUtilitiesDocument.get_mime_type(document)
        if mime_type == "application/pdf":
            return True
        if mime_type == "text/html":
            return AXUtilitiesDocument.get_uri(document).endswith(".pdf")
        return False

    @staticmethod
    def _get_object_counts(document: Atspi.Accessible) -> dict[str, int]:
        """Returns a dictionary of object counts used in a document summary."""

        result = {
            "forms": 0,
            "landmarks": 0,
            "headings": 0,
            "tables": 0,
            "unvisited_links": 0,
            "visited_links": 0,
        }

        roles = [
            Atspi.Role.HEADING,
            Atspi.Role.LINK,
            Atspi.Role.TABLE,
            Atspi.Role.FORM,
            Atspi.Role.LANDMARK,
        ]

        rule = AXCollection.create_match_rule(
            roles=roles,
            role_match_type=Atspi.CollectionMatchType.ANY,
        )
        matches = AXCollection.get_all_matches(document, rule)

        for obj in matches:
            if AXUtilitiesRole.is_heading(obj):
                result["headings"] += 1
            elif AXUtilitiesRole.is_form(obj):
                result["forms"] += 1
            elif AXUtilitiesRole.is_table(obj) and not AXUtilitiesTable.is_layout_table(obj):
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
        counts = AXUtilitiesDocument._get_object_counts(document)
        result.append(messages.landmark_count(counts.get("landmarks", 0), only_if_found))
        result.append(messages.heading_count(counts.get("headings", 0), only_if_found))
        result.append(messages.form_count(counts.get("forms", 0), only_if_found))
        result.append(messages.table_count(counts.get("tables", 0), only_if_found))
        result.append(messages.visited_link_count(counts.get("visited_links", 0), only_if_found))
        result.append(
            messages.unvisited_link_count(counts.get("unvisited_links", 0), only_if_found),
        )
        result = list(filter(lambda x: x, result))
        if not result:
            return ""

        return messages.PAGE_SUMMARY_PREFIX % ", ".join(result)
