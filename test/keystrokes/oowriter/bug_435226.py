#!/usr/bin/python

"""Test to verify bug #435226 is still fixed.
   Where-am-I doesn't correctly handle multiple selected paragraphs in 
   OOo Writer and Evolution.
   Note that bug #480278 was opened, because the output was being smushed.
   The SPEECH OUTPUT line in step #8 for this test has been adjusted to 
   reflect the now correct output.

"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

######################################################################
# 1. Start oowriter. There is a bug_435226.params file that will
#    automatically load spanish.odt.
#
sequence.append(WaitForWindowActivate("spanish(.odt|) - " + utils.getOOoName("Writer"), None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 2. Type Control-Home to position the text caret to the left of the
#    first character on the first line.
#
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 3. Type Control-right three times to position the text caret at the 
#    fourth word on the first line.
#
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(KeyComboAction("<Control>Right"))

######################################################################
# 4. Type Shift-Control-down to select from where the text caret was for
#    five paragraphs.
#
sequence.append(KeyComboAction("<Shift><Control>Down"))
sequence.append(KeyComboAction("<Shift><Control>Down"))
sequence.append(KeyComboAction("<Shift><Control>Down"))
sequence.append(KeyComboAction("<Shift><Control>Down"))
sequence.append(KeyComboAction("<Shift><Control>Down"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 5. Type Shift-down to position the text caret at the begining of the
#    last paragraph.
#
sequence.append(KeyComboAction("<Shift>Down"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 6. Type Shift-Control-right five times to also select the first five
#    words of the last paragraph.
#
sequence.append(KeyComboAction("<Shift><Control>Right"))
sequence.append(KeyComboAction("<Shift><Control>Right"))
sequence.append(KeyComboAction("<Shift><Control>Right"))
sequence.append(KeyComboAction("<Shift><Control>Right"))
sequence.append(KeyComboAction("<Shift><Control>Right"))

######################################################################
# 7. Type KP-Enter once to do a "single-click" where-am-I operation.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Type KP-Enter once to do a 'single-click' where-am-I operation",
    ["BRAILLE LINE:  'Hm! She is made of harder stuff! Cardinal Fang! Fetch the COMFY CHAIR! \$l'",
     "     VISIBLE:  'Hm! She is made of harder stuff!', cursor=17",
     "SPEECH OUTPUT: 'Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and surprise. And ruthless efficiency. Our three weapons are fear, surprise, and ruthless efficiency. And an almost fanatical devotion to the Pope. Our four. No. Amongst our weapons. Amongst our weaponry, are such elements as fear, surprise. I'll come in again. NOBODY expects the Spanish Inquisition! Amongst our weaponry are such diverse elements as: fear, surprise, ruthless efficiency, an almost fanatical devotion to the Pope, and nice red uniforms - Oh damn! Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the ungodly. Two last chances. And you shall be free. Three last chances. You have three last chances, the nature of which I have divulged in my previous utterance. Hm! She is made  selected'"]))

######################################################################
# 8. Type KP-Enter twice to do a "double-click" where-am-I operation.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Type KP-Enter twice to do a 'double-click' where-am-I operation",
    ["BRAILLE LINE:  'Hm! She is made of harder stuff! Cardinal Fang! Fetch the COMFY CHAIR! \$l'",
     "     VISIBLE:  'Hm! She is made of harder stuff!', cursor=17",
     "BRAILLE LINE:  'Hm! She is made of harder stuff! Cardinal Fang! Fetch the COMFY CHAIR! \$l'",
     "     VISIBLE:  'Hm! She is made of harder stuff!', cursor=17",
     "SPEECH OUTPUT: 'Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and surprise. And ruthless efficiency. Our three weapons are fear, surprise, and ruthless efficiency. And an almost fanatical devotion to the Pope. Our four. No. Amongst our weapons. Amongst our weaponry, are such elements as fear, surprise. I'll come in again. NOBODY expects the Spanish Inquisition! Amongst our weaponry are such diverse elements as: fear, surprise, ruthless efficiency, an almost fanatical devotion to the Pope, and nice red uniforms - Oh damn! Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the ungodly. Two last chances. And you shall be free. Three last chances. You have three last chances, the nature of which I have divulged in my previous utterance. Hm! She is made  selected'",
     "SPEECH OUTPUT: 'Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and surprise. And ruthless efficiency. Our three weapons are fear, surprise, and ruthless efficiency. And an almost fanatical devotion to the Pope. Our four. No. Amongst our weapons. Amongst our weaponry, are such elements as fear, surprise. I'll come in again. NOBODY expects the Spanish Inquisition! Amongst our weaponry are such diverse elements as: fear, surprise, ruthless efficiency, an almost fanatical devotion to the Pope, and nice red uniforms - Oh damn! Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the ungodly. Two last chances. And you shall be free. Three last chances. You have three last chances, the nature of which I have divulged in my previous utterance. Hm! She is made  ;  paragraph style Preformatted Text selected'"]))

######################################################################
# 9. Enter Alt-f, Alt-c to close the Writer application.
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
# 10. Enter Alt-f, right arrow and Return, (File->New->Text Document),
#     to get the application back to the state it was in when the
#     test started.
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
# 11. Wait for things to get back to normal.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
