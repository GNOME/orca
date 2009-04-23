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

#import pdb
import sys
import re
#import time
import pyatspi
#import debug
#import orca_state
import rolenames
import settings
import generator_settings

from orca_i18n import _         # for gettext support
from orca_i18n import ngettext  # for ngettext support
from orca_i18n import C_        # to provide qualified translatable strings

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
        'checkRole': self._getCheckRole,
        'currentLineText': self._getCurrentLineText,
        'displayedText': self._getDisplayedText,
        'expandableState': self._getExpandableState,
        'hasNoChildren': self._getHasNoChildren,
        'iconRole': self._getIconRole,
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
        'unfocusedDialogueCount': self._getUnfocusedDialogueCount
        }

    def _getTerminal(self, obj, already_focused):
        """Get the speech for a terminal

        Arguments:
        - obj: the terminal
        - already_focused: False if object just received focus

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
        
    def _getTextRole(self, obj, already_focused):
        """Get the speech for a text component.

        Arguments:
        - obj: the text component
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """
        result = []
        if obj.getRole() != pyatspi.ROLE_PARAGRAPH:
            result.extend(self._getRoleName(obj, already_focused))
        return result

    def _getCurrentLineText(self, obj, already_focused):
        """Get the speech for a text component.

        Arguments:
        - obj: the text component
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """
        result = []

        [text, caretOffset, startOffset] = self._script.getTextLineAtCaret(obj)
        return [text]

    def _getIsReadOnly(self, obj, already_focused):
        """Get the speech for a text component.

        Arguments:
        - obj: the text component
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """
        result = []

        if settings.presentReadOnlyText \
           and self._script.isReadOnlyTextArea(obj):
            result.append(settings.speechReadOnlyString)
        return result

    def _getLabelOrName2(self, obj, already_focused):
        """Get the speech for a text component.

        Arguments:
        - obj: the text component
        - already_focused: False if object just received focus

        Returns a list of utterances to be spoken for the object.
        """

        result = []
        result.extend(self._getLabel(obj, already_focused))
        if len(result) == 0:
            if obj.name and (len(obj.name)):
                result.append(obj.name)
        return result

    def _getHasNoShowingChildren(self, obj, already_focused):
        """Get the speech for a layered pane

        Arguments:
        - obj: the table
        - already_focused: False if object just received focus

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

    def _getIconRole(self, obj, already_focused):
        return [].append(rolenames.getSpeechForRoleName(
                obj, pyatspi.ROLE_ICON))

    def _getImageDescription(self, obj, already_focused):
        """Get the speech for an icon.

        Arguments:
        - obj: the icon
        - already_focused: False if object just received focus

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

    def _getEmbedded(self, obj, already_focused):
        result = self._getLabelOrName(obj, already_focused)
        if not result:
            try:
                result.append(obj.getApplication().name)
            except:
                pass
        return result

    def _getDisplayedText(self, obj, already_focused):
        return [self._script.getDisplayedText(obj)]

    def _getHasNoChildren(self, obj, already_focused):
        result = ''
        if not obj.childCount:
            # Translators: this is the number of items in a layered pane
            # or table.
            #
            result = _("0 items")
        return [result]

    def _getPercentage(self, obj, already_focused):
        value = obj.queryValue()
        percentValue = (value.currentValue / \
            (value.maximumValue - value.minimumValue)) * 100.0

        # Translators: this is the percentage value of a progress bar.
        #
        percentage = _("%d percent.") % percentValue + " "
        return [percentage]

    def _getIsCheckedState(self, obj, already_focused):
        result = []
        state = obj.getState()
        if state.contains(pyatspi.STATE_CHECKED):
            # Translators: this represents the state of a checked menu item.
            #
            result.append(_("checked"))
        return result

    def _getUnfocusedDialogueCount(self, obj, already_focused):
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
            result.extend(ngettext("%d unfocused dialog",
                            "%d unfocused dialogs",
                            alertAndDialogCount) % alertAndDialogCount)
        return result

    def _getExpandableState(self, obj, already_focused):
	# If already in focus then the tree probably collapsed or expanded
        state = obj.getState()
        if state.contains(pyatspi.STATE_EXPANDABLE):
            if state.contains(pyatspi.STATE_EXPANDED):
                # Translators: this represents the state of a node in a tree.
                # 'expanded' means the children are showing.
                # 'collapsed' means the children are not showing.
                #
                result = _("expanded")
            else:
                # Translators: this represents the state of a node in a tree.
                # 'expanded' means the children are showing.
                # 'collapsed' means the children are not showing.
                #
                result = _("collapsed")
        return [result]

    def _getValue(self, obj, already_focused):
        return [self._script.getTextForValue(obj)]

    def _getAccelerator(self, obj, already_focused):
        """Adds an utterance that describes the keyboard accelerator for the
        given object to the list of utterances passed in.

        Arguments:
        - obj: the Accessible object
        - utterances: the list of utterances to add to.

        Returns a list of utterances to be spoken.
        """

        result = []
        [mnemonic, shortcut, accelerator] = self._script.getKeyBinding(obj)
        if accelerator:
            # Add punctuation for better prosody.
            #
            #if utterances:
            #    utterances[-1] += "."
            result.append(accelerator)
        return result

    def _getRadioState(self, obj, already_focused):
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

    def _getCheckState(self, obj, already_focused):
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

    def _getToggleState(self, obj, already_focused):
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

    def _getCheckRole(self, obj, already_focused):
        if obj.getRole() == pyatspi.ROLE_TABLE_CELL:
            result = \
              self._getRoleName(obj, already_focused, pyatspi.ROLE_CHECK_BOX)
        else:
            result = self._getRoleName(obj, already_focused)
        return result

    def _getMnemonic(self, obj, already_focused):
        """returns an utterance that describes the mnemonic for the given object

        Arguments:
        - obj: the Accessible object
        """

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

    def _getAvailability(self, obj, already_focused):
        """Returns a list of utterances that describes the availability
        of the given object.

        Arguments:
        - obj: the Accessible object

        Returns a list of utterances to be spoken.
        """
        state = obj.getState()
        if not state.contains(pyatspi.STATE_SENSITIVE):
            # Translators: this represents an item on the screen that has
            # been set insensitive (or grayed out).
            #
            return [_("grayed")]
        else:
            return []

    def _getLabelOrName(self, obj, already_focused):
        result = []
        label = self._getLabel(obj, already_focused)
        name = self._getName(obj, already_focused)
        result.extend(label)
        if not len(label):
            result.extend(name)
        elif len(name) and name[0] != label[0]:
            result.extend(name)
        return result

    def _getLabel(self, obj, already_focused):
        result = []
        label = self._script.getDisplayedLabel(obj)
        if label:
            result =  [label]
        return result

    def _getUnrelatedLabels(self, obj, already_focused):
        labels = self._script.findUnrelatedLabels(obj)
        utterances = []
        for label in labels:
            name = self._getName(label, False)
            utterances.extend(name)
        return utterances

    def _getName(self, obj, already_focused):
        name = self._script.getDisplayedText(obj)
        if name:
            return [name]
        elif obj.description:
            return [obj.description]
        else:
            return []

    def _getRoleName(self, obj, already_focused, role=None):
        if (obj.getRole() != pyatspi.ROLE_UNKNOWN):
            result = [rolenames.getSpeechForRoleName(obj, role)]
            return  result
        else:
            return []

    def _getRequiredObject(self, obj, already_focused):
        """Returns the list of utterances that describe the required state
        of the given object.

        Arguments:
        - obj: the Accessible object

        Returns a list of utterances to be spoken.
        """

        state = obj.getState()
        if state.contains(pyatspi.STATE_REQUIRED):
            return [settings.speechRequiredStateString]
        else:
            return []

    def _getAllTextSelection(self, obj, already_focused):
        """Check if this object has text associated with it and it's 
        completely selected.

        Arguments:
        - obj: the object being presented
        """

        utterance = []
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
                    utterance = [C_("text", "selected")]

        return utterance

   
    def getSpeech(self, obj, already_focused):
        """ Test """
        res = {}
        role = obj.getRole()
        roleName = self._getRoleName(obj, role)

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
        assert(fmtstr != '')
        evalstr = fmtstr
        utterances = []
        myswitch = self._myswitch
        #print("fmtstr = '%s'\n" %fmtstr)
        sys.stdout.flush()
        # Looping through the arguments of the formatting string.
        #
        #pdb.set_trace()
        e = []
        while (not e or fmtstr != ''):
            arg = self._argExp.sub('\\1' , fmtstr)
            fmtstr = self._argExp.sub('\\2' , fmtstr)
            if not myswitch.has_key(arg):
                print("unable to find function for '%s'\n" %arg)
                sys.stdout.flush()
                break

            # We have already evaluated this label.
            #
            if res.has_key(arg):
                continue
            
            #print("calling func for %s" %arg)
            #sys.stdout.flush()
            res[arg] = myswitch[arg](obj, already_focused)
            #print("returns '%s'" %res[arg])
            #sys.stdout.flush()

            # Checking if we evaluate to tru
            # and therefore can escape from the loop
            # and return.
            #
            try:
                e = eval(evalstr, res)
            except NameError:
                pass
        result = [" ".join(e)]
        print("s%d='%s'\n" %(len(result[0]), result))
        sys.stdout.flush()
        return result
