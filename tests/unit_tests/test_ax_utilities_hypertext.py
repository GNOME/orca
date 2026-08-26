# Unit tests for ax_utilities_hypertext.py methods.
#
# Copyright 2025 Igalia, S.L.
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

# pylint: disable=protected-access
# pylint: disable=wrong-import-position
# pylint: disable=import-outside-toplevel

"""Unit tests for ax_utilities_hypertext.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from .orca_test_context import OrcaTestContext


@pytest.mark.unit
class TestAXUtilitiesHypertext:
    """Test AXUtilitiesHypertext class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for ax_utilities_hypertext dependencies."""

        additional_modules = [
            "orca.ax_hypertext",
            "orca.ax_text",
            "orca.ax_utilities_object",
            "orca.ax_utilities_role",
        ]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        debug_mock = essential_modules["orca.debug"]
        debug_mock.print_message = test_context.Mock()
        debug_mock.print_tokens = test_context.Mock()
        debug_mock.LEVEL_INFO = 800
        debug_mock.debugLevel = 1000

        essential_modules[
            "orca.ax_utilities_object"
        ].AXUtilitiesObject.find_descendant = test_context.Mock(return_value=None)
        essential_modules["orca.ax_utilities_role"].AXUtilitiesRole.is_grid = test_context.Mock(
            return_value=False
        )
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_combo_box = test_context.Mock(return_value=False)
        essential_modules["orca.ax_utilities_role"].AXUtilitiesRole.is_button = test_context.Mock(
            return_value=False
        )
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_block_quote = test_context.Mock(return_value=False)
        essential_modules["orca.ax_utilities_role"].AXUtilitiesRole.is_embedded = test_context.Mock(
            return_value=False
        )
        essential_modules["orca.ax_utilities_role"].AXUtilitiesRole.is_math = test_context.Mock(
            return_value=False
        )
        essential_modules["orca.ax_utilities_role"].AXUtilitiesRole.is_list_box = test_context.Mock(
            return_value=False
        )
        essential_modules["orca.ax_utilities_role"].AXUtilitiesRole.is_table = test_context.Mock(
            return_value=False
        )
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_table_row = test_context.Mock(return_value=False)
        essential_modules[
            "orca.ax_utilities_role"
        ].AXUtilitiesRole.is_menu_item_of_any_kind = test_context.Mock(return_value=False)
        for name in (
            "is_heading",
            "is_list",
            "is_list_item",
            "is_paragraph",
            "is_section",
            "is_table_cell",
        ):
            setattr(
                essential_modules["orca.ax_utilities_role"].AXUtilitiesRole,
                name,
                test_context.Mock(return_value=False),
            )

        return essential_modules

    def test_expand_eocs_in_range_in_same_object(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test endpoint inclusion is converted for the original expander."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.ax_utilities_hypertext import AXObject, AXText, AXUtilitiesHypertext

        obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "supports_text", return_value=True)
        test_context.patch_object(AXText, "get_character_count", return_value=10)
        essential_modules[
            "orca.ax_utilities_object"
        ].AXUtilitiesObject.get_common_ancestor.return_value = obj

        strings = {(obj, 2, 8): "selected"}
        test_context.patch_object(
            AXText,
            "get_substring",
            side_effect=lambda obj, start, end: strings[obj, start, end],
        )
        result = AXUtilitiesHypertext.expand_eocs_in_range(obj, 2, obj, 7)

        assert result == "selected"

    def test_expand_eocs_in_range_stops_at_embedded_child_endpoint(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test expansion recurses into the child containing the end endpoint."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.ax_utilities_hypertext import (
            AXHypertext,
            AXObject,
            AXText,
            AXUtilitiesHypertext,
        )

        parent = test_context.Mock(spec=Atspi.Accessible)
        child = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXUtilitiesHypertext, "compare_text_positions", return_value=-1)
        essential_modules[
            "orca.ax_utilities_object"
        ].AXUtilitiesObject.get_common_ancestor.return_value = parent
        test_context.patch_object(AXObject, "supports_text", return_value=True)
        test_context.patch_object(
            AXObject,
            "get_parent",
            side_effect=lambda obj: parent if obj == child else None,
        )
        test_context.patch_object(
            AXText,
            "get_character_count",
            side_effect=lambda obj: 12 if obj == parent else 9,
        )
        test_context.patch_object(AXHypertext, "get_character_offset_in_parent", return_value=11)

        strings = {(child, 0, 9): "Wikipedia"}
        test_context.patch_object(
            AXText,
            "get_substring",
            side_effect=lambda obj, start, end: strings[obj, start, end],
        )
        result = AXUtilitiesHypertext.expand_eocs_in_range(
            parent,
            10,
            child,
            8,
            include_start=False,
        )

        assert result == "Wikipedia"

    def test_expand_eocs_in_range_combines_nested_text(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test expansion continues from an embedded child into ancestor text."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.ax_utilities_hypertext import (
            AXHypertext,
            AXObject,
            AXText,
            AXUtilitiesHypertext,
        )

        section = test_context.Mock(spec=Atspi.Accessible)
        heading = test_context.Mock(spec=Atspi.Accessible)
        link = test_context.Mock(spec=Atspi.Accessible)
        parents = {link: heading, heading: section, section: None}
        counts = {section: 2, heading: 12, link: 9}
        offsets = {heading: 0, link: 11}
        test_context.patch_object(AXUtilitiesHypertext, "compare_text_positions", return_value=-1)
        essential_modules[
            "orca.ax_utilities_object"
        ].AXUtilitiesObject.get_common_ancestor.return_value = section
        test_context.patch_object(AXObject, "supports_text", return_value=True)
        test_context.patch_object(AXObject, "get_parent", side_effect=parents.get)
        test_context.patch_object(AXText, "get_character_count", side_effect=counts.get)
        test_context.patch_object(
            AXHypertext,
            "get_character_offset_in_parent",
            side_effect=offsets.get,
        )
        strings = {
            (heading, 10, 12): " Wikipedia",
            (section, 1, 2): ",",
        }
        test_context.patch_object(
            AXText,
            "get_substring",
            side_effect=lambda obj, start, end: strings[obj, start, end],
        )

        result = AXUtilitiesHypertext.expand_eocs_in_range(
            heading,
            9,
            section,
            1,
            include_start=False,
        )

        assert result == " Wikipedia,"

    def test_expand_eocs_in_range_separates_adjacent_block_elements(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test expanded text from adjacent block elements has separators."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.ax_utilities_hypertext import AXObject, AXText, AXUtilitiesHypertext

        root = test_context.Mock(spec=Atspi.Accessible)
        children = [test_context.Mock(spec=Atspi.Accessible) for _index in range(3)]
        strings = dict(zip(children, ("Fruit", "Apple", "Pear"), strict=True))
        test_context.patch_object(AXUtilitiesHypertext, "compare_text_positions", return_value=-1)
        essential_modules[
            "orca.ax_utilities_object"
        ].AXUtilitiesObject.get_common_ancestor.return_value = root
        test_context.patch_object(
            AXObject,
            "supports_text",
            side_effect=lambda obj: obj != root,
        )
        test_context.patch_object(
            AXObject,
            "get_parent",
            side_effect=lambda obj: root if obj in children else None,
        )
        test_context.patch_object(
            AXObject,
            "get_index_in_parent",
            side_effect=children.index,
        )
        test_context.patch_object(
            AXObject,
            "get_child_count",
            side_effect=lambda obj: len(children) if obj == root else 0,
        )
        test_context.patch_object(
            AXObject,
            "get_child",
            side_effect=lambda obj, index: children[index] if obj == root else None,
        )
        test_context.patch_object(
            AXText,
            "get_character_count",
            side_effect=lambda obj: len(strings[obj]),
        )
        test_context.patch_object(
            AXText,
            "get_substring",
            side_effect=lambda obj, start, end: strings[obj][start:end],
        )
        essential_modules["orca.ax_utilities_role"].AXUtilitiesRole.is_paragraph.side_effect = (
            lambda obj: obj in children
        )

        result = AXUtilitiesHypertext.expand_eocs_in_range(
            children[0],
            0,
            children[-1],
            len(strings[children[-1]]) - 1,
        )

        assert result == "Fruit Apple Pear"

    def test_expand_eocs_in_range_separates_boundary_from_intermediate_block(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test a boundary element is separated from a block expanded through its parent."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.ax_utilities_hypertext import (
            AXHypertext,
            AXObject,
            AXText,
            AXUtilitiesHypertext,
        )

        root = test_context.Mock(spec=Atspi.Accessible)
        heading = test_context.Mock(spec=Atspi.Accessible)
        paragraph = test_context.Mock(spec=Atspi.Accessible)
        quote = test_context.Mock(spec=Atspi.Accessible)
        children = [heading, paragraph, quote]
        counts = {root: 3, heading: 21, paragraph: 16, quote: 12}
        offsets = {heading: 0, paragraph: 1, quote: 2}
        expansions = {
            (heading, 0, 21): "Structural navigation",
            (root, 1, 2): "Intro paragraph.   ",
            (quote, 0, 12): "Quoted text.",
        }
        test_context.patch_object(AXUtilitiesHypertext, "compare_text_positions", return_value=-1)
        essential_modules[
            "orca.ax_utilities_object"
        ].AXUtilitiesObject.get_common_ancestor.return_value = root
        test_context.patch_object(AXObject, "supports_text", return_value=True)
        test_context.patch_object(
            AXObject,
            "get_parent",
            side_effect=lambda obj: root if obj in children else None,
        )
        test_context.patch_object(AXText, "get_character_count", side_effect=counts.get)
        test_context.patch_object(
            AXHypertext,
            "get_character_offset_in_parent",
            side_effect=offsets.get,
        )
        test_context.patch_object(
            AXUtilitiesHypertext,
            "expand_eocs",
            side_effect=lambda obj, start, end: expansions[obj, start, end],
        )
        essential_modules["orca.ax_utilities_role"].AXUtilitiesRole.is_heading.side_effect = (
            lambda obj: obj == heading
        )
        essential_modules["orca.ax_utilities_role"].AXUtilitiesRole.is_block_quote.side_effect = (
            lambda obj: obj == quote
        )

        result = AXUtilitiesHypertext.expand_eocs_in_range(heading, 0, quote, 11)

        assert result == "Structural navigation Intro paragraph. Quoted text."

    def test_expand_eocs_in_range_separates_combo_box_label_and_options(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test a combo-box label and its options are separated in expanded text."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.ax_utilities_hypertext import (
            AXHypertext,
            AXObject,
            AXText,
            AXUtilitiesHypertext,
        )

        paragraph = test_context.Mock(spec=Atspi.Accessible)
        label = test_context.Mock(spec=Atspi.Accessible)
        combo_box = test_context.Mock(spec=Atspi.Accessible)
        apple = test_context.Mock(spec=Atspi.Accessible)
        pear = test_context.Mock(spec=Atspi.Accessible)
        children = {
            paragraph: [label, combo_box],
            combo_box: [apple, pear],
        }
        parents = {
            label: paragraph,
            combo_box: paragraph,
            apple: combo_box,
            pear: combo_box,
        }
        strings = {
            label: "Fruit",
            apple: "Apple",
            pear: "Pear",
        }
        test_context.patch_object(AXUtilitiesHypertext, "compare_text_positions", return_value=-1)
        essential_modules[
            "orca.ax_utilities_object"
        ].AXUtilitiesObject.get_common_ancestor.return_value = paragraph
        test_context.patch_object(
            AXObject,
            "supports_text",
            side_effect=lambda obj: obj != combo_box,
        )
        test_context.patch_object(AXObject, "get_parent", side_effect=parents.get)
        test_context.patch_object(
            AXObject,
            "get_index_in_parent",
            side_effect=lambda obj: children[parents[obj]].index(obj),
        )
        test_context.patch_object(
            AXObject,
            "get_child_count",
            side_effect=lambda obj: len(children.get(obj, [])),
        )
        test_context.patch_object(
            AXObject,
            "get_child",
            side_effect=lambda obj, index: children.get(obj, [])[index],
        )
        test_context.patch_object(
            AXText,
            "get_character_count",
            side_effect=lambda obj: 2 if obj == paragraph else len(strings[obj]),
        )
        test_context.patch_object(
            AXText,
            "get_substring",
            side_effect=lambda obj, start, end: strings[obj][start:end],
        )
        test_context.patch_object(
            AXHypertext,
            "get_character_offset_in_parent",
            side_effect=children[paragraph].index,
        )
        essential_modules["orca.ax_utilities_role"].AXUtilitiesRole.is_combo_box.side_effect = (
            lambda obj: obj == combo_box
        )

        result = AXUtilitiesHypertext.expand_eocs_in_range(label, 0, pear, 3)

        assert result == "Fruit Apple Pear"

    def test_expand_eocs_replaces_embedded_child_with_its_text(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test single-object expansion delegates embedded child expansion."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_hypertext import AXText, AXUtilitiesHypertext

        parent = test_context.Mock(spec=Atspi.Accessible)
        child = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXText,
            "get_substring",
            side_effect=lambda obj, _start, _end: (
                "before \ufffc after" if obj == parent else "child"
            ),
        )
        test_context.patch_object(AXText, "get_character_count", return_value=5)
        test_context.patch_object(AXUtilitiesHypertext, "find_child_at_offset", return_value=child)
        result = AXUtilitiesHypertext.expand_eocs(parent, 0, -1)

        assert result == "before child after"

    def test_expand_eocs_does_not_include_button_text(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test text from a button child is not included in its parent."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_hypertext import (
            AXObject,
            AXText,
            AXUtilitiesHypertext,
            AXUtilitiesRole,
        )

        parent = test_context.Mock(spec=Atspi.Accessible)
        button = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "supports_text", return_value=True)
        test_context.patch_object(AXText, "get_character_count", return_value=10)
        strings = {(parent, 0, -1): "Question \ufffc"}
        test_context.patch_object(
            AXText,
            "get_substring",
            side_effect=lambda obj, start, end: strings[obj, start, end],
        )
        test_context.patch_object(AXUtilitiesHypertext, "find_child_at_offset", return_value=button)
        AXUtilitiesRole.is_button.side_effect = lambda obj: obj == button

        assert AXUtilitiesHypertext.expand_eocs(parent) == "Question "

    def test_expand_eocs_does_not_expand_grid(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test grid contents are not expanded."""

        dependencies = self._setup_dependencies(test_context)
        from orca.ax_utilities_hypertext import (
            AXText,
            AXUtilitiesHypertext,
            AXUtilitiesRole,
        )

        parent = test_context.Mock(spec=Atspi.Accessible)
        grid = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXText,
            "get_substring",
            side_effect=lambda obj, _start, _end: "before \ufffc after" if obj == parent else "",
        )
        test_context.patch_object(AXText, "get_character_count", return_value=5)
        test_context.patch_object(AXUtilitiesHypertext, "find_child_at_offset", return_value=grid)
        AXUtilitiesRole.is_grid.side_effect = lambda obj: obj == grid

        assert AXUtilitiesHypertext.expand_eocs(parent, 0, -1) == "before  after"
        dependencies[
            "orca.ax_utilities_object"
        ].AXUtilitiesObject.find_descendant.assert_not_called()

    def test_expand_eocs_does_not_expand_object_with_embedded_role(
        self,
        test_context: OrcaTestContext,
    ) -> None:
        """Test EOCs are not expanded in an object with the embedded role."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_hypertext import (
            AXObject,
            AXText,
            AXUtilitiesHypertext,
            AXUtilitiesRole,
        )

        obj = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(AXObject, "supports_text", return_value=True)
        test_context.patch_object(AXText, "get_character_count", return_value=10)
        test_context.patch_object(AXText, "get_substring", return_value="application child text")
        AXUtilitiesRole.is_embedded.return_value = True

        assert AXUtilitiesHypertext.expand_eocs(obj) == ""

    @pytest.mark.parametrize(
        "parent_offset,child_offset,expected_result",
        [
            pytest.param(3, 0, 0, id="equivalent_child_start"),
            pytest.param(3, 1, -1, id="parent_boundary_before_child_content"),
            pytest.param(4, 1, 1, id="parent_position_after_child"),
        ],
    )
    def test_compare_text_positions_with_hypertext_descendant(
        self,
        test_context: OrcaTestContext,
        parent_offset: int,
        child_offset: int,
        expected_result: int,
    ) -> None:
        """Test text positions account for a child's offset in ancestor hypertext."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_hypertext import (
            AXHypertext,
            AXObject,
            AXUtilitiesHypertext,
            AXUtilitiesObject,
        )

        parent = test_context.Mock(spec=Atspi.Accessible)
        child = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(
            AXUtilitiesObject,
            "is_ancestor",
            side_effect=lambda obj, ancestor: obj == child and ancestor == parent,
        )
        test_context.patch_object(AXObject, "get_parent", return_value=parent)
        test_context.patch_object(
            AXHypertext,
            "get_character_offset_in_parent",
            return_value=3,
        )

        result = AXUtilitiesHypertext.compare_text_positions(
            parent,
            parent_offset,
            child,
            child_offset,
        )

        assert result == expected_result

    @pytest.mark.parametrize(
        "start_offset, end_offset, link_ranges, expected_count",
        [
            pytest.param(0, 10, [], 0, id="no_links"),
            pytest.param(0, 10, [(5, 8)], 1, id="link_within_range"),
            pytest.param(0, 10, [(12, 15)], 0, id="link_outside_range"),
            pytest.param(0, 10, [(0, 5), (8, 10)], 2, id="multiple_links_in_range"),
            pytest.param(5, 15, [(0, 6), (10, 20)], 2, id="links_partially_overlapping"),
            pytest.param(10, 15, [(10, 12)], 1, id="link_start_matches_range_start"),
        ],
    )
    def test_get_all_links_in_range(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        start_offset,
        end_offset,
        link_ranges,
        expected_count,
        test_context,
    ) -> None:
        """Test AXUtilitiesHypertext.get_all_links_in_range."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_utilities_hypertext import AXUtilitiesHypertext

        mock_links = [test_context.Mock(spec=Atspi.Hyperlink) for _ in link_ranges]

        def get_offset(link, is_start=True) -> int:
            for i, mock_link in enumerate(mock_links):
                if link == mock_link:
                    return link_ranges[i][0 if is_start else 1]
            return -1

        test_context.patch(
            "orca.ax_hypertext.AXHypertext.get_link_count",
            return_value=len(mock_links),
        )

        def mock_get_link_at_index(_obj, index):
            return mock_links[index] if index < len(mock_links) else None

        test_context.patch(
            "orca.ax_hypertext.AXHypertext.get_link_at_index",
            side_effect=mock_get_link_at_index,
        )
        test_context.patch(
            "orca.ax_hypertext.AXHypertext.get_link_start_offset",
            side_effect=lambda link: get_offset(link, True),
        )
        test_context.patch(
            "orca.ax_hypertext.AXHypertext.get_link_end_offset",
            side_effect=lambda link: get_offset(link, False),
        )
        result = AXUtilitiesHypertext.get_all_links_in_range(
            mock_accessible, start_offset, end_offset
        )
        assert len(result) == expected_count

    @pytest.mark.parametrize(
        "uri, remove_extension, expected_result",
        [
            pytest.param(
                "https://example.com/path/file.html",
                False,
                "file.html",
                id="path_with_extension",
            ),
            pytest.param(
                "https://example.com/path/file.html",
                True,
                "file",
                id="path_with_extension_removed",
            ),
            pytest.param("https://example.com/", False, "", id="no_path_component"),
            pytest.param("", False, "", id="empty_uri"),
            pytest.param("https://example.com/simple", False, "simple", id="path_no_extension"),
            pytest.param(
                "https://example.com/simple",
                True,
                "simple",
                id="path_no_extension_capitalized",
            ),
            pytest.param("file:///home/user/document.pdf", False, "document.pdf", id="file_uri"),
            pytest.param(
                "file:///home/user/document.pdf",
                True,
                "document",
                id="file_uri_extension_removed",
            ),
        ],
    )
    def test_get_link_basename(
        self,
        uri,
        remove_extension,
        expected_result,
        test_context,
    ) -> None:
        """Test AXUtilitiesHypertext.get_link_basename."""

        mock_accessible = test_context.Mock(spec=Atspi.Accessible)
        self._setup_dependencies(test_context)
        from orca.ax_utilities_hypertext import AXUtilitiesHypertext

        test_context.patch("orca.ax_hypertext.AXHypertext.get_link_uri", return_value=uri)
        result = AXUtilitiesHypertext.get_link_basename(mock_accessible, 0, remove_extension)
        assert result == expected_result
