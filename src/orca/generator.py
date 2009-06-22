# Orca
#
# Copyright 2009 Sun Microsystems Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

"""Superclass of classes used to generate presentations for objects."""

__id__        = "$Id:$"
__version__   = "$Revision:$"
__date__      = "$Date:$"
__copyright__ = "Copyright (c) 2009 Sun Microsystems Inc."
__license__   = "LGPL"

import sys
import traceback

import debug
import pyatspi

def _formatExceptionInfo(maxTBlevel=5):
    cla, exc, trbk = sys.exc_info()
    excName = cla.__name__
    try:
        excArgs = exc.args
    except KeyError:
        excArgs = "<no args>"
    excTb = traceback.format_tb(trbk, maxTBlevel)
    return (excName, excArgs, excTb)

# [[[WDW - general note -- for all the _generate* methods, it would be great if
# we could return an empty array if we can determine the method does not
# apply to the object.  This would allow us to reduce the number of strings
# needed in formatting.py.]]]

# The prefix to use for the individual generator methods
#
METHOD_PREFIX = "_generate"

class Generator:
    """Takes accessible objects and generates a presentation for those
    objects.  See the generate method, which is the primary entry
    point."""

    # pylint: disable-msg=W0142

    def __init__(self, script, mode):
        self._mode = mode
        self._script = script
        self._methodsDict = {}
        for method in \
            filter(lambda z: callable(z),
                   map(lambda y: getattr(self, y).__get__(self, self.__class__),
                       filter(lambda x: x.startswith(METHOD_PREFIX),
                                        dir(self)))):
            name = method.__name__[len(METHOD_PREFIX):]
            name = name[0].lower() + name[1:]
            self._methodsDict[name] = method
        self._verifyFormatting()

    def _addGlobals(self, globalsDict):
        """Other things to make available from the formatting string.
        """
        globalsDict['obj'] = None
        globalsDict['role'] = None
        globalsDict['pyatspi'] = pyatspi

    def _verifyFormatting(self):

        # Verify the formatting strings are OK.  This is only
        # for verification and does not effect the function of
        # Orca at all.

        # Populate the entire globals with empty arrays
        # for the results of all the legal method names.
        #
        globalsDict = {}
        for key in self._methodsDict.keys():
            globalsDict[key] = []
        self._addGlobals(globalsDict)

        for roleKey in self._script.formatting[self._mode]:
            for key in ["focused", "unfocused"]:
                try:
                    evalString = \
                        self._script.formatting[self._mode][roleKey][key]
                except:
                    continue
                else:
                    if not evalString:
                        # It's legal to have an empty string.
                        #
                        continue
                    while True:
                        try:
                            eval(evalString, globalsDict)
                            break
                        except NameError:
                            info = _formatExceptionInfo()
                            arg = info[1][0]
                            arg = arg.replace("name '", "")
                            arg = arg.replace("' is not defined", "")
                            if not self._methodsDict.has_key(arg):
                                debug.printException(debug.LEVEL_SEVERE)
                                debug.println(
                                    debug.LEVEL_SEVERE,
                                    "Unable to find function for '%s'\n" % arg)
                            globalsDict[arg] = []
                        except:
                            debug.printException(debug.LEVEL_SEVERE)
                            debug.println(
                                debug.LEVEL_SEVERE,
                                "While processing '%s' '%s' '%s' '%s'" \
                                % (roleKey, key, evalString, globalsDict))
                            break

    def _overrideRole(self, newRole, args):
        """Convenience method to allow you to temporarily override the role in
        the args dictionary.  This changes the role in args ags
        returns the old role so you can pass it back to _restoreRole.
        """
        oldRole = args.get('role', None)
        args['role'] = newRole
        return oldRole

    def _restoreRole(self, oldRole, args):
        """Convenience method to restore the old role back in the args
        dictionary.  The oldRole should have been obtained from
        _overrideRole.  If oldRole is None, then the 'role' key/value
        pair will be deleted from args.
        """
        if oldRole:
            args['role'] = oldRole
        else:
            del args['role']

    def generate(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the complete presentatin for the
        object.  The presentatin to be generated depends highly upon the
        formatting strings in formatting.py.

        args is a dictionary that may contain any of the following:
        - alreadyFocused: if True, we're getting an object
          that previously had focus
        - priorObj: if set, represents the object that had focus before
          this object
        - includeContext: boolean (default=True) which says whether
          the context for an object should be included as a prefix
          and suffix
        - role: a role to override the object's role
        - formatType: the type of formatting, such as
          'focused', 'basicWhereAmI', etc.
        - forceMnemonic: boolean (default=False) which says if we
          should ignore the settings.enableMnemonicSpeaking setting
        - forceTutorial: boolean (default=False) which says if we
          should force a tutorial to be spoken or not
        """
        result = []
        globalsDict = {}
        self._addGlobals(globalsDict)
        globalsDict['obj'] = obj
        globalsDict['role'] = args.get('role', obj.getRole())

        try:
            # We sometimes want to override the role.  We'll keep the
            # role in the args dictionary as a means to let us do so.
            #
            args['role'] = globalsDict['role']

            # We loop through the format string, catching each error
            # as we go.  Each error should always be a NameError,
            # where the name is the name of one of our generator
            # functions.  When we encounter this, we call the function
            # and get its results, placing them in the globals for the
            # the call to eval.
            #
            args['mode'] = self._mode
            if not args.get('formatType', None):
                if args.get('alreadyFocused', False):
                    args['formatType'] = 'focused'
                else:
                    args['formatType'] = 'unfocused'

            format = self._script.formatting.getFormat(**args)

            # Add in the context if this is the first time
            # we've been called.
            #
            if not args.get('recursing', False):
                if args.get('includeContext', True):
                    prefix = self._script.formatting.getPrefix(**args)
                    suffix = self._script.formatting.getSuffix(**args)
                    format = '%s + %s + %s' % (prefix, format, suffix)
                args['recursing'] = True
                firstTimeCalled = True
            else:
                firstTimeCalled = False

            debug.println(debug.LEVEL_ALL, "generate %s for %s using '%s'" \
                          % (self._mode, repr(args), format))

            assert(format)
            while True:
                try:
                    result = eval(format, globalsDict)
                    break
                except NameError:
                    result = []
                    info = _formatExceptionInfo()
                    arg = info[1][0]
                    arg = arg.replace("name '", "")
                    arg = arg.replace("' is not defined", "")
                    if not self._methodsDict.has_key(arg):
                        debug.printException(debug.LEVEL_SEVERE)
                        debug.println(
                            debug.LEVEL_SEVERE,
                            "Unable to find function for '%s'\n" % arg)
                        break
                    globalsDict[arg] = self._methodsDict[arg](obj, **args)
                    debug.println(debug.LEVEL_ALL,
                                  "%s=%s" % (arg, repr(globalsDict[arg])))
        except:
            debug.printException(debug.LEVEL_SEVERE)
            result = []

        debug.println(debug.LEVEL_ALL,
                      "generate %s generated '%s'" % (self._mode, repr(result)))

        return result
