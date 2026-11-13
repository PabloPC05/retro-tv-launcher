#!/bin/bash
# screenshot.sh [file.png]: grabs what the TV shows.
. "$(dirname "$0")/common.sh"
a exec-out screencap -p > "${1:-screenshot.png}"
