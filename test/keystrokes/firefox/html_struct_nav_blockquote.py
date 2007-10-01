#!/usr/bin/python

"""Test of HTML blockquote output of Firefox, in particular structural
navigation and where am I.
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

sequence.append(TypeAction(utils.htmlURLPrefix + "blockquotes.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Blockquote Regression Test",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

sequence.append(PauseAction(3000))

########################################################################
# Press Q to move to the first blockquote which begins with: "NOBODY
# expects the Spanish Inquisition!" 
#
# BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. '
#      VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=1
# SPEECH OUTPUT: 'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. '
#
sequence.append(KeyComboAction("q"))
sequence.append(PauseAction(1000))

########################################################################
# Press Q to move to the second blockquote which begins with: "Now
# old lady".
#
# BRAILLE LINE:  'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the ungodly. '
#      VISIBLE:  'Now old lady, you have one last ', cursor=1
# SPEECH OUTPUT: 'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the ungodly. '
#
sequence.append(KeyComboAction("q"))
sequence.append(PauseAction(1000))

########################################################################
# Press Q to move to the third and final blockquote which begins with:
# "Hm! She is made of harder stuff!"
#
# BRAILLE LINE:  'Hm! She is made of harder stuff! Cardinal Fang! Fetch the COMFY CHAIR! '
#      VISIBLE:  'Hm! She is made of harder stuff!', cursor=1
# SPEECH OUTPUT: 'Hm! She is made of harder stuff! Cardinal Fang! Fetch the COMFY CHAIR! '
#
sequence.append(KeyComboAction("q"))
sequence.append(PauseAction(1000))

########################################################################
# Press Q again.  There are no more blockquotes on this page so we
# should wrap to the top (announce that we've done so) and then move
# to the first blockquote.
#
# SPEECH OUTPUT: 'Wrapping to top.'
# BRAILLE LINE:  'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. '
#      VISIBLE:  'NOBODY expects the Spanish Inqui', cursor=1
# SPEECH OUTPUT: 'NOBODY expects the Spanish Inquisition! Our chief weapon is surprise. Surprise and fear. Fear and surprise. '
#
sequence.append(KeyComboAction("q"))
sequence.append(PauseAction(1000))

########################################################################
# Press Shift+Q.  There are no more blockquotes above us on the page
#  so we should wrap to the bottom (announce that we've done so) and 
# then move to the third and final blockquote.
#
# SPEECH OUTPUT: 'Wrapping to bottom.'
# BRAILLE LINE:  'Hm! She is made of harder stuff! Cardinal Fang! Fetch the COMFY CHAIR! '
#      VISIBLE:  'Hm! She is made of harder stuff!', cursor=1
# SPEECH OUTPUT: 'Hm! She is made of harder stuff! Cardinal Fang! Fetch the COMFY CHAIR! '
#
sequence.append(KeyComboAction("<Shift>q"))
sequence.append(PauseAction(1000))

########################################################################
# Press Shift+Q to move to the second blockquote.
#
# BRAILLE LINE:  'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the ungodly. '
#      VISIBLE:  'Now old lady, you have one last ', cursor=1
# SPEECH OUTPUT: 'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the ungodly. '
#
sequence.append(KeyComboAction("<Shift>q"))
sequence.append(PauseAction(1000))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  [[[Mike: This is a paragraph
# inside of a blockquote, so the where am I is accurate.  However,
# I'm wondering if we should be doing anything w.r.t. the blockquote
# role.]]]
#
# BRAILLE LINE:  'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the ungodly. '
#      VISIBLE:  'Now old lady, you have one last ', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'paragraph'
# SPEECH OUTPUT: 'Now old lady, you have one last chance. Confess the heinous sin of heresy, reject the works of the ungodly. '
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

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
