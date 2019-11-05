#!/bin/bash
#
# Arguments:
#   1. fragment_file: The file to update inline.

action() {
    # get and check arguments
    local fragment_file="$1"
    local nose_bool="$2"

    if [ -z "$fragment_file" ]; then
        2>&1 echo "please pass a fragment file as argument 1"
        return "1"
    fi
    if [ ! -f "$fragment_file" ]; then
        2>&1 echo "the fragment file '$fragment_file' does not exist"
        return "2"
    fi

    # customisation occurs here
    local hook="# Customisation from command line"
    local content="# customisation for nose\ndoNose = ${nose_bool}"

    # do the injection
    sed "/$hook/a $content" -i "$fragment_file"
}
action "$@"
