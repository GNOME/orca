# Orca
#
# Copyright 2005-2009 Sun Microsystems Inc.
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

"""Utilities for obtaining speech utterances for objects.  In general,
there probably should be a singleton instance of the SpeechGenerator
class."""

__id__        = "$Id:$"
__version__   = "$Revision:$"
__date__      = "$Date:$"
__copyright__ = "Copyright (c) 2005-2009 Sun Microsystems Inc."
__license__   = "LGPL"

import sys
import traceback

import debug
import orca_state
import pyatspi
import rolenames
import settings

from orca_i18n import _         # for gettext support
from orca_i18n import ngettext  # for ngettext support
from orca_i18n import C_        # to provide qualified translatable strings

def _formatExceptionInfo(maxTBlevel=5):
    cla, exc, trbk = sys.exc_info()
    excName = cla.__name__
    try:
        excArgs = exc.args
    except KeyError:
        excArgs = "<no args>"
    excTb = traceback.format_tb(trbk, maxTBlevel)
    return (excName, excArgs, excTb)

class SpeechGenerator:
    """Takes accessible objects and produces a string to speak for
    those objects.  See the getSpeech method, which is the primary
    entry point.  Subclasses can feel free to override/extend the
    speechGenerators instance field as they see fit."""

    # pylint: disable-msg=W0142

    def _overrideRole(self, newRole, args):
        oldRole = args.get('role', None)
        args['role'] = newRole
        return oldRole

    def _restoreRole(self, oldRole, args):
        if oldRole:
            args['role'] = oldRole
        else:
            del args['role']

    def __init__(self, script):
        self._script = script
        self._methodsDict = {}
        for method in \
            filter(lambda z: callable(z),
                   map(lambda y: getattr(self, y).__get__(self, self.__class__),
                       filter(lambda x: x.startswith("_get"), dir(self)))):
            name = method.__name__[4:]
            name = name[0].lower() + name[1:]
            self._methodsDict[name] = method

        # Verify the formatting strings are OK.  This is only
        # for verification and does not effect the function of
        # Orca at all.
        #
        # Populate the entire globals with empty arrays
        # for the results of all the legal method names.
        #
        methods = {}
        for key in self._methodsDict.keys():
            methods[key] = []
        methods['voice'] = self.voice
        methods['obj'] = None
        methods['role'] = None
        methods['pyatspi'] = pyatspi
        for roleKey in self._script.formatting["speech"]:
            for speechKey in ["focused", "unfocused"]:
                try:
                    evalString = \
                        self._script.formatting["speech"][roleKey][speechKey]
                except:
                    continue
                else:
                    if not evalString:
                        # It's legal to have an empty string for speech.
                        #
                        continue
                    while True:
                        try:
                            eval(evalString, methods)
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
                        except:
                            debug.printException(debug.LEVEL_SEVERE)
                            debug.println(
                                debug.LEVEL_SEVERE,
                                "While processing '%s' '%s' '%s' '%s'" \
                                % (roleKey, speechKey, evalString, methods))
                            break

    #####################################################################
    #                                                                   #
    # Name, role, and label information                                 #
    #                                                                   #
    #####################################################################

    def _getName(self, obj, **args):
        result = []
        name = self._script.getDisplayedText(obj)
        if name:
            result.append(name)
        elif obj.description:
            result.append(obj.description)
        return result

    def _getTextRole(self, obj, **args):
        result = []
        role = args.get('role', obj.getRole())
        if role != pyatspi.ROLE_PARAGRAPH:
            result.extend(self._getRoleName(obj, **args))
        return result

    def _getRoleName(self, obj, **args):
        result = []
        role = args.get('role', obj.getRole())
        if (role != pyatspi.ROLE_UNKNOWN):
            result.append(rolenames.getSpeechForRoleName(obj, role))
        return result

    def _getLabel(self, obj, **args):
        result = []
        label = self._script.getDisplayedLabel(obj)
        if label:
            result = [label]
        return result

    def _getLabelAndName(self, obj, **args):
        """Gets the label and the name if the name is different from the label.
        """
        result = []
        label = self._getLabel(obj, **args)
        name = self._getName(obj, **args)
        result.extend(label)
        if not len(label):
            result.extend(name)
        elif len(name) and name[0] != label[0]:
            result.extend(name)
        return result

    def _getLabelOrName(self, obj, **args):
        """Gets the label or the name if the label is not preset."""
        result = []
        result.extend(self._getLabel(obj, **args))
        if not result:
            if obj.name and (len(obj.name)):
                result.append(obj.name)
        return result

    def _getUnrelatedLabels(self, obj, **args):
        """Finds all labels not in a label for or labelled by relation."""
        labels = self._script.findUnrelatedLabels(obj)
        result = []
        for label in labels:
            name = self._getName(label, **args)
            result.extend(name)
        return result

    def _getEmbedded(self, obj, **args):
        result = self._getLabelOrName(obj, **args)
        if not result:
            try:
                result.append(obj.getApplication().name)
            except:
                pass
        return result

    #####################################################################
    #                                                                   #
    # State information                                                 #
    #                                                                   #
    #####################################################################

    def _getCheckedState(self, obj, **args):
        result = []
        state = obj.getState()
        if state.contains(pyatspi.STATE_INDETERMINATE):
            # Translators: this represents the state of a checkbox.
            #
            result.append(_("partially checked"))
        elif state.contains(pyatspi.STATE_CHECKED):
            # Translators: this represents the state of a checkbox.
            #
            result.append(_("checked"))
        else:
            # Translators: this represents the state of a checkbox.
            #
            result.append(_("not checked"))
        return result

    def _getCellCheckedState(self, obj, **args):
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
                    result.extend(self.getSpeech(obj, **args))
                    self._restoreRole(oldRole, args)
        return result

    def _getRadioState(self, obj, **args):
        result = []
        state = obj.getState()
        if state.contains(pyatspi.STATE_CHECKED):
            # Translators: this is in reference to a radio button being
            # selected or not.
            #
            result.append(C_("radiobutton", "selected"))
        else:
            # Translators: this is in reference to a radio button being
            # selected or not.
            #
            result.append(C_("radiobutton", "not selected"))
        return result

    def _getToggleState(self, obj, **args):
        result = []
        state = obj.getState()
        if state.contains(pyatspi.STATE_CHECKED) \
           or state.contains(pyatspi.STATE_PRESSED):
            # Translators: the state of a toggle button.
            #
            result.append(_("pressed"))
        else:
            # Translators: the state of a toggle button.
            #
            result.append(_("not pressed"))
        return result

    def _getExpandableState(self, obj, **args):
        result = []
        state = obj.getState()
        if state.contains(pyatspi.STATE_EXPANDABLE):
            if state.contains(pyatspi.STATE_EXPANDED):
                # Translators: this represents the state of a node in a tree.
                # 'expanded' means the children are showing.
                # 'collapsed' means the children are not showing.
                #
                result.append(_("expanded"))
            else:
                # Translators: this represents the state of a node in a tree.
                # 'expanded' means the children are showing.
                # 'collapsed' means the children are not showing.
                #
                result.append(_("collapsed"))
        return result

    def _getMenuItemCheckedState(self, obj, **args):
        result = []
        state = obj.getState()
        if state.contains(pyatspi.STATE_CHECKED):
            # Translators: this represents the state of a checked menu item.
            #
            result.append(_("checked"))
        return result

    def _getAvailability(self, obj, **args):
        result = []
        state = obj.getState()
        if not state.contains(pyatspi.STATE_SENSITIVE):
            # Translators: this represents an item on the screen that has
            # been set insensitive (or grayed out).
            #
            result.append(_("grayed"))
        return result

    def _getRequired(self, obj, **args):
        result = []
        state = obj.getState()
        if state.contains(pyatspi.STATE_REQUIRED):
            result = [settings.speechRequiredStateString]
        return result

    def _getReadOnly(self, obj, **args):
        result = []
        if settings.presentReadOnlyText \
           and self._script.isReadOnlyTextArea(obj):
            result.append(settings.speechReadOnlyString)
        return result

    #####################################################################
    #                                                                   #
    # Image information                                                 #
    #                                                                   #
    #####################################################################

    def _getImageDescription(self, obj, **args ):
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

    def _getImage(self, obj, **args):
        result = []
        try:
            image = obj.queryImage()
        except:
            pass
        else:
            role = pyatspi.ROLE_IMAGE
            result.extend(self.getSpeech(obj, role=role))
        return result

    #####################################################################
    #                                                                   #
    # Table interface information                                       #
    #                                                                   #
    #####################################################################

    def _getRowHeader(self, obj, **args):
        result = []
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
                    if settings.speechVerbosityLevel \
                            == settings.VERBOSITY_LEVEL_VERBOSE:
                        text += " " \
                            + rolenames.rolenames[\
                            pyatspi.ROLE_ROW_HEADER].speech
                    result.append(text)
        return result

    def _getNewRowHeader(self, obj, **args):
        """Returns the row header for the object only if the
        row header changed from the prior object."""
        result = []
        if obj:
            priorObj = args.get('priorObj', None)
            try:
                priorParent = priorObj.parent
            except:
                priorParent = None

            if (obj.getRole() == pyatspi.ROLE_TABLE_CELL) \
                or (obj.parent.getRole() == pyatspi.ROLE_TABLE):
                try:
                    table = priorParent.queryTable()
                except:
                    table = None
                if table \
                   and ((priorObj.getRole() == pyatspi.ROLE_TABLE_CELL) \
                         or (priorObj.getRole() == pyatspi.ROLE_TABLE)):
                    index = self._script.getCellIndex(priorObj)
                    oldRow = table.getRowAtIndex(index)
                else:
                    oldRow = -1

                try:
                    table = obj.parent.queryTable()
                except:
                    pass
                else:
                    index = self._script.getCellIndex(obj)
                    newRow = table.getRowAtIndex(index)
                    if (newRow >= 0) \
                       and (index != newRow) \
                       and ((newRow != oldRow) \
                            or (obj.parent != priorParent)):
                        result = self._getRowHeader(obj, **args)
        return result

    def _getColumnHeader(self, obj, **args):
        result = []
        try:
            table = obj.parent.queryTable()
        except:
            pass
        else:
            index = self._script.getCellIndex(obj)
            columnIndex = table.getColumnAtIndex(index)
            # Don't speak Thunderbird column headers, since
            # it's not possible to navigate across a row.
            # [[[TODO: WDW - move the T-bird check to the T-bird generator.]]]
            if (columnIndex >= 0) \
               and not self._script.getTopLevelName(obj).endswith(
                " - Thunderbird"):
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
                desc = table.getColumnDescription(columnIndex)
                if not desc:
                    header = table.getColumnHeader(columnIndex)
                    if header:
                        desc = self._script.getDisplayedText(header)
                if desc and len(desc):
                    text = desc
                    if settings.speechVerbosityLevel \
                            == settings.VERBOSITY_LEVEL_VERBOSE:
                        text += " " \
                            + rolenames.rolenames[\
                            pyatspi.ROLE_COLUMN_HEADER].speech
                    result.append(text)
        return result

    def _getNewColumnHeader(self, obj, **args):
        """Returns the column header for the object only if the
        column header changed from the prior object."""
        result = []
        if obj:
            priorObj = args.get('priorObj', None)
            try:
                priorParent = priorObj.parent
            except:
                priorParent = None

            if (obj.getRole() == pyatspi.ROLE_TABLE_CELL) \
                or (obj.parent.getRole() == pyatspi.ROLE_TABLE):
                try:
                    table = priorParent.queryTable()
                except:
                    table = None
                if table \
                   and ((priorObj.getRole() == pyatspi.ROLE_TABLE_CELL) \
                         or (priorObj.getRole() == pyatspi.ROLE_TABLE)):
                    index = self._script.getCellIndex(priorObj)
                    oldCol = table.getColumnAtIndex(index)
                else:
                    oldCol = -1

                try:
                    table = obj.parent.queryTable()
                except:
                    pass
                else:
                    index = self._script.getCellIndex(obj)
                    newCol = table.getColumnAtIndex(index)
                    if (newCol >= 0) \
                       and (index != newCol) \
                       and ((newCol != oldCol) \
                            or (obj.parent != priorParent)):
                        result = self._getColumnHeader(obj, **args)
        return result

    def _getTableCell2ChildLabel(self, obj, **args):
        """Get the speech utterances for the label of a toggle in a table cell
        that has a special 2 child pattern that we run into."""
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
                        result.extend(self.getSpeech(obj[i], **args))
        return result

    def _getTableCell2ChildToggle(self, obj, **args):
        """Get the speech utterances for the toggle value in a table cell that
        has a special 2 child pattern that we run into."""
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
                        result.extend(self.getSpeech(obj[i], **args))
        return result

    def _getRealTableCell(self, obj, **args):
        result = []
        oldRole = self._overrideRole('REAL_ROLE_TABLE_CELL', args)
        result.extend(self.getSpeech(obj, **args))
        self._restoreRole(oldRole, args)
        if not result and settings.speakBlankLines:
            # Translators: "blank" is a short word to mean the
            # user has navigated to an empty line.
            #
            result = [_("blank")]
        return result

    def _getTableCellRow(self, obj, **args):
        """Get the speech for a table cell row or a single table cell
        if settings.readTableCellRow is False."""
        result = []

        try:
            parentTable = obj.parent.queryTable()
        except NotImplementedError:
            parentTable = None
        if settings.readTableCellRow and parentTable \
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
            speakAll = True
            if "lastRow" in self._script.pointOfReference \
               and "lastColumn" in self._script.pointOfReference:
                pointOfReference = self._script.pointOfReference
                speakAll = \
                    (pointOfReference["lastRow"] != row) \
                     or ((row == 0 or row == parentTable.nRows-1) \
                     and pointOfReference["lastColumn"] == column)
            if speakAll:
                for i in range(0, parentTable.nColumns):
                    cell = parentTable.getAccessibleAt(row, i)
                    if not cell:
                        continue
                    state = cell.getState()
                    showing = state.contains(pyatspi.STATE_SHOWING)
                    if showing:
                        # If this table cell has a "toggle" action, and
                        # doesn't have any label associated with it then
                        # also speak the table column header.
                        # See Orca bug #455230 for more details.
                        #
                        label = self._script.getDisplayedText(
                            self._script.getRealActiveDescendant(cell))
                        try:
                            action = cell.queryAction()
                        except NotImplementedError:
                            action = None
                        if action and (label == None or len(label) == 0):
                            for j in range(0, action.nActions):
                                # Translators: this is the action name for
                                # the 'toggle' action. It must be the same
                                # string used in the *.po file for gail.
                                #
                                if action.getName(j) in ["toggle",
                                                         _("toggle")]:
                                    accHeader = \
                                        parentTable.getColumnHeader(i)
                                    result.append(accHeader.name)
                        result.extend(self._getRealTableCell(cell, **args))
            else:
                result.extend(self._getRealTableCell(obj, **args))
        else:
            result.extend(self._getRealTableCell(obj, **args))
        return result

    def _getUnselectedCell(self, obj, **args):
        result = []

        # If this is an icon within an layered pane or a table cell
        # within a table or a tree table and the item is focused but not
        # selected, let the user know. See bug #486908 for more details.
        #
        checkIfSelected = False
        objRole, parentRole, state = None, None, None
        if obj:
            objRole = obj.getRole()
            state = obj.getState()
            if obj.parent:
                parentRole = obj.parent.getRole()

        if objRole == pyatspi.ROLE_TABLE_CELL \
           and (parentRole == pyatspi.ROLE_TREE_TABLE \
                or parentRole == pyatspi.ROLE_TABLE):
            checkIfSelected = True

        # If we met the last set of conditions, but we got here by
        # moving left or right on the same row, then don't announce the
        # selection state to the user. See bug #523235 for more details.
        #
        if checkIfSelected and orca_state.lastNonModifierKeyEvent \
           and orca_state.lastNonModifierKeyEvent.event_string \
               in ["Left", "Right"]:
            checkIfSelected = False

        if objRole == pyatspi.ROLE_ICON \
           and parentRole == pyatspi.ROLE_LAYERED_PANE:
            checkIfSelected = True

        if checkIfSelected \
           and state and not state.contains(pyatspi.STATE_SELECTED):
            # Translators: this is in reference to a table cell being
            # selected or not.
            #
            result.append(C_("tablecell", "not selected"))

        return result

    #####################################################################
    #                                                                   #
    # Terminal information                                              #
    #                                                                   #
    #####################################################################

    def _getTerminal(self, obj, **args):
        result = []
        title = None
        frame = self._script.getFrame(obj)
        if frame:
            title = frame.name
        if not title:
            title = self._script.getDisplayedLabel(obj)
        result.append(title)
        return result

    #####################################################################
    #                                                                   #
    # Text interface information                                        #
    #                                                                   #
    #####################################################################

    def _getCurrentLineText(self, obj, **args ):
        [text, caretOffset, startOffset] = self._script.getTextLineAtCaret(obj)
        return [text]

    def _getDisplayedText(self, obj, **args ):
        """Returns the text being displayed for an object or the object's
        name if no text is being displayed."""
        return [self._script.getDisplayedText(obj)]

    def _getAllTextSelection(self, obj, **args):
        """Check if this object has text associated with it and it's
        completely selected."""
        result = []
        try:
            textObj = obj.queryText()
        except:
            pass
        else:
            noOfSelections = textObj.getNSelections()
            if noOfSelections == 1:
                [string, startOffset, endOffset] = \
                   textObj.getTextAtOffset(0, pyatspi.TEXT_BOUNDARY_LINE_START)
                if startOffset == 0 and endOffset == len(string):
                    # Translators: when the user selects (highlights) text in
                    # a document, Orca lets them know this.
                    #
                    result = [C_("text", "selected")]
        return result

    #####################################################################
    #                                                                   #
    # Tree interface information                                        #
    #                                                                   #
    #####################################################################

    def _getNodeLevel(self, obj, **args):
        result = []
        level = self._script.getNodeLevel(obj)
        if level >= 0:
            # Translators: this represents the depth of a node in a tree
            # view (i.e., how many ancestors a node has).
            #
            result.append(_("tree level %d") % (level + 1))
        return result

    def _getNewNodeLevel(self, obj, **args):
        # [[[TODO: WDW - hate duplicating code from _getNodeLevel,
        # but don't want to call it because it will make the same
        # self._script.getNodeLevel call again.]]]
        #
        result = []
        oldLevel = self._script.getNodeLevel(args.get('priorObj', None))
        newLevel = self._script.getNodeLevel(obj)
        if (oldLevel != newLevel) and (newLevel >= 0):
            # Translators: this represents the depth of a node in a tree
            # view (i.e., how many ancestors a node has).
            #
            result.append(_("tree level %d") % (newLevel + 1))
        return result

    #####################################################################
    #                                                                   #
    # Value interface information                                       #
    #                                                                   #
    #####################################################################

    def _getValue(self, obj, **args):
        return [self._script.getTextForValue(obj)]

    def _getPercentage(self, obj, **args ):
        result = []
        try:
            value = obj.queryValue()
        except NotImplementedError:
            pass
        else:
            percentValue = \
                (value.currentValue
                 / (value.maximumValue - value.minimumValue)) \
                * 100.0
            # Translators: this is the percentage value of a progress bar.
            #
            percentage = _("%d percent.") % percentValue + " "
            result.append(percentage)
        return result

    #####################################################################
    #                                                                   #
    # Hierarchy and related dialog information                          #
    #                                                                   #
    #####################################################################

    def _getRadioButtonGroup(self, obj, **args):
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
        return result

    def _getNewRadioButtonGroup(self, obj, **args):
        # [[[TODO: WDW - hate duplicating code from _getRadioButtonGroup
        # but don't want to call it because it will make the same
        # AT-SPI method calls.]]]
        #
        result = []
        priorObj = args.get('priorObj', None)
        if obj and obj.getRole() == pyatspi.ROLE_RADIO_BUTTON:
            radioGroupLabel = None
            inSameGroup = False
            relations = obj.getRelationSet()
            for relation in relations:
                if (not radioGroupLabel) \
                    and (relation.getRelationType() \
                         == pyatspi.RELATION_LABELLED_BY):
                    radioGroupLabel = relation.getTarget(0)
                if (not inSameGroup) \
                    and (relation.getRelationType() \
                         == pyatspi.RELATION_MEMBER_OF):
                    for i in range(0, relation.getNTargets()):
                        target = relation.getTarget(i)
                        if target == priorObj:
                            inSameGroup = True
                            break
            if (not inSameGroup) and radioGroupLabel:
                result.append(self._script.getDisplayedText(radioGroupLabel))
        return result

    def _getRealActiveDescendantDisplayedText(self, obj, **args ):
        result = []
        text = self._script.getDisplayedText(
          self._script.getRealActiveDescendant(obj))
        if text:
            result = [text]
        return result

    def _getNumberOfChildren(self, obj, **args):
        result = []
        childNodes = self._script.getChildNodes(obj)
        children = len(childNodes)
        if children:
            # Translators: this is the number of items in a layered
            # pane or table.
            #
            itemString = ngettext("%d item", "%d items", children) % children
            result.append(itemString)
        return result

    def _getNoShowingChildren(self, obj, **args):
        result = []
        hasItems = False
        for child in obj:
            state = child.getState()
            if state.contains(pyatspi.STATE_SHOWING):
                hasItems = True
                break
        if not hasItems:
            # Translators: this is the number of items in a layered pane
            # or table.
            #
            result.append(_("0 items"))
        return result

    def _getNoChildren(self, obj, **args ):
        result = []
        if not obj.childCount:
            # Translators: this is the number of items in a layered pane
            # or table.
            #
            result.append(_("0 items"))
        return result

    def _getUnfocusedDialogCount(self, obj,  **args):
        result = []
        # If this application has more than one unfocused alert or
        # dialog window, then speak '<m> unfocused dialogs'
        # to let the user know.
        #
        alertAndDialogCount = \
            self._script.getUnfocusedAlertAndDialogCount(obj)
        if alertAndDialogCount > 0:
            # Translators: this tells the user how many unfocused
            # alert and dialog windows that this application has.
            #
            result.append(ngettext("%d unfocused dialog",
                            "%d unfocused dialogs",
                            alertAndDialogCount) % alertAndDialogCount)
        return result

    def _getAncestors(self, obj, **args):
        result = []
        priorObj = args.get('priorObj', None)
        commonAncestor = self._script.findCommonAncestor(priorObj, obj)
        if obj != commonAncestor:
            parent = obj.parent
            if parent \
                and (obj.getRole() == pyatspi.ROLE_TABLE_CELL) \
                and (parent.getRole() == pyatspi.ROLE_TABLE_CELL):
                parent = parent.parent
            while parent and (parent.parent != parent):
                if parent == commonAncestor:
                    break
                if not self._script.isLayoutOnly(parent):
                    text = self._script.getDisplayedLabel(parent)
                    if not text and 'Text' in pyatspi.listInterfaces(parent):
                        text = self._script.getDisplayedText(parent)
                    if text and len(text.strip()):
                        # Push announcement of cell to the end
                        #
                        if parent.getRole() not in [pyatspi.ROLE_TABLE_CELL,
                                                    pyatspi.ROLE_FILLER]:
                            result.extend(self._getRoleName(parent))
                        result.append(text)
                        if parent.getRole() == pyatspi.ROLE_TABLE_CELL:
                            result.extend(self._getRoleName(parent))
                parent = parent.parent
        return result.reverse() or result

    def _getNewAncestors(self, obj, **args):
        result = []
        if args.get('priorObj', None):
            result = self._getAncestors(obj, **args)
        return result

    #####################################################################
    #                                                                   #
    # Keyboard shortcut information                                     #
    #                                                                   #
    #####################################################################

    def _getAccelerator(self, obj, **args):
        result = []
        [mnemonic, shortcut, accelerator] = self._script.getKeyBinding(obj)
        if accelerator:
            # Add punctuation for better prosody.
            #
            #if result:
            #    result[-1] += "."
            result.append(accelerator)
        return result

    def _getMnemonic(self, obj, **args):
        result = []
        [mnemonic, shortcut, accelerator] = self._script.getKeyBinding(obj)
        if mnemonic:
            mnemonic = mnemonic[-1] # we just want a single character
        if not mnemonic and shortcut:
            mnemonic = shortcut
        if mnemonic:
            # Add punctuation for better prosody.
            #
            #if result:
            #    utterances[-1] += "."
            result = [mnemonic]
        return result


    #####################################################################
    #                                                                   #
    # Tutorial information                                              #
    #                                                                   #
    #####################################################################

    def _getTutorial(self, obj, **args):
        already_focused = args.get('already_focused', False)
        forceMessage = args.get('forceMessage', False)
        return self._script.tutorialGenerator.getTutorial(
            obj,
            already_focused,
            forceMessage)

    #####################################################################
    #                                                                   #
    # Tie it all together                                               #
    #                                                                   #
    #####################################################################

    def voice(self, key=None):
        try:
            voice = settings.voices[key]
        except:
            voice = settings.voices[settings.DEFAULT_VOICE]
        return [voice]

    def getSpeech(self, obj, **args):
        result = []
        methods = {}
        methods['voice'] = self.voice
        methods['obj'] = obj
        methods['pyatspi'] = pyatspi
        methods['role'] = args.get('role', obj.getRole())

        try:
            # We sometimes want to override the role.  We'll keep the
            # role in the args dictionary as a means to let us do so.
            #
            args['role'] = methods['role']

            # We loop through the format string, catching each error
            # as we go.  Each error should always be a NameError,
            # where the name is the name of one of our generator
            # functions.  When we encounter this, we call the function
            # and get its results, placing them in the globals for the
            # the call to eval.
            #
            format = self._script.formatting.getFormat('speech',
                                                       **args)

            # Add in the speech context if this is the first time
            # we've been called.
            #
            if not args.get('recursing', False):
                prefix = self._script.formatting.getPrefix('speech',
                                                           **args)
                suffix = self._script.formatting.getSuffix('speech',
                                                           **args)
                format = '%s + %s + %s' % (prefix, format, suffix)
                args['recursing'] = True
                firstTimeCalled = True
                debug.println(debug.LEVEL_ALL, "getSpeech using '%s'" % format)
            else:
                firstTimeCalled = False

            assert(format)
            while True:
                try:
                    result = eval(format, methods)
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
                    methods[arg] = self._methodsDict[arg](obj, **args)
        except:
            debug.printException(debug.LEVEL_SEVERE)
            result = []

        if firstTimeCalled:
            debug.println(debug.LEVEL_ALL,
                          "getSpeech generated '%s'" % repr(result))
        return result
