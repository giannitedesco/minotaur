#!/bin/sh

set -euo pipefail

exec 1>&2

pkgname='minotaur'
scripts=

mypy --strict ${pkgname} ${scripts}

bandit \
	${pkgname} ${scripts}

flake8 ${pkgname}

# green
