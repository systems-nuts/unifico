#!/usr/bin/env bash

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]:-$0}")" &>/dev/null && pwd 2>/dev/null)"

gdb -x ${SCRIPT_DIR}/../gdb_util/migrate.py -ex "migrate ${1}" -ex "run" -ex "quit" ${2}
