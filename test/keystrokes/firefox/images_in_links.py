#!/usr/bin/python

"""Test of line navigation output of Firefox with links that contain
images.
"""

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

sequence.append(TypeAction(utils.htmlURLPrefix + "images-in-links.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

sequence.append(WaitForFocus("Test",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file",
    ["BRAILLE LINE:  'One image with alt text in a link: Orca logo Image'",
     "     VISIBLE:  'One image with alt text in a lin', cursor=1",
     "SPEECH OUTPUT: 'One image with alt text in a link: Orca logo link image'"]))

########################################################################
# Down Arrow to the End.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. line Down",
    ["BRAILLE LINE:  'One image with title attribute in a link: Orca logo showing a whale holding a white cane Image'",
     "     VISIBLE:  'One image with title attribute i', cursor=1",
     "SPEECH OUTPUT: 'One image with title attribute in a link: Orca logo showing a whale holding a white cane link image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. line Down",
    ["BRAILLE LINE:  'One image with both alt text and title attribute in a link: Orca logo Image'",
     "     VISIBLE:  'One image with both alt text and', cursor=1",
     "SPEECH OUTPUT: 'One image with both alt text and title attribute in a link: Orca logo link image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. line Down",
    ["BRAILLE LINE:  'One \"useless\" image in a link: foo Image'",
     "     VISIBLE:  'One \"useless\" image in a link: f', cursor=1",
     "SPEECH OUTPUT: 'One \"useless\" image in a link: foo link image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. line Down",
    ["BRAILLE LINE:  'Two \"useless\" images in a link: foo Image foo Image'",
     "     VISIBLE:  'Two \"useless\" images in a link: ', cursor=1",
     "SPEECH OUTPUT: 'Two \"useless\" images in a link: foo link image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5a. line Down",
    ["BRAILLE LINE:  'Two \"useless\" images in a paragraph that is inside of a link: foo'",
     "     VISIBLE:  'Two \"useless\" images in a paragr', cursor=1",
     "SPEECH OUTPUT: 'Two \"useless\" images in a paragraph that is inside of a link: foo link"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5b. line Down",
    ["BUG? - Why are we repeating ourselves here?",
     "BRAILLE LINE:  'foo Image'",
     "     VISIBLE:  'foo Image', cursor=1",
     "BRAILLE LINE:  'foo Image'",
     "     VISIBLE:  'foo Image', cursor=1",
     "SPEECH OUTPUT: 'foo link image'",
     "SPEECH OUTPUT: 'foo link image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. line Down",
    ["BRAILLE LINE:  'One \"useless\" image and one \"useful\" image in a link: Orca logo Image foo Image'",
     "     VISIBLE:  'One \"useless\" image and one \"use', cursor=1",
     "SPEECH OUTPUT: 'One \"useless\" image and one \"useful\" image in a link: Orca logo link image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. line Down",
    ["BUG? - Why are we silent here?"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. line Down",
    ["BRAILLE LINE:  'Two \"useless\" images in a paragraph that is inside of a link along with text that is not in the paragraph: Before the paragraph'",
     "     VISIBLE:  'Two \"useless\" images in a paragr', cursor=1",
     "SPEECH OUTPUT: 'Two \"useless\" images in a paragraph that is inside of a link along with text that is not in the paragraph: Before the paragraph link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. line Down",
    ["BRAILLE LINE:  'foo Image'",
     "     VISIBLE:  'foo Image', cursor=1",
     "BRAILLE LINE:  'foo Image'",
     "     VISIBLE:  'foo Image', cursor=1",
     "SPEECH OUTPUT: 'foo link image'",
     "SPEECH OUTPUT: 'foo link image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. line Down",
    ["BRAILLE LINE:  'After the paragraph'",
     "     VISIBLE:  'After the paragraph', cursor=1",
     "SPEECH OUTPUT: 'After the paragraph link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. line Down",
    ["BRAILLE LINE:  'Two \"useless\" images and some additional text in a paragraph that is inside of a link along with text that is not in the paragraph: Before the paragraph'",
     "     VISIBLE:  'Two \"useless\" images and some ad', cursor=1",
     "SPEECH OUTPUT: 'Two \"useless\" images and some additional text in a paragraph that is inside of a link along with text that is not in the paragraph: Before the paragraph link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. line Down",
    ["BUG? - Why are we silent here?"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "13. line Down",
    ["BRAILLE LINE:  'After the paragraph'",
     "     VISIBLE:  'After the paragraph', cursor=1",
     "SPEECH OUTPUT: 'After the paragraph link'"]))

########################################################################
# Shift+Tab to give focus to each link.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Tab"))
sequence.append(utils.AssertPresentationAction(
    "0a. Shift+Tab",
    ["BRAILLE LINE:  'foo Image'",
     "     VISIBLE:  'foo Image', cursor=1",
     "SPEECH OUTPUT: 'silly link link image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Tab"))
sequence.append(utils.AssertPresentationAction(
    "0b. Shift+Tab",
    ["BRAILLE LINE:  'Two \"useless\" images and some additional text in a paragraph that is inside of a link along with text that is not in the paragraph: Before the paragraph'",
     "     VISIBLE:  'Before the paragraph', cursor=1",
     "SPEECH OUTPUT: 'Before the paragraph link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Tab"))
sequence.append(utils.AssertPresentationAction(
    "0c. Shift+Tab",
    ["BRAILLE LINE:  'After the paragraph'",
     "     VISIBLE:  'After the paragraph', cursor=1",
     "SPEECH OUTPUT: 'After the paragraph link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Tab"))
sequence.append(utils.AssertPresentationAction(
    "1. Shift+Tab",
    ["BRAILLE LINE:  'foo Image'",
     "     VISIBLE:  'foo Image', cursor=1",
     "SPEECH OUTPUT: 'foo link image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Tab"))
sequence.append(utils.AssertPresentationAction(
    "2. Shift+Tab",
    ["BRAILLE LINE:  'Two \"useless\" images in a paragraph that is inside of a link along with text that is not in the paragraph: Before the paragraph'",
     "     VISIBLE:  'Before the paragraph', cursor=1",
     "SPEECH OUTPUT: 'Before the paragraph link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Tab"))
sequence.append(utils.AssertPresentationAction(
    "3. Shift+Tab",
    ["BRAILLE LINE:  'foo Image'",
     "     VISIBLE:  'foo Image', cursor=1",
     "SPEECH OUTPUT: 'silly link link image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Tab"))
sequence.append(utils.AssertPresentationAction(
    "4. Shift+Tab",
    ["BRAILLE LINE:  'Orca logo Image'",
     "     VISIBLE:  'Orca logo Image', cursor=1",
     "SPEECH OUTPUT: 'Orca logo link image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Tab"))
sequence.append(utils.AssertPresentationAction(
    "5. Shift+Tab",
    ["BRAILLE LINE:  'foo Image'",
     "     VISIBLE:  'foo Image', cursor=1",
     "SPEECH OUTPUT: 'foo link image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Tab"))
sequence.append(utils.AssertPresentationAction(
    "6. Shift+Tab",
    ["BRAILLE LINE:  'foo'",
     "     VISIBLE:  'foo', cursor=1",
     "SPEECH OUTPUT: 'foo link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Tab"))
sequence.append(utils.AssertPresentationAction(
    "7. Shift+Tab",
    ["BRAILLE LINE:  'foo Image'",
     "     VISIBLE:  'foo Image', cursor=1",
     "SPEECH OUTPUT: 'foo link image'"]))

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
