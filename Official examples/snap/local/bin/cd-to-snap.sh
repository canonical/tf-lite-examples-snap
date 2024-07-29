#!/bin/bash

cd $SNAP

# Clear session manager variable to remove "Qt: Session management error: Could not open network socket"
export -n SESSION_MANAGER

# Remove "Warning: Ignoring XDG_SESSION_TYPE=wayland on Gnome. Use QT_QPA_PLATFORM=wayland to run on Wayland anyway."
export -n XDG_SESSION_TYPE

exec "$@"
