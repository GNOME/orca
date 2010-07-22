#!/usr/bin/python

"""Test of line navigation output of Firefox on a page with a simple
form.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the local "simple form" test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "simpleform.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

sequence.append(WaitForFocus(utils.htmlURLPrefix + "simpleform.html",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file",
    ["BRAILLE LINE:  'Type something here:  $l'",
     "     VISIBLE:  'Type something here:  $l', cursor=1",
     "SPEECH OUTPUT: 'Type something here: text'"]))

########################################################################
# Press Tab to reach the multi-line entry. Then select all the text and
# delete it.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("<Control>a"))
sequence.append(KeyComboAction("Delete"))

sequence.append(PauseAction(3000))

########################################################################
# Type some text with misspelled words.
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("Thiss is a tesst. "))
sequence.append(utils.AssertPresentationAction(
    "Type a sentence with mistakes",
    ["BRAILLE LINE:  'T $l'",
     "     VISIBLE:  'T $l', cursor=2",
     "BRAILLE LINE:  'T $l'",
     "     VISIBLE:  'T $l', cursor=2",
     "BRAILLE LINE:  'T $l'",
     "     VISIBLE:  'T $l', cursor=2",
     "BRAILLE LINE:  'Th $l'",
     "     VISIBLE:  'Th $l', cursor=3",
     "BRAILLE LINE:  'Th $l'",
     "     VISIBLE:  'Th $l', cursor=3",
     "BRAILLE LINE:  'Thi $l'",
     "     VISIBLE:  'Thi $l', cursor=4",
     "BRAILLE LINE:  'Thi $l'",
     "     VISIBLE:  'Thi $l', cursor=4",
     "BRAILLE LINE:  'This $l'",
     "     VISIBLE:  'This $l', cursor=5",
     "BRAILLE LINE:  'This $l'",
     "     VISIBLE:  'This $l', cursor=5",
     "BRAILLE LINE:  'Thiss $l'",
     "     VISIBLE:  'Thiss $l', cursor=6",
     "BRAILLE LINE:  'Thiss $l'",
     "     VISIBLE:  'Thiss $l', cursor=6",
     "BRAILLE LINE:  'Thiss  $l'",
     "     VISIBLE:  'Thiss  $l', cursor=7",
     "BRAILLE LINE:  'Thiss  $l'",
     "     VISIBLE:  'Thiss  $l', cursor=7",
     "BRAILLE LINE:  'Thiss i $l'",
     "     VISIBLE:  'Thiss i $l', cursor=8",
     "BRAILLE LINE:  'Thiss i $l'",
     "     VISIBLE:  'Thiss i $l', cursor=8",
     "BRAILLE LINE:  'Thiss is $l'",
     "     VISIBLE:  'Thiss is $l', cursor=9",
     "BRAILLE LINE:  'Thiss is $l'",
     "     VISIBLE:  'Thiss is $l', cursor=9",
     "BRAILLE LINE:  'Thiss is  $l'",
     "     VISIBLE:  'Thiss is  $l', cursor=10",
     "BRAILLE LINE:  'Thiss is  $l'",
     "     VISIBLE:  'Thiss is  $l', cursor=10",
     "BRAILLE LINE:  'Thiss is a $l'",
     "     VISIBLE:  'Thiss is a $l', cursor=11",
     "BRAILLE LINE:  'Thiss is a $l'",
     "     VISIBLE:  'Thiss is a $l', cursor=11",
     "BRAILLE LINE:  'Thiss is a  $l'",
     "     VISIBLE:  'Thiss is a  $l', cursor=12",
     "BRAILLE LINE:  'Thiss is a  $l'",
     "     VISIBLE:  'Thiss is a  $l', cursor=12",
     "BRAILLE LINE:  'Thiss is a t $l'",
     "     VISIBLE:  'Thiss is a t $l', cursor=13",
     "BRAILLE LINE:  'Thiss is a t $l'",
     "     VISIBLE:  'Thiss is a t $l', cursor=13",
     "BRAILLE LINE:  'Thiss is a te $l'",
     "     VISIBLE:  'Thiss is a te $l', cursor=14",
     "BRAILLE LINE:  'Thiss is a te $l'",
     "     VISIBLE:  'Thiss is a te $l', cursor=14",
     "BRAILLE LINE:  'Thiss is a tes $l'",
     "     VISIBLE:  'Thiss is a tes $l', cursor=15",
     "BRAILLE LINE:  'Thiss is a tes $l'",
     "     VISIBLE:  'Thiss is a tes $l', cursor=15",
     "BRAILLE LINE:  'Thiss is a tess $l'",
     "     VISIBLE:  'Thiss is a tess $l', cursor=16",
     "BRAILLE LINE:  'Thiss is a tess $l'",
     "     VISIBLE:  'Thiss is a tess $l', cursor=16",
     "BRAILLE LINE:  'Thiss is a tesst $l'",
     "     VISIBLE:  'Thiss is a tesst $l', cursor=17",
     "BRAILLE LINE:  'Thiss is a tesst $l'",
     "     VISIBLE:  'Thiss is a tesst $l', cursor=17",
     "BRAILLE LINE:  'Thiss is a tesst. $l'",
     "     VISIBLE:  'Thiss is a tesst. $l', cursor=18",
     "BRAILLE LINE:  'Thiss is a tesst. $l'",
     "     VISIBLE:  'Thiss is a tesst. $l', cursor=18",
     "BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=19",
     "BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=19",
     "SPEECH OUTPUT: 'misspelled'",
     "SPEECH OUTPUT: 'misspelled'"]))

########################################################################
# Left Arrow through the text.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "1. Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=18",
     "SPEECH OUTPUT: 'space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "2. Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=17",
     "SPEECH OUTPUT: 'dot'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "3. Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=16",
     "SPEECH OUTPUT: 'misspelled'",
     "SPEECH OUTPUT: 't'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "4. Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=15",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "5. Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=14",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "6. Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=13",
     "SPEECH OUTPUT: 'e'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "7. Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=12",
     "SPEECH OUTPUT: 't'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "8. Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=11",
     "SPEECH OUTPUT: 'space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "9. Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=10",
     "SPEECH OUTPUT: 'a'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "10. Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=9",
     "SPEECH OUTPUT: 'space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "11. Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=8",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "12. Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=7",
     "SPEECH OUTPUT: 'i'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "13. Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=6",
     "SPEECH OUTPUT: 'space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "14. Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=5",
     "SPEECH OUTPUT: 'misspelled'",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "15. Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=4",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "16. Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=3",
     "SPEECH OUTPUT: 'i'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "17. Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=2",
     "SPEECH OUTPUT: 'h'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "18. Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=1",
     "SPEECH OUTPUT: 'T'"]))

########################################################################
# Right Arrow through the text.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "1. Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=2",
     "SPEECH OUTPUT: 'h'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "2. Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=3",
     "SPEECH OUTPUT: 'i'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "3. Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=4",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "4. Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=5",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "5. Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=6",
     "SPEECH OUTPUT: 'space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "6. Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=7",
     "SPEECH OUTPUT: 'i'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "7. Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=8",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "8. Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=9",
     "SPEECH OUTPUT: 'space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "9. Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=10",
     "SPEECH OUTPUT: 'a'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "10. Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=11",
     "SPEECH OUTPUT: 'space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "11. Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=12",
     "SPEECH OUTPUT: 'misspelled'",
     "SPEECH OUTPUT: 't'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "12. Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=13",
     "SPEECH OUTPUT: 'e'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "13. Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=14",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "14. Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=15",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "15. Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=16",
     "SPEECH OUTPUT: 't'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "16. Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=17",
     "SPEECH OUTPUT: 'dot'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "17. Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=18",
     "SPEECH OUTPUT: 'space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "18. Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=19",
     "SPEECH OUTPUT: 'blank'"]))

########################################################################
# Control+Left Arrow through the text.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "1. Control Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=12",
     "SPEECH OUTPUT: 'misspelled'",
     "SPEECH OUTPUT: 'tesst. ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "2. Control Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=10",
     "SPEECH OUTPUT: 'a '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "3. Control Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=7",
     "SPEECH OUTPUT: 'is '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "4. Control Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=1",
     "SPEECH OUTPUT: 'misspelled'",
     "SPEECH OUTPUT: 'Thiss '"]))

########################################################################
# Get the formatting of this word (which is misspelled)
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("f"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Insert+f",
    ["SPEECH OUTPUT: 'size 9pt'",
     "SPEECH OUTPUT: 'family name monospace'",
     "SPEECH OUTPUT: 'mistake spelling'"]))

########################################################################
# Control+Right Arrow through the text.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "1. Control Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=6",
     "SPEECH OUTPUT: 'Thiss '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "2. Control Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=9",
     "SPEECH OUTPUT: 'is '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "3. Control Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=11",
     "SPEECH OUTPUT: 'a '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "4. Control Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=18",
     "SPEECH OUTPUT: 'misspelled'",
     "SPEECH OUTPUT: 'tesst. ",
     "'"]))

########################################################################
# Get the formatting of this word (which is not misspelled)
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("f"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Insert+f",
    ["SPEECH OUTPUT: 'size 9pt'",
     "SPEECH OUTPUT: 'family name monospace'"]))

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
