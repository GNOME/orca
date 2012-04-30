#!/usr/bin/python

"""Test to verify bug #435201 is still fixed.
   Orca is too chatty when navigating by paragraph in OOo Writer.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

######################################################################
# 1. Start oowriter. There is a bug_435201.params file that will
# automatically load spanish.odt
#
sequence.append(WaitForWindowActivate("spanish - " + utils.getOOoName("Writer"), None))

######################################################################
# 2. Type Control-Home to position the text caret to the left of the
#    first character on the first line. Then Down Arrow and Up Arrow
#    once because our caret-moved events seem to initially be AWOL in
#    m29 and m30.
#
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Up"))

######################################################################
# 3. Type Control-down to move to the next paragraph.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Down"))
sequence.append(utils.AssertPresentationAction(
    "Type Control-down to move to the next paragraph [1]",
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Amongst our weaponry are such diverse  \$l'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=1",
     "BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Amongst our weaponry are such diverse  \$l",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=1",
     "SPEECH OUTPUT: 'NOBODY expects the Spanish Inquisition! Amongst our weaponry are such diverse elements as: fear, surprise, ruthless efficiency, an almost fanatical devotion to the Pope, and nice red uniforms - Oh damn!'"]))

######################################################################
# 4. Type Control-down to move to the next paragraph.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Down"))
sequence.append(utils.AssertPresentationAction(
    "Type Control-down to move to the next paragraph [2]",
    ["BRAILLE LINE:  ' \$l'",
     "     VISIBLE:  ' \$l', cursor=1",
     "BRAILLE LINE:  ' \$l'",
     "     VISIBLE:  ' \$l', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

######################################################################
# 5. Type Control-down to move to the next paragraph.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Down"))
sequence.append(utils.AssertPresentationAction(
    "Type Control-down to move to the next paragraph [3]",
    ["BRAILLE LINE:  'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject  \$l'",
     "     VISIBLE:  'Now old lady, you have one last ', cursor=1",
     "BRAILLE LINE:  'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject  \$l'",
     "     VISIBLE:  'Now old lady, you have one last ', cursor=1",
     "SPEECH OUTPUT: 'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the ungodly. Two last chances. And you shall be free. Three last chances. You have three last chances, the nature of which I have divulged in my previous utterance.'"]))

######################################################################
# 6. Type Control-down to move to the next paragraph.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Down"))
sequence.append(utils.AssertPresentationAction(
    "Type Control-down to move to the next paragraph [4]",
    ["BRAILLE LINE:  ' \$l'",
     "     VISIBLE:  ' \$l', cursor=1",
     "BRAILLE LINE:  ' \$l'",
     "     VISIBLE:  ' \$l', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

######################################################################
# 7. Type Control-down to move to the next paragraph.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Down"))
sequence.append(utils.AssertPresentationAction(
    "Type Control-down to move to the next paragraph [5]",
    ["BRAILLE LINE:  'Hm! She is made of harder stuff! Cardinal Fang! Fetch the COMFY CHAIR! \$l'",
     "     VISIBLE:  'Hm! She is made of harder stuff!', cursor=1",
     "BRAILLE LINE:  'Hm! She is made of harder stuff! Cardinal Fang! Fetch the COMFY CHAIR! \$l'",
     "     VISIBLE:  'Hm! She is made of harder stuff!', cursor=1",
     "SPEECH OUTPUT: 'Hm! She is made of harder stuff! Cardinal Fang! Fetch the COMFY CHAIR!'"]))

######################################################################
# 8. Enter Alt-f, Alt-c to close the Writer application.
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
# 9. Enter Alt-f, right arrow and Return, (File->New->Text Document),
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
# 10. Wait for things to get back to normal.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
