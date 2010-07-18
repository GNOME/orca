#!/usr/bin/python

"""Test to verify bug #433398 is still fixed.
   Orca does not provide access to the state of checked menu items in OOo.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

######################################################################
# 1. Start oocalc. There is a bug_361167.params file that will
#    automatically load fruit.ods.
#
sequence.append(PauseAction(3000))

######################################################################
# 2. Type Control-Home to position the text caret in cell A1.
#
sequence.append(KeyComboAction("<Control>Home"))

######################################################################
# 3. Press the right arrow to move to cell B2.
#
sequence.append(KeyComboAction("Right"))

######################################################################
# 4. Type Alt-w to bring up the Windows menu.
sequence.append(KeyComboAction("<Alt>w"))
sequence.append(WaitForFocus("New Window", acc_role=pyatspi.ROLE_MENU_ITEM))

######################################################################
# 5. Type down arrow three times to get to the Freeze menu item
#
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Type down arrow to get to the Freeze menu item [1]",
    ["BRAILLE LINE:  'soffice Application fruit.ods - " + utils.getOOoName("Calc") + " Frame fruit.ods - " + utils.getOOoName("Calc") + " RootPane MenuBar Freeze'",
     "     VISIBLE:  'Freeze', cursor=1",
     "SPEECH OUTPUT: 'Freeze'"]))

######################################################################
# 6. Type Return to check it.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "Type Return to check it",
    ["BRAILLE LINE:  'soffice Application fruit.ods - " + utils.getOOoName("Calc") + " Frame fruit.ods - " + utils.getOOoName("Calc") + " RootPane ScrollPane Document view4 Sheet Sheet1 Table'",
     "     VISIBLE:  'Sheet Sheet1 Table', cursor=1",
     "BRAILLE LINE:  'soffice Application fruit.ods - " + utils.getOOoName("Calc") + " Frame fruit.ods - " + utils.getOOoName("Calc") + " RootPane ScrollPane Document view4 Sheet Sheet1 Table Apples Cell B1 '",
     "     VISIBLE:  'Apples Cell B1 ', cursor=1",
     "SPEECH OUTPUT: 'Sheet Sheet1 table'",
     "SPEECH OUTPUT: 'Apples B1'"]))

######################################################################
# 7. Type Alt-w to bring up the Windows menu.
#
sequence.append(KeyComboAction("<Alt>w"))
sequence.append(WaitForFocus("New Window", acc_role=pyatspi.ROLE_MENU_ITEM))

######################################################################
# 8. Type down arrow three times to get to the Freeze menu item.
#
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Type down arrow to get to the Freeze menu item [2]",
    ["BRAILLE LINE:  'soffice Application fruit.ods - " + utils.getOOoName("Calc") + " Frame fruit.ods - " + utils.getOOoName("Calc") + " RootPane MenuBar <x> Freeze'",
     "     VISIBLE:  '<x> Freeze', cursor=1",
     "SPEECH OUTPUT: 'Freeze checked'"]))

######################################################################
# 9. Type Return to uncheck it.
#
# BRAILLE LINE:  'soffice Application fruit - OpenOffice.org Calc Frame fruit - OpenOffice.org Calc RootPane ScrollPane Document view3 Sheet Sheet1 Table Apples Cell B1 '
# VISIBLE:  'Apples Cell B1 ', cursor=1
# SPEECH OUTPUT: 'Apples B1'
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "Type Return to uncheck it",
    ["BUG? - Our 'text does not fit feature might need some tweaking. In this case the contents are not too long. False positive likely due to the height",
     "BRAILLE LINE:  'soffice Application fruit.ods - " + utils.getOOoName("Calc") + " Frame fruit.ods - " + utils.getOOoName("Calc") + " RootPane ScrollPane Document view3 Sheet Sheet1 Table'",
     "     VISIBLE:  'Sheet Sheet1 Table', cursor=1",
     "BRAILLE LINE:  'soffice Application fruit.ods - " + utils.getOOoName("Calc") + " Frame fruit.ods - " + utils.getOOoName("Calc") + " RootPane ScrollPane Document view3 Sheet Sheet1 Table Apples Cell B1 '",
     "     VISIBLE:  'Apples Cell B1 ', cursor=1",
     "SPEECH OUTPUT: 'Sheet Sheet1 table'",
     "SPEECH OUTPUT: 'Apples B1.'",
     "SPEECH OUTPUT: '6 characters too long'"]))

######################################################################
# 10. Enter Alt-f, Alt-c to close the Calc spreadsheet window.
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
# 11. Enter Alt-f, right arrow, down arrow and Return,
#     (File->New->Spreadsheet), to get the application back
#     to the state it was in when the test started.
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
# 12. Wait for things to get back to normal.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
