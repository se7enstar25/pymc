#!/usr/bin/env bash

set -ex # fail on first error, print commands

while test $# -gt 0; do
  case "$1" in
  --global)
    GLOBAL=1
    ;;
  --no-setup)
    NO_SETUP=1
    ;;
  esac
  shift
done

command -v conda >/dev/null 2>&1 || {
  echo "Requires conda but it is not installed.  Run install_miniconda.sh." >&2
  exit 1
}

ENVNAME="${ENVNAME:-testenv}"         # if no ENVNAME is specified, use testenv

if [ -z ${GLOBAL} ]; then
  if conda env list | grep -q ${ENVNAME}; then
    echo "Environment ${ENVNAME} already exists, keeping up to date"
  else
    conda config --add channels conda-forge
    conda config --set channel_priority strict
    conda env create -f environment-dev.yml
  fi
  source activate ${ENVNAME}
fi

conda update --yes --all

#  Install editable using the setup.py
if [ -z ${NO_SETUP} ]; then
  python setup.py build_ext --inplace
fi
