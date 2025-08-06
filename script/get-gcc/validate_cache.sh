#!/bin/bash


if [[ -n "$MLC_GCC_DIR_PATH" && -e "$MLC_GCC_DIR_PATH" ]]; then
    if [[ "$(realpath "$MLC_GCC_DIR_PATH")" != "$(realpath "$MLC_GCC_INSTALLED_PATH")" ]]; then
        exit 1
    fi
fi

test $? -eq 0 || exit $?
exit 0
