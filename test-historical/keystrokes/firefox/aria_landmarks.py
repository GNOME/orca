#!/usr/bin/python

"""Test of structural navigation amongst landmarks."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("<Control>Home"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("m"))
sequence.append(utils.AssertPresentationAction(
    "1. m to next landmark",
    ["BRAILLE LINE:  'navigation'",
     "     VISIBLE:  'navigation', cursor=1",
     "SPEECH OUTPUT: 'navigation'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("m"))
sequence.append(utils.AssertPresentationAction(
    "2. m to next landmark",
    ["BRAILLE LINE:  'main application embedded'",
     "     VISIBLE:  'main application embedded', cursor=1",
     "SPEECH OUTPUT: 'main'",
     "SPEECH OUTPUT: 'embedded'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("m"))
sequence.append(utils.AssertPresentationAction(
    "3. m to next landmark",
    ["BRAILLE LINE:  'complementary'",
     "     VISIBLE:  'complementary', cursor=1",
     "SPEECH OUTPUT: 'complementary'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("m"))
sequence.append(utils.AssertPresentationAction(
    "4. m to next landmark",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'form '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("m"))
sequence.append(utils.AssertPresentationAction(
    "5. m to next landmark",
    ["BRAILLE LINE:  'search'",
     "     VISIBLE:  'search', cursor=1",
     "SPEECH OUTPUT: 'search'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("m"))
sequence.append(utils.AssertPresentationAction(
    "6. m to next landmark",
    ["BRAILLE LINE:  'contentinfo'",
     "     VISIBLE:  'contentinfo', cursor=1",
     "SPEECH OUTPUT: 'contentinfo'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("m"))
sequence.append(utils.AssertPresentationAction(
    "7. m to next landmark",
    ["BRAILLE LINE:  'Wrapping to top.'",
     "     VISIBLE:  'Wrapping to top.', cursor=0",
     "BRAILLE LINE:  'banner'",
     "     VISIBLE:  'banner', cursor=1",
     "SPEECH OUTPUT: 'Wrapping to top.' voice=system",
     "SPEECH OUTPUT: 'banner'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>m"))
sequence.append(utils.AssertPresentationAction(
    "8. Shift+m to previous landmark",
    ["BRAILLE LINE:  'Wrapping to bottom.'",
     "     VISIBLE:  'Wrapping to bottom.', cursor=0",
     "BRAILLE LINE:  'contentinfo'",
     "     VISIBLE:  'contentinfo', cursor=1",
     "SPEECH OUTPUT: 'Wrapping to bottom.' voice=system",
     "SPEECH OUTPUT: 'contentinfo'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>m"))
sequence.append(utils.AssertPresentationAction(
    "9. Shift+m to previous landmark",
    ["BRAILLE LINE:  'search'",
     "     VISIBLE:  'search', cursor=1",
     "SPEECH OUTPUT: 'search'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>m"))
sequence.append(utils.AssertPresentationAction(
    "10. Shift+m to previous landmark",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'form '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>m"))
sequence.append(utils.AssertPresentationAction(
    "11. Shift+m to previous landmark",
    ["BRAILLE LINE:  'complementary'",
     "     VISIBLE:  'complementary', cursor=1",
     "SPEECH OUTPUT: 'complementary'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>m"))
sequence.append(utils.AssertPresentationAction(
    "12. Shift+m to previous landmark",
    ["BRAILLE LINE:  'main application embedded'",
     "     VISIBLE:  'main application embedded', cursor=1",
     "SPEECH OUTPUT: 'main'",
     "SPEECH OUTPUT: 'embedded'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>m"))
sequence.append(utils.AssertPresentationAction(
    "13. Shift+m to previous landmark",
    ["BRAILLE LINE:  'navigation'",
     "     VISIBLE:  'navigation', cursor=1",
     "SPEECH OUTPUT: 'navigation'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>m"))
sequence.append(utils.AssertPresentationAction(
    "14. Shift+m to previous landmark",
    ["BRAILLE LINE:  'banner'",
     "     VISIBLE:  'banner', cursor=1",
     "SPEECH OUTPUT: 'banner'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
