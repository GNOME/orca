#!/usr/bin/python

"""Test of line navigation output of Firefox on a page with an
imagemap.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the local "backwards" test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

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
# Down Arrow to the End.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(PauseAction(1000))
sequence.append(utils.AssertPresentationAction(
    "1. line Down",
    ["BUG? - For some reason we're repeating ourselves",
     "BRAILLE LINE:  'Test: z Link y Link x Link w Link v Link u Link t Link s Link r Link q Link p Link o Link n Link m Link l Link k Link j Link i Link h Link g Link f Link e Link d Link c Link b Link a Link'",
     "     VISIBLE:  'Test: z Link y Link x Link w Lin', cursor=1",
     "BRAILLE LINE:  'Test: z Link y Link x Link w Link v Link u Link t Link s Link r Link q Link p Link o Link n Link m Link l Link k Link j Link i Link h Link g Link f Link e Link d Link c Link b Link a Link'",
     "     VISIBLE:  'Test: z Link y Link x Link w Lin', cursor=1",
     "SPEECH OUTPUT: 'Test: z link y link x link w link v link u link t link s link r link q link p link o link n link m link l link k link j link i link h link g link f link e link d link c link b link a link'",
     "SPEECH OUTPUT: 'Test: z link y link x link w link v link u link t link s link r link q link p link o link n link m link l link k link j link i link h link g link f link e link d link c link b link a link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. line Down",
    ["BRAILLE LINE:  'Here is some text.'",
     "     VISIBLE:  'Here is some text.', cursor=1",
     "SPEECH OUTPUT: 'Here is some text.'"]))

########################################################################
# Up Arrow to the Top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "1. line Up",
    ["BRAILLE LINE:  'Test: z Link y Link x Link w Link v Link u Link t Link s Link r Link q Link p Link o Link n Link m Link l Link k Link j Link i Link h Link g Link f Link e Link d Link c Link b Link a Link'",
     "     VISIBLE:  'Test: z Link y Link x Link w Lin', cursor=1",
     "SPEECH OUTPUT: 'Test: z link y link x link w link v link u link t link s link r link q link p link o link n link m link l link k link j link i link h link g link f link e link d link c link b link a link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "2. line Up",
    ["BRAILLE LINE:  'This looks like A to Z, but it's really Z to A.'",
     "     VISIBLE:  'This looks like A to Z, but it's', cursor=1",
     "SPEECH OUTPUT: 'This looks like A to Z, but it's really Z to A.'"]))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "about:blank" and press Return to restore the browser to the
# conditions at the test's start.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
