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

sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Tab"))
sequence.append(TypeAction("foo"))
sequence.append(KeyComboAction("Return"))

sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(TypeAction("foo"))
sequence.append(KeyComboAction("Return"))

sequence.append(TypeAction(" "))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction(" foo"))
sequence.append(KeyComboAction("Return"))

sequence.append(TypeAction("  "))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("  foo"))
sequence.append(KeyComboAction("Return"))

sequence.append(KeyComboAction("Tab"))
sequence.append(TypeAction(" "))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Tab"))
sequence.append(TypeAction(" foo"))
sequence.append(KeyComboAction("Return"))

sequence.append(KeyComboAction("Tab"))
sequence.append(TypeAction("  "))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Tab"))
sequence.append(TypeAction("  foo"))
sequence.append(KeyComboAction("Return"))

sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(TypeAction(" "))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(TypeAction(" foo"))
sequence.append(KeyComboAction("Return"))

sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(TypeAction("  "))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(TypeAction("  foo"))
sequence.append(KeyComboAction("Return"))

sequence.append(KeyComboAction("Tab"))
sequence.append(TypeAction(" "))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Tab"))
sequence.append(TypeAction(" "))
sequence.append(KeyComboAction("Tab"))
sequence.append(TypeAction("foo"))
sequence.append(KeyComboAction("Return"))

sequence.append(KeyComboAction("Tab"))
sequence.append(TypeAction(" "))
sequence.append(KeyComboAction("Tab"))
sequence.append(TypeAction(" "))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Tab"))
sequence.append(TypeAction(" "))
sequence.append(KeyComboAction("Tab"))
sequence.append(TypeAction(" foo"))
sequence.append(KeyComboAction("Return"))

sequence.append(KeyComboAction("Tab"))
sequence.append(TypeAction("  "))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Return"))
sequence.append(KeyComboAction("Tab"))
sequence.append(TypeAction("  "))
sequence.append(KeyComboAction("Tab"))
sequence.append(TypeAction("foo"))
sequence.append(KeyComboAction("Return"))

sequence.append(TypeAction("  "))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Return"))
sequence.append(TypeAction("  "))
sequence.append(KeyComboAction("Tab"))
sequence.append(TypeAction("foo"))
sequence.append(KeyComboAction("Return"))

sequence.append(PauseAction(3000))

