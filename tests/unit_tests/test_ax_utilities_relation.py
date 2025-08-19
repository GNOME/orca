# Unit tests for ax_utilities_relation.py methods.
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

# pylint: disable=too-many-public-methods
# pylint: disable=wrong-import-position
# pylint: disable=too-many-lines
# pylint: disable=protected-access
# pylint: disable=import-outside-toplevel

"""Unit tests for ax_utilities_relation.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext
    from unittest.mock import MagicMock

@pytest.mark.unit
class TestAXUtilitiesRelation:
    """Test AXUtilitiesRelation class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for ax_utilities_relation dependencies."""

        essential_modules = test_context.setup_shared_dependencies([])

        ax_object_mock = essential_modules["orca.ax_object"]
        ax_object_mock.is_valid = test_context.Mock(return_value=True)
        ax_object_mock.is_ancestor = test_context.Mock(return_value=False)

        return essential_modules

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "controlled_by",
                "method_name": "get_is_controlled_by",
                "relation_type": Atspi.RelationType.CONTROLLED_BY,
            },
            {
                "id": "controller_for",
                "method_name": "get_is_controller_for",
                "relation_type": Atspi.RelationType.CONTROLLER_FOR,
            },
            {
                "id": "described_by",
                "method_name": "get_is_described_by",
                "relation_type": Atspi.RelationType.DESCRIBED_BY,
            },
            {
                "id": "description_for",
                "method_name": "get_is_description_for",
                "relation_type": Atspi.RelationType.DESCRIPTION_FOR,
            },
            {
                "id": "details",
                "method_name": "get_details",
                "relation_type": Atspi.RelationType.DETAILS,
            },
            {
                "id": "details_for",
                "method_name": "get_is_details_for",
                "relation_type": Atspi.RelationType.DETAILS_FOR,
            },
            {
                "id": "embedded_by",
                "method_name": "get_is_embedded_by",
                "relation_type": Atspi.RelationType.EMBEDDED_BY,
            },
            {
                "id": "embeds",
                "method_name": "get_embeds",
                "relation_type": Atspi.RelationType.EMBEDS,
            },
            {
                "id": "error_for",
                "method_name": "get_is_error_for",
                "relation_type": Atspi.RelationType.ERROR_FOR,
            },
            {
                "id": "error_message",
                "method_name": "get_error_message",
                "relation_type": Atspi.RelationType.ERROR_MESSAGE,
            },
            {
                "id": "flows_from",
                "method_name": "get_flows_from",
                "relation_type": Atspi.RelationType.FLOWS_FROM,
            },
            {
                "id": "flows_to",
                "method_name": "get_flows_to",
                "relation_type": Atspi.RelationType.FLOWS_TO,
            },
            {
                "id": "label_for",
                "method_name": "get_is_label_for",
                "relation_type": Atspi.RelationType.LABEL_FOR,
            },
            {
                "id": "member_of",
                "method_name": "get_is_member_of",
                "relation_type": Atspi.RelationType.MEMBER_OF,
            },
            {
                "id": "node_child_of",
                "method_name": "get_is_node_child_of",
                "relation_type": Atspi.RelationType.NODE_CHILD_OF,
            },
            {
                "id": "node_parent_of",
                "method_name": "get_is_node_parent_of",
                "relation_type": Atspi.RelationType.NODE_PARENT_OF,
            },
            {
                "id": "parent_window_of",
                "method_name": "get_is_parent_window_of",
                "relation_type": Atspi.RelationType.PARENT_WINDOW_OF,
            },
            {
                "id": "popup_for",
                "method_name": "get_is_popup_for",
                "relation_type": Atspi.RelationType.POPUP_FOR,
            },
            {
                "id": "subwindow_of",
                "method_name": "get_is_subwindow_of",
                "relation_type": Atspi.RelationType.SUBWINDOW_OF,
            },
            {
                "id": "tooltip_for",
                "method_name": "get_is_tooltip_for",
                "relation_type": Atspi.RelationType.TOOLTIP_FOR,
            },
            {
                "id": "debugging_labelled_by",
                "method_name": "get_relation_targets_for_debugging",
                "relation_type": Atspi.RelationType.LABELLED_BY,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_relation_targets_wrappers(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test that various get_*_relation_targets methods call _get_relation_targets."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_relation import AXUtilitiesRelation

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_targets = [test_context.Mock(spec=Atspi.Accessible)]
        test_context.patch_object(
            AXUtilitiesRelation, "_get_relation_targets", return_value=mock_targets
        )
        method = getattr(AXUtilitiesRelation, case["method_name"])
        if case["method_name"] == "get_relation_targets_for_debugging":
            result = method(mock_obj, case["relation_type"])
        else:
            result = method(mock_obj)
        assert result == mock_targets

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "invalid_object",
                "is_valid": False,
                "has_cache": False,
                "should_raise_error": False,
                "expected_result": [],
                "should_cache": False,
            },
            {
                "id": "from_cache",
                "is_valid": True,
                "has_cache": True,
                "should_raise_error": False,
                "expected_result": "cached_relations",
                "should_cache": False,
            },
            {
                "id": "from_atspi",
                "is_valid": True,
                "has_cache": False,
                "should_raise_error": False,
                "expected_result": "atspi_relations",
                "should_cache": True,
            },
            {
                "id": "glib_error",
                "is_valid": True,
                "has_cache": False,
                "should_raise_error": True,
                "expected_result": [],
                "should_cache": False,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_relations(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test AXUtilitiesRelation.get_relations with various scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_relation import AXUtilitiesRelation
        from gi.repository import GLib

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_relations = [test_context.Mock(spec=Atspi.Relation)]

        test_context.patch(
            "orca.ax_utilities_relation.AXObject.is_valid", return_value=case["is_valid"]
        )

        AXUtilitiesRelation.RELATIONS.clear()
        if case["has_cache"]:
            AXUtilitiesRelation.RELATIONS[hash(mock_obj)] = mock_relations

        if case["should_raise_error"]:

            def raise_glib_error(self):
                raise GLib.GError("Test error")

            test_context.patch_object(
                Atspi.Accessible, "get_relation_set", side_effect=raise_glib_error
            )
        else:
            test_context.patch_object(
                Atspi.Accessible, "get_relation_set", return_value=mock_relations
            )

        result = AXUtilitiesRelation.get_relations(mock_obj)

        if case["expected_result"] in ("cached_relations", "atspi_relations"):
            assert result == mock_relations
        else:
            assert result == case["expected_result"]

        if case["should_cache"]:
            assert AXUtilitiesRelation.RELATIONS[hash(mock_obj)] == mock_relations

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "matching_type",
                "relation_type_to_find": Atspi.RelationType.LABELLED_BY,
                "relation_type_available": Atspi.RelationType.LABELLED_BY,
                "expected_result": "found_relation",
            },
            {
                "id": "no_matching_type",
                "relation_type_to_find": Atspi.RelationType.LABEL_FOR,
                "relation_type_available": Atspi.RelationType.LABELLED_BY,
                "expected_result": None,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_relation(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test AXUtilitiesRelation._get_relation with various scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_relation import AXUtilitiesRelation

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_relation = test_context.Mock(spec=Atspi.Relation)
        mock_relation.get_relation_type.return_value = case["relation_type_available"]
        test_context.patch_object(
            AXUtilitiesRelation, "get_relations", return_value=[mock_relation]
        )

        result = AXUtilitiesRelation._get_relation(mock_obj, case["relation_type_to_find"])

        if case["expected_result"] == "found_relation":
            assert result == mock_relation
        else:
            assert result is case["expected_result"]

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "from_cache",
                "scenario": "cached",
                "relation_type": Atspi.RelationType.LABELLED_BY,
                "expected_result": "cached_targets",
                "has_self_target": False,
            },
            {
                "id": "no_relation",
                "scenario": "no_relation",
                "relation_type": Atspi.RelationType.LABELLED_BY,
                "expected_result": [],
                "has_self_target": False,
            },
            {
                "id": "valid_targets",
                "scenario": "valid_targets",
                "relation_type": Atspi.RelationType.LABELLED_BY,
                "expected_result": "all_targets",
                "has_self_target": False,
            },
            {
                "id": "removes_self",
                "scenario": "with_self",
                "relation_type": Atspi.RelationType.LABELLED_BY,
                "expected_result": "exclude_self",
                "has_self_target": True,
            },
            {
                "id": "keeps_member_of_self",
                "scenario": "member_of_self",
                "relation_type": Atspi.RelationType.MEMBER_OF,
                "expected_result": "include_self",
                "has_self_target": True,
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_relation_targets(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test AXUtilitiesRelation._get_relation_targets with various scenarios."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_relation import AXUtilitiesRelation

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_target1 = test_context.Mock(spec=Atspi.Accessible)
        mock_target2 = test_context.Mock(spec=Atspi.Accessible)

        AXUtilitiesRelation.TARGETS.clear()

        if case["scenario"] == "cached":
            mock_targets = [mock_target1]
            AXUtilitiesRelation.TARGETS[hash(mock_obj)] = {case["relation_type"]: mock_targets}
            result = AXUtilitiesRelation._get_relation_targets(mock_obj, case["relation_type"])
            assert result == mock_targets
            return

        if case["scenario"] == "no_relation":
            test_context.patch_object(
                AXUtilitiesRelation, "_get_relation", return_value=None
            )
        else:
            mock_relation = test_context.Mock(spec=Atspi.Relation)
            if case["has_self_target"]:
                mock_relation.get_n_targets.return_value = 2
                mock_relation.get_target.side_effect = [mock_target1, mock_obj]
            else:
                mock_relation.get_n_targets.return_value = 2
                mock_relation.get_target.side_effect = [mock_target1, mock_target2]
            test_context.patch_object(
                AXUtilitiesRelation, "_get_relation", return_value=mock_relation
            )

        result = AXUtilitiesRelation._get_relation_targets(mock_obj, case["relation_type"])

        if case["expected_result"] == "all_targets":
            assert set(result) == {mock_target1, mock_target2}
        elif case["expected_result"] == "exclude_self":
            assert result == [mock_target1]
        elif case["expected_result"] == "include_self":
            assert set(result) == {mock_target1, mock_obj}
        else:
            assert result == case["expected_result"]

        if case["scenario"] == "no_relation":
            assert AXUtilitiesRelation.TARGETS[hash(mock_obj)][case["relation_type"]] == []

    @pytest.mark.parametrize(
        "case",
        [
            {
                "id": "without_filtering",
                "exclude_ancestors": False,
                "expected_result": "all_targets",
            },
            {
                "id": "with_filtering",
                "exclude_ancestors": True,
                "expected_result": "non_ancestors_only",
            },
        ],
        ids=lambda case: case["id"],
    )
    def test_get_is_labelled_by(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test AXUtilitiesRelation.get_is_labelled_by with and without ancestor filtering."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_relation import AXUtilitiesRelation

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        mock_ancestor = test_context.Mock(spec=Atspi.Accessible)
        mock_non_ancestor = test_context.Mock(spec=Atspi.Accessible)
        mock_targets = [mock_ancestor, mock_non_ancestor]

        test_context.patch_object(
            AXUtilitiesRelation, "_get_relation_targets", return_value=mock_targets
        )

        if case["exclude_ancestors"]:
            test_context.patch(
                "orca.ax_utilities_relation.AXObject.is_ancestor",
                side_effect=lambda child, acc: acc == mock_ancestor,
            )

        result = AXUtilitiesRelation.get_is_labelled_by(
            mock_obj, exclude_ancestors=case["exclude_ancestors"]
        )

        if case["expected_result"] == "all_targets":
            assert result == mock_targets
        else:
            assert result == [mock_non_ancestor]

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "controlled", "is_controlled": True, "expected": True},
            {"id": "not_controlled", "is_controlled": False, "expected": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_object_is_controlled_by(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test AXUtilitiesRelation.object_is_controlled_by with controlled/uncontrolled objects."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_relation import AXUtilitiesRelation

        mock_obj1 = test_context.Mock(spec=Atspi.Accessible)
        mock_obj2 = test_context.Mock(spec=Atspi.Accessible)
        mock_obj3 = test_context.Mock(spec=Atspi.Accessible)
        targets = [mock_obj2] if case["is_controlled"] else [mock_obj3]
        test_context.patch_object(
            AXUtilitiesRelation, "_get_relation_targets", return_value=targets
        )
        result = AXUtilitiesRelation.object_is_controlled_by(mock_obj1, mock_obj2)
        assert result is case["expected"]

    @pytest.mark.parametrize(
        "case",
        [
            {"id": "no_relations", "has_relations": False, "expected": True},
            {"id": "has_relations", "has_relations": True, "expected": False},
        ],
        ids=lambda case: case["id"],
    )
    def test_object_is_unrelated(self, test_context: OrcaTestContext, case: dict) -> None:
        """Test AXUtilitiesRelation.object_is_unrelated with objects with and without relations."""

        self._setup_dependencies(test_context)
        from orca.ax_utilities_relation import AXUtilitiesRelation

        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        relations = [test_context.Mock(spec=Atspi.Relation)] if case["has_relations"] else []
        test_context.patch_object(
            AXUtilitiesRelation, "get_relations", return_value=relations
        )
        result = AXUtilitiesRelation.object_is_unrelated(mock_obj)
        assert result is case["expected"]
