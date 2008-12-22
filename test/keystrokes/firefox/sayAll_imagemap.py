#!/usr/bin/python

"""Test of sayAll output of Firefox on a page with an imagemap."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the local "backwards" test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "backwards.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

sequence.append(WaitForFocus("Backwards Stuff",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file",
    ["BRAILLE LINE:  'This looks like A to Z, but it's really Z to A.'",
     "     VISIBLE:  'This looks like A to Z, but it's', cursor=1",
     "SPEECH OUTPUT: 'This looks like A to Z, but it's really Z to A.'"]))

########################################################################
# SayAll to the End.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Add"))
sequence.append(utils.AssertPresentationAction(
    "KP_Add to do a SayAll",
    ["SPEECH OUTPUT: 'This looks like A to Z, but it's really Z to A.'",
     "SPEECH OUTPUT: 'Test:'",
     "SPEECH OUTPUT: 'z link'",
     "SPEECH OUTPUT: 'y link'",
     "SPEECH OUTPUT: 'x link'",
     "SPEECH OUTPUT: 'w link'",
     "SPEECH OUTPUT: 'v link'",
     "SPEECH OUTPUT: 'u link'",
     "SPEECH OUTPUT: 't link'",
     "SPEECH OUTPUT: 's link'",
     "SPEECH OUTPUT: 'r link'",
     "SPEECH OUTPUT: 'q link'",
     "SPEECH OUTPUT: 'p link'",
     "SPEECH OUTPUT: 'o link'",
     "SPEECH OUTPUT: 'n link'",
     "SPEECH OUTPUT: 'm link'",
     "SPEECH OUTPUT: 'l link'",
     "SPEECH OUTPUT: 'k link'",
     "SPEECH OUTPUT: 'j link'",
     "SPEECH OUTPUT: 'i link'",
     "SPEECH OUTPUT: 'h link'",
     "SPEECH OUTPUT: 'g link'",
     "SPEECH OUTPUT: 'f link'",
     "SPEECH OUTPUT: 'e link'",
     "SPEECH OUTPUT: 'd link'",
     "SPEECH OUTPUT: 'c link'",
     "SPEECH OUTPUT: 'b link'",
     "SPEECH OUTPUT: 'a link'",
     "SPEECH OUTPUT: 'Here is some text.'",
     "SPEECH OUTPUT: 'Safeway had some interesting (and problematic) image maps. I didn't steal the images, but if you tab and look at the status bar, you should be able to see the URI for each region. We should also be speaking and brailling it correctly now -- at least as best as we can given what they gave us.'",
     "SPEECH OUTPUT: 'wk09_frozenmovie link image'",
     "SPEECH OUTPUT: 'www.vons.com link www.dominicks.com link www.randalls.com link www.tomthumb.com link www.genuardis.com link www.pavilions.com link www.carrsqc.com link'"]))

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
