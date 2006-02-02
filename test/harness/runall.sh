#!/bin/bash

foo=`dirname $0`
harnessDir=`cd $foo; pwd`
keystrokesDir=$harnessDir/../keystrokes

# Just a sanity check to tell anything out there to stop.
#
python $harnessDir/F12.py
sleep 5

# Look in the keystrokes directory for directories.
# The name of each directory under the keystrokes directory
# is expected to be the name of an application to run.  For
# example, the gnome-terminal keystrokes should live under
# a directory called gnome-terminal.  If there isn't an
# application associated with the directory name, we just
# assume the test should apply to the desktop in general.
#
# Each file in the associated subdirectory is expected to be
# a keystrokes file.  We go ahead and run this using our
# runone.sh script.  In addition, after we're done running
# the test, we synthesize an F12 to tell both Orca and the
# python event recording app to quit.
#
for testDir in `find $keystrokesDir -maxdepth 1 -type d`
do
  application=`basename $testDir`
  if [ $application != "CVS" ] && [ $application != "keystrokes" ]
    then
      mkdir -p tmp/$application
      cd tmp/$application
      for testFile in `find $testDir -maxdepth 1 -type f | sort`
      do
	$harnessDir/runone.sh $testFile `which $application`
	python $harnessDir/F12.py
	sleep 5
      done
      cd ../..
  fi 
done
