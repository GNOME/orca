#!/usr/bin/python

from macaroon.playback import *
import utils

sequence = MacroSequence()

#sequence.append(WaitForDocLoad())
sequence.append(PauseAction(5000))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("<Control>Home"))
sequence.append(utils.AssertPresentationAction(
    "1. Top of file",
    ["BRAILLE LINE:  'MathML \"Torture Test\" test cases'",
     "     VISIBLE:  'MathML \"Torture Test\" test cases', cursor=1",
     "SPEECH OUTPUT: 'MathML \"Torture Test\" test cases'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "2. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'x.'",
     "SPEECH OUTPUT: 'superscript 2.'",
     "SPEECH OUTPUT: 'y.'",
     "SPEECH OUTPUT: 'superscript 2.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "3. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'F.'",
     "SPEECH OUTPUT: 'pre-subscript 2'",
     "SPEECH OUTPUT: 'subscript 3'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "4. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'fraction start.'",
     "SPEECH OUTPUT: 'x plus y.'",
     "SPEECH OUTPUT: 'superscript 2.'",
     "SPEECH OUTPUT: 'over k plus 1.'",
     "SPEECH OUTPUT: 'fraction end.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "5. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'x plus y.'",
     "SPEECH OUTPUT: 'superscript fraction start.'",
     "SPEECH OUTPUT: '2 over k plus 1.'",
     "SPEECH OUTPUT: 'fraction end.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "6. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'fraction start.'",
     "SPEECH OUTPUT: 'a over b slash 2.'",
     "SPEECH OUTPUT: 'fraction end.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "7. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'a.'",
     "SPEECH OUTPUT: 'subscript 0.'",
     "SPEECH OUTPUT: 'plus fraction start.'",
     "SPEECH OUTPUT: '1 over a.'",
     "SPEECH OUTPUT: 'subscript 1.'",
     "SPEECH OUTPUT: 'plus fraction start.'",
     "SPEECH OUTPUT: '1 over a.'",
     "SPEECH OUTPUT: 'subscript 2.'",
     "SPEECH OUTPUT: 'plus fraction start.'",
     "SPEECH OUTPUT: '1 over a.'",
     "SPEECH OUTPUT: 'subscript 3.'",
     "SPEECH OUTPUT: 'plus fraction start.'",
     "SPEECH OUTPUT: '1 over a.'",
     "SPEECH OUTPUT: 'subscript 4.'",
     "SPEECH OUTPUT: 'fraction end.'",
     "SPEECH OUTPUT: 'fraction end.'",
     "SPEECH OUTPUT: 'fraction end.'",
     "SPEECH OUTPUT: 'fraction end.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "8. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'a.'",
     "SPEECH OUTPUT: 'subscript 0.'",
     "SPEECH OUTPUT: 'plus fraction start.'",
     "SPEECH OUTPUT: '1 over a.'",
     "SPEECH OUTPUT: 'subscript 1.'",
     "SPEECH OUTPUT: 'plus fraction start.'",
     "SPEECH OUTPUT: '1 over a.'",
     "SPEECH OUTPUT: 'subscript 2.'",
     "SPEECH OUTPUT: 'plus fraction start.'",
     "SPEECH OUTPUT: '1 over a.'",
     "SPEECH OUTPUT: 'subscript 3.'",
     "SPEECH OUTPUT: 'plus fraction start.'",
     "SPEECH OUTPUT: '1 over a.'",
     "SPEECH OUTPUT: 'subscript 4.'",
     "SPEECH OUTPUT: 'fraction end.'",
     "SPEECH OUTPUT: 'fraction end.'",
     "SPEECH OUTPUT: 'fraction end.'",
     "SPEECH OUTPUT: 'fraction end.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "9. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'left paren fraction without bar, start.'",
     "SPEECH OUTPUT: 'n over k slash 2.'",
     "SPEECH OUTPUT: 'fraction end.'",
     "SPEECH OUTPUT: 'right paren'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "10. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'left paren fraction without bar, start.'",
     "SPEECH OUTPUT: 'p over 2.'",
     "SPEECH OUTPUT: 'fraction end.'",
     "SPEECH OUTPUT: 'right paren x.'",
     "SPEECH OUTPUT: 'superscript 2.'",
     "SPEECH OUTPUT: 'y.'",
     "SPEECH OUTPUT: 'superscript p minus 2.'",
     "SPEECH OUTPUT: 'minus fraction start.'",
     "SPEECH OUTPUT: '1 over 1 minus x.'",
     "SPEECH OUTPUT: 'fraction end.'",
     "SPEECH OUTPUT: 'fraction start.'",
     "SPEECH OUTPUT: '1 over 1 minus x.'",
     "SPEECH OUTPUT: 'superscript 2.'",
     "SPEECH OUTPUT: 'fraction end.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "11. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'sum.'",
     "SPEECH OUTPUT: 'underscript fraction without bar, start.'",
     "SPEECH OUTPUT: '0 less than or equal to i less than or equal to m over 0 less than j less than n.'",
     "SPEECH OUTPUT: 'fraction end.'",
     "SPEECH OUTPUT: 'P left paren i comma j right paren'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "12. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'x.'",
     "SPEECH OUTPUT: 'superscript 2 y.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "13. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
    "SPEECH OUTPUT: 'sum.'",
     "SPEECH OUTPUT: 'underscript i equals 1.'",
     "SPEECH OUTPUT: 'overscript p.'",
     "SPEECH OUTPUT: 'sum.'",
     "SPEECH OUTPUT: 'underscript j equals 1.'",
     "SPEECH OUTPUT: 'overscript q.'",
     "SPEECH OUTPUT: 'sum.'",
     "SPEECH OUTPUT: 'underscript k equals 1.'",
     "SPEECH OUTPUT: 'overscript r.'",
     "SPEECH OUTPUT: 'a.'",
     "SPEECH OUTPUT: 'subscript i j.'",
     "SPEECH OUTPUT: 'b.'",
     "SPEECH OUTPUT: 'subscript j k.'",
     "SPEECH OUTPUT: 'c.'",
     "SPEECH OUTPUT: 'subscript k i.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "14. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'square root of 1 plus square root of 1 plus square root of 1 plus square root of 1 plus square root of 1 plus square root of 1 plus square root of 1 plus x.'",
     "SPEECH OUTPUT: 'root end.'",
     "SPEECH OUTPUT: 'root end.'",
     "SPEECH OUTPUT: 'root end.'",
     "SPEECH OUTPUT: 'root end.'",
     "SPEECH OUTPUT: 'root end.'",
     "SPEECH OUTPUT: 'root end.'",
     "SPEECH OUTPUT: 'root end.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "15. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'left paren fraction start.'",
     "SPEECH OUTPUT: 'partial differential.'",
     "SPEECH OUTPUT: 'superscript 2.'",
     "SPEECH OUTPUT: 'over partial differential x.'",
     "SPEECH OUTPUT: 'superscript 2.'",
     "SPEECH OUTPUT: 'fraction end.'",
     "SPEECH OUTPUT: 'plus fraction start.'",
     "SPEECH OUTPUT: 'partial differential.'",
     "SPEECH OUTPUT: 'superscript 2.'",
     "SPEECH OUTPUT: 'over partial differential y.'",
     "SPEECH OUTPUT: 'superscript 2.'",
     "SPEECH OUTPUT: 'fraction end.'",
     "SPEECH OUTPUT: 'right paren vertical bar φ  left paren x plus i y right paren vertical bar.'",
     "SPEECH OUTPUT: 'superscript 2.'",
     "SPEECH OUTPUT: 'equals 0'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "16. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: '2.'",
     "SPEECH OUTPUT: 'superscript 2.'",
     "SPEECH OUTPUT: 'superscript 2.'",
     "SPEECH OUTPUT: 'superscript x.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "17. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'integral.'",
     "SPEECH OUTPUT: 'subscript 1.'",
     "SPEECH OUTPUT: 'superscript x.'",
     "SPEECH OUTPUT: 'fraction start.'",
     "SPEECH OUTPUT: 'd t over t.'",
     "SPEECH OUTPUT: 'fraction end.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "18. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
    "SPEECH OUTPUT: 'double integral.'",
     "SPEECH OUTPUT: 'subscript D.'",
     "SPEECH OUTPUT: 'd x d y'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "19. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'f left paren x right paren equals left brace math table with 3 rows 2 columns.'",
     "SPEECH OUTPUT: 'row 1.'",
     "SPEECH OUTPUT: '1 slash 3.'",
     "SPEECH OUTPUT: 'if  0 less than or equal to x less than or equal to 1 semicolon.'",
     "SPEECH OUTPUT: 'row 2.'",
     "SPEECH OUTPUT: '2 slash 3.'",
     "SPEECH OUTPUT: 'if  3 less than or equal to x less than or equal to 4 semicolon.'",
     "SPEECH OUTPUT: 'row 3.'",
     "SPEECH OUTPUT: '0.'",
     "SPEECH OUTPUT: 'elsewhere.'",
     "SPEECH OUTPUT: 'table end.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "20. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'x plus ... plus x.'",
     "SPEECH OUTPUT: 'overscript top brace.'",
     "SPEECH OUTPUT: 'overscript k times.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "21. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'y.'",
     "SPEECH OUTPUT: 'subscript x.'",
     "SPEECH OUTPUT: 'superscript 2.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "22. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'sum.'",
     "SPEECH OUTPUT: 'underscript p  prime.'",
     "SPEECH OUTPUT: 'f left paren p right paren equals integral.'",
     "SPEECH OUTPUT: 'subscript t greater than 1.'",
     "SPEECH OUTPUT: 'f left paren t right paren d π left paren t right paren'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "23. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'left brace a comma ... comma a.'",
     "SPEECH OUTPUT: 'overscript top brace.'",
     "SPEECH OUTPUT: 'overscript k   a 's.'",
     "SPEECH OUTPUT: 'comma b comma ... comma b.'",
     "SPEECH OUTPUT: 'overscript top brace.'",
     "SPEECH OUTPUT: 'overscript l   b 's.'",
     "SPEECH OUTPUT: 'underscript bottom brace.'",
     "SPEECH OUTPUT: 'underscript k plus l  elements.'",
     "SPEECH OUTPUT: 'right brace'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "24. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'left paren math table with 2 rows 2 columns.'",
     "SPEECH OUTPUT: 'row 1.'",
     "SPEECH OUTPUT: 'left paren nested math table with 2 rows 2 columns.'",
     "SPEECH OUTPUT: 'row 1.'",
     "SPEECH OUTPUT: 'a.'",
     "SPEECH OUTPUT: 'b.'",
     "SPEECH OUTPUT: 'row 2.'",
     "SPEECH OUTPUT: 'c.'",
     "SPEECH OUTPUT: 'd.'",
     "SPEECH OUTPUT: 'nested table end.'",
     "SPEECH OUTPUT: 'right paren.'",
     "SPEECH OUTPUT: 'left paren nested math table with 2 rows 2 columns.'",
     "SPEECH OUTPUT: 'row 1.'",
     "SPEECH OUTPUT: 'e.'",
     "SPEECH OUTPUT: 'f.'",
     "SPEECH OUTPUT: 'row 2.'",
     "SPEECH OUTPUT: 'g.'",
     "SPEECH OUTPUT: 'h.'",
     "SPEECH OUTPUT: 'nested table end.'",
     "SPEECH OUTPUT: 'right paren.'",
     "SPEECH OUTPUT: 'row 2.'",
     "SPEECH OUTPUT: '0.'",
     "SPEECH OUTPUT: 'left paren nested math table with 2 rows 2 columns.'",
     "SPEECH OUTPUT: 'row 1.'",
     "SPEECH OUTPUT: 'i.'",
     "SPEECH OUTPUT: 'j.'",
     "SPEECH OUTPUT: 'row 2.'",
     "SPEECH OUTPUT: 'k.'",
     "SPEECH OUTPUT: 'l.'",
     "SPEECH OUTPUT: 'nested table end.'",
     "SPEECH OUTPUT: 'right paren.'",
     "SPEECH OUTPUT: 'table end.'",
     "SPEECH OUTPUT: 'right paren'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "25. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'det vertical bar math table with 5 rows 5 columns.'",
     "SPEECH OUTPUT: 'row 1.'",
     "SPEECH OUTPUT: 'c.'",
     "SPEECH OUTPUT: 'subscript 0.'",
     "SPEECH OUTPUT: 'c.'",
     "SPEECH OUTPUT: 'subscript 1.'",
     "SPEECH OUTPUT: 'c.'",
     "SPEECH OUTPUT: 'subscript 2.'",
     "SPEECH OUTPUT: 'horizontal ellipsis.'",
     "SPEECH OUTPUT: 'c.'",
     "SPEECH OUTPUT: 'subscript n.'",
     "SPEECH OUTPUT: 'row 2.'",
     "SPEECH OUTPUT: 'c.'",
     "SPEECH OUTPUT: 'subscript 1.'",
     "SPEECH OUTPUT: 'c.'",
     "SPEECH OUTPUT: 'subscript 2.'",
     "SPEECH OUTPUT: 'c.'",
     "SPEECH OUTPUT: 'subscript 3.'",
     "SPEECH OUTPUT: 'horizontal ellipsis.'",
     "SPEECH OUTPUT: 'c.'",
     "SPEECH OUTPUT: 'subscript n plus 1.'",
     "SPEECH OUTPUT: 'row 3.'",
     "SPEECH OUTPUT: 'c.'",
     "SPEECH OUTPUT: 'subscript 2.'",
     "SPEECH OUTPUT: 'c.'",
     "SPEECH OUTPUT: 'subscript 3.'",
     "SPEECH OUTPUT: 'c.'",
     "SPEECH OUTPUT: 'subscript 4.'",
     "SPEECH OUTPUT: 'horizontal ellipsis.'",
     "SPEECH OUTPUT: 'c.'",
     "SPEECH OUTPUT: 'subscript n plus 2.'",
     "SPEECH OUTPUT: 'row 4.'",
     "SPEECH OUTPUT: 'vertical ellipsis.'",
     "SPEECH OUTPUT: 'vertical ellipsis.'",
     "SPEECH OUTPUT: 'vertical ellipsis.'",
     "SPEECH OUTPUT: 'vertical ellipsis.'",
     "SPEECH OUTPUT: 'row 5.'",
     "SPEECH OUTPUT: 'c.'",
     "SPEECH OUTPUT: 'subscript n.'",
     "SPEECH OUTPUT: 'c.'",
     "SPEECH OUTPUT: 'subscript n plus 1.'",
     "SPEECH OUTPUT: 'c.'",
     "SPEECH OUTPUT: 'subscript n plus 2.'",
     "SPEECH OUTPUT: 'horizontal ellipsis.'",
     "SPEECH OUTPUT: 'c.'",
     "SPEECH OUTPUT: 'subscript 2 n.'",
     "SPEECH OUTPUT: 'table end.'",
     "SPEECH OUTPUT: 'vertical bar greater than 0'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "26. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'y.'",
     "SPEECH OUTPUT: 'subscript x.'",
     "SPEECH OUTPUT: 'subscript 2.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "27. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'x.'",
     "SPEECH OUTPUT: 'subscript 92.'",
     "SPEECH OUTPUT: 'superscript 31415.'",
     "SPEECH OUTPUT: 'plus π'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "28. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'x.'",
     "SPEECH OUTPUT: 'subscript y.'",
     "SPEECH OUTPUT: 'subscript b.'",
     "SPEECH OUTPUT: 'superscript a.'",
     "SPEECH OUTPUT: 'superscript z.'",
     "SPEECH OUTPUT: 'subscript c.'",
     "SPEECH OUTPUT: 'superscript d.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "29. Line Down",
    ["BRAILLE LINE:  'math'",
     "     VISIBLE:  'math', cursor=0",
     "SPEECH OUTPUT: 'y.'",
     "SPEECH OUTPUT: 'subscript 3.'",
     "SPEECH OUTPUT: 'superscript triple prime.'"]))

sequence.append(utils.StartRecordingAction())
sequence.append(KeyComboAction("Down"))
sequence.append(utils.AssertPresentationAction(
    "30. Line Down",
    ["BRAILLE LINE:  'End of test'",
     "     VISIBLE:  'End of test', cursor=1",
     "SPEECH OUTPUT: 'End of test'"]))

sequence.append(utils.AssertionSummaryAction())
sequence.start()
