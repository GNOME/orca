#!/usr/bin/python

"""Test of alert output of Firefox.
"""

from macaroon.playback import *

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "javascript:alert('I am an alert') and press Return.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction("javascript:alert('I am an alert')"))
sequence.append(KeyComboAction("Return"))

########################################################################
# An alert will appear displaying the text "I am an alert" and the
# "OK" push button.  [[[Bug? It seems we're only displaying the title
# of the alert in braille; the contents are being spoken.  Is this
# the desired behavior??]]]
#
# BRAILLE LINE:  'Minefield Application [JavaScript Application] Alert'
#      VISIBLE:  '[JavaScript Application] Alert', cursor=1
# SPEECH OUTPUT: '[JavaScript Application] I am an alert'
#
sequence.append(WaitForWindowActivate("[JavaScript Application]",None))

########################################################################
# Focus will be on the OK button. [[[Bug: We don't get a focus event 
# for it.  This seems to be true for all Firefox dialogs and is a
# known issue.]]]  Press space bar on the OK button to dismiss the
# alert and return to the Firefox main window.
#
sequence.append(TypeAction(" "))
sequence.append(WaitForWindowActivate("Minefield",None))

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
