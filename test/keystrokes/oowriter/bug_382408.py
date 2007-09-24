#!/usr/bin/python

"""Test to verify bug #382408 is still fixed.
   Significant sluggishness when navigating in OOo Writer tables.
"""

from macaroon.playback import *

sequence = MacroSequence()

######################################################################
# 1. Start oowriter. There is a bug_382408.params file that will
#    automatically load table-sample.odt
#
sequence.append(WaitForWindowActivate("table-sample - OpenOffice.org Writer",None))

######################################################################
# 2. Type Control-Home to move the text caret to the start of the document.
#
sequence.append(KeyComboAction("<Control>Home"))

######################################################################
# 3. Type Insert-F11 to switch to read table cells by row.
#
sequence.append(KeyPressAction (0, 106,"Insert"))      # Press Insert
sequence.append(KeyComboAction("F11"))
sequence.append(KeyReleaseAction(150, 106,"Insert"))   # Release Insert

######################################################################
# 4. Type a down arrow to move to the next line.
#
# BRAILLE LINE:  'soffice Application table-sample - OpenOffice.org Writer Frame table-sample - OpenOffice.org Writer RootPane ScrollPane Document view This is a test. $l'
# VISIBLE:  'This is a test. $l', cursor=16
# SPEECH OUTPUT: 'This is a test.'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 5. Type a down arrow to move to the Mon table column header.
#
# BRAILLE LINE:  'soffice Application table-sample - OpenOffice.org Writer Frame table-sample - OpenOffice.org Writer RootPane ScrollPane Document view Calendar-1 Table Mon Paragraph'
# VISIBLE:  'Mon Paragraph', cursor=1
# SPEECH OUTPUT: 'table with 7 rows and 7 columns.'
# SPEECH OUTPUT: 'Cell B1'
# SPEECH OUTPUT: 'Mon'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 6. Enter Alt-f, Alt-c to close this Writer application.
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
# 7. Enter Alt-f, right arrow and Return, (File->New->Text Document),
#    to get the application back to the state it was in when the
#    test started.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Text Document", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Return"))
sequence.append(WaitAction("object:property-change:accessible-name",
                           None,
                           None,
                           pyatspi.ROLE_ROOT_PANE,
                           30000))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 8. Wait for things to get back to normal.
#
sequence.append(PauseAction(3000))

sequence.start()
