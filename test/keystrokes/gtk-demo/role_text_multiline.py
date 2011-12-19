#!/usr/bin/python

"""Test of multiline editable text using the gtk-demo Application Main Window
   demo.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))

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
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("This is a test.", 500, 500))
sequence.append(KeyComboAction("Return", 500))
sequence.append(utils.AssertPresentationAction(
    "Typing",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane T $l'",
     "     VISIBLE:  'T $l', cursor=2",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane T $l'",
     "     VISIBLE:  'T $l', cursor=2",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane Th $l'",
     "     VISIBLE:  'Th $l', cursor=3",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane Th $l'",
     "     VISIBLE:  'Th $l', cursor=3",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane Thi $l'",
     "     VISIBLE:  'Thi $l', cursor=4",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane Thi $l'",
     "     VISIBLE:  'Thi $l', cursor=4",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This $l'",
     "     VISIBLE:  'This $l', cursor=5",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This $l'",
     "     VISIBLE:  'This $l', cursor=5",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This  $l'",
     "     VISIBLE:  'This  $l', cursor=6",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This  $l'",
     "     VISIBLE:  'This  $l', cursor=6",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This i $l'",
     "     VISIBLE:  'This i $l', cursor=7",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This i $l'",
     "     VISIBLE:  'This i $l', cursor=7",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is $l'",
     "     VISIBLE:  'This is $l', cursor=8",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is $l'",
     "     VISIBLE:  'This is $l', cursor=8",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is  $l'",
     "     VISIBLE:  'This is  $l', cursor=9",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is  $l'",
     "     VISIBLE:  'This is  $l', cursor=9",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a $l'",
     "     VISIBLE:  'This is a $l', cursor=10",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a $l'",
     "     VISIBLE:  'This is a $l', cursor=10",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a  $l'",
     "     VISIBLE:  'This is a  $l', cursor=11",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a  $l'",
     "     VISIBLE:  'This is a  $l', cursor=11",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a t $l'",
     "     VISIBLE:  'This is a t $l', cursor=12",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a t $l'",
     "     VISIBLE:  'This is a t $l', cursor=12",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a te $l'",
     "     VISIBLE:  'This is a te $l', cursor=13",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a te $l'",
     "     VISIBLE:  'This is a te $l', cursor=13",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a tes $l'",
     "     VISIBLE:  'This is a tes $l', cursor=14",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a tes $l'",
     "     VISIBLE:  'This is a tes $l', cursor=14",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a test $l'",
     "     VISIBLE:  'This is a test $l', cursor=15",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a test $l'",
     "     VISIBLE:  'This is a test $l', cursor=15",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=16",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=16",
     "BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1"]))

sequence.append(KeyComboAction("Return", 500))
sequence.append(TypeAction("I am just typing away like a mad little monkey with nothing better to do in my life than eat fruit and type.", 500))
sequence.append(KeyComboAction("Return", 500))
sequence.append(TypeAction("The keyboard sure can get sticky.", 500))
sequence.append(KeyComboAction("Return", 500))
sequence.append(TypeAction("Tis this and thus thou art in Rome.", 500))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# Go to the beginning of the text area.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home", 500))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Navigate home",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=1",
     "SPEECH OUTPUT: 'This is a test.'"]))

########################################################################
# Now, arrow right to the end of the word "This" and select "is a test"
# word by word.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right", 500))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(KeyComboAction("Right", 500))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(KeyComboAction("Right", 500))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(KeyComboAction("Right", 500))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Arrow to end of 'This'",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=2",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=3",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=4",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=5",
     "SPEECH OUTPUT: 'h'",
     "SPEECH OUTPUT: 'i'",
     "SPEECH OUTPUT: 's'",
     "SPEECH OUTPUT: 'space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift><Control>Right", 500))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(KeyComboAction("<Shift><Control>Right", 500))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(KeyComboAction("<Shift><Control>Right", 500))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Select 'is a test'",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=8",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=10",
     "BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=15",
     "SPEECH OUTPUT: ' is'",
     "SPEECH OUTPUT: 'selected'",
     "SPEECH OUTPUT: ' a'",
     "SPEECH OUTPUT: 'selected'",
     "SPEECH OUTPUT: ' test'",
     "SPEECH OUTPUT: 'selected'"]))

########################################################################
# Unselect "test".
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift><Control>Left", 500))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Unselect 'test'",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=11",
     "SPEECH OUTPUT: 'test'",
     "SPEECH OUTPUT: 'unselected'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=11",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: ' is a '",
     "SPEECH OUTPUT: 'selected'"]))

########################################################################
# Press Home to move to the beginning of the line. Arrow down to 
# "I am typing away..." and use Shift End to select to the end of the 
# line.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Home", 500))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(KeyComboAction("Down", 500))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(KeyComboAction("<Shift>End", 500))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Select to end of line",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane This is a test. $l'",
     "     VISIBLE:  'This is a test. $l', cursor=1",
     "BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "BRAILLE LINE:  'I am just typing away like a mad little monkey with nothing better to do in my life than eat fruit and type. $l'",
     "     VISIBLE:  'I am just typing away like a mad', cursor=1",
     "BRAILLE LINE:  'I am just typing away like a mad little monkey with nothing better to do in my life than eat fruit and type. $l'",
     "     VISIBLE:  'y life than eat fruit and type. ', cursor=32",
     "SPEECH OUTPUT: 'T'",
     "SPEECH OUTPUT: 'unselected' voice=system",
     "SPEECH OUTPUT: 'blank' voice=system",
     "SPEECH OUTPUT: 'I am just typing away like a mad little monkey with nothing better to do in my life than eat fruit and type.'",
     "SPEECH OUTPUT: 'I am just typing away like a mad little monkey with nothing better to do in my life than eat fruit and type.'",
     "SPEECH OUTPUT: 'selected' voice=system"]))

########################################################################
# Shift Control Right arrow to select the first two words on the next
# line.
#
sequence.append(KeyComboAction("<Shift><Control>Right", 500))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(KeyComboAction("<Shift><Control>Right", 500))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Basic Where Am I multiline selection",
    ["BRAILLE LINE:  'The keyboard sure can get sticky. $l'",
     "     VISIBLE:  'The keyboard sure can get sticky', cursor=13",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'I am just typing away like a mad little monkey with nothing better to do in my life than eat fruit and type.",
     "The keyboard'",
     "SPEECH OUTPUT: 'selected'"]))

########################################################################
# Do a detailed "Where Am I" via KP_Enter 2x.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Detailed Where Am I multiline selection",
    ["BRAILLE LINE:  'The keyboard sure can get sticky. $l'",
     "     VISIBLE:  'The keyboard sure can get sticky', cursor=13",
     "BRAILLE LINE:  'The keyboard sure can get sticky. $l'",
     "     VISIBLE:  'The keyboard sure can get sticky', cursor=13",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'I am just typing away like a mad little monkey with nothing better to do in my life than eat fruit and type.",
     "The keyboard'",
     "SPEECH OUTPUT: 'selected'",
     "SPEECH OUTPUT: 'text'",
     "SPEECH OUTPUT: 'I am just typing away like a mad little monkey with nothing better to do in my life than eat fruit and type.",
     "The keyboard'",
     "SPEECH OUTPUT: 'selected'"]))

########################################################################
# Try a "SayAll".
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Add", 500))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "SayAll",
    ["SPEECH OUTPUT: '",
     "The keyboard sure can get sticky.'",
     "SPEECH OUTPUT: '",
     "Tis this and thus thou art in Rome.'",
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
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
