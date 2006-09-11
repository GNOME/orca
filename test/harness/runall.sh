#!/bin/bash

foo=`dirname $0`
harnessDir=`cd $foo; pwd`
keystrokesDir=$harnessDir/../keystrokes

# Look in the keystrokes directory for directories.
# The name of each directory under the keystrokes directory
# is expected to be the name of an application to run.  For
# example, the gnome-terminal keystrokes should live under
# a directory called gnome-terminal.  If there isn't an
# application associated with the directory name, we just
# assume the test should apply to the desktop in general.
#
# There is expected to be a keystrokes file in each of the
# found sub-directories. We go ahead and run this using our
# runone.sh script.
#
for testDir in `find $keystrokesDir -type d`
do
  application=`basename $testDir`
  if [ $application != "CVS" ] && [ $application != "keystrokes" ]
    then
      mkdir -p tmp/$application
      cd tmp/$application
      for testFile in `find $testDir -type f -name "*.keys" | sort`
      do
        $harnessDir/runone.sh $testFile
	sleep 5
      done
      cd ../..
  fi 
done
