#!/usr/bin/python

"""Test of radio menu items in Java's SwingSet2."""

from macaroon.playback import *
import utils

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
sequence.append(PauseAction(5000))

##########################################################################
# Expected output when radio menu item gets focused.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Ocean", acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "1. Down Arrow to Ocean",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swing demo menu bar MenuBar Fonts Menu'",
     "     VISIBLE:  'Fonts Menu', cursor=1",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swing demo menu bar MenuBar &=y Ocean RadioItem'",
     "     VISIBLE:  '&=y Ocean RadioItem', cursor=1",
     "SPEECH OUTPUT: 'Ocean selected radio menu item'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "2. Basic Where Am I",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swing demo menu bar MenuBar &=y Ocean RadioItem'",
     "     VISIBLE:  '&=y Ocean RadioItem', cursor=1",
     "SPEECH OUTPUT: 'SwingSet2 application SwingSet2 frame Swing demo menu bar menu bar Themes menu Ocean radio menu item selected 3 of 9.'",
     "SPEECH OUTPUT: 'O'",
     "SPEECH OUTPUT: 'The Ocean Metal Theme'"]))

##########################################################################
# Expected output when radio menu item gets focused.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Steel", acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "3. Down Arrow to Steel",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swing demo menu bar MenuBar & y Steel RadioItem'",
     "     VISIBLE:  '& y Steel RadioItem', cursor=1",
     "SPEECH OUTPUT: 'Steel not selected radio menu item'"]))

########################################################################
# Do a basic "Where Am I" via KP_Enter.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))
sequence.append(utils.AssertPresentationAction(
    "4. Basic Where Am I",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swing demo menu bar MenuBar & y Steel RadioItem'",
     "     VISIBLE:  '& y Steel RadioItem', cursor=1",
     "SPEECH OUTPUT: 'SwingSet2 application SwingSet2 frame Swing demo menu bar menu bar Themes menu Steel radio menu item not selected 4 of 9.'",
     "SPEECH OUTPUT: 'S'",
     "SPEECH OUTPUT: 'The blue/purple Metal Theme'"]))

##########################################################################
# Expected output when radio menu item gets focused.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Aqua", acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "5. Down Arrow to Aqua",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swing demo menu bar MenuBar & y Aqua RadioItem'",
     "     VISIBLE:  '& y Aqua RadioItem', cursor=1",
     "SPEECH OUTPUT: 'Aqua not selected radio menu item'"]))

#########################################################################
# Expected output when radio menu item gets focused.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Charcoal", acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "6. Down Arrow to Charcoal",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swing demo menu bar MenuBar & y Charcoal RadioItem'",
     "     VISIBLE:  '& y Charcoal RadioItem', cursor=1",
     "SPEECH OUTPUT: 'Charcoal not selected radio menu item'"]))

##########################################################################
# Expected output when radio menu item gets focused.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("High Contrast", acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "7. Down Arrow to High Contrast",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swing demo menu bar MenuBar & y High Contrast RadioItem'",
     "     VISIBLE:  '& y High Contrast RadioItem', cursor=1",
     "SPEECH OUTPUT: 'High Contrast not selected radio menu item'"]))

##########################################################################
# Expected output when radio menu item gets focused.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Emerald", acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "8. Down Arrow to Emerald",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swing demo menu bar MenuBar & y Emerald RadioItem'",
     "     VISIBLE:  '& y Emerald RadioItem', cursor=1",
     "SPEECH OUTPUT: 'Emerald not selected radio menu item'"]))

##########################################################################
# Expected output when radio menu item gets focused.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Ruby", acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "9. Down Arrow to Ruby",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swing demo menu bar MenuBar & y Ruby RadioItem'",
     "     VISIBLE:  '& y Ruby RadioItem', cursor=1",
     "SPEECH OUTPUT: 'Ruby not selected radio menu item'"]))

##########################################################################
# Expected output when radio menu item gets focused.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitForFocus("Emerald", acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "10. Up Arrow to Emerald",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swing demo menu bar MenuBar & y Emerald RadioItem'",
     "     VISIBLE:  '& y Emerald RadioItem', cursor=1",
     "SPEECH OUTPUT: 'Emerald not selected radio menu item'"]))

##########################################################################
# Expected output when radio menu item gets focused.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitForFocus("High Contrast", acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "11. Up Arrow to High Contrast",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swing demo menu bar MenuBar & y High Contrast RadioItem'",
     "     VISIBLE:  '& y High Contrast RadioItem', cursor=1",
     "SPEECH OUTPUT: 'High Contrast not selected radio menu item'"]))

