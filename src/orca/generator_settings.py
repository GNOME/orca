# Orca
#
# Copyright 2004-2008 Sun Microsystems Inc.
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

"""Manages the formatting settings for Orca."""

__id__        = "$Id:$"
__version__   = "$Revision:$"
__date__      = "$Date:$"
__copyright__ = "Copyright (c) 2004-2008 Sun Microsystems Inc."
__license__   = "LGPL"

# importing so that we can use the role constants.
#
import pyatspi


formattingDict = {}

#### default role settings ####
__roleDict = {}

# the formatting string for the attributes to speak
# when the object has just received focus. (already_focused: False)
#
__roleDict['unfocusedSpeech'] = \
  'labelOrName + textSelection + roleName + availability'

# the formatting string for the attributes to speak
# when the object has already the focus. (already_focused: True)
#
#__roleDict['focusedSpeech'] = ''

# The acss to be used for speaking the text.
#
#__roleDict['acss'] = 

# The unfocused braille formatting string
#
#__roleDict['unfocusedBraille'] = '%labelOrName'

# The focused braille formatting string
# This is usually, but not necessarily the same as the above.
# if it is not defined, then we use the unfocused version.
#
#__roleDict['focusedBraille'] = '%labelOrName'

# braille attributes to send along for this role
#
#__roleDict['brailleAttributes'] = None
formattingDict['default'] = __roleDict


#### pyatspi.ROLE_PUSH_BUTTON ####
__roleDict = {}

__roleDict['unfocusedSpeech'] = 'labelOrName + roleName'
formattingDict[pyatspi.ROLE_PUSH_BUTTON] = __roleDict

#### pyatspi.ROLE_ALERT ####
__roleDict = {}
__roleDict['unfocusedSpeech'] = 'labelOrName + unrelatedLabels'
formattingDict[pyatspi.ROLE_ALERT] = __roleDict


#### pyatspi.ROLE_CHECK_BOX ####
__roleDict = {}
__roleDict['unfocusedSpeech'] = \
  'labelOrName + checkRole + checkState + required + availability'
__roleDict['focusedSpeech'] = 'checkState'
formattingDict[pyatspi.ROLE_CHECK_BOX] = __roleDict

#### pyatspi.ROLE_RADIO_BUTTON ####
__roleDict = {}
__roleDict['unfocusedSpeech'] = \
  'labelOrName + radioState + roleName + availability'
__roleDict['focusedSpeech'] = 'radioState'
formattingDict[pyatspi.ROLE_RADIO_BUTTON] = __roleDict


### pyatspi.ROLE_RADIO_MENU_ITEM ###
__roleDict = {}
__roleDict['focusedSpeech'] = \
__roleDict['unfocusedSpeech'] = \
formattingDict[pyatspi.ROLE_RADIO_BUTTON]['unfocusedSpeech']
__roleDict['unfocusedSpeech'] += ' + accelerator'
formattingDict[pyatspi.ROLE_RADIO_MENU_ITEM] = __roleDict

#### pyatspi.ROLE_ANIMATION####
__roleDict = {}
__roleDict['unfocusedSpeech'] = 'labelOrName'
formattingDict[pyatspi.ROLE_ANIMATION] = __roleDict


#### pyatspi.ROLE_ARROW ####
# [[[TODO: determine orientation of arrow.  Logged as bugzilla bug 319744.]]]
# text = arrow direction (left, right, up, down)
#
        
### pyatspi.ROLE_CHECK_MENU_ITEM ###
__roleDict = {}
__roleDict['unfocusedSpeech'] = \
  'labelOrName + checkRole + checkState + required + availability + accelerator'
__roleDict['focusedSpeech'] = 'checkState'
formattingDict[pyatspi.ROLE_CHECK_MENU_ITEM] = __roleDict

#### pyatspi.ROLE_DIAL ####
# [[[TODO: WDW - might need to include the value here?  Logged as
# bugzilla bug 319746.]]]
#

