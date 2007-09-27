#!/usr/bin/python

"""Test to verify bug #363801 is still fixed.
   Provide confirmation when the user presses Insert R/C in Calc.
"""

from macaroon.playback import *

sequence = MacroSequence()

######################################################################
# 1. Start oocalc. There is a bug_361167.params file that will
#    automatically load fruit.ods.
#
sequence.append(WaitForWindowActivate("fruit - OpenOffice.org Calc",None))

######################################################################
# 2. Type Control-Home to position the text caret in cell A1.
#
sequence.append(KeyComboAction("<Control>Home"))

######################################################################
# 3. Type Insert-r to set the dynamical column headers to the first column.
#
# BRAILLE LINE:  'Dynamic column header set for row 1'
# VISIBLE:  'Dynamic column header set for ro', cursor=0
# SPEECH OUTPUT: 'Dynamic column header set for row 1'
#
sequence.append(KeyPressAction (0, 106,"Insert"))      # Press Insert
sequence.append(KeyComboAction("r"))
sequence.append(KeyReleaseAction(150, 106,"Insert"))   # Release Insert

######################################################################
# 4. Type Insert-c to set the dynamical row headers to the first row.
#
# BRAILLE LINE:  'Dynamic row header set for column A'
# VISIBLE:  'Dynamic row header set for colum', cursor=0
# SPEECH OUTPUT: 'Dynamic row header set for column A'
#
sequence.append(KeyPressAction (0, 106,"Insert"))      # Press Insert
sequence.append(KeyComboAction("c"))
sequence.append(KeyReleaseAction(150, 106,"Insert"))   # Release Insert

######################################################################
# 5. Type Insert-r twice to clear the dynamical column headers.
#
# BRAILLE LINE:  'Dynamic column header cleared.'
# VISIBLE:  'Dynamic column header cleared.', cursor=0
# SPEECH OUTPUT: 'Dynamic column header cleared.'
#
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("r"))
sequence.append(KeyComboAction("r"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(PauseAction(3000))

######################################################################
# 6. Type Insert-c twice to clear the dynamical row headers.
#
# BRAILLE LINE:  'Dynamic row header cleared.'
# VISIBLE:  'Dynamic row header cleared.', cursor=0
# SPEECH OUTPUT: 'Dynamic row header cleared.'
#
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("c"))
sequence.append(KeyComboAction("c"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(PauseAction(3000))

######################################################################
# 7. Enter Alt-f, Alt-c to close the Calc spreadsheet window.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))
sequence.append(KeyComboAction("<Alt>c"))
sequence.append(WaitAction("object:property-change:accessible-name",
                           None,
                           None,
                           pyatspi.ROLE_ROOT_PANE,
                           30000))

######################################################################
# 8. Enter Alt-f, right arrow, down arrow and Return,
#    (File->New->Spreadsheet), to get the application back 
#    to the state it was in when the test started.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Text Document", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Spreadsheet", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Return"))
sequence.append(WaitAction("object:property-change:accessible-name",
                           None,
                           None,
                           pyatspi.ROLE_ROOT_PANE,
                           30000))

######################################################################
# 9. Wait for things to get back to normal.
#
sequence.append(PauseAction(3000))

sequence.start()
