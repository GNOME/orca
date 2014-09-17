#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "1. Next form field",
    ["BRAILLE LINE:  'Type something rather amusing here:  $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'Type something rather amusing here: entry'"]))

sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "2. Next form field",
    ["BRAILLE LINE:  'Amusing numbers fall between  $l and  $l.'",
     "     VISIBLE:  ' $l and  $l.', cursor=1",
     "SPEECH OUTPUT: 'Amusing numbers fall between entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "3. Next form field",
    ["BRAILLE LINE:  'Amusing numbers fall between  $l and  $l.'",
     "     VISIBLE:  ' $l.', cursor=1",
     "SPEECH OUTPUT: 'and entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "4. Next form field",
    ["BRAILLE LINE:  ' $l I'm a label'",
     "     VISIBLE:  ' $l I'm a label', cursor=1",
     "SPEECH OUTPUT: 'I'm a label entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "5. Next form field",
    ["BRAILLE LINE:  ' $l Am I a label as well?'",
     "     VISIBLE:  ' $l Am I a label as well?', cursor=1",
     "SPEECH OUTPUT: 'Am I a label as well? entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "6. Next form field",
    ["KNOWN ISSUE: As the text suggests, we probably shouldn't be guessing this.",
     "BRAILLE LINE:  ' $l Too far away to be a label.'",
     "     VISIBLE:  ' $l Too far away to be a label.', cursor=1",
     "SPEECH OUTPUT: 'Too far away to be a label. entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "7. Next form field",
    ["BRAILLE LINE:  'Distance doesn't count on the left $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'Distance doesn't count on the left entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "8. Next form field",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'First Name entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "9. Next form field",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'M.I. entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "10. Next form field",
    ["BRAILLE LINE:  ' $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'Last Name entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "11. Next form field",
    ["BRAILLE LINE:  ' $l $l $l'",
     "     VISIBLE:  ' $l $l $l', cursor=1",
     "SPEECH OUTPUT: 'First name entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "12. Next form field",
    ["BRAILLE LINE:  ' $l $l $l'",
     "     VISIBLE:  ' $l $l $l', cursor=4",
     "SPEECH OUTPUT: 'Middle",
     "initial entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "13. Next form field",
    ["BRAILLE LINE:  ' $l $l $l'",
     "     VISIBLE:  ' $l $l $l', cursor=7",
     "SPEECH OUTPUT: 'Last name entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "14. Next form field",
    ["BRAILLE LINE:  ' $l $l $l'",
     "     VISIBLE:  ' $l $l $l', cursor=1",
     "SPEECH OUTPUT: 'First Name entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "15. Next form field",
    ["BRAILLE LINE:  ' $l $l $l'",
     "     VISIBLE:  ' $l $l $l', cursor=4",
     "SPEECH OUTPUT: 'Middle",
     "initial entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "16. Next form field",
    ["BRAILLE LINE:  ' $l $l $l'",
     "     VISIBLE:  ' $l $l $l', cursor=7",
     "SPEECH OUTPUT: 'Last name entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "17. Next form field",
    ["BRAILLE LINE:  ' $l $l $l'",
     "     VISIBLE:  ' $l $l $l', cursor=1",
     "SPEECH OUTPUT: 'Given name entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "18. Next form field",
    ["BRAILLE LINE:  ' $l $l $l'",
     "     VISIBLE:  ' $l $l $l', cursor=4",
     "SPEECH OUTPUT: 'initial entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "19. Next form field",
    ["BRAILLE LINE:  ' $l $l $l'",
     "     VISIBLE:  ' $l $l $l', cursor=7",
     "SPEECH OUTPUT: 'Surname entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "20. Next form field",
    ["BRAILLE LINE:  ' $l $l $l'",
     "     VISIBLE:  ' $l $l $l', cursor=1",
     "SPEECH OUTPUT: 'First name entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "21. Next form field",
    ["BRAILLE LINE:  ' $l $l $l'",
     "     VISIBLE:  ' $l $l $l', cursor=4",
     "SPEECH OUTPUT: 'Middle",
     "initial entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "22. Next form field",
    ["BRAILLE LINE:  ' $l $l $l'",
     "     VISIBLE:  ' $l $l $l', cursor=7",
     "SPEECH OUTPUT: 'Last name entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "23. Next form field",
    ["BRAILLE LINE:  ' $l $l $l $l'",
     "     VISIBLE:  ' $l $l $l $l', cursor=1",
     "SPEECH OUTPUT: 'First name entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "24. Next form field",
    ["BRAILLE LINE:  ' $l $l $l $l'",
     "     VISIBLE:  ' $l $l $l $l', cursor=4",
     "SPEECH OUTPUT: 'Middle",
     "initial entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "25. Next form field",
    ["BRAILLE LINE:  ' $l $l $l $l'",
     "     VISIBLE:  ' $l $l $l $l', cursor=7",
     "SPEECH OUTPUT: 'Last name entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "26. Next form field",
    ["BRAILLE LINE:  ' $l $l $l $l'",
     "     VISIBLE:  ' $l $l $l $l', cursor=10",
     "SPEECH OUTPUT: 'patched image entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "27. Next form field",
    ["BRAILLE LINE:  ' $l $l $l $l'",
     "     VISIBLE:  ' $l $l $l $l', cursor=1",
     "SPEECH OUTPUT: 'First name entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "28. Next form field",
    ["BRAILLE LINE:  ' $l $l $l $l'",
     "     VISIBLE:  ' $l $l $l $l', cursor=4",
     "SPEECH OUTPUT: 'Middle",
     "initial entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "29. Next form field",
    ["BRAILLE LINE:  ' $l $l $l $l'",
     "     VISIBLE:  ' $l $l $l $l', cursor=7",
     "SPEECH OUTPUT: 'Last name entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "30. Next form field",
    ["BRAILLE LINE:  ' $l $l $l $l'",
     "     VISIBLE:  ' $l $l $l $l', cursor=10",
     "SPEECH OUTPUT: 'patched image entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "31. Next form field",
    ["BRAILLE LINE:  ' $l $l $l $l'",
     "     VISIBLE:  ' $l $l $l $l', cursor=1",
     "SPEECH OUTPUT: 'First name entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "32. Next form field",
    ["BRAILLE LINE:  ' $l $l $l $l'",
     "     VISIBLE:  ' $l $l $l $l', cursor=4",
     "SPEECH OUTPUT: 'Middle",
     "initial entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "33. Next form field",
    ["BRAILLE LINE:  ' $l $l $l $l'",
     "     VISIBLE:  ' $l $l $l $l', cursor=7",
     "SPEECH OUTPUT: 'Last name entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "34. Next form field",
    ["BRAILLE LINE:  ' $l $l $l $l'",
     "     VISIBLE:  ' $l $l $l $l', cursor=10",
     "SPEECH OUTPUT: 'patched image entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "35. Next form field",
    ["BRAILLE LINE:  'bandaid graphic $l'",
     "     VISIBLE:  'bandaid graphic $l', cursor=16",
     "SPEECH OUTPUT: 'bandaid graphic entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "36. Next form field",
    ["BRAILLE LINE:  ' $l bandaid graphic redux'",
     "     VISIBLE:  ' $l bandaid graphic redux', cursor=1",
     "SPEECH OUTPUT: 'bandaid graphic redux entry'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "37. Next form field",
    ["BRAILLE LINE:  'Magic disappearing text trick:  $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "BRAILLE LINE:  'Magic disappearing text trick:  $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'Magic disappearing text trick: entry'"]))

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
    ["BRAILLE LINE:  'I $l'",
     "     VISIBLE:  'I $l', cursor=1",
     "SPEECH OUTPUT: 'Tell me a little more about yourself: entry I",
     "am a monkey with a long tail. I like to swing from trees and eat",
     "bananas. I've recently taken up typing and plan to write my memoirs. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "40. Next form field",
    ["BRAILLE LINE:  'Wrapping to top.'",
     "     VISIBLE:  'Wrapping to top.', cursor=0",
     "BRAILLE LINE:  'Type something rather amusing here:  $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'Wrapping to top.' voice=system",
     "SPEECH OUTPUT: 'Type something rather amusing here: entry'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
