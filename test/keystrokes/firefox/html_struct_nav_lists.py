#!/usr/bin/python

"""Test of structural navigation amongst lists."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("l"))
sequence.append(utils.AssertPresentationAction(
    "1. l to first list",
    ["BRAILLE LINE:  '1. remember what the heck we are doing each day'",
     "     VISIBLE:  '1. remember what the heck we are', cursor=1",
     "SPEECH OUTPUT: 'List with 4 items' voice=system",
     "SPEECH OUTPUT: '1. remember what the heck we are doing each day.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("l"))
sequence.append(utils.AssertPresentationAction(
    "2. l to second list",
    ["KNOWN ISSUE: Gecko is not exposing this as a roman numeral.",
     "BRAILLE LINE:  '6. And use roman numerals,'",
     "     VISIBLE:  '6. And use roman numerals,', cursor=1",
     "SPEECH OUTPUT: 'List with 6 items' voice=system",
     "SPEECH OUTPUT: '6. And use roman numerals,'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("l"))
sequence.append(utils.AssertPresentationAction(
    "3. l to third list",
    ["BRAILLE LINE:  '• listing item'",
     "     VISIBLE:  '• listing item', cursor=1",
     "SPEECH OUTPUT: 'List with 2 items' voice=system",
     "SPEECH OUTPUT: '• listing item.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("l"))
sequence.append(utils.AssertPresentationAction(
    "4. l to third list's first sub list",
    ["BRAILLE LINE:  '◦ first sublevel'",
     "     VISIBLE:  '◦ first sublevel', cursor=1",
     "SPEECH OUTPUT: 'List with 2 items' voice=system",
     "SPEECH OUTPUT: '◦ first sublevel.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("l"))
sequence.append(utils.AssertPresentationAction(
    "5. l to third list's first sub list's first list",
    ["BRAILLE LINE:  '◾ look for the bullet on'",
     "     VISIBLE:  '◾ look for the bullet on', cursor=1",
     "SPEECH OUTPUT: 'List with 2 items' voice=system",
     "SPEECH OUTPUT: '◾ look for the bullet on.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("l"))
sequence.append(utils.AssertPresentationAction(
    "6. l to third list's inner-most list",
    ["BRAILLE LINE:  '◾ each sublevel'",
     "     VISIBLE:  '◾ each sublevel', cursor=1",
     "SPEECH OUTPUT: 'List with 2 items' voice=system",
     "SPEECH OUTPUT: '◾ each sublevel.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("l"))
sequence.append(utils.AssertPresentationAction(
    "7. l to next sub list in the third list",
    ["BRAILLE LINE:  '◦ if your TYPE is circle'",
     "     VISIBLE:  '◦ if your TYPE is circle', cursor=1",
     "SPEECH OUTPUT: 'List with 2 items' voice=system",
     "SPEECH OUTPUT: '◦ if your TYPE is circle.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("l"))
sequence.append(utils.AssertPresentationAction(
    "8. l to next sub list in the third list",
    ["BRAILLE LINE:  '◦ was a composer who was not square'",
     "     VISIBLE:  '◦ was a composer who was not squ', cursor=1",
     "SPEECH OUTPUT: 'List with 2 items' voice=system",
     "SPEECH OUTPUT: '◦ was a composer who was not square.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("l"))
sequence.append(utils.AssertPresentationAction(
    "9. l to the fourth list",
    ["BRAILLE LINE:  '◦ feeling listless'",
     "     VISIBLE:  '◦ feeling listless', cursor=1",
     "SPEECH OUTPUT: 'List with 3 items' voice=system",
     "SPEECH OUTPUT: '◦ feeling listless.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("l"))
sequence.append(utils.AssertPresentationAction(
    "10. l - should wrap to top",
    ["BRAILLE LINE:  'Wrapping to top.'",
     "     VISIBLE:  'Wrapping to top.', cursor=0",
     "BRAILLE LINE:  '1. remember what the heck we are doing each day'",
     "     VISIBLE:  '1. remember what the heck we are', cursor=1",
     "SPEECH OUTPUT: 'Wrapping to top.' voice=system",
     "SPEECH OUTPUT: 'List with 4 items' voice=system",
     "SPEECH OUTPUT: '1. remember what the heck we are doing each day.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>l"))
sequence.append(utils.AssertPresentationAction(
    "11. shift + l - should wrap to bottom",
    ["BRAILLE LINE:  'Wrapping to bottom.'",
     "     VISIBLE:  'Wrapping to bottom.', cursor=0",
     "BRAILLE LINE:  '◦ feeling listless'",
     "     VISIBLE:  '◦ feeling listless', cursor=1",
     "SPEECH OUTPUT: 'Wrapping to bottom.' voice=system",
     "SPEECH OUTPUT: 'List with 3 items' voice=system",
     "SPEECH OUTPUT: '◦ feeling listless.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>l"))
sequence.append(utils.AssertPresentationAction(
    "12. shift + l",
    ["BRAILLE LINE:  '◦ was a composer who was not square'",
     "     VISIBLE:  '◦ was a composer who was not squ', cursor=1",
     "SPEECH OUTPUT: 'List with 2 items' voice=system",
     "SPEECH OUTPUT: '◦ was a composer who was not square.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>l"))
sequence.append(utils.AssertPresentationAction(
    "13. shift + l",
    ["BRAILLE LINE:  '◦ if your TYPE is circle'",
     "     VISIBLE:  '◦ if your TYPE is circle', cursor=1",
     "SPEECH OUTPUT: 'List with 2 items' voice=system",
     "SPEECH OUTPUT: '◦ if your TYPE is circle.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>l"))
sequence.append(utils.AssertPresentationAction(
    "14. shift + l",
    ["BRAILLE LINE:  '◾ each sublevel'",
     "     VISIBLE:  '◾ each sublevel', cursor=1",
     "SPEECH OUTPUT: 'List with 2 items' voice=system",
     "SPEECH OUTPUT: '◾ each sublevel.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>l"))
sequence.append(utils.AssertPresentationAction(
    "15. shift + l",
    ["BRAILLE LINE:  '◾ look for the bullet on'",
     "     VISIBLE:  '◾ look for the bullet on', cursor=1",
     "SPEECH OUTPUT: 'List with 2 items' voice=system",
     "SPEECH OUTPUT: '◾ look for the bullet on.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>l"))
sequence.append(utils.AssertPresentationAction(
    "16. shift + l",
    ["BRAILLE LINE:  '◦ first sublevel'",
     "     VISIBLE:  '◦ first sublevel', cursor=1",
     "SPEECH OUTPUT: 'List with 2 items' voice=system",
     "SPEECH OUTPUT: '◦ first sublevel.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>l"))
sequence.append(utils.AssertPresentationAction(
    "17. shift + l",
    ["BRAILLE LINE:  '• listing item'",
     "     VISIBLE:  '• listing item', cursor=1",
     "SPEECH OUTPUT: 'List with 2 items' voice=system",
     "SPEECH OUTPUT: '• listing item.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>l"))
sequence.append(utils.AssertPresentationAction(
    "18. shift + l",
    ["KNOWN ISSUE: Gecko is not exposing this as a roman numeral.",
     "BRAILLE LINE:  '6. And use roman numerals,'",
     "     VISIBLE:  '6. And use roman numerals,', cursor=1",
     "SPEECH OUTPUT: 'List with 6 items' voice=system",
     "SPEECH OUTPUT: '6. And use roman numerals,'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>l"))
sequence.append(utils.AssertPresentationAction(
    "19. shift + l",
    ["BRAILLE LINE:  '1. remember what the heck we are doing each day'",
     "     VISIBLE:  '1. remember what the heck we are', cursor=1",
     "SPEECH OUTPUT: 'List with 4 items' voice=system",
     "SPEECH OUTPUT: '1. remember what the heck we are doing each day.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
