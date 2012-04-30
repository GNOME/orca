#!/usr/bin/python

"""Test to verify bug #463172 is still fixed.
   OOo sbase application crashes when entering a database record.
"""

from macaroon.playback import *

sequence = MacroSequence()

######################################################################
# 1. Start oobase. Wait for the first screen of the startup wizard to
#    appear.
#
sequence.append(WaitForWindowActivate("Database Wizard", None))
sequence.append(WaitForFocus("Select database", acc_role=pyatspi.ROLE_LABEL))

######################################################################
# 2. Press Return to get to the second screen of the startup wizard.
#
# BRAILLE LINE:  'soffice Application Database Wizard Dialog Database Wizard OptionPane Steps Panel Save and proceed Label'
# VISIBLE:  'Save and proceed Label', cursor=1
# SPEECH OUTPUT: 'Save and proceed label'
#
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("Save and proceed", acc_role=pyatspi.ROLE_LABEL))

######################################################################
# 3. Press Tab to get to the database registration radio buttons.
#
# BRAILLE LINE:  'soffice Application Database Wizard Dialog Database Wizard OptionPane &=y Do you want the wizard to register the database in OpenOffice.org? Yes, register the database for me RadioButton'
# VISIBLE:  '&=y Do you want the wizard to re', cursor=1
# SPEECH OUTPUT: 'Yes, register the database for me selected radio button'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Yes, register the database for me", acc_role=pyatspi.ROLE_RADIO_BUTTON))

######################################################################
# 4. Press down arrow to not register this database.
#
# BRAILLE LINE:  'soffice Application Database Wizard Dialog Database Wizard OptionPane &=y No, do not register the database RadioButton'
# VISIBLE:  '&=y No, do not register the data', cursor=1
# SPEECH OUTPUT: 'No, do not register the database selected radio button'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("No, do not register the database", acc_role=pyatspi.ROLE_RADIO_BUTTON))
sequence.append(PauseAction(3000))

######################################################################
# 5. Press Return to Finish the startup wizard.
#
# BRAILLE LINE:  'soffice Application Save Dialog ScrollPane Files Table'
# VISIBLE:  'Files Table', cursor=1
# SPEECH OUTPUT: 'Save'
# SPEECH OUTPUT: 'Files table'
#
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("Files", acc_role=pyatspi.ROLE_TABLE))
sequence.append(PauseAction(3000))

######################################################################
# 6. A Save dialog has appeared. Press Return to select the default name.
#    A database window will appear.
#
# BRAILLE LINE:  'soffice Application New Database - OpenOffice.org Base Frame New Database - OpenOffice.org Base RootPane IconChoiceControl Tree Forms Label'
# VISIBLE:  'Forms Label', cursor=1
# SPEECH OUTPUT: 'New Database - OpenOffice.org Base frame'
# SPEECH OUTPUT: 'panel'
# SPEECH OUTPUT: 'panel'
# SPEECH OUTPUT: 'panel'
# SPEECH OUTPUT: 'Forms label'
# SPEECH OUTPUT: 'panel'
# SPEECH OUTPUT: 'Forms label'
#
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForWindowActivate("New Database - OpenOffice.org Base", None))
sequence.append(WaitForFocus("IconChoiceControl", acc_role=pyatspi.ROLE_TREE))

######################################################################
# 7. Enter Alt-f, Alt-c to close the database window.
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
# 8. Wait for things to get back to normal.
#
sequence.append(PauseAction(3000))

sequence.start()
