#!/bin/sh
#
# Renders the Mallard help files into HTML for publishing to a web site.
#
# Assumes that a previous script has put all the Mallard docs in _build/help/* where
# the * is the language name (C, es, ja, etc.).
#
# The rendered pages are put under public/ per the convention for GitLab pages.
#
# In the end this is created:
#
# public/
#   index.html      - landing page
#   help/           - Help pages in English (from the original help/C)
#   help/es         - Spanish help
#   help/ja         - Japanese help
#   help/...        - etc.

set -eux -o pipefail

OUTPUT_DIR=$(realpath public)

toplevel=$(pwd)

LANGLINKS=" "
mkdir -p $OUTPUT_DIR/help
for d in $toplevel/_build/help/*
do
  if [ -d "$d" ]; then
    lang=$(basename $d)
    cd $d
    echo "Generating help for $lang"
    if [ $lang == "C" ]; then
      yelp-build html -o $OUTPUT_DIR/help .
      # special case to avoid having "C" in the human-readable list of languages  
      LANGLINKS="${LANGLINKS}<a href='help/'>en</a> "
    else
      lang_output_dir=$OUTPUT_DIR/help/$lang
      mkdir $lang_output_dir
      yelp-build html -o $lang_output_dir . -p ../C
      LANGLINKS="${LANGLINKS}<a href='help/$lang/'>$lang</a> "
    fi
    cd $toplevel
  fi
done
echo "User manual for Orca: ${LANGLINKS}" > $OUTPUT_DIR/index.html
