#!/usr/bin/python

"""Test of line navigation output of Firefox on the Orca wiki."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>End"))
sequence.append(utils.AssertPresentationAction(
    "1. Bottom of file",
    ["BRAILLE LINE:  'Hosted by Red Hat.'",
     "     VISIBLE:  'Hosted by Red Hat.', cursor=1",
     "SPEECH OUTPUT: 'Hosted by '",
     "SPEECH OUTPUT: 'Red Hat'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: '. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Up",
    ["BRAILLE LINE:  'Copyright \xa9 2005, 2006, 2007 The GNOME Project.'",
     "     VISIBLE:  'Copyright \xa9 2005, 2006, 2007 The', cursor=1",
     "SPEECH OUTPUT: 'Copyright \xa9 2005, 2006, 2007 '",
     "SPEECH OUTPUT: 'The GNOME Project'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: '.",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Up",
    ["BRAILLE LINE:  'GnomeWorldWide image'",
     "     VISIBLE:  'GnomeWorldWide image', cursor=1",
     "SPEECH OUTPUT: 'GnomeWorldWide'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Up",
    ["BRAILLE LINE:  'Wide h3'",
     "     VISIBLE:  'Wide h3', cursor=1",
     "SPEECH OUTPUT: 'Wide'",
     "SPEECH OUTPUT: 'heading level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Up",
    ["BRAILLE LINE:  'GNOME World h3'",
     "     VISIBLE:  'GNOME World h3', cursor=1",
     "SPEECH OUTPUT: 'GNOME World '",
     "SPEECH OUTPUT: 'heading level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Up",
    ["BRAILLE LINE:  'More Actions: combo box'",
     "     VISIBLE:  'More Actions: combo box', cursor=1",
     "SPEECH OUTPUT: 'More Actions:'",
     "SPEECH OUTPUT: 'combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Up",
    ["BRAILLE LINE:  'Attachments'",
     "     VISIBLE:  'Attachments', cursor=1",
     "SPEECH OUTPUT: 'Attachments'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Up",
    ["BRAILLE LINE:  'Info'",
     "     VISIBLE:  'Info', cursor=1",
     "SPEECH OUTPUT: 'Info'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Up",
    ["BRAILLE LINE:  'Immutable Page'",
     "     VISIBLE:  'Immutable Page', cursor=1",
     "SPEECH OUTPUT: 'Immutable Page'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "10. Line Up",
    ["BRAILLE LINE:  'Page h3'",
     "     VISIBLE:  'Page h3', cursor=1",
     "SPEECH OUTPUT: 'Page'",
     "SPEECH OUTPUT: 'heading level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "11. Line Up",
    ["BRAILLE LINE:  'Login'",
     "     VISIBLE:  'Login', cursor=1",
     "SPEECH OUTPUT: 'Login'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "12. Line Up",
    ["BRAILLE LINE:  'User h3'",
     "     VISIBLE:  'User h3', cursor=1",
     "SPEECH OUTPUT: 'User'",
     "SPEECH OUTPUT: 'heading level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "13. Line Up",
    ["BRAILLE LINE:  'Orca (last edited 2007-12-07 22:09:22 by WillieWalker)'",
     "     VISIBLE:  'Orca (last edited 2007-12-07 22:', cursor=1",
     "SPEECH OUTPUT: 'Orca (last edited 2007-12-07 22:09:22 by '",
     "SPEECH OUTPUT: 'WillieWalker'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: ')'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "14. Line Up",
    ["BRAILLE LINE:  'CategoryAccessibility'",
     "     VISIBLE:  'CategoryAccessibility', cursor=1",
     "SPEECH OUTPUT: 'CategoryAccessibility'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "15. Line Up",
    ["BRAILLE LINE:  'separator'",
     "     VISIBLE:  'separator', cursor=1",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "16. Line Up",
    ["BRAILLE LINE:  'warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.'",
     "     VISIBLE:  'warranty of MERCHANTABILITY or F', cursor=1",
     "SPEECH OUTPUT: 'warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "17. Line Up",
    ["BRAILLE LINE:  'in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied'",
     "     VISIBLE:  'in the hope that it will be usef', cursor=1",
     "SPEECH OUTPUT: 'in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "18. Line Up",
    ["BRAILLE LINE:  'The information on this page and the other Orca-related pages on this site are distributed'",
     "     VISIBLE:  'The information on this page and', cursor=1",
     "SPEECH OUTPUT: 'The information on this page and the other Orca-related pages on this site are distributed '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "19. Line Up",
    ["BRAILLE LINE:  'separator'",
     "     VISIBLE:  'separator', cursor=1",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "20. Line Up",
    ["BRAILLE LINE:  '•Python Pocket Reference, Mark Lutz'",
     "     VISIBLE:  '•Python Pocket Reference, Mark L', cursor=1",
     "SPEECH OUTPUT: '•'",
     "SPEECH OUTPUT: 'Python Pocket Reference, Mark Lutz'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "21. Line Up",
    ["BRAILLE LINE:  '•Python in a Nutshell, Alex Martelli'",
     "     VISIBLE:  '•Python in a Nutshell, Alex Mart', cursor=1",
     "SPEECH OUTPUT: '•'",
     "SPEECH OUTPUT: 'Python in a Nutshell, Alex Martelli'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "22. Line Up",
    ["BRAILLE LINE:  '•Dive Into Python, Mark Pilgrim'",
     "     VISIBLE:  '•Dive Into Python, Mark Pilgrim', cursor=1",
     "SPEECH OUTPUT: '•'",
     "SPEECH OUTPUT: 'Dive Into Python, Mark Pilgrim'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "23. Line Up",
    ["BRAILLE LINE:  '• Design documents: orca image Orca Documentation Series'",
     "     VISIBLE:  '• Design documents: orca image O', cursor=1",
     "SPEECH OUTPUT: '•'",
     "SPEECH OUTPUT: 'Design documents: '",
     "SPEECH OUTPUT: 'orca'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: 'Orca Documentation Series'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "24. Line Up",
    ["BRAILLE LINE:  '• Bug database: bugzilla.gnome.org image GNOME Bug Tracking System (Bugzilla) ( buglist image current bug list)'",
     "     VISIBLE:  '• Bug database: bugzilla.gnome.o', cursor=1",
     "SPEECH OUTPUT: '•'",
     "SPEECH OUTPUT: 'Bug database: '",
     "SPEECH OUTPUT: 'bugzilla.gnome.org'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: 'GNOME Bug Tracking System (Bugzilla)'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: ' ('",
     "SPEECH OUTPUT: 'buglist'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: 'current bug list'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: ') '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "25. Line Up",
    ["BRAILLE LINE:  '• Mailing list: orca-list image orca-list@gnome.org ( orca-list image Archives)'",
     "     VISIBLE:  '• Mailing list: orca-list image ', cursor=1",
     "SPEECH OUTPUT: '•'",
     "SPEECH OUTPUT: 'Mailing list: '",
     "SPEECH OUTPUT: 'orca-list'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: 'orca-list@gnome.org'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: ' ('",
     "SPEECH OUTPUT: 'orca-list'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: 'Archives'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: ') '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "26. Line Up",
    ["BRAILLE LINE:  '• Frequently Asked Questions: FAQ'",
     "     VISIBLE:  '• Frequently Asked Questions: FA', cursor=1",
     "SPEECH OUTPUT: '•'",
     "SPEECH OUTPUT: 'Frequently Asked Questions: '",
     "SPEECH OUTPUT: 'FAQ'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "27. Line Up",
    ["BRAILLE LINE:  'More Information h1'",
     "     VISIBLE:  'More Information h1', cursor=1",
     "SPEECH OUTPUT: 'More Information'",
     "SPEECH OUTPUT: 'heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "28. Line Up",
    ["BRAILLE LINE:  'information.'",
     "     VISIBLE:  'information.', cursor=1",
     "SPEECH OUTPUT: 'information. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "29. Line Up",
    ["BRAILLE LINE:  'There's a bunch you can do! Please refer to the How Can I Help page for detailed'",
     "     VISIBLE:  'There's a bunch you can do! Plea', cursor=1",
     "SPEECH OUTPUT: 'There's a bunch you can do! Please refer to the '",
     "SPEECH OUTPUT: 'How Can I Help page'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: ' for detailed '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "30. Line Up",
    ["BRAILLE LINE:  'How Can I Help? h1'",
     "     VISIBLE:  'How Can I Help? h1', cursor=1",
     "SPEECH OUTPUT: 'How Can I Help?'",
     "SPEECH OUTPUT: 'heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "31. Line Up",
    ["BRAILLE LINE:  'Please also refer to the Accessible Applications page for detailed information.'",
     "     VISIBLE:  'Please also refer to the Accessi', cursor=1",
     "SPEECH OUTPUT: 'Please also refer to the '",
     "SPEECH OUTPUT: 'Accessible Applications page'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: ' for detailed information. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "32. Line Up",
    ["BRAILLE LINE:  'application.'",
     "     VISIBLE:  'application.', cursor=1",
     "SPEECH OUTPUT: 'application. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "33. Line Up",
    ["BRAILLE LINE:  'See also the Application Specific Settings page for how to configure settings specific to an'",
     "     VISIBLE:  'See also the Application Specifi', cursor=1",
     "SPEECH OUTPUT: 'See also the '",
     "SPEECH OUTPUT: 'Application Specific Settings'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: ' page for how to configure settings specific to an '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "34. Line Up",
    ["BRAILLE LINE:  'tested.'",
     "     VISIBLE:  'tested.', cursor=1",
     "SPEECH OUTPUT: 'tested. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "35. Line Up",
    ["BRAILLE LINE:  'repository within which users can share experiences regarding applications they have'",
     "     VISIBLE:  'repository within which users ca', cursor=1",
     "SPEECH OUTPUT: 'repository within which users can share experiences regarding applications they have '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "36. Line Up",
    ["BRAILLE LINE:  'them. The list is not to be a conclusive list of all applications. Rather, the goal is to provide a'",
     "     VISIBLE:  'them. The list is not to be a co', cursor=1",
     "SPEECH OUTPUT: 'them. The list is not to be a conclusive list of all applications. Rather, the goal is to provide a '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "37. Line Up",
    ["BRAILLE LINE:  'various applications that can be accessed with Orca as well as tips and tricks for using'",
     "     VISIBLE:  'various applications that can be', cursor=1",
     "SPEECH OUTPUT: 'various applications that can be accessed with Orca as well as tips and tricks for using '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "38. Line Up",
    ["BRAILLE LINE:  'On the Accessible Applications page, you will find a growing list of information regarding'",
     "     VISIBLE:  'On the Accessible Applications p', cursor=1",
     "SPEECH OUTPUT: 'On the '",
     "SPEECH OUTPUT: 'Accessible Applications page'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: ', you will find a growing list of information regarding '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "39. Line Up",
    ["BRAILLE LINE:  'access to more and more applications.'",
     "     VISIBLE:  'access to more and more applicat', cursor=1",
     "SPEECH OUTPUT: 'access to more and more applications. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "40. Line Up",
    ["BRAILLE LINE:  'than others, however, and the Orca community continually works to provide compelling'",
     "     VISIBLE:  'than others, however, and the Or', cursor=1",
     "SPEECH OUTPUT: 'than others, however, and the Orca community continually works to provide compelling '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "41. Line Up",
    ["BRAILLE LINE:  'applications, OpenOffice, Firefox, and the Java platform. Some applications work better'",
     "     VISIBLE:  'applications, OpenOffice, Firefo', cursor=1",
     "SPEECH OUTPUT: 'applications, '",
     "SPEECH OUTPUT: 'OpenOffice'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: ', Firefox, and the Java platform. Some applications work better '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "42. Line Up",
    ["BRAILLE LINE:  'technology service provider interface (AT-SPI). This includes the GNOME desktop and its'",
     "     VISIBLE:  'technology service provider inte', cursor=1",
     "SPEECH OUTPUT: 'technology service provider interface (AT-SPI). This includes the GNOME desktop and its '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "43. Line Up",
    ["BRAILLE LINE:  'Orca is designed to work with applications and toolkits that support the assistive'",
     "     VISIBLE:  'Orca is designed to work with ap', cursor=1",
     "SPEECH OUTPUT: 'Orca is designed to work with applications and toolkits that support the assistive '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "44. Line Up",
    ["BRAILLE LINE:  'Accessible Applications h1'",
     "     VISIBLE:  'Accessible Applications h1', cursor=1",
     "SPEECH OUTPUT: 'Accessible Applications'",
     "SPEECH OUTPUT: 'heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "45. Line Up",
    ["BRAILLE LINE:  'Please also refer to the Configuration/Use page for detailed information.'",
     "     VISIBLE:  'Please also refer to the Configu', cursor=1",
     "SPEECH OUTPUT: 'Please also refer to the '",
     "SPEECH OUTPUT: 'Configuration/Use page'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: ' for detailed information. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "46. Line Up",
    ["BRAILLE LINE:  'includes a \"Key Bindings\" tab that allows you to get a complete list of Orca key bindings.'",
     "     VISIBLE:  'includes a \"Key Bindings\" tab th', cursor=1",
     "SPEECH OUTPUT: 'includes a \"Key Bindings\" tab that allows you to get a complete list of Orca key bindings. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "47. Line Up",
    ["BRAILLE LINE:  'information on Orca-specific keyboard commands. The Orca Configuration GUI also'",
     "     VISIBLE:  'information on Orca-specific key', cursor=1",
     "SPEECH OUTPUT: 'information on Orca-specific keyboard commands. The '",
     "SPEECH OUTPUT: 'Orca Configuration GUI'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: ' also '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "48. Line Up",
    ["BRAILLE LINE:  'mode to examine a window. Refer to Orca Keyboard Commands (Laptop Layout) for more'",
     "     VISIBLE:  'mode to examine a window. Refer ', cursor=1",
     "SPEECH OUTPUT: 'mode to examine a window. Refer to '",
     "SPEECH OUTPUT: 'Orca Keyboard Commands'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: '(Laptop Layout)'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: ' for more '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "49. Line Up",
    ["KNOWN ISSUE: Here we are combining lines which are not being combined on the way down",
     "BRAILLE LINE:  'You may sometimes wish to control Orca itself, such as bringing up the Orca Configuration'",
     "     VISIBLE:  'Orca Configuration', cursor=1",
     "SPEECH OUTPUT: 'You may sometimes wish to control Orca itself, such as bringing up the '",
     "SPEECH OUTPUT: 'Orca Configuration '",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "50. Line Up",
    ["BRAILLE LINE:  'desktop applications.'",
     "     VISIBLE:  'desktop applications.', cursor=1",
     "SPEECH OUTPUT: 'desktop applications. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "51. Line Up",
    ["BRAILLE LINE:  'designed to present information as you navigate the desktop using the keynav-1 image built-in navigation'",
     "     VISIBLE:  'keynav-1 image built-in navigati', cursor=1",
     "SPEECH OUTPUT: 'designed to present information as you navigate the desktop using the '",
     "SPEECH OUTPUT: 'keynav-1'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: 'built-in navigation '",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "52. Line Up",
    ["BRAILLE LINE:  'logged in, waiting for a second or so, then typing orca and pressing return. Orca is'",
     "     VISIBLE:  'logged in, waiting for a second ', cursor=1",
     "SPEECH OUTPUT: 'logged in, waiting for a second or so, then typing orca and pressing return. Orca is '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "53. Line Up",
    ["BRAILLE LINE:  'The command to run orca is orca. You can enter this command by pressing Alt+F2 when'",
     "     VISIBLE:  'The command to run orca is orca.', cursor=1",
     "SPEECH OUTPUT: 'The command to run orca is orca. You can enter this command by pressing Alt+F2 when '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "54. Line Up",
    ["BRAILLE LINE:  'Configuration/Use h1'",
     "     VISIBLE:  'Configuration/Use h1', cursor=1",
     "SPEECH OUTPUT: 'Configuration/Use'",
     "SPEECH OUTPUT: 'heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "55. Line Up",
    ["BRAILLE LINE:  'distributions as well as installing Orca directly from source.'",
     "     VISIBLE:  'distributions as well as install', cursor=1",
     "SPEECH OUTPUT: 'distributions as well as installing Orca directly from source. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "56. Line Up",
    ["BRAILLE LINE:  'Please also refer to the Download/Installation page for detailed information on various'",
     "     VISIBLE:  'Please also refer to the Downloa', cursor=1",
     "SPEECH OUTPUT: 'Please also refer to the '",
     "SPEECH OUTPUT: 'Download/Installation page'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: ' for detailed information on various '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "57. Line Up",
    ["BRAILLE LINE:  'and www.ubuntu.com image Ubuntu.'",
     "     VISIBLE:  'and www.ubuntu.com image Ubuntu.', cursor=1",
     "SPEECH OUTPUT: 'and '",
     "SPEECH OUTPUT: 'www.ubuntu.com'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: 'Ubuntu'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: '. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "58. Line Up",
    ["BRAILLE LINE:  'provided by default on a number of operating system distributions, including www.opensolaris.org image Open Solaris'",
     "     VISIBLE:  'provided by default on a number ', cursor=1",
     "SPEECH OUTPUT: 'provided by default on a number of operating system distributions, including '",
     "SPEECH OUTPUT: 'www.opensolaris.org'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: 'Open Solaris'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "59. Line Up",
    ["BRAILLE LINE:  'As of GNOME 2.16, Orca is a part of the GNOME platform. As a result, Orca is already'",
     "     VISIBLE:  'As of GNOME 2.16, Orca is a part', cursor=1",
     "SPEECH OUTPUT: 'As of GNOME 2.16, Orca is a part of the GNOME platform. As a result, Orca is already '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "60. Line Up",
    ["BRAILLE LINE:  'Download/Installation h1'",
     "     VISIBLE:  'Download/Installation h1', cursor=1",
     "SPEECH OUTPUT: 'Download/Installation'",
     "SPEECH OUTPUT: 'heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "61. Line Up",
    ["BRAILLE LINE:  '•Guide to installing the latest versions of Firefox and Orca'",
     "     VISIBLE:  '•Guide to installing the latest ', cursor=1",
     "SPEECH OUTPUT: '•'",
     "SPEECH OUTPUT: 'Guide to installing the latest versions of Firefox and Orca'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "62. Line Up",
    ["BRAILLE LINE:  '•Review of Fedora 7 and the Orca screen reader for the Gnome graphical desktop'",
     "     VISIBLE:  '•Review of Fedora 7 and the Orca', cursor=1",
     "SPEECH OUTPUT: '•'",
     "SPEECH OUTPUT: 'Review of Fedora 7 and the Orca screen reader for the Gnome graphical desktop'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "63. Line Up",
    ["BRAILLE LINE:  '•Walk through of the installation of Ubuntu 7.4. Very helpful tutorial'",
     "     VISIBLE:  '•Walk through of the installatio', cursor=1",
     "SPEECH OUTPUT: '•'",
     "SPEECH OUTPUT: 'Walk through of the installation of Ubuntu 7.4. Very helpful tutorial'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "64. Line Up",
    ["BRAILLE LINE:  'contribution (THANKS!)!!! The audio guides can be found at linuxat image http://www.digitaldarragh.com'",
     "     VISIBLE:  'linuxat image http://www.digital', cursor=1",
     "SPEECH OUTPUT: 'contribution (THANKS!)!!! The audio guides can be found at '",
     "SPEECH OUTPUT: 'linuxat'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: 'http://www.digitaldarragh.com'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "65. Line Up",
    ["BRAILLE LINE:  'Darragh Ó Héiligh has created several audio guides for Orca. This is a fantastic'",
     "     VISIBLE:  'Darragh Ó Héiligh has created se', cursor=1",
     "SPEECH OUTPUT: 'Darragh Ó Héiligh'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: ' has created several audio guides for Orca. This is a fantastic '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "66. Line Up",
    ["BRAILLE LINE:  'Audio Guides h1'",
     "     VISIBLE:  'Audio Guides h1', cursor=1",
     "SPEECH OUTPUT: 'Audio Guides'",
     "SPEECH OUTPUT: 'heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "67. Line Up",
    ["BRAILLE LINE:  'productive environment composed of users and developers.'",
     "     VISIBLE:  'productive environment composed ', cursor=1",
     "SPEECH OUTPUT: 'productive environment composed of users and developers. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "68. Line Up",
    ["BRAILLE LINE:  'Please join and participate on the orca-list image Orca mailing list ( orca-list image archives): it's a helpful, kind, and'",
     "     VISIBLE:  'Please join and participate on t', cursor=1",
     "SPEECH OUTPUT: 'Please join and participate on the '",
     "SPEECH OUTPUT: 'orca-list'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: 'Orca mailing list'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: ' ('",
     "SPEECH OUTPUT: 'orca-list'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: 'archives'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: '): it's a helpful, kind, and '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "69. Line Up",
    ["BRAILLE LINE:  'problems in other components, is maintained in buglist image Bugzilla (please see our notes on how we'",
     "     VISIBLE:  'notes on how we', cursor=1",
     "SPEECH OUTPUT: 'problems in other components, is maintained in '",
     "SPEECH OUTPUT: 'buglist'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: 'Bugzilla'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: ' (please see our '",
     "SPEECH OUTPUT: 'notes on how we '",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "70. Line Up",
    ["BRAILLE LINE:  'The complete list of work to do, including bugs and feature requests, along with known'",
     "     VISIBLE:  'The complete list of work to do,', cursor=1",
     "SPEECH OUTPUT: 'The complete list of work to do, including bugs and feature requests, along with known '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "71. Line Up",
    ["BRAILLE LINE:  'access image Accessibility Program Office of Sun  with contributions from many'",
     "     VISIBLE:  'contributions from many', cursor=1",
     "SPEECH OUTPUT: 'access'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: 'Accessibility Program Office of Sun '",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: ' with '",
     "SPEECH OUTPUT: 'contributions from many '",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "72. Line Up",
    ["KNOWN ISSUE: Part of the line is missing.",
     "BRAILLE LINE:  'been led by the'",
     "     VISIBLE:  'been led by the', cursor=1",
     "SPEECH OUTPUT: 'been led by the '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "73. Line Up",
    ["BRAILLE LINE:  '(e.g., the GNOME desktop). The development of Orca has'",
     "     VISIBLE:  '(e.g., the GNOME desktop). The d', cursor=1",
     "SPEECH OUTPUT: '(e.g., the GNOME desktop). The development of Orca has '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "74. Line Up",
    ["BRAILLE LINE:  'access to applications and toolkits that support the AT-SPI'",
     "     VISIBLE:  'access to applications and toolk', cursor=1",
     "SPEECH OUTPUT: 'access to applications and toolkits that support the AT-SPI '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "75. Line Up",
    ["BRAILLE LINE:  'synthesis, braille, and magnification, Orca helps provide'",
     "     VISIBLE:  'synthesis, braille, and magnific', cursor=1",
     "SPEECH OUTPUT: 'synthesis, braille, and magnification, Orca helps provide '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "76. Line Up",
    ["BRAILLE LINE:  'impairments. Using various combinations of speech'",
     "     VISIBLE:  'impairments. Using various combi', cursor=1",
     "SPEECH OUTPUT: 'impairments. Using various combinations of speech '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "77. Line Up",
    ["BRAILLE LINE:  'powerful assistive technology for people with visual'",
     "     VISIBLE:  'powerful assistive technology fo', cursor=1",
     "SPEECH OUTPUT: 'powerful assistive technology for people with visual '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "78. Line Up",
    ["BRAILLE LINE:  'Orca is a free, open source, flexible, extensible, and'",
     "     VISIBLE:  'Orca is a free, open source, fle', cursor=1",
     "SPEECH OUTPUT: 'Orca is a free, open source, flexible, extensible, and '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "79. Line Up",
    ["BRAILLE LINE:  'About h1'",
     "     VISIBLE:  'About h1', cursor=1",
     "SPEECH OUTPUT: 'About'",
     "SPEECH OUTPUT: 'heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "80. Line Up",
    ["BRAILLE LINE:  '8.More Information'",
     "     VISIBLE:  '8.More Information', cursor=1",
     "SPEECH OUTPUT: '8.'",
     "SPEECH OUTPUT: 'More Information'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "81. Line Up",
    ["BRAILLE LINE:  '7.How Can I Help?'",
     "     VISIBLE:  '7.How Can I Help?', cursor=1",
     "SPEECH OUTPUT: '7.'",
     "SPEECH OUTPUT: 'How Can I Help?'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "82. Line Up",
    ["BRAILLE LINE:  '6.Accessible Applications'",
     "     VISIBLE:  '6.Accessible Applications', cursor=1",
     "SPEECH OUTPUT: '6.'",
     "SPEECH OUTPUT: 'Accessible Applications'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "83. Line Up",
    ["BRAILLE LINE:  '5.Configuration/Use'",
     "     VISIBLE:  '5.Configuration/Use', cursor=1",
     "SPEECH OUTPUT: '5.'",
     "SPEECH OUTPUT: 'Configuration/Use'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "84. Line Up",
    ["BRAILLE LINE:  '4.Download/Installation'",
     "     VISIBLE:  '4.Download/Installation', cursor=1",
     "SPEECH OUTPUT: '4.'",
     "SPEECH OUTPUT: 'Download/Installation'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "85. Line Up",
    ["BRAILLE LINE:  '3.Audio Guides'",
     "     VISIBLE:  '3.Audio Guides', cursor=1",
     "SPEECH OUTPUT: '3.'",
     "SPEECH OUTPUT: 'Audio Guides'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "86. Line Up",
    ["BRAILLE LINE:  '2.About'",
     "     VISIBLE:  '2.About', cursor=1",
     "SPEECH OUTPUT: '2.'",
     "SPEECH OUTPUT: 'About'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "87. Line Up",
    ["BRAILLE LINE:  '1.Welcome to Orca!'",
     "     VISIBLE:  '1.Welcome to Orca!', cursor=1",
     "SPEECH OUTPUT: '1.'",
     "SPEECH OUTPUT: 'Welcome to Orca!'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "88. Line Up",
    ["BRAILLE LINE:  'Contents'",
     "     VISIBLE:  'Contents', cursor=1",
     "SPEECH OUTPUT: 'Contents'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "89. Line Up",
    ["BRAILLE LINE:  'HOT HOT HOT: Notes on access to Firefox 3.0'",
     "     VISIBLE:  'HOT HOT HOT: Notes on access to ', cursor=1",
     "SPEECH OUTPUT: 'HOT HOT HOT: Notes on '",
     "SPEECH OUTPUT: 'access to Firefox 3.0'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "90. Line Up",
    ["BRAILLE LINE:  'Orca Logo'",
     "     VISIBLE:  'Orca Logo', cursor=1",
     "SPEECH OUTPUT: 'Orca Logo'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "91. Line Up",
    ["BRAILLE LINE:  'Welcome to Orca! h1'",
     "     VISIBLE:  'Welcome to Orca! h1', cursor=1",
     "SPEECH OUTPUT: 'Welcome to Orca!'",
     "SPEECH OUTPUT: 'heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "92. Line Up",
    ["BRAILLE LINE:  'Home | Download/Installation | Configuration/Use | Accessible Applications | orca-list image Mailing List ( orca-list image'",
     "     VISIBLE:  'orca-list image', cursor=1",
     "SPEECH OUTPUT: 'Home'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: ' | '",
     "SPEECH OUTPUT: 'Download/Installation'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: ' | '",
     "SPEECH OUTPUT: 'Configuration/Use'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: ' | '",
     "SPEECH OUTPUT: 'Accessible Applications'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: ' | '",
     "SPEECH OUTPUT: 'orca-list'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: 'Mailing List'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'",
     "SPEECH OUTPUT: ' ('",
     "SPEECH OUTPUT: 'orca-list'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "93. Line Up",
    ["BRAILLE LINE:  'en Español'",
     "     VISIBLE:  'en Español', cursor=1",
     "SPEECH OUTPUT: 'en Español'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "94. Line Up",
    ["BRAILLE LINE:  'Home RecentChanges FindPage HelpContents Orca'",
     "     VISIBLE:  'Home RecentChanges FindPage Help', cursor=1",
     "SPEECH OUTPUT: 'Home'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'RecentChanges'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'FindPage'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'HelpContents'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'Orca'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "95. Line Up",
    ["BRAILLE LINE:  'live.gnome.org h1  $l Titles push button Text push button'",
     "     VISIBLE:  'live.gnome.org h1  $l Titles pus', cursor=1",
     "SPEECH OUTPUT: 'live.gnome.org '",
     "SPEECH OUTPUT: 'heading level 1'",
     "SPEECH OUTPUT: 'entry'",
     "SPEECH OUTPUT: 'Search'",
     "SPEECH OUTPUT: 'Titles'",
     "SPEECH OUTPUT: 'push button'",
     "SPEECH OUTPUT: 'grayed'",
     "SPEECH OUTPUT: 'Text'",
     "SPEECH OUTPUT: 'push button'",
     "SPEECH OUTPUT: 'grayed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "96. Line Up",
    ["BRAILLE LINE:  'Home News Projects Art Support Development Community'",
     "     VISIBLE:  'Home News Projects Art Support D', cursor=1",
     "SPEECH OUTPUT: 'Home'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'News'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'Projects'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'Art'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'Support'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'Development'",
     "SPEECH OUTPUT: 'link'",
     "SPEECH OUTPUT: 'Community'",
     "SPEECH OUTPUT: 'link'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
