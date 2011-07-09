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

sequence.append(PauseAction(3000))

########################################################################
# Position the cursor on the second line, just after the first space.
#
sequence.append(KeyComboAction("Up"))
sequence.append(KeyComboAction("Right"))
sequence.append(KeyComboAction("Right"))
sequence.append(KeyComboAction("Right"))
sequence.append(KeyComboAction("Right"))
sequence.append(KeyComboAction("Right"))

########################################################################
# Test #1 - Shift+Ctrl+Page_Up to select text to beginning of line.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift><Control>Page_Up"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Shift+Ctrl+Page_Up to select text to beginning of line",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "SPEECH OUTPUT: 'This '",
     "SPEECH OUTPUT: 'line selected from start to previous cursor position'"]))

########################################################################
# Test #2 - Shift+Ctrl+Page_Down to select text to end of line.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift><Control>Page_Down"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Shift+Ctrl+Page_Down to select text to end of line",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=21",
     "SPEECH OUTPUT: 'This is only a test.'",
     "SPEECH OUTPUT: 'line selected to end from previous cursor position'"]))

########################################################################
# Test #3 - Shift+Up to select text.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Up"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Shift+Up to select text",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a test.  $l'",
     "     VISIBLE:  'This is a test.  $l', cursor=17",
     "SPEECH OUTPUT: '",
     "This is only a test.'",
     "SPEECH OUTPUT: 'unselected' voice=system"]))

########################################################################
# Test #4 - Shift+Down to deselect text.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Down"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Shift+Down to deselect text",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=21",
     "SPEECH OUTPUT: '",
     "This is only a test.'",
     "SPEECH OUTPUT: 'unselected'"]))

########################################################################
# Test #5 - Ctrl+Page_Up to beginning of line.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Page_Up"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+Page_Up to beginning of line",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "SPEECH OUTPUT: 'T'",
     "SPEECH OUTPUT: 'unselected'"]))

########################################################################
# Test #6 - Ctrl+Page_Down to end of line.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Page_Down"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Ctrl+Page_Down to end of line",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=21",
     "SPEECH OUTPUT: 'This is only a test.'"]))

########################################################################
# Test #7 - Page up.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Up"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Page up",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a test.  $l'",
     "     VISIBLE:  'This is a test.  $l', cursor=1",
     "SPEECH OUTPUT: 'This is a test. '"]))

########################################################################
# Test #8 - Page down.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Down"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Page down",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

########################################################################
# Test #9 - Shift+Page_Up to select text.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Page_Up"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Shift+Page_Up to select text",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a test.  $l'",
     "     VISIBLE:  'This is a test.  $l', cursor=1",
     "SPEECH OUTPUT: 'This is a test. '",
     "SPEECH OUTPUT: 'page selected to cursor position'"]))

########################################################################
# Test #10 - Shift+Page_Down to deselect text.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Page_Down"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Shift+Page_Down to deselect text",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'blank'",
     "SPEECH OUTPUT: 'page unselected from cursor position'"]))

########################################################################
# Test #11 - Page_Up.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Page_Up"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Page_Up",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a test.  $l'",
     "     VISIBLE:  'This is a test.  $l', cursor=1",
     "SPEECH OUTPUT: 'This is a test. '"]))

########################################################################
# Test #12 - KP_Add to do a SayAll.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Add"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "KP_Add to do a SayAll",
    ["SPEECH OUTPUT: 'This is a test.'",
     "SPEECH OUTPUT: ' ",
     "This is only a test.'",
     "SPEECH OUTPUT: '",
     "'"]))

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
