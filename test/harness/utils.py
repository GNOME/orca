"""Utilities that can be imported by tests.  You need to make
sure your PYTHONPATH includes the directory containing this
file in order for the tests that use it to work.  The test
harness does that automatically for you."""

# Where to find Dojo tests.
#
DojoURLPrefix="http://archive.dojotoolkit.org/dojo-2007-09-20/dojotoolkit/dijit/tests/"

# Where to find our local HTML tests.
#
import sys, os
wd = os.path.dirname(sys.argv[0])
fullPath = os.path.abspath(wd)
htmlDir = os.path.abspath(fullPath + "/../../html")
htmlURLPrefix = "file://" + htmlDir + "/"

from macaroon.playback import *

errFilename = environ.get('HARNESS_ERR', None)
outFilename = environ.get('HARNESS_OUT', None)

if errFilename and len(errFilename):
    myErr = open(errFilename, 'a', 0)
else:
    myErr = sys.stderr

if outFilename and len(outFilename):
    if outFilename == errFilename:
        myOut = myErr
    else:
        myOut = open(outFilename, 'a', 0)
else:
    myOut = sys.stdout

class StartRecordingAction(AtomicAction):
    '''Tells Orca to log speech and braille output to a string which we
    can later obtain and use in an assertion (see AssertPresentationAction)'''

    def __init__(self):
        AtomicAction.__init__(self, 1000, self._startRecording)

    def _startRecording(self):
        import sys, urllib
        f = urllib.urlopen("http://localhost:20433", "recordStart")
        result = f.read()
        f.close()

    def __str__(self):
        return 'Start Recording Action'

def assertListEquality(rawOrcaResults, expectedList):
    '''Convert raw speech and braille output obtained from Orca into a
    list by splitting it at newline boundaries.  Compare it to the
    list passed in and return the actual results if they differ.'''

    results = rawOrcaResults.strip().split("\n")
    if results != expectedList:
        return "%s" % results
    else:
        return None

class AssertPresentationAction(AtomicAction):
    '''Ask Orca for the speech and braille logged since the last use
    of StartRecordingAction and apply an assertion predicate.'''

    totalCount = 0

    def __init__(self, name, expectedResults, 
                 assertionPredicate=assertListEquality):
        '''name:               the name of the test
           expectedResults:    the results we want (typically a list)
           assertionPredicate: method to compare actual results to expected
                               results
        '''
        # [[[WDW: the pause is to wait for Orca to process an event.
        # Probably should think of a better way to do this.]]]
        #
        AtomicAction.__init__(self, 1000, self._stopRecording)
        self._name = sys.argv[0] + ":" + name
        self._expectedResults = expectedResults
        self._assertionPredicate = assertionPredicate
        AssertPresentationAction.totalCount += 1
        self._num = AssertPresentationAction.totalCount

    def _stopRecording(self):
        import sys, urllib

        f = urllib.urlopen("http://localhost:20433", "recordStop")
        result = ''
        while True:
            someRead = f.read()
            result += someRead
            if not len(someRead):
                break
        f.close()

        results = self._assertionPredicate(result, self._expectedResults)
        if not results:
            print >> myOut, "Test %d of %d SUCCEEDED: %s" \
                            % (self._num, 
                               AssertPresentationAction.totalCount, 
                               self._name)
        else:
            print >> myErr, "Test %d of %d FAILED: %s" \
                            % (self._num, 
                               AssertPresentationAction.totalCount, 
                               self._name)
            print >> myErr, "EXPECTED:"
            print >> myErr, self._expectedResults
            print >> myErr, "ACTUAL:"
            print >> myErr, results
   
    def __str__(self):
        return 'Assert Presentation Action: %s' % self._name
