#!/usr/bin/python

"""Test to verify bug #363804 is still fixed.
   Add ability to turn off coordinate announcement when navigating in Calc.
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
# BRAILLE LINE:  'soffice Application fruit - OpenOffice.org Calc Frame fruit - OpenOffice.org Calc RootPane ScrollPane Document view3 Sheet Sheet1 Table Cell A1 '
# VISIBLE:  'Cell A1 ', cursor=1
# SPEECH OUTPUT: ' A1'
#
sequence.append(KeyComboAction("<Control>Home"))

######################################################################
# 3. Press the down arrow to move to cell A2.
#
# BRAILLE LINE:  'soffice Application fruit - OpenOffice.org Calc Frame fruit - OpenOffice.org Calc RootPane ScrollPane Document view3 Sheet Sheet1 Table Good in Pies Cell A2 '
# VISIBLE:  'Good in Pies Cell A2 ', cursor=1
# SPEECH OUTPUT: 'Good in Pies A2'
#
sequence.append(KeyComboAction("Down"))

######################################################################
# 4. Press the right arrow to move to cell B2.
#
# BRAILLE LINE:  'soffice Application fruit - OpenOffice.org Calc Frame fruit - OpenOffice.org Calc RootPane ScrollPane Document view3 Sheet Sheet1 Table Yes Cell B2 '
# VISIBLE:  'Yes Cell B2 ', cursor=1
# SPEECH OUTPUT: 'Yes B2'
#
sequence.append(KeyComboAction("Right"))

######################################################################
# 5. Type Insert-Control-space to bring up the application specific
#    Preferences dialog for soffice.
#
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("<control>space"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(WaitForWindowActivate("Orca Preferences for soffice",None))
sequence.append(WaitForFocus("Speech", acc_role=pyatspi.ROLE_PAGE_TAB))

######################################################################
# 6. Press End to move focus to the soffice application specific tab in
#    the Preferences dialog.
#
sequence.append(KeyComboAction("End"))
sequence.append(WaitForFocus("soffice", acc_role=pyatspi.ROLE_PAGE_TAB))

######################################################################
# 7. Press Tab to move to the "Speak spread sheet cell coordinates"
#    checkbox.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Speak spread sheet cell coordinates", acc_role=pyatspi.ROLE_CHECK_BOX))

######################################################################
# 8. Press Space to toggle the state to unchecked.
#
sequence.append(TypeAction(" "))

######################################################################
# 9. Type Alt-o to press the OK button and reload the Orca user settings.
#
sequence.append(KeyComboAction("<Alt>o"))
sequence.append(WaitForWindowActivate("fruit - OpenOffice.org Calc",None))

######################################################################
# 10. Type Control-Home to position the text caret in cell A1.
#
# BRAILLE LINE:  'soffice Application fruit - OpenOffice.org Calc Frame fruit - OpenOffice.org Calc RootPane ScrollPane Document view3 Sheet Sheet1 Table Cell A1 '
# VISIBLE:  'Cell A1 ', cursor=1
# SPEECH OUTPUT: 'blank'
#
sequence.append(KeyComboAction("<Control>Home"))

######################################################################
# 11. Press the down arrow to move to cell A2.
#
# BRAILLE LINE:  'soffice Application fruit - OpenOffice.org Calc Frame fruit - OpenOffice.org Calc RootPane ScrollPane Document view3 Sheet Sheet1 Table Good in Pies Cell A2 '
# VISIBLE:  'Good in Pies Cell A2 ', cursor=1
# SPEECH OUTPUT: 'Good in Pies'
#
sequence.append(KeyComboAction("Down"))

######################################################################
# 12. Press the right arrow to move to cell B2.
#
# BRAILLE LINE:  'soffice Application fruit - OpenOffice.org Calc Frame fruit - OpenOffice.org Calc RootPane ScrollPane Document view3 Sheet Sheet1 Table Yes Cell B2 '
# VISIBLE:  'Yes Cell B2 ', cursor=1
# SPEECH OUTPUT: 'Yes'
#
sequence.append(KeyComboAction("Right"))

######################################################################
# 13. Enter Alt-f, Alt-c to close the Calc spreadsheet window.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("<Alt>c"))
sequence.append(WaitAction("object:property-change:accessible-name",
                           None,
                           None,
                           pyatspi.ROLE_ROOT_PANE,
                           30000))
#sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PANEL))

######################################################################
# 14. Enter Alt-f, right arrow, down arrow and Return,
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
# 15. Wait for things to get back to normal.
#
sequence.append(PauseAction(3000))

sequence.start()
