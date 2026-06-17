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

"""Helpers for working with locale and language codes."""

from __future__ import annotations

import locale

try:
    from babel import Locale as _BabelLocale
    from babel.core import UnknownLocaleError as _UnknownLocaleError
except ImportError:
    _BabelLocale = None  # type: ignore[assignment, misc]
    _UnknownLocaleError = None  # type: ignore[assignment, misc]


def get_current_language_and_dialect(category: int = locale.LC_MESSAGES) -> tuple[str, str]:
    """Returns the (language, dialect) of the user's current locale, or empty strings."""

    value = locale.getlocale(category)[0] or ""
    if value in ("", "C"):
        return "", ""
    parts = value.split("_")
    return parts[0], parts[1] if len(parts) > 1 else ""


def get_current_language(category: int = locale.LC_MESSAGES) -> str:
    """Returns the language of the user's current locale, or an empty string."""

    return get_current_language_and_dialect(category)[0]


def get_known_language_codes() -> list[tuple[str, str]]:
    """Returns deduplicated (language, dialect) pairs for the locales known to the system."""

    seen: set[tuple[str, str]] = set()
    result: list[tuple[str, str]] = []
    for alias in locale.locale_alias:
        stripped = alias.split(".")[0].split("@")[0]
        parts = stripped.split("_")
        lang = parts[0].lower()
        if len(lang) != 2 or not lang.isalpha():
            continue
        region = parts[1] if len(parts) > 1 and len(parts[1]) >= 2 else ""
        candidates = [(lang, "")]
        if region:
            candidates.append((lang, region))
        for candidate in candidates:
            if candidate not in seen:
                seen.add(candidate)
                result.append(candidate)
    return result


def get_language_display_name(lang: str, dialect: str = "", in_own_language: bool = False) -> str:
    """Returns a human-readable display name for a language code."""

    if not dialect and "-" in lang:
        lang, dialect = lang.split("-", 1)

    if _BabelLocale is not None:
        try:
            locale_id = f"{lang}_{dialect}" if dialect else lang
            target = _BabelLocale.parse(locale_id)
            display_locale = target if in_own_language else _BabelLocale.default()
            if display := target.get_display_name(display_locale):
                if dialect:
                    base_display = _BabelLocale.parse(lang).get_display_name(display_locale)
                    if display == base_display:
                        return f"{display} ({dialect})"
                return display
        except (ValueError, _UnknownLocaleError):
            try:
                base_locale = _BabelLocale.parse(lang)
                display_locale = base_locale if in_own_language else _BabelLocale.default()
                if dialect and (base := base_locale.get_display_name(display_locale)):
                    return f"{base} ({dialect})"
            except (ValueError, _UnknownLocaleError):
                pass
    return f"{lang}-{dialect}" if dialect else lang


def is_standard_locale(lang: str, dialect: str) -> bool:
    """Returns True if babel recognizes the lang+dialect as a distinct locale."""

    if _BabelLocale is None:
        return len(dialect) <= 3 and dialect.isalpha()
    try:
        full = _BabelLocale.parse(f"{lang}_{dialect}")
        base = _BabelLocale.parse(lang)
        return full.get_display_name() != base.get_display_name()
    except (ValueError, _UnknownLocaleError):
        return False
