#!/usr/bin/python

"""Test of flat review of text and a toolbar."""

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

sequence.append(KeyComboAction("<Control>Home"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Down"))

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

sequence.append(KeyComboAction("<Control>Home"))
sequence.append(KeyComboAction("Down"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "KP_5 to flat review 'This'",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "SPEECH OUTPUT: 'This'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "KP_5 2X to spell 'This'",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "SPEECH OUTPUT: 'This'",
     "SPEECH OUTPUT: 'T' voice=uppercase",
     "SPEECH OUTPUT: 'h'",
     "SPEECH OUTPUT: 'i'",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(KeyComboAction("KP_5"))
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "KP_5 3X to military spell 'This'",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "SPEECH OUTPUT: 'This'",
     "SPEECH OUTPUT: 'T' voice=uppercase",
     "SPEECH OUTPUT: 'h'",
     "SPEECH OUTPUT: 'i'",
     "SPEECH OUTPUT: 's'",
     "SPEECH OUTPUT: 'tango' voice=uppercase",
     "SPEECH OUTPUT: 'hotel'",
     "SPEECH OUTPUT: 'india'",
     "SPEECH OUTPUT: 'sierra'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "KP_8 to flat review 'This is only a test.'",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "SPEECH OUTPUT: 'This is only a test.",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "KP_8 2X to spell 'This is only a test.'",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "SPEECH OUTPUT: 'This is only a test.",
     "'",
     "SPEECH OUTPUT: 'T' voice=uppercase",
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
     "SPEECH OUTPUT: 'a'",
     "SPEECH OUTPUT: ' '",
     "SPEECH OUTPUT: 't'",
     "SPEECH OUTPUT: 'e'",
     "SPEECH OUTPUT: 's'",
     "SPEECH OUTPUT: 't'",
     "SPEECH OUTPUT: '.'",
     "SPEECH OUTPUT: '",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(KeyComboAction("KP_8"))
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "KP_8 3X to military spell 'This is only a test.'",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "SPEECH OUTPUT: 'This is only a test.",
     "'",
     "SPEECH OUTPUT: 'T' voice=uppercase",
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
     "SPEECH OUTPUT: 'a'",
     "SPEECH OUTPUT: ' '",
     "SPEECH OUTPUT: 't'",
     "SPEECH OUTPUT: 'e'",
     "SPEECH OUTPUT: 's'",
     "SPEECH OUTPUT: 't'",
     "SPEECH OUTPUT: '.'",
     "SPEECH OUTPUT: '",
     "'",
     "SPEECH OUTPUT: 'tango' voice=uppercase",
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
     "SPEECH OUTPUT: 'alpha'",
     "SPEECH OUTPUT: ' '",
     "SPEECH OUTPUT: 'tango'",
     "SPEECH OUTPUT: 'echo'",
     "SPEECH OUTPUT: 'sierra'",
     "SPEECH OUTPUT: 'tango'",
     "SPEECH OUTPUT: '.'",
     "SPEECH OUTPUT: '",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_2"))
sequence.append(utils.AssertPresentationAction(
    "KP_2 to flat review 'T'",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "SPEECH OUTPUT: 'T'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_2"))
sequence.append(KeyComboAction("KP_2"))
sequence.append(utils.AssertPresentationAction(
    "KP_2 2X to military spell 'T'",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "SPEECH OUTPUT: 'T'",
     "SPEECH OUTPUT: 'tango' voice=uppercase"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "KP_6 to flat review 'is'",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=6",
     "SPEECH OUTPUT: 'is'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "KP_7 to flat review 'This is a test.' and the scrollbar",
    ["BRAILLE LINE:  'This is a test.  vertical scroll bar 0% $l'",
     "     VISIBLE:  'This is a test.  vertical scroll', cursor=1",
     "SPEECH OUTPUT: 'This is a test. ",
     " vertical scroll bar 0 percent.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "KP_7 to flat review toolbar",
    ["KNOWN ISSUE: gtk-demo's toolbar widgets lack names that were present in the past",
     "BRAILLE LINE:  'push button push button panel push button $l'",
     "     VISIBLE:  'push button push button panel pu', cursor=1",
     "SPEECH OUTPUT: 'push button push button panel push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "KP_7 to flat review menu",
    ["BRAILLE LINE:  'Preferences Help $l'",
     "     VISIBLE:  'Preferences Help $l', cursor=1",
     "SPEECH OUTPUT: 'Preferences Help'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "KP_5 to flat review 'Preferences'",
    ["BRAILLE LINE:  'Preferences Help $l'",
     "     VISIBLE:  'Preferences Help $l', cursor=1",
     "SPEECH OUTPUT: 'Preferences'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "KP_6 to flat review 'Help'",
    ["BRAILLE LINE:  'Preferences Help $l'",
     "     VISIBLE:  'Preferences Help $l', cursor=13",
     "SPEECH OUTPUT: 'Help'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_5"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Insert+KP_5 to flat review 'Help' accessible",
    ["SPEECH OUTPUT: 'Help'",
     "SPEECH OUTPUT: 'menu'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_9"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Insert+KP_9 to flat review end",
    ["BRAILLE LINE:  ' Cursor at row 1 column 0 - 60 chars in document $l'",
     "     VISIBLE:  ' Cursor at row 1 column 0 - 60 c', cursor=2",
     "SPEECH OUTPUT: 'Cursor at row 1 column 0 - 60 chars in document'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_7"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Insert+KP_7 to flat review home",
    ["BRAILLE LINE:  'Preferences Help $l'",
     "     VISIBLE:  'Preferences Help $l', cursor=1",
     "SPEECH OUTPUT: 'Preferences Help'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_6"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Insert+KP_6 to flat review below",
    ["KNOWN ISSUE: gtk-demo's toolbar widgets lack names that were present in the past",
     "BRAILLE LINE:  'push button push button panel push button $l'",
     "     VISIBLE:  'push button push button panel pu', cursor=1",
     "SPEECH OUTPUT: 'push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_4"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Insert+KP_4 to flat review above",
    ["BRAILLE LINE:  'Preferences Help $l'",
     "     VISIBLE:  'Preferences Help $l', cursor=1",
     "SPEECH OUTPUT: 'Preferences'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Subtract"))
sequence.append(utils.AssertPresentationAction(
    "KP_Subtract to exit flat review",
    ["BRAILLE LINE:  'Leaving flat review.'",
     "     VISIBLE:  'Leaving flat review.', cursor=0",
     "BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "SPEECH OUTPUT: 'Leaving flat review.' voice=system"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
