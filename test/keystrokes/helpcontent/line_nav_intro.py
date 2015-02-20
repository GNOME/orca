#!/usr/bin/python

"""Test of learn mode."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

sequence.append(KeyPressAction(0, None, "KP_Insert"))
sequence.append(TypeAction("h"))
sequence.append(KeyReleaseAction(0, None, "KP_Insert"))

sequence.append(KeyComboAction("F1"))
sequence.append(PauseAction(2000))

sequence.append(KeyComboAction("k"))
sequence.append(KeyComboAction("Return"))
sequence.append(PauseAction(2000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "1. Down",
    ["BRAILLE LINE:  ' Next $l'",
     "     VISIBLE:  ' Next $l', cursor=2",
     "SPEECH OUTPUT: 'Next link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Down",
    ["BRAILLE LINE:  ' Welcome to Orca h1'",
     "     VISIBLE:  ' Welcome to Orca h1', cursor=2",
     "SPEECH OUTPUT: 'Welcome to Orca'",
     "SPEECH OUTPUT: 'heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Down",
    ["BRAILLE LINE:  ' Orca is a free, open source, flexible, and extensible screen reader that provides access to the graphical desktop via speech and refreshable braille.'",
     "     VISIBLE:  'Orca is a free, open source, fle', cursor=1",
     "SPEECH OUTPUT: 'Orca is a free, open source, flexible, and extensible '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Down",
    ["BRAILLE LINE:  'Orca is a free, open source, flexible, and extensible screen reader that provides access to the graphical desktop via speech and refreshable braille.'",
     "     VISIBLE:  'Orca is a free, open source, fle', cursor=1",
     "SPEECH OUTPUT: 'screen reader that provides access to the graphical desktop via speech '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Down",
    ["BRAILLE LINE:  'Orca is a free, open source, flexible, and extensible screen reader that provides access to the graphical desktop via speech and refreshable braille.'",
     "     VISIBLE:  'Orca is a free, open source, fle', cursor=1",
     "SPEECH OUTPUT: 'and refreshable braille.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Down",
    ["BRAILLE LINE:  ' Orca works with applications and toolkits that support the Assistive Technology Service Provider Interface (AT-SPI), which is the primary assistive technology infrastructure for Linux and Solaris. Applications and toolkits supporting the AT-SPI include the GNOME Gtk+ toolkit, the Java platform's Swing toolkit, LibreOffice, Gecko, and WebKitGtk. AT-SPI support for the KDE Qt toolkit is being pursued.'",
     "     VISIBLE:  'Orca works with applications and', cursor=1",
     "SPEECH OUTPUT: 'Orca works with applications and toolkits that support the Assistive '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Down",
    ["BRAILLE LINE:  'Orca works with applications and toolkits that support the Assistive Technology Service Provider Interface (AT-SPI), which is the primary assistive technology infrastructure for Linux and Solaris. Applications and toolkits supporting the AT-SPI include the GNOME Gtk+ toolkit, the Java platform's Swing toolkit, LibreOffice, Gecko, and WebKitGtk. AT-SPI support for the KDE Qt toolkit is being pursued.'",
     "     VISIBLE:  'Orca works with applications and', cursor=1",
     "SPEECH OUTPUT: 'Technology Service Provider Interface (AT-SPI), which is the primary '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Down",
    ["BRAILLE LINE:  'Orca works with applications and toolkits that support the Assistive Technology Service Provider Interface (AT-SPI), which is the primary assistive technology infrastructure for Linux and Solaris. Applications and toolkits supporting the AT-SPI include the GNOME Gtk+ toolkit, the Java platform's Swing toolkit, LibreOffice, Gecko, and WebKitGtk. AT-SPI support for the KDE Qt toolkit is being pursued.'",
     "     VISIBLE:  'Orca works with applications and', cursor=1",
     "SPEECH OUTPUT: 'assistive technology infrastructure for Linux and Solaris. Applications '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Down",
    ["BRAILLE LINE:  'Orca works with applications and toolkits that support the Assistive Technology Service Provider Interface (AT-SPI), which is the primary assistive technology infrastructure for Linux and Solaris. Applications and toolkits supporting the AT-SPI include the GNOME Gtk+ toolkit, the Java platform's Swing toolkit, LibreOffice, Gecko, and WebKitGtk. AT-SPI support for the KDE Qt toolkit is being pursued.'",
     "     VISIBLE:  'Orca works with applications and', cursor=1",
     "SPEECH OUTPUT: 'and toolkits supporting the AT-SPI include the GNOME Gtk+ toolkit, '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Down",
    ["BRAILLE LINE:  'Orca works with applications and toolkits that support the Assistive Technology Service Provider Interface (AT-SPI), which is the primary assistive technology infrastructure for Linux and Solaris. Applications and toolkits supporting the AT-SPI include the GNOME Gtk+ toolkit, the Java platform's Swing toolkit, LibreOffice, Gecko, and WebKitGtk. AT-SPI support for the KDE Qt toolkit is being pursued.'",
     "     VISIBLE:  'Orca works with applications and', cursor=1",
     "SPEECH OUTPUT: 'the Java platform's Swing toolkit, LibreOffice, Gecko, and WebKitGtk. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Down",
    ["BRAILLE LINE:  'Orca works with applications and toolkits that support the Assistive Technology Service Provider Interface (AT-SPI), which is the primary assistive technology infrastructure for Linux and Solaris. Applications and toolkits supporting the AT-SPI include the GNOME Gtk+ toolkit, the Java platform's Swing toolkit, LibreOffice, Gecko, and WebKitGtk. AT-SPI support for the KDE Qt toolkit is being pursued.'",
     "     VISIBLE:  'Orca works with applications and', cursor=1",
     "SPEECH OUTPUT: 'AT-SPI support for the KDE Qt toolkit is being pursued.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. Down",
    ["BRAILLE LINE:  ' Launching Orca h2'",
     "     VISIBLE:  ' Launching Orca h2', cursor=2",
     "SPEECH OUTPUT: 'Launching Orca'",
     "SPEECH OUTPUT: 'heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "13. Down",
    ["BRAILLE LINE:  ' To launch Orca:'",
     "     VISIBLE:  ' To launch Orca:', cursor=2",
     "SPEECH OUTPUT: 'To launch Orca:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "14. Down",
    ["BRAILLE LINE:  ' The method for configuring Orca to be launched automatically as your preferred screen reader will depend upon which desktop environment you use. For instance, in GNOME 3.x this option can be found in the Universal Access Control Center panel on the Seeing page.'",
     "     VISIBLE:  'The method for configuring Orca ', cursor=1",
     "SPEECH OUTPUT: 'The method for configuring Orca to be launched automatically as '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "15. Down",
    ["BRAILLE LINE:  'The method for configuring Orca to be launched automatically as your preferred screen reader will depend upon which desktop environment you use. For instance, in GNOME 3.x this option can be found in the Universal Access Control Center panel on the Seeing page.'",
     "     VISIBLE:  'The method for configuring Orca ', cursor=1",
     "SPEECH OUTPUT: 'your preferred screen reader will depend upon which desktop '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "16. Down",
    ["BRAILLE LINE:  'The method for configuring Orca to be launched automatically as your preferred screen reader will depend upon which desktop environment you use. For instance, in GNOME 3.x this option can be found in the Universal Access Control Center panel on the Seeing page.'",
     "     VISIBLE:  'The method for configuring Orca ', cursor=1",
     "SPEECH OUTPUT: 'environment you use. For instance, in GNOME 3.x this option can '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "17. Down",
    ["BRAILLE LINE:  'The method for configuring Orca to be launched automatically as your preferred screen reader will depend upon which desktop environment you use. For instance, in GNOME 3.x this option can be found in the Universal Access Control Center panel on the Seeing page.'",
     "     VISIBLE:  'The method for configuring Orca ', cursor=1",
     "SPEECH OUTPUT: 'be found in the Universal Access Control Center panel on the'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "18. Down",
    ["BRAILLE LINE:  'The method for configuring Orca to be launched automatically as your preferred screen reader will depend upon which desktop environment you use. For instance, in GNOME 3.x this option can be found in the Universal Access Control Center panel on the Seeing page.'",
     "     VISIBLE:  'ca to be launched automatically ', cursor=32",
     "SPEECH OUTPUT: 'be found in the Universal Access Control Center panel on the'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "19. Down",
    ["BRAILLE LINE:  ' To toggle Orca on and off in GNOME, press Super+Alt+S.'",
     "     VISIBLE:  'To toggle Orca on and off in GNO', cursor=1",
     "SPEECH OUTPUT: 'To toggle Orca on and off in GNOME, press'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "20. Down",
    ["BRAILLE LINE:  ' To toggle Orca on and off in GNOME, press Super+Alt+S.'",
     "     VISIBLE:  'Orca on and off in GNOME, press ', cursor=32",
     "SPEECH OUTPUT: 'To toggle Orca on and off in GNOME, press'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "21. Up",
    ["BRAILLE LINE:  ' To toggle Orca on and off in GNOME, press Super+Alt+S.'",
     "     VISIBLE:  'To toggle Orca on and off in GNO', cursor=1",
     "SPEECH OUTPUT: 'To toggle Orca on and off in GNOME, press'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "22. Up",
    ["BRAILLE LINE:  'be found in the Universal Access Control Center panel on the'",
     "     VISIBLE:  'ess Control Center panel on the', cursor=32",
     "SPEECH OUTPUT: 'be found in the Universal Access Control Center panel on the'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "23. Up",
    ["BRAILLE LINE:  'be found in the Universal Access Control Center panel on the'",
     "     VISIBLE:  'be found in the Universal Access', cursor=1",
     "SPEECH OUTPUT: 'be found in the Universal Access Control Center panel on the'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "24. Up",
    ["BRAILLE LINE:  'environment you use. For instance, in GNOME 3.x this option can '",
     "     VISIBLE:  'environment you use. For instanc', cursor=1",
     "SPEECH OUTPUT: 'environment you use. For instance, in GNOME 3.x this option can '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "25. Up",
    ["BRAILLE LINE:  'your preferred screen reader will depend upon which desktop '",
     "     VISIBLE:  'your preferred screen reader wil', cursor=1",
     "SPEECH OUTPUT: 'your preferred screen reader will depend upon which desktop '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "26. Up",
    ["BRAILLE LINE:  ' The method for configuring Orca to be launched automatically as '",
     "     VISIBLE:  'The method for configuring Orca ', cursor=1",
     "SPEECH OUTPUT: 'The method for configuring Orca to be launched automatically as '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "27. Up",
    ["BRAILLE LINE:  ' To launch Orca:'",
     "     VISIBLE:  ' To launch Orca:', cursor=2",
     "SPEECH OUTPUT: 'To launch Orca:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "28. Up",
    ["BRAILLE LINE:  ' Launching Orca h2'",
     "     VISIBLE:  ' Launching Orca h2', cursor=2",
     "SPEECH OUTPUT: 'Launching Orca'",
     "SPEECH OUTPUT: 'heading level 2'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "29. Up",
    ["BRAILLE LINE:  'AT-SPI support for the KDE Qt toolkit is being pursued.'",
     "     VISIBLE:  'AT-SPI support for the KDE Qt to', cursor=1",
     "SPEECH OUTPUT: 'AT-SPI support for the KDE Qt toolkit is being pursued.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "30. Up",
    ["BRAILLE LINE:  'the Java platform's Swing toolkit, LibreOffice, Gecko, and WebKitGtk. '",
     "     VISIBLE:  'the Java platform's Swing toolki', cursor=1",
     "SPEECH OUTPUT: 'the Java platform's Swing toolkit, LibreOffice, Gecko, and WebKitGtk. '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "31. Up",
    ["BRAILLE LINE:  'and toolkits supporting the AT-SPI include the GNOME Gtk+ toolkit, '",
     "     VISIBLE:  'and toolkits supporting the AT-S', cursor=1",
     "SPEECH OUTPUT: 'and toolkits supporting the AT-SPI include the GNOME Gtk+ toolkit, '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "32. Up",
    ["BRAILLE LINE:  'assistive technology infrastructure for Linux and Solaris. Applications '",
     "     VISIBLE:  'assistive technology infrastruct', cursor=1",
     "SPEECH OUTPUT: 'assistive technology infrastructure for Linux and Solaris. Applications '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "33. Up",
    ["BRAILLE LINE:  'Technology Service Provider Interface (AT-SPI), which is the primary '",
     "     VISIBLE:  'Technology Service Provider Inte', cursor=1",
     "SPEECH OUTPUT: 'Technology Service Provider Interface (AT-SPI), which is the primary '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "34. Up",
    ["BRAILLE LINE:  ' Orca works with applications and toolkits that support the Assistive '",
     "     VISIBLE:  'Orca works with applications and', cursor=1",
     "SPEECH OUTPUT: 'Orca works with applications and toolkits that support the Assistive '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "35. Up",
    ["BRAILLE LINE:  'and refreshable braille.'",
     "     VISIBLE:  'and refreshable braille.', cursor=1",
     "SPEECH OUTPUT: 'and refreshable braille.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "36. Up",
    ["BRAILLE LINE:  'screen reader that provides access to the graphical desktop via speech '",
     "     VISIBLE:  'screen reader that provides acce', cursor=1",
     "SPEECH OUTPUT: 'screen reader that provides access to the graphical desktop via speech '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "37. Up",
    ["BRAILLE LINE:  ' Orca is a free, open source, flexible, and extensible '",
     "     VISIBLE:  'Orca is a free, open source, fle', cursor=1",
     "SPEECH OUTPUT: 'Orca is a free, open source, flexible, and extensible '"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "38. Up",
    ["BRAILLE LINE:  ' Welcome to Orca h1'",
     "     VISIBLE:  ' Welcome to Orca h1', cursor=2",
     "SPEECH OUTPUT: 'Welcome to Orca'",
     "SPEECH OUTPUT: 'heading level 1'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "39. Up",
    ["BRAILLE LINE:  ' Next $l'",
     "     VISIBLE:  ' Next $l', cursor=2",
     "SPEECH OUTPUT: 'Next link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "40. Up",
    ["BRAILLE LINE:  ' Introduction to the Orca Screen Reader Getting Started'",
     "     VISIBLE:  ' Introduction to the Orca Screen', cursor=0",
     "SPEECH OUTPUT: 'Introduction to the Orca Screen Reader link \xa0\u203a Getting Started link \xa0\xbb'"]))

sequence.append(KeyComboAction("<Alt>F4"))
sequence.append(utils.AssertionSummaryAction())
sequence.start()
