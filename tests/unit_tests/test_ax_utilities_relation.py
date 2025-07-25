# Unit tests for ax_utilities_relation.py relation-related methods.
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
# pylint: disable=unused-argument

"""Unit tests for ax_utilities_relation.py relation-related methods."""

from unittest.mock import Mock

import gi
import pytest

from conftest import clean_module_cache

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi



@pytest.mark.unit
class TestAXUtilitiesRelation:
    """Test relation-related methods."""

    def setup_method(self):
        """Clear cached data before each test."""
        clean_module_cache("orca.ax_utilities_relation")

    @pytest.mark.parametrize(
        "method_name, relation_type",
        [
            ("get_is_controlled_by", Atspi.RelationType.CONTROLLED_BY),
            ("get_is_controller_for", Atspi.RelationType.CONTROLLER_FOR),
            ("get_is_described_by", Atspi.RelationType.DESCRIBED_BY),
            ("get_is_description_for", Atspi.RelationType.DESCRIPTION_FOR),
            ("get_details", Atspi.RelationType.DETAILS),
            ("get_is_details_for", Atspi.RelationType.DETAILS_FOR),
            ("get_is_embedded_by", Atspi.RelationType.EMBEDDED_BY),
            ("get_embeds", Atspi.RelationType.EMBEDS),
            ("get_is_error_for", Atspi.RelationType.ERROR_FOR),
            ("get_error_message", Atspi.RelationType.ERROR_MESSAGE),
            ("get_flows_from", Atspi.RelationType.FLOWS_FROM),
            ("get_flows_to", Atspi.RelationType.FLOWS_TO),
            ("get_is_label_for", Atspi.RelationType.LABEL_FOR),
            ("get_is_member_of", Atspi.RelationType.MEMBER_OF),
            ("get_is_node_child_of", Atspi.RelationType.NODE_CHILD_OF),
            ("get_is_node_parent_of", Atspi.RelationType.NODE_PARENT_OF),
            ("get_is_parent_window_of", Atspi.RelationType.PARENT_WINDOW_OF),
            ("get_is_popup_for", Atspi.RelationType.POPUP_FOR),
            ("get_is_subwindow_of", Atspi.RelationType.SUBWINDOW_OF),
            ("get_is_tooltip_for", Atspi.RelationType.TOOLTIP_FOR),
            ("get_relation_targets_for_debugging", Atspi.RelationType.LABELLED_BY),
        ],
    )
    def test_get_relation_targets_wrappers(
        self, monkeypatch, method_name, relation_type, mock_orca_dependencies
    ):
        """Test that various get_*_relation_targets methods call _get_relation_targets."""

        clean_module_cache("orca.ax_utilities_relation")
        from orca.ax_utilities_relation import AXUtilitiesRelation

        mock_obj = Mock(spec=Atspi.Accessible)
        mock_targets = [Mock(spec=Atspi.Accessible)]
        monkeypatch.setattr(
            AXUtilitiesRelation, "_get_relation_targets", lambda obj, rel_type: mock_targets
        )

        method = getattr(AXUtilitiesRelation, method_name)
        if method_name == "get_relation_targets_for_debugging":
            result = method(mock_obj, relation_type)
        else:
            result = method(mock_obj)

        assert result == mock_targets

    def test_get_relations_with_invalid_object(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRelation.get_relations for invalid object."""

        clean_module_cache("orca.ax_utilities_relation")
        from orca.ax_utilities_relation import AXUtilitiesRelation
        from orca import ax_utilities_relation

        mock_obj = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(ax_utilities_relation.AXObject, "is_valid", lambda obj: False)
        result = AXUtilitiesRelation.get_relations(mock_obj)
        assert result == []

    def test_get_relations_from_cache(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRelation.get_relations with cached relations."""

        clean_module_cache("orca.ax_utilities_relation")
        from orca.ax_utilities_relation import AXUtilitiesRelation
        from orca import ax_utilities_relation

        mock_obj = Mock(spec=Atspi.Accessible)
        mock_relations = [Mock(spec=Atspi.Relation)]
        monkeypatch.setattr(ax_utilities_relation.AXObject, "is_valid", lambda obj: True)
        AXUtilitiesRelation.RELATIONS[hash(mock_obj)] = mock_relations
        result = AXUtilitiesRelation.get_relations(mock_obj)
        assert result == mock_relations

    def test_get_relations_from_atspi(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRelation.get_relations fetches from AT-SPI."""

        clean_module_cache("orca.ax_utilities_relation")
        from orca.ax_utilities_relation import AXUtilitiesRelation
        from orca import ax_utilities_relation

        mock_obj = Mock(spec=Atspi.Accessible)
        mock_relations = [Mock(spec=Atspi.Relation)]
        monkeypatch.setattr(ax_utilities_relation.AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(Atspi.Accessible, "get_relation_set", lambda self: mock_relations)
        result = AXUtilitiesRelation.get_relations(mock_obj)
        assert result == mock_relations
        assert AXUtilitiesRelation.RELATIONS[hash(mock_obj)] == mock_relations

    def test_get_relations_with_glib_error(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRelation.get_relations when GLib.GError occurs."""

        clean_module_cache("orca.ax_utilities_relation")
        from orca.ax_utilities_relation import AXUtilitiesRelation
        from orca import ax_utilities_relation
        from gi.repository import GLib

        mock_obj = Mock(spec=Atspi.Accessible)

        def raise_glib_error(self):
            raise GLib.GError("Test error")

        monkeypatch.setattr(ax_utilities_relation.AXObject, "is_valid", lambda obj: True)
        monkeypatch.setattr(Atspi.Accessible, "get_relation_set", raise_glib_error)
        result = AXUtilitiesRelation.get_relations(mock_obj)
        assert result == []

    def test_get_relation_with_matching_type(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRelation._get_relation with matching type."""

        clean_module_cache("orca.ax_utilities_relation")
        from orca.ax_utilities_relation import AXUtilitiesRelation

        mock_obj = Mock(spec=Atspi.Accessible)
        mock_relation = Mock(spec=Atspi.Relation)
        mock_relation.get_relation_type.return_value = Atspi.RelationType.LABELLED_BY
        monkeypatch.setattr(AXUtilitiesRelation, "get_relations", lambda obj: [mock_relation])
        result = AXUtilitiesRelation._get_relation(mock_obj, Atspi.RelationType.LABELLED_BY)
        assert result == mock_relation

    def test_get_relation_with_no_matching_type(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRelation._get_relation when no matching type found."""

        clean_module_cache("orca.ax_utilities_relation")
        from orca.ax_utilities_relation import AXUtilitiesRelation

        mock_obj = Mock(spec=Atspi.Accessible)
        mock_relation = Mock(spec=Atspi.Relation)
        mock_relation.get_relation_type.return_value = Atspi.RelationType.LABELLED_BY
        monkeypatch.setattr(AXUtilitiesRelation, "get_relations", lambda obj: [mock_relation])
        result = AXUtilitiesRelation._get_relation(mock_obj, Atspi.RelationType.LABEL_FOR)
        assert result is None

    def test_get_relation_targets_from_cache(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRelation._get_relation_targets with cached targets."""

        clean_module_cache("orca.ax_utilities_relation")
        from orca.ax_utilities_relation import AXUtilitiesRelation

        mock_obj = Mock(spec=Atspi.Accessible)
        mock_targets = [Mock(spec=Atspi.Accessible)]
        AXUtilitiesRelation.TARGETS[hash(mock_obj)] = {
            Atspi.RelationType.LABELLED_BY: mock_targets
        }

        result = AXUtilitiesRelation._get_relation_targets(mock_obj, Atspi.RelationType.LABELLED_BY)
        assert result == mock_targets

    def test_get_relation_targets_with_no_relation(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRelation._get_relation_targets when no relation exists."""

        clean_module_cache("orca.ax_utilities_relation")
        from orca.ax_utilities_relation import AXUtilitiesRelation

        mock_obj = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(AXUtilitiesRelation, "_get_relation", lambda obj, rel_type: None)
        result = AXUtilitiesRelation._get_relation_targets(mock_obj, Atspi.RelationType.LABELLED_BY)
        assert result == []
        assert AXUtilitiesRelation.TARGETS[hash(mock_obj)][Atspi.RelationType.LABELLED_BY] == []

    def test_get_relation_targets_with_valid_targets(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRelation._get_relation_targets from relation."""

        clean_module_cache("orca.ax_utilities_relation")
        from orca.ax_utilities_relation import AXUtilitiesRelation

        mock_obj = Mock(spec=Atspi.Accessible)
        mock_target1 = Mock(spec=Atspi.Accessible)
        mock_target2 = Mock(spec=Atspi.Accessible)
        mock_relation = Mock(spec=Atspi.Relation)
        mock_relation.get_n_targets.return_value = 2
        mock_relation.get_target.side_effect = [mock_target1, mock_target2]
        monkeypatch.setattr(
            AXUtilitiesRelation, "_get_relation", lambda obj, rel_type: mock_relation)
        result = AXUtilitiesRelation._get_relation_targets(mock_obj, Atspi.RelationType.LABELLED_BY)
        assert set(result) == {mock_target1, mock_target2}

    def test_get_relation_targets_removes_self_reference(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRelation._get_relation_targets removes self-references."""

        clean_module_cache("orca.ax_utilities_relation")
        from orca.ax_utilities_relation import AXUtilitiesRelation

        mock_obj = Mock(spec=Atspi.Accessible)
        mock_target = Mock(spec=Atspi.Accessible)
        mock_relation = Mock(spec=Atspi.Relation)
        mock_relation.get_n_targets.return_value = 2
        mock_relation.get_target.side_effect = [mock_target, mock_obj]
        monkeypatch.setattr(
            AXUtilitiesRelation, "_get_relation", lambda obj, rel_type: mock_relation)
        result = AXUtilitiesRelation._get_relation_targets(mock_obj, Atspi.RelationType.LABELLED_BY)
        assert result == [mock_target]

    def test_get_relation_targets_keeps_self_for_member_of(
        self, monkeypatch, mock_orca_dependencies
    ):
        """Test AXUtilitiesRelation._get_relation_targets keeps MEMBER_OF self-references."""

        clean_module_cache("orca.ax_utilities_relation")
        from orca.ax_utilities_relation import AXUtilitiesRelation

        mock_obj = Mock(spec=Atspi.Accessible)
        mock_target = Mock(spec=Atspi.Accessible)
        mock_relation = Mock(spec=Atspi.Relation)
        mock_relation.get_n_targets.return_value = 2
        mock_relation.get_target.side_effect = [mock_target, mock_obj]
        monkeypatch.setattr(
            AXUtilitiesRelation, "_get_relation", lambda obj, rel_type: mock_relation)
        result = AXUtilitiesRelation._get_relation_targets(mock_obj, Atspi.RelationType.MEMBER_OF)
        assert set(result) == {mock_target, mock_obj}

    def test_get_is_labelled_by_without_filtering(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRelation.get_is_labelled_by with exclude_ancestors=False."""

        clean_module_cache("orca.ax_utilities_relation")
        from orca.ax_utilities_relation import AXUtilitiesRelation

        mock_obj = Mock(spec=Atspi.Accessible)
        mock_targets = [Mock(spec=Atspi.Accessible)]
        monkeypatch.setattr(
            AXUtilitiesRelation, "_get_relation_targets", lambda obj, rel_type: mock_targets)
        result = AXUtilitiesRelation.get_is_labelled_by(mock_obj, exclude_ancestors=False)
        assert result == mock_targets

    def test_get_is_labelled_by_with_filtering(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRelation.get_is_labelled_by with exclude_ancestors=True."""

        clean_module_cache("orca.ax_utilities_relation")
        from orca.ax_utilities_relation import AXUtilitiesRelation
        from orca import ax_utilities_relation

        mock_obj = Mock(spec=Atspi.Accessible)
        mock_ancestor = Mock(spec=Atspi.Accessible)
        mock_non_ancestor = Mock(spec=Atspi.Accessible)
        mock_targets = [mock_ancestor, mock_non_ancestor]
        monkeypatch.setattr(
            AXUtilitiesRelation, "_get_relation_targets", lambda obj, rel_type: mock_targets)
        # Mock is_ancestor directly on the imported module
        monkeypatch.setattr(ax_utilities_relation.AXObject, "is_ancestor",
                          lambda child, acc: acc == mock_ancestor)
        result = AXUtilitiesRelation.get_is_labelled_by(mock_obj, exclude_ancestors=True)
        assert result == [mock_non_ancestor]

    def test_object_is_controlled_by_true(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRelation.object_is_controlled_by when obj2 controls obj1."""

        clean_module_cache("orca.ax_utilities_relation")
        from orca.ax_utilities_relation import AXUtilitiesRelation

        mock_obj1 = Mock(spec=Atspi.Accessible)
        mock_obj2 = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(
            AXUtilitiesRelation, "_get_relation_targets", lambda obj, rel_type: [mock_obj2])
        result = AXUtilitiesRelation.object_is_controlled_by(mock_obj1, mock_obj2)
        assert result is True

    def test_object_is_controlled_by_false(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRelation.object_is_controlled_by when obj2 doesn't control obj1."""

        clean_module_cache("orca.ax_utilities_relation")
        from orca.ax_utilities_relation import AXUtilitiesRelation

        mock_obj1 = Mock(spec=Atspi.Accessible)
        mock_obj2 = Mock(spec=Atspi.Accessible)
        mock_obj3 = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(
            AXUtilitiesRelation, "_get_relation_targets", lambda obj, rel_type: [mock_obj3])
        result = AXUtilitiesRelation.object_is_controlled_by(mock_obj1, mock_obj2)
        assert result is False

    def test_object_is_unrelated_true(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRelation.object_is_unrelated when object has no relations."""

        clean_module_cache("orca.ax_utilities_relation")
        from orca.ax_utilities_relation import AXUtilitiesRelation

        mock_obj = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(AXUtilitiesRelation, "get_relations", lambda obj: [])
        result = AXUtilitiesRelation.object_is_unrelated(mock_obj)
        assert result is True

    def test_object_is_unrelated_false(self, monkeypatch, mock_orca_dependencies):
        """Test AXUtilitiesRelation.object_is_unrelated when object has relations."""

        clean_module_cache("orca.ax_utilities_relation")
        from orca.ax_utilities_relation import AXUtilitiesRelation

        mock_obj = Mock(spec=Atspi.Accessible)
        monkeypatch.setattr(
            AXUtilitiesRelation, "get_relations", lambda obj: [Mock(spec=Atspi.Relation)])
        result = AXUtilitiesRelation.object_is_unrelated(mock_obj)
        assert result is False
