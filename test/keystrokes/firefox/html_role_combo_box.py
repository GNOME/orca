#!/usr/bin/python

"""Test of HTML combo box output of Firefox, including label guess and
forcing a combo box that has been reached by caret browsing to expand
and gain focus.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the local combo box test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "combobox.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Combo Box Regression Test",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Tab twice to get to the Severity combo box.  This combo box
# has a proper label (the Severity link that precedes it).
#
#
# BRAILLE LINE:  'Severity Link :  normal Combo'
#      VISIBLE:  'Severity Link :  normal Combo', cursor=18
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Severity normal combo box'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Severity", acc_role=pyatspi.ROLE_LINK))

sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Severity", acc_role=pyatspi.ROLE_COMBO_BOX))

########################################################################
# Press Tab twice to get to the Priority combo box.  This combo box
# lacks a proper label. Label guess should guess "Priority" from the
# link that precedes it.
# BRAILLE LINE:  'Priority Link :  Normal Combo'
#      VISIBLE:  'Priority Link :  Normal Combo', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Priority link'
# BRAILLE LINE:  'Priority Link :  Normal Combo'
#      VISIBLE:  'Priority Link :  Normal Combo', cursor=18
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Priority: Normal combo box'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Priority", acc_role=pyatspi.ROLE_LINK))

sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_COMBO_BOX))

########################################################################
# Press Tab once to get to the Resolution combo box.  This combo box
# lacks a proper label. Label guess should guess "Resolution" from the
# text above it. 
#
# BRAILLE LINE:  'FIXED Combo'
#     VISIBLE:  'FIXED Combo', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Resolution: FIXED combo box'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_COMBO_BOX))

########################################################################
# Press Down Arrow to change the selection to WONTFIX.  Note: The
# output seems to suggest that we repeat the item.  But it doesn't
# sound like that when you actually use it.  I suspect we're getting
# a couple of back-to-back events and the second event is interrupting
# the first.
#
# BRAILLE LINE:  'WONTFIX Combo'
#      VISIBLE:  'WONTFIX Combo', cursor=1
# SPEECH OUTPUT: 'WONTFIX combo box'
# BRAILLE LINE:  'WONTFIX'
#      VISIBLE:  'WONTFIX', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'WONTFIX'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("WONTFIX", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Press Down Arrow to change the selection to NOTABUG
#
# BRAILLE LINE:  'NOTABUG'
# 3    VISIBLE:  'NOTABUG', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'NOTABUG'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("NOTABUG", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Press Up Arrow to change the selection back to WONTFIX.
#
# BRAILLE LINE:  'WONTFIX'
#      VISIBLE:  'WONTFIX', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'WONTFIX'
#
sequence.append(KeyComboAction("Up"))
sequence.append(WaitForFocus("WONTFIX", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Press Up Arrow to change the selection back to FIXED.
#
# BRAILLE LINE:  'FIXED'
#      VISIBLE:  'FIXED', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'FIXED'
# 
sequence.append(KeyComboAction("Up"))
sequence.append(WaitForFocus("FIXED", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Press Alt Down Arrow to expand the combo box.  We won't get a focus
# event, so just pause a bit.
#
# BRAILLE LINE:  'FIXED'
#      VISIBLE:  'FIXED', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'FIXED combo box'
#
sequence.append(KeyComboAction("<Alt>Down"))
sequence.append(PauseAction(1000))

########################################################################
# Press Down Arrow to change the selection back to WONTFIX.
#
# BRAILLE LINE:  'WONTFIX'
#      VISIBLE:  'WONTFIX', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'WONTFIX'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("WONTFIX", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Press Return to collapse the combo box with WONTFIX selected.
#
# BRAILLE LINE:  'WONTFIX Combo'
#      VISIBLE:  'WONTFIX Combo', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Resolution: WONTFIX combo box'
#
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_COMBO_BOX))

########################################################################
# Press Tab once to get to the Version combo box.  This combo box
# lacks a proper label. Label guess should guess "Version" from the
# text in the table cell on the left.
#
# BRAILLE LINE:  'Version 2.16 Combo'
#      VISIBLE:  'Version 2.16 Combo', cursor=9
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Version 2.16 combo box'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_COMBO_BOX))

########################################################################
# Press Left Arrow 5 times to move off of this combo box and onto the
# 'n' at the end of "Version".
#
# BRAILLE LINE:  'Version 2.16 Combo'
#      VISIBLE:  'Version 2.16 Combo', cursor=9
# SPEECH OUTPUT: '6'
# BRAILLE LINE:  'Version 2.16 Combo'
#      VISIBLE:  'Version 2.16 Combo', cursor=9
# SPEECH OUTPUT: '1'
# BRAILLE LINE:  'Version 2.16 Combo'
#      VISIBLE:  'Version 2.16 Combo', cursor=9
# SPEECH OUTPUT: '.'
# BRAILLE LINE:  'Version 2.16 Combo'
#      VISIBLE:  'Version 2.16 Combo', cursor=9
# SPEECH OUTPUT: '2'
# BRAILLE LINE:  'Version 2.16 Combo'
#      VISIBLE:  'Version 2.16 Combo', cursor=7
# SPEECH OUTPUT: 'n'
# 
sequence.append(KeyComboAction("Left"))
sequence.append(KeyComboAction("Left"))
sequence.append(KeyComboAction("Left"))
sequence.append(KeyComboAction("Left"))
sequence.append(KeyComboAction("Left"))

########################################################################
# Press Down Arrow once to move to the next line which contains
# the text "Component" in a table cell.
#
# BRAILLE LINE:  'Component'
#      VISIBLE:  'Component', cursor=1
# SPEECH OUTPUT: 'Component'
#
sequence.append(KeyComboAction("Down"))

########################################################################
# Press Down Arrow again to move to the next line which contains
# a combo box.
#
# BRAILLE LINE:  'Speech Combo'
#      VISIBLE:  'Speech Combo', cursor=1
# SPEECH OUTPUT: 'Speech combo box'
#
sequence.append(KeyComboAction("Down"))

########################################################################
# Press Alt Down Arrow once to grab focus on this technically unfocused
# combo box and force it to expand.
#
# BRAILLE LINE:  'Speech Combo'
#      VISIBLE:  'Speech Combo', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Speech combo box'
#
sequence.append(KeyComboAction("<Alt>Down"))
sequence.append(WaitForFocus("Speech", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Press Down Arrow to change the selection to Braille.
#
# BRAILLE LINE:  'Braille'
#      VISIBLE:  'Braille', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Braille'
#
sequence.append(KeyComboAction("Down"))
sequence.append(WaitForFocus("Braille", acc_role=pyatspi.ROLE_MENU_ITEM))

########################################################################
# Press Return to collapse the combo box with Braille selected.
#
# BRAILLE LINE:  'Braille Combo'
#      VISIBLE:  'Braille Combo', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Component Braille combo box'
#
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_COMBO_BOX))

########################################################################
# Do a basic "Where Am I" via KP_Enter. [[[Bug:  Hmmmm.... Looks like
# we might need to do a bit of where am I work for HTML combo boxes.]]]
#
# BRAILLE LINE:  'Braille Combo'
#      VISIBLE:  'Braille Combo', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'combo box'
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: ''
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Press Shift Tab once to return to the Version combo box.  
#
# BRAILLE LINE:  'Version 2.16 Combo'
#      VISIBLE:  'Version 2.16 Combo', cursor=9
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Version 2.16 combo box'
#
sequence.append(KeyComboAction("<Shift>ISO_Left_Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_COMBO_BOX))

########################################################################
# Press Tab once to return to the Component combo box.  This combo box
# lacks a proper label. Label guess should guess "Component" from the
# text in the table cell above it.  Because the label is not on the
# same as the combo box, it does not appear in braille.
#
# BRAILLE LINE:  'Braille Combo'
#      VISIBLE:  'Braille Combo', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'Component Braille combo box'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_COMBO_BOX))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "about:blank" and press Return to restore the browser to the
# conditions at the test's start.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
