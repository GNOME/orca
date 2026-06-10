# Unit tests for scripts/web/script_utilities.py methods.
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

# pylint: disable=wrong-import-position
# pylint: disable=import-outside-toplevel
# pylint: disable=protected-access

"""Unit tests for scripts/web/script_utilities.py methods."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import gi
import pytest

gi.require_version("Atspi", "2.0")
from gi.repository import Atspi

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from .orca_test_context import OrcaTestContext


@pytest.mark.unit
class TestWebUtilitiesCache:
    """Tests the manager-backed web utility cache."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Set up mocks for web script_utilities dependencies."""

        essential_modules = test_context.setup_shared_dependencies(
            [
                "orca.caret_navigator",
                "orca.document_presenter",
                "orca.input_event_manager",
                "orca.script_utilities",
                "orca.speech_presenter",
                "orca.ax_component",
                "orca.ax_document",
                "orca.ax_hypertext",
                "orca.ax_text",
                "orca.ax_utilities",
                "orca.ax_utilities_debugging",
            ]
        )

        class BaseUtilities:
            """Minimal base class for importing web utilities."""

            def __init__(self, script) -> None:
                self._script = script

            def get_document_for_object(self, _obj):
                return None

            def get_top_level_document_for_object(self, _obj):
                return None

        essential_modules["orca.script_utilities"].Utilities = BaseUtilities
        return essential_modules

    @staticmethod
    def _load_script_utilities_module():
        """Loads the web script_utilities module without importing the web package."""

        module_name = "tests.unit_tests._web_script_utilities_under_test"
        module_path = (
            Path(__file__).resolve().parents[2] / "src/orca/scripts/web/script_utilities.py"
        )
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module

    def test_registers_owner_lifetime_web_namespaces(self, test_context: OrcaTestContext) -> None:
        """Test _WebUtilitiesCache registers manager-backed namespaces."""

        self._setup_dependencies(test_context)
        from orca import ax_cache_manager

        manager = ax_cache_manager.get_manager()
        register = test_context.patch_object(
            manager,
            "register_cache",
            wraps=manager.register_cache,
        )

        web_utilities_cache = self._load_script_utilities_module()._WebUtilitiesCache
        cache = web_utilities_cache()
        registered_namespaces = {
            call.args[1] for call in register.call_args_list if call.args[0] is cache
        }

        assert registered_namespaces == set(cache.OBJECT_DECISION_NAMESPACES) | set(
            cache.CONTENT_NAMESPACES
        ) | set(cache.TEMPORARY_CONTEXT_NAMESPACES) | {
            cache.CARET_CONTEXTS,
            cache.PRIOR_CONTEXTS,
            cache.FIND_CONTAINER,
        }
        for call in register.call_args_list:
            if call.args[0] is cache:
                assert call.kwargs["lifetime"] is ax_cache_manager.Lifetime.OWNER
                assert call.kwargs["clear_on_demand"] is ax_cache_manager.ClearPolicy.PRESERVE
                assert call.kwargs["clear_interval_seconds"] is None

    def test_clear_object_decisions_clears_object_decision_namespaces(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test direct web clearing removes object decisions."""

        self._setup_dependencies(test_context)
        from orca import ax_cache_manager

        web_utilities_cache = self._load_script_utilities_module()._WebUtilitiesCache
        cache = web_utilities_cache()
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        cache.set_for_object(cache.IS_LINK, mock_obj, False)

        cache.clear_object_decisions("test reason")

        assert cache.get_for_object(cache.IS_LINK, mock_obj) is ax_cache_manager.MISSING

    def test_manager_clear_cache_now_preserves_object_decision_namespaces(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test routine manager clearing preserves web object decisions."""

        self._setup_dependencies(test_context)
        from orca import ax_cache_manager

        web_utilities_cache = self._load_script_utilities_module()._WebUtilitiesCache
        cache = web_utilities_cache()
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        cache.set_for_object(cache.IS_LINK, mock_obj, False)

        ax_cache_manager.get_manager().clear_cache_now("test reason")

        assert cache.get_for_object(cache.IS_LINK, mock_obj) is False

    def test_clear_content_clears_content_namespaces(self, test_context: OrcaTestContext) -> None:
        """Test direct web clearing removes cached contents."""

        self._setup_dependencies(test_context)

        web_utilities_cache = self._load_script_utilities_module()._WebUtilitiesCache
        cache = web_utilities_cache()
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        contents = [(mock_obj, 0, 1, "x")]
        cache.set_content(cache.LINE_CONTENTS, contents)

        cache.clear_content("test reason")

        assert cache.get_content(cache.LINE_CONTENTS) is None

    def test_manager_clear_cache_now_preserves_content_namespaces(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test routine manager clearing preserves web contents."""

        self._setup_dependencies(test_context)
        from orca import ax_cache_manager

        web_utilities_cache = self._load_script_utilities_module()._WebUtilitiesCache
        cache = web_utilities_cache()
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        contents = [(mock_obj, 0, 1, "x")]
        cache.set_content(cache.LINE_CONTENTS, contents)

        ax_cache_manager.get_manager().clear_cache_now("test reason")

        assert cache.get_content(cache.LINE_CONTENTS) == contents

    def test_clear_caret_context_decisions_clears_context_namespace(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test direct web clearing removes caret-context decisions."""

        self._setup_dependencies(test_context)

        web_utilities_cache = self._load_script_utilities_module()._WebUtilitiesCache
        cache = web_utilities_cache()
        mock_obj = test_context.Mock(spec=Atspi.Accessible)
        cache.set_caret_context_decision(mock_obj, False)

        cache.clear_caret_context_decisions("test reason")

        assert cache.get_caret_context_decision(mock_obj) is None

    def test_context_maps_store_and_remove_contexts(self, test_context: OrcaTestContext) -> None:
        """Test web caret-context maps are manager backed."""

        self._setup_dependencies(test_context)

        web_utilities_cache = self._load_script_utilities_module()._WebUtilitiesCache
        cache = web_utilities_cache()
        parent = test_context.Mock(spec=Atspi.Accessible)
        obj = test_context.Mock(spec=Atspi.Accessible)
        context = (obj, 3)

        cache.set_context_for_parent(cache.CARET_CONTEXTS, parent, context)
        cache.set_context_for_parent(cache.PRIOR_CONTEXTS, parent, (obj, 2))

        assert cache.get_context_for_parent(cache.CARET_CONTEXTS, parent) == context
        assert cache.get_caret_contexts() == {hash(parent): context}
        assert cache.get_context_for_parent(cache.PRIOR_CONTEXTS, parent) == (obj, 2)

        cache.discard_context_for_parent(cache.CARET_CONTEXTS, parent)
        cache.clear_prior_contexts("test reason")

        assert cache.get_context_for_parent(cache.CARET_CONTEXTS, parent) is None
        assert cache.get_context_for_parent(cache.PRIOR_CONTEXTS, parent) is None

    def test_find_container_is_manager_backed(self, test_context: OrcaTestContext) -> None:
        """Test find-in-page container storage uses the manager."""

        self._setup_dependencies(test_context)

        web_utilities_cache = self._load_script_utilities_module()._WebUtilitiesCache
        cache = web_utilities_cache()
        container = test_context.Mock(spec=Atspi.Accessible)

        assert cache.get_find_container() is None

        cache.set_find_container(container)

        assert cache.get_find_container() is container

    def test_has_grid_descendant_checks_object_after_document_cache_miss(
        self, test_context: OrcaTestContext
    ) -> None:
        """Test object grid checks continue after a cache miss."""

        self._setup_dependencies(test_context)
        web_module = self._load_script_utilities_module()
        utilities = web_module.Utilities(test_context.Mock())
        document = test_context.Mock(spec=Atspi.Accessible)
        obj = test_context.Mock(spec=Atspi.Accessible)
        grid = test_context.Mock(spec=Atspi.Accessible)
        test_context.patch_object(utilities, "active_document", return_value=document, create=True)
        test_context.patch_object(web_module.AXObject, "get_child_count", return_value=1)

        def find_all_grids(current_obj):
            if current_obj is document:
                return [grid]
            return []

        find_all = test_context.patch_object(
            web_module.AXUtilities,
            "find_all_grids",
            side_effect=find_all_grids,
        )

        assert utilities._has_grid_descendant(obj) is False
        assert find_all.call_args_list[-1].args == (obj,)
