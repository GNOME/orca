#!/usr/bin/python

"""Test of HTML links output of Firefox, in particular structural
navigation.
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
# Press U to move to the next unvisited link, anchors.html. Note that 
# for the braille I have replaced the bullet character with an asterisk
# as the bullets are causing "Non-ASCII character" syntax errors.
#
# BRAILLE LINE:  '*  anchors.html Link'
#      VISIBLE:  '*  anchors.html Link', cursor=4
# SPEECH OUTPUT: 'anchors.html link'
#
sequence.append(KeyComboAction("u"))
sequence.append(WaitForFocus("anchors.html", acc_role=pyatspi.ROLE_LINK))

########################################################################
# Press U to move to the next unvisited link, blockquotes.html
#
# BRAILLE LINE:  '*  blockquotes.html Link'
#      VISIBLE:  '*  blockquotes.html Link', cursor=4
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'blockquotes.html link'
#
sequence.append(KeyComboAction("u"))
sequence.append(WaitForFocus("blockquotes.html", 
                             acc_role=pyatspi.ROLE_LINK))

########################################################################
# Press Shift+U to move to the previous unvisited link.
#
# BRAILLE LINE:  '*  anchors.html Link'
#      VISIBLE:  '*  anchors.html Link', cursor=4
# SPEECH OUTPUT: 'anchors.html link'
#
sequence.append(KeyComboAction("<Shift>u"))
sequence.append(WaitForFocus("anchors.html", acc_role=pyatspi.ROLE_LINK))

########################################################################
# Press Shift+U to move to the previous unvisited link.  Note that there
# are no more previous links between us and the top of the page. 
# Therefore we wrap to the bottom (and announce that fact) and then 
# move to the first link we come to.
#
# SPEECH OUTPUT: 'Wrapping to bottom.'
# BRAILLE LINE:  '*  textattributes.html Link'
#      VISIBLE:  '*  textattributes.html Link', cursor=4
# SPEECH OUTPUT: 'textattributes.html link'
#
sequence.append(KeyComboAction("<Shift>u"))
sequence.append(WaitForFocus("textattributes.html", 
                             acc_role=pyatspi.ROLE_LINK))

########################################################################
# Press Shift+U to move to the previous unvisited link.
#
# BRAILLE LINE:  '*  tables.html Link'
#      VISIBLE:  '*  tables.html Link', cursor=4
# SPEECH OUTPUT: 'tables.html link'
#
sequence.append(KeyComboAction("<Shift>u"))
sequence.append(WaitForFocus("tables.html", acc_role=pyatspi.ROLE_LINK))

########################################################################
# Press Return to follow the tables.html link.
#
# BRAILLE LINE:  'Loading.  Please wait.'
#      VISIBLE:  'Loading.  Please wait.', cursor=0
# SPEECH OUTPUT: 'Loading.  Please wait.'
# BRAILLE LINE:  'Tables h1'
#      VISIBLE:  'Tables h1', cursor=1
# SPEECH OUTPUT: 'Table Test Page html content'
# SPEECH OUTPUT: 'Tables heading'
# SPEECH OUTPUT: 'tree level 1'
#
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(PauseAction(3000))

########################################################################
# Press Alt+Left Arrow to return to the anchors2.html page. [[[TODO:
# work out why we land at the top of the page and see about retaining
# our previous position.]]]
#
# BRAILLE LINE:  'Links to test files'
#      VISIBLE:  'Links to test files', cursor=0
# SPEECH OUTPUT: 'Links to test files page'
# BRAILLE LINE:  'Here are some of our local test files:'
#      VISIBLE:  'Here are some of our local test ', cursor=1
# SPEECH OUTPUT: 'Here are some of our local test files:'
#
sequence.append(KeyComboAction("<Alt>Left"))
sequence.append(WaitForDocLoad())

########################################################################
# Press U to move to the next unvisited link, anchors.html. 
#
# BRAILLE LINE:  '*  anchors.html Link'
#      VISIBLE:  '*  anchors.html Link', cursor=4
# SPEECH OUTPUT: 'anchors.html link'
#
sequence.append(KeyComboAction("u"))
sequence.append(WaitForFocus("anchors.html", acc_role=pyatspi.ROLE_LINK))

########################################################################
# Press U to move to the next unvisited link, blockquotes.html
#
# BRAILLE LINE:  '*  blockquotes.html Link'
#      VISIBLE:  '*  blockquotes.html Link', cursor=4
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: 'blockquotes.html link'
#
sequence.append(KeyComboAction("u"))
sequence.append(WaitForFocus("blockquotes.html", 
                             acc_role=pyatspi.ROLE_LINK))

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
sequence.append(WaitForDocLoad())
sequence.append(PauseAction(3000))

########################################################################
# Press Alt+Left Arrow to return to the anchors2.html page. [[[TODO:
# work out why we land at the top of the page and see about retaining
# our previous position.]]]
#
# BRAILLE LINE:  '*  blockquotes.html Link'
#      VISIBLE:  '*  blockquotes.html Link', cursor=4
# SPEECH OUTPUT: 'Links to test files html content'
# SPEECH OUTPUT: 'blockquotes.html link'
# BRAILLE LINE:  'Finished loading Links to test files.'
#      VISIBLE:  'Finished loading Links to test f', cursor=0
# SPEECH OUTPUT: 'Finished loading Links to test files.'
# BRAILLE LINE:  'Here are some of our local test files:'
#      VISIBLE:  'Here are some of our local test ', cursor=1
# SPEECH OUTPUT: 'Here are some of our local test files:'
#
sequence.append(KeyComboAction("<Alt>Left"))
sequence.append(WaitForDocLoad())
sequence.append(PauseAction(3000))

########################################################################
# Press V to move to the next visited link, blockquotes.html.  I think
# we're failing to get a focus event here.
#
# BRAILLE LINE:  '*  blockquotes.html Link'
#      VISIBLE:  '*  blockquotes.html Link', cursor=4
# SPEECH OUTPUT: 'blockquotes.html link'
#
sequence.append(KeyComboAction("v"))
sequence.append(PauseAction(3000))

########################################################################
# Press V to move to the next visited link, tables.html
#
# BRAILLE LINE:  '*  tables.html Link'
#      VISIBLE:  '*  tables.html Link', cursor=4
# SPEECH OUTPUT: 'tables.html link'
#
sequence.append(KeyComboAction("v"))
sequence.append(WaitForFocus("tables.html", acc_role=pyatspi.ROLE_LINK))

########################################################################
# Press V to move to the next visited link, blockquotes.html [[[Bug:
# it seems we've lost the wrapping announcement for visited links.]]]
#
# BRAILLE LINE:  '*  blockquotes.html Link'
#      VISIBLE:  '*  blockquotes.html Link', cursor=4
# SPEECH OUTPUT: 'blockquotes.html link'
#
sequence.append(KeyComboAction("v"))
sequence.append(WaitForFocus("blockquotes.html",
                             acc_role=pyatspi.ROLE_LINK))

########################################################################
# Press V to move to the next visited link, tables.html. [[[Bug:
# it seems we've lost the wrapping announcement for visited links.]]]
#
# BRAILLE LINE:  '*  tables.html Link'
#      VISIBLE:  '*  tables.html Link', cursor=4
# SPEECH OUTPUT: 'tables.html link'
#
sequence.append(KeyComboAction("<Shift>v"))
sequence.append(WaitForFocus("tables.html", acc_role=pyatspi.ROLE_LINK))

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
