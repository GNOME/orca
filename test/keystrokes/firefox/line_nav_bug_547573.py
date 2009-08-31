# -*- coding: utf-8 -*-
#!/usr/bin/python

"""Test of line navigation output of Firefox. 
"""

from macaroon.playback import *
import utils

sequence = MacroSequence()

########################################################################
# We wait for the focus to be on a blank Firefox window.
#
sequence.append(WaitForWindowActivate(utils.firefoxFrameNames, None))

########################################################################
# Load the local "simple form" test case.
#
sequence.append(KeyComboAction("<Control>l"))
sequence.append(WaitForFocus(acc_role=pyatspi.ROLE_ENTRY))

sequence.append(TypeAction(utils.htmlURLPrefix + "java-sun-com.html"))
sequence.append(KeyComboAction("Return"))

sequence.append(WaitForDocLoad())

sequence.append(WaitForFocus("",
                             acc_role=pyatspi.ROLE_DOCUMENT_FRAME))

########################################################################
# Press Control+Home to move to the top.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "Top of file",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'link'"]))

########################################################################
# Down Arrow.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Line Down",
    ["BRAILLE LINE:  'Skip to Content Sun Java Solaris Communities My SDN Account Join SDN'",
     "     VISIBLE:  'Skip to Content Sun Java Solaris', cursor=1",
     "SPEECH OUTPUT: 'Skip to Content link Sun link Java link Solaris link Communities link My SDN Account link Join SDN link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  '» search tips  Search $l Submit Search Button Home Page Image'",
     "     VISIBLE:  '» search tips  Search $l Submit ', cursor=1",
     "SPEECH OUTPUT: '»  search tips link   text Search Submit Search button Home Page link image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'APIs Downloads Products Support Training Participate'",
     "     VISIBLE:  'APIs Downloads Products Support ', cursor=1",
     "SPEECH OUTPUT: 'APIs link Downloads link Products link Support link Training link Participate link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=0",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  'JavaTM SE 6 Release Notes'",
     "     VISIBLE:  'JavaTM SE 6 Release Notes', cursor=1",
     "SPEECH OUTPUT: 'JavaTM SE 6 Release Notes'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Down",
    ["BRAILLE LINE:  'Linux Installation (32-bit) h1'",
     "     VISIBLE:  'Linux Installation (32-bit) h1', cursor=1",
     "SPEECH OUTPUT: 'Linux Installation (32-bit) heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Down",
    ["BRAILLE LINE:  'Separator'",
     "     VISIBLE:  'Separator', cursor=1",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Down",
    ["BRAILLE LINE:  'JDK Documentation'",
     "     VISIBLE:  'JDK Documentation', cursor=1",
     "SPEECH OUTPUT: 'JDK Documentation link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Down",
    ["BRAILLE LINE:  'Contents h2'",
     "     VISIBLE:  'Contents h2', cursor=1",
     "SPEECH OUTPUT: 'Contents heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Line Down",
    ["BRAILLE LINE:  'System Requirements'",
     "     VISIBLE:  'System Requirements', cursor=1",
     "SPEECH OUTPUT: 'System Requirements link",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Line Down",
    ["BRAILLE LINE:  'JDK Installation Instructions'",
     "     VISIBLE:  'JDK Installation Instructions', cursor=1",
     "SPEECH OUTPUT: 'JDK Installation Instructions link ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. Line Down",
    ["BRAILLE LINE:  '   Installation of Self-Extracting Binary'",
     "     VISIBLE:  '   Installation of Self-Extracti', cursor=2",
     "SPEECH OUTPUT: '    Installation of Self-Extracting Binary link ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "13. Line Down",
    ["BRAILLE LINE:  '   Installation of RPM File'",
     "     VISIBLE:  '   Installation of RPM File', cursor=1",
     "SPEECH OUTPUT: '    Installation of RPM File link ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "14. Line Down",
    ["BRAILLE LINE:  'Java Plugin Browser Registration Instructions'",
     "     VISIBLE:  'Java Plugin Browser Registration', cursor=1",
     "SPEECH OUTPUT: 'Java Plugin Browser Registration Instructions link",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "15. Line Down",
    ["BRAILLE LINE:  'Java Web Start Installation Notes'",
     "     VISIBLE:  'Java Web Start Installation Note', cursor=1",
     "SPEECH OUTPUT: 'Java Web Start Installation Notes link",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "16. Line Down",
    ["BRAILLE LINE:  'Troubleshooting'",
     "     VISIBLE:  'Troubleshooting', cursor=1",
     "SPEECH OUTPUT: 'Troubleshooting link",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "17. Line Down",
    ["BRAILLE LINE:  'System Requirements h2'",
     "     VISIBLE:  'System Requirements h2', cursor=1",
     "SPEECH OUTPUT: 'System Requirements heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "18. Line Down",
    ["BRAILLE LINE:  'See supported System Configurations for information about supported platforms, operating systems, desktop managers, and browsers.'",
     "     VISIBLE:  'See supported System Configurati', cursor=1",
     "SPEECH OUTPUT: 'See supported System Configurations link  for information about supported platforms, operating systems, desktop managers, and browsers.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "19. Line Down",
    ["BRAILLE LINE:  'For issues, see the Troubleshooting section below.'",
     "     VISIBLE:  'For issues, see the Troubleshoot', cursor=1",
     "SPEECH OUTPUT: 'For issues, see the Troubleshooting link  section below.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "20. Line Down",
    ["BRAILLE LINE:  'Installation Instructions h2'",
     "     VISIBLE:  'Installation Instructions h2', cursor=1",
     "SPEECH OUTPUT: 'Installation Instructions heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "21. Line Down",
    ["BRAILLE LINE:  'Installing the JDK automatically installs the Java Plugin and Java Web Start. Note that the Java Plugin needs to be registered with the browser. After installing the JDK, refer to:'",
     "     VISIBLE:  'Installing the JDK automatically', cursor=1",
     "SPEECH OUTPUT: 'Installing the JDK automatically installs the Java Plugin and Java Web Start. Note that the Java Plugin needs to be registered with the browser. After installing the JDK, refer to:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "22. Line Down",
    ["BRAILLE LINE:  '• Java Plugin Browser Registration Instructions'",
     "     VISIBLE:  '• Java Plugin Browser Registrati', cursor=1",
     "SPEECH OUTPUT: '• Java Plugin Browser Registration Instructions link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "23. Line Down",
    ["BRAILLE LINE:  '• Java Web Start Installation Notes'",
     "     VISIBLE:  '• Java Web Start Installation No', cursor=1",
     "SPEECH OUTPUT: '• Java Web Start Installation Notes link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "24. Line Down",
    ["BRAILLE LINE:  'Install formats - This version of the JDK is available in two installation formats.'",
     "     VISIBLE:  'Install formats - This version o', cursor=1",
     "SPEECH OUTPUT: 'Install formats - This version of the JDK is available in two installation formats.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "25. Line Down",
    ["BRAILLE LINE:  '• Self-extracting Binary File - This file can be used to install the JDK in a location chosen by the user. This one can be installed by anyone (not only root users), and it can'",
     "     VISIBLE:  '• Self-extracting Binary File - ', cursor=1",
     "SPEECH OUTPUT: '• Self-extracting Binary File - This file can be used to install the JDK in a location chosen by the user. This one can be installed by anyone (not only root users), and it can'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "26. Line Down",
    ["BRAILLE LINE:  'easily be installed in any location. As long as you are not root user, it cannot displace the system version of the Java platform suppled by Linux. To use this file, see'",
     "     VISIBLE:  'easily be installed in any locat', cursor=1",
     "SPEECH OUTPUT: 'easily be installed in any location. As long as you are not root user, it cannot displace the system version of the Java platform suppled by Linux. To use this file, see'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "27. Line Down",
    ["BRAILLE LINE:  'Installation of Self-Extracting Binary below.'",
     "     VISIBLE:  'Installation of Self-Extracting ', cursor=1",
     "SPEECH OUTPUT: 'Installation of Self-Extracting Binary link  below.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "28. Line Down",
    ["BRAILLE LINE:  '• RPM Packages - A rpm.bin file containing RPM packages, installed with the rpm utility. Requires root access to install. RPM packages are the recommended method for'",
     "     VISIBLE:  '• RPM Packages - A rpm.bin file ', cursor=1",
     "SPEECH OUTPUT: '• RPM Packages - A rpm.bin file containing RPM packages, installed with the rpm utility. Requires root access to install. RPM packages are the recommended method for'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "29. Line Down",
    ["BRAILLE LINE:  'installation on Linux. To use this bundle, see Installation of RPM File below.'",
     "     VISIBLE:  'installation on Linux. To use th', cursor=1",
     "SPEECH OUTPUT: 'installation on Linux. To use this bundle, see Installation of RPM File link  below.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "30. Line Down",
    ["BRAILLE LINE:  'Choose the install format that is most suitable to your needs.'",
     "     VISIBLE:  'Choose the install format that i', cursor=1",
     "SPEECH OUTPUT: 'Choose the install format that is most suitable to your needs.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "31. Line Down",
    ["BRAILLE LINE:  'Note: For any text on this page containing the following notation, you must substitute the appropriate JDK update version number for the notation.'",
     "     VISIBLE:  'Note: For any text on this page ', cursor=1",
     "SPEECH OUTPUT: 'Note: For any text on this page containing the following notation, you must substitute the appropriate JDK update version number for the notation.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "32. Line Down",
    ["BRAILLE LINE:  '<version>'",
     "     VISIBLE:  '<version>', cursor=1",
     "SPEECH OUTPUT: '<version>",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "33. Line Down",
    ["BUG? - Even if we're not saying anything here, shouldn't there be a SPEECH OUTPUT line?",
     "BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "34. Line Down",
    ["BRAILLE LINE:  'For example, if you were downloading update 6_01, the following command:'",
     "     VISIBLE:  'For example, if you were downloa', cursor=1",
     "SPEECH OUTPUT: 'For example, if you were downloading update 6_01, the following command:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "35. Line Down",
    ["BRAILLE LINE:  './jdk-6<version>-linux-i586.bin'",
     "     VISIBLE:  './jdk-6<version>-linux-i586.bin', cursor=1",
     "SPEECH OUTPUT: './jdk-6<version>-linux-i586.bin",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "36. Line Down",
    ["BUG? - Even if we're not saying anything here, shouldn't there be a SPEECH OUTPUT line?",
     "BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "37. Line Down",
    ["BRAILLE LINE:  'would become:'",
     "     VISIBLE:  'would become:', cursor=1",
     "SPEECH OUTPUT: 'would become:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "38. Line Down",
    ["BRAILLE LINE:  './jdk-6u1-linux-i586.bin'",
     "     VISIBLE:  './jdk-6u1-linux-i586.bin', cursor=1",
     "SPEECH OUTPUT: './jdk-6u1-linux-i586.bin",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "39. Line Down",
    ["BUG? - Even if we're not saying anything here, shouldn't there be a SPEECH OUTPUT line?",
     "BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "40. Line Down",
    ["BRAILLE LINE:  'Installation of Self-Extracting Binary h3'",
     "     VISIBLE:  'Installation of Self-Extracting ', cursor=1",
     "SPEECH OUTPUT: 'Installation of Self-Extracting Binary heading level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "41. Line Down",
    ["BRAILLE LINE:  'Use these instructions if you want to use the self-extracting binary file to install the JDK. If you want to install RPM packages instead, see Installation of RPM File.'",
     "     VISIBLE:  'Use these instructions if you wa', cursor=1",
     "SPEECH OUTPUT: 'Use these instructions if you want to use the self-extracting binary file to install the JDK. If you want to install RPM packages instead, see Installation of RPM File link .'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "42. Line Down",
    ["BRAILLE LINE:  '1. Download and check the download file size to ensure that you have downloaded the full, uncorrupted software bundle.'",
     "     VISIBLE:  '1. Download and check the downlo', cursor=1",
     "SPEECH OUTPUT: '1. Download and check the download file size to ensure that you have downloaded the full, uncorrupted software bundle.",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "43. Line Down",
    ["BRAILLE LINE:  'You can download to any directory you choose; it does not have to be the directory where you want to install the JDK.'",
     "     VISIBLE:  'You can download to any director', cursor=1",
     "SPEECH OUTPUT: 'You can download to any directory you choose; it does not have to be the directory where you want to install the JDK.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "44. Line Down",
    ["BRAILLE LINE:  'Before you download the file, notice its byte size provided on the download page on the web site. Once the download has completed, compare that file size to the'",
     "     VISIBLE:  'Before you download the file, no', cursor=1",
     "SPEECH OUTPUT: 'Before you download the file, notice its byte size provided on the download page on the web site. Once the download has completed, compare that file size to the'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "45. Line Down",
    ["BRAILLE LINE:  'size of the downloaded file to make sure they are equal.'",
     "     VISIBLE:  'size of the downloaded file to m', cursor=1",
     "SPEECH OUTPUT: 'size of the downloaded file to make sure they are equal.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "46. Line Down",
    ["BRAILLE LINE:  '2. Make sure that execute permissions are set on the self-extracting binary.'",
     "     VISIBLE:  '2. Make sure that execute permis', cursor=1",
     "SPEECH OUTPUT: '2. Make sure that execute permissions are set on the self-extracting binary.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "47. Line Down",
    ["BRAILLE LINE:  'Run this command:'",
     "     VISIBLE:  'Run this command:', cursor=1",
     "SPEECH OUTPUT: 'Run this command:",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "48. Line Down",
    ["BRAILLE LINE:  'chmod +x jdk-6<version>-linux-i586.bin'",
     "     VISIBLE:  'chmod +x jdk-6<version>-linux-i5', cursor=1",
     "SPEECH OUTPUT: 'chmod +x jdk-6<version>-linux-i586.bin'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "49. Line Down",
    ["BRAILLE LINE:  '3. Change directory to the location where you would like the files to be installed.'",
     "     VISIBLE:  '3. Change directory to the locat', cursor=1",
     "SPEECH OUTPUT: '3. Change directory to the location where you would like the files to be installed.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "50. Line Down",
    ["BRAILLE LINE:  'The next step installs the JDK into the current directory.'",
     "     VISIBLE:  'The next step installs the JDK i', cursor=1",
     "SPEECH OUTPUT: 'The next step installs the JDK into the current directory.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "51. Line Down",
    ["BRAILLE LINE:  '4. Run the self-extracting binary.'",
     "     VISIBLE:  '4. Run the self-extracting binar', cursor=1",
     "SPEECH OUTPUT: '4. Run the self-extracting binary.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "52. Line Down",
    ["BRAILLE LINE:  'Execute the downloaded file, prepended by the path to it. For example, if the file is in the current directory, prepend it with \"./\" \(necessary if \".\" is not in the PATH'",
     "     VISIBLE:  'Execute the downloaded file, pre', cursor=1",
     "SPEECH OUTPUT: 'Execute the downloaded file, prepended by the path to it. For example, if the file is in the current directory, prepend it with \"./\" \(necessary if \".\" is not in the PATH'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "53. Line Down",
    ["BRAILLE LINE:  'environment variable\):'",
     "     VISIBLE:  'environment variable\):', cursor=1",
     "SPEECH OUTPUT: 'environment variable\):'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "54. Line Down",
    ["BRAILLE LINE:  './jdk-6<version>-linux-i586.bin'",
     "     VISIBLE:  './jdk-6<version>-linux-i586.bin', cursor=1",
     "SPEECH OUTPUT: './jdk-6<version>-linux-i586.bin'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "55. Line Down",
    ["BRAILLE LINE:  'The binary code license is displayed, and you are prompted to agree to its terms.'",
     "     VISIBLE:  'The binary code license is displ', cursor=1",
     "SPEECH OUTPUT: 'The binary code license is displayed, and you are prompted to agree to its terms.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "56. Line Down",
    ["BRAILLE LINE:  'The JDK files are installed in a directory called jdk1.6.0_<version> in the current directory. Follow this link to see its directory structure. The JDK documentation'",
     "     VISIBLE:  'The JDK files are installed in a', cursor=1",
     "SPEECH OUTPUT: 'The JDK files are installed in a directory called jdk1.6.0_<version> in the current directory. Follow this link to see its directory structure link . The JDK documentation'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "57. Line Down",
    ["BRAILLE LINE:  'is a separate download.'",
     "     VISIBLE:  'is a separate download.', cursor=1",
     "SPEECH OUTPUT: 'is a separate download.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "58. Line Down",
    ["BRAILLE LINE:  'Note about Root Access: Unbundling the software automatically creates a directory called jdk1.6.0_<version>. Note that if you choose to install the JDK into'",
     "     VISIBLE:  'Note about Root Access: Unbundli', cursor=1",
     "SPEECH OUTPUT: 'Note about Root Access: Unbundling the software automatically creates a directory called jdk1.6.0_<version>. Note that if you choose to install the JDK into'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "59. Line Down",
    ["BRAILLE LINE:  'system-wide location such as /usr/local, you must first become root to gain the necessary permissions. If you do not have root access, simply install the JDK'",
     "     VISIBLE:  'system-wide location such as /us', cursor=1",
     "SPEECH OUTPUT: 'system-wide location such as /usr/local, you must first become root to gain the necessary permissions. If you do not have root access, simply install the JDK'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "60. Line Down",
    ["BRAILLE LINE:  'into your home directory, or a subdirectory that you have permission to write to.'",
     "     VISIBLE:  'into your home directory, or a s', cursor=1",
     "SPEECH OUTPUT: 'into your home directory, or a subdirectory that you have permission to write to.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "61. Line Down",
    ["BRAILLE LINE:  'Note about Overwriting Files: If you unpack the software in a directory that contains a subdirectory named jdk1.6.0_<version>, the new software overwrites'",
     "     VISIBLE:  'Note about Overwriting Files: If', cursor=1",
     "SPEECH OUTPUT: 'Note about Overwriting Files: If you unpack the software in a directory that contains a subdirectory named jdk1.6.0_<version>, the new software overwrites'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "62. Line Down",
    ["BRAILLE LINE:  'files of the same name in that jdk1.6.0_<version> directory. Please be careful to rename the old directory if it contains files you would like to keep.'",
     "     VISIBLE:  'files of the same name in that j', cursor=1",
     "SPEECH OUTPUT: 'files of the same name in that jdk1.6.0_<version> directory. Please be careful to rename the old directory if it contains files you would like to keep.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "63. Line Down",
    ["BRAILLE LINE:  'Note about System Preferences: By default, the installation script configures the system such that the backing store for system preferences is created inside the'",
     "     VISIBLE:  'Note about System Preferences: B', cursor=1",
     "SPEECH OUTPUT: 'Note about System Preferences: By default, the installation script configures the system such that the backing store for system preferences is created inside the'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "64. Line Down",
    ["BRAILLE LINE:  'JDK's installation directory. If the JDK is installed on a network-mounted drive, it and the system preferences can be exported for sharing with Java runtime'",
     "     VISIBLE:  'JDK's installation directory. If', cursor=1",
     "SPEECH OUTPUT: 'JDK's installation directory. If the JDK is installed on a network-mounted drive, it and the system preferences can be exported for sharing with Java runtime'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "65. Line Down",
    ["BRAILLE LINE:  'environments on other machines.'",
     "     VISIBLE:  'environments on other machines.', cursor=1",
     "SPEECH OUTPUT: 'environments on other machines.", 
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "66. Line Down",
    ["BRAILLE LINE:  'See the Preferences API documentation for more information about preferences in the Java platform.'",
     "     VISIBLE:  'See the Preferences API document', cursor=1",
     "SPEECH OUTPUT: 'See the Preferences API link  documentation for more information about preferences in the Java platform.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "67. Line Down",
    ["BRAILLE LINE:  'Installation of RPM File h3'",
     "     VISIBLE:  'Installation of RPM File h3', cursor=1",
     "SPEECH OUTPUT: 'Installation of RPM File heading level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "68. Line Down",
    ["BRAILLE LINE:  'Use these instructions if you want to install JDK in the form of RPM packages. If you want to use the self-extracting binary file instead, see Installation of Self-Extracting Binary.'",
     "     VISIBLE:  'Use these instructions if you wa', cursor=1",
     "SPEECH OUTPUT: 'Use these instructions if you want to install JDK in the form of RPM packages. If you want to use the self-extracting binary file instead, see Installation of Self-Extracting Binary link .'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "69. Line Down",
    ["BRAILLE LINE:  '1. Download and check the file size.'",
     "     VISIBLE:  '1. Download and check the file s', cursor=1",
     "SPEECH OUTPUT: '1. Download and check the file size.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "70. Line Down",
    ["BRAILLE LINE:  'You can download to any directory you choose.'",
     "     VISIBLE:  'You can download to any director', cursor=1",
     "SPEECH OUTPUT: 'You can download to any directory you choose.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "71. Line Down",
    ["BRAILLE LINE:  'Before you download the file, notice its byte size provided on the download page on the web site. Once the download has completed, compare that file size to the'",
     "     VISIBLE:  'Before you download the file, no', cursor=1",
     "SPEECH OUTPUT: 'Before you download the file, notice its byte size provided on the download page on the web site. Once the download has completed, compare that file size to the'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "72. Line Down",
    ["BRAILLE LINE:  'size of the downloaded file to make sure they are equal.'",
     "     VISIBLE:  'size of the downloaded file to m', cursor=1",
     "SPEECH OUTPUT: 'size of the downloaded file to make sure they are equal.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "73. Line Down",
    ["BRAILLE LINE:  '2. Become root by running the su command and entering the super-user password.'",
     "     VISIBLE:  '2. Become root by running the su', cursor=1",
     "SPEECH OUTPUT: '2. Become root by running the su command and entering the super-user password.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "74. Line Down",
    ["BRAILLE LINE:  '3. Extract and install the contents of the downloaded file.'",
     "     VISIBLE:  '3. Extract and install the conte', cursor=1",
     "SPEECH OUTPUT: '3. Extract and install the contents of the downloaded file.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "75. Line Down",
    ["BRAILLE LINE:  'Change directory to where the downloaded file is located and run these commands to first set the executable permissions and then run the binary to extract and'",
     "     VISIBLE:  'Change directory to where the do', cursor=1",
     "SPEECH OUTPUT: 'Change directory to where the downloaded file is located and run these commands to first set the executable permissions and then run the binary to extract and'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "76. Line Down",
    ["BRAILLE LINE:  'run the RPM file:'",
     "     VISIBLE:  'run the RPM file:', cursor=1",
     "SPEECH OUTPUT: 'run the RPM file:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "77. Line Down",
    ["BRAILLE LINE:  'chmod a+x jdk-6<version>-linux-i586-rpm.bin'",
     "     VISIBLE:  'chmod a+x jdk-6<version>-linux-i', cursor=1",
     "SPEECH OUTPUT: 'chmod a+x jdk-6<version>-linux-i586-rpm.bin", 
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "78. Line Down",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "79. Line Down",
    ["BRAILLE LINE:  './jdk-6<version>-linux-i586-rpm.bin'",
     "     VISIBLE:  './jdk-6<version>-linux-i586-rpm.', cursor=1",
     "SPEECH OUTPUT: './jdk-6<version>-linux-i586-rpm.bin", 
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "80. Line Down",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "81. Line Down",
    ["BRAILLE LINE:  'Note that the initial \"./\" is required if you do not have \".\" in your PATH environment variable.'",
     "     VISIBLE:  'Note that the initial \"./\" is re', cursor=1",
     "SPEECH OUTPUT: 'Note that the initial \"./\" is required if you do not have \".\" in your PATH environment variable.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "82. Line Down",
    ["BRAILLE LINE:  'The script displays a binary license agreement, which you are asked to agree to before installation can proceed. Once you have agreed to the license, the install'",
     "     VISIBLE:  'The script displays a binary lic', cursor=1",
     "SPEECH OUTPUT: 'The script displays a binary license agreement, which you are asked to agree to before installation can proceed. Once you have agreed to the license, the install'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "83. Line Down",
    ["BRAILLE LINE:  'script creates and runs the file jdk-6<version>-linux-i586.rpm in the current directory.'",
     "     VISIBLE:  'script creates and runs the file', cursor=1",
     "SPEECH OUTPUT: 'script creates and runs the file jdk-6<version>-linux-i586.rpm in the current directory.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "84. Line Down",
    ["BRAILLE LINE:  'NOTE - If instead you want to only extract the RPM file but not install it, you can run the .bin file with the -x argument. You do not need to be root to do this.'",
     "     VISIBLE:  'NOTE - If instead you want to on', cursor=1",
     "SPEECH OUTPUT: 'NOTE - If instead you want to only extract the RPM file but not install it, you can run the .bin file with the -x argument. You do not need to be root to do this.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "85. Line Down",
    ["BRAILLE LINE:  '4. Delete the bin and rpm file if you want to save disk space.'",
     "     VISIBLE:  '4. Delete the bin and rpm file i', cursor=1",
     "SPEECH OUTPUT: '4. Delete the bin and rpm file if you want to save disk space.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "86. Line Down",
    ["BRAILLE LINE:  '5. Exit the root shell.'",
     "     VISIBLE:  '5. Exit the root shell.', cursor=1",
     "SPEECH OUTPUT: '5. Exit the root shell.", 
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "87. Line Down",
    ["BRAILLE LINE:  'The RPM packages creates two links /usr/java/latest and /usr/java/default. '",
     "     VISIBLE:  'The RPM packages creates two lin', cursor=1",
     "SPEECH OUTPUT: 'The RPM packages creates two links /usr/java/latest and /usr/java/default.  ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "88. Line Down",
    ["BRAILLE LINE:  '• The /usr/java/latest link will always point to the version of Java that Sun Microsystems considers the latest version.  Subsequent upgrades of the packages will overwrite this'",
     "     VISIBLE:  '• The /usr/java/latest link will', cursor=1",
     "SPEECH OUTPUT: '• The /usr/java/latest link will always point to the version of Java that Sun Microsystems considers the latest version.  Subsequent upgrades of the packages will overwrite this'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "89. Line Down",
    ["BRAILLE LINE:  'value if it is not the latest version.'",
     "     VISIBLE:  'value if it is not the latest ve', cursor=1",
     "SPEECH OUTPUT: 'value if it is not the latest version.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "90. Line Down",
    ["BRAILLE LINE:  '• By default, /usr/java/default points to /usr/java/latest. However, if administrators change /usr/java/default to  point to another version of Java, subsequent package upgrades'",
     "     VISIBLE:  '• By default, /usr/java/default ', cursor=1",
     "SPEECH OUTPUT: '• By default, /usr/java/default points to /usr/java/latest. However, if administrators change /usr/java/default to  point to another version of Java, subsequent package upgrades'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "91. Line Down",
    ["BRAILLE LINE:  'will be provided by the administrators and cannot be overwritten.'",
     "     VISIBLE:  'will be provided by the administ', cursor=1",
     "SPEECH OUTPUT: 'will be provided by the administrators and cannot be overwritten.", 
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "92. Line Down",
    ["BRAILLE LINE:  'When the JDK is installed, links to  javac jar and javadoc are also created apart from the JRE links. These links point to the appropriate tool referenced by /usr/java/default. This'",
     "     VISIBLE:  'When the JDK is installed, links', cursor=1",
     "SPEECH OUTPUT: 'When the JDK is installed, links to  javac jar and javadoc are also created apart from the JRE links. These links point to the appropriate tool referenced by /usr/java/default. This'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "93. Line Down",
    ["BRAILLE LINE:  'allows the user to easily run the default version of these Java tools.'",
     "     VISIBLE:  'allows the user to easily run th', cursor=1",
     "SPEECH OUTPUT: 'allows the user to easily run the default version of these Java tools.", 
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "94. Line Down",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "95. Line Down",
    ["BRAILLE LINE:  'A new service script, named jexec, is added to /etc/init.d. This script allows users to directly execute any standalone JAR file that has an execution permission set. This can be'",
     "     VISIBLE:  'A new service script, named jexe', cursor=1",
     "SPEECH OUTPUT: 'A new service script, named jexec, is added to /etc/init.d. This script allows users to directly execute any standalone JAR file that has an execution permission set. This can be'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "96. Line Down",
    ["BRAILLE LINE:  'demonstrated using an example from the JDK:'",
     "     VISIBLE:  'demonstrated using an example fr', cursor=1",
     "SPEECH OUTPUT: 'demonstrated using an example from the JDK:", 
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "97. Line Down",
    ["BRAILLE LINE:  '	cd /usr/java/jdk1.6.0/demo/jfc/SwingSet2'",
     "     VISIBLE:  '	cd /usr/java/jdk1.6.0/demo/jfc/', cursor=1",
     "SPEECH OUTPUT: '	cd /usr/java/jdk1.6.0/demo/jfc/SwingSet2", 
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "98. Line Down",
    ["BRAILLE LINE:  '	chmod +x SwingSet2.jar'",
     "     VISIBLE:  '	chmod +x SwingSet2.jar', cursor=1",
     "SPEECH OUTPUT: '	chmod +x SwingSet2.jar", 
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "99. Line Down",
    ["BRAILLE LINE:  '	./SwingSet2.jar'",
     "     VISIBLE:  '	./SwingSet2.jar', cursor=1",
     "SPEECH OUTPUT: '	./SwingSet2.jar'"]))

########################################################################
# Up Arrow.
#
sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "1. Line Up",
    ["BRAILLE LINE:  '	chmod +x SwingSet2.jar'",
     "     VISIBLE:  '	chmod +x SwingSet2.jar', cursor=1",
     "SPEECH OUTPUT: '	chmod +x SwingSet2.jar", 
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Up",
    ["BRAILLE LINE:  '	cd /usr/java/jdk1.6.0/demo/jfc/SwingSet2'",
     "     VISIBLE:  '	cd /usr/java/jdk1.6.0/demo/jfc/', cursor=1",
     "SPEECH OUTPUT: '	cd /usr/java/jdk1.6.0/demo/jfc/SwingSet2", 
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Up",
    ["BRAILLE LINE:  'demonstrated using an example from the JDK:'",
     "     VISIBLE:  'demonstrated using an example fr', cursor=1",
     "SPEECH OUTPUT: 'demonstrated using an example from the JDK:", 
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Up",
    ["BRAILLE LINE:  'A new service script, named jexec, is added to /etc/init.d. This script allows users to directly execute any standalone JAR file that has an execution permission set. This can be'",
     "     VISIBLE:  'A new service script, named jexe', cursor=1",
     "SPEECH OUTPUT: 'A new service script, named jexec, is added to /etc/init.d. This script allows users to directly execute any standalone JAR file that has an execution permission set. This can be'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Up",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Up",
    ["BRAILLE LINE:  'allows the user to easily run the default version of these Java tools.'",
     "     VISIBLE:  'allows the user to easily run th', cursor=1",
     "SPEECH OUTPUT: 'allows the user to easily run the default version of these Java tools.", 
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Up",
    ["BRAILLE LINE:  'When the JDK is installed, links to  javac jar and javadoc are also created apart from the JRE links. These links point to the appropriate tool referenced by /usr/java/default. This'",
     "     VISIBLE:  'When the JDK is installed, links', cursor=1",
     "SPEECH OUTPUT: 'When the JDK is installed, links to  javac jar and javadoc are also created apart from the JRE links. These links point to the appropriate tool referenced by /usr/java/default. This'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Up",
    ["BRAILLE LINE:  'will be provided by the administrators and cannot be overwritten.'",
     "     VISIBLE:  'will be provided by the administ', cursor=1",
     "SPEECH OUTPUT: 'will be provided by the administrators and cannot be overwritten.", 
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Up",
    ["BRAILLE LINE:  '• By default, /usr/java/default points to /usr/java/latest. However, if administrators change /usr/java/default to  point to another version of Java, subsequent package upgrades'",
     "     VISIBLE:  '• By default, /usr/java/default ', cursor=1",
     "SPEECH OUTPUT: '• By default, /usr/java/default points to /usr/java/latest. However, if administrators change /usr/java/default to  point to another version of Java, subsequent package upgrades'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "10. Line Up",
    ["BRAILLE LINE:  'value if it is not the latest version.'",
     "     VISIBLE:  'value if it is not the latest ve', cursor=1",
     "SPEECH OUTPUT: 'value if it is not the latest version.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "11. Line Up",
    ["BRAILLE LINE:  '• The /usr/java/latest link will always point to the version of Java that Sun Microsystems considers the latest version.  Subsequent upgrades of the packages will overwrite this'",
     "     VISIBLE:  '• The /usr/java/latest link will', cursor=1",
     "SPEECH OUTPUT: '• The /usr/java/latest link will always point to the version of Java that Sun Microsystems considers the latest version.  Subsequent upgrades of the packages will overwrite this'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "12a. Line Up",
    ["BUG? - We should lose the final space in the braille line.",
     "BRAILLE LINE:  'The RPM packages creates two links /usr/java/latest and /usr/java/default. '",
     "     VISIBLE:  'The RPM packages creates two lin', cursor=1",
     "SPEECH OUTPUT: 'The RPM packages creates two links /usr/java/latest and /usr/java/default.  ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "12b. Line Up",
    ["BRAILLE LINE:  '5. Exit the root shell.'",
     "     VISIBLE:  '5. Exit the root shell.', cursor=1",
     "SPEECH OUTPUT: '5. Exit the root shell.", 
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "13. Line Up",
    ["BRAILLE LINE:  '4. Delete the bin and rpm file if you want to save disk space.'",
     "     VISIBLE:  '4. Delete the bin and rpm file i', cursor=1",
     "SPEECH OUTPUT: '4. Delete the bin and rpm file if you want to save disk space.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "14. Line Up",
    ["BRAILLE LINE:  'NOTE - If instead you want to only extract the RPM file but not install it, you can run the .bin file with the -x argument. You do not need to be root to do this.'",
     "     VISIBLE:  'NOTE - If instead you want to on', cursor=1",
     "SPEECH OUTPUT: 'NOTE - If instead you want to only extract the RPM file but not install it, you can run the .bin file with the -x argument. You do not need to be root to do this.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "15. Line Up",
    ["BRAILLE LINE:  'script creates and runs the file jdk-6<version>-linux-i586.rpm in the current directory.'",
     "     VISIBLE:  'script creates and runs the file', cursor=1",
     "SPEECH OUTPUT: 'script creates and runs the file jdk-6<version>-linux-i586.rpm in the current directory.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "16. Line Up",
    ["BRAILLE LINE:  'The script displays a binary license agreement, which you are asked to agree to before installation can proceed. Once you have agreed to the license, the install'",
     "     VISIBLE:  'The script displays a binary lic', cursor=1",
     "SPEECH OUTPUT: 'The script displays a binary license agreement, which you are asked to agree to before installation can proceed. Once you have agreed to the license, the install'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "17. Line Up",
    ["BRAILLE LINE:  'Note that the initial \"./\" is required if you do not have \".\" in your PATH environment variable.'",
     "     VISIBLE:  'Note that the initial \"./\" is re', cursor=1",
     "SPEECH OUTPUT: 'Note that the initial \"./\" is required if you do not have \".\" in your PATH environment variable.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "18. Line Up",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "19. Line Up",
    ["BRAILLE LINE:  './jdk-6<version>-linux-i586-rpm.bin'",
     "     VISIBLE:  './jdk-6<version>-linux-i586-rpm.', cursor=1",
     "SPEECH OUTPUT: './jdk-6<version>-linux-i586-rpm.bin", 
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "20. Line Up",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "21. Line Up",
    ["BRAILLE LINE:  'chmod a+x jdk-6<version>-linux-i586-rpm.bin'",
     "     VISIBLE:  'chmod a+x jdk-6<version>-linux-i', cursor=1",
     "SPEECH OUTPUT: 'chmod a+x jdk-6<version>-linux-i586-rpm.bin", 
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "22. Line Up",
    ["BRAILLE LINE:  'run the RPM file:'",
     "     VISIBLE:  'run the RPM file:', cursor=1",
     "SPEECH OUTPUT: 'run the RPM file:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "23a. Line Up",
    ["BRAILLE LINE:  'Change directory to where the downloaded file is located and run these commands to first set the executable permissions and then run the binary to extract and'",
     "     VISIBLE:  'Change directory to where the do', cursor=1",
     "SPEECH OUTPUT: 'Change directory to where the downloaded file is located and run these commands to first set the executable permissions and then run the binary to extract and'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "23b. Line Up",
    ["BRAILLE LINE:  '3. Extract and install the contents of the downloaded file.'",
     "     VISIBLE:  '3. Extract and install the conte', cursor=1",
     "SPEECH OUTPUT: '3. Extract and install the contents of the downloaded file.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "23c. Line Up",
    ["BRAILLE LINE:  '2. Become root by running the su command and entering the super-user password.'",
     "     VISIBLE:  '2. Become root by running the su', cursor=1",
     "SPEECH OUTPUT: '2. Become root by running the su command and entering the super-user password.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "24. Line Up",
    ["BRAILLE LINE:  'size of the downloaded file to make sure they are equal.'",
     "     VISIBLE:  'size of the downloaded file to m', cursor=1",
     "SPEECH OUTPUT: 'size of the downloaded file to make sure they are equal.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "25. Line Up",
    ["BRAILLE LINE:  'Before you download the file, notice its byte size provided on the download page on the web site. Once the download has completed, compare that file size to the'",
     "     VISIBLE:  'Before you download the file, no', cursor=1",
     "SPEECH OUTPUT: 'Before you download the file, notice its byte size provided on the download page on the web site. Once the download has completed, compare that file size to the'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "26a. Line Up",
    ["BRAILLE LINE:  'You can download to any directory you choose.'",
     "     VISIBLE:  'You can download to any director', cursor=1",
     "SPEECH OUTPUT: 'You can download to any directory you choose.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "26b. Line Up",
    ["BRAILLE LINE:  '1. Download and check the file size.'",
     "     VISIBLE:  '1. Download and check the file s', cursor=1",
     "SPEECH OUTPUT: '1. Download and check the file size.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "27. Line Up",
    ["BRAILLE LINE:  'Use these instructions if you want to install JDK in the form of RPM packages. If you want to use the self-extracting binary file instead, see Installation of Self-Extracting Binary.'",
     "     VISIBLE:  'Use these instructions if you wa', cursor=1",
     "SPEECH OUTPUT: 'Use these instructions if you want to install JDK in the form of RPM packages. If you want to use the self-extracting binary file instead, see Installation of Self-Extracting Binary link .'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "28. Line Up",
    ["BRAILLE LINE:  'Installation of RPM File h3'",
     "     VISIBLE:  'Installation of RPM File h3', cursor=1",
     "SPEECH OUTPUT: 'Installation of RPM File heading level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "29. Line Up",
    ["BRAILLE LINE:  'See the Preferences API documentation for more information about preferences in the Java platform.'",
     "     VISIBLE:  'See the Preferences API document', cursor=1",
     "SPEECH OUTPUT: 'See the Preferences API link  documentation for more information about preferences in the Java platform.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "30. Line Up",
    ["BRAILLE LINE:  'environments on other machines.'",
     "     VISIBLE:  'environments on other machines.', cursor=1",
     "SPEECH OUTPUT: 'environments on other machines. ", 
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "31. Line Up",
    ["BRAILLE LINE:  'JDK's installation directory. If the JDK is installed on a network-mounted drive, it and the system preferences can be exported for sharing with Java runtime'",
     "     VISIBLE:  'JDK's installation directory. If', cursor=1",
     "SPEECH OUTPUT: 'JDK's installation directory. If the JDK is installed on a network-mounted drive, it and the system preferences can be exported for sharing with Java runtime'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "32. Line Up",
    ["BRAILLE LINE:  'Note about System Preferences: By default, the installation script configures the system such that the backing store for system preferences is created inside the'",
     "     VISIBLE:  'Note about System Preferences: B', cursor=1",
     "SPEECH OUTPUT: 'Note about System Preferences: By default, the installation script configures the system such that the backing store for system preferences is created inside the'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "33. Line Up",
    ["BRAILLE LINE:  'files of the same name in that jdk1.6.0_<version> directory. Please be careful to rename the old directory if it contains files you would like to keep.'",
     "     VISIBLE:  'files of the same name in that j', cursor=1",
     "SPEECH OUTPUT: 'files of the same name in that jdk1.6.0_<version> directory. Please be careful to rename the old directory if it contains files you would like to keep.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "34. Line Up",
    ["BRAILLE LINE:  'Note about Overwriting Files: If you unpack the software in a directory that contains a subdirectory named jdk1.6.0_<version>, the new software overwrites'",
     "     VISIBLE:  'Note about Overwriting Files: If', cursor=1",
     "SPEECH OUTPUT: 'Note about Overwriting Files: If you unpack the software in a directory that contains a subdirectory named jdk1.6.0_<version>, the new software overwrites'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "35. Line Up",
    ["BRAILLE LINE:  'into your home directory, or a subdirectory that you have permission to write to.'",
     "     VISIBLE:  'into your home directory, or a s', cursor=1",
     "SPEECH OUTPUT: 'into your home directory, or a subdirectory that you have permission to write to.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "36. Line Up",
    ["BRAILLE LINE:  'system-wide location such as /usr/local, you must first become root to gain the necessary permissions. If you do not have root access, simply install the JDK'",
     "     VISIBLE:  'system-wide location such as /us', cursor=1",
     "SPEECH OUTPUT: 'system-wide location such as /usr/local, you must first become root to gain the necessary permissions. If you do not have root access, simply install the JDK'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "37. Line Up",
    ["BRAILLE LINE:  'Note about Root Access: Unbundling the software automatically creates a directory called jdk1.6.0_<version>. Note that if you choose to install the JDK into'",
     "     VISIBLE:  'Note about Root Access: Unbundli', cursor=1",
     "SPEECH OUTPUT: 'Note about Root Access: Unbundling the software automatically creates a directory called jdk1.6.0_<version>. Note that if you choose to install the JDK into'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "38. Line Up",
    ["BRAILLE LINE:  'is a separate download.'",
     "     VISIBLE:  'is a separate download.', cursor=1",
     "SPEECH OUTPUT: 'is a separate download.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "39. Line Up",
    ["BRAILLE LINE:  'The JDK files are installed in a directory called jdk1.6.0_<version> in the current directory. Follow this link to see its directory structure. The JDK documentation'",
     "     VISIBLE:  'The JDK files are installed in a', cursor=1",
     "SPEECH OUTPUT: 'The JDK files are installed in a directory called jdk1.6.0_<version> in the current directory. Follow this link to see its directory structure link . The JDK documentation'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "40. Line Up",
    ["BRAILLE LINE:  'The binary code license is displayed, and you are prompted to agree to its terms.'",
     "     VISIBLE:  'The binary code license is displ', cursor=1",
     "SPEECH OUTPUT: 'The binary code license is displayed, and you are prompted to agree to its terms.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "41. Line Up",
    ["BRAILLE LINE:  './jdk-6<version>-linux-i586.bin'",
     "     VISIBLE:  './jdk-6<version>-linux-i586.bin', cursor=1",
     "SPEECH OUTPUT: './jdk-6<version>-linux-i586.bin'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "42. Line Up",
    ["BRAILLE LINE:  'environment variable\):'",
     "     VISIBLE:  'environment variable\):', cursor=1",
     "SPEECH OUTPUT: 'environment variable\):'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "43. Line Up",
    ["BRAILLE LINE:  'Execute the downloaded file, prepended by the path to it. For example, if the file is in the current directory, prepend it with \"./\" \(necessary if \".\" is not in the PATH'",
     "     VISIBLE:  'Execute the downloaded file, pre', cursor=1",
     "SPEECH OUTPUT: 'Execute the downloaded file, prepended by the path to it. For example, if the file is in the current directory, prepend it with \"./\" \(necessary if \".\" is not in the PATH'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "44. Line Up",
    ["BRAILLE LINE:  '4. Run the self-extracting binary.'",
     "     VISIBLE:  '4. Run the self-extracting binar', cursor=1",
     "SPEECH OUTPUT: '4. Run the self-extracting binary.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "45. Line Up",
    ["BRAILLE LINE:  'The next step installs the JDK into the current directory.'",
     "     VISIBLE:  'The next step installs the JDK i', cursor=1",
     "SPEECH OUTPUT: 'The next step installs the JDK into the current directory.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "46. Line Up",
    ["BRAILLE LINE:  '3. Change directory to the location where you would like the files to be installed.'",
     "     VISIBLE:  '3. Change directory to the locat', cursor=1",
     "SPEECH OUTPUT: '3. Change directory to the location where you would like the files to be installed.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "47. Line Up",
    ["BRAILLE LINE:  'chmod +x jdk-6<version>-linux-i586.bin'",
     "     VISIBLE:  'chmod +x jdk-6<version>-linux-i5', cursor=1",
     "SPEECH OUTPUT: 'chmod +x jdk-6<version>-linux-i586.bin'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "48. Line Up",
    ["BRAILLE LINE:  'Run this command:'",
     "     VISIBLE:  'Run this command:', cursor=1",
     "SPEECH OUTPUT: 'Run this command:",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "49. Line Up",
    ["BRAILLE LINE:  '2. Make sure that execute permissions are set on the self-extracting binary.'",
     "     VISIBLE:  '2. Make sure that execute permis', cursor=1",
     "SPEECH OUTPUT: '2. Make sure that execute permissions are set on the self-extracting binary.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "50. Line Up",
    ["BRAILLE LINE:  'size of the downloaded file to make sure they are equal.'",
     "     VISIBLE:  'size of the downloaded file to m', cursor=1",
     "SPEECH OUTPUT: 'size of the downloaded file to make sure they are equal.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "51. Line Up",
    ["BRAILLE LINE:  'Before you download the file, notice its byte size provided on the download page on the web site. Once the download has completed, compare that file size to the'",
     "     VISIBLE:  'Before you download the file, no', cursor=1",
     "SPEECH OUTPUT: 'Before you download the file, notice its byte size provided on the download page on the web site. Once the download has completed, compare that file size to the'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "52. Line Up",
    ["BRAILLE LINE:  'You can download to any directory you choose; it does not have to be the directory where you want to install the JDK.'",
     "     VISIBLE:  'You can download to any director', cursor=1",
     "SPEECH OUTPUT: 'You can download to any directory you choose; it does not have to be the directory where you want to install the JDK.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "53. Line Up",
    ["BRAILLE LINE:  '1. Download and check the download file size to ensure that you have downloaded the full, uncorrupted software bundle.'",
     "     VISIBLE:  '1. Download and check the downlo', cursor=1",
     "SPEECH OUTPUT: '1. Download and check the download file size to ensure that you have downloaded the full, uncorrupted software bundle.",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "54. Line Up",
    ["BRAILLE LINE:  'Use these instructions if you want to use the self-extracting binary file to install the JDK. If you want to install RPM packages instead, see Installation of RPM File.'",
     "     VISIBLE:  'Use these instructions if you wa', cursor=1",
     "SPEECH OUTPUT: 'Use these instructions if you want to use the self-extracting binary file to install the JDK. If you want to install RPM packages instead, see Installation of RPM File link .'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "55. Line Up",
    ["BRAILLE LINE:  'Installation of Self-Extracting Binary h3'",
     "     VISIBLE:  'Installation of Self-Extracting ', cursor=1",
     "SPEECH OUTPUT: 'Installation of Self-Extracting Binary heading level 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "56. Line Up",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "57. Line Up",
    ["BRAILLE LINE:  './jdk-6u1-linux-i586.bin'",
     "     VISIBLE:  './jdk-6u1-linux-i586.bin', cursor=1",
     "SPEECH OUTPUT: './jdk-6u1-linux-i586.bin",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "58. Line Up",
    ["BRAILLE LINE:  'would become:'",
     "     VISIBLE:  'would become:', cursor=1",
     "SPEECH OUTPUT: 'would become:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "59. Line Up",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "60. Line Up",
    ["BRAILLE LINE:  './jdk-6<version>-linux-i586.bin'",
     "     VISIBLE:  './jdk-6<version>-linux-i586.bin', cursor=1",
     "SPEECH OUTPUT: './jdk-6<version>-linux-i586.bin",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "61. Line Up",
    ["BRAILLE LINE:  'For example, if you were downloading update 6_01, the following command:'",
     "     VISIBLE:  'For example, if you were downloa', cursor=1",
     "SPEECH OUTPUT: 'For example, if you were downloading update 6_01, the following command:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "62. Line Up",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=1"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "63. Line Up",
    ["BRAILLE LINE:  '<version>'",
     "     VISIBLE:  '<version>', cursor=1",
     "SPEECH OUTPUT: '<version>",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "64. Line Up",
    ["BRAILLE LINE:  'Note: For any text on this page containing the following notation, you must substitute the appropriate JDK update version number for the notation.'",
     "     VISIBLE:  'Note: For any text on this page ', cursor=1",
     "SPEECH OUTPUT: 'Note: For any text on this page containing the following notation, you must substitute the appropriate JDK update version number for the notation.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "65. Line Up",
    ["BRAILLE LINE:  'Choose the install format that is most suitable to your needs.'",
     "     VISIBLE:  'Choose the install format that i', cursor=1",
     "SPEECH OUTPUT: 'Choose the install format that is most suitable to your needs.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "66. Line Up",
    ["BRAILLE LINE:  'installation on Linux. To use this bundle, see Installation of RPM File below.'",
     "     VISIBLE:  'installation on Linux. To use th', cursor=1",
     "SPEECH OUTPUT: 'installation on Linux. To use this bundle, see Installation of RPM File link  below.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "67. Line Up",
    ["BRAILLE LINE:  '• RPM Packages - A rpm.bin file containing RPM packages, installed with the rpm utility. Requires root access to install. RPM packages are the recommended method for'",
     "     VISIBLE:  '• RPM Packages - A rpm.bin file ', cursor=1",
     "SPEECH OUTPUT: '• RPM Packages - A rpm.bin file containing RPM packages, installed with the rpm utility. Requires root access to install. RPM packages are the recommended method for'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "68. Line Up",
    ["BRAILLE LINE:  'Installation of Self-Extracting Binary below.'",
     "     VISIBLE:  'Installation of Self-Extracting ', cursor=1",
     "SPEECH OUTPUT: 'Installation of Self-Extracting Binary link  below.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "69. Line Up",
    ["BRAILLE LINE:  'easily be installed in any location. As long as you are not root user, it cannot displace the system version of the Java platform suppled by Linux. To use this file, see'",
     "     VISIBLE:  'easily be installed in any locat', cursor=1",
     "SPEECH OUTPUT: 'easily be installed in any location. As long as you are not root user, it cannot displace the system version of the Java platform suppled by Linux. To use this file, see'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "70a. Line Up",
    ["BRAILLE LINE:  '• Self-extracting Binary File - This file can be used to install the JDK in a location chosen by the user. This one can be installed by anyone (not only root users), and it can'",
     "     VISIBLE:  '• Self-extracting Binary File - ', cursor=1",
     "SPEECH OUTPUT: '• Self-extracting Binary File - This file can be used to install the JDK in a location chosen by the user. This one can be installed by anyone (not only root users), and it can'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "70b. Line Up",
    ["BRAILLE LINE:  'Install formats - This version of the JDK is available in two installation formats.'",
     "     VISIBLE:  'Install formats - This version o', cursor=1",
     "SPEECH OUTPUT: 'Install formats - This version of the JDK is available in two installation formats.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "71. Line Up",
    ["BRAILLE LINE:  '• Java Web Start Installation Notes'",
     "     VISIBLE:  '• Java Web Start Installation No', cursor=1",
     "SPEECH OUTPUT: '• Java Web Start Installation Notes link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "72. Line Up",
    ["BRAILLE LINE:  '• Java Plugin Browser Registration Instructions'",
     "     VISIBLE:  '• Java Plugin Browser Registrati', cursor=1",
     "SPEECH OUTPUT: '• Java Plugin Browser Registration Instructions link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "73. Line Up",
    ["BRAILLE LINE:  'Installing the JDK automatically installs the Java Plugin and Java Web Start. Note that the Java Plugin needs to be registered with the browser. After installing the JDK, refer to:'",
     "     VISIBLE:  'Installing the JDK automatically', cursor=1",
     "SPEECH OUTPUT: 'Installing the JDK automatically installs the Java Plugin and Java Web Start. Note that the Java Plugin needs to be registered with the browser. After installing the JDK, refer to:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "74. Line Up",
    ["BRAILLE LINE:  'Installation Instructions h2'",
     "     VISIBLE:  'Installation Instructions h2', cursor=1",
     "SPEECH OUTPUT: 'Installation Instructions heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "75. Line Up",
    ["BRAILLE LINE:  'For issues, see the Troubleshooting section below.'",
     "     VISIBLE:  'For issues, see the Troubleshoot', cursor=1",
     "SPEECH OUTPUT: 'For issues, see the Troubleshooting link  section below.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "76. Line Up",
    ["BRAILLE LINE:  'See supported System Configurations for information about supported platforms, operating systems, desktop managers, and browsers.'",
     "     VISIBLE:  'See supported System Configurati', cursor=1",
     "SPEECH OUTPUT: 'See supported System Configurations link  for information about supported platforms, operating systems, desktop managers, and browsers.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "77. Line Up",
    ["BRAILLE LINE:  'System Requirements h2'",
     "     VISIBLE:  'System Requirements h2', cursor=1",
     "SPEECH OUTPUT: 'System Requirements heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "78. Line Up",
    ["BRAILLE LINE:  'Troubleshooting'",
     "     VISIBLE:  'Troubleshooting', cursor=1",
     "SPEECH OUTPUT: 'Troubleshooting link",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "79. Line Up",
    ["BRAILLE LINE:  'Java Web Start Installation Notes'",
     "     VISIBLE:  'Java Web Start Installation Note', cursor=1",
     "SPEECH OUTPUT: 'Java Web Start Installation Notes link",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "80. Line Up",
    ["BRAILLE LINE:  'Java Plugin Browser Registration Instructions'",
     "     VISIBLE:  'Java Plugin Browser Registration', cursor=1",
     "SPEECH OUTPUT: 'Java Plugin Browser Registration Instructions link",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "81. Line Up",
    ["BRAILLE LINE:  '   Installation of RPM File'",
     "     VISIBLE:  '   Installation of RPM File', cursor=1",
     "SPEECH OUTPUT: '    Installation of RPM File link ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "82. Line Up",
    ["BRAILLE LINE:  'Installation of Self-Extracting Binary'",
     "     VISIBLE:  'Installation of Self-Extracting ', cursor=1",
     "SPEECH OUTPUT: 'Installation of Self-Extracting Binary link ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "84. Line Up",
    ["BRAILLE LINE:  'JDK Installation Instructions'",
     "     VISIBLE:  'JDK Installation Instructions', cursor=1",
     "SPEECH OUTPUT: 'JDK Installation Instructions link ",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "85. Line Up",
    ["BRAILLE LINE:  'System Requirements'",
     "     VISIBLE:  'System Requirements', cursor=1",
     "SPEECH OUTPUT: 'System Requirements link",
     "'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "86. Line Up",
    ["BRAILLE LINE:  'Contents h2'",
     "     VISIBLE:  'Contents h2', cursor=1",
     "SPEECH OUTPUT: 'Contents heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "87. Line Up",
    ["BRAILLE LINE:  'JDK Documentation'",
     "     VISIBLE:  'JDK Documentation', cursor=1",
     "SPEECH OUTPUT: 'JDK Documentation link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "88. Line Up",
    ["BRAILLE LINE:  'Separator'",
     "     VISIBLE:  'Separator', cursor=1",
     "SPEECH OUTPUT: 'separator'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "89. Line Up",
    ["BRAILLE LINE:  'Linux Installation (32-bit) h1'",
     "     VISIBLE:  'Linux Installation (32-bit) h1', cursor=1",
     "SPEECH OUTPUT: 'Linux Installation (32-bit) heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "90. Line Up",
    ["BRAILLE LINE:  'JavaTM SE 6 Release Notes'",
     "     VISIBLE:  'JavaTM SE 6 Release Notes', cursor=1",
     "SPEECH OUTPUT: 'JavaTM SE 6 Release Notes'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "91. Line Up",
    ["BRAILLE LINE:  ''",
     "     VISIBLE:  '', cursor=0",
     "SPEECH OUTPUT: 'blank'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "92. Line Up",
    ["BRAILLE LINE:  'APIs Downloads Products Support Training Participate'",
     "     VISIBLE:  'APIs Downloads Products Support ', cursor=1",
     "SPEECH OUTPUT: 'APIs link Downloads link Products link Support link Training link Participate link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "93. Line Up",
    ["BRAILLE LINE:  '» search tips  Search $l Submit Search Button Home Page Image'",
     "     VISIBLE:  '» search tips  Search $l Submit ', cursor=1",
     "SPEECH OUTPUT: '»  search tips link   text Search Submit Search button Home Page link image'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "94. Line Up",
    ["BRAILLE LINE:  'Skip to Content Sun Java Solaris Communities My SDN Account Join SDN'",
     "     VISIBLE:  'Skip to Content Sun Java Solaris', cursor=1",
     "SPEECH OUTPUT: 'Skip to Content link Sun link Java link Solaris link Communities link My SDN Account link Join SDN link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "95. Line Up",
    [""]))

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
