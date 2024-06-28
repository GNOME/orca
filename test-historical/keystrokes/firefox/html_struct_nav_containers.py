#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("<Control>r"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Ctrl+Home",
    ["BRAILLE LINE:  '1. item 1'",
     "     VISIBLE:  '1. item 1', cursor=1",
     "SPEECH OUTPUT: '1. item 1.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("comma"))
sequence.append(utils.AssertPresentationAction(
    "2. comma",
    ["BRAILLE LINE:  'Cell 1'",
     "     VISIBLE:  'Cell 1', cursor=1",
     "SPEECH OUTPUT: 'leaving list.'",
     "SPEECH OUTPUT: 'Cell 1.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("comma"))
sequence.append(utils.AssertPresentationAction(
    "3. comma",
    ["BRAILLE LINE:  'A paragraph without much text.'",
     "     VISIBLE:  'A paragraph without much text.', cursor=1",
     "SPEECH OUTPUT: 'A paragraph without much text.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("comma"))
sequence.append(utils.AssertPresentationAction(
    "4. comma",
    ["BRAILLE LINE:  'Not in a container.'",
     "     VISIBLE:  'Not in a container.', cursor=0",
     "SPEECH OUTPUT: 'Not in a container.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Down",
    ["BRAILLE LINE:  'A paragraph without much text.'",
     "     VISIBLE:  'A paragraph without much text.', cursor=1",
     "BRAILLE LINE:  'Another paragraph without much text.'",
     "     VISIBLE:  'Another paragraph without much t', cursor=1",
     "SPEECH OUTPUT: 'Another paragraph without much text. panel.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("comma"))
sequence.append(utils.AssertPresentationAction(
    "6. comma",
    ["BRAILLE LINE:  'A quoted paragraph without much text.'",
     "     VISIBLE:  'A quoted paragraph without much ', cursor=1",
     "SPEECH OUTPUT: 'block quote.'",
     "SPEECH OUTPUT: 'A quoted paragraph without much text.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("comma"))
sequence.append(utils.AssertPresentationAction(
    "7. comma",
    ["BRAILLE LINE:  '• item 3'",
     "     VISIBLE:  '• item 3', cursor=1",
     "SPEECH OUTPUT: 'leaving blockquote.'",
     "SPEECH OUTPUT: 'List with 2 items.'",
     "SPEECH OUTPUT: '• item 3.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("comma"))
sequence.append(utils.AssertPresentationAction(
    "8. comma",
    ["BRAILLE LINE:  'End of container.'",
     "     VISIBLE:  'End of container.', cursor=0",
     "BRAILLE LINE:  '• item 4'",
     "     VISIBLE:  '• item 4', cursor=1",
     "SPEECH OUTPUT: 'End of container.' voice=system",
     "SPEECH OUTPUT: '• item 4.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("comma"))
sequence.append(utils.AssertPresentationAction(
    "9. comma",
    ["BRAILLE LINE:  'End of container.'",
     "     VISIBLE:  'End of container.', cursor=0",
     "BRAILLE LINE:  '• item 4'",
     "     VISIBLE:  '• item 4', cursor=1",
     "SPEECH OUTPUT: 'End of container.' voice=system",
     "SPEECH OUTPUT: '• item 4.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>comma"))
sequence.append(utils.AssertPresentationAction(
    "10. shift+comma",
    ["BRAILLE LINE:  '• item 3'",
     "     VISIBLE:  '• item 3', cursor=1",
     "SPEECH OUTPUT: '• item 3.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "11. up",
    ["BRAILLE LINE:  'Another quoted paragraph without much text.'",
     "     VISIBLE:  'Another quoted paragraph without', cursor=1",
     "SPEECH OUTPUT: 'leaving list.'",
     "SPEECH OUTPUT: 'block quote.'",
     "SPEECH OUTPUT: 'Another quoted paragraph without much text.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>comma"))
sequence.append(utils.AssertPresentationAction(
    "12. shift+comma",
    ["BRAILLE LINE:  'A quoted paragraph without much text.'",
     "     VISIBLE:  'A quoted paragraph without much ', cursor=1",
     "SPEECH OUTPUT: 'A quoted paragraph without much text.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "13. up",
    ["BRAILLE LINE:  'Another paragraph without much text.'",
     "     VISIBLE:  'Another paragraph without much t', cursor=1",
     "SPEECH OUTPUT: 'leaving blockquote.'",
     "SPEECH OUTPUT: 'Another paragraph without much text. panel.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>comma"))
sequence.append(utils.AssertPresentationAction(
    "14. shift+comma",
    ["BRAILLE LINE:  'Another paragraph without much text.'",
     "     VISIBLE:  'Another paragraph without much t', cursor=1",
     "SPEECH OUTPUT: 'Another paragraph without much text.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "15. up",
    ["BRAILLE LINE:  'A paragraph without much text.'",
     "     VISIBLE:  'A paragraph without much text.', cursor=1",
     "SPEECH OUTPUT: 'A paragraph without much text.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>comma"))
sequence.append(utils.AssertPresentationAction(
    "16. shift+comma",
    ["BRAILLE LINE:  'Not in a container.'",
     "     VISIBLE:  'Not in a container.', cursor=0",
     "SPEECH OUTPUT: 'Not in a container.' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "17. up",
    ["BRAILLE LINE:  'A paragraph without much text.'",
     "     VISIBLE:  'A paragraph without much text.', cursor=1",
     "BRAILLE LINE:  'Cell 3 Cell 4 (it's the last one)'",
     "     VISIBLE:  'Cell 3 Cell 4 (it's the last one', cursor=1",
     "SPEECH OUTPUT: 'Cell 3.'",
     "SPEECH OUTPUT: 'Cell 4 (it's the last one)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>comma"))
sequence.append(utils.AssertPresentationAction(
    "18. shift+comma",
    ["BRAILLE LINE:  'Cell 1'",
     "     VISIBLE:  'Cell 1', cursor=1",
     "SPEECH OUTPUT: 'Cell 1.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "19. up",
    ["BRAILLE LINE:  '2. item 2'",
     "     VISIBLE:  '2. item 2', cursor=1",
     "SPEECH OUTPUT: 'List with 2 items.'",
     "SPEECH OUTPUT: '2. item 2.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>comma"))
sequence.append(utils.AssertPresentationAction(
    "20. shift+comma",
    ["BRAILLE LINE:  '1. item 1'",
     "     VISIBLE:  '1. item 1', cursor=1",
     "SPEECH OUTPUT: '1. item 1.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
