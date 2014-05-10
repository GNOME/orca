#!/usr/bin/python

"""Test of Orca's presentation of Writer toolbar buttons."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("F6"))
sequence.append(utils.AssertPresentationAction(
    "1. F6 to menu bar",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane File menu'",
     "     VISIBLE:  'File menu', cursor=1",
     "SPEECH OUTPUT: 'File menu'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("F6"))
sequence.append(utils.AssertPresentationAction(
    "2. F6 to Standard toolbar",
    ["KNOWN ISSUE: We are not speaking the toolbar name",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Standard tool bar New push button'",
     "     VISIBLE:  'New push button', cursor=1",
     "SPEECH OUTPUT: 'New push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>F1"))
sequence.append(utils.AssertPresentationAction(
    "3. Control F1 to show Tooltip.",
    ["KNOWN ISSUE: We are presenting nothing here.",
     ""]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "4. Right Arrow to Open button",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Standard tool bar Open push button'",
     "     VISIBLE:  'Open push button', cursor=1",
     "SPEECH OUTPUT: 'Open push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "5. Right Arrow to Save button",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Standard tool bar Save push button'",
     "     VISIBLE:  'Save push button', cursor=1",
     "SPEECH OUTPUT: 'Save push button grayed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("F6"))
sequence.append(KeyComboAction("F6"))
sequence.append(utils.AssertPresentationAction(
    "6. F6 to Formatting Toolbar",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Formatting tool bar Styles and Formatting push button'",
     "     VISIBLE:  'Styles and Formatting push butto', cursor=1",
     "SPEECH OUTPUT: 'Styles and Formatting push button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(utils.AssertPresentationAction(
    "7. Right to Apply Style",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Formatting tool bar Apply Style panel'",
     "     VISIBLE:  'Apply Style panel', cursor=1",
     "SPEECH OUTPUT: 'Apply Style panel'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "8. Return to activate Apply Style",
    ["KNOWN ISSUE: Way too chatty here and in the next assertions",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Formatting tool bar Default Style $l'",
     "     VISIBLE:  'Default Style $l', cursor=14",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Formatting tool bar Default Style $l'",
     "     VISIBLE:  'Default Style $l', cursor=14",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Formatting tool bar  combo boxDefault Style $l Clear formatting list item'",
     "     VISIBLE:  'Clear formatting list item', cursor=1",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Formatting tool bar Default Style $l'",
     "     VISIBLE:  'Default Style $l', cursor=14",
     "SPEECH OUTPUT: 'Default Style combo box'",
     "SPEECH OUTPUT: 'text Default Style selected'",
     "SPEECH OUTPUT: 'Clear formatting'",
     "SPEECH OUTPUT: 'text Default Style selected'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Down in Apply Style (Collapsed)",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Formatting tool bar Text Body $l'",
     "     VISIBLE:  'Text Body $l', cursor=10",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Formatting tool bar Text Body $l'",
     "     VISIBLE:  'Text Body $l', cursor=10",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Formatting tool bar Text Body $l'",
     "     VISIBLE:  'Text Body $l', cursor=10",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Formatting tool bar Text Body $l'",
     "     VISIBLE:  'Text Body $l', cursor=10",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Formatting tool bar  combo boxText Body $l Text Body list item'",
     "     VISIBLE:  'Text Body list item', cursor=1",
     "SPEECH OUTPUT: 'Text Body'",
     "SPEECH OUTPUT: 'unselected' voice=system",
     "SPEECH OUTPUT: 'Text Body'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Down in Apply Style (Collapsed)",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Formatting tool bar Quotations $l'",
     "     VISIBLE:  'Quotations $l', cursor=11",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Formatting tool bar Quotations $l'",
     "     VISIBLE:  'Quotations $l', cursor=11",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Formatting tool bar  combo boxQuotations $l Quotations list item'",
     "     VISIBLE:  'Quotations list item', cursor=1",
     "SPEECH OUTPUT: 's'",
     "SPEECH OUTPUT: 'selected' voice=system",
     "SPEECH OUTPUT: 'Quotations'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Alt Down to expand list",
    ["KNOWN ISSUE: We are presenting nothing here.",
     ""]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. Down in Apply Style (Expanded)",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Formatting tool bar Title $l'",
     "     VISIBLE:  'Title $l', cursor=6",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Formatting tool bar Title $l'",
     "     VISIBLE:  'Title $l', cursor=6",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Formatting tool bar  combo boxTitle $l Title list item'",
     "     VISIBLE:  'Title list item', cursor=1",
     "SPEECH OUTPUT: 'unselected' voice=system",
     "SPEECH OUTPUT: 'Title'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "13. Down in Apply Style (Expanded)",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Formatting tool bar Subtitle $l'",
     "     VISIBLE:  'Subtitle $l', cursor=9",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Formatting tool bar Subtitle $l'",
     "     VISIBLE:  'Subtitle $l', cursor=9",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Formatting tool bar  combo boxSubtitle $l Subtitle list item'",
     "     VISIBLE:  'Subtitle list item', cursor=1",
     "SPEECH OUTPUT: 'tle'",
     "SPEECH OUTPUT: 'selected' voice=system",
     "SPEECH OUTPUT: 'Subtitle'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "14. Up in Apply Style (Expanded)",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Formatting tool bar Title $l'",
     "     VISIBLE:  'Title $l', cursor=6",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Formatting tool bar Title $l'",
     "     VISIBLE:  'Title $l', cursor=6",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Formatting tool bar  combo boxTitle $l Title list item'",
     "     VISIBLE:  'Title list item', cursor=1",
     "SPEECH OUTPUT: 'unselected' voice=system",
     "SPEECH OUTPUT: 'Title'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "15. Up in Apply Style (Expanded)",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Formatting tool bar Quotations $l'",
     "     VISIBLE:  'Quotations $l', cursor=11",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Formatting tool bar Quotations $l'",
     "     VISIBLE:  'Quotations $l', cursor=11",
     "BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Formatting tool bar  combo boxQuotations $l Quotations list item'",
     "     VISIBLE:  'Quotations list item', cursor=1",
     "SPEECH OUTPUT: 'tions'",
     "SPEECH OUTPUT: 'selected' voice=system",
     "SPEECH OUTPUT: 'Quotations'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>Up"))
sequence.append(utils.AssertPresentationAction(
    "16. Alt+Up to collapse list",
    ["KNOWN ISSUE: We are presenting nothing here.",
     ""]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "17. Tab to Font Name",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Formatting tool bar Font Name panel'",
     "     VISIBLE:  'Font Name panel', cursor=1",
     "SPEECH OUTPUT: 'Font Name panel'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "18. Tab to Font Size",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Formatting tool bar Font Size panel'",
     "     VISIBLE:  'Font Size panel', cursor=1",
     "SPEECH OUTPUT: 'Font Size panel'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "19. Tab to Bold",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Formatting tool bar & y Bold toggle button'",
     "     VISIBLE:  '& y Bold toggle button', cursor=1",
     "SPEECH OUTPUT: 'Bold off'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "20. Toggle Bold on",
    ["SPEECH OUTPUT: 'Bold on'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(utils.AssertPresentationAction(
    "21. Tab to Italic",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Formatting tool bar & y Italic toggle button'",
     "     VISIBLE:  '& y Italic toggle button', cursor=1",
     "SPEECH OUTPUT: 'Italic off'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(utils.AssertPresentationAction(
    "22. Shift Tab to Bold",
    ["BRAILLE LINE:  'soffice application Untitled 1 - LibreOffice Writer frame Untitled 1 - LibreOffice Writer root pane Formatting tool bar &=y Bold toggle button'",
     "     VISIBLE:  '&=y Bold toggle button', cursor=1",
     "SPEECH OUTPUT: 'Bold on'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "23. Toggle Bold off",
    ["SPEECH OUTPUT: 'Bold off'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
