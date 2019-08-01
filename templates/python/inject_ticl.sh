#!/bin/bash

# This script injects the lines required to run ticl into a
# reconstruction fragment obtained through (e.g.) runTheMatrix.py.
#
# A function is used to be able to use local variables.
#
# Arguments:
#   1. fragment_file: The file to update inline.

action() {
    # get and check arguments
    local fragment_file="$1"
    if [ -z "$fragment_file" ]; then
        2>&1 echo "please pass a fragment file as argument 1"
        return "1"
    fi
    if [ ! -f "$fragment_file" ]; then
        2>&1 echo "the fragment file '$fragment_file' does not exist"
        return "2"
    fi

    # define what to inject where
    local hook="# customisation of the process."
    local content="# run TICL\nfrom RecoHGCal.TICL.ticl_iterations import TICL_iterations_withReco\nprocess = TICL_iterations_withReco(process)"

    # do the injection
    sed "/$hook/a $content" -i "$fragment_file"
}
action "$@"
