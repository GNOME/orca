# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
# Copyright 2011-2025 Igalia, S.L.
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

"""Provides braille presentation support."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc." \
                "Copyright (c) 2011-2025 Igalia, S.L."
__license__   = "LGPL"

import os
from enum import Enum

from . import braille
from . import dbus_service
from . import debug
from . import input_event_manager
from . import settings
from . import settings_manager
from .orca_platform import tablesdir # pylint: disable=import-error

class VerbosityLevel(Enum):
    """Verbosity level enumeration with int values from settings."""

    BRIEF = settings.VERBOSITY_LEVEL_BRIEF
    VERBOSE = settings.VERBOSITY_LEVEL_VERBOSE

    @property
    def string_name(self) -> str:
        """Returns the lowercase string name for this enum value."""

        return self.name.lower()

class RolenameStyle(Enum):
    """Rolename style enumeration with int values from settings."""

    SHORT = settings.BRAILLE_ROLENAME_STYLE_SHORT
    LONG = settings.BRAILLE_ROLENAME_STYLE_LONG

    @property
    def string_name(self) -> str:
        """Returns the lowercase string name for this enum value."""

        return self.name.lower()

class BrailleIndicator(Enum):
    """Braille indicator enumeration with int values from settings."""

    NONE = settings.BRAILLE_UNDERLINE_NONE
    DOT7 = settings.BRAILLE_UNDERLINE_7
    DOT8 = settings.BRAILLE_UNDERLINE_8
    DOTS78 = settings.BRAILLE_UNDERLINE_BOTH

    @property
    def string_name(self) -> str:
        """Returns the lowercase string name for this enum value."""

        return self.name.lower()

class BraillePresenter:
    """Provides braille presentation support."""

    def __init__(self) -> None:
        msg = "BRAILLE PRESENTER: Registering D-Bus commands."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        controller = dbus_service.get_remote_controller()
        controller.register_decorated_module("BraillePresenter", self)

    def use_braille(self) -> bool:
        """Returns whether braille is to be used."""

        manager = settings_manager.get_manager()
        result = manager.get_setting("enableBraille") or manager.get_setting("enableBrailleMonitor")
        if not result:
            msg = "BRAILLE PRESENTER: Braille is disabled."
            debug.print_message(debug.LEVEL_INFO, msg, True)
        return result

    @dbus_service.getter
    def get_braille_is_enabled(self) -> bool:
        """Returns whether braille is enabled."""

        return settings_manager.get_manager().get_setting("enableBraille")

    @dbus_service.setter
    def set_braille_is_enabled(self, value: bool) -> bool:
        """Sets whether braille is enabled."""

        msg = f"BRAILLE PRESENTER: Setting enable braille to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("enableBraille", value)

        if value:
            braille.init(input_event_manager.get_manager().process_braille_event)
        else:
            braille.shutdown()

        return True

    def use_verbose_braille(self) -> bool:
        """Returns whether the braille verbosity level is set to verbose."""

        level = settings_manager.get_manager().get_setting("brailleVerbosityLevel")
        return level == settings.VERBOSITY_LEVEL_VERBOSE

    @dbus_service.getter
    def get_verbosity_level(self) -> str:
        """Returns the current braille verbosity level for object presentation."""

        int_value = settings_manager.get_manager().get_setting("brailleVerbosityLevel")
        return VerbosityLevel(int_value).string_name

    @dbus_service.setter
    def set_verbosity_level(self, value: str) -> bool:
        """Sets the braille verbosity level for object presentation."""

        try:
            level = VerbosityLevel[value.upper()]
        except KeyError:
            msg = f"BRAILLE PRESENTER: Invalid verbosity level: {value}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        msg = f"BRAILLE PRESENTER: Setting verbosity level to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("brailleVerbosityLevel", level.value)
        return True

    def use_full_rolenames(self) -> bool:
        """Returns whether full rolenames should be used."""

        level = settings_manager.get_manager().get_setting("brailleRolenameStyle")
        return level == settings.VERBOSITY_LEVEL_VERBOSE

    @dbus_service.getter
    def get_rolename_style(self) -> str:
        """Returns the current rolename style for object presentation."""

        int_value = settings_manager.get_manager().get_setting("brailleRolenameStyle")
        return RolenameStyle(int_value).string_name

    @dbus_service.setter
    def set_rolename_style(self, value: str) -> bool:
        """Sets the current rolename style for object presentation."""

        try:
            style = RolenameStyle[value.upper()]
        except KeyError:
            msg = f"BRAILLE PRESENTER: Invalid rolename style: {value}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        msg = f"BRAILLE PRESENTER: Setting rolename style to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("brailleRolenameStyle", style.value)
        return True

    @dbus_service.getter
    def get_display_ancestors(self) -> bool:
        """Returns whether ancestors of the current object will be displayed."""

        return settings_manager.get_manager().get_setting("enableBrailleContext")

    @dbus_service.setter
    def set_display_ancestors(self, value: bool) -> bool:
        """Sets whether ancestors of the current object will be displayed."""

        msg = f"BRAILLE PRESENTER: Setting enable braille context to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("enableBrailleContext", value)
        return True

    @dbus_service.getter
    def get_contracted_braille_is_enabled(self) -> bool:
        """Returns whether contracted braille is enabled."""

        return settings_manager.get_manager().get_setting("enableContractedBraille")

    @dbus_service.setter
    def set_contracted_braille_is_enabled(self, value: bool) -> bool:
        """Sets whether contracted braille is enabled."""

        msg = f"BRAILLE PRESENTER: Setting enable contracted braille to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("enableContractedBraille", value)
        return True

    @dbus_service.getter
    def get_contraction_table(self) -> str:
        """Returns the current braille contraction table name."""

        full_path = settings_manager.get_manager().get_setting("brailleContractionTable")
        if not full_path:
            return ""
        return os.path.splitext(os.path.basename(full_path))[0]

    @dbus_service.getter
    def get_available_contraction_tables(self) -> list[str]:
        """Returns a list of available contraction table names."""

        table_files = braille.get_table_files()
        return [os.path.splitext(filename)[0] for filename in table_files]

    @dbus_service.setter
    def set_contraction_table(self, value: str) -> bool:
        """Sets the current braille contraction table."""

        table_files = braille.get_table_files()
        base_name = os.path.splitext(value)[0]
        filename = None
        for table_file in table_files:
            if table_file.startswith(base_name + "."):
                filename = table_file
                break

        if not filename:
            msg = f"BRAILLE PRESENTER: Invalid contraction table: {value}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        full_path = os.path.join(tablesdir, filename)
        msg = f"BRAILLE PRESENTER: Setting contraction table to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("brailleContractionTable", full_path)
        return True

    @dbus_service.getter
    def get_end_of_line_indicator_is_enabled(self) -> bool:
        """Returns whether the end-of-line indicator is enabled."""

        # The setting, unfortunately, is disableBrailleEOL.
        return not settings_manager.get_manager().get_setting("disableBrailleEOL")

    @dbus_service.setter
    def set_end_of_line_indicator_is_enabled(self, value: bool) -> bool:
        """Sets whether the end-of-line indicator is enabled."""

        # The setting, unfortunately, is disableBrailleEOL.
        value = not value
        msg = f"BRAILLE PRESENTER: Setting disable-eol to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("disableBrailleEOL", value)
        return True

    @dbus_service.getter
    def get_word_wrap_is_enabled(self) -> bool:
        """Returns whether braille word wrap is enabled."""

        return settings_manager.get_manager().get_setting("enableBrailleWordWrap")

    @dbus_service.setter
    def set_word_wrap_is_enabled(self, value: bool) -> bool:
        """Sets whether braille word wrap is enabled."""

        msg = f"BRAILLE PRESENTER: Setting enable word wrap to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("enableBrailleWordWrap", value)
        return True

    @dbus_service.getter
    def get_flash_messages_are_enabled(self) -> bool:
        """Returns whether 'flash' messages (i.e. announcements) are enabled."""

        return settings_manager.get_manager().get_setting("enableFlashMessages")

    @dbus_service.setter
    def set_flash_messages_are_enabled(self, value: bool) -> bool:
        """Sets whether 'flash' messages (i.e. announcements) are enabled."""

        msg = f"BRAILLE PRESENTER: Setting enable flash messages to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("enableFlashMessages", value)
        return True

    def get_flashtime_from_settings(self) -> int:
        """Returns flash message duration in milliseconds based on user settings."""

        if self.get_flash_messages_are_persistent():
            return -1
        return self.get_flash_message_duration()

    @dbus_service.getter
    def get_flash_message_duration(self) -> int:
        """Returns flash message duration in milliseconds."""

        return settings_manager.get_manager().get_setting("brailleFlashTime")

    @dbus_service.setter
    def set_flash_message_duration(self, value: int) -> bool:
        """Sets flash message duration in milliseconds."""

        msg = f"BRAILLE PRESENTER: Setting braille flash time to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("brailleFlashTime", value)
        return True

    @dbus_service.getter
    def get_flash_messages_are_persistent(self) -> bool:
        """Returns whether 'flash' messages are persistent (as opposed to temporary)."""

        return settings_manager.get_manager().get_setting("flashIsPersistent")

    @dbus_service.setter
    def set_flash_messages_are_persistent(self, value: bool) -> bool:
        """Sets whether 'flash' messages are persistent (as opposed to temporary)."""

        msg = f"BRAILLE PRESENTER: Setting flash messages are persistent to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("flashIsPersistent", value)
        return True

    @dbus_service.getter
    def get_flash_messages_are_detailed(self) -> bool:
        """Returns whether 'flash' messages are detailed (as opposed to brief)."""

        return settings_manager.get_manager().get_setting("flashIsDetailed")

    @dbus_service.setter
    def set_flash_messages_are_detailed(self, value: bool) -> bool:
        """Sets whether 'flash' messages are detailed (as opposed to brief)."""

        msg = f"BRAILLE PRESENTER: Setting flash messages are detailed to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("flashIsDetailed", value)
        return True

    @dbus_service.getter
    def get_selector_indicator(self) -> str:
        """Returns the braille selector indicator style."""

        int_value = settings_manager.get_manager().get_setting("brailleSelectorIndicator")
        return BrailleIndicator(int_value).string_name

    @dbus_service.setter
    def set_selector_indicator(self, value: str) -> bool:
        """Sets the braille selector indicator style."""

        try:
            indicator = BrailleIndicator[value.upper()]
        except KeyError:
            msg = f"BRAILLE PRESENTER: Invalid selector indicator: {value}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        msg = f"BRAILLE PRESENTER: Setting selector indicator to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("brailleSelectorIndicator", indicator.value)
        return True

    @dbus_service.getter
    def get_link_indicator(self) -> str:
        """Returns the braille link indicator style."""

        int_value = settings_manager.get_manager().get_setting("brailleLinkIndicator")
        return BrailleIndicator(int_value).string_name

    @dbus_service.setter
    def set_link_indicator(self, value: str) -> bool:
        """Sets the braille link indicator style."""

        try:
            indicator = BrailleIndicator[value.upper()]
        except KeyError:
            msg = f"BRAILLE PRESENTER: Invalid link indicator: {value}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        msg = f"BRAILLE PRESENTER: Setting link indicator to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting("brailleLinkIndicator", indicator.value)
        return True

    @dbus_service.getter
    def get_text_attributes_indicator(self) -> str:
        """Returns the braille text attributes indicator style."""

        int_value = settings_manager.get_manager().get_setting("textAttributesBrailleIndicator")
        return BrailleIndicator(int_value).string_name

    @dbus_service.setter
    def set_text_attributes_indicator(self, value: str) -> bool:
        """Sets the braille text attributes indicator style."""

        try:
            indicator = BrailleIndicator[value.upper()]
        except KeyError:
            msg = f"BRAILLE PRESENTER: Invalid text attributes indicator: {value}"
            debug.print_message(debug.LEVEL_WARNING, msg, True)
            return False

        msg = f"BRAILLE PRESENTER: Setting text attributes indicator to {value}."
        debug.print_message(debug.LEVEL_INFO, msg, True)
        settings_manager.get_manager().set_setting(
            "textAttributesBrailleIndicator", indicator.value)
        return True


_presenter: BraillePresenter = BraillePresenter()

def get_presenter() -> BraillePresenter:
    """Returns the Braille Presenter"""

    return _presenter
