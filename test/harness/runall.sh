#!/bin/bash -x
#
# runall.sh can take the following optional parameters:
#
# -h|--help          - print a usage message.
# -k <keystrokesDir> - alternate keystroke directory (default is ../keystrokes).
# -r <resultsDir>    - alternate results directory (default is ../results).
#

OPERATING_SYSTEMS="SunOS Linux"
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

# (Bug #359919). Check to see if the application exists. 
# If it does, then supply that as the $2 parameter to the runone.sh command.
# If it doesn't exist see if the name is in a list of system types that
# we care about (currently "SunOS" and "Linux").
#   If it is, then compare the directory name against the result of running 
#   `uname`.
#     If they match, then run the scripts in that directory.
#     If they don't match, ignore that directory.
#   If it isn't, then don't supply a $2 parameter to the runone.sh command.

      oldifs="$IFS"
      IFS=:
      found=0
      for dir in $PATH; do
        test -x "$dir/$application" && {
          found=1
          break
        }
      done
      IFS="$oldifs"
      mkdir -p tmp/$application
      cd tmp/$application
      for testFile in `find $testDir -type f -name "*.keys" | sort`; do
        if [ "$found" -gt 0 ]
        then
          $harnessDir/runone.sh $testFile $application
        else
          osType=`uname`
          for os in $OPERATING_SYSTEMS; do
            if [ $application == $os ]
            then
              found=1
              if [ $osType == $os ]
              then
                $harnessDir/runone.sh $testFile
              fi
            fi
          done
          if [ "$found" -eq 0 ]
          then
            $harnessDir/runone.sh $testFile
          fi
        fi
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