##########################################################################
# Expected output when radio menu item gets focused.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitForFocus("Charcoal", acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "12. Up Arrow to Charcoal",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swing demo menu bar MenuBar & y Charcoal RadioItem'",
     "     VISIBLE:  '& y Charcoal RadioItem', cursor=1",
     "SPEECH OUTPUT: 'Charcoal not selected radio menu item'"]))

##########################################################################
# Expected output when radio menu item gets focused.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitForFocus("Aqua", acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "13. Up Arrow to Aqua",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swing demo menu bar MenuBar & y Aqua RadioItem'",
     "     VISIBLE:  '& y Aqua RadioItem', cursor=1",
     "SPEECH OUTPUT: 'Aqua not selected radio menu item'"]))

##########################################################################
# Expected output when radio menu item gets focused.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitForFocus("Steel", acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "14. Up Arrow to Steel",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swing demo menu bar MenuBar & y Steel RadioItem'",
     "     VISIBLE:  '& y Steel RadioItem', cursor=1",
     "SPEECH OUTPUT: 'Steel not selected radio menu item'"]))

##########################################################################
# Expected output when radio menu item is selected.
#
sequence.append(utils.StartRecordingAction())
sequence.append(TypeAction(" "))
sequence.append(WaitAction("object:property-change:accessible-value", None,
                           None, pyatspi.ROLE_RADIO_MENU_ITEM, 5000))
sequence.append(utils.AssertPresentationAction(
    "15. Select the radio menu item",
    ["BUG? - Why are we speaking JInternalFrame demo? Also, some times the state of the toggle button is wrong. Need to investigate.",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swing demo menu bar MenuBar &=y Steel RadioItem'",
     "     VISIBLE:  '&=y Steel RadioItem', cursor=1",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane ToolBar &=y ToggleButton'",
     "     VISIBLE:  '&=y ToggleButton', cursor=1",
     "SPEECH OUTPUT: 'Steel selected radio menu item'",
     "SPEECH OUTPUT: 'JInternalFrame demo toggle button pressed'"]))

sequence.append(KeyComboAction("<Alt>t"))
sequence.append(WaitForFocus("Audio", acc_role=pyatspi.ROLE_MENU))
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Fonts", acc_role=pyatspi.ROLE_MENU))

##########################################################################
# Expected output when radio menu item gets focused.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Ocean", acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "16. Down Arrow to Ocean",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swing demo menu bar MenuBar Fonts Menu'",
     "     VISIBLE:  'Fonts Menu', cursor=1",
     "BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swing demo menu bar MenuBar & y Ocean RadioItem'",
     "     VISIBLE:  '& y Ocean RadioItem', cursor=1",
     "SPEECH OUTPUT: 'Ocean not selected radio menu item'"]))

##########################################################################
# Expected output when radio menu item gets focused.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Steel", acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "17. Down Arrow to Steel",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swing demo menu bar MenuBar &=y Steel RadioItem'",
     "     VISIBLE:  '&=y Steel RadioItem', cursor=1",
     "SPEECH OUTPUT: 'Steel selected radio menu item'"]))

##########################################################################
# Expected output when radio menu item gets focused.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Aqua", acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "18. Down Arrow to Aqua",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swing demo menu bar MenuBar & y Aqua RadioItem'",
     "     VISIBLE:  '& y Aqua RadioItem', cursor=1",
     "SPEECH OUTPUT: 'Aqua not selected radio menu item'"]))

##########################################################################
# Expected output when radio menu item gets focused.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitForFocus("Steel", acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "19. Up Arrow to Steel",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swing demo menu bar MenuBar &=y Steel RadioItem'",
     "     VISIBLE:  '&=y Steel RadioItem', cursor=1",
     "SPEECH OUTPUT: 'Steel selected radio menu item'"]))

##########################################################################
# Expected output when radio menu item gets focused.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(WaitForFocus("Ocean", acc_role=pyatspi.ROLE_RADIO_MENU_ITEM))
sequence.append(utils.AssertPresentationAction(
    "20. Up Arrow to Ocean",
    ["BRAILLE LINE:  'SwingSet2 Application SwingSet2 Frame RootPane LayeredPane Swing demo menu bar MenuBar & y Ocean RadioItem'",
     "     VISIBLE:  '& y Ocean RadioItem', cursor=1",
     "SPEECH OUTPUT: 'Ocean not selected radio menu item'"]))
    
sequence.append(TypeAction(" "))
sequence.append(WaitAction("object:property-change:accessible-value", None,
                           None, pyatspi.ROLE_RADIO_MENU_ITEM, 5000))

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
