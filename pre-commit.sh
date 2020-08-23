#!/bin/sh

set -euo pipefail

exec 1>&2

pkgname='minotaur'
scripts=setup.py

mypy \
	--check-untyped-defs \
	--no-implicit-optional \
	--ignore-missing \
	${pkgname} ${scripts}

pycodestyle-3 \
	${pkgname}

#./unit-tests.sh
