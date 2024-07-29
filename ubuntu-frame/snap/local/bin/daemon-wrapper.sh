#!/bin/bash -ex

DAEMON_ARGUMENTS=$(snapctl get camera-detect-stream.arguments)

if [ -z "${DAEMON_ARGUMENTS}" ]; then
    exec $@
else
    exec $@ $DAEMON_ARGUMENTS
fi
