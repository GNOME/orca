# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of sayAll output of Firefox on the Orca wiki.
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the local "wiki" test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "orca-wiki.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

sequence.append(WaitForFocus("Orca - GNOME Live!",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

sequence.append(PauseAction(3000))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file", 
    ["BRAILLE LINE:  'Home News Projects Art Support Development Community'",
     "     VISIBLE:  'Home News Projects Art Support D', cursor=1",
     "SPEECH OUTPUT: 'Home link News link Projects link Art link Support link Development link Community link'"]))

########################################################################
# SayAll to the End.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("KP_Add"))
sequence.append(utils.AssertPresentationAction(
    "KP_Add to do a SayAll",
    ["SPEECH OUTPUT: 'Home link'",
     "SPEECH OUTPUT: 'News link'",
     "SPEECH OUTPUT: 'Projects link'",
     "SPEECH OUTPUT: 'Art link'",
     "SPEECH OUTPUT: 'Support link'",
     "SPEECH OUTPUT: 'Development link'",
     "SPEECH OUTPUT: 'Community link'",
     "SPEECH OUTPUT: 'live.gnome.org heading level 1'",
     "SPEECH OUTPUT: 'Search: text Search'",
     "SPEECH OUTPUT: 'Titles button Text button'",
     "SPEECH OUTPUT: 'Home link'",
     "SPEECH OUTPUT: 'RecentChanges link'",
     "SPEECH OUTPUT: 'FindPage link'",
     "SPEECH OUTPUT: 'HelpContents link'",
     "SPEECH OUTPUT: 'Orca link'",
     "SPEECH OUTPUT: 'en Español link'",
     "SPEECH OUTPUT: 'Home link'",
     "SPEECH OUTPUT: ' | Download/Installation link  | Configuration/Use link  | Accessible Applications link  | Mailing List link  ( Archives link ) | FAQ link  | DocIndex link'",
     "SPEECH OUTPUT: 'Welcome to Orca! heading level 1'",
     "SPEECH OUTPUT: 'Orca Logo link image'",
     "SPEECH OUTPUT: 'HOT HOT HOT: Notes on access to Firefox 3.0 link'",
     "SPEECH OUTPUT: 'Contents'",
     "SPEECH OUTPUT: '1. Welcome to Orca! link'",
     "SPEECH OUTPUT: '2. About link'",
     "SPEECH OUTPUT: '3. Audio Guides link'",
     "SPEECH OUTPUT: '4. Download/Installation link'",
     "SPEECH OUTPUT: '5. Configuration/Use link'",
     "SPEECH OUTPUT: '6. Accessible Applications link'",
     "SPEECH OUTPUT: '7. How Can I Help? link'",
     "SPEECH OUTPUT: '8. More Information link'",
     "SPEECH OUTPUT: 'About heading level 1'",
     "SPEECH OUTPUT: 'Orca is a free, open source, flexible, extensible, and powerful assistive technology for people with visual impairments. Using various combinations of speech synthesis, braille, and magnification, Orca helps provide access to applications and toolkits that support the AT-SPI (e.g., the GNOME desktop). The development of Orca has been led by the Accessibility Program Office of Sun Microsystems, Inc. link  with contributions from many community members link .'",
     "SPEECH OUTPUT: 'The complete list of work to do, including bugs and feature requests, along with known problems in other components, is maintained in Bugzilla link  (please see our notes on how we use Bugzilla link ).'",
     "SPEECH OUTPUT: 'Please join and participate on the Orca mailing list link  ( archives link ): it's a helpful, kind, and productive environment composed of users and developers.'",
     "SPEECH OUTPUT: 'Audio Guides heading level 1'",
     "SPEECH OUTPUT: 'Darragh Ó Héiligh link'",
     "SPEECH OUTPUT: ' has created several audio guides for Orca. This is a fantastic contribution (THANKS!)!!! The audio guides can be found at http://www.digitaldarragh.com/linuxat.asp link  and include the following:'",
     "SPEECH OUTPUT: '• Walk through of the installation of Ubuntu 7.4. Very helpful tutorial link'",
     "SPEECH OUTPUT: '• Review of Fedora 7 and the Orca screen reader for the Gnome graphical desktop link'",
     "SPEECH OUTPUT: '• Guide to installing the latest versions of Firefox and Orca link'",
     "SPEECH OUTPUT: 'Download/Installation heading level 1'",
     "SPEECH OUTPUT: 'As of GNOME 2.16, Orca is a part of the GNOME platform. As a result, Orca is already provided by default on a number of operating system distributions, including Open Solaris link  and Ubuntu link .'",
     "SPEECH OUTPUT: 'Please also refer to the Download/Installation page link  for detailed information on various distributions as well as installing Orca directly from source.'",
     "SPEECH OUTPUT: 'Configuration/Use heading level 1'",
     "SPEECH OUTPUT: 'The command to run orca is orca. You can enter this command by pressing Alt+F2 when logged in, waiting for a second or so, then typing orca and pressing return. Orca is designed to present information as you navigate the desktop using the built-in navigation mechanisms of GNOME link . These navigation mechanisms are consistent across most desktop applications.'",
     "SPEECH OUTPUT: 'You may sometimes wish to control Orca itself, such as bringing up the Orca Configuration GUI link  (accessed by pressing Insert+Space when Orca is running) and for using flat review mode to examine a window. Refer to Orca Keyboard Commands link (Laptop Layout) link  for more information on Orca-specific keyboard commands. The Orca Configuration GUI link  also includes a \"Key Bindings\" tab that allows you to get a complete list of Orca key bindings.'",
     "SPEECH OUTPUT: 'Please also refer to the Configuration/Use page link  for detailed information.'",
     "SPEECH OUTPUT: 'Accessible Applications heading level 1'",
     "SPEECH OUTPUT: 'Orca is designed to work with applications and toolkits that support the assistive technology service provider interface (AT-SPI). This includes the GNOME desktop and its applications, OpenOffice link , Firefox, and the Java platform. Some applications work better than others, however, and the Orca community continually works to provide compelling access to more and more applications.'",
     "SPEECH OUTPUT: 'On the Accessible Applications page link , you will find a growing list of information regarding various applications that can be accessed with Orca as well as tips and tricks for using them. The list is not to be a conclusive list of all applications. Rather, the goal is to provide a repository within which users can share experiences regarding applications they have tested.'",
     "SPEECH OUTPUT: 'See also the Application Specific Settings link  page for how to configure settings specific to an application.'",
     "SPEECH OUTPUT: 'Please also refer to the Accessible Applications page link  for detailed information.'",
     "SPEECH OUTPUT: 'How Can I Help? heading level 1'",
     "SPEECH OUTPUT: 'There's a bunch you can do! Please refer to the How Can I Help page link  for detailed information.'",
     "SPEECH OUTPUT: 'More Information heading level 1'",
     "SPEECH OUTPUT: '• Frequently Asked Questions: FAQ link'",
     "SPEECH OUTPUT: '• Mailing list: orca-list@gnome.org link  ( Archives link )'",
     "SPEECH OUTPUT: '• Bug database: GNOME Bug Tracking System (Bugzilla) link  ( current bug list link )'",
     "SPEECH OUTPUT: '• Design documents: Orca Documentation Series link'",
     "SPEECH OUTPUT: '• Dive Into Python, Mark Pilgrim link'",
     "SPEECH OUTPUT: '• Python in a Nutshell, Alex Martelli link'",
     "SPEECH OUTPUT: '• Python Pocket Reference, Mark Lutz link'",
     "SPEECH OUTPUT: 'separator'",
     "SPEECH OUTPUT: 'The information on this page and the other Orca-related pages on this site are distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.'",
     "SPEECH OUTPUT: 'separator'",
     "SPEECH OUTPUT: 'CategoryAccessibility link'",
     "SPEECH OUTPUT: 'Orca (last edited 2007-12-07 22:09:22 by WillieWalker link )'",
     "SPEECH OUTPUT: 'User heading level 3'",
     "SPEECH OUTPUT: 'Login link'",
     "SPEECH OUTPUT: 'Page heading level 3'",
     "SPEECH OUTPUT: 'Immutable Page'",
     "SPEECH OUTPUT: 'Info link'",
     "SPEECH OUTPUT: 'Attachments link'",
     "SPEECH OUTPUT: 'More Actions: combo box'",
     "SPEECH OUTPUT: 'GNOME World Wide heading level 3'",
     "SPEECH OUTPUT: 'GnomeWorldWide link image'",
     "SPEECH OUTPUT: 'Copyright © 2005, 2006, 2007 The GNOME Project link .",
     "Hosted by Red Hat link .'"]))

########################################################################
# Move to the location bar by pressing Control+L.  When it has focus
# type "about:blank" and press Return to restore the browser to the
# conditions at the test's start.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction("about:blank"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

# Just a little extra wait to let some events get through.
#
sequence.append(PauseAction(3000))

sequence.append(utils.AssertionSummaryAction())

sequence.start()
