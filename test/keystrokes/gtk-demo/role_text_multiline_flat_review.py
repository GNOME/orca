#!/usr/bin/python

"""Test of flat review of text and a toolbar."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("<Control>f"))
sequence.append(TypeAction("Application main window"))
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))

sequence.append(KeyComboAction("Tab"))
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
    "1. KP_Subtract to enter flat review",
    ["BRAILLE LINE:  'Entering flat review.'",
     "     VISIBLE:  'Entering flat review.', cursor=0",
     "BRAILLE LINE:  'PLEASE DO NOT PANIC. $l'",
     "     VISIBLE:  'PLEASE DO NOT PANIC. $l', cursor=1",
     "SPEECH OUTPUT: 'Entering flat review.' voice=system",
     "SPEECH OUTPUT: 'PLEASE '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "2. KP_8 to flat review 'PLEASE DO NOT PANIC.'",
    ["BRAILLE LINE:  'PLEASE DO NOT PANIC. $l'",
     "     VISIBLE:  'PLEASE DO NOT PANIC. $l', cursor=1",
     "SPEECH OUTPUT: 'PLEASE DO NOT PANIC.",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "3. KP_5 to flat review 'PLEASE '",
    ["BRAILLE LINE:  'PLEASE DO NOT PANIC. $l'",
     "     VISIBLE:  'PLEASE DO NOT PANIC. $l', cursor=1",
     "SPEECH OUTPUT: 'PLEASE '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_2"))
sequence.append(utils.AssertPresentationAction(
    "4. KP_2 to flat review 'P'",
    ["BRAILLE LINE:  'PLEASE DO NOT PANIC. $l'",
     "     VISIBLE:  'PLEASE DO NOT PANIC. $l', cursor=1",
     "SPEECH OUTPUT: 'P'"]))

sequence.append(KeyComboAction("<Control>Home"))
sequence.append(KeyComboAction("Down"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "5. KP_5 to flat review 'This '",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "SPEECH OUTPUT: 'This '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "6. KP_5 2X to spell 'This '",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "SPEECH OUTPUT: 'This '",
     "SPEECH OUTPUT: 'T'",
     "SPEECH OUTPUT: 'h'",
     "SPEECH OUTPUT: 'i'",
     "SPEECH OUTPUT: 's'",
     "SPEECH OUTPUT: 'space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(KeyComboAction("KP_5"))
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "7. KP_5 3X to military spell 'This '",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "SPEECH OUTPUT: 'This '",
     "SPEECH OUTPUT: 'T'",
     "SPEECH OUTPUT: 'h'",
     "SPEECH OUTPUT: 'i'",
     "SPEECH OUTPUT: 's'",
     "SPEECH OUTPUT: 'space'",
     "SPEECH OUTPUT: 'tango'",
     "SPEECH OUTPUT: 'hotel'",
     "SPEECH OUTPUT: 'india'",
     "SPEECH OUTPUT: 'sierra'",
     "SPEECH OUTPUT: ' '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "8. KP_8 to flat review 'This is only a test.'",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "SPEECH OUTPUT: 'This is only a test.",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "9. KP_8 2X to spell 'This is only a test.'",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "SPEECH OUTPUT: 'This is only a test.",
     "'",
     "SPEECH OUTPUT: 'T'",
     "SPEECH OUTPUT: 'h'",
     "SPEECH OUTPUT: 'i'",
     "SPEECH OUTPUT: 's'",
     "SPEECH OUTPUT: 'space'",
     "SPEECH OUTPUT: 'i'",
     "SPEECH OUTPUT: 's'",
     "SPEECH OUTPUT: 'space'",
     "SPEECH OUTPUT: 'o'",
     "SPEECH OUTPUT: 'n'",
     "SPEECH OUTPUT: 'l'",
     "SPEECH OUTPUT: 'y'",
     "SPEECH OUTPUT: 'space'",
     "SPEECH OUTPUT: 'a'",
     "SPEECH OUTPUT: 'space'",
     "SPEECH OUTPUT: 't'",
     "SPEECH OUTPUT: 'e'",
     "SPEECH OUTPUT: 's'",
     "SPEECH OUTPUT: 't'",
     "SPEECH OUTPUT: 'dot'",
     "SPEECH OUTPUT: 'newline'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(KeyComboAction("KP_8"))
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "10. KP_8 3X to military spell 'This is only a test.'",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "SPEECH OUTPUT: 'This is only a test.",
     "'",
     "SPEECH OUTPUT: 'T'",
     "SPEECH OUTPUT: 'h'",
     "SPEECH OUTPUT: 'i'",
     "SPEECH OUTPUT: 's'",
     "SPEECH OUTPUT: 'space'",
     "SPEECH OUTPUT: 'i'",
     "SPEECH OUTPUT: 's'",
     "SPEECH OUTPUT: 'space'",
     "SPEECH OUTPUT: 'o'",
     "SPEECH OUTPUT: 'n'",
     "SPEECH OUTPUT: 'l'",
     "SPEECH OUTPUT: 'y'",
     "SPEECH OUTPUT: 'space'",
     "SPEECH OUTPUT: 'a'",
     "SPEECH OUTPUT: 'space'",
     "SPEECH OUTPUT: 't'",
     "SPEECH OUTPUT: 'e'",
     "SPEECH OUTPUT: 's'",
     "SPEECH OUTPUT: 't'",
     "SPEECH OUTPUT: 'dot'",
     "SPEECH OUTPUT: 'newline'",
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
    "11. KP_2 to flat review 'T'",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "SPEECH OUTPUT: 'T'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_2"))
sequence.append(KeyComboAction("KP_2"))
sequence.append(utils.AssertPresentationAction(
    "12. KP_2 2X to military spell 'T'",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "SPEECH OUTPUT: 'T'",
     "SPEECH OUTPUT: 'tango'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "13. KP_6 to flat review 'is'",
    ["BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=6",
     "SPEECH OUTPUT: 'is '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "14. KP_7 to flat review 'This is a test.' and the scrollbar",
    ["BRAILLE LINE:  'This is a test.  $l'",
     "     VISIBLE:  'This is a test.  $l', cursor=1",
     "SPEECH OUTPUT: 'This is a test. ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "15. KP_7 to flat review toolbar",
    ["BRAILLE LINE:  'Open & y toggle button Quit GTK! $l'",
     "     VISIBLE:  'Open & y toggle button Quit GTK!', cursor=1",
     "SPEECH OUTPUT: 'Open not pressed toggle button Quit GTK!'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "16. KP_7 to flat review menu",
    ["BRAILLE LINE:  'File Preferences Help $l'",
     "     VISIBLE:  'File Preferences Help $l', cursor=1",
     "SPEECH OUTPUT: 'File Preferences Help'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "17. KP_6 to flat review 'Preferences'",
    ["BRAILLE LINE:  'File Preferences Help $l'",
     "     VISIBLE:  'File Preferences Help $l', cursor=6",
     "SPEECH OUTPUT: 'Preferences'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "18. KP_6 to flat review 'Help'",
    ["BRAILLE LINE:  'File Preferences Help $l'",
     "     VISIBLE:  'File Preferences Help $l', cursor=18",
     "SPEECH OUTPUT: 'Help'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_5"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "19. Insert+KP_5 to flat review 'Help' accessible",
    ["SPEECH OUTPUT: 'Help menu.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_9"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "20. Insert+KP_9 to flat review end",
    ["BRAILLE LINE:  'Cursor at row 1 column 0 - 60 chars in document $l'",
     "     VISIBLE:  'chars in document $l', cursor=17",
     "SPEECH OUTPUT: 'Cursor at row 1 column 0 - 60 chars in document'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_7"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "21. Insert+KP_7 to flat review home",
    ["BRAILLE LINE:  'File Preferences Help $l'",
     "     VISIBLE:  'File Preferences Help $l', cursor=1",
     "SPEECH OUTPUT: 'File Preferences Help'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_6"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "22. Insert+KP_6 to flat review below",
    ["BRAILLE LINE:  'Open & y toggle button Quit GTK! $l'",
     "     VISIBLE:  '& y toggle button Quit GTK! $l', cursor=1",
     "SPEECH OUTPUT: 'not pressed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("KP_4"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "23. Insert+KP_4 to flat review above",
    ["BRAILLE LINE:  'File Preferences Help $l'",
     "     VISIBLE:  'File Preferences Help $l', cursor=1",
     "SPEECH OUTPUT: 'File'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Subtract"))
sequence.append(utils.AssertPresentationAction(
    "24. KP_Subtract to exit flat review",
    ["BRAILLE LINE:  'Leaving flat review.'",
     "     VISIBLE:  'Leaving flat review.', cursor=0",
     "BRAILLE LINE:  'This is only a test. $l'",
     "     VISIBLE:  'This is only a test. $l', cursor=1",
     "SPEECH OUTPUT: 'Leaving flat review.' voice=system"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
