#!/bin/bash -ex

DAEMON_ARGUMENTS=$(snapctl get camera-detect-stream.arguments)

exec $@ $DAEMON_ARGUMENTS
