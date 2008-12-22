#!/usr/bin/python

"""Test of document tabs
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the frame.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the htmlpage.html test page.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction(utils.htmlURLPrefix + "htmlpage.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("HTML test page",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Open a new tab, and load orca wiki.
#
sequence.append(KeyComboAction("<Control>t"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction(utils.htmlURLPrefix + "orca-wiki.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Orca - GNOME Live!",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Open a new tab, and load bugzilla start page.
#
sequence.append(KeyComboAction("<Control>t"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction(utils.htmlURLPrefix + "bugzilla_top.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("GNOME Bug Tracking System",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Switch to tab one
#
sequence.append(PauseAction(1000))
sequence.append(KeyComboAction("<Alt>1"))
sequence.append(WaitForFocus("HTML test page",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Switch to tab two
#
sequence.append(PauseAction(1000))
sequence.append(KeyComboAction("<Alt>2"))
sequence.append(WaitForFocus("Orca - GNOME Live!",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Switch to tab three
#
sequence.append(PauseAction(1000))
sequence.append(KeyComboAction("<Alt>3"))
sequence.append(WaitForFocus("GNOME Bug Tracking System",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Delete tab three.
#
sequence.append(PauseAction(1000))
sequence.append(KeyComboAction("<Ctrl>w"))
sequence.append(WaitForFocus("Orca - GNOME Live!",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Load first tabs url in second tab, have them both identical.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction(utils.htmlURLPrefix + "htmlpage.html"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("HTML test page",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Switch to tab one
#
sequence.append(PauseAction(1000))
sequence.append(KeyComboAction("<Alt>1"))
sequence.append(WaitForFocus("HTML test page",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Switch to tab two
#
sequence.append(PauseAction(1000))
sequence.append(KeyComboAction("<Alt>2"))
sequence.append(WaitForFocus("HTML test page",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Delete tab two.
#
sequence.append(PauseAction(1000))
sequence.append(KeyComboAction("<Ctrl>w"))
sequence.append(WaitForFocus("HTML test page",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Close the demo
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
