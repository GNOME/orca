#!/usr/bin/python

"""Test presentation of spelling errors in text."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

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
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=18",
     "SPEECH OUTPUT: 'space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "2. Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=17",
     "SPEECH OUTPUT: 'dot'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "3. Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=16",
     "SPEECH OUTPUT: 'misspelled'",
     "SPEECH OUTPUT: 't'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "4. Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=15",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "5. Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=14",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "6. Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=13",
     "SPEECH OUTPUT: 'e'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "7. Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=12",
     "SPEECH OUTPUT: 't'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "8. Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=11",
     "SPEECH OUTPUT: 'space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "9. Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=10",
     "SPEECH OUTPUT: 'a'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "10. Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=9",
     "SPEECH OUTPUT: 'space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "11. Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=8",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "12. Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=7",
     "SPEECH OUTPUT: 'i'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "13. Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=6",
     "SPEECH OUTPUT: 'space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "14. Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=5",
     "SPEECH OUTPUT: 'misspelled'",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "15. Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=4",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "16. Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=3",
     "SPEECH OUTPUT: 'i'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "17. Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=2",
     "SPEECH OUTPUT: 'h'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Left"))
sequence.append(utils.AssertPresentationAction(
    "18. Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=1",
     "SPEECH OUTPUT: 'T'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "19. Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=2",
     "SPEECH OUTPUT: 'h'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "20. Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=3",
     "SPEECH OUTPUT: 'i'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "21. Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=4",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "22. Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=5",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "23. Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=6",
     "SPEECH OUTPUT: 'space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "24. Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=7",
     "SPEECH OUTPUT: 'i'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "25. Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=8",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "26. Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=9",
     "SPEECH OUTPUT: 'space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "27. Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=10",
     "SPEECH OUTPUT: 'a'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "28. Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=11",
     "SPEECH OUTPUT: 'space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "29. Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=12",
     "SPEECH OUTPUT: 'misspelled'",
     "SPEECH OUTPUT: 't'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "30. Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=13",
     "SPEECH OUTPUT: 'e'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "31. Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=14",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "32. Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=15",
     "SPEECH OUTPUT: 's'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "33. Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=16",
     "SPEECH OUTPUT: 't'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "34. Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=17",
     "SPEECH OUTPUT: 'dot'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "35. Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=18",
     "SPEECH OUTPUT: 'space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "36. Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=19",
     "SPEECH OUTPUT: 'blank' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "37. Control Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=12",
     "SPEECH OUTPUT: 'misspelled' voice=system",
     "SPEECH OUTPUT: 'tesst. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "38. Control Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=10",
     "SPEECH OUTPUT: 'a '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "39. Control Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=7",
     "SPEECH OUTPUT: 'is '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Left"))
sequence.append(utils.AssertPresentationAction(
    "40. Control Left",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=1",
     "SPEECH OUTPUT: 'misspelled'",
     "SPEECH OUTPUT: 'Thiss '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("f"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "41. Insert+f",
    ["SPEECH OUTPUT: 'size 9pt' voice=system",
     "SPEECH OUTPUT: 'family name DejaVu Sans Mono' voice=system",
     "SPEECH OUTPUT: 'weight 400' voice=system",
     "SPEECH OUTPUT: 'style normal' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "42. Control Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=6",
     "SPEECH OUTPUT: 'Thiss '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "43. Control Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=9",
     "SPEECH OUTPUT: 'is '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "44. Control Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=11",
     "SPEECH OUTPUT: 'a '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(utils.AssertPresentationAction(
    "45. Control Right",
    ["BRAILLE LINE:  'Thiss is a tesst.  $l'",
     "     VISIBLE:  'Thiss is a tesst.  $l', cursor=18",
     "SPEECH OUTPUT: 'misspelled'",
     "SPEECH OUTPUT: 'tesst. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(KeyComboAction("f"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "46. Insert+f",
    ["SPEECH OUTPUT: 'size 9pt' voice=system",
     "SPEECH OUTPUT: 'family name DejaVu Sans Mono' voice=system",
     "SPEECH OUTPUT: 'weight 400' voice=system",
     "SPEECH OUTPUT: 'style normal' voice=system"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
