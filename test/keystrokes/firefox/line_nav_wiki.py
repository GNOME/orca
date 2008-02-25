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
sequence.append(WaitForWindowActivate("Minefield",None))

########################################################################
# Load the local "wiki" test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus("Location", acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "orca-wiki.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

sequence.append(WaitForFocus("Orca - GNOME Live!",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file", 
    ["BRAILLE LINE:  'Home Link News Link Projects Link Art Link Support Link Development Link Community Link'",
     "     VISIBLE:  'Home Link News Link Projects Lin', cursor=1",
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
     "SPEECH OUTPUT: 'live.gnome.org heading  '",
     "SPEECH OUTPUT: 'level 1'",
     "SPEECH OUTPUT: 'text Search Titles button grayed Text button grayed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Home Link RecentChanges Link FindPage Link HelpContents Link Orca Link'",
     "     VISIBLE:  'Home Link RecentChanges Link Fin', cursor=1",
     "SPEECH OUTPUT: 'Home link RecentChanges link FindPage link HelpContents link Orca link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'en Español Link'",
     "     VISIBLE:  'en Español Link', cursor=1",
     "SPEECH OUTPUT: 'en Español link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'Home Link | Download/Installation Link  | Configuration/Use Link  | Accessible Applications Link  | Mailing List Link'",
     "     VISIBLE:  'Home Link | Download/Installatio', cursor=1",
     "SPEECH OUTPUT: 'Home link | Download/Installation link  | Configuration/Use link  | Accessible Applications link  | Mailing List link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  '( Archives Link ) | FAQ Link  | DocIndex Link'",
     "     VISIBLE:  '( Archives Link ) | FAQ Link  | ', cursor=1",
     "SPEECH OUTPUT: '( Archives link ) | FAQ link  | DocIndex link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'Welcome to Orca! h1'",
     "     VISIBLE:  'Welcome to Orca! h1', cursor=1",
     "SPEECH OUTPUT: 'Welcome to Orca! heading  '",
     "SPEECH OUTPUT: 'level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'Orca Logo Link Image'",
     "     VISIBLE:  'Orca Logo Link Image', cursor=1",
     "SPEECH OUTPUT: 'Orca Logo link image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'HOT HOT HOT: Notes on access to Firefox 3.0 Link'",
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
    ["BRAILLE LINE:  '1. Welcome to Orca! Link'",
     "     VISIBLE:  '1. Welcome to Orca! Link', cursor=1",
     "SPEECH OUTPUT: '1. Welcome to Orca! link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  '2. About Link'",
     "     VISIBLE:  '2. About Link', cursor=1",
     "SPEECH OUTPUT: '2. About link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  '3. Audio Guides Link'",
     "     VISIBLE:  '3. Audio Guides Link', cursor=1",
     "SPEECH OUTPUT: '3. Audio Guides link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  '4. Download/Installation Link'",
     "     VISIBLE:  '4. Download/Installation Link', cursor=1",
     "SPEECH OUTPUT: '4. Download/Installation link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  '5. Configuration/Use Link'",
     "     VISIBLE:  '5. Configuration/Use Link', cursor=1",
     "SPEECH OUTPUT: '5. Configuration/Use link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  '6. Accessible Applications Link'",
     "     VISIBLE:  '6. Accessible Applications Link', cursor=1",
     "SPEECH OUTPUT: '6. Accessible Applications link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  '7. How Can I Help? Link'",
     "     VISIBLE:  '7. How Can I Help? Link', cursor=1",
     "SPEECH OUTPUT: '7. How Can I Help? link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  '8. More Information Link'",
     "     VISIBLE:  '8. More Information Link', cursor=1",
     "SPEECH OUTPUT: '8. More Information link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'About h1'",
     "     VISIBLE:  'About h1', cursor=1",
     "SPEECH OUTPUT: 'About heading  '",
     "SPEECH OUTPUT: 'level 1'"]))

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
     "     VISIBLE:  'assistive technology for people ', cursor=1",
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
    ["BRAILLE LINE:  'toolkits that support the AT-SPI (e.g., the GNOME desktop).'",
     "     VISIBLE:  'toolkits that support the AT-SPI', cursor=1",
     "SPEECH OUTPUT: 'toolkits that support the AT-SPI (e.g., the GNOME desktop).'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'The development of Orca has been led by the Accessibility Link'",
     "     VISIBLE:  'The development of Orca has been', cursor=1",
     "SPEECH OUTPUT: 'The development of Orca has been led by the Accessibility link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'Program Office of Sun Microsystems, Inc. Link with contributions Link'",
     "     VISIBLE:  'Program Office of Sun Microsyste', cursor=1",
     "SPEECH OUTPUT: 'Program Office of Sun Microsystems, Inc. link with contributions link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'from many community members Link .'",
     "     VISIBLE:  'from many community members Link', cursor=1",
     "SPEECH OUTPUT: 'from many community members link .'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'The complete list of work to do, including bugs and feature'",
     "     VISIBLE:  'The complete list of work to do,', cursor=1",
     "SPEECH OUTPUT: 'The complete list of work to do, including bugs and feature'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'requests, along with known problems in other components, is maintained in Bugzilla Link'",
     "     VISIBLE:  'requests, along with known probl', cursor=1",
     "SPEECH OUTPUT: 'requests, along with known problems in other components, is maintained in Bugzilla link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  '(please see our notes on how we use Bugzilla Link ).'",
     "     VISIBLE:  '(please see our notes on how we ', cursor=1",
     "SPEECH OUTPUT: '(please see our notes on how we use Bugzilla link ).'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'Please join and participate on the Orca mailing list Link  ( archives Link ): it's a helpful, kind, and'",
     "     VISIBLE:  'Please join and participate on t', cursor=1",
     "SPEECH OUTPUT: 'Please join and participate on the Orca mailing list link  ( archives link ): it's a helpful, kind, and'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'productive environment composed of users and developers.'",
     "     VISIBLE:  'productive environment composed ', cursor=1",
     "SPEECH OUTPUT: 'productive environment composed of users and developers.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'Audio Guides h1'",
     "     VISIBLE:  'Audio Guides h1', cursor=1",
     "SPEECH OUTPUT: 'Audio Guides heading  '",
     "SPEECH OUTPUT: 'level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'Darragh Ó Héiligh Link has created several audio guides for Orca. This is a fantastic contribution'",
     "     VISIBLE:  'Darragh Ó Héiligh Link has cre', cursor=1",
     "SPEECH OUTPUT: 'Darragh Ó Héiligh link has created several audio guides for Orca. This is a fantastic contribution'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  '(THANKS!)!!! The audio guides can be found at http://www.digitaldarragh.com/linuxat.asp Link'",
     "     VISIBLE:  '(THANKS!)!!! The audio guides ca', cursor=1",
     "SPEECH OUTPUT: '(THANKS!)!!! The audio guides can be found at http://www.digitaldarragh.com/linuxat.asp link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'and include the following:'",
     "     VISIBLE:  'and include the following:', cursor=1",
     "SPEECH OUTPUT: 'and include the following:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  '• Walk through of the installation of Ubuntu 7.4. Very helpful tutorial Link'",
     "     VISIBLE:  '• Walk through of the installa', cursor=1",
     "SPEECH OUTPUT: '• Walk through of the installation of Ubuntu 7.4. Very helpful tutorial link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  '• Review of Fedora 7 and the Orca screen reader for the Gnome graphical desktop Link'",
     "     VISIBLE:  '• Review of Fedora 7 and the O', cursor=1",
     "SPEECH OUTPUT: '• Review of Fedora 7 and the Orca screen reader for the Gnome graphical desktop link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  '• Guide to installing the latest versions of Firefox and Orca Link'",
     "     VISIBLE:  '• Guide to installing the late', cursor=1",
     "SPEECH OUTPUT: '• Guide to installing the latest versions of Firefox and Orca link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'Download/Installation h1'",
     "     VISIBLE:  'Download/Installation h1', cursor=1",
     "SPEECH OUTPUT: 'Download/Installation heading  '",
     "SPEECH OUTPUT: 'level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'As of GNOME 2.16, Orca is a part of the GNOME platform. As a result, Orca is already'",
     "     VISIBLE:  'As of GNOME 2.16, Orca is a part', cursor=1",
     "SPEECH OUTPUT: 'As of GNOME 2.16, Orca is a part of the GNOME platform. As a result, Orca is already'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'provided by default on a number of operating system distributions, including Open Solaris Link'",
     "     VISIBLE:  'provided by default on a number ', cursor=1",
     "SPEECH OUTPUT: 'provided by default on a number of operating system distributions, including Open Solaris link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'and Ubuntu Link .'",
     "     VISIBLE:  'and Ubuntu Link .', cursor=1",
     "SPEECH OUTPUT: 'and Ubuntu link .'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'Please also refer to the Download/Installation page Link  for detailed information on various'",
     "     VISIBLE:  'Please also refer to the Downloa', cursor=1",
     "SPEECH OUTPUT: 'Please also refer to the Download/Installation page link  for detailed information on various'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'distributions as well as installing Orca directly from source.'",
     "     VISIBLE:  'distributions as well as install', cursor=1",
     "SPEECH OUTPUT: 'distributions as well as installing Orca directly from source.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'Configuration/Use h1'",
     "     VISIBLE:  'Configuration/Use h1', cursor=1",
     "SPEECH OUTPUT: 'Configuration/Use heading  '",
     "SPEECH OUTPUT: 'level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'The command to run orca is orca. You can enter this command by pressing Alt+F2 when'",
     "     VISIBLE:  'The command to run orca is orca.', cursor=1",
     "SPEECH OUTPUT: 'The command to run orca is orca. You can enter this command by pressing Alt+F2 when'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'logged in, waiting for a second or so, then typing orca and pressing return. Orca is'",
     "     VISIBLE:  'logged in, waiting for a second ', cursor=1",
     "SPEECH OUTPUT: 'logged in, waiting for a second or so, then typing orca and pressing return. Orca is'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'designed to present information as you navigate the desktop using the built-in navigation Link'",
     "     VISIBLE:  'designed to present information ', cursor=1",
     "SPEECH OUTPUT: 'designed to present information as you navigate the desktop using the built-in navigation link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'mechanisms of GNOME Link . These navigation mechanisms are consistent across most'",
     "     VISIBLE:  'mechanisms of GNOME Link . These', cursor=1",
     "SPEECH OUTPUT: 'mechanisms of GNOME link . These navigation mechanisms are consistent across most'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'desktop applications.'",
     "     VISIBLE:  'desktop applications.', cursor=1",
     "SPEECH OUTPUT: 'desktop applications.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'You may sometimes wish to control Orca itself, such as bringing up the Orca Configuration Link'",
     "     VISIBLE:  'You may sometimes wish to contro', cursor=1",
     "SPEECH OUTPUT: 'You may sometimes wish to control Orca itself, such as bringing up the Orca Configuration link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'GUI Link (accessed by pressing Insert+Space when Orca is running) and for using flat review'",
     "     VISIBLE:  'GUI Link (accessed by pressing I', cursor=1",
     "SPEECH OUTPUT: 'GUI link (accessed by pressing Insert+Space when Orca is running) and for using flat review'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'mode to examine a window. Refer to Orca Keyboard Commands Link (Laptop Layout) Link  for more'",
     "     VISIBLE:  'mode to examine a window. Refer ', cursor=1",
     "SPEECH OUTPUT: 'mode to examine a window. Refer to Orca Keyboard Commands link (Laptop Layout) link  for more'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'information on Orca-specific keyboard commands. The Orca Configuration GUI Link  also'",
     "     VISIBLE:  'information on Orca-specific key', cursor=1",
     "SPEECH OUTPUT: 'information on Orca-specific keyboard commands. The Orca Configuration GUI link  also'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down", 
    ["BRAILLE LINE:  'includes a \"Key Bindings\" tab that allows you to get a complete list of Orca key bindings.'",
     "     VISIBLE:  'includes a \"Key Bindings\" tab th', cursor=1",
     "SPEECH OUTPUT: 'includes a \"Key Bindings\" tab that allows you to get a complete list of Orca key bindings.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Please also refer to the Configuration/Use page Link  for detailed information.'",
     "     VISIBLE:  'Please also refer to the Configu', cursor=1",
     "SPEECH OUTPUT: 'Please also refer to the Configuration/Use page link  for detailed information.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Accessible Applications h1'",
     "     VISIBLE:  'Accessible Applications h1', cursor=1",
     "SPEECH OUTPUT: 'Accessible Applications heading  '",
     "SPEECH OUTPUT: 'level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Orca is designed to work with applications and toolkits that support the assistive'",
     "     VISIBLE:  'Orca is designed to work with ap', cursor=1",
     "SPEECH OUTPUT: 'Orca is designed to work with applications and toolkits that support the assistive'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'technology service provider interface (AT-SPI). This includes the GNOME desktop and its'",
     "     VISIBLE:  'technology service provider inte', cursor=1",
     "SPEECH OUTPUT: 'technology service provider interface (AT-SPI). This includes the GNOME desktop and its'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'applications, OpenOffice Link , Firefox, and the Java platform. Some applications work better'",
     "     VISIBLE:  'applications, OpenOffice Link , ', cursor=1",
     "SPEECH OUTPUT: 'applications, OpenOffice link , Firefox, and the Java platform. Some applications work better'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'than others, however, and the Orca community continually works to provide compelling'",
     "     VISIBLE:  'than others, however, and the Or', cursor=1",
     "SPEECH OUTPUT: 'than others, however, and the Orca community continually works to provide compelling'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'access to more and more applications.'",
     "     VISIBLE:  'access to more and more applicat', cursor=1",
     "SPEECH OUTPUT: 'access to more and more applications.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'On the Accessible Applications page Link , you will find a growing list of information regarding'",
     "     VISIBLE:  'On the Accessible Applications p', cursor=1",
     "SPEECH OUTPUT: 'On the Accessible Applications page link , you will find a growing list of information regarding'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'various applications that can be accessed with Orca as well as tips and tricks for using'",
     "     VISIBLE:  'various applications that can be', cursor=1",
     "SPEECH OUTPUT: 'various applications that can be accessed with Orca as well as tips and tricks for using'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'them. The list is not to be a conclusive list of all applications. Rather, the goal is to provide a'",
     "     VISIBLE:  'them. The list is not to be a co', cursor=1",
     "SPEECH OUTPUT: 'them. The list is not to be a conclusive list of all applications. Rather, the goal is to provide a'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'repository within which users can share experiences regarding applications they have'",
     "     VISIBLE:  'repository within which users ca', cursor=1",
     "SPEECH OUTPUT: 'repository within which users can share experiences regarding applications they have'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'tested.'",
     "     VISIBLE:  'tested.', cursor=1",
     "SPEECH OUTPUT: 'tested.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'See also the Application Specific Settings Link  page for how to configure settings specific to an'",
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
    ["BRAILLE LINE:  'Please also refer to the Accessible Applications page Link  for detailed information.'",
     "     VISIBLE:  'Please also refer to the Accessi', cursor=1",
     "SPEECH OUTPUT: 'Please also refer to the Accessible Applications page link  for detailed information.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'How Can I Help? h1'",
     "     VISIBLE:  'How Can I Help? h1', cursor=1",
     "SPEECH OUTPUT: 'How Can I Help? heading  '",
     "SPEECH OUTPUT: 'level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'There's a bunch you can do! Please refer to the How Can I Help page Link  for detailed'",
     "     VISIBLE:  'There's a bunch you can do! Plea', cursor=1",
     "SPEECH OUTPUT: 'There's a bunch you can do! Please refer to the How Can I Help page link  for detailed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'information.'",
     "     VISIBLE:  'information.', cursor=1",
     "SPEECH OUTPUT: 'information.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'More Information h1'",
     "     VISIBLE:  'More Information h1', cursor=1",
     "SPEECH OUTPUT: 'More Information heading  '",
     "SPEECH OUTPUT: 'level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '• Frequently Asked Questions: FAQ Link'",
     "     VISIBLE:  '• Frequently Asked Questions: ', cursor=1",
     "SPEECH OUTPUT: '• Frequently Asked Questions: FAQ link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '• Mailing list: orca-list@gnome.org Link  ( Archives Link )'",
     "     VISIBLE:  '• Mailing list: orca-list@gnom', cursor=1",
     "SPEECH OUTPUT: '• Mailing list: orca-list@gnome.org link  ( Archives link )'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '• Bug database: GNOME Bug Tracking System (Bugzilla) Link  ( current bug list Link )'",
     "     VISIBLE:  '• Bug database: GNOME Bug Trac', cursor=1",
     "SPEECH OUTPUT: '• Bug database: GNOME Bug Tracking System (Bugzilla) link  ( current bug list link )'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '• Design documents: Orca Documentation Series Link'",
     "     VISIBLE:  '• Design documents: Orca Docum', cursor=1",
     "SPEECH OUTPUT: '• Design documents: Orca Documentation Series link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '• Dive Into Python, Mark Pilgrim Link'",
     "     VISIBLE:  '• Dive Into Python, Mark Pilgr', cursor=1",
     "SPEECH OUTPUT: '• Dive Into Python, Mark Pilgrim link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '• Python in a Nutshell, Alex Martelli Link'",
     "     VISIBLE:  '• Python in a Nutshell, Alex M', cursor=1",
     "SPEECH OUTPUT: '• Python in a Nutshell, Alex Martelli link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  '• Python Pocket Reference, Mark Lutz Link'",
     "     VISIBLE:  '• Python Pocket Reference, Mar', cursor=1",
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
    ["BRAILLE LINE:  'The information on this page and the other Orca-related pages on this site are distributed'",
     "     VISIBLE:  'The information on this page and', cursor=1",
     "SPEECH OUTPUT: 'The information on this page and the other Orca-related pages on this site are distributed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied'",
     "     VISIBLE:  'in the hope that it will be usef', cursor=1",
     "SPEECH OUTPUT: 'in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.'",
     "     VISIBLE:  'warranty of MERCHANTABILITY or F', cursor=1",
     "SPEECH OUTPUT: 'warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.'"]))

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
    ["BRAILLE LINE:  'CategoryAccessibility Link'",
     "     VISIBLE:  'CategoryAccessibility Link', cursor=1",
     "SPEECH OUTPUT: 'CategoryAccessibility link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Orca (last edited 2007-12-07 22:09:22 by WillieWalker Link )'",
     "     VISIBLE:  'Orca (last edited 2007-12-07 22:', cursor=1",
     "SPEECH OUTPUT: 'Orca (last edited 2007-12-07 22:09:22 by WillieWalker link )'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'User h3'",
     "     VISIBLE:  'User h3', cursor=1",
     "SPEECH OUTPUT: 'User heading  '",
     "SPEECH OUTPUT: 'level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Login Link'",
     "     VISIBLE:  'Login Link', cursor=1",
     "SPEECH OUTPUT: 'Login link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Page h3'",
     "     VISIBLE:  'Page h3', cursor=1",
     "SPEECH OUTPUT: 'Page heading  '",
     "SPEECH OUTPUT: 'level 3'"]))

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
    ["BRAILLE LINE:  'Info Link'",
     "     VISIBLE:  'Info Link', cursor=1",
     "SPEECH OUTPUT: 'Info link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'Attachments Link'",
     "     VISIBLE:  'Attachments Link', cursor=1",
     "SPEECH OUTPUT: 'Attachments link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'More Actions: Combo'",
     "     VISIBLE:  'More Actions: Combo', cursor=0",
     "SPEECH OUTPUT: 'More Actions: combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "Line Down",
    ["BRAILLE LINE:  'GNOME World Wide h3'",
     "     VISIBLE:  'GNOME World Wide h3', cursor=1",
     "SPEECH OUTPUT: 'GNOME World Wide heading  '",
     "SPEECH OUTPUT: 'level 3'"]))

