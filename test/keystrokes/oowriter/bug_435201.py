#!/usr/bin/python

"""Test to verify bug #435201 is still fixed.
   Orca is too chatty when navigating by paragraph in OOo Writer.
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
# 3. Enter the following lines. <Return> means pressing the Return key:
#
# NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and surprise. And ruthless efficiency. Our three weapons are fear, surprise, and ruthless efficiency. And an almost fanatical devotion to the Pope. Our four. No. Amongst our weapons. Amongst our weaponry, are such elements as fear, surprise. I'll come in again.<Return>
# NOBODY expects the Spanish Inquisition! Amongst our weaponry are such diverse elements as: fear, surprise, ruthless efficiency, an almost fanatical devotion to the Pope, and nice red uniforms - Oh damn!<Return>
# <Return>
# Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the ungodly. Two last chances. And you shall be free. Three last chances. You have three last chances, the nature of which I have divulged in my previous utterance.<Return>
# <Return>
# Hm! She is made of harder stuff! Cardinal Fang! Fetch the COMFY CHAIR!<Return>
#
sequence.append(TypeAction("NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. Our two weapons are fear and surprise. And ruthless efficiency. Our three weapons are fear, surprise, and ruthless efficiency. And an almost fanatical devotion to the Pope. Our four. No. Amongst our weapons. Amongst our weaponry, are such elements as fear, surprise. I'll come in again."))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

sequence.append(TypeAction("NOBODY expects the Spanish Inquisition! Amongst our weaponry are such diverse elements as: fear, surprise, ruthless efficiency, an almost fanatical devotion to the Pope, and nice red uniforms - Oh damn!"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

sequence.append(KeyComboAction("Return"))

sequence.append(TypeAction("Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the ungodly. Two last chances. And you shall be free. Three last chances. You have three last chances, the nature of which I have divulged in my previous utterance."))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

sequence.append(KeyComboAction("Return"))

sequence.append(TypeAction("Hm! She is made of harder stuff! Cardinal Fang! Fetch the COMFY CHAIR!"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 4. Type Control-Home to position the text caret to the left of the
#    first character on the first line.
#
# BRAILLE LINE:  'soffice Application spanish - OpenOffice.org Writer Frame spanish - OpenOffice.org Writer RootPane ScrollPane Document view NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and  $l'
# VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=1
# SPEECH OUTPUT: 'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and '
#
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 5. Type Control-down to move to the next paragraph.
#
# BRAILLE LINE:  'soffice Application spanish - OpenOffice.org Writer Frame spanish - OpenOffice.org Writer RootPane ScrollPane Document view NOBODY expects the Spanish Inquisition! Amongst our weaponry are such diverse  $l'
# VISIBLE:  ' NOBODY expects the Spanish Inqui', cursor=1
# SPEECH OUTPUT: 'NOBODY expects the Spanish Inquisition! Amongst our weaponry are such diverse '
#
sequence.append(KeyComboAction("<Control>Down"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 6. Type Control-down to move to the next paragraph.
#
# BRAILLE LINE:  'soffice Application spanish - OpenOffice.org Writer Frame spanish - OpenOffice.org Writer RootPane ScrollPane Document view NOBODY expects the Spanish Inquisition! Amongst our weaponry are such diverse  $l'
# VISIBLE:  ' NOBODY expects the Spanish Inqu', cursor=1
# SPEECH OUTPUT: 'blank'
#
sequence.append(KeyComboAction("<Control>Down"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 7. Type Control-down to move to the next paragraph.
#
# BRAILLE LINE:  'soffice Application spanish - OpenOffice.org Writer Frame spanish - OpenOffice.org Writer RootPane ScrollPane Document view Now old lady, you have one last chance. Confess the heinous sin of heresy, reject  $l'
# VISIBLE:  'Now old lady, you have one last ', cursor=1
# SPEECH OUTPUT: 'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject '
#
sequence.append(KeyComboAction("<Control>Down"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 8. Type Control-down to move to the next paragraph.
#
# BRAILLE LINE:  'soffice Application spanish - OpenOffice.org Writer Frame spanish - OpenOffice.org Writer RootPane ScrollPane Document view Now old lady, you have one last chance. Confess the heinous sin of heresy, reject  $l'
# VISIBLE:  ' Now old lady, you have one last', cursor=1
# SPEECH OUTPUT: 'blank'
#
sequence.append(KeyComboAction("<Control>Down"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 9. Type Control-down to move to the next paragraph.
#
# BRAILLE LINE:  'soffice Application spanish - OpenOffice.org Writer Frame spanish - OpenOffice.org Writer RootPane ScrollPane Document view Hm! She is made of harder stuff! Cardinal Fang! Fetch the COMFY CHAIR! $l'
# VISIBLE:  'Hm! She is made of harder stuff!', cursor=1
# SPEECH OUTPUT: 'Hm! She is made of harder stuff! Cardinal Fang! Fetch the COMFY CHAIR!'
#
sequence.append(KeyComboAction("<Control>Down"))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))

######################################################################
# 10. Enter Alt-f, Alt-c to close the Writer application.
#
sequence.append(KeyComboAction("<Alt>f"))
sequence.append(WaitForFocus("New", acc_role=pyatspi.ROLE_MENU))

sequence.append(KeyComboAction("<Alt>c"))
sequence.append(WaitForFocus("Save", acc_role=pyatspi.ROLE_PUSH_BUTTON))

######################################################################
# 11. Enter Tab and Return to discard the current changes.
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("Discard", acc_role=pyatspi.ROLE_PUSH_BUTTON))
sequence.append(KeyComboAction("Return"))

######################################################################
# 12. Wait for things to get back to normal.
#
sequence.append(WaitForWindowActivate("Untitled1 - OpenOffice.org Writer", None))
sequence.append(WaitForFocus("", acc_role=pyatspi.ROLE_PARAGRAPH))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_INVALID, timeout=3000))

sequence.start()
