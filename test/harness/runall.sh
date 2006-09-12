#!/bin/bash
#
# runall.sh can take the following optional parameters:
#
# -h|--help          - print a usage message.
# -k <keystrokesDir> - alternate keystroke directory (default is ../results).
# -r <resultsDir>    - alternate results directory (default is ../keystrokes).
#

foo=`dirname $0`
harnessDir=`cd $foo; pwd`
keystrokesDir=$harnessDir/../keystrokes
resultsDir=$harnessDir/../results

process_cl () {
    while [ $# != 0 ]; do
        case "$1" in
            -k )
                shift
                if [ $# == 0 ]; then
                    echo "Option -k requires an argument."
                    exit 1
                fi
                keystrokesDir=$1
                ;;
            -r )
                shift
                if [ $# == 0 ]; then
                    echo "Option -r requires an argument."
                    exit 1
                fi
                resultsDir=$1
                ;;
            -h|--help)
                echo "Usage: $0 [options]"
                echo "options:"
                echo "   -h, --help        print this usage message"
                echo "   -k keystrokeDir   specify an alternate keystrokes directory"
                echo "   -r resultsDir     specify an alternate results directory"
                exit 0
                ;;
            *)
                echo "Unknown option: $1"
                exit 1
                ;;
        esac
        shift
    done
}

# Process the users command line options.
#
process_cl "${@}"

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
  if [ $application != "CVS" ] && [ $application != `basename $keystrokesDir` ]
    then
      mkdir -p tmp/$application
      cd tmp/$application
      for testFile in `find $testDir -type f -name "*.keys" | sort`
      do
        $harnessDir/runone.sh $testFile
	sleep 5
        newResultsFile=`basename $testFile .keys`.orca
        expectedResultsFile=$resultsDir/$application/$newResultsFile
        echo Comparing results for $testFile
        diff -s $expectedResultsFile $newResultsFile
        echo ========================================
      done
      cd ../..
  fi 
done
