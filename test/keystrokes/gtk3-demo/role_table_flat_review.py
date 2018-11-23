#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyComboAction("End"))
sequence.append(KeyComboAction("<Shift>Right"))
sequence.append(KeyComboAction("Down"))
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Down",
    ["BRAILLE LINE:  'gtk3-demo application Editable Cells frame table Number column header 5 packages of noodles ",
     "     VISIBLE:  '5 packages of noodles ', cursor=1",
     "SPEECH OUTPUT: '5.'",
     "SPEECH OUTPUT: 'packages of noodles.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down",
    ["BRAILLE LINE:  'gtk3-demo application Editable Cells frame table Number column header 2 packages of chocolate chip cookies ",
     "     VISIBLE:  '2 packages of chocolate chip coo', cursor=1",
     "SPEECH OUTPUT: '2.'",
     "SPEECH OUTPUT: 'packages of chocolate chip cookies.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Subtract"))
sequence.append(utils.AssertPresentationAction(
    "3. Enter flat review",
    ["BRAILLE LINE:  'Entering flat review.'",
     "     VISIBLE:  'Entering flat review.', cursor=0",
     "BRAILLE LINE:  '2 packages of chocolate chip cookies $l'",
     "     VISIBLE:  '2 packages of chocolate chip coo', cursor=1",
     "SPEECH OUTPUT: 'Entering flat review.' voice=system",
     "SPEECH OUTPUT: '2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_8"))
sequence.append(utils.AssertPresentationAction(
    "4. Review current line",
    ["BRAILLE LINE:  '2 packages of chocolate chip cookies $l'",
     "     VISIBLE:  '2 packages of chocolate chip coo', cursor=1",
     "SPEECH OUTPUT: '2 packages of chocolate chip cookies'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_5"))
sequence.append(utils.AssertPresentationAction(
    "5. Review current word'",
    ["BRAILLE LINE:  '2 packages of chocolate chip cookies $l'",
     "     VISIBLE:  '2 packages of chocolate chip coo', cursor=1",
     "SPEECH OUTPUT: '2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_2"))
sequence.append(utils.AssertPresentationAction(
    "6. Review current char'",
    ["BRAILLE LINE:  '2 packages of chocolate chip cookies $l'",
     "     VISIBLE:  '2 packages of chocolate chip coo', cursor=1",
     "SPEECH OUTPUT: '2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "7. Review next word'",
    ["BRAILLE LINE:  '2 packages of chocolate chip cookies $l'",
     "     VISIBLE:  'packages of chocolate chip cooki', cursor=1",
     "SPEECH OUTPUT: 'packages '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_6"))
sequence.append(utils.AssertPresentationAction(
    "8. Review next word'",
    ["BRAILLE LINE:  '2 packages of chocolate chip cookies $l'",
     "     VISIBLE:  'packages of chocolate chip cooki', cursor=10",
     "SPEECH OUTPUT: 'of '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_3"))
sequence.append(utils.AssertPresentationAction(
    "9. Review next char'",
    ["BRAILLE LINE:  '2 packages of chocolate chip cookies $l'",
     "     VISIBLE:  'packages of chocolate chip cooki', cursor=11",
     "SPEECH OUTPUT: 'f'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_3"))
sequence.append(utils.AssertPresentationAction(
    "10. Review next char'",
    ["BRAILLE LINE:  '2 packages of chocolate chip cookies $l'",
     "     VISIBLE:  'packages of chocolate chip cooki', cursor=12",
     "SPEECH OUTPUT: 'space'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_1"))
sequence.append(utils.AssertPresentationAction(
    "11. Review previous char'",
    ["BRAILLE LINE:  '2 packages of chocolate chip cookies $l'",
     "     VISIBLE:  'packages of chocolate chip cooki', cursor=11",
     "SPEECH OUTPUT: 'f'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_1"))
sequence.append(utils.AssertPresentationAction(
    "12. Review previous char'",
    ["BRAILLE LINE:  '2 packages of chocolate chip cookies $l'",
     "     VISIBLE:  'packages of chocolate chip cooki', cursor=10",
     "SPEECH OUTPUT: 'o'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_4"))
sequence.append(utils.AssertPresentationAction(
    "13. Review previous word'",
    ["BRAILLE LINE:  '2 packages of chocolate chip cookies $l'",
     "     VISIBLE:  'packages of chocolate chip cooki', cursor=1",
     "SPEECH OUTPUT: 'packages '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_4"))
sequence.append(utils.AssertPresentationAction(
    "14. Review previous word'",
    ["BRAILLE LINE:  '2 packages of chocolate chip cookies $l'",
     "     VISIBLE:  '2 packages of chocolate chip coo', cursor=1",
     "SPEECH OUTPUT: '2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_4"))
sequence.append(utils.AssertPresentationAction(
    "15. Review previous word'",
    ["BRAILLE LINE:  '5 packages of noodles $l'",
     "     VISIBLE:  '5 packages of noodles $l', cursor=15",
     "SPEECH OUTPUT: 'noodles'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "16. Review next line",
    ["BRAILLE LINE:  '2 packages of chocolate chip cookies $l'",
     "     VISIBLE:  '2 packages of chocolate chip coo', cursor=1",
     "SPEECH OUTPUT: '2 packages of chocolate chip cookies'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "17. Review next line",
    ["BRAILLE LINE:  '1 can vanilla ice cream $l'",
     "     VISIBLE:  '1 can vanilla ice cream $l', cursor=1",
     "SPEECH OUTPUT: '1 can vanilla ice cream'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_9"))
sequence.append(utils.AssertPresentationAction(
    "18. Review next line",
    ["BRAILLE LINE:  'horizontal scroll bar 0% $l'",
     "     VISIBLE:  'horizontal scroll bar 0% $l', cursor=1",
     "SPEECH OUTPUT: 'horizontal scroll bar 0 percent.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "19. Review previous line",
    ["BRAILLE LINE:  '1 can vanilla ice cream $l'",
     "     VISIBLE:  '1 can vanilla ice cream $l', cursor=1",
     "SPEECH OUTPUT: '1 can vanilla ice cream'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "20. Review previous line",
    ["BRAILLE LINE:  '2 packages of chocolate chip cookies $l'",
     "     VISIBLE:  '2 packages of chocolate chip coo', cursor=1",
     "SPEECH OUTPUT: '2 packages of chocolate chip cookies'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "21. Review previous line",
    ["BRAILLE LINE:  '5 packages of noodles $l'",
     "     VISIBLE:  '5 packages of noodles $l', cursor=1",
     "SPEECH OUTPUT: '5 packages of noodles"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "22. Review previous line",
    ["BRAILLE LINE:  '3 bottles of coke $l'",
     "     VISIBLE:  '3 bottles of coke $l', cursor=1",
     "SPEECH OUTPUT: '3 bottles of coke'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "23. Review previous line",
    ["BRAILLE LINE:  'vertical scroll bar 0% $l'",
     "     VISIBLE:  'vertical scroll bar 0% $l', cursor=1",
     "SPEECH OUTPUT: 'vertical scroll bar 0 percent."]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "24. Review previous line",
    ["BRAILLE LINE:  'Number Product Yummy $l'",
     "     VISIBLE:  'Number Product Yummy $l', cursor=1",
     "SPEECH OUTPUT: 'Number Product Yummy"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "25. Review previous line",
    ["BRAILLE LINE:  'Shopping list (you can edit the cells!) $l'",
     "     VISIBLE:  'Shopping list (you can edit the ', cursor=1",
     "SPEECH OUTPUT: 'Shopping list (you can edit the cells!)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_7"))
sequence.append(utils.AssertPresentationAction(
    "26. Review previous line",
    [""]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