### pyatspi.ROLE_DIALOG ###
__roleDict = {}
__roleDict['unfocusedSpeech'] = 'labelOrName + unrelatedLabels'
formattingDict[pyatspi.ROLE_DIALOG] = __roleDict

### pyatspi.ROLE_LIST ###
# [[[TODO: WDW - include how many items in the list?
# Logged as bugzilla bug 319749.]]]
#

### pyatspi.ROLE_TOGGLE_BUTTON ###
__roleDict = {}
__roleDict['unfocusedSpeech'] = \
  'labelOrName + roleName + toggleState + availability'
__roleDict['focusedSpeech'] = 'toggleState'
formattingDict[pyatspi.ROLE_TOGGLE_BUTTON] = __roleDict

### pyatspi.ROLE_SLIDER ###
# Ignore the text on the slider.  See bug 340559
# (http://bugzilla.gnome.org/show_bug.cgi?id=340559): the
# implementors of the slider support decided to put in a
# Unicode left-to-right character as part of the text,
# even though that is not painted on the screen.
#
# In Java, however, there are sliders without a label. In
# this case, we'll add to presentation the slider name if
# it exists and we haven't found anything yet.
#
__roleDict = {}
__roleDict['unfocusedSpeech'] = \
  'labelOrName + roleName + value + required + availability'
__roleDict['focusedSpeech'] = 'value'
formattingDict[pyatspi.ROLE_SLIDER] = __roleDict

### pyatspi.ROLE_SPIN_BUTTON ###
__roleDict = {}
__roleDict['unfocusedSpeech'] = \
  formattingDict['default']['unfocusedSpeech'] + ' + required'
__roleDict['focusedSpeech'] = 'name'
formattingDict[pyatspi.ROLE_SPIN_BUTTON] = __roleDict

### pyatspi.ROLE_FRAME ###
__roleDict = {}
__roleDict['unfocusedSpeech'] = \
  'labelOrName +textSelection +roleName +unfocusedDialogueCount +availability'
__roleDict['focusedSpeech'] = ''
formattingDict[pyatspi.ROLE_FRAME] = __roleDict


### pyatspi.ROLE_LIST_ITEM ###
__roleDict = {}
__roleDict['unfocusedSpeech'] = \
  'labelOrName + textSelection + expandableState + availability'
__roleDict['focusedSpeech'] = 'expandableState + availability'
formattingDict[pyatspi.ROLE_LIST_ITEM] = __roleDict


### pyatspi.ROLE_MENU ###
__roleDict = {}
__roleDict['unfocusedSpeech'] = \
  'labelOrName + textSelection + roleName + availability'
__roleDict['focusedSpeech'] = ''
formattingDict[pyatspi.ROLE_MENU] = __roleDict


### pyatspi.ROLE_MENU_ITEM ###
# OpenOffice check menu items currently have a role of "menu item"
# rather then "check menu item", so we need to test if one of the
# states is CHECKED. If it is, then add that in to the list of
# speech utterances. Note that we can't tell if this is a "check
# menu item" that is currently unchecked and speak that state. 
# See Orca bug #433398 for more details.
#
__roleDict = {}
__roleDict['unfocusedSpeech'] = \
  'labelOrName + isCheckedState + availability + accelerator'
__roleDict['focusedSpeech'] = ''
formattingDict[pyatspi.ROLE_MENU_ITEM] = __roleDict


### pyatspi.ROLE_PROGRESS_BAR ###
__roleDict = {}
__roleDict['unfocusedSpeech'] = 'labelOrName + percentage'
__roleDict['focusedSpeech'] = 'percentage'
formattingDict[pyatspi.ROLE_PROGRESS_BAR] = __roleDict


### pyatspi.ROLE_SCROLL_BAR ###
# [[[TODO: WDW - want to get orientation and maybe the
# percentage scrolled so far. Logged as bugzilla bug
# 319744.]]]
#

