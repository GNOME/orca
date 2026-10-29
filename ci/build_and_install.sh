#!/bin/sh

set -eux -o pipefail

meson setup -D prefix=/usr -D mathcat="${ORCA_BUILD_MATHCAT:-false}" _build
meson compile -C _build
meson install -C _build
