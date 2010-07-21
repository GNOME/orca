# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of HTML blockquote output of Firefox, in particular structural
navigation and where am I.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the local blockquote test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "blockquotes.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Blockquote Regression Test",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

sequence.append(PauseAction(3000))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file", 
    ["BRAILLE LINE:  'On weaponry:'",
     "     VISIBLE:  'On weaponry:', cursor=1",
     "BRAILLE LINE:  'On weaponry:'",
     "     VISIBLE:  'On weaponry:', cursor=1",
     "SPEECH OUTPUT: 'On weaponry:'"]))

########################################################################
# Press Q to move to the first blockquote which begins with: "NOBODY
# expects the Spanish Inquisition!" 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("q"))
sequence.append(utils.AssertPresentationAction(
    "q to first quote", 
    ["BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=1",
     "SPEECH OUTPUT: 'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and'"]))

########################################################################
# Press Q to move to the second blockquote which begins with: "Now
# old lady".
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("q"))
sequence.append(utils.AssertPresentationAction(
    "q to second quote", 
    ["BRAILLE LINE:  'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the ungodly. Two last chances. And you shall'",
     "     VISIBLE:  'Now old lady, you have one last ', cursor=1",
     "SPEECH OUTPUT: 'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the ungodly. Two last chances. And you shall'"]))

########################################################################
# Press Q to move to the third and final blockquote which begins with:
# "Hm! She is made of harder stuff!"
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("q"))
sequence.append(utils.AssertPresentationAction(
    "q to third quote", 
    ["BRAILLE LINE:  'Hm! She is made of harder stuff! Cardinal Fang! Fetch the COMFY CHAIR!'",
     "     VISIBLE:  'Hm! She is made of harder stuff!', cursor=1",
     "SPEECH OUTPUT: 'Hm! She is made of harder stuff! Cardinal Fang! Fetch the COMFY CHAIR!'"]))

########################################################################
# Press Q again.  There are no more blockquotes on this page so we
# should wrap to the top (announce that we've done so) and then move
# to the first blockquote.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("q"))
sequence.append(utils.AssertPresentationAction(
    "q wrap to top", 
    ["BRAILLE LINE:  'Wrapping to top.'",
     "     VISIBLE:  'Wrapping to top.', cursor=0",
     "BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and'",
     "     VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=1",
     "SPEECH OUTPUT: 'Wrapping to top.'",
     "SPEECH OUTPUT: 'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and'"]))

########################################################################
# Press Shift+Q.  There are no more blockquotes above us on the page
#  so we should wrap to the bottom (announce that we've done so) and 
# then move to the third and final blockquote.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>q"))
sequence.append(utils.AssertPresentationAction(
    "Shift+q wrap to bottom", 
    ["BRAILLE LINE:  'Wrapping to bottom.'",
     "     VISIBLE:  'Wrapping to bottom.', cursor=0",
     "BRAILLE LINE:  'Hm! She is made of harder stuff! Cardinal Fang! Fetch the COMFY CHAIR!'",
     "     VISIBLE:  'Hm! She is made of harder stuff!', cursor=1",
     "SPEECH OUTPUT: 'Wrapping to bottom.'",
     "SPEECH OUTPUT: 'Hm! She is made of harder stuff! Cardinal Fang! Fetch the COMFY CHAIR!'"]))

########################################################################
# Press Shift+Q to move to the second blockquote.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>q"))
sequence.append(utils.AssertPresentationAction(
    "Shift+q wrap to second quote", 
    ["BRAILLE LINE:  'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the ungodly. Two last chances. And you shall'",
     "     VISIBLE:  'Now old lady, you have one last ', cursor=1",
     "SPEECH OUTPUT: 'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the ungodly. Two last chances. And you shall'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter. 
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I",
    ["BRAILLE LINE:  'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the ungodly. Two last chances. And you shall'",
     "     VISIBLE:  'Now old lady, you have one last ', cursor=1",
     "SPEECH OUTPUT: 'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the ungodly. Two last chances. And you shall '"]))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "about:blank" and press Return to restore the browser to the
# conditions at the test's start.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
