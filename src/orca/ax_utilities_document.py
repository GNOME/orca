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

from . import debug, messages
from .ax_collection import AXCollection
from .ax_document import AXDocument
from .ax_utilities_hypertext import AXUtilitiesHypertext
from .ax_utilities_role import AXUtilitiesRole
from .ax_utilities_state import AXUtilitiesState
from .ax_utilities_table import AXUtilitiesTable
from .ax_utilities_text import AXUtilitiesText


class AXUtilitiesDocument:
    """Utilities for accessible documents."""

    @staticmethod
    def get_document_selected_texts(
        document: Atspi.Accessible,
    ) -> tuple[bool, list[str]]:
        """Returns whether the document getter succeeded and its selected text ranges."""

        success, selections = AXDocument.get_text_selections(document)
        if not success:
            return False, []

        strings = []
        for selection in selections:
            start_obj = selection.start_object
            end_obj = selection.end_object
            start_offset = selection.start_offset
            end_offset = selection.end_offset
            if start_obj is None or end_obj is None or start_offset < 0 or end_offset < 0:
                tokens = [
                    "AXUtilitiesDocument: Ignoring invalid text selection from",
                    document,
                    selection,
                ]
                debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                continue

            string = AXUtilitiesHypertext.expand_eocs_in_range(
                start_obj,
                start_offset,
                end_obj,
                end_offset,
                include_start=True,
                include_end=False,
            )
            if string:
                strings.append(string)

        tokens = [
            "AXUtilitiesDocument:",
            document,
            "has",
            len(strings),
            "selected text range(s).",
        ]
        debug.print_tokens(debug.LEVEL_INFO, tokens, True)
        return True, strings

    @staticmethod
    def get_document_text_selection_endpoints(
        document: Atspi.Accessible | None,
        root: Atspi.Accessible,
        search_text_objects: bool = True,
    ) -> tuple[
        tuple[Atspi.Accessible | None, int],
        tuple[Atspi.Accessible | None, int],
    ]:
        """Returns the inclusive start and exclusive end of the document selection."""

        if document is not None:
            success, selections = AXDocument.get_text_selections(document)
            if selections:
                selection = selections[0]
                if (
                    selection.start_object is not None
                    and selection.end_object is not None
                    and selection.start_offset >= 0
                    and selection.end_offset >= 0
                ):
                    start = selection.start_object, selection.start_offset
                    end = selection.end_object, selection.end_offset
                    tokens = [
                        "AXUtilitiesDocument: Text selection boundaries in",
                        document,
                        "are",
                        start,
                        end,
                    ]
                    debug.print_tokens(debug.LEVEL_INFO, tokens, True)
                    return start, end
            if success:
                return (None, -1), (None, -1)

        if not search_text_objects:
            msg = "AXUtilitiesDocument: Not searching text objects for selection boundaries."
            debug.print_message(debug.LEVEL_INFO, msg, True)
            return (None, -1), (None, -1)

        msg = "AXUtilitiesDocument: Getting text selection boundaries from text objects."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        start, end = AXUtilitiesText.get_text_selection_endpoints(root)
        if end[0] is not None:
            end = end[0], end[1] + 1
        return start, end

    @staticmethod
    def set_document_text_selection_endpoints(
        document: Atspi.Accessible,
        anchor_obj: Atspi.Accessible,
        anchor_offset: int,
        active_obj: Atspi.Accessible,
        active_offset: int,
    ) -> bool:
        """Sets the document selection from the anchor to the active position."""

        comparison = AXUtilitiesHypertext.compare_text_positions(
            anchor_obj,
            anchor_offset,
            active_obj,
            active_offset,
        )
        if comparison <= 0:
            return AXDocument.set_text_selection(
                document,
                anchor_obj,
                anchor_offset,
                active_obj,
                active_offset,
                False,
            )

        return AXDocument.set_text_selection(
            document,
            active_obj,
            active_offset,
            anchor_obj,
            anchor_offset,
            True,
        )

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

        mime_type = AXUtilitiesDocument.get_mime_type(document)
        if mime_type == "text/plain":
            return True
        if mime_type == "text/html":
            return AXUtilitiesDocument.get_uri(document).endswith(".txt")
        return False

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
