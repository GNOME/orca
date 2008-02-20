#!/usr/bin/python

"""Test to verify bug #364407 is still fixed.
   Shift+Ctrl+T in OOCalc results in very verbose output.
"""

from macaroon.playback import *
import utils

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
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Text Document", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Spreadsheet", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("Sheet Sheet1", acc_role=pyatspi.ROLE_TABLE))
sequence.append(utils.AssertPresentationAction(
    "File->New->Spreadsheet",
    ["BRAILLE LINE:  'soffice Application Untitled2 - OpenOffice.org Calc Frame'",
     "     VISIBLE:  'Untitled2 - OpenOffice.org Calc ', cursor=1",
     "BRAILLE LINE:  'soffice Application Untitled2 - OpenOffice.org Calc Frame Untitled2 - OpenOffice.org Calc RootPane Panel'",
     "     VISIBLE:  'Panel', cursor=1",
     "BRAILLE LINE:  'soffice Application Untitled2 - OpenOffice.org Calc Frame Untitled2 - OpenOffice.org Calc RootPane ScrollPane Document view3 Sheet Sheet1 Table'",
     "     VISIBLE:  'Sheet Sheet1 Table', cursor=1",
     "BRAILLE LINE:  'soffice Application Untitled2 - OpenOffice.org Calc Frame Untitled2 - OpenOffice.org Calc RootPane ScrollPane Document view3 Sheet Sheet1 Table Cell A1 '",
     "     VISIBLE:  'Cell A1 ', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Untitled2 - OpenOffice.org Calc frame'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'panel'",
     "SPEECH OUTPUT: 'Sheet Sheet1 table grayed'",
     "SPEECH OUTPUT: ' A1'"]))

######################################################################
# 3. Type Control-Shift-t to give focus to the spreadsheet cell locator.
#
# BRAILLE LINE:  'soffice Application Untitled2 - OpenOffice.org Calc Frame Untitled2 - OpenOffice.org Calc RootPane ToolBar A1 $l'
# VISIBLE:  'A1 $l', cursor=2
# SPEECH OUTPUT: ''
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift><Control>t"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_LIST))
sequence.append(utils.AssertPresentationAction(
    "Type Control-Shift-t to give focus to the spreadsheet cell locator",
    ["BUG: not brailling/speaking anything"]))

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
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("c3", 0, 1000))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("Sheet Sheet1", acc_role=pyatspi.ROLE_TABLE))
sequence.append(utils.AssertPresentationAction(
    "Type 'c3' followed by Return to jump to cell C3 in the spreadsheet",
    ["BRAILLE LINE:  'soffice Application Untitled2 - OpenOffice.org Calc Frame Untitled2 - OpenOffice.org Calc RootPane ToolBar c $l'",
     "     VISIBLE:  'c $l', cursor=2",
     "BRAILLE LINE:  'soffice Application Untitled2 - OpenOffice.org Calc Frame Untitled2 - OpenOffice.org Calc RootPane ToolBar c $l'",
     "     VISIBLE:  'c $l', cursor=2",
     "BRAILLE LINE:  'soffice Application Untitled2 - OpenOffice.org Calc Frame Untitled2 - OpenOffice.org Calc RootPane ToolBar c3 $l'",
     "     VISIBLE:  'c3 $l', cursor=3",
     "BRAILLE LINE:  'soffice Application Untitled2 - OpenOffice.org Calc Frame Untitled2 - OpenOffice.org Calc RootPane ToolBar c3 $l'",
     "     VISIBLE:  'c3 $l', cursor=3",
     "BRAILLE LINE:  'soffice Application Untitled2 - OpenOffice.org Calc Frame Untitled2 - OpenOffice.org Calc RootPane ToolBar c3 $l'",
     "     VISIBLE:  'c3 $l', cursor=1",
     "BRAILLE LINE:  'soffice Application Untitled2 - OpenOffice.org Calc Frame Untitled2 - OpenOffice.org Calc RootPane ScrollPane Document view3 Sheet Sheet1 Table Cell C3 '",
     "     VISIBLE:  'Cell C3 ', cursor=1",
     "SPEECH OUTPUT: ' C3'"]))

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

sequence.append(utils.AssertionSummaryAction())

sequence.start()
