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

