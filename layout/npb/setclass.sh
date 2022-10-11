#!/bin/bash

HELP_STR="Usage: $0 {S | A | B | C}"
HEADER_FILE=npbparams.h

[[ $# -ne 1 ]] && echo "${HELP_STR}" && exit 1

[[ $1 != "S" && $1 != "A" && $1 != "B" && $1 != "C" ]] &&
  echo "${HELP_STR}" && exit 2

CLASS=$1

for W in bt cg dc ep ft is lu mg sp ua; do
  cd $W
  rm -f ${HEADER_FILE}

  BMK_CLASS=$CLASS
  if [[ $W == "dc" && $CLASS == "C" ]]; then
    BMK_CLASS="B"
    echo "warning: using class ${BMK_CLASS} for benchmark ${W}"
  fi

  ln -s npbparams-${BMK_CLASS}.h ${HEADER_FILE}
  cd ..
done