### pyatspi.ROLE_SPLIT_PANE ###
__roleDict = {}
__roleDict['unfocusedSpeech'] = ' labelOrName + roleName + value + availability'
__roleDict['focusedSpeech'] = 'value'
formattingDict[pyatspi.ROLE_SPLIT_PANE] = __roleDict

### pyatspi.ROLE_TABLE ###
__roleDict = {}
__roleDict['unfocusedSpeech'] = \
__roleDict['focusedSpeech'] = \
formattingDict['default']['unfocusedSpeech'] + ' + hasNoChildren'
formattingDict[pyatspi.ROLE_TABLE] = __roleDict

### REAL_ROLE_TABLE_CELL ### 
# the real cell information
# note that pyatspi.ROLE_TABLE_CELL is used to work out if we need to
# read a whole row. It calls REAL_ROLE_TABLE_CELL internally.
# maybe it can be done in a cleaner way?

__roleDict = {}
__roleDict['unfocusedSpeech'] = \
__roleDict['focusedSpeech'] = \
  '(tableCell2ChildLabel +tableCell2ChildToggle ) or isCheckbox ' + \
  ' + (realActiveDescendantDisplayedText or imageDescription +image) ' + \
  ' + (expandableState and (expandableState +noOfChildren ) ) +required '
formattingDict['REAL_ROLE_TABLE_CELL']  = __roleDict

######## mesar ####

__roleDict = {}
__roleDict['unfocusedSpeech'] = 'tableCellRow'
__roleDict['focusedSpeech'] = \
  '( tableCell2ChildLabel + tableCell2ChildToggle ) or ' + \
  ' isCheckbox + ( realActiveDescendantDisplayedText or imageDescription ) + ' \
  '( expandableState and ( expandableState + noOfChildren ) ) + required '
formattingDict[pyatspi.ROLE_TABLE_CELL] = __roleDict

### pyatspi.ROLE_EMBEDDED ###
__roleDict = {}
__roleDict['unfocusedSpeech'] = \
__roleDict['focusedSpeech'] = 'embedded'
formattingDict[pyatspi.ROLE_EMBEDDED] = __roleDict


### pyatspi.ROLE_ICON ###
__roleDict = {}
__roleDict['unfocusedSpeech'] = \
__roleDict['focusedSpeech'] = 'labelOrName + imageDescription + roleName'
formattingDict[pyatspi.ROLE_ICON] = __roleDict

### pyatspi.ROLE_LAYERED_PANE ###
__roleDict = {}
__roleDict['unfocusedSpeech'] = \
__roleDict['focusedSpeech'] = \
formattingDict['default']['unfocusedSpeech'] + ' + hasNoShowingChildren '
formattingDict[pyatspi.ROLE_LAYERED_PANE] = __roleDict

### pyatspi.ROLE_PARAGRAPH, pyatspi.ROLE_PASSWORD_TEXT, pyatspi.ROLE_TEXT ###
# [[[TODO: WDW - HACK to remove availability because some text
# areas, such as those in yelp, come up as insensitive though
# they really are ineditable.]]]
#
__roleDict = {}
__roleDict['unfocusedSpeech'] = \
__roleDict['focusedSpeech'] = \
  'labelOrName2 + isReadOnly + textRole + currentLineText + textSelection'
formattingDict[pyatspi.ROLE_PARAGRAPH] = \
formattingDict[pyatspi.ROLE_PASSWORD_TEXT] = \
formattingDict[pyatspi.ROLE_TEXT] = __roleDict

### pyatspi.ROLE_TERMINAL ###
__roleDict = {}
__roleDict['unfocusedSpeech'] = \
__roleDict['focusedSpeech'] = 'terminal'
formattingDict[pyatspi.ROLE_TERMINAL] = __roleDict

### pyatspi.ROLE_TEAROFF_MENU_ITEM ###
formattingDict[pyatspi.ROLE_TEAROFF_MENU_ITEM] = \
formattingDict[pyatspi.ROLE_MENU]
