#!/usr/bin/python

"""Test of combo box output using Firefox.
"""

from macaroon.playback import *

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Open the "Edit" menu and Up Arrow to Preferences, then press Return.
#
sequence.append(KeyComboAction("<Alt>e"))
sequence.append(WaitForFocus("Undo", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Up"))
sequence.append(WaitForFocus("Preferences", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Return"))

########################################################################
# We wait for the Preferences dialog to appear.  When it does, press
# Tab to move to the "When Minefield starts" combo box.  This combo
# box is contained in a scroll pane called Main (which didn't used to
# have focus) in a panel called "Startup".  The currently selected item
# in the combo box is "Show a blank page".
#
# BRAILLE LINE:  'Minefield Application Minefield Preferences Dialog Main ScrollPane Startup Panel When Minefield starts: Show a blank page Combo'
#      VISIBLE:  'Show a blank page Combo', cursor=1
# SPEECH OUTPUT: 'Main scroll pane Startup panel'
# SPEECH OUTPUT: 'When Minefield starts: Show a blank page combo box'
#
sequence.append(WaitForWindowActivate("Minefield Preferences",None))
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus("When Minefield starts:", acc_role=pyatspi.ROLE_COMBO_BOX))

########################################################################
# Now that focus is on the combo box, arrow down to "Show my windows
# and tabs from last time". [[[Bug 1: Due to a Firefox regression around
# 1 Sept, we no longer get events when arrowing in a collapsed XUL
# combo box.  This is a known issue. For now, this test was conducted 
# prior to that regression so that we would have coverage for combo
# boxes.]]] [[[Bug 2, which may or may not be resolved when they fix
# Bug 1:  Tabbing to the combo box gave focus to the combo box; not
# the selected menu item.  It seems that as a result we first get a
# focus event for the original item, followed by a focus event for the
# item that just gained focus.]]] [[[Bug 3:  What's up with the brl?]]]
# 
# BRAILLE LINE:  'Minefield Application Minefield Preferences Dialog Main ScrollPane Startup Panel  ComboShow my windows and tabs from last timeWhen Minefield starts:  Show a blank page'
#      VISIBLE:  'Show a blank page', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Show a blank page'
#
# BRAILLE LINE:  'Minefield Application Minefield Preferences Dialog Main ScrollPane Startup Panel  ComboShow my windows and tabs from last timeWhen Minefield starts:  Show my windows and tabs from last time'
#      VISIBLE:  'Show my windows and tabs from la', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Show my windows and tabs from last time'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Show my windows and tabs from last time", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Down arrow again to "Show my home page".
#
# BRAILLE LINE:  'Minefield Application Minefield Preferences Dialog Main ScrollPane Startup Panel  ComboShow my home pageWhen Minefield starts:  Show my home page'
#      VISIBLE:  'Show my home page', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Show my home page'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Show my home page", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Up arrow back to "Show my windows and tabs from last time".
#
# BRAILLE LINE:  'Minefield Application Minefield Preferences Dialog Main ScrollPane Startup Panel  ComboShow my windows and tabs from last timeWhen Minefield starts:  Show my windows and tabs from last time'
#      VISIBLE:  'Show my windows and tabs from la', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Show my windows and tabs from last time'
#
sequence.append(KeyComboAction("Up"))
sequence.append(WaitForFocus("Show my windows and tabs from last time", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Up arrow back to "Show a blank page".
#
# BRAILLE LINE:  'Minefield Application Minefield Preferences Dialog Main ScrollPane Startup Panel  ComboShow a blank pageWhen Minefield starts:  Show a blank page'
#      VISIBLE:  'Show a blank page', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Show a blank page'
#
sequence.append(KeyComboAction("Up"))
sequence.append(WaitForFocus("Show a blank page", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Now expand the combo box with Alt+Down Arrow.  [[[Bug?  I don't think
# we're getting any events related to the combo box expanding,
# we aren't speaking or brailling anything]]].
#
sequence.append(KeyComboAction("<Alt>Down"))

########################################################################
# Down arrow again to "Show my windows and tabs from last time".
#
# BRAILLE LINE:  'Minefield Application Minefield Preferences Dialog Main ScrollPane Startup Panel  ComboShow a blank pageWhen Minefield starts:  Show my windows and tabs from last time'
#      VISIBLE:  'Show my windows and tabs from la', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Show my windows and tabs from last time'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Show my windows and tabs from last time", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Up arrow back to "Show a blank page".
#
# BRAILLE LINE:  'Minefield Application Minefield Preferences Dialog Main ScrollPane Startup Panel  ComboShow a blank pageWhen Minefield starts:  Show a blank page'
#      VISIBLE:  'Show a blank page', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Show a blank page'
#
sequence.append(KeyComboAction("Up"))
sequence.append(WaitForFocus("Show a blank page", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Press Return to collapse the combo box.
#
# BRAILLE LINE:  'Minefield Application Minefield Preferences Dialog Main ScrollPane Startup Panel When Minefield starts: Show a blank page Combo'
#     VISIBLE:  'Show a blank page Combo', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'When Minefield starts: Show a blank page combo box'
#
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("When Minefield starts:", acc_role=pyatspi.ROLE_COMBO_BOX))

########################################################################
# Now try first letter navigation.  All of the items begin with S.
# The first press should move us to "Show my home page"
#
# BRAILLE LINE:  'Minefield Application Minefield Preferences Dialog Main ScrollPane Startup Panel  ComboShow my home pageWhen Minefield starts:  Show my home page'
#      VISIBLE:  'Show my home page', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Show my home page'
#
sequence.append(TypeAction("s"))
sequence.append(WaitForFocus("Show my home page", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# The second press should move us back to "Show a blank page".
#
# BRAILLE LINE:  'Minefield Application Minefield Preferences Dialog Main ScrollPane Startup Panel  ComboShow a blank pageWhen Minefield starts:  Show a blank page'
#      VISIBLE:  'Show a blank page', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Show a blank page'
#
sequence.append(TypeAction("s"))
sequence.append(WaitForFocus("Show a blank page", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  [[[Bug:  Techically the parent
# of the focused menu item (what combo boxes contain) is a menu, but
# in this case we presumably want to indicate that the focused item
# is a combo box.]]]
#
# BRAILLE LINE:  'Minefield Application Minefield Preferences Dialog Main ScrollPane Startup Panel  ComboShow a blank pageWhen Minefield starts:  Show a blank page'
#      VISIBLE:  'Show a blank page', cursor=1
# SPEECH OUTPUT: 'Show a blank page menu'
# SPEECH OUTPUT: 'Show a blank page'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: ''
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Press Shift+Tab to move back to the Main list item.
#
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(WaitForFocus("Main", acc_role=pyatspi.ROLE_LIST_ITEM))

########################################################################
# Dismiss the dialog by pressing Escape and wait for the location bar
# to regain focus.
#
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
