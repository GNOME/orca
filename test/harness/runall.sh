#!/bin/bash
#
#
# runall.sh can take the following optional parameters:
#
# -a <appDir>        - absolute path to directory with tests for a single app 
# -c                 - analyze test coverage instead of regression testing
# -h|--help          - print a usage message.
# -k <keystrokesDir> - alternate keystroke directory (default is ../keystrokes).
# -p                 - create profile information instead of regression testing
# -r <resultsDir>    - alternate results directory (default is ../results).
# -s                 - require the tester to press return between each test
#

OPERATING_SYSTEMS="SunOS Linux"
foo=`dirname $0`
harnessDir=`cd $foo; pwd`
keystrokesDir=$harnessDir/../keystrokes
resultsDir=$harnessDir/../results

# OpenOffice 2.2 executables are installed in
# /usr/lib/openoffice/program
#
export PATH=$harnessDir/bin:$PATH:/usr/lib/openoffice/program

coverageMode=0
profileMode=0
runOrcaOnce=0

process_cl () {
    while [ $# != 0 ]; do
        case "$1" in
            -a )
                shift
                if [ $# == 0 ]; then
                    echo "Option -a requires an argument."
                    exit 1
                fi
                testDirs=$1
                ;;
            -c )
                coverageMode=1
                ;;
            -k )
                shift
                if [ $# == 0 ]; then
                    echo "Option -k requires an argument."
                    exit 1
                fi
                keystrokesDir=$1
                ;;
            -p )
                profileMode=1
                ;;
            -r )
                shift
                if [ $# == 0 ]; then
                    echo "Option -r requires an argument."
                    exit 1
                fi
                resultsDir=$1
                ;;
            -s )
                stepMode=1
                ;;
            -h|--help)
                echo "Usage: $0 [options]"
                echo "options:"
		echo "   -a appDir         run tests only from appDir (absolute path)"
                echo "   -c                perform code coverage analysis"
                echo "   -h, --help        print this usage message"
                echo "   -k keystrokeDir   specify an alternate keystrokes directory"
                echo "   -p                create profile information"
                echo "   -r resultsDir     specify an alternate results directory"
                echo "   -s                require a return to be pressed between keystrokes files"
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

if [ "$coverageMode" -eq 1 ]
then
    runOrcaOnce=1
    export HARNESS_ASSERT=0
    echo generating coverage map...
    coverageDir=../coverage/`date +%Y-%m-%d_%H:%M:%S`
    mkdir -p $coverageDir
    cp $harnessDir/user-settings.conf.in user-settings.conf
    #echo $harnessDir/user-settings.conf.in
    trace2html.py -o $coverageDir -w orca -r $harnessDir/runorca.py &
    trace_pid=$!
    sleep 10
fi

if [ "$profileMode" -eq 1 ]
then
    runOrcaOnce=1
    export HARNESS_ASSERT=0
    echo generating profile information...
    cp $harnessDir/user-settings.conf.in user-settings.conf
    python $harnessDir/runprofiler.py&
    profiler_pid=$!
    sleep 10
fi

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
dirprefix=`date +%Y-%m-%d_%H:%M:%S`

if [ "x$testDirs" == "x" ]
then 
    testDirs=`find $keystrokesDir -type d | grep -v "[.]svn" | sort`
fi

for testDir in $testDirs
do
  application=`basename $testDir`
  if [ $application != ".svn" ] && [ $application != `basename $keystrokesDir` ]
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
      outputdir=$dirprefix/$application
      currentdir=`pwd`

      # We run under ./tmp as a means to help provide consistent
      # output for things that expose directory paths.
      #
      mkdir -p ./tmp/$application
      cd ./tmp/$application
      for testFile in `find $testDir -xtype f -name "*.py" | sort`; do
        echo ========================================
        echo Running $testFile
        if [ "$found" -gt 0 ]
        then
          $harnessDir/runone.sh $testFile $application $runOrcaOnce
        else
          osType=`uname`
          for os in $OPERATING_SYSTEMS; do
            if [ $application == $os ]
            then
              found=1
              if [ $osType == $os ]
              then
                $harnessDir/runone.sh $testFile $runOrcaOnce
              fi
            fi
          done
          if [ "$found" -eq 0 ]
          then
            $harnessDir/runone.sh $testFile $runOrcaOnce
          fi
        fi

        if [ "$runOrcaOnce" -eq 0 ]
        then
            # Copy the results (.orca) file to the output directory.
            # This is the file that will be used for regression
            # testing.
            newResultsFile=`basename $testFile .py`
            mkdir -p $currentdir/$outputdir

            # Filter the results...
            #
            # For braille, get rid of spurious "Desktop Frame" lines which
            # happen when there's enough of a pause for nautilus to think
            # it has focus.
            #
            # For speech, we do the same thing, but we need to get rid of
            # several lines in a row.  So, we use sed.
            #
            grep -v "Desktop Frame" $newResultsFile.braille > $currentdir/$outputdir/$newResultsFile.braille
            mv $newResultsFile.braille $currentdir/$outputdir/$newResultsFile.braille.unfiltered
            sed "/speech.speakUtterances utterance='Desktop frame'/,/speech.speakUtterances utterance='Icon View layered pane'/ d" $newResultsFile.speech > $currentdir/$outputdir/$newResultsFile.speech
            mv $newResultsFile.speech $currentdir/$outputdir/$newResultsFile.speech.unfiltered
            mv $newResultsFile.debug $currentdir/$outputdir
            rm -rf *
        fi

        echo Finished running $testFile.
        if [ "x$stepMode" == "x1" ]
        then
          echo Press Return to continue...
          read foo
        fi
        echo ========================================
      done
      cd $currentdir
      rm -rf ./tmp/$application
  fi
done

if [ "$coverageMode" -eq 1 ]
then
    rm user-settings.conf
    echo ...finished generating coverage map.
fi

if [ "$profileMode" -eq 1 ]
then
    rm -f user-settings.conf
    mkdir -p ../profile
    profileFilePrefix=../profile/`date +%Y-%m-%d_%H:%M:%S`
    python -c "import pstats; pstats.Stats('orcaprof').sort_stats('cumulative').print_stats()" > $profileFilePrefix.txt
    mv orcaprof $profileFilePrefix.orcaprof
    echo ...finished generating profile information.
fi

echo $dirprefix completed at `date +%Y-%m-%d_%H:%M:%S`
