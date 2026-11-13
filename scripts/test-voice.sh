#!/bin/bash
# test-voice.sh "phrase": sends a typed query to the Google assistant, as if it had been said to the remote's mic.
. "$(dirname "$0")/common.sh"
a shell am start -a android.search.action.GLOBAL_SEARCH --es query "\"$1\""
