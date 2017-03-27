# Orca
#
# Copyright 2016 Igalia, S.L.
#
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

"""Utilities for obtaining sounds to be presented for objects."""

__id__        = "$Id:$"
__version__   = "$Revision:$"
__date__      = "$Date:$"
__copyright__ = "Copyright (c) 2016 Igalia, S.L."
__license__   = "LGPL"

import pyatspi

from orca import settings_manager
from orca import sound_generator

_settingsManager = settings_manager.getManager()


class SoundGenerator(sound_generator.SoundGenerator):

    def __init__(self, script):
        super().__init__(script)

    def _generateClickable(self, obj, **args):
        """Returns an array of sounds indicating obj is clickable."""

        if not _settingsManager.getSetting('playSoundForState'):
            return []

        if not self._script.utilities.inDocumentContent(obj):
            return []

        if not args.get('mode', None):
            args['mode'] = self._mode

        args['stringType'] = 'clickable'
        if self._script.utilities.isClickableElement(obj):
            filenames = [self._script.formatting.getString(**args)]
            result = list(map(self._convertFilenameToIcon, filenames))
            if result:
                return result

        return []

    def _generateHasLongDesc(self, obj, **args):
        """Returns an array of sounds indicating obj has a longdesc."""

        if not _settingsManager.getSetting('playSoundForState'):
            return []

        if not self._script.utilities.inDocumentContent(obj):
            return []

        if not args.get('mode', None):
            args['mode'] = self._mode

        args['stringType'] = 'haslongdesc'
        if self._script.utilities.hasLongDesc(obj):
            filenames = [self._script.formatting.getString(**args)]
            result = list(map(self._convertFilenameToIcon, filenames))
            if result:
                return result

        return []

    def generateSound(self, obj, **args):
        """Returns an array of sounds for the complete presentation of obj."""

        if not self._script.utilities.inDocumentContent(obj):
            return super().generateSound(obj, **args)

        result = []
        if args.get('formatType') == 'detailedWhereAmI':
            oldRole = self._overrideRole('default', args)
        elif self._script.utilities.isLink(obj):
            oldRole = self._overrideRole(pyatspi.ROLE_LINK, args)
        elif self._script.utilities.treatAsDiv(obj):
            oldRole = self._overrideRole(pyatspi.ROLE_SECTION, args)
        else:
            oldRole = self._overrideRole(self._getAlternativeRole(obj, **args), args)

        result.extend(super().generateSound(obj, **args))
        result = list(filter(lambda x: x, result))
        self._restoreRole(oldRole, args)

        return result

    def generateContents(self, contents, **args):
        """Returns an array of an array of sounds for the contents."""

        if not len(contents):
            return []

        result = []
        contents = self._script.utilities.filterContentsForPresentation(contents, False)
        for i, content in enumerate(contents):
            obj, start, end, string = content
            icon = self.generateSound(
                obj, startOffset=start, endOffset=end, string=string,
                index=i, total=len(contents), **args)
            result.append(icon)

        return result
