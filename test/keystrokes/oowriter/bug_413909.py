#!/usr/bin/python

"""Test to verify bug #413909 is still fixed.
   Orca can no longer provide "smarts" for spell checking in OOo 
   Writer v2.1 (or later).
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

######################################################################
# 1. Start oowriter.
#
sequence.append(WaitForWindowActivate("Untitled 1 - " + utils.getOOoName("Writer"), None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 2. Enter Alt-f, right arrow and Return.  (File->New->Text Document).
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("Right"))
sequence.append(WaitForFocus("Text Document", acc_role=pyatspi.ROLE_MENU_ITEM))

sequence.append(KeyComboAction("Return"))
sequence.append(WaitForWindowActivate("Untitled 2 - " + utils.getOOoName("Writer"), None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 3. Enter the following line, each one followed by a Return:
#      The quuuiick brown fox 
#      jumps over the lazy dog
#
sequence.append(TypeAction("The quuuiick brown fox"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

sequence.append(TypeAction("jumps over the lazy dog"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 4. Type Control-Home to position the text caret to the left of
#    the first character on the first line.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(utils.AssertPresentationAction(
    "Type Control-Home to move to the start of the document",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "Untitled 2", "The quuuiick brown fox \$l") + "'",
     "     VISIBLE:  'The quuuiick brown fox $l', cursor=1",
     "BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "Untitled 2", "The quuuiick brown fox \$l") + "'",
     "     VISIBLE:  'The quuuiick brown fox $l', cursor=1",
     "SPEECH OUTPUT: 'The quuuiick brown fox'"]))

######################################################################
# 5. Enter F7 to bring up the spell checking dialog.
#
language = "(English \(USA\)|\[None\])"
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("F7"))
sequence.append(WaitForFocus("Change", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(utils.AssertPresentationAction(
    "Enter F7 to bring up the spell checking dialog",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "Untitled 2", "The quuuiick brown fox \$l") + "'",
     "     VISIBLE:  'The quuuiick brown fox $l', cursor=2",
     "BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "Untitled 2", "The quuuiick brown fox \$l") + "'",
     "     VISIBLE:  'The quuuiick brown fox $l', cursor=3",
     "BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "Untitled 2", "The quuuiick brown fox \$l") + "'",
     "     VISIBLE:  'The quuuiick brown fox $l', cursor=4",
     "BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "Untitled 2", "The quuuiick brown fox \$l") + "'",
     "     VISIBLE:  'The quuuiick brown fox $l', cursor=5",
     "BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "Untitled 2", "The quuuiick brown fox \$l") + "'",
     "     VISIBLE:  'The quuuiick brown fox $l', cursor=23",
     "BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "Untitled 2", "The quuuiick brown fox \$l") + "'",
     "     VISIBLE:  'The quuuiick brown fox $l', cursor=14",
     "BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "Untitled 2", "The quuuiick brown fox \$l") + "'",
     "     VISIBLE:  'The quuuiick brown fox $l', cursor=15",
     "BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "Untitled 2", "The quuuiick brown fox \$l") + "'",
     "     VISIBLE:  'The quuuiick brown fox $l', cursor=16",
     "BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "Untitled 2", "The quuuiick brown fox \$l") + "'",
     "     VISIBLE:  'The quuuiick brown fox $l', cursor=17",
     "BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "Untitled 2", "The quuuiick brown fox \$l") + "'",
     "     VISIBLE:  'The quuuiick brown fox $l', cursor=18",
     "BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "Untitled 2", "The quuuiick brown fox \$l") + "'",
     "     VISIBLE:  'The quuuiick brown fox $l', cursor=19",
     "BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "Untitled 2", "The quuuiick brown fox \$l") + "'",
     "     VISIBLE:  'The quuuiick brown fox $l', cursor=20",
     "BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "Untitled 2", "The quuuiick brown fox \$l") + "'",
     "     VISIBLE:  'The quuuiick brown fox $l', cursor=21",
     "BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "Untitled 2", "The quuuiick brown fox \$l") + "'",
     "     VISIBLE:  'The quuuiick brown fox $l', cursor=22",
     "BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "Untitled 2", "The quuuiick brown fox \$l") + "'",
     "     VISIBLE:  'The quuuiick brown fox $l', cursor=23",
     "BRAILLE LINE:  'soffice Application Spelling: " + language + " Dialog'",
     "     VISIBLE:  'Spelling: " + language + " Dialog', cursor=1",
     "BRAILLE LINE:  'soffice Application Spelling: " + language + " Dialog Spelling: " + language + " OptionPane Change Button'",
     "     VISIBLE:  'Change Button', cursor=1",
     "SPEECH OUTPUT: 'Spelling: " + language + "'",
     "SPEECH OUTPUT: 'Misspelled word: quuuiick Context is The quuuiick brown fox'",
     "SPEECH OUTPUT: 'Change button'"]))

######################################################################
# 6. Press Esc to dismiss the spell checking dialog.
#
sequence.append(KeyComboAction("Escape"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 7. Enter Alt-f, Alt-c to close the Writer application.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("<Alt>c"))
sequence.append(WaitForFocus("Save", acc_role=pyatspi.ROLE_PUSH_BUTTON))

######################################################################
# 8. Enter Tab and Return to discard the current changes.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Discard", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Return"))

######################################################################
# 9. Wait for things to get back to normal.
#
sequence.append(WaitForWindowActivate("Untitled 1 - " + utils.getOOoName("Writer"), None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
