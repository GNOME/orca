#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "1. Next form field",
    ["BRAILLE LINE:  'Type something rather amusing here:  $l'",
     "     VISIBLE:  ' something rather amusing here: ', cursor=32",
     "SPEECH OUTPUT: 'Type something rather amusing here: entry.'"]))

sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "2. Next form field",
    ["BRAILLE LINE:  'Amusing numbers fall between  $l'",
     "     VISIBLE:  'Amusing numbers fall between  $l', cursor=29",
     "SPEECH OUTPUT: 'Amusing numbers fall between entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "3. Next form field",
    ["BRAILLE LINE:  'and  $l'",
     "     VISIBLE:  'and  $l', cursor=4",
     "SPEECH OUTPUT: 'and entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "4. Next form field",
    ["BRAILLE LINE:  'I'm a label  $l'",
     "     VISIBLE:  'I'm a label  $l', cursor=12",
     "SPEECH OUTPUT: 'I'm a label entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "5. Next form field",
    ["BRAILLE LINE:  'Am I a label as well?  $l'",
     "     VISIBLE:  'Am I a label as well?  $l', cursor=22",
     "SPEECH OUTPUT: 'Am I a label as well? entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "6. Next form field",
    ["BRAILLE LINE:  'Looking at what follows visually, I'm not sure what I would type/i.e. what the labels are.  $l'",
     "     VISIBLE:  ' type/i.e. what the labels are. ', cursor=32",
     "SPEECH OUTPUT: 'Looking at what follows visually, I'm not sure what I would type/i.e. what the labels are. entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "7. Next form field",
    ["BRAILLE LINE:  'Distance doesn't count on the left  $l'",
     "     VISIBLE:  'tance doesn't count on the left ', cursor=32",
     "SPEECH OUTPUT: 'Distance doesn't count on the left entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "8. Next form field",
    ["BRAILLE LINE:  'First Name  $l'",
     "     VISIBLE:  'First Name  $l', cursor=11",
     "SPEECH OUTPUT: 'First Name entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "9. Next form field",
    ["BRAILLE LINE:  'M.I.  $l'",
     "     VISIBLE:  'M.I.  $l', cursor=5",
     "SPEECH OUTPUT: 'M.I. entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "10. Next form field",
    ["BRAILLE LINE:  'Last Name  $l'",
     "     VISIBLE:  'Last Name  $l', cursor=10",
     "SPEECH OUTPUT: 'Last Name entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "11. Next form field",
    ["BRAILLE LINE:  'First name  $l'",
     "     VISIBLE:  'First name  $l', cursor=11",
     "SPEECH OUTPUT: 'First name entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "12. Next form field",
    ["BRAILLE LINE:  'Middle initial  $l'",
     "     VISIBLE:  'Middle initial  $l', cursor=15",
     "SPEECH OUTPUT: 'Middle initial entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "13. Next form field",
    ["BRAILLE LINE:  'Last name  $l'",
     "     VISIBLE:  'Last name  $l', cursor=10",
     "SPEECH OUTPUT: 'Last name entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "14. Next form field",
    ["BRAILLE LINE:  'First Name  $l'",
     "     VISIBLE:  'First Name  $l', cursor=11",
     "SPEECH OUTPUT: 'First Name entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "15. Next form field",
    ["BRAILLE LINE:  'Middle initial  $l'",
     "     VISIBLE:  'Middle initial  $l', cursor=15",
     "SPEECH OUTPUT: 'Middle initial entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "16. Next form field",
    ["BRAILLE LINE:  'Last name  $l'",
     "     VISIBLE:  'Last name  $l', cursor=10",
     "SPEECH OUTPUT: 'Last name entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "17. Next form field",
    ["BRAILLE LINE:  'Given name  $l'",
     "     VISIBLE:  'Given name  $l', cursor=11",
     "SPEECH OUTPUT: 'Given name entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "18. Next form field",
    ["BRAILLE LINE:  'initial  $l'",
     "     VISIBLE:  'initial  $l', cursor=8",
     "SPEECH OUTPUT: 'initial entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "19. Next form field",
    ["BRAILLE LINE:  'Surname  $l'",
     "     VISIBLE:  'Surname  $l', cursor=8",
     "SPEECH OUTPUT: 'Surname entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "20. Next form field",
    ["BRAILLE LINE:  'First name  $l'",
     "     VISIBLE:  'First name  $l', cursor=11",
     "SPEECH OUTPUT: 'First name entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "21. Next form field",
    ["BRAILLE LINE:  'Middle initial  $l'",
     "     VISIBLE:  'Middle initial  $l', cursor=15",
     "SPEECH OUTPUT: 'Middle initial entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "22. Next form field",
    ["BRAILLE LINE:  'Last name  $l'",
     "     VISIBLE:  'Last name  $l', cursor=10",
     "SPEECH OUTPUT: 'Last name entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "23. Next form field",
    ["BRAILLE LINE:  'First name  $l'",
     "     VISIBLE:  'First name  $l', cursor=11",
     "SPEECH OUTPUT: 'First name entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "24. Next form field",
    ["BRAILLE LINE:  'Middle initial  $l'",
     "     VISIBLE:  'Middle initial  $l', cursor=15",
     "SPEECH OUTPUT: 'Middle initial entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "25. Next form field",
    ["BRAILLE LINE:  'Last name  $l'",
     "     VISIBLE:  'Last name  $l', cursor=10",
     "SPEECH OUTPUT: 'Last name entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "26. Next form field",
    ["BRAILLE LINE:  'patched image  $l'",
     "     VISIBLE:  'patched image  $l', cursor=14",
     "SPEECH OUTPUT: 'patched image entry.'"]))


sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "27. Next form field",
    ["BRAILLE LINE:  'First name  $l'",
     "     VISIBLE:  'First name  $l', cursor=11",
     "SPEECH OUTPUT: 'First name entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "28. Next form field",
    ["BRAILLE LINE:  'Middle initial  $l'",
     "     VISIBLE:  'Middle initial  $l', cursor=15",
     "SPEECH OUTPUT: 'Middle initial entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "29. Next form field",
    ["BRAILLE LINE:  'Last name  $l'",
     "     VISIBLE:  'Last name  $l', cursor=10",
     "SPEECH OUTPUT: 'Last name entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "30. Next form field",
    ["BRAILLE LINE:  'patched image  $l'",
     "     VISIBLE:  'patched image  $l', cursor=14",
     "SPEECH OUTPUT: 'patched image entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "31. Next form field",
    ["BRAILLE LINE:  'First name  $l'",
     "     VISIBLE:  'First name  $l', cursor=11",
     "SPEECH OUTPUT: 'First name entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "32. Next form field",
    ["BRAILLE LINE:  'Middle initial  $l'",
     "     VISIBLE:  'Middle initial  $l', cursor=15",
     "SPEECH OUTPUT: 'Middle initial entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "33. Next form field",
    ["BRAILLE LINE:  'Last name  $l'",
     "     VISIBLE:  'Last name  $l', cursor=10",
     "SPEECH OUTPUT: 'Last name entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "34. Next form field",
    ["BRAILLE LINE:  'patched image  $l'",
     "     VISIBLE:  'patched image  $l', cursor=14",
     "SPEECH OUTPUT: 'patched image entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "35. Next form field",
    ["BRAILLE LINE:  'bandaid graphic  $l'",
     "     VISIBLE:  'bandaid graphic  $l', cursor=16",
     "SPEECH OUTPUT: 'bandaid graphic entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "36. Next form field",
    ["BRAILLE LINE:  'bandaid graphic redux  $l'",
     "     VISIBLE:  'bandaid graphic redux  $l', cursor=22",
     "SPEECH OUTPUT: 'bandaid graphic redux entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "37. Next form field",
    ["BRAILLE LINE:  'Magic disappearing text trick:  $l'",
     "     VISIBLE:  'Magic disappearing text trick:  ', cursor=0",
     "BRAILLE LINE:  'Magic disappearing text trick:  $l'",
     "     VISIBLE:  'Magic disappearing text trick:  ', cursor=32",
     "SPEECH OUTPUT: 'Magic disappearing text trick: entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "38. Next form field",
    ["BRAILLE LINE:  'Tell me a secret:  $l'",
     "     VISIBLE:  'Tell me a secret:  $l', cursor=19",
     "SPEECH OUTPUT: 'Tell me a secret: password text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "39. Next form field",
    ["BRAILLE LINE:  'Tell me a little more about yourself: I $l'",
     "     VISIBLE:  ' a little more about yourself: I', cursor=32",
     "SPEECH OUTPUT: 'Tell me a little more about yourself: entry I",
     "am a monkey with a long tail. I like to swing from trees and eat",
     "bananas. I've recently taken up typing and plan to write my memoirs. .'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "40. Next form field",
    ["BRAILLE LINE:  'Wrapping to top.'",
     "     VISIBLE:  'Wrapping to top.', cursor=0",
     "BRAILLE LINE:  'Type something rather amusing here:  $l'",
     "     VISIBLE:  ' something rather amusing here: ', cursor=32",
     "SPEECH OUTPUT: 'Wrapping to top.' voice=system",
     "SPEECH OUTPUT: 'Type something rather amusing here: entry.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
