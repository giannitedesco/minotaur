#!/bin/sh

set -euo pipefail

exec 1>&2

pkgname='minotaur'
scripts=setup.py

mypy \
	--disallow-any-generics \
	--warn-redundant-casts \
	--warn-unused-ignores \
	--no-warn-no-return \
	--warn-return-any \
	--check-untyped-defs \
	--no-implicit-optional \
	--ignore-missing \
	${pkgname} ${scripts}

pycodestyle-3 \
	${pkgname}

#./unit-tests.sh
