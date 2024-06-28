#!/usr/bin/python

"""Test of learn mode."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(TypeAction("h"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))

sequence.append(PauseAction(2000))
sequence.append(KeyComboAction("F1"))
sequence.append(PauseAction(2000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Down",
    ["BRAILLE LINE:  ' Before You Begin h2'",
     "     VISIBLE:  ' Before You Begin h2', cursor=2",
     "SPEECH OUTPUT: 'Before You Begin'",
     "SPEECH OUTPUT: 'heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down",
    ["BRAILLE LINE:  ' If you are not yet familiar with the navigation commands provided by your desktop environment, you are encouraged to read that documentation first.'",
     "     VISIBLE:  'If you are not yet familiar with', cursor=1",
     "SPEECH OUTPUT: 'If you are not yet familiar with the navigation commands provided '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Down",
    ["BRAILLE LINE:  'If you are not yet familiar with the navigation commands provided by your desktop environment, you are encouraged to read that documentation first.'",
     "     VISIBLE:  'If you are not yet familiar with', cursor=1",
     "SPEECH OUTPUT: 'by your desktop environment, you are encouraged to read that '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Down",
    ["BRAILLE LINE:  'If you are not yet familiar with the navigation commands provided by your desktop environment, you are encouraged to read that documentation first.'",
     "     VISIBLE:  'If you are not yet familiar with', cursor=1",
     "SPEECH OUTPUT: 'documentation first.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Down",
    ["BRAILLE LINE:  ' Getting Started h2'",
     "     VISIBLE:  ' Getting Started h2', cursor=2",
     "SPEECH OUTPUT: 'Getting Started'",
     "SPEECH OUTPUT: 'heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Down",
    ["BRAILLE LINE:  ' Welcome to Orca'",
     "     VISIBLE:  ' Welcome to Orca', cursor=2",
     "SPEECH OUTPUT: 'Welcome to Orca'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Down",
    ["BRAILLE LINE:  ' Welcome to Orca'",
     "     VISIBLE:  ' Welcome to Orca', cursor=2",
     "SPEECH OUTPUT: 'Welcome to Orca'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Down",
    ["BRAILLE LINE:  ' reader'",
     "     VISIBLE:  ' reader', cursor=2",
     "SPEECH OUTPUT: 'reader'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Down",
    ["BRAILLE LINE:  ' The Orca Modifier'",
     "     VISIBLE:  ' The Orca Modifier', cursor=2",
     "SPEECH OUTPUT: 'The Orca Modifier'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Down",
    ["BRAILLE LINE:  ' The Orca Modifier'",
     "     VISIBLE:  ' The Orca Modifier', cursor=2",
     "SPEECH OUTPUT: 'The Orca Modifier'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Down",
    ["BRAILLE LINE:  ' A key that works like Shift,'",
     "     VISIBLE:  ' A key that works like Shift,', cursor=2",
     "SPEECH OUTPUT: 'A key that works like Shift,'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. Down",
    ["BRAILLE LINE:  ' Configuration'",
     "     VISIBLE:  ' Configuration', cursor=2",
     "SPEECH OUTPUT: 'Configuration'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "13. Down",
    ["BRAILLE LINE:  ' Configuration'",
     "     VISIBLE:  ' Configuration', cursor=2",
     "SPEECH OUTPUT: 'Configuration'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "14. Down",
    ["BRAILLE LINE:  ' \"Learn\" Mode'",
     "     VISIBLE:  ' \"Learn\" Mode', cursor=2",
     "SPEECH OUTPUT: '\"Learn\" Mode'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "15. Down",
    ["BRAILLE LINE:  ' \"Learn\" Mode'",
     "     VISIBLE:  ' \"Learn\" Mode', cursor=2",
     "SPEECH OUTPUT: '\"Learn\" Mode'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "16. Down",
    ["BRAILLE LINE:  ' Keyboard Layout'",
     "     VISIBLE:  ' Keyboard Layout', cursor=2",
     "SPEECH OUTPUT: 'Keyboard Layout'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "17. Down",
    ["BRAILLE LINE:  ' Keyboard Layout'",
     "     VISIBLE:  ' Keyboard Layout', cursor=2",
     "SPEECH OUTPUT: 'Keyboard Layout'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "18. Down",
    ["BRAILLE LINE:  ' layout'",
     "     VISIBLE:  ' layout', cursor=2",
     "SPEECH OUTPUT: 'layout'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "19. Down",
    ["BRAILLE LINE:  ' CapsLock in Laptop Layout'",
     "     VISIBLE:  ' CapsLock in Laptop Layout', cursor=2",
     "SPEECH OUTPUT: 'CapsLock in Laptop Layout'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "20. Down",
    ["BRAILLE LINE:  ' CapsLock in Laptop Layout'",
     "     VISIBLE:  ' CapsLock in Laptop Layout', cursor=2",
     "SPEECH OUTPUT: 'CapsLock in Laptop Layout'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "21. Up",
    ["BRAILLE LINE:  ' CapsLock in Laptop Layout'",
     "     VISIBLE:  ' CapsLock in Laptop Layout', cursor=2",
     "SPEECH OUTPUT: 'CapsLock in Laptop Layout'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "22. Up",
    ["BRAILLE LINE:  ' layout'",
     "     VISIBLE:  ' layout', cursor=2",
     "SPEECH OUTPUT: 'layout'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "23. Up",
    ["BRAILLE LINE:  ' Keyboard Layout'",
     "     VISIBLE:  ' Keyboard Layout', cursor=2",
     "SPEECH OUTPUT: 'Keyboard Layout'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "24. Up",
    ["BRAILLE LINE:  ' Keyboard Layout'",
     "     VISIBLE:  ' Keyboard Layout', cursor=2",
     "SPEECH OUTPUT: 'Keyboard Layout'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "25. Up",
    ["BRAILLE LINE:  ' \"Learn\" Mode'",
     "     VISIBLE:  ' \"Learn\" Mode', cursor=2",
     "SPEECH OUTPUT: '\"Learn\" Mode'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "26. Up",
    ["BRAILLE LINE:  ' \"Learn\" Mode'",
     "     VISIBLE:  ' \"Learn\" Mode', cursor=2",
     "SPEECH OUTPUT: '\"Learn\" Mode'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "27. Up",
    ["BRAILLE LINE:  ' Configuration'",
     "     VISIBLE:  ' Configuration', cursor=2",
     "SPEECH OUTPUT: 'Configuration'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "28. Up",
    ["BRAILLE LINE:  ' Configuration'",
     "     VISIBLE:  ' Configuration', cursor=2",
     "SPEECH OUTPUT: 'Configuration'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "29. Up",
    ["BRAILLE LINE:  ' A key that works like Shift,'",
     "     VISIBLE:  ' A key that works like Shift,', cursor=2",
     "SPEECH OUTPUT: 'A key that works like Shift,'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "30. Up",
    ["BRAILLE LINE:  ' The Orca Modifier'",
     "     VISIBLE:  ' The Orca Modifier', cursor=2",
     "SPEECH OUTPUT: 'The Orca Modifier'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "31. Up",
    ["BRAILLE LINE:  ' The Orca Modifier'",
     "     VISIBLE:  ' The Orca Modifier', cursor=2",
     "SPEECH OUTPUT: 'The Orca Modifier'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "32. Up",
    ["BRAILLE LINE:  ' reader'",
     "     VISIBLE:  ' reader', cursor=2",
     "SPEECH OUTPUT: 'reader'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "33. Up",
    ["BRAILLE LINE:  ' Welcome to Orca'",
     "     VISIBLE:  ' Welcome to Orca', cursor=2",
     "SPEECH OUTPUT: 'Welcome to Orca'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "34. Up",
    ["BRAILLE LINE:  ' Welcome to Orca'",
     "     VISIBLE:  ' Welcome to Orca', cursor=2",
     "SPEECH OUTPUT: 'Welcome to Orca'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "35. Up",
    ["BRAILLE LINE:  ' Getting Started h2'",
     "     VISIBLE:  ' Getting Started h2', cursor=2",
     "SPEECH OUTPUT: 'Getting Started'",
     "SPEECH OUTPUT: 'heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "36. Up",
    ["BRAILLE LINE:  'documentation first.'",
     "     VISIBLE:  'documentation first.', cursor=1",
     "SPEECH OUTPUT: 'documentation first.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "37. Up",
    ["BRAILLE LINE:  'by your desktop environment, you are encouraged to read that '",
     "     VISIBLE:  'by your desktop environment, you', cursor=1",
     "SPEECH OUTPUT: 'by your desktop environment, you are encouraged to read that '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "38. Up",
    ["BRAILLE LINE:  ' If you are not yet familiar with the navigation commands provided '",
     "     VISIBLE:  'If you are not yet familiar with', cursor=1",
     "SPEECH OUTPUT: 'If you are not yet familiar with the navigation commands provided '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "39. Up",
    ["BRAILLE LINE:  ' Before You Begin h2'",
     "     VISIBLE:  ' Before You Begin h2', cursor=2",
     "SPEECH OUTPUT: 'Before You Begin'",
     "SPEECH OUTPUT: 'heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "40. Up",
    ["BRAILLE LINE:  ' Orca's logo Orca Screen Reader h1'",
     "     VISIBLE:  'Orca's logo Orca Screen Reader h', cursor=1",
     "SPEECH OUTPUT: 'Orca's logo'",
     "SPEECH OUTPUT: ' Orca Screen Reade'",
     "SPEECH OUTPUT: 'heading level 1'"]))

sequence.append(KeyComboAction("<Alt>F4"))
sequence.append(utils.AssertionSummaryAction())
sequence.start()
