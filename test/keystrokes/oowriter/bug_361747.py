#!/usr/bin/python

"""Test to verify bug #361747 is still fixed.
   Orca should use weight to determine if text is bolded in OO writer and calc.
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
# 3. Enter the following (without the quotation marks) to create a line 
#    with three words on it; one bold, one italic and one in a regular font:
#  Control-b "bold" Control-b Space Control-i "italic" Control-i Space "normal"
#
sequence.append(KeyComboAction("<Control>b"))
sequence.append(TypeAction("bold"))
sequence.append(KeyComboAction("<Control>b"))
sequence.append(TypeAction(" "))
sequence.append(KeyComboAction("<Control>i"))
sequence.append(TypeAction("italic"))
sequence.append(KeyComboAction("<Control>i"))
sequence.append(TypeAction(" normal"))

######################################################################
# 4. Enter Control-Home to position the text caret to the left of
#    the first character in the line.
#
# BRAILLE LINE:  'soffice Application Untitled2 - OpenOffice.org Writer Frame Untitled2 - OpenOffice.org Writer RootPane ScrollPane Document view bold italic normal $l'
# VISIBLE:  'bold italic normal $l'
# SPEECH OUTPUT: 'bold italic normal'
#
sequence.append(KeyComboAction("<Control>Home"))

######################################################################
# 5. Type Insert-f to get the text information for the bold word.
#
# BRAILLE LINE:  'soffice Application Untitled2 - OpenOffice.org Writer Frame Untitled2 - OpenOffice.org Writer RootPane ScrollPane Document view bold italic normal $l'
# VISIBLE:  'bold italic normal $l' cursor=1
# SPEECH OUTPUT: 'size 12'
# SPEECH OUTPUT: 'family-name Times'
# SPEECH OUTPUT: 'bold'
#
sequence.append(KeyPressAction (0, 106,"Insert"))      # Press Insert
sequence.append(TypeAction ("f"))
sequence.append(KeyReleaseAction(150, 106,"Insert"))   # Release Insert

######################################################################
# 6. Type Control-right and Insert-f to get the text information
#    for the italic word.
#
# BRAILLE LINE:  'soffice Application Untitled2 - OpenOffice.org Writer Frame Untitled2 - OpenOffice.org Writer RootPane ScrollPane Document view bold italic normal $l'
# VISIBLE:  'bold italic normal $l', cursor=7
# SPEECH OUTPUT: 'size 12'
# SPEECH OUTPUT: 'family-name Times'
# SPEECH OUTPUT: 'style italic'
#
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(KeyPressAction (0, 106,"Insert"))      # Press Insert
sequence.append(TypeAction ("f"))
sequence.append(KeyReleaseAction(150, 106,"Insert"))   # Release Insert

######################################################################
# 7. Type Control-right and Insert-f to get the text information
#    for the regular word.
#
# BRAILLE LINE:  'soffice Application Untitled2 - OpenOffice.org Writer Frame Untitled2 - OpenOffice.org Writer RootPane ScrollPane Document view bold italic normal $l'
# VISIBLE:  'bold italic normal $l', cursor=13
# SPEECH OUTPUT: 'size 12'
# SPEECH OUTPUT: 'family-name Times'
#
sequence.append(KeyComboAction("<Control>Right"))
sequence.append(KeyPressAction (0, 106,"Insert"))      # Press Insert
sequence.append(TypeAction ("f"))
sequence.append(KeyReleaseAction(150, 106,"Insert"))   # Release Insert

######################################################################
# 8. Enter Alt-f, Alt-c to close the Writer application.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("<Alt>c"))

# We'll get a new window, but we'll wait for the "Save" button to get focus.
#
sequence.append(WaitForFocus("Save", acc_role=pyatspi.ROLE_PUSH_BUTTON))

######################################################################
# 9. Enter Tab and Return to discard the current changes.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Discard", acc_role=pyatspi.ROLE_PUSH_BUTTON))

sequence.append(KeyComboAction("Return"))

######################################################################
# 10. Wait for things to get back to normal.
#
sequence.append(WaitForWindowActivate("Untitled1 - OpenOffice.org Writer", None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(PauseAction(3000))

sequence.start()
