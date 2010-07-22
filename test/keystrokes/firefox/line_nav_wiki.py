# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of line navigation output of Firefox on the Orca wiki.
Note that this is based on the following Firefox 3 build:
Gecko/2007122122 Minefield/3.0b3pre.  In addition, it is using
the current patch to bug 505102 to handle a significant change
made in the current Firefox.  The assertions in the test will
fail if your configuration is different.
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
# Down Arrow to the End.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'live.gnome.org h1 Search $l Titles Button Text Button'",
     "     VISIBLE:  'live.gnome.org h1 Search $l Titl', cursor=1",
     "SPEECH OUTPUT: 'live.gnome.org heading level 1 Search: text Search Titles button Text button'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Home RecentChanges FindPage HelpContents Orca'",
     "     VISIBLE:  'Home RecentChanges FindPage Help', cursor=1",
     "SPEECH OUTPUT: 'Home link RecentChanges link FindPage link HelpContents link Orca link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'en Español'",
     "     VISIBLE:  'en Español', cursor=1",
     "SPEECH OUTPUT: 'en Español link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'Home | Download/Installation | Configuration/Use | Accessible Applications | Mailing List \(Archives\) |'",
     "     VISIBLE:  'Home | Download/Installation | C', cursor=1",
     "SPEECH OUTPUT: 'Home link  | Download/Installation link  | Configuration/Use link  | Accessible Applications link  | Mailing List link  \( Archives link \) |'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  '| FAQ | DocIndex'",
     "     VISIBLE:  '| FAQ | DocIndex', cursor=1",
     "SPEECH OUTPUT: '| FAQ link  | DocIndex link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'Welcome to Orca! h1'",
     "     VISIBLE:  'Welcome to Orca! h1', cursor=1",
     "SPEECH OUTPUT: 'Welcome to Orca! heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BUG? - Why are we presenting this twice?",
     "BRAILLE LINE:  'Orca Logo Image'",
     "     VISIBLE:  'Orca Logo Image', cursor=1",
     "BRAILLE LINE:  'Orca Logo Image'",
     "     VISIBLE:  'Orca Logo Image', cursor=1",
     "SPEECH OUTPUT: 'Orca Logo link image'"
     "SPEECH OUTPUT: 'Orca Logo link image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'HOT HOT HOT: Notes on access to Firefox 3.0'",
     "     VISIBLE:  'HOT HOT HOT: Notes on access to ', cursor=1",
     "SPEECH OUTPUT: 'HOT HOT HOT: Notes on access to Firefox 3.0 link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'Contents'",
     "     VISIBLE:  'Contents', cursor=1",
     "SPEECH OUTPUT: 'Contents'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  '1. Welcome to Orca!'",
     "     VISIBLE:  '1. Welcome to Orca!', cursor=1",
     "SPEECH OUTPUT: '1. Welcome to Orca! link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  '2. About'",
     "     VISIBLE:  '2. About', cursor=1",
     "SPEECH OUTPUT: '2. About link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  '3. Audio Guides'",
     "     VISIBLE:  '3. Audio Guides', cursor=1",
     "SPEECH OUTPUT: '3. Audio Guides link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  '4. Download/Installation'",
     "     VISIBLE:  '4. Download/Installation', cursor=1",
     "SPEECH OUTPUT: '4. Download/Installation link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  '5. Configuration/Use'",
     "     VISIBLE:  '5. Configuration/Use', cursor=1",
     "SPEECH OUTPUT: '5. Configuration/Use link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  '6. Accessible Applications'",
     "     VISIBLE:  '6. Accessible Applications', cursor=1",
     "SPEECH OUTPUT: '6. Accessible Applications link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  '7. How Can I Help?'",
     "     VISIBLE:  '7. How Can I Help?', cursor=1",
     "SPEECH OUTPUT: '7. How Can I Help? link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  '8. More Information'",
     "     VISIBLE:  '8. More Information', cursor=1",
     "SPEECH OUTPUT: '8. More Information link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'About h1'",
     "     VISIBLE:  'About h1', cursor=1",
     "SPEECH OUTPUT: 'About heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'Orca is a free, open source, flexible, extensible, and powerful'",
     "     VISIBLE:  'Orca is a free, open source, fle', cursor=1",
     "SPEECH OUTPUT: 'Orca is a free, open source, flexible, extensible, and powerful'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'assistive technology for people with visual impairments. Using'",
     "     VISIBLE:  'assistive technology for people', cursor=1",
     "SPEECH OUTPUT: 'assistive technology for people with visual impairments. Using'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'various combinations of speech synthesis, braille, and'",
     "     VISIBLE:  'various combinations of speech s', cursor=1",
     "SPEECH OUTPUT: 'various combinations of speech synthesis, braille, and'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'magnification, Orca helps provide access to applications and'",
     "     VISIBLE:  'magnification, Orca helps provid', cursor=1",
     "SPEECH OUTPUT: 'magnification, Orca helps provide access to applications and'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'toolkits that support the AT-SPI (e.g., the GNOME desktop). The'",
     "     VISIBLE:  'toolkits that support the AT-SPI', cursor=1",
     "SPEECH OUTPUT: 'toolkits that support the AT-SPI (e.g., the GNOME desktop). The'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'development of Orca has been led by the Accessibility Program'",
     "     VISIBLE:  'development of Orca has been led', cursor=1",
     "SPEECH OUTPUT: 'development of Orca has been led by the Accessibility Program link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'Office of Sun Microsystems, Inc. with contributions from many'",
     "     VISIBLE:  'Office of Sun Microsystems, Inc.', cursor=1",
     "SPEECH OUTPUT: 'Office of Sun Microsystems, Inc. link  with contributions from many link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'community members.'",
     "     VISIBLE:  'community members.', cursor=1",
     "SPEECH OUTPUT: 'community members link .'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'The complete list of work to do, including bugs and feature requests,'",
     "     VISIBLE:  'The complete list of work to do,', cursor=1",
     "SPEECH OUTPUT: 'The complete list of work to do, including bugs and feature requests,'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'along with known problems in other components, is maintained in Bugzilla \(please see our notes on'",
     "     VISIBLE:  'along with known problems in oth', cursor=1",
     "SPEECH OUTPUT: 'along with known problems in other components, is maintained in Bugzilla link  \(please see our notes on link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'how we use Bugzilla\).'",
     "     VISIBLE:  'how we use Bugzilla\).', cursor=1",
     "SPEECH OUTPUT: 'how we use Bugzilla link \).'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'Please join and participate on the Orca mailing list (archives): it's a helpful, kind, and productive'",
     "     VISIBLE:  'Please join and participate on t', cursor=1",
     "SPEECH OUTPUT: 'Please join and participate on the Orca mailing list link  ( archives link ): it's a helpful, kind, and productive'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'environment composed of users and developers.'",
     "     VISIBLE:  'environment composed of users an', cursor=1",
     "SPEECH OUTPUT: 'environment composed of users and developers.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'Audio Guides h1'",
     "     VISIBLE:  'Audio Guides h1', cursor=1",
     "SPEECH OUTPUT: 'Audio Guides heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'Darragh Ó Héiligh has created several audio guides for Orca. This is a fantastic contribution'",
     "     VISIBLE:  'Darragh Ó Héiligh has created se', cursor=1",
     "SPEECH OUTPUT: 'Darragh Ó Héiligh link  has created several audio guides for Orca. This is a fantastic contribution'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  '\(THANKS!\)!!! The audio guides can be found at http://www.digitaldarragh.com/linuxat.asp and'",
     "     VISIBLE:  '\(THANKS!\)!!! The audio guides ca', cursor=1",
     "SPEECH OUTPUT: '\(THANKS!\)!!! The audio guides can be found at http://www.digitaldarragh.com/linuxat.asp link  and'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'include the following:'",
     "     VISIBLE:  'include the following:', cursor=1",
     "SPEECH OUTPUT: 'include the following:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  '• Walk through of the installation of Ubuntu 7.4. Very helpful tutorial'",
     "     VISIBLE:  '• Walk through of the installati', cursor=1",
     "SPEECH OUTPUT: '• Walk through of the installation of Ubuntu 7.4. Very helpful tutorial link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  '• Review of Fedora 7 and the Orca screen reader for the Gnome graphical desktop'",
     "     VISIBLE:  '• Review of Fedora 7 and the Orc', cursor=1",
     "SPEECH OUTPUT: '• Review of Fedora 7 and the Orca screen reader for the Gnome graphical desktop link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  '• Guide to installing the latest versions of Firefox and Orca'",
     "     VISIBLE:  '• Guide to installing the latest', cursor=1",
     "SPEECH OUTPUT: '• Guide to installing the latest versions of Firefox and Orca link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'Download/Installation h1'",
     "     VISIBLE:  'Download/Installation h1', cursor=1",
     "SPEECH OUTPUT: 'Download/Installation heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'As of GNOME 2.16, Orca is a part of the GNOME platform. As a result, Orca is already provided by'",
     "     VISIBLE:  'As of GNOME 2.16, Orca is a part', cursor=1",
     "SPEECH OUTPUT: 'As of GNOME 2.16, Orca is a part of the GNOME platform. As a result, Orca is already provided by'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'default on a number of operating system distributions, including Open Solaris and Ubuntu.'",
     "     VISIBLE:  'default on a number of operating', cursor=1",
     "SPEECH OUTPUT: 'default on a number of operating system distributions, including Open Solaris link  and Ubuntu link .'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'Please also refer to the Download/Installation page for detailed information on various distributions'",
     "     VISIBLE:  'Please also refer to the Downloa', cursor=1",
     "SPEECH OUTPUT: 'Please also refer to the Download/Installation page link  for detailed information on various distributions'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'as well as installing Orca directly from source.'",
     "     VISIBLE:  'as well as installing Orca direc', cursor=1",
     "SPEECH OUTPUT: 'as well as installing Orca directly from source.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'Configuration/Use h1'",
     "     VISIBLE:  'Configuration/Use h1', cursor=1",
     "SPEECH OUTPUT: 'Configuration/Use heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'The command to run orca is orca. You can enter this command by pressing Alt+F2 when logged in,'",
     "     VISIBLE:  'The command to run orca is orca.', cursor=1",
     "SPEECH OUTPUT: 'The command to run orca is orca. You can enter this command by pressing Alt+F2 when logged in,'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'waiting for a second or so, then typing orca and pressing return. Orca is designed to present'",
     "     VISIBLE:  'waiting for a second or so, then', cursor=1",
     "SPEECH OUTPUT: 'waiting for a second or so, then typing orca and pressing return. Orca is designed to present'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'information as you navigate the desktop using the built-in navigation mechanisms of GNOME.'",
     "     VISIBLE:  'information as you navigate the ', cursor=1",
     "SPEECH OUTPUT: 'information as you navigate the desktop using the built-in navigation mechanisms of GNOME link .'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'These navigation mechanisms are consistent across most desktop applications.'",
     "     VISIBLE:  'These navigation mechanisms are ', cursor=1",
     "SPEECH OUTPUT: 'These navigation mechanisms are consistent across most desktop applications.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'You may sometimes wish to control Orca itself, such as bringing up the Orca Configuration GUI'",
     "     VISIBLE:  'You may sometimes wish to contro', cursor=1",
     "SPEECH OUTPUT: 'You may sometimes wish to control Orca itself, such as bringing up the Orca Configuration GUI link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  '(accessed by pressing Insert+Space when Orca is running) and for using flat review mode to examine'",
     "     VISIBLE:  '(accessed by pressing Insert+Spa', cursor=1",
     "SPEECH OUTPUT: '(accessed by pressing Insert+Space when Orca is running) and for using flat review mode to examine'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'a window. Refer to Orca Keyboard Commands (Laptop Layout) for more information on Orca-specific'",
     "     VISIBLE:  'a window. Refer to Orca Keyboard', cursor=1",
     "SPEECH OUTPUT: 'a window. Refer to Orca Keyboard Commands link (Laptop Layout) link  for more information on Orca-specific'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'keyboard commands. The Orca Configuration GUI also includes a \"Key Bindings\" tab that allows'",
     "     VISIBLE:  'keyboard commands. The Orca Conf', cursor=1",
     "SPEECH OUTPUT: 'keyboard commands. The Orca Configuration GUI link  also includes a \"Key Bindings\" tab that allows'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'you to get a complete list of Orca key bindings.'",
     "     VISIBLE:  'you to get a complete list of Or', cursor=1",
     "SPEECH OUTPUT: 'you to get a complete list of Orca key bindings.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Please also refer to the Configuration/Use page for detailed information.'",
     "     VISIBLE:  'Please also refer to the Configu', cursor=1",
     "SPEECH OUTPUT: 'Please also refer to the Configuration/Use page link  for detailed information.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Accessible Applications h1'",
     "     VISIBLE:  'Accessible Applications h1', cursor=1",
     "SPEECH OUTPUT: 'Accessible Applications heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Orca is designed to work with applications and toolkits that support the assistive technology service'",
     "     VISIBLE:  'Orca is designed to work with ap', cursor=1",
     "SPEECH OUTPUT: 'Orca is designed to work with applications and toolkits that support the assistive technology service'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'provider interface (AT-SPI). This includes the GNOME desktop and its applications, OpenOffice,'",
     "     VISIBLE:  'provider interface (AT-SPI). Thi', cursor=1",
     "SPEECH OUTPUT: 'provider interface (AT-SPI). This includes the GNOME desktop and its applications, OpenOffice link ,'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Firefox, and the Java platform. Some applications work better than others, however, and the Orca'",
     "     VISIBLE:  'Firefox, and the Java platform. ', cursor=1",
     "SPEECH OUTPUT: 'Firefox, and the Java platform. Some applications work better than others, however, and the Orca'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'community continually works to provide compelling access to more and more applications.'",
     "     VISIBLE:  'community continually works to p', cursor=1",
     "SPEECH OUTPUT: 'community continually works to provide compelling access to more and more applications.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'On the Accessible Applications page, you will find a growing list of information regarding various'",
     "     VISIBLE:  'On the Accessible Applications p', cursor=1",
     "SPEECH OUTPUT: 'On the Accessible Applications page link , you will find a growing list of information regarding various'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'applications that can be accessed with Orca as well as tips and tricks for using them. The list is not to'",
     "     VISIBLE:  'applications that can be accesse', cursor=1",
     "SPEECH OUTPUT: 'applications that can be accessed with Orca as well as tips and tricks for using them. The list is not to'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'be a conclusive list of all applications. Rather, the goal is to provide a repository within which users'",
     "     VISIBLE:  'be a conclusive list of all appl', cursor=1",
     "SPEECH OUTPUT: 'be a conclusive list of all applications. Rather, the goal is to provide a repository within which users'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'can share experiences regarding applications they have tested.'",
     "     VISIBLE:  'can share experiences regarding ', cursor=1",
     "SPEECH OUTPUT: 'can share experiences regarding applications they have tested.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'See also the Application Specific Settings page for how to configure settings specific to an'",
     "     VISIBLE:  'See also the Application Specifi', cursor=1",
     "SPEECH OUTPUT: 'See also the Application Specific Settings link  page for how to configure settings specific to an'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'application.'",
     "     VISIBLE:  'application.', cursor=1",
     "SPEECH OUTPUT: 'application.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Please also refer to the Accessible Applications page for detailed information.'",
     "     VISIBLE:  'Please also refer to the Accessi', cursor=1",
     "SPEECH OUTPUT: 'Please also refer to the Accessible Applications page link  for detailed information.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'How Can I Help? h1'",
     "     VISIBLE:  'How Can I Help? h1', cursor=1",
     "SPEECH OUTPUT: 'How Can I Help? heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'There's a bunch you can do! Please refer to the How Can I Help page for detailed information.'",
     "     VISIBLE:  'There's a bunch you can do! Plea', cursor=1",
     "SPEECH OUTPUT: 'There's a bunch you can do! Please refer to the How Can I Help page link  for detailed information.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'More Information h1'",
     "     VISIBLE:  'More Information h1', cursor=1",
     "SPEECH OUTPUT: 'More Information heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '• Frequently Asked Questions: FAQ'",
     "     VISIBLE:  '• Frequently Asked Questions: FA', cursor=1",
     "SPEECH OUTPUT: '• Frequently Asked Questions: FAQ link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '• Mailing list: orca-list@gnome.org \(Archives\)'",
     "     VISIBLE:  '• Mailing list: orca-list@gnome.', cursor=1",
     "SPEECH OUTPUT: '• Mailing list: orca-list@gnome.org link  \( Archives link \)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '• Bug database: GNOME Bug Tracking System \(Bugzilla\) \(current bug list\)'",
     "     VISIBLE:  '• Bug database: GNOME Bug Tracki', cursor=1",
     "SPEECH OUTPUT: '• Bug database: GNOME Bug Tracking System \(Bugzilla\) link  \( current bug list link \)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '• Design documents: Orca Documentation Series'",
     "     VISIBLE:  '• Design documents: Orca Documen', cursor=1",
     "SPEECH OUTPUT: '• Design documents: Orca Documentation Series link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '• Dive Into Python, Mark Pilgrim'",
     "     VISIBLE:  '• Dive Into Python, Mark Pilgrim', cursor=1",
     "SPEECH OUTPUT: '• Dive Into Python, Mark Pilgrim link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '• Python in a Nutshell, Alex Martelli'",
     "     VISIBLE:  '• Python in a Nutshell, Alex Mar', cursor=1",
     "SPEECH OUTPUT: '• Python in a Nutshell, Alex Martelli link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '• Python Pocket Reference, Mark Lutz'",
     "     VISIBLE:  '• Python Pocket Reference, Mark ', cursor=1",
     "SPEECH OUTPUT: '• Python Pocket Reference, Mark Lutz link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Separator'",
     "     VISIBLE:  'Separator', cursor=1",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'The information on this page and the other Orca-related pages on this site are distributed in the hope'",
     "     VISIBLE:  'The information on this page and', cursor=1",
     "SPEECH OUTPUT: 'The information on this page and the other Orca-related pages on this site are distributed in the hope'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of'",
     "     VISIBLE:  'that it will be useful, but WITH', cursor=1",
     "SPEECH OUTPUT: 'that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.'",
     "     VISIBLE:  'MERCHANTABILITY or FITNESS FOR A', cursor=1",
     "SPEECH OUTPUT: 'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Separator'",
     "     VISIBLE:  'Separator', cursor=1",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'CategoryAccessibility'",
     "     VISIBLE:  'CategoryAccessibility', cursor=1",
     "SPEECH OUTPUT: 'CategoryAccessibility link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Orca \(last edited 2007-12-07 22:09:22 by WillieWalker\)'",
     "     VISIBLE:  'Orca \(last edited 2007-12-07 22:', cursor=1",
     "SPEECH OUTPUT: 'Orca \(last edited 2007-12-07 22:09:22 by WillieWalker link \)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'User h3'",
     "     VISIBLE:  'User h3', cursor=1",
     "SPEECH OUTPUT: 'User heading level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Login'",
     "     VISIBLE:  'Login', cursor=1",
     "SPEECH OUTPUT: 'Login link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Page h3'",
     "     VISIBLE:  'Page h3', cursor=1",
     "SPEECH OUTPUT: 'Page heading level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Immutable Page'",
     "     VISIBLE:  'Immutable Page', cursor=1",
     "SPEECH OUTPUT: 'Immutable Page'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Info'",
     "     VISIBLE:  'Info', cursor=1",
     "SPEECH OUTPUT: 'Info link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Attachments'",
     "     VISIBLE:  'Attachments', cursor=1",
     "SPEECH OUTPUT: 'Attachments link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BUG? - In 3.1 we aren't presenting More Actions at times; other times we are",
     "BRAILLE LINE:  'Combo'",
     "     VISIBLE:  'Combo', cursor=1",
     "SPEECH OUTPUT: 'combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'GNOME World Wide h3'",
     "     VISIBLE:  'GNOME World Wide h3', cursor=1",
     "SPEECH OUTPUT: 'GNOME World Wide heading level 3'"]))

