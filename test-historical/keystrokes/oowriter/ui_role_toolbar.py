#!/usr/bin/python

"""Test of Orca's presentation of Writer toolbar buttons."""

from macaroon.playback import *
import utils

sequence = MacroSequence()
sequence.append(PauseAction(3000))
sequence.append(KeyComboAction("F6"))
sequence.append(PauseAction(3000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("F6"))
sequence.append(utils.AssertPresentationAction(
    "1. F6 to Standard toolbar",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Standard tool bar New push button'",
     "     VISIBLE:  'New push button', cursor=1",
     "SPEECH OUTPUT: 'Standard tool bar'",
     "SPEECH OUTPUT: 'New push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "2. Right Arrow to Open button",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Standard tool bar Open push button'",
     "     VISIBLE:  'Open push button', cursor=1",
     "SPEECH OUTPUT: 'Open push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "3. Right Arrow to Save button",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Standard tool bar Save push button'",
     "     VISIBLE:  'Save push button', cursor=1",
     "SPEECH OUTPUT: 'Save push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("F6"))
sequence.append(utils.AssertPresentationAction(
    "4. F6 to next toolbar",
    ["KNOWN ISSUE: We're double-speaking the combobox name",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Formatting tool bar Default Style $l combo box'",
     "     VISIBLE:  'Default Style $l combo box', cursor=1",
     "SPEECH OUTPUT: 'Formatting tool bar'",
     "SPEECH OUTPUT: 'Paragraph Style Paragraph Style editable combo box.'",
     "SPEECH OUTPUT: 'Default Style'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "5. Tab to next item",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Formatting tool bar Update push button'",
     "     VISIBLE:  'Update push button', cursor=1",
     "SPEECH OUTPUT: 'Update push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(utils.AssertPresentationAction(
    "6. Shift+Tab to return to the former widget",
    ["KNOWN ISSUE: We're double-speaking the combobox name",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Formatting tool bar Default Style $l combo box'",
     "     VISIBLE:  'Default Style $l combo box', cursor=1",
     "SPEECH OUTPUT: 'Paragraph Style Paragraph Style editable combo box.'",
     "SPEECH OUTPUT: 'Default Style'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Down in Apply Style (Collapsed)",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Formatting tool bar Text Body list item'",
     "     VISIBLE:  'Text Body list item', cursor=1",
     "SPEECH OUTPUT: 'Text Body.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Down in Apply Style (Collapsed)",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Formatting tool bar Quotations list item'",
     "     VISIBLE:  'Quotations list item', cursor=1",
     "SPEECH OUTPUT: 'Quotations.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Alt Down to expand list",
    ["KNOWN ISSUE: We say nothing here",
     ""]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Down in Apply Style (Expanded)",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Formatting tool bar  combo boxTitle $l Title list item'",
     "     VISIBLE:  'Title list item', cursor=1",
     "SPEECH OUTPUT: 'Title.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Down in Apply Style (Expanded)",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Formatting tool bar  combo boxSubtitle $l Subtitle list item'",
     "     VISIBLE:  'Subtitle list item', cursor=1",
     "SPEECH OUTPUT: 'Subtitle.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "12. Up in Apply Style (Expanded)",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Formatting tool bar  combo boxTitle $l Title list item'",
     "     VISIBLE:  'Title list item', cursor=1",
     "SPEECH OUTPUT: 'Title.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>Up"))
sequence.append(utils.AssertPresentationAction(
    "13. Alt+Up to collapse list",
    ["KNOWN ISSUE: We say nothing",
     ""]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "14. Tab to next widget",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Formatting tool bar Update push button'",
     "     VISIBLE:  'Update push button', cursor=1",
     "SPEECH OUTPUT: 'Update push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "15. Tab to next widget",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Formatting tool bar New push button'",
     "     VISIBLE:  'New push button', cursor=1",
     "SPEECH OUTPUT: 'New push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "16. Tab to next widget",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Formatting tool bar Liberation Sans $l combo box'",
     "     VISIBLE:  'Liberation Sans $l combo box', cursor=1",
     "SPEECH OUTPUT: 'Font Name Liberation Sans editable combo box.'",
     "SPEECH OUTPUT: 'Liberation Sans'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(utils.AssertPresentationAction(
    "17. Shift+Tab to return to the previous widget",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Formatting tool bar New push button'",
     "     VISIBLE:  'New push button', cursor=1",
     "SPEECH OUTPUT: 'New push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(utils.AssertPresentationAction(
    "18. Shift+Tab to return to the previous widget",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Formatting tool bar Update push button'",
     "     VISIBLE:  'Update push button', cursor=1",
     "SPEECH OUTPUT: 'Update push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "19. Tab to next widget",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Formatting tool bar New push button'",
     "     VISIBLE:  'New push button', cursor=1",
     "SPEECH OUTPUT: 'New push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "20. Tab to next widget",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Formatting tool bar Liberation Sans $l combo box'",
     "     VISIBLE:  'Liberation Sans $l combo box', cursor=1",
     "SPEECH OUTPUT: 'Font Name Liberation Sans editable combo box.'",
     "SPEECH OUTPUT: 'Liberation Sans'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "21. Tab to next widget",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Formatting tool bar 28 $l combo box'",
     "     VISIBLE:  '28 $l combo box', cursor=1",
     "SPEECH OUTPUT: 'Font Size 28 editable combo box.'",
     "SPEECH OUTPUT: '28'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "22. Tab to next widget",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Formatting tool bar &=y Bold toggle button'",
     "     VISIBLE:  '&=y Bold toggle button', cursor=1",
     "SPEECH OUTPUT: 'Bold on'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "23. Tab to next widget",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Formatting tool bar & y Italic toggle button'",
     "     VISIBLE:  '& y Italic toggle button', cursor=1",
     "SPEECH OUTPUT: 'Italic off'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "24. Tab to next widget",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Formatting tool bar & y Underline toggle button'",
     "     VISIBLE:  '& y Underline toggle button', cursor=1",
     "SPEECH OUTPUT: 'Underline off'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "25. Toggle its state",
    ["SPEECH OUTPUT: 'Underline on'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "26. Tab to next widget",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Formatting tool bar & y Strikethrough toggle button'",
     "     VISIBLE:  '& y Strikethrough toggle button', cursor=1",
     "SPEECH OUTPUT: 'Strikethrough off'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(utils.AssertPresentationAction(
    "27. Shift Tab to previous widget",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer root pane Formatting tool bar &=y Underline toggle button'",
     "     VISIBLE:  '&=y Underline toggle button', cursor=1",
     "SPEECH OUTPUT: 'Underline on'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "28. Toggle its state",
    ["SPEECH OUTPUT: 'Underline off'"]))

sequence.append(KeyComboAction("<Alt>F4"))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
