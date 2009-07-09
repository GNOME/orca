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

import pyatspi

import braille
import debug
import rolenames
import settings

from orca_i18n import _         # for gettext support

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

        # pylint: disable-msg=W0108

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

            debug.println(
                debug.LEVEL_ALL,
                "generate %s for %s (args=%s) using '%s'" \
                % (self._mode,
                   debug.getAccessibleDetails(obj),
                   repr(args),
                   format))

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

        debug.println(debug.LEVEL_ALL, "generate %s results:" % self._mode)
        for element in result:
            debug.println(debug.LEVEL_ALL, "  " + str(element))

        return result

    #####################################################################
    #                                                                   #
    # Name, role, and label information                                 #
    #                                                                   #
    #####################################################################

    def _generateRoleName(self, obj, **args):
        """Returns the role name for the object in an array of strings, with
        the exception that the pyatspi.ROLE_UNKNOWN role will yield an
        empty array.  Note that a 'role' attribute in args will
        override the accessible role of the obj.
        """
        # Subclasses must override this.
        return []

    def _generateName(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the name of the object.  If the object is directly
        displaying any text, that text will be treated as the name.
        Otherwise, the accessible name of the object will be used.  If
        there is no accessible name, then the description of the
        object will be used.  This method will return an empty array
        if nothing can be found.  [[[WDW - I wonder if we should just
        have _generateName, _generateDescription,
        _generateDisplayedText, etc., that don't do any fallback.
        Then, we can allow the formatting to do the fallback (e.g.,
        'displayedText or name or description'). [[[JD to WDW - I
        needed a _generateDescription for whereAmI. :-) See below.
        """
        result = []
        name = self._script.getDisplayedText(obj)
        if name:
            result.append(name)
        elif obj.description:
            result.append(obj.description)
        return result

    def _generateLabelAndName(self, obj, **args):
        """Returns the label and the name as an array of strings for speech
        and braille.  The name will only be present if the name is
        different from the label.
        """
        result = []
        label = self._generateLabel(obj, **args)
        name = self._generateName(obj, **args)
        result.extend(label)
        if not len(label):
            result.extend(name)
        elif len(name) and name[0] != label[0]:
            result.extend(name)
        return result

    def _generateLabelOrName(self, obj, **args):
        """Returns the label as an array of strings for speech and braille.
        If the label cannot be found, the name will be used instead.
        If the name cannot be found, an empty array will be returned.
        """
        result = []
        result.extend(self._generateLabel(obj, **args))
        if not result:
            if obj.name and (len(obj.name)):
                result.append(obj.name)
        return result

    def _generateDescription(self, obj, **args):
        """Returns an array of strings fo use by speech and braille that
        represent the description of the object, if that description
        is different from that of the name and label.
        """
        result = []
        label = self._script.getDisplayedLabel(obj)
        if obj.description and not obj.description in [obj.name, label]:
            result.append(obj.description)
        return result

    def _generateLabel(self, obj, **args):
        """Returns the label for an object as an array of strings for use by
        speech and braille.  The label is determined by the
        getDisplayedLabel of the script, and an empty array will be
        returned if no label can be found.
        """
        result = []
        label = self._script.getDisplayedLabel(obj)
        if label:
            result.append(label)
        return result

    #####################################################################
    #                                                                   #
    # Image information                                                 #
    #                                                                   #
    #####################################################################

    def _generateImageDescription(self, obj, **args ):
        """Returns an array of strings for use by speech and braille that
        represent the description of the image on the object, if it
        exists.  Otherwise, an empty array is returned.
        """
        result = []
        try:
            image = obj.queryImage()
        except NotImplementedError:
            pass
        else:
            description = image.imageDescription
            if description and len(description):
                result.append(description)
        return result

    #####################################################################
    #                                                                   #
    # State information                                                 #
    #                                                                   #
    #####################################################################

    def _generateAvailability(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the grayed/sensitivity/availability state of the
        object, but only if it is insensitive (i.e., grayed out and
        inactive).  Otherwise, and empty array will be returned.
        """
        result = []
        if not args.get('mode', None):
            args['mode'] = self._mode
        args['stringType'] = 'insensitive'
        if not obj.getState().contains(pyatspi.STATE_SENSITIVE):
            result.append(self._script.formatting.getString(**args))
        return result

    def _generateRequired(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the required state of the object, but only if it is
        required (i.e., it is in a dialog requesting input and the
        user must give it a value).  Otherwise, and empty array will
        be returned.
        """
        result = []
        if not args.get('mode', None):
            args['mode'] = self._mode
        args['stringType'] = 'required'
        if obj.getState().contains(pyatspi.STATE_REQUIRED) \
           or (obj.getRole() == pyatspi.ROLE_RADIO_BUTTON \
               and obj.parent.getState().contains(pyatspi.STATE_REQUIRED)):
            result.append(self._script.formatting.getString(**args))
        return result

    def _generateReadOnly(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the read only state of this object, but only if it
        is read only (i.e., it is a text area that cannot be edited).
        """
        result = []
        if not args.get('mode', None):
            args['mode'] = self._mode
        args['stringType'] = 'readonly'
        if settings.presentReadOnlyText \
           and self._script.isReadOnlyTextArea(obj):
            result.append(self._script.formatting.getString(**args))
        return result

    def _generateCellCheckedState(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the checked state of the object.  This is typically
        for check boxes that are in a table. An empty array will be
        returned if this is not a checkable cell.
        """
        result = []
        try:
            action = obj.queryAction()
        except NotImplementedError:
            action = None
        if action:
            for i in range(0, action.nActions):
                # Translators: this is the action name for
                # the 'toggle' action. It must be the same
                # string used in the *.po file for gail.
                #
                if action.getName(i) in ["toggle", _("toggle")]:
                    oldRole = self._overrideRole(pyatspi.ROLE_CHECK_BOX,
                                            args)
                    result.extend(self.generate(obj, **args))
                    self._restoreRole(oldRole, args)
        return result

    def _generateCheckedState(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the checked state of the object.  This is typically
        for check boxes. [[[WDW - should we return an empty array if
        we can guarantee we know this thing is not checkable?]]]
        """
        result = []
        if not args.get('mode', None):
            args['mode'] = self._mode
        args['stringType'] = 'checkbox'
        indicators = self._script.formatting.getString(**args)
        state = obj.getState()
        if state.contains(pyatspi.STATE_INDETERMINATE):
            result.append(indicators[2])
        elif state.contains(pyatspi.STATE_CHECKED):
            result.append(indicators[1])
        else:
            result.append(indicators[0])
        return result

    def _generateRadioState(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the checked state of the object.  This is typically
        for check boxes. [[[WDW - should we return an empty array if
        we can guarantee we know this thing is not checkable?]]]
        """
        result = []
        if not args.get('mode', None):
            args['mode'] = self._mode
        args['stringType'] = 'radiobutton'
        indicators = self._script.formatting.getString(**args)
        state = obj.getState()
        if state.contains(pyatspi.STATE_CHECKED):
            result.append(indicators[1])
        else:
            result.append(indicators[0])
        return result

    def _generateToggleState(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the checked state of the object.  This is typically
        for check boxes. [[[WDW - should we return an empty array if
        we can guarantee we know this thing is not checkable?]]]
        """
        result = []
        if not args.get('mode', None):
            args['mode'] = self._mode
        args['stringType'] = 'togglebutton'
        indicators = self._script.formatting.getString(**args)
        state = obj.getState()
        if state.contains(pyatspi.STATE_CHECKED) \
           or state.contains(pyatspi.STATE_PRESSED):
            result.append(indicators[1])
        else:
            result.append(indicators[0])
        return result

    def _generateMenuItemCheckedState(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the checked state of the menu item, only if it is
        checked. Otherwise, and empty array will be returned.
        """
        result = []
        if not args.get('mode', None):
            args['mode'] = self._mode
        args['stringType'] = 'checkbox'
        indicators = self._script.formatting.getString(**args)
        if obj.getState().contains(pyatspi.STATE_CHECKED):
            # Translators: this represents the state of a checked menu item.
            #
            result.append(indicators[1])
        return result

    def _generateExpandableState(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the expanded/collapsed state of an object, such as a
        tree node. If the object is not expandable, an empty array
        will be returned.
        """
        result = []
        if not args.get('mode', None):
            args['mode'] = self._mode
        args['stringType'] = 'expansion'
        indicators = self._script.formatting.getString(**args)
        state = obj.getState()
        if state.contains(pyatspi.STATE_EXPANDABLE):
            if state.contains(pyatspi.STATE_EXPANDED):
                result.append(indicators[1])
            else:
                result.append(indicators[0])
        return result

    #####################################################################
    #                                                                   #
    # Table interface information                                       #
    #                                                                   #
    #####################################################################

    def _generateRowHeader(self, obj, **args):
        """Returns an array of strings to be used in speech and braille that
        represent the row header for an object that is in a table, if
        it exists.  Otherwise, an empty array is returned.
        """
        result = []

        # Do not return yourself as a header.
        #
        role = args.get('role', obj.getRole())
        if role in [pyatspi.ROLE_ROW_HEADER,
                    pyatspi.ROLE_TABLE_ROW_HEADER]:
            return result

        if not args.get('mode', None):
            args['mode'] = self._mode
        try:
            table = obj.parent.queryTable()
        except:
            pass
        else:
            index = self._script.getCellIndex(obj)
            rowIndex = table.getRowAtIndex(index)
            if rowIndex >= 0:
                # Get the header information.  In Java Swing, the
                # information is not exposed via the description
                # but is instead a header object, so we fall back
                # to that if it exists.
                #
                # [[[TODO: WDW - the more correct thing to do, I
                # think, is to look at the row header object.
                # We've been looking at the description for so
                # long, though, that we'll give the description
                # preference for now.]]]
                #
                desc = table.getRowDescription(rowIndex)
                if not desc:
                    header = table.getRowHeader(rowIndex)
                    if header:
                        desc = self._script.getDisplayedText(header)
                if desc and len(desc):
                    text = desc
                    if args['mode'] == 'speech':
                        if settings.speechVerbosityLevel \
                           == settings.VERBOSITY_LEVEL_VERBOSE \
                           and not args.get('formatType', None) \
                                   in ['basicWhereAmI', 'detailedWhereAmI']:
                            text += " " + rolenames.rolenames[\
                                    pyatspi.ROLE_ROW_HEADER].speech
                    elif args['mode'] == 'braille':
                        if settings.brailleVerbosityLevel \
                           == settings.VERBOSITY_LEVEL_VERBOSE:
                            if settings.brailleRolenameStyle \
                               == settings.BRAILLE_ROLENAME_STYLE_LONG:
                                text = desc + " " + rolenames.rolenames[\
                                       pyatspi.ROLE_ROW_HEADER].brailleLong
                            else:
                                text = desc + " " + rolenames.rolenames[\
                                       pyatspi.ROLE_ROW_HEADER].brailleShort
                    result.append(text)
        return result

    def _generateColumnHeader(self, obj, **args):
        """Returns an array of strings (and possibly voice and audio
        specifications) that represent the column header for an object
        that is in a table, if it exists.  Otherwise, an empty array
        is returned.
        """
        result = []

        # Do not return yourself as a header.
        #
        role = args.get('role', obj.getRole())
        if role in [pyatspi.ROLE_COLUMN_HEADER,
                    pyatspi.ROLE_TABLE_COLUMN_HEADER]:
            return result

        try:
            table = obj.parent.queryTable()
        except:
            pass
        else:
            index = self._script.getCellIndex(obj)
            columnIndex = table.getColumnAtIndex(index)
            if columnIndex >= 0:
                # Get the header information.  In Java Swing, the
                # information is not exposed via the description
                # but is instead a header object, so we fall back
                # to that if it exists.
                #
                # [[[TODO: WDW - the more correct thing to do, I
                # think, is to look at the column header object.
                # We've been looking at the description for so
                # long, though, that we'll give the description
                # preference for now.]]]
                #
                desc = table.getColumnDescription(columnIndex)
                if not desc:
                    header = table.getColumnHeader(columnIndex)
                    if header:
                        desc = self._script.getDisplayedText(header)
                if desc and len(desc):
                    text = desc
                    if args['mode'] == 'speech':
                        if settings.speechVerbosityLevel \
                           == settings.VERBOSITY_LEVEL_VERBOSE \
                           and not args.get('formatType', None) \
                                   in ['basicWhereAmI', 'detailedWhereAmI']:
                            text += " " + rolenames.rolenames[\
                                    pyatspi.ROLE_COLUMN_HEADER].speech
                    elif args['mode'] == 'braille':
                        if settings.brailleVerbosityLevel \
                           == settings.VERBOSITY_LEVEL_VERBOSE:
                            if settings.brailleRolenameStyle \
                               == settings.BRAILLE_ROLENAME_STYLE_LONG:
                                text = desc + " " + rolenames.rolenames[\
                                       pyatspi.ROLE_COLUMN_HEADER].brailleLong
                            else:
                                text = desc + " " + rolenames.rolenames[\
                                       pyatspi.ROLE_COLUMN_HEADER].brailleShort
                    result.append(text)
        return result

    def _generateTableCell2ChildLabel(self, obj, **args):
        """Returns an array of strings for use by speech and braille for the
        label of a toggle in a table cell that has a special 2 child
        pattern that we run into.  Otherwise, an empty array is
        returned.
        """
        result = []

        # If this table cell has 2 children and one of them has a
        # 'toggle' action and the other does not, then present this
        # as a checkbox where:
        # 1) we get the checked state from the cell with the 'toggle' action
        # 2) we get the label from the other cell.
        # See Orca bug #376015 for more details.
        #
        if obj.childCount == 2:
            cellOrder = []
            hasToggle = [False, False]
            for i, child in enumerate(obj):
                try:
                    action = child.queryAction()
                except NotImplementedError:
                    continue
                else:
                    for j in range(0, action.nActions):
                        # Translators: this is the action name for
                        # the 'toggle' action. It must be the same
                        # string used in the *.po file for gail.
                        #
                        if action.getName(j) in ["toggle", _("toggle")]:
                            hasToggle[i] = True
                            break
            if hasToggle[0] and not hasToggle[1]:
                cellOrder = [ 1, 0 ]
            elif not hasToggle[0] and hasToggle[1]:
                cellOrder = [ 0, 1 ]
            if cellOrder:
                for i in cellOrder:
                    if not hasToggle[i]:
                        result.extend(self.generate(obj[i], **args))
        return result

    def _generateTableCell2ChildToggle(self, obj, **args):
        """Returns an array of strings for use by speech and braille for the
        toggle value of a toggle in a table cell that has a special 2
        child pattern that we run into.  Otherwise, an empty array is
        returned.
        """
        result = []

        # If this table cell has 2 children and one of them has a
        # 'toggle' action and the other does not, then present this
        # as a checkbox where:
        # 1) we get the checked state from the cell with the 'toggle' action
        # 2) we get the label from the other cell.
        # See Orca bug #376015 for more details.
        #
        if obj.childCount == 2:
            cellOrder = []
            hasToggle = [False, False]
            for i, child in enumerate(obj):
                try:
                    action = child.queryAction()
                except NotImplementedError:
                    continue
                else:
                    for j in range(0, action.nActions):
                        # Translators: this is the action name for
                        # the 'toggle' action. It must be the same
                        # string used in the *.po file for gail.
                        #
                        if action.getName(j) in ["toggle", _("toggle")]:
                            hasToggle[i] = True
                            break

            if hasToggle[0] and not hasToggle[1]:
                cellOrder = [ 1, 0 ]
            elif not hasToggle[0] and hasToggle[1]:
                cellOrder = [ 0, 1 ]
            if cellOrder:
                for i in cellOrder:
                    if hasToggle[i]:
                        result.extend(self.generate(obj[i], **args))
        return result

    def _generateColumnHeaderIfToggleAndNoText(self, obj, **args):
        """If this table cell has a "toggle" action, and doesn't have any
        label associated with it then also speak the table column
        header.  See Orca bug #455230 for more details.
        """
        # If we're reading just a single cell in speech, the new
        # header portion is going to give us this information.
        #
        if args['mode'] == 'speech' and not args.get('readingRow', False):
            return []

        result = []
        try:
            parentTable = obj.parent.queryTable()
        except:
            return result
        try:
            action = obj.queryAction()
            label = self._script.getDisplayedText(
                        self._script.getRealActiveDescendant(obj))
        except NotImplementedError:
            action = None
            label = None
        if action and (label == None or len(label) == 0):
            index = self._script.getCellIndex(obj)
            column = parentTable.getColumnAtIndex(index)
            for j in range(0, action.nActions):
                # Translators: this is the action name for
                # the 'toggle' action. It must be the same
                # string used in the *.po file for gail.
                #
                if action.getName(j) in ["toggle",
                                         _("toggle")]:
                    accHeader = \
                        parentTable.getColumnHeader(column)
                    result.append(accHeader.name)
        return result

    def _generateRealTableCell(self, obj, **args):
        """Orca has a feature to automatically read an entire row of a table
        as the user arrows up/down the roles.  This leads to
        complexity in the code.  This method is used to return an
        array of strings for use by speech and braille for a single
        table cell itself.  The string, 'blank', is added for empty
        cells.
        """
        result = []
        oldRole = self._overrideRole('REAL_ROLE_TABLE_CELL', args)
        result.extend(self.generate(obj, **args))
        self._restoreRole(oldRole, args)
        return result

    def _generateTableCellRow(self, obj, **args):
        """Orca has a feature to automatically read an entire row of a table
        as the user arrows up/down the roles.  This leads to complexity in
        the code.  This method is used to return an array of strings
        (and possibly voice and audio specifications) for an entire row
        in a table if that's what the user has requested and if the row
        has changed.  Otherwise, it will return an array for just the
        current cell.
        """
        result = []

        try:
            parentTable = obj.parent.queryTable()
        except:
            parentTable = None
        isDetailedWhereAmI = args.get('formatType', None) == 'detailedWhereAmI'
        if (settings.readTableCellRow or isDetailedWhereAmI) and parentTable \
           and (not self._script.isLayoutOnly(obj.parent)):
            parent = obj.parent
            index = self._script.getCellIndex(obj)
            row = parentTable.getRowAtIndex(index)
            column = parentTable.getColumnAtIndex(index)

            # This is an indication of whether we should speak all the
            # table cells (the user has moved focus up or down a row),
            # or just the current one (focus has moved left or right in
            # the same row).
            #
            presentAll = True
            if isDetailedWhereAmI:
                if parentTable.nColumns <= 1:
                    return result
            elif "lastRow" in self._script.pointOfReference \
               and "lastColumn" in self._script.pointOfReference:
                pointOfReference = self._script.pointOfReference
                presentAll = \
                    (self._mode == 'braille') \
                    or \
                    ((pointOfReference["lastRow"] != row) \
                     or ((row == 0 or row == parentTable.nRows-1) \
                         and pointOfReference["lastColumn"] == column))
            if presentAll:
                args['readingRow'] = True
                for i in range(0, parentTable.nColumns):
                    cell = parentTable.getAccessibleAt(row, i)
                    if not cell:
                        continue
                    state = cell.getState()
                    showing = state.contains(pyatspi.STATE_SHOWING)
                    if showing:
                        cellResult = self._generateRealTableCell(cell, **args)
                        if cellResult and result and self._mode == 'braille':
                            result.append(braille.Region(
                                    settings.brailleTableCellDelimiter))
                        result.extend(cellResult)
            else:
                result.extend(self._generateRealTableCell(obj, **args))
        else:
            result.extend(self._generateRealTableCell(obj, **args))
        return result

    #####################################################################
    #                                                                   #
    # Text interface information                                        #
    #                                                                   #
    #####################################################################

    def _generateCurrentLineText(self, obj, **args ):
        """Returns an array of strings for use by speech and braille
        that represents the current line of text, if
        this is a text object.  [[[WDW - consider returning an empty
        array if this is not a text object.]]]
        """
        [text, caretOffset, startOffset] = self._script.getTextLineAtCaret(obj)
        return [text]

    def _generateDisplayedText(self, obj, **args ):
        """Returns an array of strings for use by speech and braille that
        represents all the text being displayed by the object. [[[WDW
        - consider returning an empty array if this is not a text
        object.]]]
        """
        return [self._script.getDisplayedText(obj)]

    #####################################################################
    #                                                                   #
    # Tree interface information                                        #
    #                                                                   #
    #####################################################################

    def _generateNodeLevel(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represents the tree node level of the object, or an empty
        array if the object is not a tree node.
        """
        result = []
        if not args.get('mode', None):
            args['mode'] = self._mode
        args['stringType'] = 'nodelevel'
        level = self._script.getNodeLevel(obj)
        if level >= 0:
            result.append(self._script.formatting.getString(**args)\
                          % (level + 1))
        return result

    #####################################################################
    #                                                                   #
    # Value interface information                                       #
    #                                                                   #
    #####################################################################

    def _generateValue(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represents the value of the object.  This is typically the
        numerical value, but may also be the text of the 'value'
        attribute if it exists on the object.  [[[WDW - we should
        consider returning an empty array if there is no value.
        """
        return [self._script.getTextForValue(obj)]

    #####################################################################
    #                                                                   #
    # Hierarchy and related dialog information                          #
    #                                                                   #
    #####################################################################

    def _generateApplicationName(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represents the name of the applicaton for the object.
        """
        result = []
        try:
            result.append(obj.getApplication().name)
        except:
            pass
        return result

    def _generateNestingLevel(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represent the nesting level of an object in a list.
        """
        result = []
        if not args.get('mode', None):
            args['mode'] = self._mode
        args['stringType'] = 'nestinglevel'
        nestingLevel = self._script.getNestingLevel(obj)
        if nestingLevel:
            result.append(self._script.formatting.getString(**args)\
                          % nestingLevel)
        return result

    def _generateRadioButtonGroup(self, obj, **args):
        """Returns an array of strings for use by speech and braille that
        represents the radio button group label for the object, or an
        empty array if the object has no such label.
        """
        result = []
        if obj.getRole() == pyatspi.ROLE_RADIO_BUTTON:
            radioGroupLabel = None
            relations = obj.getRelationSet()
            for relation in relations:
                if (not radioGroupLabel) \
                    and (relation.getRelationType() \
                         == pyatspi.RELATION_LABELLED_BY):
                    radioGroupLabel = relation.getTarget(0)
                    break
            if radioGroupLabel:
                result.append(self._script.getDisplayedText(radioGroupLabel))
            else:
                parent = obj.parent
                while parent and (parent.parent != parent):
                    if parent.getRole() in [pyatspi.ROLE_PANEL,
                                            pyatspi.ROLE_FILLER]:
                        label = self._generateLabelAndName(parent)
                        if label:
                            result.extend(label)
                            break
                    parent = parent.parent
        return result

    def _generateRealActiveDescendantDisplayedText(self, obj, **args ):
        """Objects, such as tables and trees, can represent individual cells
        via a complicated nested hierarchy.  This method returns an
        array of strings for use by speech and braille that represents
        the text actually being painted in the cell, if it can be
        found.  Otherwise, an empty array is returned.
        """
        result = []
        text = self._script.getDisplayedText(
          self._script.getRealActiveDescendant(obj))
        if text:
            result = [text]
        return result

    def _generateRealActiveDescendantRoleName(self, obj, **args ):
        """Objects, such as tables and trees, can represent individual cells
        via a complicated nested hierarchy.  This method returns an
        array of strings for use by speech and braille that represents
        the role of the object actually being painted in the cell.
        """
        rad = self._script.getRealActiveDescendant(obj)
        args['role'] = rad.getRole()
        return self._generateRoleName(rad, **args)
