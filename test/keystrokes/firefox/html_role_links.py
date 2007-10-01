#!/usr/bin/python

"""Test of HTML links output of Firefox, including basic navigation and
where am I.
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

sequence.append(TypeAction(utils.htmlURLPrefix + "anchors2.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("Links to test files",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Tab to move to the anchors.html link.  Note that for the braille
# I have replaced the bullet character with an asterisk as the bullets
# are causing "Non-ASCII character" syntax errors.
#
# BRAILLE LINE:  '*  anchors.html Link'
#      VISIBLE:  '*  anchors.html Link', cursor=4
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'anchors.html link'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("anchors.html", acc_role=pyatspi.ROLE_LINK))

########################################################################
# Press Tab to move to the blockquotes.html link.
#
# BRAILLE LINE:  '*  blockquotes.html Link'
#      VISIBLE:  '*  blockquotes.html Link', cursor=4
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'blockquotes.html link'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("blockquotes.html", acc_role=pyatspi.ROLE_LINK))

########################################################################
# Press Tab to move to the bugzilla_top.html link.
#
# BRAILLE LINE:  '*  bugzilla_top.html Link'
#      VISIBLE:  '*  bugzilla_top.html Link', cursor=4
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'bugzilla_top.html link'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus("bugzilla_top.html", acc_role=pyatspi.ROLE_LINK))

########################################################################
# Press Shift+Tab to move to the blockquotes.html link.
#
# BRAILLE LINE:  '*  blockquotes.html Link'
#      VISIBLE:  '*  blockquotes.html Link', cursor=4
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'blockquotes.html link'
#
sequence.append(KeyComboAction("<Shift>Tab"))
sequence.append(WaitForFocus("blockquotes.html", acc_role=pyatspi.ROLE_LINK))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  Because we're on a link, we
# get special link-related information.
#
# BRAILLE LINE:  '*  blockquotes.html Link'
#      VISIBLE:  '*  blockquotes.html Link', cursor=4
# SPEECH OUTPUT: 'file link to blockquotes.html'
# SPEECH OUTPUT: 'same site'
# SPEECH OUTPUT: '1188 bytes'
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Press Return to follow the blockquotes.html link.
#
# BRAILLE LINE:  'Loading.  Please wait.'
#      VISIBLE:  'Loading.  Please wait.', cursor=0
# SPEECH OUTPUT: 'Loading.  Please wait.'
# BRAILLE LINE:  'On weaponry:'
#      VISIBLE:  'On weaponry:', cursor=1
# SPEECH OUTPUT: 'Blockquote Regression Test html content'
# SPEECH OUTPUT: 'On weaponry:'
#
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForFocus("Blockquote Regression Test",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))
sequence.append(PauseAction(3000))

########################################################################
# Press Alt+Left Arrow to return to the anchors2.html page.
#
# BRAILLE LINE:  'Loading.  Please wait.'
#      VISIBLE:  'Loading.  Please wait.', cursor=0
# SPEECH OUTPUT: 'Loading.  Please wait.'
# BRAILLE LINE:  '*  blockquotes.html Link'
#      VISIBLE:  '*  blockquotes.html Link', cursor=4
# SPEECH OUTPUT: 'Links to test files html content'
# SPEECH OUTPUT: 'blockquotes.html link'
#
sequence.append(KeyComboAction("<Alt>Left"))
sequence.append(WaitForDocLoad())

########################################################################
# Do a basic "Where Am I" via KP_Enter.  It seems we're back at the
# top of the document. [[[TODO: Figure out if this is Firefox's doing
# or Orca's.  I'd guess it's Orcas.... It would be much nicer to just
# keep on going from where we left off....]]]
#
# BRAILLE LINE:  'Here are some of our local test files:'
#      VISIBLE:  'Here are some of our local test ', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'paragraph'
# SPEECH OUTPUT: 'Here are some of our local test files:'
# SPEECH OUTPUT: ''
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Press Down Arrow to move to the anchors.html link.  We probably
# won't get a focus event, so we'll just pause in the next step.
#
# BRAILLE LINE:  '*  anchors.html Link'
#      VISIBLE:  '*  anchors.html Link', cursor=1
# SPEECH OUTPUT: '*  anchors.html link'
#
sequence.append(KeyComboAction("Down"))

########################################################################
# Press Down Arrow to move to the blockquotes.html link.  We probably
# won't get a focus event, so we'll just pause in the next step.
#
# BRAILLE LINE:  '*  blockquotes.html Link'
#      VISIBLE:  '*  blockquotes.html Link', cursor=1
# SPEECH OUTPUT: '*  blockquotes.html link'
#
sequence.append(KeyComboAction("Down", 1000))

########################################################################
# Press Up Arrow to move to the anchors.html link.  We probably won't
# get a focus event, so we'll just pause in the next step.
#
# BRAILLE LINE:  '*  anchors.html Link'
#      VISIBLE:  '*  anchors.html Link', cursor=1
# SPEECH OUTPUT: '*  anchors.html link'
#
sequence.append(KeyComboAction("Up", 1000))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "about:blank" and press Return to restore the browser to the
# conditions at the test's start.
#
sequence.append(KeyComboAction("<Control>l", 1000))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
