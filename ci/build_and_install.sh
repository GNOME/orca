#!/bin/sh

set -eux -o pipefail

source ci/env.sh
meson setup -D prefix=/usr _build
meson compile -C _build
meson install -C _build
