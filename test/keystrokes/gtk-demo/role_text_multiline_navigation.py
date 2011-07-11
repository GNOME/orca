#!/usr/bin/python

"""Test of general text navigation using caret navigation and flat review 
techniques.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))

########################################################################
# Once gtk-demo is running, invoke the Application Main Window demo
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Application main window", 1000))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# When the demo comes up, go to the text area and type.
#
#sequence.append(WaitForWindowActivate("Application Window",None))
sequence.append(WaitForFocus("Open", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))

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

sequence.append(PauseAction(3000))

########################################################################
# Do a bunch of navigation
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Left once from end to '.' after 'wild'",
    ["KNOWN ISSUE - Sometimes we double update braille here; other times we do not.",
     "BRAILLE LINE:  'in the wild. $l'",
     "     VISIBLE:  'in the wild. $l', cursor=12",
     "BRAILLE LINE:  'in the wild. $l'",
     "     VISIBLE:  'in the wild. $l', cursor=12",
     "SPEECH OUTPUT: 'dot'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Left a second time to 'd' in 'wild'",
    ["BRAILLE LINE:  'in the wild. $l'",
     "     VISIBLE:  'in the wild. $l', cursor=11",
     "SPEECH OUTPUT: 'd'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Left a third time to 'l' in 'wild'",
    ["BRAILLE LINE:  'in the wild. $l'",
     "     VISIBLE:  'in the wild. $l', cursor=10",
     "SPEECH OUTPUT: 'l'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+Left to beginning of 'wild'",
    ["BRAILLE LINE:  'in the wild. $l'",
     "     VISIBLE:  'in the wild. $l', cursor=8",
     "SPEECH OUTPUT: 'wild.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+Left to beginning of 'the'",
    ["BRAILLE LINE:  'in the wild. $l'",
     "     VISIBLE:  'in the wild. $l', cursor=4",
     "SPEECH OUTPUT: 'the '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+Left to beginning of 'in'",
    ["BRAILLE LINE:  'in the wild. $l'",
     "     VISIBLE:  'in the wild. $l', cursor=1",
     "SPEECH OUTPUT: 'in '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+Left to beginning of 'time' at end of previous line",
    ["BRAILLE LINE:  'time in the lab and not enough time $l'",
     "     VISIBLE:  'time in the lab and not enough t', cursor=32",
     "SPEECH OUTPUT: 'newline'",
     "SPEECH OUTPUT: 'time",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Home"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Home to beginning of line",
    ["BRAILLE LINE:  'time in the lab and not enough time $l'",
     "     VISIBLE:  'time in the lab and not enough t', cursor=1",
     "SPEECH OUTPUT: 't'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("End"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "End to end of line",
    ["BRAILLE LINE:  'time in the lab and not enough time $l'",
     "     VISIBLE:  ' in the lab and not enough time ', cursor=32",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+Home to beginning of document",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a test.  $l'",
     "     VISIBLE:  'This is a test.  $l', cursor=1",
     "SPEECH OUTPUT: 'This is a test. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>End"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+End to end of document",
    ["BRAILLE LINE:  'in the wild. $l'",
     "     VISIBLE:  'in the wild. $l', cursor=13",
     "SPEECH OUTPUT: 'in the wild.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+Home back to beginning of document",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a test.  $l'",
     "     VISIBLE:  'This is a test.  $l', cursor=1",
     "SPEECH OUTPUT: 'This is a test. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Right once to 'h' in 'This'",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a test.  $l'",
     "     VISIBLE:  'This is a test.  $l', cursor=2",
     "SPEECH OUTPUT: 'h'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Right a second time to 'i' in 'This'",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a test.  $l'",
     "     VISIBLE:  'This is a test.  $l', cursor=3",
     "SPEECH OUTPUT: 'i'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Right a third time to 's' in 'This'",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a test.  $l'",
     "     VISIBLE:  'This is a test.  $l', cursor=4",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+Right to end of 'This'",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a test.  $l'",
     "     VISIBLE:  'This is a test.  $l', cursor=5",
     "SPEECH OUTPUT: 'newline'",
     "SPEECH OUTPUT: 'This '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+Right to end of 'is'",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a test.  $l'",
     "     VISIBLE:  'This is a test.  $l', cursor=8",
     "SPEECH OUTPUT: 'is '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+Right to end of 'a'",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a test.  $l'",
     "     VISIBLE:  'This is a test.  $l', cursor=10",
     "SPEECH OUTPUT: 'a '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Down a line to 'n' in 'only'",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=10",
     "SPEECH OUTPUT: 'This is only a test.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("End"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "End of line",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=21",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Right to blank line",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Right to beginning of 'PLEASE'",
    ["BRAILLE LINE:  'PLEASE DO NOT PANIC. $l'",
     "     VISIBLE:  'PLEASE DO NOT PANIC. $l', cursor=1",
     "SPEECH OUTPUT: 'P'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Subtract"))
sequence.append(utils.AssertPresentationAction(
    "KP_Subtract to enter flat review",
    ["BRAILLE LINE:  'Entering flat review.'",
     "     VISIBLE:  'Entering flat review.', cursor=0",
     "BRAILLE LINE:  'PLEASE DO NOT PANIC. $l'",
     "     VISIBLE:  'PLEASE DO NOT PANIC. $l', cursor=1",
     "SPEECH OUTPUT: 'Entering flat review.'",
     "SPEECH OUTPUT: 'PLEASE' voice=uppercase"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "KP_8 to flat review 'PLEASE DO NOT PANIC.'",
    ["BRAILLE LINE:  'PLEASE DO NOT PANIC. $l'",
     "     VISIBLE:  'PLEASE DO NOT PANIC. $l', cursor=1",
     "SPEECH OUTPUT: 'PLEASE DO NOT PANIC.",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "KP_5 to flat review 'PLEASE'",
    ["BRAILLE LINE:  'PLEASE DO NOT PANIC. $l'",
     "     VISIBLE:  'PLEASE DO NOT PANIC. $l', cursor=1",
     "SPEECH OUTPUT: 'PLEASE'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_2"))
sequence.append(utils.AssertPresentationAction(
    "KP_2 to flat review 'P'",
    ["BRAILLE LINE:  'PLEASE DO NOT PANIC. $l'",
     "     VISIBLE:  'PLEASE DO NOT PANIC. $l', cursor=1",
     "SPEECH OUTPUT: 'P'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Down to line with one space",
    ["BUG? For some reason we are presenting other things here",
     "BRAILLE LINE:  '  $l'",
     "     VISIBLE:  '  $l', cursor=1",
     "BRAILLE LINE:  '  $l'",
     "     VISIBLE:  '  $l', cursor=1",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame'",
     "     VISIBLE:  'Application Window Frame', cursor=1",
     "BRAILLE LINE:  '  $l'",
     "     VISIBLE:  '  $l', cursor=1",
     "SPEECH OUTPUT: ' '",
     "SPEECH OUTPUT: 'Application Window frame'",
     "SPEECH OUTPUT: 'text  '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "KP_8 to flat review ' '",
    ["BRAILLE LINE:  '  $l'",
     "     VISIBLE:  '  $l', cursor=1",
     "SPEECH OUTPUT: 'white space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "KP_5 to flat review ' '",
    ["BRAILLE LINE:  '  $l'",
     "     VISIBLE:  '  $l', cursor=1",
     "SPEECH OUTPUT: 'white space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_2"))
sequence.append(utils.AssertPresentationAction(
    "KP_2 to flat review ' '",
    ["BRAILLE LINE:  '  $l'",
     "     VISIBLE:  '  $l', cursor=1",
     "SPEECH OUTPUT: 'space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Back up to 'PLEASE DO NOT PANIC.'",
    ["BUG? For some reason we are presenting other things here",
     "BRAILLE LINE:  'PLEASE DO NOT PANIC. $l'",
     "     VISIBLE:  'PLEASE DO NOT PANIC. $l', cursor=1",
     "BRAILLE LINE:  'PLEASE DO NOT PANIC. $l'",
     "     VISIBLE:  'PLEASE DO NOT PANIC. $l', cursor=1",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame'",
     "     VISIBLE:  'Application Window Frame', cursor=1",
     "BRAILLE LINE:  'PLEASE DO NOT PANIC. $l'",
     "     VISIBLE:  'PLEASE DO NOT PANIC. $l', cursor=1",
     "SPEECH OUTPUT: 'PLEASE DO NOT PANIC.' voice=uppercase",
     "SPEECH OUTPUT: 'Application Window frame'",
     "SPEECH OUTPUT: 'text PLEASE DO NOT PANIC.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+Right over PLEASE",
    ["BRAILLE LINE:  'PLEASE DO NOT PANIC. $l'",
     "     VISIBLE:  'PLEASE DO NOT PANIC. $l', cursor=7",
     "SPEECH OUTPUT: 'PLEASE '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
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
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Left to blank line",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Right to beginning of 'PLEASE' again",
    ["BRAILLE LINE:  'PLEASE DO NOT PANIC. $l'",
     "     VISIBLE:  'PLEASE DO NOT PANIC. $l', cursor=1",
     "SPEECH OUTPUT: 'P'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Up to blank line",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+Home to beginning of document",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a test.  $l'",
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
sequence.append(WaitAction("object:text-changed:delete",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Delete right 'T' in 'This'",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane his is a test.  $l'",
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
sequence.append(WaitAction("object:text-changed:delete",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Delete right 'h' in 'his'",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane is is a test.  $l'",
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
sequence.append(WaitAction("object:text-changed:delete",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+Delete right remaining 'is' of 'This'",
    ["BUG? - We update braille but not speech",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane  is a test.  $l'",
     "     VISIBLE:  ' is a test.  $l', cursor=1"]))

# [[[NOTE: WDW - with orca.settings.asyncMode=False, which is what
# the regression tests use, the Delete will not give the same output
# as what we see when orca.settings.asyncMode=True (the normal 
# operating behavior).  See the NOTE in default.py:onTextDeleted 
# for an explanation. We include the synchronous output here.]]]
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Delete"))
sequence.append(WaitAction("object:text-changed:delete",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+Delete right 'is'",
    ["BUG? - We update braille but not speech",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane  a test.  $l'",
     "     VISIBLE:  ' a test.  $l', cursor=1"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Down a line",
    [     "BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "SPEECH OUTPUT: 'This is only a test.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("End"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "End of line",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=21",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("BackSpace"))
sequence.append(WaitAction("object:text-changed:delete",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "BackSpace '.' after 'test'",
    ["BRAILLE LINE:  'This is only a test $l'",
     "     VISIBLE:  'This is only a test $l', cursor=20",
     "BRAILLE LINE:  'This is only a test $l'",
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
sequence.append(WaitAction("object:text-changed:delete",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+BackSpace to delete 'this'",
    ["BUG? - We update braille but not speech",
     "BRAILLE LINE:  'This is only a  $l'",
     "     VISIBLE:  'This is only a  $l', cursor=16",
     "BRAILLE LINE:  'This is only a  $l'",
     "     VISIBLE:  'This is only a  $l', cursor=16"]))

# [[[NOTE: WDW - with orca.settings.asyncMode=False, which is what
# the regression tests use, the BackSpace will not give the same output
# as what we see when orca.settings.asyncMode=True (the normal 
# operating behavior).  See the NOTE in default.py:onTextDeleted 
# for an explanation. We include the synchronous output here.]]]
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>BackSpace"))
sequence.append(WaitAction("object:text-changed:delete",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+BackSpace to delete 'a'",
    ["BUG? - We update braille but not speech",
     "BRAILLE LINE:  'This is only  $l'",
     "     VISIBLE:  'This is only  $l', cursor=14",
     "BRAILLE LINE:  'This is only  $l'",
     "     VISIBLE:  'This is only  $l', cursor=14"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
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
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+Left to beginning of 'is'",
    ["BRAILLE LINE:  'This is only  $l'",
     "     VISIBLE:  'This is only  $l', cursor=6",
     "SPEECH OUTPUT: 'is '"]))

########################################################################
# Do a bunch of flat review
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "KP_5 to flat review 'is'",
    ["BRAILLE LINE:  'This is only  $l'",
     "     VISIBLE:  'This is only  $l', cursor=6",
     "SPEECH OUTPUT: 'is'"]))

sequence.append(PauseAction(1000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "KP_5 2X to spell 'is'",
    ["BRAILLE LINE:  'This is only  $l'",
     "     VISIBLE:  'This is only  $l', cursor=6",
     "BRAILLE LINE:  'This is only  $l'",
     "     VISIBLE:  'This is only  $l', cursor=6",
     "SPEECH OUTPUT: 'is'",
     "SPEECH OUTPUT: 'i'",
     "SPEECH OUTPUT: 's'"]))

sequence.append(PauseAction(1000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(KeyComboAction("KP_5"))
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "KP_5 3X to military spell 'is'",
    ["BRAILLE LINE:  'This is only  $l'",
     "     VISIBLE:  'This is only  $l', cursor=6",
     "BRAILLE LINE:  'This is only  $l'",
     "     VISIBLE:  'This is only  $l', cursor=6",
     "BRAILLE LINE:  'This is only  $l'",
     "     VISIBLE:  'This is only  $l', cursor=6",
     "SPEECH OUTPUT: 'is'",
     "SPEECH OUTPUT: 'i'",
     "SPEECH OUTPUT: 's'",
     "SPEECH OUTPUT: 'india'",
     "SPEECH OUTPUT: 'sierra'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "KP_8 to flat review 'This is only'",
    ["BRAILLE LINE:  'This is only  $l'",
     "     VISIBLE:  'This is only  $l', cursor=6",
     "SPEECH OUTPUT: 'This is only ",
     "'"]))

sequence.append(PauseAction(1000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "KP_8 2X to spell 'This is only'",
    ["BRAILLE LINE:  'This is only  $l'",
     "     VISIBLE:  'This is only  $l', cursor=6",
     "BRAILLE LINE:  'This is only  $l'",
     "     VISIBLE:  'This is only  $l', cursor=6",
     "SPEECH OUTPUT: 'This is only ",
     "'",
     "SPEECH OUTPUT: 'T'",
     "SPEECH OUTPUT: 'h'",
     "SPEECH OUTPUT: 'i'",
     "SPEECH OUTPUT: 's'",
     "SPEECH OUTPUT: ' '",
     "SPEECH OUTPUT: 'i'",
     "SPEECH OUTPUT: 's'",
     "SPEECH OUTPUT: ' '",
     "SPEECH OUTPUT: 'o'",
     "SPEECH OUTPUT: 'n'",
     "SPEECH OUTPUT: 'l'",
     "SPEECH OUTPUT: 'y'",
     "SPEECH OUTPUT: ' '",
     "SPEECH OUTPUT: '",
     "'"]))

sequence.append(PauseAction(1000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(KeyComboAction("KP_8"))
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "KP_8 3X to military spell 'This is only'",
    ["BRAILLE LINE:  'This is only  $l'",
     "     VISIBLE:  'This is only  $l', cursor=6",
     "BRAILLE LINE:  'This is only  $l'",
     "     VISIBLE:  'This is only  $l', cursor=6",
     "BRAILLE LINE:  'This is only  $l'",
     "     VISIBLE:  'This is only  $l', cursor=6",
     "SPEECH OUTPUT: 'This is only ",
     "'",
     "SPEECH OUTPUT: 'T'",
     "SPEECH OUTPUT: 'h'",
     "SPEECH OUTPUT: 'i'",
     "SPEECH OUTPUT: 's'",
     "SPEECH OUTPUT: ' '",
     "SPEECH OUTPUT: 'i'",
     "SPEECH OUTPUT: 's'",
     "SPEECH OUTPUT: ' '",
     "SPEECH OUTPUT: 'o'",
     "SPEECH OUTPUT: 'n'",
     "SPEECH OUTPUT: 'l'",
     "SPEECH OUTPUT: 'y'",
     "SPEECH OUTPUT: ' '",
     "SPEECH OUTPUT: '",
     "'",
     "SPEECH OUTPUT: 'tango'",
     "SPEECH OUTPUT: 'hotel'",
     "SPEECH OUTPUT: 'india'",
     "SPEECH OUTPUT: 'sierra'",
     "SPEECH OUTPUT: ' '",
     "SPEECH OUTPUT: 'india'",
     "SPEECH OUTPUT: 'sierra'",
     "SPEECH OUTPUT: ' '",
     "SPEECH OUTPUT: 'oscar'",
     "SPEECH OUTPUT: 'november'",
     "SPEECH OUTPUT: 'lima'",
     "SPEECH OUTPUT: 'yankee'",
     "SPEECH OUTPUT: ' '",
     "SPEECH OUTPUT: '",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_2"))
sequence.append(utils.AssertPresentationAction(
    "KP_2 to flat review 'i'",
    ["BRAILLE LINE:  'This is only  $l'",
     "     VISIBLE:  'This is only  $l', cursor=6",
     "SPEECH OUTPUT: 'i'"]))

sequence.append(PauseAction(1000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_2"))
sequence.append(KeyComboAction("KP_2"))
sequence.append(utils.AssertPresentationAction(
    "KP_2 2X to military spell 'i'",
    ["BRAILLE LINE:  'This is only  $l'",
     "     VISIBLE:  'This is only  $l', cursor=6",
     "BRAILLE LINE:  'This is only  $l'",
     "     VISIBLE:  'This is only  $l', cursor=6",
     "SPEECH OUTPUT: 'i'",
     "SPEECH OUTPUT: 'india'"]))

sequence.append(PauseAction(1000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_1"))
sequence.append(utils.AssertPresentationAction(
    "KP_1 to flat review space",
    ["BRAILLE LINE:  'This is only  $l'",
     "     VISIBLE:  'This is only  $l', cursor=5",
     "SPEECH OUTPUT: 'space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_1"))
sequence.append(utils.AssertPresentationAction(
    "KP_1 to flat review 's'",
    ["BRAILLE LINE:  'This is only  $l'",
     "     VISIBLE:  'This is only  $l', cursor=4",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_3"))
sequence.append(utils.AssertPresentationAction(
    "KP_3 to flat review space",
    ["BRAILLE LINE:  'This is only  $l'",
     "     VISIBLE:  'This is only  $l', cursor=5",
     "SPEECH OUTPUT: 'space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "KP_5 to flat review whitespace",
    ["BRAILLE LINE:  'This is only  $l'",
     "     VISIBLE:  'This is only  $l', cursor=5",
     "SPEECH OUTPUT: 'white space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_4"))
sequence.append(utils.AssertPresentationAction(
    "KP_4 to flat review 'This'",
    ["BRAILLE LINE:  'This is only  $l'",
     "     VISIBLE:  'This is only  $l', cursor=1",
     "SPEECH OUTPUT: 'This'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "KP_6 to flat review 'is'",
    ["BRAILLE LINE:  'This is only  $l'",
     "     VISIBLE:  'This is only  $l', cursor=6",
     "SPEECH OUTPUT: 'is'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "KP_7 to flat review 'a test' and scrollbar",
    ["BRAILLE LINE:  ' a test.  vertical ScrollBar 0% $l'",
     "     VISIBLE:  ' a test.  vertical ScrollBar 0% ', cursor=1",
     "SPEECH OUTPUT: ' a test. ",
     " vertical scroll bar 0 percent.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "KP_6 to flat review 'a'",
    ["BRAILLE LINE:  ' a test.  vertical ScrollBar 0% $l'",
     "     VISIBLE:  ' a test.  vertical ScrollBar 0% ', cursor=2",
     "SPEECH OUTPUT: 'a'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "KP_6 to flat review 'test.'",
    ["BRAILLE LINE:  ' a test.  vertical ScrollBar 0% $l'",
     "     VISIBLE:  ' a test.  vertical ScrollBar 0% ', cursor=4",
     "SPEECH OUTPUT: 'test.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "KP_6 to flat review scrollbar",
    ["BRAILLE LINE:  ' a test.  vertical ScrollBar 0% $l'",
     "     VISIBLE:  ' a test.  vertical ScrollBar 0% ', cursor=11",
     "SPEECH OUTPUT: 'vertical scroll bar 0 percent.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "KP_7 to flat review toolbar",
    ["BRAILLE LINE:  'Open & y toggle button Quit panel GTK! $l'",
     "     VISIBLE:  'Open & y toggle button Quit pane', cursor=1",
     "SPEECH OUTPUT: 'Open not pressed toggle button Quit panel GTK!'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "KP_5 to flat review 'open'",
    ["BRAILLE LINE:  'Open & y toggle button Quit panel GTK! $l'",
     "     VISIBLE:  'Open & y toggle button Quit pane', cursor=1",
     "SPEECH OUTPUT: 'Open'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "KP_6 to flat review toggle button indicator",
    ["BRAILLE LINE:  'Open & y toggle button Quit panel GTK! $l'",
     "     VISIBLE:  'Open & y toggle button Quit pane', cursor=6",
     "SPEECH OUTPUT: 'not pressed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "KP_6 to flat review toggle button",
    ["BRAILLE LINE:  'Open & y toggle button Quit panel GTK! $l'",
     "     VISIBLE:  'Open & y toggle button Quit pane', cursor=10",
     "SPEECH OUTPUT: 'toggle button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "KP_7 to flat review menu",
    ["BRAILLE LINE:  'File Preferences Help $l'",
     "     VISIBLE:  'File Preferences Help $l', cursor=1",
     "SPEECH OUTPUT: 'File Preferences Help'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "KP_5 to flat review 'File'",
    ["BRAILLE LINE:  'File Preferences Help $l'",
     "     VISIBLE:  'File Preferences Help $l', cursor=1",
     "SPEECH OUTPUT: 'File'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "KP_6 to flat review 'Preferences'",
    ["BRAILLE LINE:  'File Preferences Help $l'",
     "     VISIBLE:  'File Preferences Help $l', cursor=6",
     "SPEECH OUTPUT: 'Preferences'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_5"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Insert+KP_5 to flat review 'Preferences' accessible",
    ["SPEECH OUTPUT: 'Preferences'",
     "SPEECH OUTPUT: 'menu'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_9"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Insert+KP_9 to flat review end",
    ["BRAILLE LINE:  'Cursor at row 1 column 5 - 243 chars in document $l'",
     "     VISIBLE:  'Cursor at row 1 column 5 - 243 c', cursor=1",
     "SPEECH OUTPUT: 'Cursor at row 1 column 5 - 243 chars in document'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_7"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Insert+KP_7 to flat review home",
    ["BRAILLE LINE:  'File Preferences Help $l'",
     "     VISIBLE:  'File Preferences Help $l', cursor=1",
     "SPEECH OUTPUT: 'File Preferences Help'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_6"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Insert+KP_6 to flat review below",
    ["BRAILLE LINE:  'Open & y toggle button Quit panel GTK! $l'",
     "     VISIBLE:  'Open & y toggle button Quit pane', cursor=1",
     "SPEECH OUTPUT: 'Open'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_4"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Insert+KP_4 to flat review above",
    ["BRAILLE LINE:  'File Preferences Help $l'",
     "     VISIBLE:  'File Preferences Help $l', cursor=1",
     "SPEECH OUTPUT: 'File'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "KP_9 to flat review next line",
    ["BRAILLE LINE:  'Open & y toggle button Quit panel GTK! $l'",
     "     VISIBLE:  'Open & y toggle button Quit pane', cursor=1",
     "SPEECH OUTPUT: 'Open not pressed toggle button Quit panel GTK!'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_1"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Insert+KP_1 to flat review end of line",
    ["BRAILLE LINE:  'Open & y toggle button Quit panel GTK! $l'",
     "     VISIBLE:  'l GTK! $l', cursor=3",
     "SPEECH OUTPUT: 'GTK!'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Subtract"))
sequence.append(utils.AssertPresentationAction(
    "KP_Subtract to exit flat review",
    ["BUG? - Extra stuff here",
     "BRAILLE LINE:  'Leaving flat review.'",
     "     VISIBLE:  'Leaving flat review.', cursor=0",
     "BRAILLE LINE:  'This is only  $l'",
     "     VISIBLE:  'This is only  $l', cursor=6",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame'",
     "     VISIBLE:  'Application Window Frame', cursor=1",
     "BRAILLE LINE:  'This is only  $l'",
     "     VISIBLE:  'This is only  $l', cursor=6",
     "SPEECH OUTPUT: 'Leaving flat review.' voice=system",
     "SPEECH OUTPUT: 'Application Window frame'",
     "SPEECH OUTPUT: 'text This is only '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "KP_5 to flat review 'is'",
    ["BRAILLE LINE:  'This is only  $l'",
     "     VISIBLE:  'This is only  $l', cursor=6",
     "SPEECH OUTPUT: 'is'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "KP_6 to flat review 'only'",
    ["BRAILLE LINE:  'This is only  $l'",
     "     VISIBLE:  'This is only  $l', cursor=9",
     "SPEECH OUTPUT: 'only'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_3"))
sequence.append(utils.AssertPresentationAction(
    "KP_3 to flat review 'n'",
    ["BRAILLE LINE:  'This is only  $l'",
     "     VISIBLE:  'This is only  $l', cursor=10",
     "SPEECH OUTPUT: 'n'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_3"))
sequence.append(utils.AssertPresentationAction(
    "KP_3 to flat review 'l'",
    ["BRAILLE LINE:  'This is only  $l'",
     "     VISIBLE:  'This is only  $l', cursor=11",
     "SPEECH OUTPUT: 'l'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Divide"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "KP_Divide to left click on 'l'",
    ["BRAILLE LINE:  'This is only  $l'",
     "     VISIBLE:  'This is only  $l', cursor=11",
     "BRAILLE LINE:  'This is only  $l'",
     "     VISIBLE:  'This is only  $l', cursor=11"]))

########################################################################
# Dismiss the menu and close the Application Window demo window
#
sequence.append(KeyComboAction("<Alt>F4"))

########################################################################
# Go back to the main gtk-demo window and reselect the
# "Application main window" menu.  Let the harness kill the app.
#
#sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(PauseAction(1000))
sequence.append(KeyComboAction("Home"))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
