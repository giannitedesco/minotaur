#!/bin/sh

set -euo pipefail

exec 1>&2

pkgname='minotaur'
scripts=setup.py

mypy --strict ${pkgname} ${scripts}

flake8 ${pkgname} ${scripts}
