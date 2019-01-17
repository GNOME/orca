# Orca
#
# Copyright 2019 Hypra
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

"""Settings migration module. This will transform settings between two version
of the configuration."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2019 Hypra"
__license__   = "LGPL"

from . import debug
from . import settings


class SettingsMigration(object):
    """
    To add a new migration path for a setting, add a method like this:

    def _migrateTheOptionName(self, general, name):
        if self.fromVersion < theVersionThatIntroducedTheSetting:
            # perform any changes required
            general[...] = ...
        return general

    In normal situation, one can assume that
    - The source and target versions are different
    - The target version is the current one (settings.settingsVersion)
    - We're *upgrading*.  Support for downgrading is theoretically possible,
      but unlikely be implemented for all options.
    """

    def __init__(self, fromVersion, toVersion=settings.settingsVersion):
        self.fromVersion = fromVersion
        self.toVersion = toVersion

    def migrateGeneral(self, general):
        if self.fromVersion != self.toVersion:
            debug.println(debug.LEVEL_CONFIGURATION,
                          "CONFIGURATION MIGRATION: " +
                          "Migrating general settings from v%s to v%s" %
                          (self.fromVersion, self.toVersion))
            for name in general:
                migratorName = '_migrate' + name[0].upper() + name[1:]
                migrator = getattr(self, migratorName, None)
                if migrator:
                    general = migrator(general, name)

        return general
