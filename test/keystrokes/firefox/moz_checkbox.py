#!/usr/bin/python

"""Test of Mozilla ARIA checkbox presentation using Firefox.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on the Firefox window as well as for focus
# to move to the "DHTML Checkbox" frame.
#
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the Mozilla ARIA checkbox demo.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("http://www.mozilla.org/access/dhtml/checkbox"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())
sequence.append(WaitForFocus("DHTML Checkbox", acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Tab to the first checkbox.  The following will be presented.
#
# BRAILLE LINE:  '<x>  Include decorative fruit basket  CheckBox'
# VISIBLE:  '<x>  Include decorative fruit ba', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: ' Include decorative fruit basket  check box checked'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus(" Include decorative fruit basket", acc_role=pyatspi.ROLE_CHECK_BOX))

########################################################################
# Now, change its state.  The following should be presented in speech
# and braille:
#
# BRAILLE LINE:  '< >  Include decorative fruit basket  CheckBox'
#     VISIBLE:  '< >  Include decorative fruit ba', cursor=1
# SPEECH OUTPUT: 'not checked'
#
sequence.append(TypeAction(" "))

########################################################################
# Tab to the second checkbox.  The following will be presented.
#
# BRAILLE LINE:  '<x>  Required checkbox  CheckBox'
#     VISIBLE:  '<x>  Required checkbox  CheckBox', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: ' Required checkbox  check box checked'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus(" Required checkbox", acc_role=pyatspi.ROLE_CHECK_BOX))

########################################################################
# Now, change its state.  The following should be presented in speech
# and braille:
#
# BRAILLE LINE:  '< >  Required checkbox  CheckBox'
#     VISIBLE:  '< >  Required checkbox  CheckBox', cursor=1
# SPEECH OUTPUT: 'not checked'
#
sequence.append(TypeAction(" "))

########################################################################
# Tab to the third checkbox.  The following will be presented.
#
# BRAILLE LINE:  '<x>  Invalid checkbox  CheckBox'
#     VISIBLE:  '<x>  Invalid checkbox  CheckBox', cursor=1
# SPEECH OUTPUT: ''
# SPEECH OUTPUT: ' Invalid checkbox  check box checked'
#
sequence.append(KeyComboAction("Tab"))
sequence.append(WaitForFocus(" Invalid checkbox", acc_role=pyatspi.ROLE_CHECK_BOX))

########################################################################
# Now, change its state.  The following should be presented in speech
# and braille:
#
# BRAILLE LINE:  '< >  Invalid checkbox  CheckBox'
#     VISIBLE:  '< >  Invalid checkbox  CheckBox', cursor=1
# SPEECH OUTPUT: 'not checked'
#
sequence.append(TypeAction(" "))

########################################################################
# Now, change its state back.  The following should be presented in speech
# and braille:
#
# BRAILLE LINE:  '<x>  Invalid checkbox  CheckBox'
#     VISIBLE:  '<x>  Invalid checkbox  CheckBox', cursor=1
# SPEECH OUTPUT: 'checked'
#
sequence.append(TypeAction(" "))

########################################################################
# Do a basic "Where Am I" via KP_Enter.  The following should be
# presented in speech and braille:
#
# BRAILLE LINE:  '< >  Invalid checkbox CheckBox'
#     VISIBLE:  '< >  Invalid checkbox CheckBox', cursor=1
# SPEECH OUTPUT: 'Invalid checkbox check box'
# SPEECH OUTPUT: 'not checked'
# SPEECH OUTPUT: ''
#
sequence.append(KeyComboAction("KP_Enter"))
sequence.append(PauseAction(3000))

########################################################################
# Close the demo
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_name="Location", acc_role=pyatspi.ROLE_ENTRY))
sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))
sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.start()
