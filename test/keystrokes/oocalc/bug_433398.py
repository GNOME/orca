#!/usr/bin/python

"""Test to verify bug #433398 is still fixed.
   Orca does not provide access to the state of checked menu items in OOo.
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
# BRAILLE LINE:  'soffice Application fruit - OpenOffice.org Calc Frame fruit - OpenOffice.org Calc RootPane MenuBar Freeze'
# VISIBLE:  'Freeze', cursor=1
# SPEECH OUTPUT: 'Freeze'
#
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))

######################################################################
# 6. Type Return to check it.
#
# BRAILLE LINE:  'soffice Application fruit - OpenOffice.org Calc Frame fruit - OpenOffice.org Calc RootPane ScrollPane Document view4 Sheet Sheet1 Table Apples Cell B1 '
# VISIBLE:  'Apples Cell B1 ', cursor=1
# SPEECH OUTPUT: 'Apples B1'
#
sequence.append(KeyComboAction("Return"))

######################################################################
# 7. Type Alt-w to bring up the Windows menu.
#
sequence.append(KeyComboAction("<Alt>w"))
sequence.append(WaitForFocus("New Window", acc_role=pyatspi.ROLE_MENU_ITEM))

######################################################################
# 8. Type down arrow three times to get to the Freeze menu item.
#
# BRAILLE LINE:  'soffice Application fruit - OpenOffice.org Calc Frame fruit - OpenOffice.org Calc RootPane MenuBar <x> Freeze'
# VISIBLE:  '<x> Freeze', cursor=1
# SPEECH OUTPUT: 'Freeze checked'
#
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))

######################################################################
# 9. Type Return to uncheck it.
#
# BRAILLE LINE:  'soffice Application fruit - OpenOffice.org Calc Frame fruit - OpenOffice.org Calc RootPane ScrollPane Document view3 Sheet Sheet1 Table Apples Cell B1 '
# VISIBLE:  'Apples Cell B1 ', cursor=1
# SPEECH OUTPUT: 'Apples B1'
#
sequence.append(KeyComboAction("Return"))

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

sequence.start()
