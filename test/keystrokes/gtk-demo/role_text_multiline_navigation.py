#!/usr/bin/python

"""Test of text output for caret navigation."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Application class"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Return"))

sequence.append(TypeAction("This is a test. "))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("This is only a test."))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("PLEASE DO NOT PANIC."))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction(" "))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("I'm just going to keep on typing."))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("Then, I'm going to type some"))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("more.  I just do not know when to"))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("quit typing."))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("I think I might have spent too much"))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("time in the lab and not enough time"))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("in the wild."))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Left once from end to '.' after 'wild'",
    ["BRAILLE LINE:  'in the wild. $l'",
     "     VISIBLE:  'in the wild. $l', cursor=12",
     "SPEECH OUTPUT: 'dot'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Left a second time to 'd' in 'wild'",
    ["BRAILLE LINE:  'in the wild. $l'",
     "     VISIBLE:  'in the wild. $l', cursor=11",
     "SPEECH OUTPUT: 'd'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Left a third time to 'l' in 'wild'",
    ["BRAILLE LINE:  'in the wild. $l'",
     "     VISIBLE:  'in the wild. $l', cursor=10",
     "SPEECH OUTPUT: 'l'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+Left to beginning of 'wild'",
    ["BRAILLE LINE:  'in the wild. $l'",
     "     VISIBLE:  'in the wild. $l', cursor=8",
     "SPEECH OUTPUT: 'wild.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+Left to beginning of 'the'",
    ["BRAILLE LINE:  'in the wild. $l'",
     "     VISIBLE:  'in the wild. $l', cursor=4",
     "SPEECH OUTPUT: 'the '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+Left to beginning of 'in'",
    ["BRAILLE LINE:  'in the wild. $l'",
     "     VISIBLE:  'in the wild. $l', cursor=1",
     "SPEECH OUTPUT: 'in '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+Left to beginning of 'time' at end of previous line",
    ["BRAILLE LINE:  'time in the lab and not enough time $l'",
     "     VISIBLE:  'time in the lab and not enough t', cursor=32",
     "SPEECH OUTPUT: 'newline'",
     "SPEECH OUTPUT: 'time",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Home"))
sequence.append(utils.AssertPresentationAction(
    "Home to beginning of line",
    ["BRAILLE LINE:  'time in the lab and not enough time $l'",
     "     VISIBLE:  'time in the lab and not enough t', cursor=1",
     "SPEECH OUTPUT: 't'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("End"))
sequence.append(utils.AssertPresentationAction(
    "End to end of line",
    ["BRAILLE LINE:  'time in the lab and not enough time $l'",
     "     VISIBLE:  ' in the lab and not enough time ', cursor=32",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+Home to beginning of document",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame This is a test.  $l'",
     "     VISIBLE:  'This is a test.  $l', cursor=1",
     "SPEECH OUTPUT: 'This is a test. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>End"))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+End to end of document",
    ["BRAILLE LINE:  'in the wild. $l'",
     "     VISIBLE:  'in the wild. $l', cursor=13",
     "SPEECH OUTPUT: 'in the wild.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+Home back to beginning of document",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame This is a test.  $l'",
     "     VISIBLE:  'This is a test.  $l', cursor=1",
     "SPEECH OUTPUT: 'This is a test. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Right once to 'h' in 'This'",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame This is a test.  $l'",
     "     VISIBLE:  'This is a test.  $l', cursor=2",
     "SPEECH OUTPUT: 'h'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Right a second time to 'i' in 'This'",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame This is a test.  $l'",
     "     VISIBLE:  'This is a test.  $l', cursor=3",
     "SPEECH OUTPUT: 'i'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Right a third time to 's' in 'This'",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame This is a test.  $l'",
     "     VISIBLE:  'This is a test.  $l', cursor=4",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+Right to end of 'This'",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame This is a test.  $l'",
     "     VISIBLE:  'This is a test.  $l', cursor=5",
     "SPEECH OUTPUT: 'newline'",
     "SPEECH OUTPUT: 'This '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+Right to end of 'is'",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame This is a test.  $l'",
     "     VISIBLE:  'This is a test.  $l', cursor=8",
     "SPEECH OUTPUT: 'is '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+Right to end of 'a'",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame This is a test.  $l'",
     "     VISIBLE:  'This is a test.  $l', cursor=10",
     "SPEECH OUTPUT: 'a '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Down a line to 'n' in 'only'",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=10",
     "SPEECH OUTPUT: 'This is only a test.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("End"))
sequence.append(utils.AssertPresentationAction(
    "End of line",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=21",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Right to blank line",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Right to beginning of 'PLEASE'",
    ["BRAILLE LINE:  'PLEASE DO NOT PANIC. $l'",
     "     VISIBLE:  'PLEASE DO NOT PANIC. $l', cursor=1",
     "SPEECH OUTPUT: 'P'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Down to line with one space",
    ["BRAILLE LINE:  '  $l'",
     "     VISIBLE:  '  $l', cursor=1",
     "SPEECH OUTPUT: ' '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Back up to 'PLEASE DO NOT PANIC.'",
    ["BRAILLE LINE:  'PLEASE DO NOT PANIC. $l'",
     "     VISIBLE:  'PLEASE DO NOT PANIC. $l', cursor=1",
     "SPEECH OUTPUT: 'PLEASE DO NOT PANIC.' voice=uppercase"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+Right over PLEASE",
    ["BRAILLE LINE:  'PLEASE DO NOT PANIC. $l'",
     "     VISIBLE:  'PLEASE DO NOT PANIC. $l', cursor=7",
     "SPEECH OUTPUT: 'PLEASE '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+Left over PLEASE",
    ["BRAILLE LINE:  'PLEASE DO NOT PANIC. $l'",
     "     VISIBLE:  'PLEASE DO NOT PANIC. $l', cursor=1",
     "SPEECH OUTPUT: 'PLEASE '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(TypeAction("f"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Insert+f for text attributes",
    ["SPEECH OUTPUT: 'size 11' voice=system",
     "SPEECH OUTPUT: 'family name Cantarell' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "Left to blank line",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "Right to beginning of 'PLEASE' again",
    ["BRAILLE LINE:  'PLEASE DO NOT PANIC. $l'",
     "     VISIBLE:  'PLEASE DO NOT PANIC. $l', cursor=1",
     "SPEECH OUTPUT: 'P'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Up to blank line",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+Home to beginning of document",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame This is a test.  $l'",
     "     VISIBLE:  'This is a test.  $l', cursor=1",
     "SPEECH OUTPUT: 'This is a test. '"]))

# [[[NOTE: WDW - with orca.settings.asyncMode=False, which is what
# the regression tests use, the Delete will not give the same output
# as what we see when orca.settings.asyncMode=True (the normal 
# operating behavior).  See the NOTE in default.py:onTextDeleted 
# for an explanation. We include the synchronous output here.]]]
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Delete"))
sequence.append(utils.AssertPresentationAction(
    "Delete right 'T' in 'This'",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame his is a test.  $l'",
     "     VISIBLE:  'his is a test.  $l', cursor=1",
     "SPEECH OUTPUT: 'h'"]))

# [[[NOTE: WDW - with orca.settings.asyncMode=False, which is what
# the regression tests use, the Delete will not give the same output
# as what we see when orca.settings.asyncMode=True (the normal 
# operating behavior).  See the NOTE in default.py:onTextDeleted 
# for an explanation. We include the synchronous output here.]]]
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Delete"))
sequence.append(utils.AssertPresentationAction(
    "Delete right 'h' in 'his'",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame is is a test.  $l'",
     "     VISIBLE:  'is is a test.  $l', cursor=1",
     "SPEECH OUTPUT: 'i'"]))

# [[[NOTE: WDW - with orca.settings.asyncMode=False, which is what
# the regression tests use, the Delete will not give the same output
# as what we see when orca.settings.asyncMode=True (the normal 
# operating behavior).  See the NOTE in default.py:onTextDeleted 
# for an explanation. We include the synchronous output here.]]]
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Delete"))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+Delete right remaining 'is' of 'This'",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame  is a test.  $l'",
     "     VISIBLE:  ' is a test.  $l', cursor=1",
     "SPEECH OUTPUT: 'space'"]))

# [[[NOTE: WDW - with orca.settings.asyncMode=False, which is what
# the regression tests use, the Delete will not give the same output
# as what we see when orca.settings.asyncMode=True (the normal 
# operating behavior).  See the NOTE in default.py:onTextDeleted 
# for an explanation. We include the synchronous output here.]]]
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Delete"))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+Delete right 'is'",
    ["BRAILLE LINE:  'gtk3-demo-application application Application Class frame  a test.  $l'",
     "     VISIBLE:  ' a test.  $l', cursor=1",
     "SPEECH OUTPUT: 'space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Down a line",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "SPEECH OUTPUT: 'This is only a test.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("End"))
sequence.append(utils.AssertPresentationAction(
    "End of line",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=21",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("BackSpace"))
sequence.append(utils.AssertPresentationAction(
    "BackSpace '.' after 'test'",
    ["BRAILLE LINE:  'This is only a test $l'",
     "     VISIBLE:  'This is only a test $l', cursor=20",
     "SPEECH OUTPUT: 'dot'"]))

# [[[NOTE: WDW - with orca.settings.asyncMode=False, which is what
# the regression tests use, the BackSpace will not give the same output
# as what we see when orca.settings.asyncMode=True (the normal 
# operating behavior).  See the NOTE in default.py:onTextDeleted 
# for an explanation. We include the synchronous output here.]]]
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>BackSpace"))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+BackSpace to delete 'this'",
    ["BRAILLE LINE:  'This is only a  $l'",
     "     VISIBLE:  'This is only a  $l', cursor=16",
     "BRAILLE LINE:  'This is only a  $l'",
     "     VISIBLE:  'This is only a  $l', cursor=16",
     "SPEECH OUTPUT: 'test'"]))

# [[[NOTE: WDW - with orca.settings.asyncMode=False, which is what
# the regression tests use, the BackSpace will not give the same output
# as what we see when orca.settings.asyncMode=True (the normal 
# operating behavior).  See the NOTE in default.py:onTextDeleted 
# for an explanation. We include the synchronous output here.]]]
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>BackSpace"))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+BackSpace to delete 'a'",
    ["BRAILLE LINE:  'This is only  $l'",
     "     VISIBLE:  'This is only  $l', cursor=14",
     "SPEECH OUTPUT: 'a '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+Left to beginning of 'only'",
    ["BRAILLE LINE:  'This is only  $l'",
     "     VISIBLE:  'This is only  $l', cursor=9",
     "SPEECH OUTPUT: 'newline'",
     "SPEECH OUTPUT: 'only ",
     "",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+Left to beginning of 'is'",
    ["BRAILLE LINE:  'This is only  $l'",
     "     VISIBLE:  'This is only  $l', cursor=6",
     "SPEECH OUTPUT: 'is '"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
