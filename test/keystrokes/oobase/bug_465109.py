#!/usr/bin/python

"""Test to verify bug #465109 is still fixed.
   OOo sbase application crashes when entering a database record.
"""

from macaroon.playback import *

sequence = MacroSequence()

######################################################################
# 1. Start oobase. There is a bug_465109.params file that will
# automatically load bug_465109.odb.
#
sequence.append(WaitForWindowActivate("bug_465109 - OpenOffice.org Base", None))

######################################################################
# 2. Enter Alt-v, right arrow and Return to select Tables from the
# Database column and show the Tables view.
#
# BRAILLE LINE:  'soffice Application bug_465109 - OpenOffice.org Base Frame bug_465109 - OpenOffice.org Base RootPane IconChoiceControl Tree Tables Label'
# VISIBLE:  'Tables Label', cursor=1
# SPEECH OUTPUT: 'Database Objects menu'
# SPEECH OUTPUT: 'View menu'
# SPEECH OUTPUT: 'Forms label'
# SPEECH OUTPUT: 'Tables label'
#
sequence.append(KeyComboAction("<Alt>v"))
sequence.append(WaitForFocus("Database Objects", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Tables", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Return"))

######################################################################
# 3.  Enter Tab three times to get focus to the Addresses table in the
# Tables pane.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TREE))

sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("None", acc_role=pyatspi.ROLE_PUSH_BUTTON))

sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TREE))

######################################################################
# 4. Enter down arrow and Return to bring up a separate window showing
#    the NameAddrPhone table.
#
# BRAILLE LINE:  'soffice Application bug_465109: NameAddrPhone Frame bug_465109: NameAddrPhone RootPane Data source table view Panel'
# VISIBLE:  'Data source table view Panel', cursor=1
# SPEECH OUTPUT: 'bug_465109: NameAddrPhone frame'
# SPEECH OUTPUT: 'panel'
# SPEECH OUTPUT: 'Data source table view panel'
#
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForWindowActivate("bug_465109: NameAddrPhone", None))
sequence.append(WaitForFocus("Data source table view", acc_role=pyatspi.ROLE_PANEL))

######################################################################
# 5. Press Tab to get focus into the LastName field and enter "smith".
#
# BRAILLE LINE:  'soffice Application bug_465109: NameAddrPhone Frame bug_465109: NameAddrPhone RootPane Data source table view Panel  $l'
# VISIBLE:  ' $l', cursor=1
# SPEECH OUTPUT: 'LastName, Row 0 text '
# SPEECH OUTPUT: 'text '
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TEXT))

sequence.append(TypeAction("smith"))

######################################################################
# 6. Press Tab to get focus into the City field and enter "san francisco".
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TEXT))

sequence.append(TypeAction("san francisco"))

######################################################################
# 7. Press Tab to get focus into the StateOrProvince field and enter
#    "california".
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TEXT))

sequence.append(TypeAction("california"))

######################################################################
# 8. Press Tab to get focus into the PhoneNumber field and enter
#    "415-555-1212".
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TEXT))

sequence.append(TypeAction("415-555-1212"))

######################################################################
# 9. Enter Alt-f, up arrow and Return to select Exit from the File menu.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("Up"))
sequence.append(WaitForFocus("Exit", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("Yes", acc_role=pyatspi.ROLE_PUSH_BUTTON))

######################################################################
# 10. Press Tab and Return to not save the current changes.
#     This dismisses the NameAddrPhone table window.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("No", acc_role=pyatspi.ROLE_PUSH_BUTTON))

sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TREE))

######################################################################
# 9. Enter Alt-f, up arrow and Return to select Exit from the File menu.
#    of the main oobase window.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("Up"))
sequence.append(WaitForFocus("Exit", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Return"))

######################################################################
# 10. Wait for things to get back to normal.
#
sequence.append(PauseAction(3000))

sequence.start()
