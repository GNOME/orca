#!/usr/bin/python

"""Test to verify bug #361167 is still fixed.
   Add dynamic row and column header support in Orca for 
   StarOffice/OpenOffice calc.
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
# 5. Press the down arrow to move to cell A2.
#
# BRAILLE LINE:  'soffice Application fruit - OpenOffice.org Calc Frame fruit - OpenOffice.org Calc RootPane ScrollPane Document view3 Sheet Sheet1 Table  Good in Pies Good in Pies Cell A2 '
# VISIBLE:  'Good in Pies Cell A2 ', cursor=1
# SPEECH OUTPUT: 'Good in Pies Good in Pies A2'
#
sequence.append(KeyComboAction("Down"))

######################################################################
# 6. Press the right arrow to move to cell B2.
#
# BRAILLE LINE:  'soffice Application fruit - OpenOffice.org Calc Frame fruit - OpenOffice.org Calc RootPane ScrollPane Document view3 Sheet Sheet1 Table  Apples Yes Cell B2 '
# VISIBLE:  'Yes Cell B2 ', cursor=1
# SPEECH OUTPUT: 'Apples Yes B2'
#
sequence.append(KeyComboAction("Right"))

######################################################################
# 7. Press the down arrow to move to cell B3.
#
# BRAILLE LINE:  'soffice Application fruit - OpenOffice.org Calc Frame fruit - OpenOffice.org Calc RootPane ScrollPane Document view3 Sheet Sheet1 Table  Juiceable Yes Cell B3 '
# VISIBLE:  'Yes Cell B3 ', cursor=1
# SPEECH OUTPUT: 'Juiceable Yes B3'
#
sequence.append(KeyComboAction("Down"))

######################################################################
# 8. Press the right arrow to move to cell C3.
#
# BRAILLE LINE:  'soffice Application fruit - OpenOffice.org Calc Frame fruit - OpenOffice.org Calc RootPane ScrollPane Document view3 Sheet Sheet1 Table  Pears Yes Cell C3 '
# VISIBLE:  'Yes Cell C3 ', cursor=1
# SPEECH OUTPUT: 'Pears Yes C3'
#
sequence.append(KeyComboAction("Right"))

######################################################################
# 9. Press the up arrow to move to cell C2.
#
# BRAILLE LINE:  'soffice Application fruit - OpenOffice.org Calc Frame fruit - OpenOffice.org Calc RootPane ScrollPane Document view3 Sheet Sheet1 Table  Good in Pies No Cell C2 '
# VISIBLE:  'No Cell C2 ', cursor=1
# SPEECH OUTPUT: 'Good in Pies No C2'
#
sequence.append(KeyComboAction("Up"))

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
