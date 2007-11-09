#!/usr/bin/python

"""Test to verify bug #364407 is still fixed.
   Shift+Ctrl+T in OOCalc results in very verbose output.
"""

from macaroon.playback import *

sequence = MacroSequence()

######################################################################
# 1. Start oocalc.
#
sequence.append(WaitForWindowActivate("Untitled1 - OpenOffice.org Calc",None))
sequence.append(WaitForFocus("Sheet Sheet1", acc_role=pyatspi.ROLE_TABLE))

######################################################################
# 2. Enter Alt-f, right arrow, down arrow and Return.
#    (File->New->Spreadsheet).
#
# BRAILLE LINE:  'soffice Application Untitled2 - OpenOffice.org Calc Frame Untitled2 - OpenOffice.org Calc RootPane ScrollPane Document view3 Sheet Sheet1 Table Cell A1 '
# VISIBLE:  'Cell A1 ', cursor=1
# SPEECH OUTPUT: ' A1'
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Text Document", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Spreadsheet", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("Sheet Sheet1", acc_role=pyatspi.ROLE_TABLE))

######################################################################
# 3. Type Control-Shift-t to give focus to the spreadsheet cell locator.
#
# BRAILLE LINE:  'soffice Application Untitled2 - OpenOffice.org Calc Frame Untitled2 - OpenOffice.org Calc RootPane ToolBar A1 $l'
# VISIBLE:  'A1 $l', cursor=2
# SPEECH OUTPUT: ''
#
sequence.append(KeyComboAction("<Shift><Control>t"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_LIST))

######################################################################
# 4. Type right arrow twice and backspace twice to remove the current 
#    text ("A1").
#
sequence.append(KeyComboAction("Right"))
sequence.append(KeyComboAction("Right"))
sequence.append(KeyComboAction("BackSpace"))
sequence.append(KeyComboAction("BackSpace"))

######################################################################
# 5. Type "c3" followed by Return to jump to cell C3 in the spreadsheet.
#
# BRAILLE LINE:  'soffice Application Untitled2 - OpenOffice.org Calc Frame Untitled2 - OpenOffice.org Calc RootPane ScrollPane Document view3 Sheet Sheet1 Table Cell C3 '
# VISIBLE:  'Cell C3 ', cursor=1
# SPEECH OUTPUT: ' C3'
#
sequence.append(TypeAction("c3", 0, 1000))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("Sheet Sheet1", acc_role=pyatspi.ROLE_TABLE))

######################################################################
# 6. Enter Alt-f, Alt-c to close the Calc spreadsheet window.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))
sequence.append(KeyComboAction("<Alt>c"))

######################################################################
# 7. Wait for things to get back to normal.
#
sequence.append(PauseAction(3000))

sequence.start()
