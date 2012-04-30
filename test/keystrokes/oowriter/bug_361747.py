#!/usr/bin/python

"""Test to verify bug #361747 is still fixed.
   Orca should use weight to determine if text is bolded in OO writer and calc.
"""

from macaroon.playback import *

sequence = MacroSequence()
import utils

######################################################################
# 1. Start oowriter. There is a bug_361747.params file that will
#    automatically load empty_document.odt. This uses the FreeSerif 
#    font as the default which should be available on all test systems.
#
sequence.append(WaitForWindowActivate("empty_document(.odt|) - " + utils.getOOoName("Writer"), None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 2. Type Control-Home to move the text caret to the start of the document.
#
sequence.append(KeyComboAction("<Control>Home"))

######################################################################
# 3. Enter the following (without the quotation marks) to create a line 
#    with three words on it; one bold, one italic and one in a regular font:
#    Control-b "Bold" Control-b Space Control-i "Italic" Control-i " Normal"
#
sequence.append(KeyComboAction("<Control>b"))
sequence.append(TypeAction("Bold"))
sequence.append(KeyComboAction("<Control>b"))
sequence.append(TypeAction(" "))
sequence.append(KeyComboAction("<Control>i"))
sequence.append(TypeAction("Italic"))
sequence.append(KeyComboAction("<Control>i"))
sequence.append(TypeAction(" Normal"))

######################################################################
# 5. Enter Control-Home to position the text caret to the left of
#    the first character in the line.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Control-Home to move to start of document",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "empty_document(.odt|)", "Bold Italic Normal \$l") + "'",
     "     VISIBLE:  'Bold Italic Normal $l', cursor=1",
     "SPEECH OUTPUT: 'Bold Italic Normal'"]))

######################################################################
# 6. Type Insert-f to get the text information for the bold word.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(TypeAction ("f"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Text information for bold word",
    ["SPEECH OUTPUT: 'size 12'",
     "SPEECH OUTPUT: 'family name FreeSerif'",
     "SPEECH OUTPUT: 'bold'",
     "SPEECH OUTPUT: 'paragraph style Default'"]))

######################################################################
# 7. Type Control-right and Insert-f to get the text information
#    for the italic word.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(TypeAction ("f"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Text information for italic word",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "empty_document(.odt|)", "Bold Italic Normal \$l") + "'",
     "     VISIBLE:  'Bold Italic Normal $l', cursor=6",
     "SPEECH OUTPUT: 'Italic '",
     "SPEECH OUTPUT: 'size 12'",
     "SPEECH OUTPUT: 'family name FreeSerif'",
     "SPEECH OUTPUT: 'style italic'",
     "SPEECH OUTPUT: 'paragraph style Default'"]))

######################################################################
# 8. Type Control-right and Insert-f to get the text information
#    for the regular word.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(TypeAction ("f"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))
sequence.append(utils.AssertPresentationAction(
    "Text information for regular word",
    ["BRAILLE LINE:  '" + utils.getOOoBrailleLine("Writer", "empty_document(.odt|)", "Bold Italic Normal \$l") + "'",
     "     VISIBLE:  'Bold Italic Normal $l', cursor=13",
     "SPEECH OUTPUT: 'Normal'",
     "SPEECH OUTPUT: 'size 12'",
     "SPEECH OUTPUT: 'family name FreeSerif'",
     "SPEECH OUTPUT: 'paragraph style Default'"]))

######################################################################
# 9. Enter Alt-f, Alt-c to close the Writer application.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("<Alt>c"))

# We'll get a new window, but we'll wait for the "Save" button to get focus.
#
sequence.append(WaitForFocus("Save", acc_role=pyatspi.ROLE_PUSH_BUTTON))

######################################################################
# 10. Enter Tab and Return to discard the current changes.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Discard", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Return"))

sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))
sequence.append(KeyComboAction("<Alt>c"))

######################################################################
# 11. Wait for things to get back to normal.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
