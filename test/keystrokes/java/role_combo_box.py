#!/usr/bin/python

"""Test of combo boxes in Java's SwingSet2.
"""

from macaroon.playback.keypress_mimic import *

sequence = MacroSequence()

##########################################################################
# We wait for the demo to come up and for focus to be on the toggle button
#
#sequence.append(WaitForWindowActivate("SwingSet2",None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))

# Wait for entire window to get populated.
sequence.append(PauseAction(5000))

##########################################################################
# Tab over to the combo box demo, and activate it.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(TypeAction(" "))

##########################################################################
# Tab all the way down to the button page tab.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("ComboBox Demo", acc_role=pyatspi.ROLE_PAGE_TAB))

##########################################################################
# Expected output when focusing over first combo box
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane ComboBox Demo TabList ComboBox Demo Presets: Philip, Howard, Jeff Combo'
#      VISIBLE:  'Philip, Howard, Jeff Combo', cursor=1
# 
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Presets: Philip, Howard, Jeff combo box'


sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Philip, Howard, Jeff", 
                             acc_role=pyatspi.ROLE_COMBO_BOX))


########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented:
#
# SPEECH OUTPUT: 'Presets:'
# SPEECH OUTPUT: 'combo box'
# SPEECH OUTPUT: 'Philip, Howard, Jeff'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: ''
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

##########################################################################
# Bring up combo box list by pressing space, the following should be 
# in output:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane ComboBox Demo TabList ComboBox Demo  ComboPhilip, Howard, JeffPresets:  PopupMenu ScrollPane Viewport List Philip, Howard, Jeff Label'
#      VISIBLE:  'Philip, Howard, Jeff Label', cursor=1
# 
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Philip, Howard, Jeff label unselected'

sequence.append(TypeAction(" "))

##########################################################################
# Arrow down to next list item.
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane ComboBox Demo TabList ComboBox Demo  ComboHoward, Scott, HansPresets:  PopupMenu ScrollPane Viewport List Jeff, Larry, Philip Label'
#      VISIBLE:  'Jeff, Larry, Philip Label', cursor=1
# 
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Jeff, Larry, Philip label unselected'
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Jeff, Larry, Philip", acc_role=pyatspi.ROLE_LABEL))

##########################################################################
# Arrow down to next list item.
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane ComboBox Demo TabList ComboBox Demo  ComboPhilip, Jeff, HansPresets:  PopupMenu ScrollPane Viewport List Howard, Scott, Hans Label'
#      VISIBLE:  'Howard, Scott, Hans Label', cursor=1
# 
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Howard, Scott, Hans label unselected'

sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Howard, Scott, Hans", acc_role=pyatspi.ROLE_LABEL))

########################################################################
# TODO: Shouldn't this have more info? Like "item x of y"?
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented:
#
# SPEECH OUTPUT: 'Howard, Scott, Hans'
# SPEECH OUTPUT: 'label'

sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

##########################################################################
# Arrow down to next list item.
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane ComboBox Demo TabList ComboBox Demo  ComboPhilip, Jeff, HansPresets:  PopupMenu ScrollPane Viewport List Philip, Jeff, Hans Label'
#      VISIBLE:  'Philip, Jeff, Hans Label', cursor=1
# 
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Philip, Jeff, Hans label selected'

sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Philip, Jeff, Hans", acc_role=pyatspi.ROLE_LABEL))

##########################################################################
# Press return to close list and select current item.
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane ComboBox Demo TabList ComboBox Demo Presets: Philip, Jeff, Hans Combo'
#      VISIBLE:  'Philip, Jeff, Hans Combo', cursor=1
# 
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Presets: Philip, Jeff, Hans combo box'
sequence.append(KeyComboAction("Return"))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented:
#
# SPEECH OUTPUT: 'Presets:'
# SPEECH OUTPUT: 'combo box'
# SPEECH OUTPUT: 'Philip, Jeff, Hans'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: ''
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

##########################################################################
# Bring up combo box list by pressing space, the following should be 
# in output:
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane ComboBox Demo TabList ComboBox Demo  ComboPhilip, Jeff, HansPresets:  PopupMenu ScrollPane Viewport List Philip, Jeff, Hans Label'
#      VISIBLE:  'Philip, Jeff, Hans Label', cursor=1
# 
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Philip, Jeff, Hans label selected'
sequence.append(TypeAction(" "))

##########################################################################
# Arrow up to previous list item.
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane ComboBox Demo TabList ComboBox Demo  ComboHoward, Scott, HansPresets:  PopupMenu ScrollPane Viewport List Howard, Scott, Hans Label'
#      VISIBLE:  'Howard, Scott, Hans Label', cursor=1
# 
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Howard, Scott, Hans label selected'
sequence.append(KeyComboAction("Up"))
sequence.append(WaitForFocus("Howard, Scott, Hans", acc_role=pyatspi.ROLE_LABEL))

##########################################################################
# Arrow up to previous list item.
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Combo
# Box Demo TabList ComboBox Demo  ComboJeff, Larry, PhilipPresets:  PopupMenu ScrollPane Viewport List Jeff, Larry, Philip Label'
#      VISIBLE:  'Jeff, Larry, Philip Label', cursor=1
# 
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Jeff, Larry, Philip label unselected'
sequence.append(KeyComboAction("Up"))
sequence.append(WaitForFocus("Jeff, Larry, Philip", acc_role=pyatspi.ROLE_LABEL))

##########################################################################
# Arrow up to previous list item.
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane ComboBox Demo TabList ComboBox Demo  ComboPhilip, Howard, JeffPresets:  PopupMenu ScrollPane Viewport List Philip, Howard, Jeff Label'
#      VISIBLE:  'Philip, Howard, Jeff Label', cursor=1
# 
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Philip, Howard, Jeff label selected'
sequence.append(KeyComboAction("Up"))
sequence.append(WaitForFocus("Philip, Howard, Jeff", acc_role=pyatspi.ROLE_LABEL))

##########################################################################
# Press return to close list and select current item.
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane ComboBox Demo TabList ComboBox Demo Presets: Philip, Howard, Jeff Combo'
#      VISIBLE:  'Philip, Howard, Jeff Combo', cursor=1
# 
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Presets: Philip, Howard, Jeff combo box'
sequence.append(KeyComboAction("Return"))

##########################################################################
# Tab to next combo box.
# 
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane ComboBox Demo TabList ComboBox Demo Hair: Philip Combo'
#      VISIBLE:  'Philip Combo', cursor=1
# 
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Hair: Philip combo box'
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Philip", acc_role=pyatspi.ROLE_COMBO_BOX))

##########################################################################
# Tab to next combo box.
#
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane ComboBox Demo TabList ComboBox Demo Eyes & Nose: Howard Combo'
#      VISIBLE:  'Howard Combo', cursor=1
# 
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Eyes & Nose: Howard combo box'
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Howard", acc_role=pyatspi.ROLE_COMBO_BOX))

##########################################################################
# Tab to next combo box.
#
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane ComboBox Demo TabList ComboBox Demo Mouth: Jeff Combo'
#      VISIBLE:  'Jeff Combo', cursor=1
# 
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Mouth: Jeff combo box'
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Jeff", acc_role=pyatspi.ROLE_COMBO_BOX))


##########################################################################
# Tab back up to starting state
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TEXT))
sequence.append(KeyComboAction("Tab"))

sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))
# Toggle the top left button, to return to normal state.
sequence.append(TypeAction           (" "))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
