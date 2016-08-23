#!/usr/bin/python

"""Test of presentation of whitespace with braille disabled."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Application main window"))
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("Tab"))

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

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. 1 Tab",
    ["SPEECH OUTPUT: 'left control '",
     "SPEECH OUTPUT: '1 tab ' voice=system",
     "SPEECH OUTPUT: '	'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. 1 Tab and the word 'foo'",
    ["SPEECH OUTPUT: '1 tab ' voice=system",
     "SPEECH OUTPUT: '	foo'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. 2 Tabs",
    ["SPEECH OUTPUT: '2 tabs ' voice=system",
     "SPEECH OUTPUT: '		'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. 2 Tabs and the word 'foo'",
    ["SPEECH OUTPUT: '2 tabs ' voice=system",
     "SPEECH OUTPUT: '		foo'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. 1 space",
    ["SPEECH OUTPUT: '1 space ' voice=system",
     "SPEECH OUTPUT: ' '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. 1 space and the word 'foo'",
    ["SPEECH OUTPUT: '1 space ' voice=system",
     "SPEECH OUTPUT: ' foo'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. 2 spaces",
    ["SPEECH OUTPUT: '2 spaces ' voice=system",
     "SPEECH OUTPUT: '  '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. 2 spaces and the word 'foo'",
    ["SPEECH OUTPUT: '2 spaces ' voice=system",
     "SPEECH OUTPUT: '  foo'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. 1 Tab and 1 space",
    ["SPEECH OUTPUT: '1 tab 1 space ' voice=system",
     "SPEECH OUTPUT: '	 '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. 1 Tab, 1 space, and the word 'foo'",
    ["SPEECH OUTPUT: '1 tab 1 space ' voice=system",
     "SPEECH OUTPUT: '	 foo'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. 1 Tab and 2 spaces",
    ["SPEECH OUTPUT: '1 tab 2 spaces ' voice=system",
     "SPEECH OUTPUT: '	  '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. 1 Tab, 2 spaces, and the word 'foo'",
    ["SPEECH OUTPUT: '1 tab 2 spaces ' voice=system",
     "SPEECH OUTPUT: '	  foo'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "13. 2 Tabs and 1 space",
    ["SPEECH OUTPUT: '2 tabs 1 space ' voice=system",
     "SPEECH OUTPUT: '		 '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "14. 2 Tabs, 1 space, and the word 'foo'",
    ["SPEECH OUTPUT: '2 tabs 1 space ' voice=system",
     "SPEECH OUTPUT: '		 foo'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "15. 2 Tabs and 2 spaces",
    ["SPEECH OUTPUT: '2 tabs 2 spaces ' voice=system",
     "SPEECH OUTPUT: '		  '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "16. 2 Tabs, 2 spaces, and the word 'foo'",
    ["SPEECH OUTPUT: '2 tabs 2 spaces ' voice=system",
     "SPEECH OUTPUT: '		  foo'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "17. 1 Tab, 1 space, and 1 Tab",
    ["SPEECH OUTPUT: '1 tab 1 space 1 tab ' voice=system",
     "SPEECH OUTPUT: '	 	'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "18. 1 Tab, 1 space, 1 Tab, and the word 'foo'",
    ["SPEECH OUTPUT: '1 tab 1 space 1 tab ' voice=system",
     "SPEECH OUTPUT: '	 	foo'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "19. 1 Tab, 1 space, 1 Tab, and 1 space",
    ["SPEECH OUTPUT: '1 tab 1 space 1 tab 1 space ' voice=system",
     "SPEECH OUTPUT: '	 	 '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "20. 1 Tab, 1 space, 1 Tab, 1 space, and the word 'foo'",
    ["SPEECH OUTPUT: '1 tab 1 space 1 tab 1 space ' voice=system",
     "SPEECH OUTPUT: '	 	 foo'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "21. 1 Tab, 2 spaces, and 1 Tab",
    ["SPEECH OUTPUT: '1 tab 2 spaces 1 tab ' voice=system",
     "SPEECH OUTPUT: '	  	'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "22. 1 Tab, 2 spaces, 1 Tab, and the word 'foo'",
    ["SPEECH OUTPUT: '1 tab 2 spaces 1 tab ' voice=system",
     "SPEECH OUTPUT: '	  	foo'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "23. 2 spaces and 1 Tab",
    ["SPEECH OUTPUT: '2 spaces 1 tab ' voice=system",
     "SPEECH OUTPUT: '  	'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "24. 2 spaces, 1 Tab, and the word 'foo'",
    ["SPEECH OUTPUT: '2 spaces 1 tab ' voice=system",
     "SPEECH OUTPUT: '  	foo'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
