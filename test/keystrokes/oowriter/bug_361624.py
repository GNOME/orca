#!/usr/bin/python

"""Test to verify bug #361624 is still fixed.
   Flat review sometimes fails to move to second column of text in 
   OOo Writer documents.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

######################################################################
# 1. Start oowriter. There is a bug_361624.params file that will
#    automatically load column-example.odt.
#
sequence.append(WaitForWindowActivate("column-example " + utils.getOOoName("Writer"), None))

######################################################################
# 2. Type Control-Home to position the text caret to the left of the
#    first character on the first line.
#
sequence.append(KeyComboAction("<Control>Home"))

######################################################################
# 3. Type KP-8 to read the first line in flat review mode.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8", 3000))
sequence.append(utils.AssertPresentationAction(
    "Read first line in flat review mode",
    ["BRAILLE LINE:  'panel EFFector Vol. 19, No. 38  October  Intercept Personal  $l'",
     "     VISIBLE:  'EFFector Vol. 19, No. 38  Octobe', cursor=1",
     "SPEECH OUTPUT: 'panel EFFector Vol. 19, No. 38  October  Intercept Personal ",
     "'"]))

######################################################################
# 4. Type KP-9 to read the next line in flat review mode.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9", 3000))
sequence.append(utils.AssertPresentationAction(
    "Read line two in flat review mode",
    ["BRAILLE LINE:  '10, 2006  editor@eff.org Communications $l'",
     "     VISIBLE:  '10, 2006  editor@eff.org Communi', cursor=1",
     "SPEECH OUTPUT: '10, 2006  editor@eff.org",
     " Communications",
     "'"]))

######################################################################
# 5. Type KP-9 to read the next line in flat review mode.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9", 3000))
sequence.append(utils.AssertPresentationAction(
    "Read line three in flat review mode",
    ["BRAILLE LINE:  '  $l'",
     "     VISIBLE:  '  $l', cursor=1",
     "SPEECH OUTPUT: 'white space'"]))

######################################################################
# 6. Type KP-9 to read the next line in flat review mode.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9", 3000))
sequence.append(utils.AssertPresentationAction(
    "Read line four in flat review mode",
    ["BRAILLE LINE:  'A Publication of the Electronic  Washington, D.C. - The FLAG  $l'",
     "     VISIBLE:  'A Publication of the Electronic ', cursor=1",
     "SPEECH OUTPUT: 'A Publication of the Electronic  Washington, D.C. - The FLAG '"]))

######################################################################
# 7. Enter Alt-f, Alt-c to close the Writer application.
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
# 8. Enter Alt-f, right arrow and Return, (File->New->Text Document),
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
# 9. Wait for things to get back to normal.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
