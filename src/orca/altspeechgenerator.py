# Orca
#
# Copyright 2005-2008 Sun Microsystems Inc.
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
__copyright__ = "Copyright (c) 2005-2008 Sun Microsystems Inc."
__license__   = "LGPL"

import pdb
import sys
import re
#import time
import traceback

import pyatspi
#import debug
#import orca_state
import rolenames
import settings
#import focus_tracking_presenter_settings
import generator_settings

from orca_i18n import _         # for gettext support
from orca_i18n import ngettext  # for ngettext support
from orca_i18n import C_        # to provide qualified translatable strings
from IPython.Shell import IPShellEmbed
ipshell = IPShellEmbed() 

def formatExceptionInfo(maxTBlevel=5):
    cla, exc, trbk = sys.exc_info()
    excName = cla.__name__
    try:
        excArgs = exc.args
    except KeyError:
        excArgs = "<no args>"
    excTb = traceback.format_tb(trbk, maxTBlevel)
    #print "-*** exception ***-"
    #print excName
    #print excArgs
    #for i in excTb:
    #    print i
    #print "-*** ***-"
    return (excName, excArgs, excTb)

class AltSpeechGenerator:
    """Takes accessible objects and produces a string to speak for
    those objects.  See the getSpeech method, which is the primary
    entry point.  Subclasses can feel free to override/extend the
    speechGenerators instance field as they see fit."""

    def __init__(self, script):

        # The script that created us.  This allows us to ask the
        # script for information if we need it.
        #
        self._script = script

        self._argExp = re.compile('[ ]*\+?[ ]*([a-zA-Z0-9]+)[ ]*(.*)')

        self._myswitch = {
        'accelerator' : self._getAccelerator,
        'embedded': self._getEmbedded,
        'availability' : self._getAvailability,
        'checkState': self._getCheckState,
        'isCheckbox': self._isCheckbox,
        'checkRole': self._getCheckRole,
        'currentLineText': self._getCurrentLineText,
        'displayedText': self._getDisplayedText,
        'realActiveDescendantDisplayedText': \
          self._getRealActiveDescendantDisplayedText,
        'tableCell2ChildLabel': self._getTableCell2ChildLabel,
        'tableCell2ChildToggle': self._getTableCell2ChildToggle,
        'tableCellRow': self._getTableCellRow,
        'expandableState': self._getExpandableState,
        'hasNoChildren': self._getHasNoChildren,
        'imageDescription': self._getImageDescription,
        'isCheckedState': self._getIsCheckedState,
        'isReadOnly': self._getIsReadOnly,
        'label' : self._getLabel,
        'labelOrName': self._getLabelOrName,
        'labelOrName2': self._getLabelOrName2,
        'mnemonic' : self._getMnemonic,
        'name' : self._getName,
        'percentage': self._getPercentage,
        'radioState': self._getRadioState,
        'required' : self._getRequiredObject,
        'roleName' : self._getRoleName,
        'terminal': self._getTerminal,
        'textRole': self._getTextRole,
        'textSelection' : self._getAllTextSelection,
        'toggleState': self._getToggleState,
        'unrelatedLabels' : self._getUnrelatedLabels,
        'value': self._getValue,
        'hashNoShowingChildren': self._getHasNoShowingChildren,
        'noOfChildren': self._getNoOfChildren,
        'unfocusedDialogueCount': self._getUnfocusedDialogueCount,
        'image': self._getImage
        }

    def _getImage(self, obj, **args):
        result = []
        try:
            image = obj.queryImage()
        except:
            image = None
        else:
            print "args is:"
            print args
            #pdb.set_trace()
            #oldFmtstr = args.get('fmtstr', None)
            role = pyatspi.ROLE_IMAGE
            result.extend(self.getSpeech(obj, role=role))
            #args['fmtstr'] = oldFmtstr
        return result

    def _getNoOfChildren(self, obj, **args):
        result = []
        childNodes = self._script.getChildNodes(obj)
        children = len(childNodes)

        if not children:
            # Translators: this is the number of items in a layered
            # pane or table.
            #
            itemString = ngettext("%d item", "%d items", children) % children
            result.append(itemString)
        return result

    def _isCheckbox(self, obj, **args):
        # pylint: disable-msg=W0142
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
                    #pdb.set_trace()
                    #ipshell()

                    oldFmtstr = args.get('fmtstr', None)

                    args['fmtstr'] = self._getFmtstr( \
                      forceRole=pyatspi.ROLE_CHECK_BOX, **args) 
                    #print "args is:"
                    #print args
                    #pdb.set_trace()
                    result.extend( \
                      self.getSpeech(obj, **args))
                    args['fmtstr'] = oldFmtstr
                    break
        return result

    def _getTerminal(self, obj, **args):
        """Get the speech for a terminal

        Arguments:
        - obj: the terminal
        
        Returns a list of utterances to be spoken for the object.
        """
        result = []

        title = None
        frame = self._script.getFrame(obj)
        if frame:
            title = frame.name
        if not title:
            title = self._script.getDisplayedLabel(obj)

        result.append(title)
        return result
        
    def _getTextRole(self, obj, **args):
        """Get the speech for a text component.

        Arguments:
        - obj: the text component
        
        Returns a list of utterances to be spoken for the object.
        """
        result = []
        # pylint: disable-msg=W0142
        if obj.getRole() != pyatspi.ROLE_PARAGRAPH:
            result.extend(self._getRoleName(obj, **args))
        return result

    def _getCurrentLineText(self, obj, **args ):
        """Get the speech for a text component.

        Arguments:
        - obj: the text component

        Returns a list of utterances to be spoken for the object.
        """
        result = []

        [text, caretOffset, startOffset] = self._script.getTextLineAtCaret(obj)
        return [text]

    def _getIsReadOnly(self, obj, **args):
        """Get the speech for a text component.

        Arguments:
        - obj: the text component

        Returns a list of utterances to be spoken for the object.
        """
        result = []

        if settings.presentReadOnlyText \
           and self._script.isReadOnlyTextArea(obj):
            result.append(settings.speechReadOnlyString)
        return result

    def _getLabelOrName2(self, obj, **args ):
        """Get the speech for a text component.

        Arguments:
        - obj: the text component

        Returns a list of utterances to be spoken for the object.
        """

        result = []
        # pylint: disable-msg=W0142
        result.extend(self._getLabel(obj, **args))
        if len(result) == 0:
            if obj.name and (len(obj.name)):
                result.append(obj.name)
        return result

    def _getHasNoShowingChildren(self, obj, **args):
        """Get the speech for a layered pane

        Arguments:
        - obj: the table

        Returns a list of utterances to be spoken for the object.
        """
        result = []

        # If this has no children, then let the user know.
        #
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

    def _getImageDescription(self, obj, **args ):
        """Get the speech for an icon.

        Arguments:
        - obj: the icon

        Returns a list of utterances to be spoken for the object.
        """

        # [[[TODO: WDW - HACK to remove availability output because nautilus
        # doesn't include this information for desktop icons.  If, at some
        # point, it is determined that availability should be added back in,
        # then a custom script for nautilus needs to be written to remove the
        # availability.]]]
        #        
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

    def _getEmbedded(self, obj, **args):
        # pylint: disable-msg=W0142
        result = self._getLabelOrName(obj, **args)
        if not result:
            try:
                result.append(obj.getApplication().name)
            except:
                pass
        return result

    def _getDisplayedText(self, obj, **args ):
        return [self._script.getDisplayedText(obj)]

    def _getRealActiveDescendantDisplayedText(self, obj, **args ):
        text = self._script.getDisplayedText(\
          self._script.getRealActiveDescendant(obj))
        if text:
            return [text]
        else:
            return []

    def _getHasNoChildren(self, obj, **args ):
        result = []
        if not obj.childCount:
            # Translators: this is the number of items in a layered pane
            # or table.
            #
            result.append(_("0 items"))
        return result

    def _getPercentage(self, obj, **args ):
        value = obj.queryValue()
        percentValue = (value.currentValue / \
            (value.maximumValue - value.minimumValue)) * 100.0

        # Translators: this is the percentage value of a progress bar.
        #
        percentage = _("%d percent.") % percentValue + " "
        return [percentage]

    def _getIsCheckedState(self, obj, **args ):
        result = []
        state = obj.getState()
        if state.contains(pyatspi.STATE_CHECKED):
            # Translators: this represents the state of a checked menu item.
            #
            result.append(_("checked"))
        return result

    def _getUnfocusedDialogueCount(self, obj,  **args):
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

    def _getExpandableState(self, obj, **args):
        result = []
        # If already in focus then the tree probably collapsed or expanded
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
                result.append( _("collapsed"))
        return result

    def _getValue(self, obj, **args):
        return [self._script.getTextForValue(obj)]

    def _getAccelerator(self, obj, **args):
        """returns an utterance that describes the keyboard accelerator for the
        given object.

        Arguments:
        - obj: the Accessible object

        Returns a list of utterances to be spoken.
        """
        # replaces _addSpeechForObjectAccelerator

        result = []
        [mnemonic, shortcut, accelerator] = self._script.getKeyBinding(obj)
        if accelerator:
            # Add punctuation for better prosody.
            #
            #if utterances:
            #    utterances[-1] += "."
            result.append(accelerator)
        return result

    def _getRadioState(self, obj, **args):
        state = obj.getState()
        if state.contains(pyatspi.STATE_CHECKED):
            # Translators: this is in reference to a radio button being
            # selected or not.
            #
            selectionState = C_("radiobutton", "selected")
        else:
            # Translators: this is in reference to a radio button being
            # selected or not.
            #
            selectionState = C_("radiobutton", "not selected")
        return [selectionState]

    def _getCheckState(self, obj, **args):
        # replaces _getSpeechForCheckBox
        state = obj.getState()
        if state.contains(pyatspi.STATE_INDETERMINATE):
            # Translators: this represents the state of a checkbox.
            #
            checkedState = _("partially checked")
        elif state.contains(pyatspi.STATE_CHECKED):
            # Translators: this represents the state of a checkbox.
            #
            checkedState = _("checked")
        else:
            # Translators: this represents the state of a checkbox.
            #
            checkedState = _("not checked")
        return [checkedState]

    def _getToggleState(self, obj, **args):
        state = obj.getState()
        if state.contains(pyatspi.STATE_CHECKED) \
           or state.contains(pyatspi.STATE_PRESSED):
            # Translators: the state of a toggle button.
            #
            checkedState = _("pressed")
        else:
            # Translators: the state of a toggle button.
            #
            checkedState = _("not pressed")
        return [checkedState]

    def _getCheckRole(self, obj, **args):
        # replaces _getSpeechForCheckBox
        # pylint: disable-msg=W0142
        if obj.getRole() == pyatspi.ROLE_TABLE_CELL:
            result = \
              self._getRoleName(obj, forceRole=pyatspi.ROLE_CHECK_BOX, **args)
        else:
            result = self._getRoleName(obj, **args)
        return result

    def _getMnemonic(self, obj, **args):
        """returns an utterance that describes the mnemonic for the given object

        Arguments:
        - obj: the Accessible object
        """
        # replaces _addSpeechForObjectMnemonic

        result = []
        #if obj != orca_state.locusOfFocus:
        #    return []
        [mnemonic, shortcut, accelerator] = self._script.getKeyBinding(obj)
        if mnemonic:
            mnemonic = mnemonic[-1] # we just want a single character
        if not mnemonic and shortcut:
            mnemonic = shortcut
        if mnemonic:
            # Add punctuation for better prosody.
            #
            #if utterances:
            #    utterances[-1] += "."
            result = [mnemonic]
        return result

    def _getAvailability(self, obj, **args):
        """Returns a list of utterances that describes the availability
        of the given object.

        Arguments:
        - obj: the Accessible object

        Returns a list of utterances to be spoken.
        """
        # replaces _getSpeechForObjectAvailability

        state = obj.getState()
        if not state.contains(pyatspi.STATE_SENSITIVE):
            # Translators: this represents an item on the screen that has
            # been set insensitive (or grayed out).
            #
            return [_("grayed")]
        else:
            return []

    def _getLabelOrName(self, obj, **args):
        # pylint: disable-msg=W0142
        result = []
        label = self._getLabel(obj, **args)
        name = self._getName(obj, **args)
        result.extend(label)
        if not len(label):
            result.extend(name)
        elif len(name) and name[0] != label[0]:
            result.extend(name)
        return result

    def _getLabel(self, obj, **args):
        # replaces _getSpeechForObjectLabel

        result = []
        label = self._script.getDisplayedLabel(obj)
        if label:
            result =  [label]
        return result

    def _getUnrelatedLabels(self, obj, **args):
        # _getSpeechForAlert
        labels = self._script.findUnrelatedLabels(obj)
        result = []
        for label in labels:
            name = self._getName(label, False)
            result.extend(name)
        return result

    def _getName(self, obj, **args):
        # replaces _getSpeechForObjectName
        name = self._script.getDisplayedText(obj)
        if name:
            return [name]
        elif obj.description:
            return [obj.description]
        else:
            return []

    def _getRoleName(self, obj, forceRole=None, **args):
        # replaces getSpeechForObjectRole
        role =  args.get('role', None)

        if forceRole:
            role = forceRole

        if (obj.getRole() != pyatspi.ROLE_UNKNOWN):
            result = [rolenames.getSpeechForRoleName(obj, role)]
            return  result
        else:
            return []

    def _getRequiredObject(self, obj, **args):
        """Returns the list of utterances that describe the required state
        of the given object.

        Arguments:
        - obj: the Accessible object

        Returns a list of utterances to be spoken.
        """
        # replaces _getSpeechForRequiredObject
        state = obj.getState()
        if state.contains(pyatspi.STATE_REQUIRED):
            return [settings.speechRequiredStateString]
        else:
            return []

    def _getAllTextSelection(self, obj, **args):
        """Check if this object has text associated with it and it's 
        completely selected.

        Arguments:
        - obj: the object being presented
        """
        # replaces _getSpeechForAllTextSelection

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


    def _getFmtstr(self, forceRole=None, **args):
        already_focused = args.get('already_focused', False)
        role = args.get('role', None)

        if forceRole:
            role = forceRole

        fmtstr = ''
        # Finding the formatting string to be used.
        #
        # Checking if we have the role defined.
        #
        if generator_settings.formattingDict.has_key(role):
            roleDict =     generator_settings.formattingDict[role]
        else:
            roleDict =     generator_settings.formattingDict['default']

        if already_focused and 'focusedSpeech' in roleDict:
            fmtstr = roleDict['focusedSpeech']
        else:
            fmtstr = roleDict['unfocusedSpeech']
        return fmtstr


    def _getTableCell2ChildLabel(self, obj, **args):
        """Get the speech utterances for a single table cell

        Arguments:
        - obj: the table
        
        Returns a list of utterances to be spoken for the object.
        """

        # pylint: disable-msg=W0142
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
            hasToggle = [ False, False ]
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
                args['fmtstr'] = self._getFmtstr( \
                  forceRole=pyatspi.ROLE_TABLE_CELL, **args)
                for i in cellOrder:
                    if not hasToggle[i]:
                        result.extend( \
                            self.getSpeech(obj[i],
                                                        **args))
        return result

    def _getTableCell2ChildToggle(self, obj, **args):
        """Get the speech utterances for a single table cell

        Arguments:
        - obj: the table

        Returns a list of utterances to be spoken for the object.
        """

        # pylint: disable-msg=W0142
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
            hasToggle = [ False, False ]
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
                args['role'] = pyatspi.ROLE_CHECK_BOX 
                for i in cellOrder:
                    if hasToggle[i]:
                        result.extend( \
                            self.getSpeech(obj[i],
                                                        **args))
        return result

    def _getTableCellRow(self, obj, **args):
        """Get the speech for a table cell row or a single table cell
        if settings.readTableCellRow is False.

        Arguments:
        - obj: the table
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        # pylint: disable-msg=W0142
        utterances = []
        #pdb.set_trace()

        try:
            parent_table = obj.parent.queryTable()
        except NotImplementedError:
            parent_table = None
        if settings.readTableCellRow and parent_table \
            and (not self._script.isLayoutOnly(obj.parent)):
            parent = obj.parent
            index = self._script.getCellIndex(obj)
            row = parent_table.getRowAtIndex(index)
            column = parent_table.getColumnAtIndex(index)

            # This is an indication of whether we should speak all the
            # table cells (the user has moved focus up or down a row),
            # or just the current one (focus has moved left or right in
            # the same row).
            #
            speakAll = True
            if "lastRow" in self._script.pointOfReference and \
                "lastColumn" in self._script.pointOfReference:
                pointOfReference = self._script.pointOfReference
                speakAll = (pointOfReference["lastRow"] != row) or \
                    ((row == 0 or row == parent_table.nRows-1) and \
                       pointOfReference["lastColumn"] == column)

            if speakAll:
                print("this table has %s columns" %parent_table.nColumns)
                for i in range(0, parent_table.nColumns):
                    #print("trying to deal with child %s" %i)
                    cell = parent_table.getAccessibleAt(row, i)
                    if not cell:
                        #debug.println(debug.LEVEL_WARNING,
                        #     "ERROR: speechgenerator." \
                        #     + "_getSpeechForTableCellRow" \
                        #     + " no accessible at (%d, %d)" % (row, i))
                        continue
                    state = cell.getState()
                    showing = state.contains(pyatspi.STATE_SHOWING)
                    if showing:
                        # If this table cell has a "toggle" action, and
                        # doesn't have any label associated with it then 
                        # also speak the table column header.
                        # See Orca bug #455230 for more details.
                        #
                        label = self._script.getDisplayedText( \
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
                                if action.getName(j) in ["toggle", \
                                                         _("toggle")]:
                                    accHeader = \
                                        parent_table.getColumnHeader(i)
                                    utterances.append(accHeader.name)
                        fmtstr = self._getFmtstr( \
                          forceRole='REAL_ROLE_TABLE_CELL', **args)
                        utterances.extend( \
                          self.getSpeech(cell, fmtstr=fmtstr, **args))
                    #print ("finished with child")
            else:
                fmtstr = self._getFmtstr( \
                  forceRole='REAL_ROLE_TABLE_CELL', **args)
                utterances.extend( \
                  self.getSpeech(obj, fmtstr=fmtstr, **args))
        else:
            fmtstr = self._getFmtstr(forceRole='REAL_ROLE_TABLE_CELL', **args)
            utterances = self.getSpeech(obj, \
              fmtstr=fmtstr, **args)
        return utterances

    def getSpeech(self, obj, already_focused=False, **args):
        """ Test """
        # pylint: disable-msg=W0142
        res = {}
        #pdb.set_trace()
        try:
            role = args.get('role', obj.getRole())
            forceRole = args.get('forceRole', role)
            role = forceRole

            # Used for debugging a particular role.
            #
            if role in []: # pyatspi.ROLE_DIALOG as example
                pdb.set_trace()
            #pdb.set_trace()
            roleName = self._getRoleName(obj, forceRole=role, **args)
            # If someone has already given us the format string to be used
            # then we dont need to look it up.
            fmtstr = args.get('fmtstr', '')

            #print "looking up fmtstr\n"
            #sys.stdout.flush()
            if not fmtstr:
                args['already_focused'] = already_focused
                fmtstr = self._getFmtstr(forceRole=role, **args)
            fmtstrKey = args.get('fmtstrKey', None)
            if fmtstrKey:
                fmtstr = self._getFmtstr(forceRole=fmtstrKey, **args)

            assert(fmtstr != '')
            evalstr = fmtstr
            utterances = []
            myswitch = self._myswitch
            #print("fmtstr = '%s'\n" %fmtstr)
            sys.stdout.flush()
            # Looping through the arguments of the formatting string.
            #
            e = []
            finished = None
            while not e and not finished:

                # Checking if we evaluate to tru
                # and therefore can escape from the loop
                # and return.
                #
                try:
                    e = eval(evalstr, res)
                    finished = True
                except NameError:
                    e = []
                    info = formatExceptionInfo()
                    #print "--here is the info:\n"
                    #print info[1]
                    #print "\n---end of info"
                    #pdb.set_trace()
                    arg = info[1][0]
                    arg = arg.replace("name '", "")
                    arg = arg.replace("' is not defined", "")

                    if not myswitch.has_key(arg):
                        print("unable to find function for '%s'\n" %arg)
                        sys.stdout.flush()
                        break
            
                    #print("calling func for %s" %arg)
                    sys.stdout.flush()
                    res[arg] = myswitch[arg](obj, **args)
                    #print("returns '%s'" %res[arg])
                    sys.stdout.flush()


        except:
            print formatExceptionInfo()

        result = e
        return result
