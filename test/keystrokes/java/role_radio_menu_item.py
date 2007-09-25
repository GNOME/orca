#!/usr/bin/python

"""Test of radio menu items in Java's SwingSet2.
"""

from macaroon.playback.keypress_mimic import *

sequence = MacroSequence()

##########################################################################
# We wait for the demo to come up and for focus to be on the toggle button
#
#sequence.append(WaitForWindowActivate("SwingSet2",None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_TOGGLE_BUTTON))

sequence.append(PauseAction(5000))

##########################################################################
# Invoke Themes menu
sequence.append(KeyComboAction("<Alt>t"))
sequence.append(WaitForFocus("Audio", acc_role=pyatspi.ROLE_MENU))
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Fonts", acc_role=pyatspi.ROLE_MENU))
sequence.append(KeyComboAction("Down"))

##########################################################################
# Expected output when radio menu item gets focused.
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane PopupMenu &=y Ocean RadioItem'
#      VISIBLE:  '&=y Ocean RadioItem', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Ocean selected radio menu item'
sequence.append(WaitForFocus("Ocean", acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
# 
# SPEECH OUTPUT: ' popup menu'
# SPEECH OUTPUT: 'Ocean'
# SPEECH OUTPUT: 'radio menu item'
# SPEECH OUTPUT: 'selected'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'item 3 of 9'
# SPEECH OUTPUT: ''
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

sequence.append(KeyComboAction("Down"))

##########################################################################
# Expected output when radio menu item gets focused.
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane PopupMenu & y Steel RadioItem'
#      VISIBLE:  '& y Steel RadioItem', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Steel not selected radio menu item'
sequence.append(WaitForFocus("Steel", acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
# 
# SPEECH OUTPUT: ' popup menu'
# SPEECH OUTPUT: 'Steel'
# SPEECH OUTPUT: 'radio menu item'
# SPEECH OUTPUT: 'not selected'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'item 4 of 9'
# SPEECH OUTPUT: ''
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

sequence.append(KeyComboAction("Down"))

##########################################################################
# Expected output when radio menu item gets focused.
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane PopupMenu & y Aqua RadioItem'
#      VISIBLE:  '& y Aqua RadioItem', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Aqua not selected radio menu item'
sequence.append(WaitForFocus("Aqua", acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))
sequence.append(KeyComboAction("Down"))

##########################################################################
# Expected output when radio menu item gets focused.
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane PopupMenu & y Charcoal RadioItem'
#      VISIBLE:  '& y Charcoal RadioItem', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Charcoal not selected radio menu item'
sequence.append(WaitForFocus("Charcoal", acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))
sequence.append(KeyComboAction("Down"))

##########################################################################
# Expected output when radio menu item gets focused.
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane PopupMenu & y High Contrast RadioItem'
#      VISIBLE:  '& y High Contrast RadioItem', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'High Contrast not selected radio menu item'
sequence.append(WaitForFocus("High Contrast", acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))
sequence.append(KeyComboAction("Down"))

##########################################################################
# Expected output when radio menu item gets focused.
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane PopupMenu & y Emerald RadioItem'
#      VISIBLE:  '& y Emerald RadioItem', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Emerald not selected radio menu item'
sequence.append(WaitForFocus("Emerald", acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))
sequence.append(KeyComboAction("Down"))

##########################################################################
# Expected output when radio menu item gets focused.
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane PopupMenu & y Ruby RadioItem'
#      VISIBLE:  '& y Ruby RadioItem', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Ruby not selected radio menu item'
sequence.append(WaitForFocus("Ruby", acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))
sequence.append(KeyComboAction("Up"))

##########################################################################
# Expected output when radio menu item gets focused.
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane PopupMenu & y Emerald RadioItem'
#      VISIBLE:  '& y Emerald RadioItem', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Emerald not selected radio menu item'
sequence.append(WaitForFocus("Emerald", acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))
sequence.append(KeyComboAction("Up"))

##########################################################################
# Expected output when radio menu item gets focused.
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane PopupMenu & y High Contrast RadioItem'
#      VISIBLE:  '& y High Contrast RadioItem', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'High Contrast not selected radio menu item'
sequence.append(WaitForFocus("High Contrast", acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))
sequence.append(KeyComboAction("Up"))

##########################################################################
# Expected output when radio menu item gets focused.
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane PopupMenu & y Charcoal RadioItem'
#      VISIBLE:  '& y Charcoal RadioItem', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Charcoal not selected radio menu item'
sequence.append(WaitForFocus("Charcoal", acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))
sequence.append(KeyComboAction("Up"))

##########################################################################
# Expected output when radio menu item gets focused.
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane PopupMenu & y Aqua RadioItem'
#      VISIBLE:  '& y Aqua RadioItem', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Aqua not selected radio menu item'
sequence.append(WaitForFocus("Aqua", acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))
sequence.append(KeyComboAction("Up"))

##########################################################################
# Expected output when radio menu item gets focused.
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane PopupMenu & y Steel RadioItem'
#      VISIBLE:  '& y Steel RadioItem', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Steel not selected radio menu item'
sequence.append(WaitForFocus("Steel", acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))
sequence.append(TypeAction(" "))

##########################################################################
# Expected output when radio menu item is selected.
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane PopupMenu &=y Steel RadioItem'
#      VISIBLE:  '&=y Steel RadioItem', cursor=1
# 
# SPEECH OUTPUT: 'Steel selected radio menu item'
sequence.append(WaitAction("object:property-change:accessible-value", None,
                           None, pyatspi.ROLE_RADIO_MENU_ITEM, 5000))

sequence.append(KeyComboAction("<Alt>t"))

sequence.append(WaitForFocus("Audio", acc_role=pyatspi.ROLE_MENU))
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Fonts", acc_role=pyatspi.ROLE_MENU))
sequence.append(KeyComboAction("Down"))

##########################################################################
# Expected output when radio menu item gets focused.
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane PopupMenu & y Ocean RadioItem'
#      VISIBLE:  '& y Ocean RadioItem', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Ocean not selected radio menu item'
sequence.append(WaitForFocus("Ocean", acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))
sequence.append(KeyComboAction("Down"))

##########################################################################
# Expected output when radio menu item gets focused.
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane PopupMenu &=y Steel RadioItem'
#      VISIBLE:  '&=y Steel RadioItem', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Steel selected radio menu item'
sequence.append(WaitForFocus("Steel", acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))
sequence.append(KeyComboAction("Down"))

##########################################################################
# Expected output when radio menu item gets focused.
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane PopupMenu & y Aqua RadioItem'
#      VISIBLE:  '& y Aqua RadioItem', cursor=1
# 
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Aqua not selected radio menu item'
sequence.append(WaitForFocus("Aqua", acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))
sequence.append(KeyComboAction("Up"))

##########################################################################
# Expected output when radio menu item gets focused.
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane PopupMenu &=y Steel RadioItem'
#      VISIBLE:  '&=y Steel RadioItem', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Steel selected radio menu item'
sequence.append(WaitForFocus("Steel", acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))
sequence.append(KeyComboAction("Up"))

##########################################################################
# Expected output when radio menu item gets focused.
# BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane PopupMenu & y Ocean RadioItem'
#      VISIBLE:  '& y Ocean RadioItem', cursor=1
# 
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Ocean not selected radio menu item'
sequence.append(WaitForFocus("Ocean", acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))
sequence.append(TypeAction           (" "))
sequence.append(WaitAction("object:property-change:accessible-value", None,
                           None, pyatspi.ROLE_RADIO_MENU_ITEM, 5000))

sequence.append(PauseAction(5000))

sequence.start()
