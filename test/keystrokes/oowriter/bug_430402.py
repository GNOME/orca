#!/usr/bin/python

"""Test to verify bug #430402 is still fixed.
   Orca unable to speak last character of each "sentence" when doing a 
   sayAll in OOo Writer.
"""

from macaroon.playback import *

sequence = MacroSequence()

######################################################################
# 1. Start oowriter.
#
sequence.append(WaitForWindowActivate("Untitled1 - OpenOffice.org Writer",None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 2. Enter Alt-f, right arrow and Return.  (File->New->Text Document).
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Text Document", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Return"))
sequence.append(WaitForWindowActivate("Untitled2 - OpenOffice.org Writer",None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 3. Enter the following line, each one followed by a Return:
#      The quick
#      brown
#      fox jumps over
#      the lazy dog
#
sequence.append(TypeAction("The quick"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

sequence.append(TypeAction("brown"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

sequence.append(TypeAction("fox jumps over"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

sequence.append(TypeAction("the lazy dog"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 4. Type Control-Home to position the text caret to the left of the 
#    first character.
# BRAILLE LINE:  'soffice Application Untitled2 - OpenOffice.org Writer Frame Untitled2 - OpenOffice.org Writer RootPane ScrollPane Document view The quick $l'
# VISIBLE:  'The quick $l', cursor=1
# SPEECH OUTPUT: 'The quick'
#
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 5. Enter KP+ to perform a "say all" on the document.
#
# BRAILLE LINE:  'soffice Application Untitled2 - OpenOffice.org Writer Frame Untitled2 - OpenOffice.org Writer RootPane ScrollPane Document view the lazy dog $l'
# VISIBLE:  'the lazy dog $l', cursor=13
# SPEECH OUTPUT: 'The quick'
# SPEECH OUTPUT: 'brown'
# SPEECH OUTPUT: 'fox jumps over'
# SPEECH OUTPUT: 'the lazy dog'
#
sequence.append(KeyComboAction("KP_Plus", 3000))

######################################################################
# 6. Enter Alt-f, Alt-c to close the Writer application.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("<Alt>c"))
sequence.append(WaitForFocus("Save", acc_role=pyatspi.ROLE_PUSH_BUTTON))

######################################################################
# 7. Enter Tab and Return to discard the current changes.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Discard", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Return"))

######################################################################
# 8. Wait for things to get back to normal.
#
sequence.append(WaitForWindowActivate("Untitled1 - OpenOffice.org Writer", None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_INVALID, timeout=3000))

sequence.start()
