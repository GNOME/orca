#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

# Work around some new quirk in Gecko that causes this test to fail if
# run via the test harness rather than manually.
sequence.append(KeyComboAction("<Control>r"))

sequence.append(KeyComboAction("<Control>Home"))
sequence.append(KeyComboAction("h"))
sequence.append(KeyComboAction("h"))
sequence.append(KeyComboAction("h"))
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Shift Down",
    ["BRAILLE LINE:  'About h1'",
     "     VISIBLE:  'About h1', cursor=1",
     "SPEECH OUTPUT: 'About'",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Shift Down",
    ["BRAILLE LINE:  'Orca is a free, open source, flexible, extensible, and'",
     "     VISIBLE:  'rce, flexible, extensible, and', cursor=32",
     "SPEECH OUTPUT: 'Orca is a free, open source, flexible, extensible, and '",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Shift Down",
    ["BRAILLE LINE:  'powerful assistive technology for people with visual'",
     "     VISIBLE:  'hnology for people with visual', cursor=32",
     "SPEECH OUTPUT: 'powerful assistive technology for people with visual '",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Shift Down",
    ["BRAILLE LINE:  'impairments. Using various combinations of speech'",
     "     VISIBLE:  'various combinations of speech', cursor=32",
     "SPEECH OUTPUT: 'impairments. Using various combinations of speech '",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Shift Down",
    ["BRAILLE LINE:  'synthesis, braille, and magnification, Orca helps provide'",
     "     VISIBLE:  'nification, Orca helps provide', cursor=32",
     "SPEECH OUTPUT: 'synthesis, braille, and magnification, Orca helps provide '",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Shift Down",
    ["BRAILLE LINE:  'access to applications and toolkits that support the AT-SPI'",
     "     VISIBLE:  'olkits that support the AT-SPI', cursor=32",
     "SPEECH OUTPUT: 'access to applications and toolkits that support the AT-SPI '",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Shift Down",
    ["BRAILLE LINE:  '(e.g., the GNOME desktop). The development of Orca has'",
     "     VISIBLE:  '). The development of Orca has', cursor=32",
     "SPEECH OUTPUT: '(e.g., the GNOME desktop). The development of Orca has '",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Shift Down",
    ["BRAILLE LINE:  'been led by the Accessibility Program Office of Sun'",
     "     VISIBLE:  'been led by the Accessibility Pr', cursor=17",
     "SPEECH OUTPUT: 'been led by the '",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Shift Down",
    ["BRAILLE LINE:  'Microsystems, Inc. with contributions from many'",
     "     VISIBLE:  'Microsystems, Inc. with contribu', cursor=1",
     "SPEECH OUTPUT: 'Accessibility Program Office of Sun Microsystems, Inc.  with'",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Shift Down",
    ["BRAILLE LINE:  'community members.'",
     "     VISIBLE:  'community members.', cursor=1",
     "SPEECH OUTPUT: 'contributions from many community members .'",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Shift Down",
    ["BRAILLE LINE:  'The complete list of work to do, including bugs and feature requests, along with known'",
     "     VISIBLE:  'ure requests, along with known', cursor=32",
     "SPEECH OUTPUT: 'The complete list of work to do, including bugs and feature requests, along with known '",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Down"))
sequence.append(utils.AssertPresentationAction(
    "12. Shift Down",
    ["BRAILLE LINE:  'problems in other components, is maintained in Bugzilla \\(please see our notes on how'",
     "     VISIBLE:  'r components, is maintained in B', cursor=32",
     "SPEECH OUTPUT: 'problems in other components, is maintained in Bugzilla  \\(please see our'",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Down"))
sequence.append(utils.AssertPresentationAction(
    "13. Shift Down",
    ["BRAILLE LINE:  'we use Bugzilla\\).'",
     "     VISIBLE:  'we use Bugzilla\\).', cursor=1",
     "SPEECH OUTPUT: 'notes on how we use Bugzilla \\).'",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Down"))
sequence.append(utils.AssertPresentationAction(
    "14. Shift Down",
    ["BRAILLE LINE:  'Please join and participate on the Orca mailing list (archives): it's a helpful, kind, and'",
     "     VISIBLE:  'se join and participate on the O', cursor=32",
     "SPEECH OUTPUT: 'Please join and participate on the Orca mailing list  (archives ): it's a helpful, kind, and'",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Down"))
sequence.append(utils.AssertPresentationAction(
    "15. Shift Down",
    ["BRAILLE LINE:  'productive environment composed of users and developers.'",
     "     VISIBLE:  'productive environment composed ', cursor=0",
     "SPEECH OUTPUT: 'productive environment composed of users and developers. '",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Down"))
sequence.append(utils.AssertPresentationAction(
    "16. Shift Down",
    ["BRAILLE LINE:  'Audio Guides h1'",
     "     VISIBLE:  'Audio Guides h1', cursor=1",
     "SPEECH OUTPUT: 'Audio Guides'",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Down"))
sequence.append(utils.AssertPresentationAction(
    "17. Shift Down",
    ["BRAILLE LINE:  'Darragh Ó Héiligh has created several audio guides for Orca. This is a fantastic'",
     "     VISIBLE:  'Darragh Ó Héiligh has created se', cursor=1",
     "SPEECH OUTPUT: 'Darragh Ó Héiligh  has created several audio guides for Orca. This is a fantastic'",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Down"))
sequence.append(utils.AssertPresentationAction(
    "18. Shift Down",
    ["BRAILLE LINE:  'contribution (THANKS!)!!! The audio guides can be found at'",
     "     VISIBLE:  'e audio guides can be found at', cursor=32",
     "SPEECH OUTPUT: 'contribution (THANKS!)!!! The audio guides can be found at '",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Down"))
sequence.append(utils.AssertPresentationAction(
    "19. Shift Down",
    ["BRAILLE LINE:  'http://www.digitaldarragh.com/linuxat.asp and include the following:'",
     "     VISIBLE:  'http://www.digitaldarragh.com/li', cursor=1",
     "SPEECH OUTPUT: 'http://www.digitaldarragh.com/linuxat.asp  and include the following:'",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Down"))
sequence.append(utils.AssertPresentationAction(
    "20. Shift Down",
    ["BRAILLE LINE:  '• Walk through of the installation of Ubuntu 7.4. Very helpful tutorial'",
     "     VISIBLE:  'Walk through of the installation', cursor=1",
     "SPEECH OUTPUT: 'Walk through of the installation of Ubuntu 7.4. Very helpful tutorial'",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Down"))
sequence.append(utils.AssertPresentationAction(
    "21. Shift Down",
    ["BRAILLE LINE:  '• Review of Fedora 7 and the Orca screen reader for the Gnome graphical desktop'",
     "     VISIBLE:  'Review of Fedora 7 and the Orca ', cursor=1",
     "SPEECH OUTPUT: 'Review of Fedora 7 and the Orca screen reader for the Gnome graphical desktop'",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Down"))
sequence.append(utils.AssertPresentationAction(
    "22. Shift Down",
    ["BRAILLE LINE:  '• Guide to installing the latest versions of Firefox and Orca'",
     "     VISIBLE:  'Guide to installing the latest v', cursor=1",
     "SPEECH OUTPUT: 'Guide to installing the latest versions of Firefox and Orca'",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Down"))
sequence.append(utils.AssertPresentationAction(
    "23. Shift Down",
    ["BRAILLE LINE:  'Download/Installation h1'",
     "     VISIBLE:  'Download/Installation h1', cursor=1",
     "SPEECH OUTPUT: 'Download/Installation'",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Down"))
sequence.append(utils.AssertPresentationAction(
    "24. Shift Down",
    ["BRAILLE LINE:  'As of GNOME 2.16, Orca is a part of the GNOME platform. As a result, Orca is already'",
     "     VISIBLE:  '. As a result, Orca is already', cursor=32",
     "SPEECH OUTPUT: 'As of GNOME 2.16, Orca is a part of the GNOME platform. As a result, Orca is already '",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Down"))
sequence.append(utils.AssertPresentationAction(
    "25. Shift Down",
    ["BRAILLE LINE:  'provided by default on a number of operating system distributions, including Open'",
     "     VISIBLE:  'ystem distributions, including O', cursor=32",
     "SPEECH OUTPUT: 'provided by default on a number of operating system distributions, including '",
     "SPEECH OUTPUT: 'selected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Up"))
sequence.append(utils.AssertPresentationAction(
    "26. Shift Up",
    ["BRAILLE LINE:  'Solaris and Ubuntu.'",
     "     VISIBLE:  'Solaris and Ubuntu.', cursor=1",
     "SPEECH OUTPUT: 'provided by default on a number of operating system distributions, including '",
     "SPEECH OUTPUT: 'unselected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Up"))
sequence.append(utils.AssertPresentationAction(
    "27. Shift Up",
    ["BRAILLE LINE:  'provided by default on a number of operating system distributions, including Open'",
     "     VISIBLE:  'provided by default on a number ', cursor=0",
     "SPEECH OUTPUT: 'As of GNOME 2.16, Orca is a part of the GNOME platform. As a result, Orca is already '",
     "SPEECH OUTPUT: 'unselected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Up"))
sequence.append(utils.AssertPresentationAction(
    "28. Shift Up",
    ["BRAILLE LINE:  'As of GNOME 2.16, Orca is a part of the GNOME platform. As a result, Orca is already'",
     "     VISIBLE:  'As of GNOME 2.16, Orca is a part', cursor=1",
     "SPEECH OUTPUT: 'Download/Installation'",
     "SPEECH OUTPUT: 'unselected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Up"))
sequence.append(utils.AssertPresentationAction(
    "29. Shift Up",
    ["BRAILLE LINE:  'Download/Installation h1'",
     "     VISIBLE:  'Download/Installation h1', cursor=1",
     "SPEECH OUTPUT: 'Guide to installing the latest versions of Firefox and Orca'",
     "SPEECH OUTPUT: 'unselected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Up"))
sequence.append(utils.AssertPresentationAction(
    "30. Shift Up",
    ["BRAILLE LINE:  '• Guide to installing the latest versions of Firefox and Orca'",
     "     VISIBLE:  'Guide to installing the latest v', cursor=1",
     "SPEECH OUTPUT: 'Review of Fedora 7 and the Orca screen reader for the Gnome graphical desktop'",
     "SPEECH OUTPUT: 'unselected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Up"))
sequence.append(utils.AssertPresentationAction(
    "31. Shift Up",
    ["BRAILLE LINE:  '• Review of Fedora 7 and the Orca screen reader for the Gnome graphical desktop'",
     "     VISIBLE:  'Review of Fedora 7 and the Orca ', cursor=1",
     "SPEECH OUTPUT: 'Walk through of the installation of Ubuntu 7.4. Very helpful tutorial'",
     "SPEECH OUTPUT: 'unselected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Up"))
sequence.append(utils.AssertPresentationAction(
    "32. Shift Up",
    ["BRAILLE LINE:  '• Walk through of the installation of Ubuntu 7.4. Very helpful tutorial'",
     "     VISIBLE:  'Walk through of the installation', cursor=1",
     "SPEECH OUTPUT: 'http://www.digitaldarragh.com/linuxat.asp  and include the following:'",
     "SPEECH OUTPUT: 'unselected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Up"))
sequence.append(utils.AssertPresentationAction(
    "33. Shift Up",
    ["BRAILLE LINE:  'http://www.digitaldarragh.com/linuxat.asp and include the following:'",
     "     VISIBLE:  'http://www.digitaldarragh.com/li', cursor=1",
     "SPEECH OUTPUT: 'contribution (THANKS!)!!! The audio guides can be found at '",
     "SPEECH OUTPUT: 'unselected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Up"))
sequence.append(utils.AssertPresentationAction(
    "34. Shift Up",
    ["BRAILLE LINE:  'contribution (THANKS!)!!! The audio guides can be found at'",
     "     VISIBLE:  'contribution (THANKS!)!!! The au', cursor=0",
     "SPEECH OUTPUT: 'Darragh Ó Héiligh  has created several audio guides for Orca. This is a fantastic'",
     "SPEECH OUTPUT: 'unselected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Up"))
sequence.append(utils.AssertPresentationAction(
    "35. Shift Up",
    ["BRAILLE LINE:  'Darragh Ó Héiligh has created several audio guides for Orca. This is a fantastic'",
     "     VISIBLE:  'Darragh Ó Héiligh has created se', cursor=1",
     "SPEECH OUTPUT: 'Audio Guides'",
     "SPEECH OUTPUT: 'unselected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Shift>Up"))
sequence.append(utils.AssertPresentationAction(
    "36. Shift Up",
    ["BRAILLE LINE:  'Audio Guides h1'",
     "     VISIBLE:  'Audio Guides h1', cursor=1",
     "SPEECH OUTPUT: 'productive environment composed of users and developers. '",
     "SPEECH OUTPUT: 'unselected' voice=system"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>c"))
sequence.append(utils.AssertPresentationAction(
    "37. Control c",
    ["BRAILLE LINE:  'Copied selection to clipboard.'",
     "     VISIBLE:  'Copied selection to clipboard.', cursor=0",
     "SPEECH OUTPUT: 'Copied selection to clipboard.' voice=system"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
