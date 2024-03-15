#!/bin/sh
#
# Once Orca is built in a _build directory by another script, _build/help/ will contain
# the translated help files as Mallard .page files.
#
# However, the original docs (help/C/ in the srcdir) are not there,
# since they are not translations.  This script just copies that
# directory to the one with the translations so that the help files
# for all languages can be rendered later into HTML.

set -eux -o pipefail

cp -r help/C/ _build/help/C/