########################################################################
# Up Arrow to the Top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BUG? - In 3.1 we aren't presenting More Actions at times; other times we are",
     "BRAILLE LINE:  'Combo'",
     "     VISIBLE:  'Combo', cursor=1",
     "SPEECH OUTPUT: 'combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Attachments'",
     "     VISIBLE:  'Attachments', cursor=1",
     "SPEECH OUTPUT: 'Attachments link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Info'",
     "     VISIBLE:  'Info', cursor=1",
     "SPEECH OUTPUT: 'Info link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Immutable Page'",
     "     VISIBLE:  'Immutable Page', cursor=1",
     "SPEECH OUTPUT: 'Immutable Page'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Page h3'",
     "     VISIBLE:  'Page h3', cursor=1",
     "SPEECH OUTPUT: 'Page heading level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Login'",
     "     VISIBLE:  'Login', cursor=1",
     "SPEECH OUTPUT: 'Login link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'User h3'",
     "     VISIBLE:  'User h3', cursor=1",
     "SPEECH OUTPUT: 'User heading level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Orca \(last edited 2007-12-07 22:09:22 by WillieWalker\)'",
     "     VISIBLE:  'Orca \(last edited 2007-12-07 22:', cursor=1",
     "SPEECH OUTPUT: 'Orca \(last edited 2007-12-07 22:09:22 by WillieWalker link \)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'CategoryAccessibility'",
     "     VISIBLE:  'CategoryAccessibility', cursor=1",
     "SPEECH OUTPUT: 'CategoryAccessibility link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Separator'",
     "     VISIBLE:  'Separator', cursor=1",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.'",
     "     VISIBLE:  'MERCHANTABILITY or FITNESS FOR A', cursor=1",
     "SPEECH OUTPUT: 'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of'",
     "     VISIBLE:  'that it will be useful, but WITH', cursor=1",
     "SPEECH OUTPUT: 'that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'The information on this page and the other Orca-related pages on this site are distributed in the hope'",
     "     VISIBLE:  'The information on this page and', cursor=1",
     "SPEECH OUTPUT: 'The information on this page and the other Orca-related pages on this site are distributed in the hope'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Separator'",
     "     VISIBLE:  'Separator', cursor=1",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '• Python Pocket Reference, Mark Lutz'",
     "     VISIBLE:  '• Python Pocket Reference, Mark ', cursor=1",
     "SPEECH OUTPUT: '• Python Pocket Reference, Mark Lutz link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '• Python in a Nutshell, Alex Martelli'",
     "     VISIBLE:  '• Python in a Nutshell, Alex Mar', cursor=1",
     "SPEECH OUTPUT: '• Python in a Nutshell, Alex Martelli link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '• Dive Into Python, Mark Pilgrim'",
     "     VISIBLE:  '• Dive Into Python, Mark Pilgrim', cursor=1",
     "SPEECH OUTPUT: '• Dive Into Python, Mark Pilgrim link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '• Design documents: Orca Documentation Series'",
     "     VISIBLE:  '• Design documents: Orca Documen', cursor=1",
     "SPEECH OUTPUT: '• Design documents: Orca Documentation Series link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '• Bug database: GNOME Bug Tracking System \(Bugzilla\) \(current bug list\)'",
     "     VISIBLE:  '• Bug database: GNOME Bug Tracki', cursor=1",
     "SPEECH OUTPUT: '• Bug database: GNOME Bug Tracking System \(Bugzilla\) link  \( current bug list link \)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '• Mailing list: orca-list@gnome.org \(Archives\)'",
     "     VISIBLE:  '• Mailing list: orca-list@gnome.', cursor=1",
     "SPEECH OUTPUT: '• Mailing list: orca-list@gnome.org link  \( Archives link \)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '• Frequently Asked Questions: FAQ'",
     "     VISIBLE:  '• Frequently Asked Questions: FA', cursor=1",
     "SPEECH OUTPUT: '• Frequently Asked Questions: FAQ link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'More Information h1'",
     "     VISIBLE:  'More Information h1', cursor=1",
     "SPEECH OUTPUT: 'More Information heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'There's a bunch you can do! Please refer to the How Can I Help page for detailed information.'",
     "     VISIBLE:  'There's a bunch you can do! Plea', cursor=1",
     "SPEECH OUTPUT: 'There's a bunch you can do! Please refer to the How Can I Help page link  for detailed information.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'How Can I Help? h1'",
     "     VISIBLE:  'How Can I Help? h1', cursor=1",
     "SPEECH OUTPUT: 'How Can I Help? heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Please also refer to the Accessible Applications page for detailed information.'",
     "     VISIBLE:  'Please also refer to the Accessi', cursor=1",
     "SPEECH OUTPUT: 'Please also refer to the Accessible Applications page link  for detailed information.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'application.'",
     "     VISIBLE:  'application.', cursor=1",
     "SPEECH OUTPUT: 'application.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'See also the Application Specific Settings page for how to configure settings specific to an'",
     "     VISIBLE:  'See also the Application Specifi', cursor=1",
     "SPEECH OUTPUT: 'See also the Application Specific Settings link  page for how to configure settings specific to an'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'can share experiences regarding applications they have tested.'",
     "     VISIBLE:  'can share experiences regarding ', cursor=1",
     "SPEECH OUTPUT: 'can share experiences regarding applications they have tested.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'be a conclusive list of all applications. Rather, the goal is to provide a repository within which users'",
     "     VISIBLE:  'be a conclusive list of all appl', cursor=1",
     "SPEECH OUTPUT: 'be a conclusive list of all applications. Rather, the goal is to provide a repository within which users'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'applications that can be accessed with Orca as well as tips and tricks for using them. The list is not to'",
     "     VISIBLE:  'applications that can be accesse', cursor=1",
     "SPEECH OUTPUT: 'applications that can be accessed with Orca as well as tips and tricks for using them. The list is not to'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'On the Accessible Applications page, you will find a growing list of information regarding various'",
     "     VISIBLE:  'On the Accessible Applications p', cursor=1",
     "SPEECH OUTPUT: 'On the Accessible Applications page link , you will find a growing list of information regarding various'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'community continually works to provide compelling access to more and more applications.'",
     "     VISIBLE:  'community continually works to p', cursor=1",
     "SPEECH OUTPUT: 'community continually works to provide compelling access to more and more applications.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Firefox, and the Java platform. Some applications work better than others, however, and the Orca'",
     "     VISIBLE:  'Firefox, and the Java platform. ', cursor=1",
     "SPEECH OUTPUT: 'Firefox, and the Java platform. Some applications work better than others, however, and the Orca'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'provider interface \(AT-SPI\). This includes the GNOME desktop and its applications, OpenOffice,'",
     "     VISIBLE:  'provider interface \(AT-SPI\). Thi', cursor=1",
     "SPEECH OUTPUT: 'provider interface \(AT-SPI\). This includes the GNOME desktop and its applications, OpenOffice link ,'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Orca is designed to work with applications and toolkits that support the assistive technology service'",
     "     VISIBLE:  'Orca is designed to work with ap', cursor=1",
     "SPEECH OUTPUT: 'Orca is designed to work with applications and toolkits that support the assistive technology service'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Accessible Applications h1'",
     "     VISIBLE:  'Accessible Applications h1', cursor=1",
     "SPEECH OUTPUT: 'Accessible Applications heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Please also refer to the Configuration/Use page for detailed information.'",
     "     VISIBLE:  'Please also refer to the Configu', cursor=1",
     "SPEECH OUTPUT: 'Please also refer to the Configuration/Use page link  for detailed information.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'you to get a complete list of Orca key bindings.'",
     "     VISIBLE:  'you to get a complete list of Or', cursor=1",
     "SPEECH OUTPUT: 'you to get a complete list of Orca key bindings.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'keyboard commands. The Orca Configuration GUI also includes a \"Key Bindings\" tab that allows'",
     "     VISIBLE:  'keyboard commands. The Orca Conf', cursor=1",
     "SPEECH OUTPUT: 'keyboard commands. The Orca Configuration GUI link  also includes a \"Key Bindings\" tab that allows'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'a window. Refer to Orca Keyboard Commands \(Laptop Layout\) for more information on Orca-specific'",
     "     VISIBLE:  'a window. Refer to Orca Keyboard', cursor=1",
     "SPEECH OUTPUT: 'a window. Refer to Orca Keyboard Commands link \(Laptop Layout\) link  for more information on Orca-specific'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  '\(accessed by pressing Insert\+Space when Orca is running\) and for using flat review mode to examine'",
     "     VISIBLE:  '\(accessed by pressing Insert\+Spa', cursor=1",
     "SPEECH OUTPUT: '\(accessed by pressing Insert\+Space when Orca is running\) and for using flat review mode to examine'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'You may sometimes wish to control Orca itself, such as bringing up the Orca Configuration GUI'",
     "     VISIBLE:  'You may sometimes wish to contro', cursor=1",
     "SPEECH OUTPUT: 'You may sometimes wish to control Orca itself, such as bringing up the Orca Configuration GUI link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'navigation mechanisms are consistent across most desktop applications.'",
     "     VISIBLE:  'navigation mechanisms are consis', cursor=1",
     "SPEECH OUTPUT: 'navigation mechanisms are consistent across most desktop applications.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'information as you navigate the desktop using the built-in navigation mechanisms of GNOME. These'",
     "     VISIBLE:  'information as you navigate the ', cursor=1",
     "SPEECH OUTPUT: 'information as you navigate the desktop using the built-in navigation mechanisms of GNOME link . These'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'waiting for a second or so, then typing orca and pressing return. Orca is designed to present'",
     "     VISIBLE:  'waiting for a second or so, then', cursor=1",
     "SPEECH OUTPUT: 'waiting for a second or so, then typing orca and pressing return. Orca is designed to present'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'The command to run orca is orca. You can enter this command by pressing Alt+F2 when logged in,'",
     "     VISIBLE:  'The command to run orca is orca.', cursor=1",
     "SPEECH OUTPUT: 'The command to run orca is orca. You can enter this command by pressing Alt+F2 when logged in,'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'Configuration/Use h1'",
     "     VISIBLE:  'Configuration/Use h1', cursor=1",
     "SPEECH OUTPUT: 'Configuration/Use heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'as well as installing Orca directly from source.'",
     "     VISIBLE:  'as well as installing Orca direc', cursor=1",
     "SPEECH OUTPUT: 'as well as installing Orca directly from source.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'Please also refer to the Download/Installation page for detailed information on various distributions'",
     "     VISIBLE:  'Please also refer to the Downloa', cursor=1",
     "SPEECH OUTPUT: 'Please also refer to the Download/Installation page link  for detailed information on various distributions'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'default on a number of operating system distributions, including Open Solaris and Ubuntu.'",
     "     VISIBLE:  'default on a number of operating', cursor=1",
     "SPEECH OUTPUT: 'default on a number of operating system distributions, including Open Solaris link  and Ubuntu link .'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'As of GNOME 2.16, Orca is a part of the GNOME platform. As a result, Orca is already provided by'",
     "     VISIBLE:  'As of GNOME 2.16, Orca is a part', cursor=1",
     "SPEECH OUTPUT: 'As of GNOME 2.16, Orca is a part of the GNOME platform. As a result, Orca is already provided by'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'Download/Installation h1'",
     "     VISIBLE:  'Download/Installation h1', cursor=1",
     "SPEECH OUTPUT: 'Download/Installation heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  '• Guide to installing the latest versions of Firefox and Orca'",
     "     VISIBLE:  '• Guide to installing the latest', cursor=1",
     "SPEECH OUTPUT: '• Guide to installing the latest versions of Firefox and Orca link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  '• Review of Fedora 7 and the Orca screen reader for the Gnome graphical desktop'",
     "     VISIBLE:  '• Review of Fedora 7 and the Orc', cursor=1",
     "SPEECH OUTPUT: '• Review of Fedora 7 and the Orca screen reader for the Gnome graphical desktop link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  '• Walk through of the installation of Ubuntu 7.4. Very helpful tutorial'",
     "     VISIBLE:  '• Walk through of the installati', cursor=1",
     "SPEECH OUTPUT: '• Walk through of the installation of Ubuntu 7.4. Very helpful tutorial link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'include the following:'",
     "     VISIBLE:  'include the following:', cursor=1",
     "SPEECH OUTPUT: 'include the following:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  '\(THANKS!\)!!! The audio guides can be found at http://www.digitaldarragh.com/linuxat.asp and'",
     "     VISIBLE:  '\(THANKS!\)!!! The audio guides ca', cursor=1",
     "SPEECH OUTPUT: '\(THANKS!\)!!! The audio guides can be found at http://www.digitaldarragh.com/linuxat.asp link  and'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'Darragh Ó Héiligh has created several audio guides for Orca. This is a fantastic contribution'",
     "     VISIBLE:  'Darragh Ó Héiligh has created se', cursor=1",
     "SPEECH OUTPUT: 'Darragh Ó Héiligh link  has created several audio guides for Orca. This is a fantastic contribution'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'Audio Guides h1'",
     "     VISIBLE:  'Audio Guides h1', cursor=1",
     "SPEECH OUTPUT: 'Audio Guides heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'environment composed of users and developers.'",
     "     VISIBLE:  'environment composed of users an', cursor=1",
     "SPEECH OUTPUT: 'environment composed of users and developers.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'Please join and participate on the Orca mailing list \(archives\): it's a helpful, kind, and productive'",
     "     VISIBLE:  'Please join and participate on t', cursor=1",
     "SPEECH OUTPUT: 'Please join and participate on the Orca mailing list link  \( archives link \): it's a helpful, kind, and productive'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  '" + bugzillaStringBraille + "( |)" + "how we use Bugzilla\).'",
     "     VISIBLE:  '" + bugzillaStringVisible + "', cursor=1",
     "SPEECH OUTPUT: '" + bugzillaStringSpeech + "( |)" + "how we use Bugzilla link \).'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'along with known problems in other components, is maintained in" + "( |)" + bugzillaStringBraille + "'",
     "     VISIBLE:  'along with known problems in oth', cursor=1",
     "SPEECH OUTPUT: 'along with known problems in other components, is maintained in" + "( |)" + bugzillaStringSpeech + "( link|)'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'The complete list of work to do, including bugs and feature requests,'",
     "     VISIBLE:  'The complete list of work to do,', cursor=1",
     "SPEECH OUTPUT: 'The complete list of work to do, including bugs and feature requests,'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'with contributions from many community members.'",
     "     VISIBLE:  'with contributions from many com', cursor=1",
     "SPEECH OUTPUT: 'with contributions from many community members link .'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'been led by the Accessibility Program Office of Sun Microsystems, Inc.'",
     "     VISIBLE:  'been led by the Accessibility Pr', cursor=1",
     "SPEECH OUTPUT: 'been led by the Accessibility Program Office of Sun Microsystems, Inc. link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'AT-SPI (e.g., the GNOME desktop). The development of Orca has'",
     "     VISIBLE:  'AT-SPI (e.g., the GNOME desktop)', cursor=1",
     "SPEECH OUTPUT: 'AT-SPI (e.g., the GNOME desktop). The development of Orca has'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'helps provide access to applications and toolkits that support the'",
     "     VISIBLE:  'helps provide access to applicat', cursor=1",
     "SPEECH OUTPUT: 'helps provide access to applications and toolkits that support the'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'combinations of speech synthesis, braille, and magnification, Orca'",
     "     VISIBLE:  'combinations of speech synthesis', cursor=1",
     "SPEECH OUTPUT: 'combinations of speech synthesis, braille, and magnification, Orca'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'technology for people with visual impairments. Using various'",
     "     VISIBLE:  'technology for people with visua', cursor=1",
     "SPEECH OUTPUT: 'technology for people with visual impairments. Using various'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'Orca is a free, open source, flexible, extensible, and powerful assistive'",
     "     VISIBLE:  'Orca is a free, open source, fle', cursor=1",
     "SPEECH OUTPUT: 'Orca is a free, open source, flexible, extensible, and powerful assistive'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'About h1'",
     "     VISIBLE:  'About h1', cursor=1",
     "SPEECH OUTPUT: 'About heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  '8. More Information'",
     "     VISIBLE:  '8. More Information', cursor=1",
     "SPEECH OUTPUT: '8. More Information link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  '7. How Can I Help?'",
     "     VISIBLE:  '7. How Can I Help?', cursor=1",
     "SPEECH OUTPUT: '7. How Can I Help? link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  '6. Accessible Applications'",
     "     VISIBLE:  '6. Accessible Applications', cursor=1",
     "SPEECH OUTPUT: '6. Accessible Applications link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  '5. Configuration/Use'",
     "     VISIBLE:  '5. Configuration/Use', cursor=1",
     "SPEECH OUTPUT: '5. Configuration/Use link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  '4. Download/Installation'",
     "     VISIBLE:  '4. Download/Installation', cursor=1",
     "SPEECH OUTPUT: '4. Download/Installation link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  '3. Audio Guides'",
     "     VISIBLE:  '3. Audio Guides', cursor=1",
     "SPEECH OUTPUT: '3. Audio Guides link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  '2. About'",
     "     VISIBLE:  '2. About', cursor=1",
     "SPEECH OUTPUT: '2. About link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  '1. Welcome to Orca!'",
     "     VISIBLE:  '1. Welcome to Orca!', cursor=1",
     "SPEECH OUTPUT: '1. Welcome to Orca! link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'Contents'",
     "     VISIBLE:  'Contents', cursor=1",
     "SPEECH OUTPUT: 'Contents'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'HOT HOT HOT: Notes on access to Firefox 3.0'",
     "     VISIBLE:  'HOT HOT HOT: Notes on access to ', cursor=1",
     "SPEECH OUTPUT: 'HOT HOT HOT: Notes on access to Firefox 3.0 link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'Orca Logo Image'",
     "     VISIBLE:  'Orca Logo Image', cursor=1",
     "SPEECH OUTPUT: 'Orca Logo link image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'Welcome to Orca! h1'",
     "     VISIBLE:  'Welcome to Orca! h1', cursor=1",
     "SPEECH OUTPUT: 'Welcome to Orca! heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'FAQ | DocIndex'",
     "     VISIBLE:  'FAQ | DocIndex', cursor=1",
     "SPEECH OUTPUT: 'FAQ link | DocIndex link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'Home | Download/Installation | Configuration/Use | Accessible Applications | Mailing List \(Archives\) |'",
     "     VISIBLE:  'Home | Download/Installation | Co', cursor=1",
     "SPEECH OUTPUT: 'Home link  | Download/Installation link  | Configuration/Use link  | Accessible Applications link  | Mailing List link  \( archives link \) |'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'en Español'",
     "     VISIBLE:  'en Español', cursor=1",
     "SPEECH OUTPUT: 'en Español link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Home RecentChanges FindPage HelpContents Orca'",
     "     VISIBLE:  'Home RecentChanges FindPage Help', cursor=1",
     "SPEECH OUTPUT: 'Home link RecentChanges link FindPage link HelpContents link Orca link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'live.gnome.org h1 Search $l Titles Button Text Button'",
     "     VISIBLE:  'live.gnome.org h1 Search $l Titl', cursor=1",
     "SPEECH OUTPUT: 'live.gnome.org heading level 1 Search: text Search Titles button grayed Text button grayed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Home News Projects Art Support Development Community'",
     "     VISIBLE:  'Home News Projects Art Support D', cursor=1",
     "SPEECH OUTPUT: 'Home link News link Projects link Art link Support link Development link Community link'"]))

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
