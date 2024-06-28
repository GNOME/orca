#!/usr/bin/python

"""Test of presentation of links that contain images."""

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

# Work around some new quirk in Gecko that causes this test to fail if
# run via the test harness rather than manually.
sequence.append(KeyComboAction("<Control>r"))

sequence.append(KeyComboAction("<Control>Home"))
sequence.append(KeyComboAction("Down"))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'One image with alt text in a link:'",
     "     VISIBLE:  'One image with alt text in a lin', cursor=1",
     "SPEECH OUTPUT: 'One image with alt text in a link:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'Orca logo image'",
     "     VISIBLE:  'Orca logo image', cursor=1",
     "SPEECH OUTPUT: 'Orca logo image link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'One image with title attribute in a link:'",
     "     VISIBLE:  'One image with title attribute i', cursor=1",
     "SPEECH OUTPUT: 'One image with title attribute in a link:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  'Orca logo showing a whale holding a white cane image'",
     "     VISIBLE:  'Orca logo showing a whale holdin', cursor=1",
     "SPEECH OUTPUT: 'Orca logo showing a whale holding a white cane image link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  'One image with both alt text and title attribute in a link:'",
     "     VISIBLE:  'One image with both alt text and', cursor=1",
     "SPEECH OUTPUT: 'One image with both alt text and title attribute in a link:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Down",
    ["BRAILLE LINE:  'Orca logo image'",
     "     VISIBLE:  'Orca logo image', cursor=1",
     "SPEECH OUTPUT: 'Orca logo image link Orca logo showing a whale holding a white cane'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Down",
    ["BRAILLE LINE:  'One \"useless\" image in a link:'",
     "     VISIBLE:  'One \"useless\" image in a link:', cursor=1",
     "SPEECH OUTPUT: 'One \"useless\" image in a link:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Down",
    ["BRAILLE LINE:  'foo image'",
     "     VISIBLE:  'foo image', cursor=1",
     "SPEECH OUTPUT: 'foo image link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Down",
    ["BRAILLE LINE:  'Two \"useless\" images in a link:'",
     "     VISIBLE:  'Two \"useless\" images in a link:', cursor=1",
     "SPEECH OUTPUT: 'Two \"useless\" images in a link:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Line Down",
    ["BRAILLE LINE:  'foo image foo image'",
     "     VISIBLE:  'foo image foo image', cursor=1",
     "SPEECH OUTPUT: 'foo image'",
     "SPEECH OUTPUT: 'foo image link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Line Down",
    ["BRAILLE LINE:  'Two \"useless\" images in a paragraph that is inside of a link:'",
     "     VISIBLE:  'Two \"useless\" images in a paragr', cursor=1",
     "SPEECH OUTPUT: 'Two \"useless\" images in a paragraph that is inside of a link:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. Line Down",
    ["BRAILLE LINE:  'foo image foo image'",
     "     VISIBLE:  'foo image foo image', cursor=1",
     "SPEECH OUTPUT: 'foo image'",
     "SPEECH OUTPUT: 'foo image link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "13. Line Down",
    ["BRAILLE LINE:  'One \"useless\" image and one \"useful\" image in a link:'",
     "     VISIBLE:  'One \"useless\" image and one \"use', cursor=1",
     "SPEECH OUTPUT: 'One \"useless\" image and one \"useful\" image in a link:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "14. Line Down",
    ["BRAILLE LINE:  'Orca logo image foo image'",
     "     VISIBLE:  'Orca logo image foo image', cursor=1",
     "SPEECH OUTPUT: 'Orca logo image'",
     "SPEECH OUTPUT: 'foo image link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "15. Line Down",
    ["BRAILLE LINE:  'Two \"useless\" images along with some text in a link:'",
     "     VISIBLE:  'Two \"useless\" images along with ', cursor=1",
     "SPEECH OUTPUT: 'Two \"useless\" images along with some text in a link:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "16. Line Down",
    ["BRAILLE LINE:  'foo image'",
     "     VISIBLE:  'foo image', cursor=1",
     "SPEECH OUTPUT: 'foo image link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "17. Line Down",
    ["BRAILLE LINE:  'silly link'",
     "     VISIBLE:  'silly link', cursor=1",
     "SPEECH OUTPUT: 'silly link'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "18. Line Down",
    ["BRAILLE LINE:  'foo image'",
     "     VISIBLE:  'foo image', cursor=1",
     "SPEECH OUTPUT: 'foo image link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "19. Line Down",
    ["BRAILLE LINE:  'Two \"useless\" images in a paragraph that is inside of a link along with text that is not in the paragraph: Before the'",
     "     VISIBLE:  'Two \"useless\" images in a paragr', cursor=1",
     "SPEECH OUTPUT: 'Two \"useless\" images in a paragraph that is inside of a link along with text that is not in the paragraph:'",
     "SPEECH OUTPUT: 'Before the'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "20. Line Down",
    ["BRAILLE LINE:  'paragraph'",
     "     VISIBLE:  'paragraph', cursor=1",
     "SPEECH OUTPUT: 'paragraph'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "21. Line Down",
    ["BRAILLE LINE:  'foo image foo image'",
     "     VISIBLE:  'foo image foo image', cursor=1",
     "SPEECH OUTPUT: 'foo image'",
     "SPEECH OUTPUT: 'foo image link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "22. Line Down",
    ["BRAILLE LINE:  'After the paragraph'",
     "     VISIBLE:  'After the paragraph', cursor=1",
     "SPEECH OUTPUT: 'After the paragraph'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "23. Line Down",
    ["BRAILLE LINE:  'Two \"useless\" images and some additional text in a paragraph that is inside of a link along with text that is not in the'",
     "     VISIBLE:  'Two \"useless\" images and some ad', cursor=1",
     "SPEECH OUTPUT: 'Two \"useless\" images and some additional text in a paragraph that is inside of a link along with text that is not in the'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "24. Line Down",
    ["BRAILLE LINE:  'paragraph: Before the paragraph'",
     "     VISIBLE:  'paragraph: Before the paragraph', cursor=1",
     "SPEECH OUTPUT: 'paragraph:'",
     "SPEECH OUTPUT: 'Before the paragraph'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "25. Line Down",
    ["BRAILLE LINE:  'foo image'",
     "     VISIBLE:  'foo image', cursor=1",
     "SPEECH OUTPUT: 'foo image link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "26. Line Down",
    ["BRAILLE LINE:  'silly link'",
     "     VISIBLE:  'silly link', cursor=1",
     "SPEECH OUTPUT: 'silly link'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "27. Line Down",
    ["BRAILLE LINE:  'foo image'",
     "     VISIBLE:  'foo image', cursor=1",
     "SPEECH OUTPUT: 'foo image link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "28. Line Down",
    ["BRAILLE LINE:  'After the paragraph'",
     "     VISIBLE:  'After the paragraph', cursor=1",
     "SPEECH OUTPUT: 'After the paragraph'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "29. Line Up",
    ["BRAILLE LINE:  'foo image'",
     "     VISIBLE:  'foo image', cursor=1",
     "SPEECH OUTPUT: 'foo image link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "30. Line Up",
    ["BRAILLE LINE:  'silly link'",
     "     VISIBLE:  'silly link', cursor=1",
     "SPEECH OUTPUT: 'silly link'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "31. Line Up",
    ["BRAILLE LINE:  'foo image'",
     "     VISIBLE:  'foo image', cursor=1",
     "SPEECH OUTPUT: 'foo image link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "32. Line Up",
    ["BRAILLE LINE:  'paragraph: Before the paragraph'",
     "     VISIBLE:  'paragraph: Before the paragraph', cursor=1",
     "SPEECH OUTPUT: 'paragraph:'",
     "SPEECH OUTPUT: 'Before the paragraph'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "33. Line Up",
    ["BRAILLE LINE:  'Two \"useless\" images and some additional text in a paragraph that is inside of a link along with text that is not in the'",
     "     VISIBLE:  'Two \"useless\" images and some ad', cursor=1",
     "SPEECH OUTPUT: 'Two \"useless\" images and some additional text in a paragraph that is inside of a link along with text that is not in the'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "34. Line Up",
    ["BRAILLE LINE:  'After the paragraph'",
     "     VISIBLE:  'After the paragraph', cursor=1",
     "SPEECH OUTPUT: 'After the paragraph'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "35. Line Up",
    ["BRAILLE LINE:  'foo image foo image'",
     "     VISIBLE:  'foo image foo image', cursor=1",
     "SPEECH OUTPUT: 'foo image'",
     "SPEECH OUTPUT: 'foo image link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "36. Line Up",
    ["BRAILLE LINE:  'paragraph'",
     "     VISIBLE:  'paragraph', cursor=1",
     "SPEECH OUTPUT: 'paragraph'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "37. Line Up",
    ["BRAILLE LINE:  'Two \"useless\" images in a paragraph that is inside of a link along with text that is not in the paragraph: Before the'",
     "     VISIBLE:  'Two \"useless\" images in a paragr', cursor=1",
     "SPEECH OUTPUT: 'Two \"useless\" images in a paragraph that is inside of a link along with text that is not in the paragraph:'",
     "SPEECH OUTPUT: 'Before the'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "38. Line Up",
    ["BRAILLE LINE:  'foo image'",
     "     VISIBLE:  'foo image', cursor=1",
     "SPEECH OUTPUT: 'foo image link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "39. Line Up",
    ["BRAILLE LINE:  'silly link'",
     "     VISIBLE:  'silly link', cursor=1",
     "SPEECH OUTPUT: 'silly link'",
     "SPEECH OUTPUT: 'link.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "40. Line Up",
    ["BRAILLE LINE:  'foo image'",
     "     VISIBLE:  'foo image', cursor=1",
     "SPEECH OUTPUT: 'foo image link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "41. Line Up",
    ["BRAILLE LINE:  'Two \"useless\" images along with some text in a link:'",
     "     VISIBLE:  'Two \"useless\" images along with ', cursor=1",
     "SPEECH OUTPUT: 'Two \"useless\" images along with some text in a link:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "42. Line Up",
    ["BRAILLE LINE:  'Orca logo image foo image'",
     "     VISIBLE:  'Orca logo image foo image', cursor=1",
     "SPEECH OUTPUT: 'Orca logo image'",
     "SPEECH OUTPUT: 'foo image link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "43. Line Up",
    ["BRAILLE LINE:  'One \"useless\" image and one \"useful\" image in a link:'",
     "     VISIBLE:  'One \"useless\" image and one \"use', cursor=1",
     "SPEECH OUTPUT: 'One \"useless\" image and one \"useful\" image in a link:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "44. Line Up",
    ["BRAILLE LINE:  'foo image foo image'",
     "     VISIBLE:  'foo image foo image', cursor=1",
     "SPEECH OUTPUT: 'foo image'",
     "SPEECH OUTPUT: 'foo image link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "45. Line Up",
    ["BRAILLE LINE:  'Two \"useless\" images in a paragraph that is inside of a link:'",
     "     VISIBLE:  'Two \"useless\" images in a paragr', cursor=1",
     "SPEECH OUTPUT: 'Two \"useless\" images in a paragraph that is inside of a link:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "46. Line Up",
    ["BRAILLE LINE:  'foo image foo image'",
     "     VISIBLE:  'foo image foo image', cursor=1",
     "SPEECH OUTPUT: 'foo image'",
     "SPEECH OUTPUT: 'foo image link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "47. Line Up",
    ["BRAILLE LINE:  'Two \"useless\" images in a link:'",
     "     VISIBLE:  'Two \"useless\" images in a link:', cursor=1",
     "SPEECH OUTPUT: 'Two \"useless\" images in a link:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "48. Line Up",
    ["BRAILLE LINE:  'foo image'",
     "     VISIBLE:  'foo image', cursor=1",
     "SPEECH OUTPUT: 'foo image link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "49. Line Up",
    ["BRAILLE LINE:  'One \"useless\" image in a link:'",
     "     VISIBLE:  'One \"useless\" image in a link:', cursor=1",
     "SPEECH OUTPUT: 'One \"useless\" image in a link:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "50. Line Up",
    ["BRAILLE LINE:  'Orca logo image'",
     "     VISIBLE:  'Orca logo image', cursor=1",
     "SPEECH OUTPUT: 'Orca logo image link Orca logo showing a whale holding a white cane'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "51. Line Up",
    ["BRAILLE LINE:  'One image with both alt text and title attribute in a link:'",
     "     VISIBLE:  'One image with both alt text and', cursor=1",
     "SPEECH OUTPUT: 'One image with both alt text and title attribute in a link:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "52. Line Up",
    ["BRAILLE LINE:  'Orca logo showing a whale holding a white cane image'",
     "     VISIBLE:  'Orca logo showing a whale holdin', cursor=1",
     "SPEECH OUTPUT: 'Orca logo showing a whale holding a white cane image link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "53. Line Up",
    ["BRAILLE LINE:  'One image with title attribute in a link:'",
     "     VISIBLE:  'One image with title attribute i', cursor=1",
     "SPEECH OUTPUT: 'One image with title attribute in a link:'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "54. Line Up",
    ["BRAILLE LINE:  'Orca logo image'",
     "     VISIBLE:  'Orca logo image', cursor=1",
     "SPEECH OUTPUT: 'Orca logo image link'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Up"))
sequence.append(utils.AssertPresentationAction(
    "55. Line Up",
    ["BRAILLE LINE:  'One image with alt text in a link:'",
     "     VISIBLE:  'One image with alt text in a lin', cursor=1",
     "SPEECH OUTPUT: 'One image with alt text in a link:'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
