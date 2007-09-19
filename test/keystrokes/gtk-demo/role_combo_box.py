#!/usr/bin/python

"""Test of combobox output using the gtk-demo Combo boxes demo.
"""

from macaroon.playback import *

sequence = MacroSequence()

########################################################################
# We wait for the demo to come up and for focus to be on the tree table
#
sequence.append(WaitForWindowActivate("GTK+ Code Demos"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))

########################################################################
# Once gtk-demo is running, invoke the Combo boxes demo 
#
sequence.append(KeyComboAction("<Control>f"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))
sequence.append(TypeAction("Combo boxes", 1000))
sequence.append(KeyComboAction("Return", 500))

########################################################################
# When the Combo boxes demo window appears, the following should be
# presented in speech and braille [[[BUG?: where is that extra "Some
# stock icons" coming from in braille?  It happens throughout this
# test.]]]:
#
# BRAILLE LINE:  'gtk-demo Application Combo boxes Frame Some stock icons Some stock icons Panel Warning Combo'
#      VISIBLE:  'Warning Combo', cursor=1
# 
# SPEECH OUTPUT: 'Combo boxes frame'
# SPEECH OUTPUT: 'Some stock icons panel'
# SPEECH OUTPUT: 'Warning combo box'
# 
#sequence.append(WaitForWindowActivate("Combo boxes",None))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_COMBO_BOX))

########################################################################
# Open the combo box.  The following should be presented in speech and
# braille:
#
# BRAILLE LINE:  'gtk-demo Application Combo boxes Frame Some stock icons Some stock icons Panel  ComboWarning Warning'
#      VISIBLE:  'Warning', cursor=1
#
# SPEECH OUTPUT: 'window'
# SPEECH OUTPUT: 'Some stock icons panel'
# SPEECH OUTPUT: 'Warning'
#
sequence.append(TypeAction(" "))
sequence.append(WaitForFocus("Warning", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'gtk-demo Application Combo boxes Frame Some stock icons Some stock icons Panel  ComboWarning Warning'
#      VISIBLE:  'Warning', cursor=1
#
# SPEECH OUTPUT: ' menu'
# SPEECH OUTPUT: 'Warning'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'item 1 of 5'
# SPEECH OUTPUT: ''
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Now arrow down and select the "New" item.  The following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'gtk-demo Application Combo boxes Frame Some stock icons Some stock icons Panel  ComboWarning New'
#      VISIBLE:  'New', cursor=1
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'New'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
#
# BRAILLE LINE:  'gtk-demo Application Combo boxes Frame Some stock icons Some stock icons Panel  ComboWarning New'
#      VISIBLE:  'New', cursor=1
#
# SPEECH OUTPUT: ' menu'
# SPEECH OUTPUT: 'New'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'item 3 of 5'
# SPEECH OUTPUT: ''
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Select the "New" entry and tab to the editable text combo box.  Skip
# the middle combo.  It's bizarre.
#
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_COMBO_BOX))
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus("Boston", acc_role=pyatspi.ROLE_COMBO_BOX))
sequence.append(KeyComboAction("Tab"))

########################################################################
# When you land on the editable text combo box, the following should
# be presented in speech and braille:
#
# BRAILLE LINE:  'gtk-demo Application Combo boxes Frame Editable Editable Panel  $l'
#      VISIBLE:  ' $l', cursor=1
#
# SPEECH OUTPUT: 'Editable panel'
# SPEECH OUTPUT: 'text '
#
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))

########################################################################
# Type "Four" in the text area and do a basic "Where Am I" via
# KP_Enter.  The following should be presented in speech and braille:
#
# BRAILLE LINE:  'gtk-demo Application Combo boxes Frame Editable Editable Panel Four $l'
#      VISIBLE:  'Four $l', cursor=5
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'text'
# SPEECH OUTPUT: 'Four'
# SPEECH OUTPUT: ''
#
sequence.append(TypeAction("Four"))
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Tab to the triangular down arrow of the editable combo box.  The
# following should be presented in speech and braille:
#
# BRAILLE LINE:  'gtk-demo Application Combo boxes Frame Editable Editable Panel Four Combo'
#      VISIBLE:  'Four Combo', cursor=1
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Four combo box'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_COMBO_BOX))

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
sequence.append(KeyComboAction("Tab"))

########################################################################
# When you land on the "Four" combo box, the following should be
# presented in speech and braille [[[BUG?: the text "Four" is selected,
# shouldn't that be mentioned in speech?  It is displayed as such in
# braille.]]]:
#
# BRAILLE LINE:  'gtk-demo Application Combo boxes Frame Editable Editable Panel Four $l'
#      VISIBLE:  'Four $l', cursor=5
#
# SPEECH OUTPUT: 'Editable panel'
# SPEECH OUTPUT: 'text Four'
#
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
# BRAILLE LINE:  'gtk-demo Application Combo boxes Frame Editable Editable Panel Four $l'
#      VISIBLE:  'Four $l', cursor=5
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'text'
# SPEECH OUTPUT: 'Four'
# SPEECH OUTPUT: 'selected'
# SPEECH OUTPUT: ''
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Tab to the triangular down arrow of the editable combo box and open
# the combo box.  The following should be presented -- note that it
# just mentions a 'menu' since nothing in the menu is selected yet:
#
# BRAILLE LINE:  'gtk-demo Application Combo boxes Frame Editable Editable Panel Menu'
#      VISIBLE:  'Menu', cursor=1
#
# SPEECH OUTPUT: 'window'
# SPEECH OUTPUT: 'Editable panel'
# SPEECH OUTPUT: 'menu'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_COMBO_BOX))
sequence.append(TypeAction(" "))

########################################################################
# Now down arrow to the "Two" item.  The following should be presented
# [[[BUG?: "Two Two" showing up instead of "Two" and double space
# between "Panel ComboTwo":
#
# BRAILLE LINE:  'gtk-demo Application Combo boxes Frame Editable Editable Panel  ComboTwo Two'
#      VISIBLE:  'Two', cursor=1
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Two'
#
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_MENU))
sequence.append(KeyComboAction("Down"))

sequence.append(WaitForFocus("One", acc_role=pyatspi.ROLE_MENU_ITEM))
sequence.append(KeyComboAction("Down"))

sequence.append(WaitForFocus("Two", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Select "Two" and Shift+Tab back to the text area.  The following
# should be presented [[[BUG?: Shouldn't the selection state of "Two"
# be spoken?  The state is shown in braille.]]]:
#
# BRAILLE LINE:  'gtk-demo Application Combo boxes Frame Editable Editable Panel Two $l'
#      VISIBLE:  'Two $l', cursor=4
#
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'text Two'
#
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("Two", acc_role=pyatspi.ROLE_COMBO_BOX))
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TEXT))

########################################################################
# Close the Combo boxes demo
#
sequence.append(KeyComboAction("<Alt>F4", 500))

########################################################################
# Go back to the main gtk-demo window and reselect the
# "Application main window" menu.  Let the harness kill the app.
#
#sequence.append(WaitForWindowActivate("GTK+ Code Demos",None))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_TREE_TABLE))
sequence.append(KeyComboAction("Home"))

sequence.append(WaitAction("object:active-descendant-changed",
                           None,
                           None,
                           pyatspi.ROLE_TREE_TABLE,
                           5000))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