########################################################################
# Up Arrow to the Top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'More Actions: Combo'",
     "     VISIBLE:  'More Actions: Combo', cursor=0",
     "SPEECH OUTPUT: 'More Actions: combo box'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Attachments Link'",
     "     VISIBLE:  'Attachments Link', cursor=1",
     "SPEECH OUTPUT: 'Attachments link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Info Link'",
     "     VISIBLE:  'Info Link', cursor=1",
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
     "SPEECH OUTPUT: 'Page heading  '",
     "SPEECH OUTPUT: 'level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Login Link'",
     "     VISIBLE:  'Login Link', cursor=1",
     "SPEECH OUTPUT: 'Login link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'User h3'",
     "     VISIBLE:  'User h3', cursor=1",
     "SPEECH OUTPUT: 'User heading  '",
     "SPEECH OUTPUT: 'level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Orca (last edited 2007-12-07 22:09:22 by WillieWalker Link )'",
     "     VISIBLE:  'Orca (last edited 2007-12-07 22:', cursor=1",
     "SPEECH OUTPUT: 'Orca (last edited 2007-12-07 22:09:22 by WillieWalker link )'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'CategoryAccessibility Link'",
     "     VISIBLE:  'CategoryAccessibility Link', cursor=1",
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
    ["BRAILLE LINE:  'warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.'",
     "     VISIBLE:  'warranty of MERCHANTABILITY or F', cursor=1",
     "SPEECH OUTPUT: 'warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied'",
     "     VISIBLE:  'in the hope that it will be usef', cursor=1",
     "SPEECH OUTPUT: 'in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'The information on this page and the other Orca-related pages on this site are distributed'",
     "     VISIBLE:  'The information on this page and', cursor=1",
     "SPEECH OUTPUT: 'The information on this page and the other Orca-related pages on this site are distributed'"]))

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
    ["BRAILLE LINE:  '• Python Pocket Reference, Mark Lutz Link'",
     "     VISIBLE:  '• Python Pocket Reference, Mar', cursor=1",
     "SPEECH OUTPUT: '• Python Pocket Reference, Mark Lutz link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '• Python in a Nutshell, Alex Martelli Link'",
     "     VISIBLE:  '• Python in a Nutshell, Alex M', cursor=1",
     "SPEECH OUTPUT: '• Python in a Nutshell, Alex Martelli link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '• Dive Into Python, Mark Pilgrim Link'",
     "     VISIBLE:  '• Dive Into Python, Mark Pilgr', cursor=1",
     "SPEECH OUTPUT: '• Dive Into Python, Mark Pilgrim link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '• Design documents: Orca Documentation Series Link'",
     "     VISIBLE:  '• Design documents: Orca Docum', cursor=1",
     "SPEECH OUTPUT: '• Design documents: Orca Documentation Series link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '• Bug database: GNOME Bug Tracking System (Bugzilla) Link  ( current bug list Link )'",
     "     VISIBLE:  '• Bug database: GNOME Bug Trac', cursor=1",
     "SPEECH OUTPUT: '• Bug database: GNOME Bug Tracking System (Bugzilla) link  ( current bug list link )'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '• Mailing list: orca-list@gnome.org Link  ( Archives Link )'",
     "     VISIBLE:  '• Mailing list: orca-list@gnom', cursor=1",
     "SPEECH OUTPUT: '• Mailing list: orca-list@gnome.org link  ( Archives link )'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  '• Frequently Asked Questions: FAQ Link'",
     "     VISIBLE:  '• Frequently Asked Questions: ', cursor=1",
     "SPEECH OUTPUT: '• Frequently Asked Questions: FAQ link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'More Information h1'",
     "     VISIBLE:  'More Information h1', cursor=1",
     "SPEECH OUTPUT: 'More Information heading  '",
     "SPEECH OUTPUT: 'level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'information.'",
     "     VISIBLE:  'information.', cursor=1",
     "SPEECH OUTPUT: 'information.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'There's a bunch you can do! Please refer to the How Can I Help page Link  for detailed'",
     "     VISIBLE:  'There's a bunch you can do! Plea', cursor=1",
     "SPEECH OUTPUT: 'There's a bunch you can do! Please refer to the How Can I Help page link  for detailed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'How Can I Help? h1'",
     "     VISIBLE:  'How Can I Help? h1', cursor=1",
     "SPEECH OUTPUT: 'How Can I Help? heading  '",
     "SPEECH OUTPUT: 'level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Please also refer to the Accessible Applications page Link  for detailed information.'",
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
    ["BRAILLE LINE:  'See also the Application Specific Settings Link  page for how to configure settings specific to an'",
     "     VISIBLE:  'See also the Application Specifi', cursor=1",
     "SPEECH OUTPUT: 'See also the Application Specific Settings link  page for how to configure settings specific to an'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'tested.'",
     "     VISIBLE:  'tested.', cursor=1",
     "SPEECH OUTPUT: 'tested.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'repository within which users can share experiences regarding applications they have'",
     "     VISIBLE:  'repository within which users ca', cursor=1",
     "SPEECH OUTPUT: 'repository within which users can share experiences regarding applications they have'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'them. The list is not to be a conclusive list of all applications. Rather, the goal is to provide a'",
     "     VISIBLE:  'them. The list is not to be a co', cursor=1",
     "SPEECH OUTPUT: 'them. The list is not to be a conclusive list of all applications. Rather, the goal is to provide a'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'various applications that can be accessed with Orca as well as tips and tricks for using'",
     "     VISIBLE:  'various applications that can be', cursor=1",
     "SPEECH OUTPUT: 'various applications that can be accessed with Orca as well as tips and tricks for using'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'On the Accessible Applications page Link , you will find a growing list of information regarding'",
     "     VISIBLE:  'On the Accessible Applications p', cursor=1",
     "SPEECH OUTPUT: 'On the Accessible Applications page link , you will find a growing list of information regarding'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'access to more and more applications.'",
     "     VISIBLE:  'access to more and more applicat', cursor=1",
     "SPEECH OUTPUT: 'access to more and more applications.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'than others, however, and the Orca community continually works to provide compelling'",
     "     VISIBLE:  'than others, however, and the Or', cursor=1",
     "SPEECH OUTPUT: 'than others, however, and the Orca community continually works to provide compelling'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'applications, OpenOffice Link , Firefox, and the Java platform. Some applications work better'",
     "     VISIBLE:  'applications, OpenOffice Link , ', cursor=1",
     "SPEECH OUTPUT: 'applications, OpenOffice link , Firefox, and the Java platform. Some applications work better'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'technology service provider interface (AT-SPI). This includes the GNOME desktop and its'",
     "     VISIBLE:  'technology service provider inte', cursor=1",
     "SPEECH OUTPUT: 'technology service provider interface (AT-SPI). This includes the GNOME desktop and its'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Orca is designed to work with applications and toolkits that support the assistive'",
     "     VISIBLE:  'Orca is designed to work with ap', cursor=1",
     "SPEECH OUTPUT: 'Orca is designed to work with applications and toolkits that support the assistive'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Accessible Applications h1'",
     "     VISIBLE:  'Accessible Applications h1', cursor=1",
     "SPEECH OUTPUT: 'Accessible Applications heading  '",
     "SPEECH OUTPUT: 'level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Please also refer to the Configuration/Use page Link  for detailed information.'",
     "     VISIBLE:  'Please also refer to the Configu', cursor=1",
     "SPEECH OUTPUT: 'Please also refer to the Configuration/Use page link  for detailed information.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'includes a \"Key Bindings\" tab that allows you to get a complete list of Orca key bindings.'",
     "     VISIBLE:  'includes a \"Key Bindings\" tab th', cursor=1",
     "SPEECH OUTPUT: 'includes a \"Key Bindings\" tab that allows you to get a complete list of Orca key bindings.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'information on Orca-specific keyboard commands. The Orca Configuration GUI Link  also'",
     "     VISIBLE:  'information on Orca-specific key', cursor=1",
     "SPEECH OUTPUT: 'information on Orca-specific keyboard commands. The Orca Configuration GUI link  also'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'mode to examine a window. Refer to Orca Keyboard Commands Link (Laptop Layout) Link  for more'",
     "     VISIBLE:  'mode to examine a window. Refer ', cursor=1",
     "SPEECH OUTPUT: 'mode to examine a window. Refer to Orca Keyboard Commands link (Laptop Layout) link  for more'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'GUI Link (accessed by pressing Insert+Space when Orca is running) and for using flat review'",
     "     VISIBLE:  'GUI Link (accessed by pressing I', cursor=1",
     "SPEECH OUTPUT: 'GUI link (accessed by pressing Insert+Space when Orca is running) and for using flat review'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'You may sometimes wish to control Orca itself, such as bringing up the Orca Configuration Link'",
     "     VISIBLE:  'You may sometimes wish to contro', cursor=1",
     "SPEECH OUTPUT: 'You may sometimes wish to control Orca itself, such as bringing up the Orca Configuration link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'desktop applications.'",
     "     VISIBLE:  'desktop applications.', cursor=1",
     "SPEECH OUTPUT: 'desktop applications.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'mechanisms of GNOME Link . These navigation mechanisms are consistent across most'",
     "     VISIBLE:  'mechanisms of GNOME Link . These', cursor=1",
     "SPEECH OUTPUT: 'mechanisms of GNOME link . These navigation mechanisms are consistent across most'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'designed to present information as you navigate the desktop using the built-in navigation Link'",
     "     VISIBLE:  'designed to present information ', cursor=1",
     "SPEECH OUTPUT: 'designed to present information as you navigate the desktop using the built-in navigation link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'logged in, waiting for a second or so, then typing orca and pressing return. Orca is'",
     "     VISIBLE:  'logged in, waiting for a second ', cursor=1",
     "SPEECH OUTPUT: 'logged in, waiting for a second or so, then typing orca and pressing return. Orca is'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'The command to run orca is orca. You can enter this command by pressing Alt+F2 when'",
     "     VISIBLE:  'The command to run orca is orca.', cursor=1",
     "SPEECH OUTPUT: 'The command to run orca is orca. You can enter this command by pressing Alt+F2 when'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'Configuration/Use h1'",
     "     VISIBLE:  'Configuration/Use h1', cursor=1",
     "SPEECH OUTPUT: 'Configuration/Use heading  '",
     "SPEECH OUTPUT: 'level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'distributions as well as installing Orca directly from source.'",
     "     VISIBLE:  'distributions as well as install', cursor=1",
     "SPEECH OUTPUT: 'distributions as well as installing Orca directly from source.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'Please also refer to the Download/Installation page Link  for detailed information on various'",
     "     VISIBLE:  'Please also refer to the Downloa', cursor=1",
     "SPEECH OUTPUT: 'Please also refer to the Download/Installation page link  for detailed information on various'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'and Ubuntu Link .'",
     "     VISIBLE:  'and Ubuntu Link .', cursor=1",
     "SPEECH OUTPUT: 'and Ubuntu link .'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'provided by default on a number of operating system distributions, including Open Solaris Link'",
     "     VISIBLE:  'provided by default on a number ', cursor=1",
     "SPEECH OUTPUT: 'provided by default on a number of operating system distributions, including Open Solaris link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'As of GNOME 2.16, Orca is a part of the GNOME platform. As a result, Orca is already'",
     "     VISIBLE:  'As of GNOME 2.16, Orca is a part', cursor=1",
     "SPEECH OUTPUT: 'As of GNOME 2.16, Orca is a part of the GNOME platform. As a result, Orca is already'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'Download/Installation h1'",
     "     VISIBLE:  'Download/Installation h1', cursor=1",
     "SPEECH OUTPUT: 'Download/Installation heading  '",
     "SPEECH OUTPUT: 'level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  '• Guide to installing the latest versions of Firefox and Orca Link'",
     "     VISIBLE:  '• Guide to installing the late', cursor=1",
     "SPEECH OUTPUT: '• Guide to installing the latest versions of Firefox and Orca link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  '• Review of Fedora 7 and the Orca screen reader for the Gnome graphical desktop Link'",
     "     VISIBLE:  '• Review of Fedora 7 and the O', cursor=1",
     "SPEECH OUTPUT: '• Review of Fedora 7 and the Orca screen reader for the Gnome graphical desktop link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  '• Walk through of the installation of Ubuntu 7.4. Very helpful tutorial Link'",
     "     VISIBLE:  '• Walk through of the installa', cursor=1",
     "SPEECH OUTPUT: '• Walk through of the installation of Ubuntu 7.4. Very helpful tutorial link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'and include the following:'",
     "     VISIBLE:  'and include the following:', cursor=1",
     "SPEECH OUTPUT: 'and include the following:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  '(THANKS!)!!! The audio guides can be found at http://www.digitaldarragh.com/linuxat.asp Link'",
     "     VISIBLE:  '(THANKS!)!!! The audio guides ca', cursor=1",
     "SPEECH OUTPUT: '(THANKS!)!!! The audio guides can be found at http://www.digitaldarragh.com/linuxat.asp link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'Darragh Ó Héiligh Link has created several audio guides for Orca. This is a fantastic contribution'",
     "     VISIBLE:  'Darragh Ó Héiligh Link has cre', cursor=1",
     "SPEECH OUTPUT: 'Darragh Ó Héiligh link has created several audio guides for Orca. This is a fantastic contribution'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'Audio Guides h1'",
     "     VISIBLE:  'Audio Guides h1', cursor=1",
     "SPEECH OUTPUT: 'Audio Guides heading  '",
     "SPEECH OUTPUT: 'level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'productive environment composed of users and developers.'",
     "     VISIBLE:  'productive environment composed ', cursor=1",
     "SPEECH OUTPUT: 'productive environment composed of users and developers.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'Please join and participate on the Orca mailing list Link  ( archives Link ): it's a helpful, kind, and'",
     "     VISIBLE:  'Please join and participate on t', cursor=1",
     "SPEECH OUTPUT: 'Please join and participate on the Orca mailing list link  ( archives link ): it's a helpful, kind, and'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  '(please see our notes on how we use Bugzilla Link ).'",
     "     VISIBLE:  '(please see our notes on how we ', cursor=1",
     "SPEECH OUTPUT: '(please see our notes on how we use Bugzilla link ).'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'requests, along with known problems in other components, is maintained in Bugzilla Link'",
     "     VISIBLE:  'requests, along with known probl', cursor=1",
     "SPEECH OUTPUT: 'requests, along with known problems in other components, is maintained in Bugzilla link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'The complete list of work to do, including bugs and feature'",
     "     VISIBLE:  'The complete list of work to do,', cursor=1",
     "SPEECH OUTPUT: 'The complete list of work to do, including bugs and feature'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'from many community members Link .'",
     "     VISIBLE:  'from many community members Link', cursor=1",
     "SPEECH OUTPUT: 'from many community members link .'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'contributions Link'",
     "     VISIBLE:  'contributions Link', cursor=1",
     "SPEECH OUTPUT: 'contributions link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BUG? - We're missing a link that's split across two lines", 
     "BRAILLE LINE:  'Program Office of Sun Microsystems, Inc. Link with contributions Link'",
     "     VISIBLE:  'Program Office of Sun Microsyste', cursor=1",
     "SPEECH OUTPUT: 'Program Office of Sun Microsystems, Inc. link with contributions link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'The development of Orca has been led by the Accessibility Link'",
     "     VISIBLE:  'The development of Orca has been', cursor=1",
     "SPEECH OUTPUT: 'The development of Orca has been led by the Accessibility link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'toolkits that support the AT-SPI (e.g., the GNOME desktop).'",
     "     VISIBLE:  'toolkits that support the AT-SPI', cursor=1",
     "SPEECH OUTPUT: 'toolkits that support the AT-SPI (e.g., the GNOME desktop).'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'magnification, Orca helps provide access to applications and'",
     "     VISIBLE:  'magnification, Orca helps provid', cursor=1",
     "SPEECH OUTPUT: 'magnification, Orca helps provide access to applications and'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'various combinations of speech synthesis, braille, and'",
     "     VISIBLE:  'various combinations of speech s', cursor=1",
     "SPEECH OUTPUT: 'various combinations of speech synthesis, braille, and'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'assistive technology for people with visual impairments. Using'",
     "     VISIBLE:  'assistive technology for people ', cursor=1",
     "SPEECH OUTPUT: 'assistive technology for people with visual impairments. Using'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'Orca is a free, open source, flexible, extensible, and powerful'",
     "     VISIBLE:  'Orca is a free, open source, fle', cursor=1",
     "SPEECH OUTPUT: 'Orca is a free, open source, flexible, extensible, and powerful'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'About h1'",
     "     VISIBLE:  'About h1', cursor=1",
     "SPEECH OUTPUT: 'About heading  '",
     "SPEECH OUTPUT: 'level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  '8. More Information Link'",
     "     VISIBLE:  '8. More Information Link', cursor=1",
     "SPEECH OUTPUT: '8. More Information link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  '7. How Can I Help? Link'",
     "     VISIBLE:  '7. How Can I Help? Link', cursor=1",
     "SPEECH OUTPUT: '7. How Can I Help? link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  '6. Accessible Applications Link'",
     "     VISIBLE:  '6. Accessible Applications Link', cursor=1",
     "SPEECH OUTPUT: '6. Accessible Applications link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  '5. Configuration/Use Link'",
     "     VISIBLE:  '5. Configuration/Use Link', cursor=1",
     "SPEECH OUTPUT: '5. Configuration/Use link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  '4. Download/Installation Link'",
     "     VISIBLE:  '4. Download/Installation Link', cursor=1",
     "SPEECH OUTPUT: '4. Download/Installation link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  '3. Audio Guides Link'",
     "     VISIBLE:  '3. Audio Guides Link', cursor=1",
     "SPEECH OUTPUT: '3. Audio Guides link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  '2. About Link'",
     "     VISIBLE:  '2. About Link', cursor=1",
     "SPEECH OUTPUT: '2. About link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  '1. Welcome to Orca! Link'",
     "     VISIBLE:  '1. Welcome to Orca! Link', cursor=1",
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
    ["BRAILLE LINE:  'HOT HOT HOT: Notes on access to Firefox 3.0 Link'",
     "     VISIBLE:  'HOT HOT HOT: Notes on access to ', cursor=1",
     "SPEECH OUTPUT: 'HOT HOT HOT: Notes on access to Firefox 3.0 link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'Orca Logo Link Image'",
     "     VISIBLE:  'Orca Logo Link Image', cursor=1",
     "SPEECH OUTPUT: 'Orca Logo link image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'Welcome to Orca! h1'",
     "     VISIBLE:  'Welcome to Orca! h1', cursor=1",
     "SPEECH OUTPUT: 'Welcome to Orca! heading  '",
     "SPEECH OUTPUT: 'level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  '( Archives Link ) | FAQ Link  | DocIndex Link'",
     "     VISIBLE:  '( Archives Link ) | FAQ Link  | ', cursor=1",
     "SPEECH OUTPUT: '( Archives link ) | FAQ link  | DocIndex link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'Home Link | Download/Installation Link  | Configuration/Use Link  | Accessible Applications Link  | Mailing List Link'",
     "     VISIBLE:  'Home Link | Download/Installatio', cursor=1",
     "SPEECH OUTPUT: 'Home link | Download/Installation link  | Configuration/Use link  | Accessible Applications link  | Mailing List link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up", 
    ["BRAILLE LINE:  'en Español Link'",
     "     VISIBLE:  'en Español Link', cursor=1",
     "SPEECH OUTPUT: 'en Español link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Home Link RecentChanges Link FindPage Link HelpContents Link Orca Link'",
     "     VISIBLE:  'Home Link RecentChanges Link Fin', cursor=1",
     "SPEECH OUTPUT: 'Home link RecentChanges link FindPage link HelpContents link Orca link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'live.gnome.org h1 Search $l Titles Button Text Button'",
     "     VISIBLE:  'live.gnome.org h1 Search $l Titl', cursor=1",
     "SPEECH OUTPUT: 'live.gnome.org heading  '",
     "SPEECH OUTPUT: 'level 1'",
     "SPEECH OUTPUT: 'text Search Titles button grayed Text button grayed'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "Line Up",
    ["BRAILLE LINE:  'Home Link News Link Projects Link Art Link Support Link Development Link Community Link'",
     "     VISIBLE:  'Home Link News Link Projects Lin', cursor=1",
     "SPEECH OUTPUT: 'Home link News link Projects link Art link Support link Development link Community link'"]))

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

sequence.append(utils.AssertionSummaryAction())

sequence.start()
