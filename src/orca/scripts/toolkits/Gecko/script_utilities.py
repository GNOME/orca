# Orca
#
# Copyright 2010 Joanmarie Diggs.
# Copyright 2014-2015 Igalia, S.L.
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

"""Commonly-required utility methods needed by -- and potentially
   customized by -- application and toolkit scripts. They have
   been pulled out from the scripts because certain scripts had
   gotten way too large as a result of including these methods."""

__id__ = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2010 Joanmarie Diggs." \
                "Copyright (c) 2014-2015 Igalia, S.L."
__license__   = "LGPL"

import pyatspi

from orca import debug
from orca import orca_state
from orca.scripts import web


class Utilities(web.Utilities):

    def __init__(self, script):
        super().__init__(script)

    def _attemptBrokenTextRecovery(self, obj, **args):
        boundary = args.get('boundary')

        # Gecko fails to implement this boundary type.
        if boundary == pyatspi.TEXT_BOUNDARY_SENTENCE_START:
            return True

        if self.isContentEditableWithEmbeddedObjects(obj):
            return boundary == pyatspi.TEXT_BOUNDARY_WORD_START

        return True

    def _treatAsLeafNode(self, obj):
        if obj.getRole() == pyatspi.ROLE_TABLE_ROW:
            return not obj.childCount

        return super()._treatAsLeafNode(obj)

    def containsPoint(self, obj, x, y, coordType, margin=2):
        if not super().containsPoint(obj, x, y, coordType, margin):
            return False

        roles = [pyatspi.ROLE_MENU, pyatspi.ROLE_TOOL_TIP]
        if obj.getRole() in roles and self.topLevelObject(obj) == obj.parent:
            msg = "GECKO: %s is suspected to be off screen object" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        return True

    def nodeLevel(self, obj):
        """Determines the level of at which this object is at by using
        the object attribute 'level'.  To be consistent with the default
        nodeLevel() this value is 0-based (Gecko return is 1-based) """

        if obj is None or obj.getRole() == pyatspi.ROLE_HEADING \
           or (obj.parent and obj.parent.getRole() == pyatspi.ROLE_MENU):
            return -1

        try:
            attrs = obj.getAttributes()
        except:
            msg = "GECKO: Exception getting attributes for %s" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return -1
        for attr in attrs:
            if attr.startswith("level:"):
                return int(attr[6:]) - 1
        return -1

    def isSameObject(self, obj1, obj2, comparePaths=False, ignoreNames=False):
        if super().isSameObject(obj1, obj2, comparePaths, ignoreNames):
            return True
        try:
            role1 = obj1.getRole()
            role2 = obj2.getRole()
        except:
            msg = "GECKO: Exception getting role for %s and %s" % (obj1, obj2)
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        if not(role1 == role2 == pyatspi.ROLE_FRAME):
            return False

        try:
            name1 = obj1.name
            name2 = obj2.name
        except:
            msg = "GECKO: Exception getting name for %s and %s" % (obj1, obj2)
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        rv = name1 == name2
        msg = "GECKO: Treating %s and %s as same object: %s" % (obj1, obj2, rv)
        debug.println(debug.LEVEL_INFO, msg, True)
        return rv

    def isOnScreen(self, obj, boundingbox=None):
        if not super().isOnScreen(obj, boundingbox):
            return False
        if obj.getRole() != pyatspi.ROLE_UNKNOWN:
            return True

        if self.topLevelObject(obj) == obj.parent:
            msg = "INFO: %s is suspected to be off screen object" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return False

        return True

    def getOnScreenObjects(self, root, extents=None):
        objects = super().getOnScreenObjects(root, extents)

        # For things like Thunderbird's "Select columns to display" button
        if root.getRole() == pyatspi.ROLE_TREE_TABLE and root.childCount:
            isExtra = lambda x: x and x.getRole() != pyatspi.ROLE_COLUMN_HEADER
            objects.extend([x for x in root[0] if isExtra(x)])

        return objects

    def isEditableMessage(self, obj):
        """Returns True if this is an editable message."""

        if not obj:
            return False

        if not obj.getState().contains(pyatspi.STATE_EDITABLE):
            return False

        if self.isDocument(obj):
            msg = "GECKO: %s is believed to be an editable message" % obj
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        document = self.getContainingDocument(obj)
        if document and document.getState().contains(pyatspi.STATE_EDITABLE):
            msg = "GECKO: %s is in an editable document: %s" % (obj, document)
            debug.println(debug.LEVEL_INFO, msg, True)
            return True

        msg = "GECKO: Editable %s not in an editable document" % obj
        debug.println(debug.LEVEL_INFO, msg, True)
        return False
