# Unit tests for language_utilities.py methods.
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

"""Unit tests for language_utilities.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from .orca_test_context import OrcaTestContext


@pytest.mark.unit
class TestLanguageUtilities:
    """Test the locale/language helpers."""

    @pytest.mark.parametrize(
        "locale_value, expected",
        [
            (("en_US", "UTF-8"), ("en", "US")),
            (("fr", "UTF-8"), ("fr", "")),
            (("en_US_POSIX", "UTF-8"), ("en", "US")),
            ((None, None), ("", "")),
            (("C", None), ("", "")),
        ],
        ids=["language_and_dialect", "language_only", "extra_parts", "unset", "c_locale"],
    )
    def test_get_current_language_and_dialect(
        self, test_context: OrcaTestContext, locale_value: tuple, expected: tuple[str, str]
    ) -> None:
        """Test get_current_language_and_dialect parses the current locale."""

        test_context.patch("locale.getlocale", return_value=locale_value)
        from orca import language_utilities

        assert language_utilities.get_current_language_and_dialect() == expected
        assert language_utilities.get_current_language() == expected[0]

    def test_get_known_language_codes(self, test_context: OrcaTestContext) -> None:
        """Test get_known_language_codes yields valid, deduplicated language pairs."""

        from orca import language_utilities

        codes = language_utilities.get_known_language_codes()

        assert ("en", "") in codes
        assert len(codes) == len(set(codes))
        for lang, _dialect in codes:
            assert len(lang) == 2 and lang.isalpha() and lang.islower()

    def test_get_language_display_name_without_babel(self, test_context: OrcaTestContext) -> None:
        """Test get_language_display_name falls back to the code when babel is unavailable."""

        from orca import language_utilities

        test_context.patch_object(language_utilities, "_BabelLocale", new=None)
        assert language_utilities.get_language_display_name("en") == "en"
        assert language_utilities.get_language_display_name("en", "gb") == "en-gb"
        assert language_utilities.get_language_display_name("en-gb") == "en-gb"

    def test_is_standard_locale_without_babel(self, test_context: OrcaTestContext) -> None:
        """Test is_standard_locale's dialect heuristic when babel is unavailable."""

        from orca import language_utilities

        test_context.patch_object(language_utilities, "_BabelLocale", new=None)
        assert language_utilities.is_standard_locale("en", "gb") is True
        assert language_utilities.is_standard_locale("en", "1234") is False
        assert language_utilities.is_standard_locale("en", "g1") is False

    def test_get_language_display_name_with_babel(self, test_context: OrcaTestContext) -> None:
        """Test get_language_display_name returns localized names when babel is available."""

        babel = pytest.importorskip("babel")
        from orca import language_utilities

        test_context.patch_object(
            language_utilities._BabelLocale, "default", return_value=babel.Locale("en")
        )
        assert language_utilities.get_language_display_name("fr") == "French"
        assert (
            language_utilities.get_language_display_name("en", "gb") == "English (United Kingdom)"
        )
        assert language_utilities.get_language_display_name("zz") == "zz"

    def test_is_standard_locale_with_babel(self, test_context: OrcaTestContext) -> None:
        """Test is_standard_locale distinguishes real locales via babel when available."""

        pytest.importorskip("babel")
        from orca import language_utilities

        assert language_utilities.is_standard_locale("en", "GB") is True
        assert language_utilities.is_standard_locale("en", "US") is True
