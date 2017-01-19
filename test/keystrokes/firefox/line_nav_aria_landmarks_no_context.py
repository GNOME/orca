#!/usr/bin/python

"""Test of line navigation output of Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(2000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'Start of test'",
     "     VISIBLE:  'Start of test', cursor=1",
     "SPEECH OUTPUT: 'Start of test'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'Line one'",
     "     VISIBLE:  'Line one', cursor=1",
     "SPEECH OUTPUT: 'Line one'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'Line two'",
     "     VISIBLE:  'Line two', cursor=1",
     "SPEECH OUTPUT: 'Line two'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  'Click me push button'",
     "     VISIBLE:  'Click me push button', cursor=1",
     "SPEECH OUTPUT: 'Click me push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  'Line one'",
     "     VISIBLE:  'Line one', cursor=1",
     "SPEECH OUTPUT: 'Line one'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Down",
    ["BRAILLE LINE:  'Line two'",
     "     VISIBLE:  'Line two', cursor=1",
     "SPEECH OUTPUT: 'Line two'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Down",
    ["BRAILLE LINE:  'Click me push button'",
     "     VISIBLE:  'Click me push button', cursor=1",
     "SPEECH OUTPUT: 'Click me push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Down",
    ["BRAILLE LINE:  'Line one'",
     "     VISIBLE:  'Line one', cursor=1",
     "SPEECH OUTPUT: 'Line one'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Down",
    ["BRAILLE LINE:  'Line two'",
     "     VISIBLE:  'Line two', cursor=1",
     "SPEECH OUTPUT: 'Line two'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Line Down",
    ["BRAILLE LINE:  'Click me push button'",
     "     VISIBLE:  'Click me push button', cursor=1",
     "SPEECH OUTPUT: 'Click me push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Line Down",
    ["BRAILLE LINE:  'Line one'",
     "     VISIBLE:  'Line one', cursor=1",
     "SPEECH OUTPUT: 'Line one'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. Line Down",
    ["BRAILLE LINE:  'Line two'",
     "     VISIBLE:  'Line two', cursor=1",
     "SPEECH OUTPUT: 'Line two'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "13. Line Down",
    ["BRAILLE LINE:  'Click me push button'",
     "     VISIBLE:  'Click me push button', cursor=1",
     "SPEECH OUTPUT: 'Click me push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "14. Line Down",
    ["BRAILLE LINE:  'Line four'",
     "     VISIBLE:  'Line four', cursor=1",
     "SPEECH OUTPUT: 'Line four'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "15. Line Down",
    ["BRAILLE LINE:  'Line five'",
     "     VISIBLE:  'Line five', cursor=1",
     "SPEECH OUTPUT: 'Line five'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "16. Line Down",
    ["BRAILLE LINE:  'Line one'",
     "     VISIBLE:  'Line one', cursor=1",
     "SPEECH OUTPUT: 'Line one'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "17. Line Down",
    ["BRAILLE LINE:  'Line two'",
     "     VISIBLE:  'Line two', cursor=1",
     "SPEECH OUTPUT: 'Line two'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "18. Line Down",
    ["BRAILLE LINE:  'Click me push button'",
     "     VISIBLE:  'Click me push button', cursor=1",
     "SPEECH OUTPUT: 'Click me push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "19. Line Down",
    ["BRAILLE LINE:  'Line one'",
     "     VISIBLE:  'Line one', cursor=1",
     "SPEECH OUTPUT: 'Line one'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "20. Line Down",
    ["BRAILLE LINE:  'Line two'",
     "     VISIBLE:  'Line two', cursor=1",
     "SPEECH OUTPUT: 'Line two'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "21. Line Down",
    ["BRAILLE LINE:  'Click me push button'",
     "     VISIBLE:  'Click me push button', cursor=1",
     "SPEECH OUTPUT: 'Click me push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "22. Line Down",
    ["BRAILLE LINE:  'Line four'",
     "     VISIBLE:  'Line four', cursor=1",
     "SPEECH OUTPUT: 'Line four'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "23. Line Down",
    ["BRAILLE LINE:  'Line one'",
     "     VISIBLE:  'Line one', cursor=1",
     "SPEECH OUTPUT: 'Line one'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "24. Line Down",
    ["BRAILLE LINE:  'Line two'",
     "     VISIBLE:  'Line two', cursor=1",
     "SPEECH OUTPUT: 'Line two'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "25. Line Down",
    ["BRAILLE LINE:  'Click me push button'",
     "     VISIBLE:  'Click me push button', cursor=1",
     "SPEECH OUTPUT: 'Click me push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "26. Line Down",
    ["BRAILLE LINE:  'Line five'",
     "     VISIBLE:  'Line five', cursor=1",
     "SPEECH OUTPUT: 'Line five'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "27. Line Down",
    ["BRAILLE LINE:  'Line one'",
     "     VISIBLE:  'Line one', cursor=1",
     "SPEECH OUTPUT: 'Line one'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "28. Line Down",
    ["BRAILLE LINE:  'Line two'",
     "     VISIBLE:  'Line two', cursor=1",
     "SPEECH OUTPUT: 'Line two'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "29. Line Down",
    ["BRAILLE LINE:  'Click me push button'",
     "     VISIBLE:  'Click me push button', cursor=1",
     "SPEECH OUTPUT: 'Click me push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "30. Line Down",
    ["BRAILLE LINE:  'Line one'",
     "     VISIBLE:  'Line one', cursor=1",
     "SPEECH OUTPUT: 'Line one'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "31. Line Down",
    ["BRAILLE LINE:  'Line two'",
     "     VISIBLE:  'Line two', cursor=1",
     "SPEECH OUTPUT: 'Line two'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "32. Line Down",
    ["BRAILLE LINE:  'Click me push button'",
     "     VISIBLE:  'Click me push button', cursor=1",
     "SPEECH OUTPUT: 'Click me push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "33. Line Down",
    ["BRAILLE LINE:  'End of test'",
     "     VISIBLE:  'End of test', cursor=1",
     "SPEECH OUTPUT: 'End of test'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "34. Line Up",
    ["BRAILLE LINE:  'Click me push button'",
     "     VISIBLE:  'Click me push button', cursor=1",
     "SPEECH OUTPUT: 'Click me push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "35. Line Up",
    ["BRAILLE LINE:  'Line two'",
     "     VISIBLE:  'Line two', cursor=1",
     "SPEECH OUTPUT: 'Line two'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "36. Line Up",
    ["BRAILLE LINE:  'Line one'",
     "     VISIBLE:  'Line one', cursor=1",
     "SPEECH OUTPUT: 'Line one'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "37. Line Up",
    ["BRAILLE LINE:  'Click me push button'",
     "     VISIBLE:  'Click me push button', cursor=1",
     "SPEECH OUTPUT: 'Click me push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "38. Line Up",
    ["BRAILLE LINE:  'Line two'",
     "     VISIBLE:  'Line two', cursor=1",
     "SPEECH OUTPUT: 'Line two'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "39. Line Up",
    ["BRAILLE LINE:  'Line one'",
     "     VISIBLE:  'Line one', cursor=1",
     "SPEECH OUTPUT: 'Line one'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "40. Line Up",
    ["BRAILLE LINE:  'Line five'",
     "     VISIBLE:  'Line five', cursor=1",
     "SPEECH OUTPUT: 'Line five'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "41. Line Up",
    ["BRAILLE LINE:  'Click me push button'",
     "     VISIBLE:  'Click me push button', cursor=1",
     "SPEECH OUTPUT: 'Click me push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "42. Line Up",
    ["BRAILLE LINE:  'Line two'",
     "     VISIBLE:  'Line two', cursor=1",
     "SPEECH OUTPUT: 'Line two'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "43. Line Up",
    ["BRAILLE LINE:  'Line one'",
     "     VISIBLE:  'Line one', cursor=1",
     "SPEECH OUTPUT: 'Line one'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "44. Line Up",
    ["BRAILLE LINE:  'Line four'",
     "     VISIBLE:  'Line four', cursor=1",
     "SPEECH OUTPUT: 'Line four'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "45. Line Up",
    ["BRAILLE LINE:  'Click me push button'",
     "     VISIBLE:  'Click me push button', cursor=1",
     "SPEECH OUTPUT: 'Click me push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "46. Line Up",
    ["BRAILLE LINE:  'Line two'",
     "     VISIBLE:  'Line two', cursor=1",
     "SPEECH OUTPUT: 'Line two'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "47. Line Up",
    ["BRAILLE LINE:  'Line one'",
     "     VISIBLE:  'Line one', cursor=1",
     "SPEECH OUTPUT: 'Line one'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "48. Line Up",
    ["BRAILLE LINE:  'Click me push button'",
     "     VISIBLE:  'Click me push button', cursor=1",
     "SPEECH OUTPUT: 'Click me push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "49. Line Up",
    ["BRAILLE LINE:  'Line two'",
     "     VISIBLE:  'Line two', cursor=1",
     "SPEECH OUTPUT: 'Line two'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "50. Line Up",
    ["BRAILLE LINE:  'Line one'",
     "     VISIBLE:  'Line one', cursor=1",
     "SPEECH OUTPUT: 'Line one'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "51. Line Up",
    ["BRAILLE LINE:  'Line five'",
     "     VISIBLE:  'Line five', cursor=1",
     "SPEECH OUTPUT: 'Line five'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "52. Line Up",
    ["BRAILLE LINE:  'Line four'",
     "     VISIBLE:  'Line four', cursor=1",
     "SPEECH OUTPUT: 'Line four'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "53. Line Up",
    ["BRAILLE LINE:  'Click me push button'",
     "     VISIBLE:  'Click me push button', cursor=1",
     "SPEECH OUTPUT: 'Click me push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "54. Line Up",
    ["BRAILLE LINE:  'Line two'",
     "     VISIBLE:  'Line two', cursor=1",
     "SPEECH OUTPUT: 'Line two'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "55. Line Up",
    ["BRAILLE LINE:  'Line one'",
     "     VISIBLE:  'Line one', cursor=1",
     "SPEECH OUTPUT: 'Line one'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "56. Line Up",
    ["BRAILLE LINE:  'Click me push button'",
     "     VISIBLE:  'Click me push button', cursor=1",
     "SPEECH OUTPUT: 'Click me push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "57. Line Up",
    ["BRAILLE LINE:  'Line two'",
     "     VISIBLE:  'Line two', cursor=1",
     "SPEECH OUTPUT: 'Line two'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "58. Line Up",
    ["BRAILLE LINE:  'Line one'",
     "     VISIBLE:  'Line one', cursor=1",
     "SPEECH OUTPUT: 'Line one'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "59. Line Up",
    ["BRAILLE LINE:  'Click me push button'",
     "     VISIBLE:  'Click me push button', cursor=1",
     "SPEECH OUTPUT: 'Click me push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "60. Line Up",
    ["BRAILLE LINE:  'Line two'",
     "     VISIBLE:  'Line two', cursor=1",
     "SPEECH OUTPUT: 'Line two'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "61. Line Up",
    ["BRAILLE LINE:  'Line one'",
     "     VISIBLE:  'Line one', cursor=1",
     "SPEECH OUTPUT: 'Line one'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "62. Line Up",
    ["BRAILLE LINE:  'Click me push button'",
     "     VISIBLE:  'Click me push button', cursor=1",
     "SPEECH OUTPUT: 'Click me push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "63. Line Up",
    ["BRAILLE LINE:  'Line two'",
     "     VISIBLE:  'Line two', cursor=1",
     "SPEECH OUTPUT: 'Line two'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "64. Line Up",
    ["BRAILLE LINE:  'Line one'",
     "     VISIBLE:  'Line one', cursor=1",
     "SPEECH OUTPUT: 'Line one'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "65. Line Up",
    ["BRAILLE LINE:  'Start of test'",
     "     VISIBLE:  'Start of test', cursor=1",
     "SPEECH OUTPUT: 'Start of test'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
