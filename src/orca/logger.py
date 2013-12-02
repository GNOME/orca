# Orca
#
# Copyright 2008 Sun Microsystems Inc.
# Copyright 2012 Igalia, S.L.
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

"""Output logger for regression testing."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2012 Igalia, S.L."
__license__   = "LGPL"

import io
import logging

class Logger:

    def __init__(self):
        self._logs = {}

    def getLogNames(self):
        return self._logs.keys()

    def newLog(self, name, level=logging.INFO):
        log = logging.getLogger(name)
        log.setLevel(level)

        handler = logging.StreamHandler(io.StringIO())
        handler.setFormatter(logging.Formatter('%(message)s'))
        log.addHandler(handler)

        self._logs[name] = handler.stream
        return log

    def clearLog(self, name):
        stream = self._logs.get(name)
        if stream:
            stream.truncate(0)
            stream.seek(0)

    def getLogContent(self, name):
        stream = self._logs.get(name)
        if stream:
            return stream.getvalue()

        return ""

    def shutdown(self):
        for name in self._logs.keys():
            stream = self._logs.get(name)
            stream.close()

_logger = Logger()

def getLogger():
    return _logger
