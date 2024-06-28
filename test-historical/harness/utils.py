"""Utilities that can be used by tests."""

import difflib
import re
import sys

import gi
gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")

from gi.repository import Gio
from gi.repository import Gdk
from gi.repository import Gtk
from macaroon.playback import *

testLogger = Gio.DBusProxy.new_for_bus_sync(
    Gio.BusType.SESSION,
    Gio.DBusProxyFlags.NONE,
    None,
    'org.gnome.Orca',
    '/org/gnome/Orca',
    'org.gnome.Orca.Logger',
    None)

enable_assert = \
    environ.get('HARNESS_ASSERT', 'yes') in ('yes', 'true', 'y', '1', 1)
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

def getKeyCodeForName(name):
    keymap = Gdk.Keymap.get_default()
    success, entries = keymap.get_entries_for_keyval(Gdk.keyval_from_name(name))
    if success:
        return entries[-1].keycode

    return None

def setClipboardText(text):
    clipboard = Gtk.Clipboard.get(Gdk.Atom.intern("CLIPBOARD", False))
    clipboard.set_text(text, -1)

class StartRecordingAction(AtomicAction):
    '''Tells Orca to log speech and braille output to a string which we
    can later obtain and use in an assertion (see AssertPresentationAction)'''

    def __init__(self):
        if enable_assert:
            AtomicAction.__init__(self, 1000, self._startRecording)
        else:
            AtomicAction.__init__(self, 0, lambda: None)

    def _startRecording(self):
        testLogger.startRecording()

    def __str__(self):
        return 'Start Recording Action'

def assertListEquality(rawOrcaResults, expectedList):
    '''Convert raw speech and braille output obtained from Orca into a
    list by splitting it at newline boundaries.  Compare it to the
    list passed in and return the actual results if they differ.
    Otherwise, return None to indicate an equality.'''

    results = rawOrcaResults.strip().split("\n")

    # Shoot for a string comparison first.
    #
    if results == expectedList:
        return None
    elif len(results) != len(expectedList):
        return results

    # If the string comparison failed, do a regex match item by item
    #
    for i in range(0, len(expectedList)):
        if results[i] == expectedList[i]:
            continue
        else:
            expectedResultRE = re.compile(expectedList[i])
            if expectedResultRE.match(results[i]):
                continue
            else:
                return results

    return None

class AssertPresentationAction(AtomicAction):
    '''Ask Orca for the speech and braille logged since the last use
    of StartRecordingAction and apply an assertion predicate.'''

    totalCount = 0
    totalSucceed = 0
    totalFail = 0
    totalKnownIssues = 0

    def __init__(self, name, expectedResults,
                 assertionPredicate=assertListEquality):
        '''name:               the name of the test
           expectedResults:    the results we want (typically a list of strings
                               that can be treated as regular expressions)
           assertionPredicate: method to compare actual results to expected
                               results
        '''
        # [[[WDW: the pause is to wait for Orca to process an event.
        # Probably should think of a better way to do this.]]]
        #
        if enable_assert:
            AtomicAction.__init__(self, 1000, self._stopRecording)
            self._name = sys.argv[0] + ":" + name
            self._expectedResults = expectedResults
            self._assertionPredicate = assertionPredicate
            AssertPresentationAction.totalCount += 1
            self._num = AssertPresentationAction.totalCount
        else:
            AtomicAction.__init__(self, 0, lambda: None)

    def printDiffs(self, results):
        """Compare the expected results with the actual results and print
        out a set of diffs.

        Arguments:
        - results: the actual results.

        Returns an indication of whether this test was expected to fail.
        """

        knownIssue = False
        print("DIFFERENCES FOUND:", file=myErr)
        if isinstance(self._expectedResults, [].__class__):
            for result in self._expectedResults:
                if result.startswith("KNOWN ISSUE") \
                   or result.startswith("BUG?"):
                    knownIssue = True
        else:
            if self._expectedResults.startswith("KNOWN ISSUE") \
               or self._expectedResults.startswith("BUG?"):
                knownIssue = True

        d = difflib.Differ()
        try:
            # This can stack trace for some odd reason (UTF-8 characters?),
            # so we need to capture it.  Otherwise, it can hang the tests.
            #
            diffs = list(d.compare(self._expectedResults, results))
            print('\n'.join(list(diffs)), file=myErr)
        except:
            print("(ERROR COMPUTING DIFFERENCES!!!)", file=myErr)
            for i in range(0, max(len(results), len(self._expectedResults))):
                try:
                    print("  EXPECTED: %s" \
                          % self._expectedResults[i].decode("UTF-8", "replace"), file=myErr)
                except:
                    pass
                try:
                    print("  ACTUAL:   %s" \
                          % results[i].decode("UTF-8", "replace"), file=myErr)
                except:
                    pass

        return knownIssue

    def _stopRecording(self):
        result = testLogger.stopRecording()
        results = self._assertionPredicate(result, self._expectedResults)
        if not results:
            AssertPresentationAction.totalSucceed += 1
            print("Test %d of %d SUCCEEDED: %s" \
                            % (self._num,
                               AssertPresentationAction.totalCount,
                               self._name), file=myOut)
        else:
            AssertPresentationAction.totalFail += 1
            print("Test %d of %d FAILED: %s" \
                            % (self._num,
                               AssertPresentationAction.totalCount,
                               self._name), file=myErr)

            knownIssue = self.printDiffs(results)
            if knownIssue:
                AssertPresentationAction.totalKnownIssues += 1
                print('[FAILURE WAS EXPECTED - ' \
                                'LOOK FOR KNOWN ISSUE OR BUG? ' \
                                'IN EXPECTED RESULTS]', file=myErr)
            else:
                print('[FAILURE WAS UNEXPECTED]', file=myErr)

    def __str__(self):
        return 'Assert Presentation Action: %s' % self._name

class AssertionSummaryAction(AtomicAction):
    '''Output the summary of successes and failures of
    AssertPresentationAction assertions.'''

    def __init__(self):
        AtomicAction.__init__(self, 0, self._printSummary)

    def _printSummary(self):
        print("SUMMARY: %d SUCCEEDED and %d FAILED (%d UNEXPECTED) of %d for %s"\
            % (AssertPresentationAction.totalSucceed,
               AssertPresentationAction.totalFail,
               (AssertPresentationAction.totalFail \
               - AssertPresentationAction.totalKnownIssues),
               AssertPresentationAction.totalCount,
               sys.argv[0]), file=myOut)

    def __str__(self):
        return 'Start Recording Action'
