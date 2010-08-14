#!/usr/bin/python

"""Test to verify bug #382408 is still fixed.
   Significant sluggishness when navigating in OOo Writer tables.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

######################################################################
# 1. Start oowriter. There is a bug_382408.params file that will
#    automatically load table-sample.odt
#
sequence.append(WaitForWindowActivate("table-sample(.odt|) - " + utils.getOOoName("Writer"),None))

######################################################################
# 2. Type Control-Home to move the text caret to the start of the document.
#
sequence.append(KeyComboAction("<Control>Home"))

######################################################################
# 3. Type Insert-F11 to switch to read table cells by row.
#
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("F11"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))

######################################################################
# 4. Type a down arrow to move to the next line.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "Type a down arrow to move to the next line",
    ["BRAILLE LINE:  'soffice Application table-sample.odt - OOo-dev Writer Frame table-sample.odt - OOo-dev Writer RootPane ScrollPane Document view December 2006 \$l'",
     "     VISIBLE:  'December 2006 $l', cursor=1",
     "BRAILLE LINE:  'This is a test. \$l'",
     "     VISIBLE:  'This is a test. \$l', cursor=16",
     "BRAILLE LINE:  'This is a test. \$l'",
     "     VISIBLE:  'This is a test. \$l', cursor=16",
     "SPEECH OUTPUT: 'This is a test.'"]))

######################################################################
# 5. Type a down arrow to move to the Mon table column header.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "Type a down arrow to move to the Mon table column header",
    ["BRAILLE LINE:  'table with 7 rows 7 columns'",
     "     VISIBLE:  'table with 7 rows 7 columns', cursor=0",
     "BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "table-sample(.odt|)", "Calendar-1 Table Sun Mon Tue Wed Thu Fri Sat") + "'",
     "     VISIBLE:  'Mon Tue Wed Thu Fri Sat', cursor=1",
     "SPEECH OUTPUT: 'table with 7 rows 7 columns'",
     "SPEECH OUTPUT: 'Sun Mon Tue Wed Thu Fri Sat'"]))

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

sequence.append(utils.AssertionSummaryAction())

sequence.start()