########################################################################
# Do a bunch of navigation
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Home to 1 tab",
    ["BRAILLE LINE:  'gtk-demo Application Application Window Frame ScrollPane 	 $l'",
     "     VISIBLE:  '	 $l', cursor=1",
     "SPEECH OUTPUT: 'left control'",
     "SPEECH OUTPUT: 'home'",
     "SPEECH OUTPUT: '1 tab ' voice=system",
     "SPEECH OUTPUT: '	'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Down to 1 tab and foo",
    ["BRAILLE LINE:  '	foo $l'",
     "     VISIBLE:  '	foo $l', cursor=1",
     "SPEECH OUTPUT: '1 tab '",
     "SPEECH OUTPUT: '	foo'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Down to 2 tabs",
    ["BRAILLE LINE:  '		 $l'",
     "     VISIBLE:  '		 $l', cursor=1",
     "SPEECH OUTPUT: '2 tabs '",
     "SPEECH OUTPUT: '		'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Down to 2 tabs and foo",
    ["BRAILLE LINE:  '		foo $l'",
     "     VISIBLE:  '		foo $l', cursor=1",
     "SPEECH OUTPUT: '2 tabs '",
     "SPEECH OUTPUT: '		foo'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Down to 1 space",
    ["BRAILLE LINE:  '  $l'",
     "     VISIBLE:  '  $l', cursor=1",
     "SPEECH OUTPUT: '1 space '",
     "SPEECH OUTPUT: ' '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Down to 1 space and foo",
    ["BRAILLE LINE:  ' foo $l'",
     "     VISIBLE:  ' foo $l', cursor=1",
     "SPEECH OUTPUT: '1 space '",
     "SPEECH OUTPUT: ' foo'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Down to 2 spaces",
    ["BRAILLE LINE:  '   $l'",
     "     VISIBLE:  '   $l', cursor=1",
     "SPEECH OUTPUT: '2 spaces '",
     "SPEECH OUTPUT: '  '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Down to 2 spaces and foo",
    ["BRAILLE LINE:  '  foo $l'",
     "     VISIBLE:  '  foo $l', cursor=1",
     "SPEECH OUTPUT: '2 spaces '",
     "SPEECH OUTPUT: '  foo'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Down to 1 tab 1 space",
    ["BRAILLE LINE:  '	  $l'",
     "     VISIBLE:  '	  $l', cursor=1",
     "SPEECH OUTPUT: '1 tab 1 space '",
     "SPEECH OUTPUT: '	 '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Down to 1 tab 1 space and foo",
    ["BRAILLE LINE:  '	 foo $l'",
     "     VISIBLE:  '	 foo $l', cursor=1",
     "SPEECH OUTPUT: '1 tab 1 space '",
     "SPEECH OUTPUT: '	 foo'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Down to 1 tab 2 spaces",
    ["BRAILLE LINE:  '	   $l'",
     "     VISIBLE:  '	   $l', cursor=1",
     "SPEECH OUTPUT: '1 tab 2 spaces '",
     "SPEECH OUTPUT: '	  '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Down to 1 tab 2 spaces and foo",
    ["BRAILLE LINE:  '	  foo $l'",
     "     VISIBLE:  '	  foo $l', cursor=1",
     "SPEECH OUTPUT: '1 tab 2 spaces '",
     "SPEECH OUTPUT: '	  foo'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Down to 2 tabs 1 space",
    ["BRAILLE LINE:  '		  $l'",
     "     VISIBLE:  '		  $l', cursor=1",
     "SPEECH OUTPUT: '2 tabs 1 space '",
     "SPEECH OUTPUT: '		 '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Down to 2 tabs 1 space and foo",
    ["BRAILLE LINE:  '		 foo $l'",
     "     VISIBLE:  '		 foo $l', cursor=1",
     "SPEECH OUTPUT: '2 tabs 1 space '",
     "SPEECH OUTPUT: '		 foo'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Down to 2 tabs 2 spaces",
    ["BRAILLE LINE:  '		   $l'",
     "     VISIBLE:  '		   $l', cursor=1",
     "SPEECH OUTPUT: '2 tabs 2 spaces '",
     "SPEECH OUTPUT: '		  '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Down to 2 tabs 2 spaces and foo",
    ["BRAILLE LINE:  '		  foo $l'",
     "     VISIBLE:  '		  foo $l', cursor=1",
     "SPEECH OUTPUT: '2 tabs 2 spaces '",
     "SPEECH OUTPUT: '		  foo'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Down to 1 tab 1 space 1 tab",
    ["BRAILLE LINE:  '	 	 $l'",
     "     VISIBLE:  '	 	 $l', cursor=1",
     "SPEECH OUTPUT: '1 tab 1 space 1 tab '",
     "SPEECH OUTPUT: '	 	'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Down to 1 tab 1 space 1 tab and foo",
    ["BRAILLE LINE:  '	 	foo $l'",
     "     VISIBLE:  '	 	foo $l', cursor=1",
     "SPEECH OUTPUT: '1 tab 1 space 1 tab '",
     "SPEECH OUTPUT: '	 	foo'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Down to 1 tab 1 space 1 tab 1 space",
    ["BRAILLE LINE:  '	 	  $l'",
     "     VISIBLE:  '	 	  $l', cursor=1",
     "SPEECH OUTPUT: '1 tab 1 space 1 tab 1 space '",
     "SPEECH OUTPUT: '	 	 '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Down to 1 tab 1 space 1 tab 1 space and foo",
    ["BRAILLE LINE:  '	 	 foo $l'",
     "     VISIBLE:  '	 	 foo $l', cursor=1",
     "SPEECH OUTPUT: '1 tab 1 space 1 tab 1 space '",
     "SPEECH OUTPUT: '	 	 foo'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Down to 1 tab 2 spaces 1 tab",
    ["BRAILLE LINE:  '	  	 $l'",
     "     VISIBLE:  '	  	 $l', cursor=1",
     "SPEECH OUTPUT: '1 tab 2 spaces 1 tab '",
     "SPEECH OUTPUT: '	  	'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Down to 1 tab 2 spaces 1 tab and foo",
    ["BRAILLE LINE:  '	  	foo $l'",
     "     VISIBLE:  '	  	foo $l', cursor=1",
     "SPEECH OUTPUT: '1 tab 2 spaces 1 tab '",
     "SPEECH OUTPUT: '	  	foo'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Down to 2 spaces 1 tab",
    ["BRAILLE LINE:  '  	 $l'",
     "     VISIBLE:  '  	 $l', cursor=1",
     "SPEECH OUTPUT: '2 spaces 1 tab '",
     "SPEECH OUTPUT: '  	'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:text-caret-moved",
                           None,
                           None,
                           pyatspi.ROLE_TEXT,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Down to 2 spaces 1 tab and foo",
    ["BRAILLE LINE:  '  	foo $l'",
     "     VISIBLE:  '  	foo $l', cursor=1",
     "SPEECH OUTPUT: '2 spaces 1 tab '",
     "SPEECH OUTPUT: '  	foo'"]))

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
