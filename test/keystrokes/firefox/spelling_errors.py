#!/usr/bin/python

"""Test presentation of spelling errors in text."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("Tab"))
sequence.append(KeyComboAction("<Control>a"))
sequence.append(KeyComboAction("Delete"))
sequence.append(TypeAction("Thiss is a tesst. "))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "1. Left",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=31",
     "SPEECH OUTPUT: 'space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "2. Left",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=30",
     "SPEECH OUTPUT: 'dot'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "3. Left",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=29",
     "SPEECH OUTPUT: 'misspelled'",
     "SPEECH OUTPUT: 't'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "4. Left",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=28",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "5. Left",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=27",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "6. Left",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=26",
     "SPEECH OUTPUT: 'e'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "7. Left",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=25",
     "SPEECH OUTPUT: 't'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "8. Left",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=24",
     "SPEECH OUTPUT: 'space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "9. Left",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=23",
     "SPEECH OUTPUT: 'a'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "10. Left",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=22",
     "SPEECH OUTPUT: 'space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "11. Left",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=21",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "12. Left",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=20",
     "SPEECH OUTPUT: 'i'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "13. Left",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=19",
     "SPEECH OUTPUT: 'space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "14. Left",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=18",
     "SPEECH OUTPUT: 'misspelled'",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "15. Left",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=17",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "16. Left",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=16",
     "SPEECH OUTPUT: 'i'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "17. Left",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=15",
     "SPEECH OUTPUT: 'h'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "18. Left",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=14",
     "SPEECH OUTPUT: 'T'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "19. Right",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=15",
     "SPEECH OUTPUT: 'h'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "20. Right",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=16",
     "SPEECH OUTPUT: 'i'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "21. Right",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=17",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "22. Right",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=18",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "23. Right",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=19",
     "SPEECH OUTPUT: 'space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "24. Right",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=20",
     "SPEECH OUTPUT: 'i'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "25. Right",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=21",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "26. Right",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=22",
     "SPEECH OUTPUT: 'space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "27. Right",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=23",
     "SPEECH OUTPUT: 'a'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "28. Right",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=24",
     "SPEECH OUTPUT: 'space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "29. Right",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=25",
     "SPEECH OUTPUT: 'misspelled'",
     "SPEECH OUTPUT: 't'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "30. Right",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=26",
     "SPEECH OUTPUT: 'e'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "31. Right",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=27",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "32. Right",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=28",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "33. Right",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=29",
     "SPEECH OUTPUT: 't'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "34. Right",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=30",
     "SPEECH OUTPUT: 'dot'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "35. Right",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=31",
     "SPEECH OUTPUT: 'space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "36. Right",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=32",
     "SPEECH OUTPUT: 'blank' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "37. Control Left",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=25",
     "SPEECH OUTPUT: 'misspelled' voice=system",
     "SPEECH OUTPUT: 'tesst. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "38. Control Left",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=23",
     "SPEECH OUTPUT: 'a '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "39. Control Left",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=20",
     "SPEECH OUTPUT: 'is '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "40. Control Left",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=14",
     "SPEECH OUTPUT: 'misspelled'",
     "SPEECH OUTPUT: 'Thiss '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("f"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "41. Insert+f",
    ["SPEECH OUTPUT: 'size: 12' voice=system",
     "SPEECH OUTPUT: 'family name: DejaVu Sans Mono' voice=system",
     "SPEECH OUTPUT: 'misspelled' voice=system",
     "SPEECH OUTPUT: 'foreground color: black' voice=system",
     "SPEECH OUTPUT: 'background color: white' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "42. Control Right",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=19",
     "SPEECH OUTPUT: 'Thiss '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "43. Control Right",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=22",
     "SPEECH OUTPUT: 'is '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "44. Control Right",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=24",
     "SPEECH OUTPUT: 'a '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "45. Control Right",
    ["BRAILLE LINE:  'Tell me a little more about yourself: Thiss is a tesst.  $l'",
     "     VISIBLE:  'ut yourself: Thiss is a tesst.  ', cursor=31",
     "SPEECH OUTPUT: 'misspelled'",
     "SPEECH OUTPUT: 'tesst. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("f"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "46. Insert+f",
    ["SPEECH OUTPUT: 'size: 12' voice=system",
     "SPEECH OUTPUT: 'family name: DejaVu Sans Mono' voice=system",
     "SPEECH OUTPUT: 'foreground color: black' voice=system",
     "SPEECH OUTPUT: 'background color: white' voice=system"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
