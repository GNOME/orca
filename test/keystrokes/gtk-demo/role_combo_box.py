#!/usr/bin/python

"""Test of combobox output using the gtk-demo Combo boxes demo.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))

########################################################################
# Once gtk-demo is running, invoke the Combo boxes demo 
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Combo boxes", 1000))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# When the Combo boxes demo window appears, open the combo box.
#
#sequence.append(WaitForWindowActivate("Combo boxes",None))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_COMBO_BOX))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(WaitForFocus("Warning", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "Warning combo box item",
    ["BRAILLE LINE:  'gtk-demo Application Window'",
     "     VISIBLE:  'gtk-demo Application Window', cursor=22",
     "BRAILLE LINE:  'gtk-demo Application Combo boxes Frame Some stock icons Panel  ComboWarning Warning'",
     "     VISIBLE:  'Warning', cursor=1",
     "SPEECH OUTPUT: 'window'",
     "SPEECH OUTPUT: 'Some stock icons panel Warning'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
# JD to WDW: This to me looks like two bug fixes:
# 1) Lost a trailing space
# 2) Before we were saying "menu"; I don't think we should in a combo box,
#    even though technically there is a menu in between a combo box and
#    the options it contains in the hierarchy.
# Question: Should we be presenting the containing panel or not?
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Warning combo box item Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application Combo boxes Frame Some stock icons Panel  ComboWarning Warning'",
     "     VISIBLE:  'Warning', cursor=1",
     "SPEECH OUTPUT: 'Some stock icons panel Warning 1 of 5'"]))

########################################################################
# Now arrow down and select the "New" item.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "New combo box item",
    ["BRAILLE LINE:  'gtk-demo Application Combo boxes Frame Some stock icons Panel  ComboWarning New'",
     "     VISIBLE:  'New', cursor=1",
     "SPEECH OUTPUT: 'New'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
# JD to WDW: This to me looks like two bug fixes:
# 1) Lost a trailing space
# 2) Before we were saying "menu"; I don't think we should in a combo box,
#    even though technically there is a menu in between a combo box and
#    the options it contains in the hierarchy.
# Question: Should we be presenting the containing panel or not?
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "New combo box item Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application Combo boxes Frame Some stock icons Panel  ComboWarning New'",
     "     VISIBLE:  'New', cursor=1",
     "SPEECH OUTPUT: 'Some stock icons panel New 3 of 5'"]))

########################################################################
# Select the "New" entry and tab to the editable text combo box.  Skip
# the middle combo.  It's bizarre.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_COMBO_BOX))
sequence.append(utils.AssertPresentationAction(
    "New combo box item selection",
    ["BRAILLE LINE:  'gtk-demo Application Combo boxes Frame'",
     "     VISIBLE:  'Combo boxes Frame', cursor=1",
     "BRAILLE LINE:  'gtk-demo Application Combo boxes Frame Some stock icons Panel New Combo'",
     "     VISIBLE:  'New Combo', cursor=1",
     "SPEECH OUTPUT: 'Combo boxes frame'",
     "SPEECH OUTPUT: 'Some stock icons panel New combo box'"]))

sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Boston", acc_role=pyatspi.ROLE_COMBO_BOX))

########################################################################
# Land on the editable text combo box.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(utils.AssertPresentationAction(
    "Editable text combo box",
    ["BRAILLE LINE:  'gtk-demo Application Combo boxes Frame Editable Panel  $l'",
     "     VISIBLE:  ' $l', cursor=1",
     "SPEECH OUTPUT: 'Editable panel text '"]))

########################################################################
# Type "Four" in the text area.
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction("Four"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Editable text combo box typing",
    ["KNOWN ISSUE - Looks like we are getting more events than we would like causing us to update braille frequently;",
     "BRAILLE LINE:  'gtk-demo Application Combo boxes Frame Editable Panel  $l'",
     "     VISIBLE:  ' $l', cursor=2",
     "BRAILLE LINE:  'gtk-demo Application Combo boxes Frame Editable Panel F $l'",
     "     VISIBLE:  'F $l', cursor=2",
     "BRAILLE LINE:  'gtk-demo Application Combo boxes Frame Editable Panel F $l'",
     "     VISIBLE:  'F $l', cursor=3",
     "BRAILLE LINE:  'gtk-demo Application Combo boxes Frame Editable Panel Fo $l'",
     "     VISIBLE:  'Fo $l', cursor=3",
     "BRAILLE LINE:  'gtk-demo Application Combo boxes Frame Editable Panel Fo $l'",
     "     VISIBLE:  'Fo $l', cursor=4",
     "BRAILLE LINE:  'gtk-demo Application Combo boxes Frame Editable Panel Fou $l'",
     "     VISIBLE:  'Fou $l', cursor=4",
     "BRAILLE LINE:  'gtk-demo Application Combo boxes Frame Editable Panel Fou $l'",
     "     VISIBLE:  'Fou $l', cursor=5",
     "BRAILLE LINE:  'gtk-demo Application Combo boxes Frame Editable Panel Four $l'",
     "     VISIBLE:  'Four $l', cursor=5"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Editable text combo box Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application Combo boxes Frame Editable Panel Four $l'",
     "     VISIBLE:  'Four $l', cursor=5",
     "SPEECH OUTPUT: 'text Four'"]))

########################################################################
# Tab to the triangular down arrow of the editable combo box.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_COMBO_BOX))
sequence.append(utils.AssertPresentationAction(
    "Editable text combo box open button",
    ["BRAILLE LINE:  'gtk-demo Application Combo boxes Frame Editable Panel Four $l Combo'",
     "     VISIBLE:  'Four $l Combo', cursor=5",
     "SPEECH OUTPUT: 'Four combo box'"]))

########################################################################
# Tab back to the top combo box and put things back the way they were.
# Then, go back to the combo box where you typed "Four".
#
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_COMBO_BOX))
sequence.append(TypeAction(" "))

sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(KeyComboAction("Up"))

sequence.append(WaitForFocus("Warning", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForFocus("Warning", acc_role=pyatspi.ROLE_COMBO_BOX))
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus("Boston", acc_role=pyatspi.ROLE_COMBO_BOX))

########################################################################
# When you land on the "Four" combo box, the text should be selected.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_COMBO_BOX))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(utils.AssertPresentationAction(
    "Editable text combo box with selected text",
    ["BRAILLE LINE:  'gtk-demo Application Combo boxes Frame Editable Panel Four $l'",
     "     VISIBLE:  'Four $l', cursor=5",
     "SPEECH OUTPUT: 'text Four selected'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "Editable text combo box with selected text Where Am I",
    ["BRAILLE LINE:  'gtk-demo Application Combo boxes Frame Editable Panel Four $l'",
     "     VISIBLE:  'Four $l', cursor=5",
     "SPEECH OUTPUT: 'text Four selected'"]))

########################################################################
# Tab to the triangular down arrow of the editable combo box and open
# the combo box.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_COMBO_BOX))

sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("One", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "Editable text combo box menu",
    ["BRAILLE LINE:  'gtk-demo Application Window'",
     "     VISIBLE:  'gtk-demo Application Window', cursor=22",
     "BRAILLE LINE:  'gtk-demo Application Combo boxes Frame Editable Panel  ComboFour $l One'",
     "     VISIBLE:  'One', cursor=1",
     "SPEECH OUTPUT: 'window'",
     "SPEECH OUTPUT: 'Editable panel One'"]))

########################################################################
# Now down arrow to the "Two" item.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Two", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "Editable text combo box One item",
    ["BRAILLE LINE:  'gtk-demo Application Combo boxes Frame Editable Panel  ComboFour $l Two'",
     "     VISIBLE:  'Two', cursor=1",
     "SPEECH OUTPUT: 'Two'"]))

########################################################################
# Select "Two" and Shift+Tab back to the text area.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Return"))
sequence.append(utils.AssertPresentationAction(
    "Editable text combo box Two selected",
    ["BRAILLE LINE:  'gtk-demo Application Combo boxes Frame'",
     "     VISIBLE:  'Combo boxes Frame', cursor=1",
     "BRAILLE LINE:  'gtk-demo Application Combo boxes Frame Editable Panel Two $l Combo'",
     "     VISIBLE:  'Two $l Combo', cursor=1",
     "BRAILLE LINE:  'gtk-demo Application Combo boxes Frame Editable Panel Two $l'",
     "     VISIBLE:  'Two $l', cursor=1",
     "SPEECH OUTPUT: 'Combo boxes frame'",
     "SPEECH OUTPUT: 'Editable panel Two combo box'"]))

sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_COMBO_BOX))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(utils.AssertPresentationAction(
    "Editable text combo box Two text selected",
    ["KNOWN ISSUE -   Sometimes we speak selected at the end; sometimes we do not. Probably a timing issue which we need to investigate.",
     "BRAILLE LINE:  'gtk-demo Application Combo boxes Frame Editable Panel Two $l'",
     "     VISIBLE:  'Two $l', cursor=4",
     "SPEECH OUTPUT: 'text Two selected'"]))

########################################################################
# Close the Combo boxes demo
#
sequence.append(KeyComboAction("<Alt>F4", 500))

########################################################################
# Go back to the main gtk-demo window and reselect the
# "Application main window" menu.  Let the harness kill the app.
#
#sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(PauseAction(1000))
sequence.append(KeyComboAction("Home"))

sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TREE_TABLE,
                           5000))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
