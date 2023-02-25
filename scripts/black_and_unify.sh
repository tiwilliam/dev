#!/usr/bin/env bash

set -e

black --line-length=100 --skip-string-normalization "$@"
unify "${@: -1}" | sed -e '1,2d'
