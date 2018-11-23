#!/usr/bin/python

"""Test of structural navigation amongst list items."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("<Control>Home"))

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
    "3. l to third list (3) landing on the first item (3.1)",
    ["BRAILLE LINE:  '• listing item'",
     "     VISIBLE:  '• listing item', cursor=1",
     "SPEECH OUTPUT: 'List with 2 items' voice=system",
     "SPEECH OUTPUT: '• listing item.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "4. i to next list item, which is nested (3.1.1)",
    ["BRAILLE LINE:  '◦ first sublevel'",
     "     VISIBLE:  '◦ first sublevel', cursor=1",
     "SPEECH OUTPUT: '◦ first sublevel.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "5. i to next list item, which is nested (3.1.1.1)",
    ["BRAILLE LINE:  '◾ look for the bullet on'",
     "     VISIBLE:  '◾ look for the bullet on', cursor=1",
     "SPEECH OUTPUT: '◾ look for the bullet on.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "6. i to next list item, which is nested (3.1.1.1.1)",
    ["BRAILLE LINE:  '◾ each sublevel'",
     "     VISIBLE:  '◾ each sublevel', cursor=1",
     "SPEECH OUTPUT: '◾ each sublevel.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "7. i to next list item, which is a peer (3.1.1.1.2)",
    ["BRAILLE LINE:  '◾ they should all be different, except here.'",
     "     VISIBLE:  '◾ they should all be different, ', cursor=1",
     "SPEECH OUTPUT: '◾ they should all be different, except here.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "8. i to next list item, moving outside of the innermost list (3.1.1.2)",
    ["BRAILLE LINE:  '◾ second sublevel'",
     "     VISIBLE:  '◾ second sublevel', cursor=1",
     "SPEECH OUTPUT: '◾ second sublevel.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "9. i to next list item, moving outside of the current nested list (3.1.2)",
    ["BRAILLE LINE:  '◾ or you can specify a square'",
     "     VISIBLE:  '◾ or you can specify a square', cursor=1",
     "SPEECH OUTPUT: '◾ or you can specify a square.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "10. i to next list item, which is nested (3.1.2.1)",
    ["BRAILLE LINE:  '◦ if your TYPE is circle'",
     "     VISIBLE:  '◦ if your TYPE is circle', cursor=25",
     "SPEECH OUTPUT: '◦ if your TYPE is circle.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "11. i to next list item, which is further nested (3.1.2.2)",
    ["BRAILLE LINE:  '• or even a disc'",
     "     VISIBLE:  '• or even a disc', cursor=1",
     "SPEECH OUTPUT: '• or even a disc.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "12. i to next list item, moving out of the last two levels (3.2)",
    ["BRAILLE LINE:  '◾ Franz Liszt'",
     "     VISIBLE:  '◾ Franz Liszt', cursor=1",
     "SPEECH OUTPUT: '◾ Franz Liszt.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "13. i to next list item which is nested (3.2.1)",
    ["BRAILLE LINE:  '◦ was a composer who was not square'",
     "     VISIBLE:  'square', cursor=7",
     "SPEECH OUTPUT: '◦ was a composer who was not square.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "14. i to next list item which is nested (3.2.2)",
    ["BRAILLE LINE:  '• would have liked the Who'",
     "     VISIBLE:  '• would have liked the Who', cursor=1",
     "SPEECH OUTPUT: '• would have liked the Who.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "15. i to next list item which is starts a new list (4.1)",
    ["BRAILLE LINE:  '◦ feeling listless'",
     "     VISIBLE:  '◦ feeling listless', cursor=1",
     "SPEECH OUTPUT: '◦ feeling listless"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "16. i to next list item in the fourth list (4.2)",
    ["BRAILLE LINE:  '◾ blah, blah, blah'",
     "     VISIBLE:  '◾ blah, blah, blah', cursor=1",
     "SPEECH OUTPUT: '◾ blah, blah, blah.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "17. i to last list item in the fourth list (4.3)",
    ["BRAILLE LINE:  '• whine, whine, whine'",
     "     VISIBLE:  '• whine, whine, whine', cursor=1",
     "SPEECH OUTPUT: '• whine, whine, whine.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("i"))
sequence.append(utils.AssertPresentationAction(
    "18. i should wrap to top",
    ["BRAILLE LINE:  'Wrapping to top.'",
     "     VISIBLE:  'Wrapping to top.', cursor=0",
     "BRAILLE LINE:  '1. remember what the heck we are doing each day'",
     "     VISIBLE:  '1. remember what the heck we are', cursor=1",
     "SPEECH OUTPUT: 'Wrapping to top.' voice=system",
     "SPEECH OUTPUT: '1. remember what the heck we are doing each day.'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
