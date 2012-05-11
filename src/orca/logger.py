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

import logging
import StringIO

from . import debug

class Logger:

    def __init__(self, *types):
        self._types = types or ['braille', 'speech']
        self._fileHandlers = {}
        self._streamHandlers = {}
        self._formatter = logging.Formatter('%(message)s')

    def setDebug(self, debugFile, debugLevel):
        if debug.debugFile:
            debug.debugFile.close()
            debug.debugFile = None
        if debugFile:
            debug.debugFile = open('%s.debug' % debugFile, 'w', 0)
            debug.debugLevel = debugLevel

    def setLogFile(self, logFile):
        self._closeFileHandlers()
        self._createFileHandlers(logFile)

    def startRecording(self):
        self._closeStreamHandlers()
        self._createStreamHandlers()

    def stopRecording(self):
        return self._closeStreamHandlers()

    def _createFileHandlers(self, fileName):
        if not fileName:
            return

        for logger in self._types:
            handler = logging.FileHandler('%s.%s' % (fileName, logger), 'w')
            self._fileHandlers[logger] = handler
            log = logging.getLogger(logger)
            self._createHandler(log, handler)

    def _createStreamHandlers(self):
        for logger in self._types:
            stringIO = StringIO.StringIO()
            handler = logging.StreamHandler(stringIO)
            self._streamHandlers[logger] = [stringIO, handler]
            log = logging.getLogger(logger)
            self._createHandler(log, handler)

    def _createHandler(self, log, handler):
        handler.setFormatter(self._formatter)
        log.setLevel(logging.INFO)
        log.addHandler(handler)

    def _closeFileHandlers(self):
        for logger in self._types:
            log = logging.getLogger(logger)
            handler = self._fileHandlers.get(logger)
            self._closeHandler(log, handler)

    def _closeStreamHandlers(self):
        result = ''
        for logger in self._types:
            log = logging.getLogger(logger)
            stringIO, handler = self._streamHandlers.get(logger, (None, None))
            self._closeHandler(log, handler)
            if stringIO:
                try:
                    result += stringIO.getvalue()
                    stringIO.close()
                except ValueError:
                    pass

        return result

    def _closeHandler(self, log, handler):
        try:
            handler.flush()
            handler.close()
            log.removeHandler(handler)
        except:
            pass
