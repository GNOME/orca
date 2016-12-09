#!/usr/bin/python

"""Test of line navigation output of Firefox."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

# Work around some new quirk in Gecko that causes this test to fail if
# run via the test harness rather than manually.
sequence.append(KeyComboAction("<Control>r"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'separator'",
     "     VISIBLE:  'separator', cursor=1",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'HTML Form and Widgets'",
     "     VISIBLE:  'HTML Form and Widgets', cursor=1",
     "SPEECH OUTPUT: 'HTML Form and Widgets'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'Textfield :'",
     "     VISIBLE:  'Textfield :', cursor=1",
     "SPEECH OUTPUT: 'Textfield :'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  'Enter your Name:  $l text field using default type=text'",
     "     VISIBLE:  'Enter your Name:  $l text field ', cursor=1",
     "SPEECH OUTPUT: 'Enter your Name:'",
     "SPEECH OUTPUT: 'entry.'",
     "SPEECH OUTPUT: 'text field using default type=text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  '1. Enter your Address:  $l text field using SIZE and MAXLENGTH'",
     "     VISIBLE:  '1. Enter your Address:  $l text ', cursor=1",
     "SPEECH OUTPUT: '1. Enter your Address:'",
     "SPEECH OUTPUT: 'entry.'",
     "SPEECH OUTPUT: 'text field using SIZE and MAXLENGTH'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Down",
    ["BRAILLE LINE:  '2. Enter your City:  $l 3. Enter your State:  $l 4. Enter your Country: US $l text field using'",
     "     VISIBLE:  '2. Enter your City:  $l 3. Enter', cursor=1",
     "SPEECH OUTPUT: '2. Enter your City:'",
     "SPEECH OUTPUT: 'entry.'",
     "SPEECH OUTPUT: '3. Enter your State:'",
     "SPEECH OUTPUT: 'entry.'",
     "SPEECH OUTPUT: '4. Enter your Country:'",
     "SPEECH OUTPUT: 'entry'",
     "SPEECH OUTPUT: 'US.'",
     "SPEECH OUTPUT: 'text field using'"]))

sequence.append(KeyComboAction("Down"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Down",
    ["BRAILLE LINE:  '5. Enter your Zip:  $l'",
     "     VISIBLE:  '5. Enter your Zip:  $l', cursor=1",
     "SPEECH OUTPUT: '5. Enter your Zip:'",
     "SPEECH OUTPUT: 'entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Down",
    ["BRAILLE LINE:  '6. What happens when a fixed-width font(the default) is used for a one-byte text input area, let's try it.. Enter one'",
     "     VISIBLE:  '6. What happens when a fixed-wid', cursor=1",
     "SPEECH OUTPUT: '6. What happens when a fixed-width font(the default) is used for a one-byte text input area, let's try it.. Enter one'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Down",
    ["BRAILLE LINE:  'character:  $l '",
     "     VISIBLE:  'character:  $l ', cursor=1",
     "SPEECH OUTPUT: 'character:'",
     "SPEECH OUTPUT: 'entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Line Down",
    ["BRAILLE LINE:  'separator'",
     "     VISIBLE:  'separator', cursor=1",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Line Down",
    ["BRAILLE LINE:  ' CheckBox:'",
     "     VISIBLE:  ' CheckBox:', cursor=1",
     "SPEECH OUTPUT: 'CheckBox:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. Line Down",
    ["BRAILLE LINE:  'What are your favorite pets? h2'",
     "     VISIBLE:  'What are your favorite pets? h2', cursor=1",
     "SPEECH OUTPUT: 'What are your favorite pets? heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "13. Line Down",
    ["BRAILLE LINE:  '< > bird check box'",
     "     VISIBLE:  '< > bird check box', cursor=1",
     "SPEECH OUTPUT: 'bird check box not checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "14. Line Down",
    ["BRAILLE LINE:  '< > fish check box'",
     "     VISIBLE:  '< > fish check box', cursor=1",
     "SPEECH OUTPUT: 'fish check box not checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "15. Line Down",
    ["BRAILLE LINE:  '< > wild animal check box'",
     "     VISIBLE:  '< > wild animal check box', cursor=1",
     "SPEECH OUTPUT: 'wild animal check box not checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "16. Line Down",
    ["BRAILLE LINE:  'separator'",
     "     VISIBLE:  'separator', cursor=1",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "17. Line Down",
    ["BRAILLE LINE:  'Radio Buttons:'",
     "     VISIBLE:  'Radio Buttons:', cursor=1",
     "SPEECH OUTPUT: 'Radio Buttons:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "18. Line Down",
    ["BRAILLE LINE:  'Would type of wine do you like? h2'",
     "     VISIBLE:  'Would type of wine do you like? ', cursor=1",
     "SPEECH OUTPUT: 'Would type of wine do you like? heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "19. Line Down",
    ["BRAILLE LINE:  '&=y cabernet sauvignon radio button'",
     "     VISIBLE:  '&=y cabernet sauvignon radio but', cursor=1",
     "SPEECH OUTPUT: 'cabernet sauvignon.'",
     "SPEECH OUTPUT: 'selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "20. Line Down",
    ["BRAILLE LINE:  '& y merlot radio button'",
     "     VISIBLE:  '& y merlot radio button', cursor=1",
     "SPEECH OUTPUT: 'merlot.'",
     "SPEECH OUTPUT: 'not selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "21. Line Down",
    ["BRAILLE LINE:  '& y nebbiolo radio button'",
     "     VISIBLE:  '& y nebbiolo radio button', cursor=1",
     "SPEECH OUTPUT: 'nebbiolo.'",
     "SPEECH OUTPUT: 'not selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "22. Line Down",
    ["BRAILLE LINE:  '& y pinot noir radio button'",
     "     VISIBLE:  '& y pinot noir radio button', cursor=1",
     "SPEECH OUTPUT: 'pinot noir.'",
     "SPEECH OUTPUT: 'not selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "23. Line Down",
    ["BRAILLE LINE:  '& y don't drink wine radio button'",
     "     VISIBLE:  '& y don't drink wine radio butto', cursor=1",
     "SPEECH OUTPUT: 'don't drink wine.'",
     "SPEECH OUTPUT: 'not selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "24. Line Up",
    ["BRAILLE LINE:  '& y pinot noir radio button'",
     "     VISIBLE:  '& y pinot noir radio button', cursor=1",
     "SPEECH OUTPUT: 'pinot noir.'",
     "SPEECH OUTPUT: 'not selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "25. Line Up",
    ["BRAILLE LINE:  '& y nebbiolo radio button'",
     "     VISIBLE:  '& y nebbiolo radio button', cursor=1",
     "SPEECH OUTPUT: 'nebbiolo.'",
     "SPEECH OUTPUT: 'not selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "26. Line Up",
    ["BRAILLE LINE:  '& y merlot radio button'",
     "     VISIBLE:  '& y merlot radio button', cursor=1",
     "SPEECH OUTPUT: 'merlot.'",
     "SPEECH OUTPUT: 'not selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "27. Line Up",
    ["BRAILLE LINE:  '&=y cabernet sauvignon radio button'",
     "     VISIBLE:  '&=y cabernet sauvignon radio but', cursor=1",
     "SPEECH OUTPUT: 'cabernet sauvignon.'",
     "SPEECH OUTPUT: 'selected radio button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "28. Line Up",
    ["BRAILLE LINE:  'Would type of wine do you like? h2'",
     "     VISIBLE:  'Would type of wine do you like? ', cursor=1",
     "SPEECH OUTPUT: 'Would type of wine do you like? heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "29. Line Up",
    ["BRAILLE LINE:  'Radio Buttons:'",
     "     VISIBLE:  'Radio Buttons:', cursor=1",
     "SPEECH OUTPUT: 'Radio Buttons:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "30. Line Up",
    ["BRAILLE LINE:  'separator'",
     "     VISIBLE:  'separator', cursor=1",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "31. Line Up",
    ["BRAILLE LINE:  '< > wild animal check box'",
     "     VISIBLE:  '< > wild animal check box', cursor=1",
     "SPEECH OUTPUT: 'wild animal check box not checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "32. Line Up",
    ["BRAILLE LINE:  '< > fish check box'",
     "     VISIBLE:  '< > fish check box', cursor=1",
     "SPEECH OUTPUT: 'fish check box not checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "33. Line Up",
    ["BRAILLE LINE:  '< > bird check box'",
     "     VISIBLE:  '< > bird check box', cursor=1",
     "SPEECH OUTPUT: 'bird check box not checked.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "34. Line Up",
    ["BRAILLE LINE:  'What are your favorite pets? h2'",
     "     VISIBLE:  'What are your favorite pets? h2', cursor=1",
     "SPEECH OUTPUT: 'What are your favorite pets? heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "35. Line Up",
    ["BRAILLE LINE:  ' CheckBox:'",
     "     VISIBLE:  ' CheckBox:', cursor=1",
     "SPEECH OUTPUT: 'CheckBox:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "36. Line Up",
    ["BRAILLE LINE:  'separator'",
     "     VISIBLE:  'separator', cursor=1",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "37. Line Up",
    ["BRAILLE LINE:  'character:  $l '",
     "     VISIBLE:  'character:  $l ', cursor=1",
     "SPEECH OUTPUT: 'character:'",
     "SPEECH OUTPUT: 'entry.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "38. Line Up",
    ["BRAILLE LINE:  '6. What happens when a fixed-width font(the default) is used for a one-byte text input area, let's try it.. Enter one'",
     "     VISIBLE:  '6. What happens when a fixed-wid', cursor=1",
     "SPEECH OUTPUT: '6. What happens when a fixed-width font(the default) is used for a one-byte text input area, let's try it.. Enter one'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "39. Line Up",
    ["BRAILLE LINE:  '5. Enter your Zip:  $l'",
     "     VISIBLE:  '5. Enter your Zip:  $l', cursor=1",
     "SPEECH OUTPUT: '5. Enter your Zip:'",
     "SPEECH OUTPUT: 'entry.'"]))

sequence.append(KeyComboAction("Up"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "40. Line Up",
    ["BRAILLE LINE:  '2. Enter your City:  $l 3. Enter your State:  $l 4. Enter your Country: US $l text field using'",
     "     VISIBLE:  '2. Enter your City:  $l 3. Enter', cursor=1",
     "SPEECH OUTPUT: '2. Enter your City:'",
     "SPEECH OUTPUT: 'entry.'",
     "SPEECH OUTPUT: '3. Enter your State:'",
     "SPEECH OUTPUT: 'entry.'",
     "SPEECH OUTPUT: '4. Enter your Country:'",
     "SPEECH OUTPUT: 'entry'",
     "SPEECH OUTPUT: 'US.'",
     "SPEECH OUTPUT: 'text field using'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "41. Line Up",
    ["BRAILLE LINE:  '1. Enter your Address:  $l text field using SIZE and MAXLENGTH'",
     "     VISIBLE:  '1. Enter your Address:  $l text ', cursor=1",
     "SPEECH OUTPUT: '1. Enter your Address:'",
     "SPEECH OUTPUT: 'entry.'",
     "SPEECH OUTPUT: 'text field using SIZE and MAXLENGTH'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "42. Line Up",
    ["BRAILLE LINE:  'Enter your Name:  $l text field using default type=text'",
     "     VISIBLE:  'Enter your Name:  $l text field ', cursor=1",
     "SPEECH OUTPUT: 'Enter your Name:'",
     "SPEECH OUTPUT: 'entry.'",
     "SPEECH OUTPUT: 'text field using default type=text'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "43. Line Up",
    ["BRAILLE LINE:  'Textfield :'",
     "     VISIBLE:  'Textfield :', cursor=1",
     "SPEECH OUTPUT: 'Textfield :'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "44. Line Up",
    ["BRAILLE LINE:  'HTML Form and Widgets'",
     "     VISIBLE:  'HTML Form and Widgets', cursor=1",
     "SPEECH OUTPUT: 'HTML Form and Widgets'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "45. Line Up",
    ["BRAILLE LINE:  'separator'",
     "     VISIBLE:  'separator', cursor=1",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
