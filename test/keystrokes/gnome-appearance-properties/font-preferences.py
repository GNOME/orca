#!/usr/bin/python

"""Testing of font preferences in the gnome-appearance properties dialog."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# Wait for the application gnome-appearance-properties comes up and
# then navigate to the Fonts tab
#
sequence.append(WaitForWindowActivate("Appearance Preferences"))
sequence.append(WaitForFocus("Theme", acc_role=pyatspi.ROLE_PAGE_TAB))

sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Background", acc_role=pyatspi.ROLE_PAGE_TAB))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Fonts", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(utils.AssertPresentationAction(
    "Fonts tab",
    ["BRAILLE LINE:  'gnome-appearance-properties Application Appearance Preferences Dialog Fonts'",
     "     VISIBLE:  'Fonts', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Fonts page'"]))

########################################################################
# Open the 'Pick a Font' dialog
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PUSH_BUTTON))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Alt>a"))
#sequence.append(WaitForWindowActivate("Pick a Font"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TABLE))
sequence.append(utils.AssertPresentationAction(
    "Pick a Font dialog",
    ["BRAILLE LINE:  'gnome-appearance-properties Application Pick a Font FontChooser'",
     "     VISIBLE:  'Pick a Font FontChooser', cursor=1",
     "BRAILLE LINE:  'gnome-appearance-properties Application Pick a Font FontChooser ScrollPane Family: Table Family ColumnHeader Sans'",
     "     VISIBLE:  'Sans', cursor=1",
     "SPEECH OUTPUT: 'Pick a Font font chooser'",
     "SPEECH OUTPUT: 'Family: table'",
     "SPEECH OUTPUT: 'Family column header'",
     "SPEECH OUTPUT: 'Sans'"]))

########################################################################
# Examine the Family a little bit
#
#sequence.append(KeyComboAction("<Alt>f")) # 'Family' is already selected
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitAction("object:state-changed:selected",
                           None,
                           None,
                           pyatspi.ROLE_TABLE_CELL,
                           5000))
sequence.append(KeyComboAction("Up"))
sequence.append(WaitAction("object:state-changed:selected",
                           None,
                           None,
                           pyatspi.ROLE_TABLE_CELL,
                           5000))
sequence.append(utils.AssertPresentationAction(
    "Examine Family",
    ["BRAILLE LINE:  'gnome-appearance-properties Application Pick a Font FontChooser ScrollPane Family: Table Family ColumnHeader Saraswati 5'",
     "     VISIBLE:  'Saraswati 5', cursor=1",
     "BRAILLE LINE:  'gnome-appearance-properties Application Pick a Font FontChooser ScrollPane Family: Table Family ColumnHeader Sans'",
     "     VISIBLE:  'Sans', cursor=1",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Saraswati 5'",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Sans'"]))

########################################################################
# Go over the style
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TABLE))
sequence.append(utils.AssertPresentationAction(
    "Style table",
    ["BRAILLE LINE:  'gnome-appearance-properties Application Pick a Font FontChooser ScrollPane Style: Table Face ColumnHeader Regular'",
     "     VISIBLE:  'Regular', cursor=1",
     "SPEECH OUTPUT: 'Style: table'",
     "SPEECH OUTPUT: 'Face column header'",
     "SPEECH OUTPUT: 'Regular'"]))

########################################################################
# Go to the 'Size' areas and change it to 18 from 10
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TEXT))
sequence.append(utils.AssertPresentationAction(
    "Size table",
    ["BRAILLE LINE:  'gnome-appearance-properties Application Pick a Font FontChooser Size: 10 $l'",
     "     VISIBLE:  'Size: 10 $l', cursor=7",
     "BRAILLE LINE:  'gnome-appearance-properties Application Pick a Font FontChooser Size: 10 $l'",
     "     VISIBLE:  'Size: 10 $l', cursor=9",
     "SPEECH OUTPUT: ''",
     "SPEECH OUTPUT: 'Size: text 10'"]))
#sequence.append(KeyComboAction("<Alt>z")) # 'Size' is already selected
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("18"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitAction("object:selection-changed",
                           None,
                           None,
                           pyatspi.ROLE_TABLE,
                           5000))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TABLE))
sequence.append(utils.AssertPresentationAction(
    "Change size",
    ["BRAILLE LINE:  'gnome-appearance-properties Application Pick a Font FontChooser Size: 10 $l'",
     "     VISIBLE:  'Size: 10 $l', cursor=9",
     "BRAILLE LINE:  'gnome-appearance-properties Application Pick a Font FontChooser Size: 10 $l'",
     "     VISIBLE:  'Size: 10 $l', cursor=7",
     "BRAILLE LINE:  'gnome-appearance-properties Application Pick a Font FontChooser Size: 1 $l'",
     "     VISIBLE:  'Size: 1 $l', cursor=8",
     "BRAILLE LINE:  'gnome-appearance-properties Application Pick a Font FontChooser Size: 1 $l'",
     "     VISIBLE:  'Size: 1 $l', cursor=8",
     "BRAILLE LINE:  'gnome-appearance-properties Application Pick a Font FontChooser Size: 18 $l'",
     "     VISIBLE:  'Size: 18 $l', cursor=9",
     "BRAILLE LINE:  'gnome-appearance-properties Application Pick a Font FontChooser Size: 18 $l'",
     "     VISIBLE:  'Size: 18 $l', cursor=9",
     "BRAILLE LINE:  'gnome-appearance-properties Application Pick a Font FontChooser ScrollPane Size: Table Size ColumnHeader 18'",
     "     VISIBLE:  '18', cursor=1",
     "SPEECH OUTPUT: 'Size: table'",
     "SPEECH OUTPUT: 'Size column header'",
     "SPEECH OUTPUT: '18'"]))

########################################################################
# Accept the change and dismiss the 'Pick a Font' dialog.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TEXT))

# check the font attributes
sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(TypeAction("f"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Check text attributes for size 18",
    ["SPEECH OUTPUT: 'size 18'",
     "SPEECH OUTPUT: 'family-name Sans'"]))

sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Cancel", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("OK", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("<Alt>o"))

########################################################################
# Bring the 'Pick a Font' dialog back up
#
#sequence.append(WaitForWindowActivate("Appearance Preferences"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Return"))

#sequence.append(WaitForWindowActivate("Pick a Font"))
sequence.append(WaitForFocus("OK", acc_role=pyatspi.ROLE_PUSH_BUTTON))

########################################################################
# Go to the 'Size' areas and change it to 10 from 18
#
sequence.append(KeyComboAction("<Alt>z"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("10"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitAction("object:selection-changed",
                           None,
                           None,
                           pyatspi.ROLE_TABLE,
                           5000))

########################################################################
# Accept the change and dismiss the 'Pick a Font' dialog.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TABLE))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TEXT))

# check the font attributes
sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(TypeAction("f"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Check text attributes for size 10",
    ["SPEECH OUTPUT: 'size 10'",
     "SPEECH OUTPUT: 'family-name Sans'"]))

sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Cancel", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("OK", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("<Alt>o"))

########################################################################
# Revert application to original status
#
#sequence.append(WaitForWindowActivate("Appearance Preferences"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(WaitForFocus("Fonts", acc_role=pyatspi.ROLE_PAGE_TAB))

sequence.append(KeyComboAction("Left"))
sequence.append(WaitForFocus("Background", acc_role=pyatspi.ROLE_PAGE_TAB))
sequence.append(KeyComboAction("Left"))
sequence.append(WaitForFocus("Theme", acc_role=pyatspi.ROLE_PAGE_TAB))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
