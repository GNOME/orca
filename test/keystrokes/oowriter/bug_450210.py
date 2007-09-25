#!/usr/bin/python

"""Test to verify bug #450210 is still fixed.
   StarOffice.py needs null-check for self.getFrame(event.source).
"""

from macaroon.playback import *

sequence = MacroSequence()

######################################################################
# 1. Start oowriter.
#
sequence.append(WaitForWindowActivate("Untitled1 - OpenOffice.org Writer",None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 2. Enter Alt-f, to display the File menu.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

######################################################################
# 3. Press "o" to open the Open File Chooser.
#
# BRAILLE LINE:  'soffice Application Open Dialog ScrollPane Files Table'
# VISIBLE:  'Files Table', cursor=1 
# SPEECH OUTPUT: 'Open Version:'
# SPEECH OUTPUT: 'Location: text '
# SPEECH OUTPUT: 'Files table'
#
sequence.append(TypeAction("o"))
sequence.append(WaitAction("focus:",
                           None,
                           None,
                           pyatspi.ROLE_TABLE,
                           30000))

######################################################################
# 4. Press Escape to dismiss the Open File Chooser.
#
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 5. Wait for things to get back to normal.
#
sequence.append(PauseAction(3000))

sequence.start()
