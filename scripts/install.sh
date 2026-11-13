#!/bin/bash
# install.sh: installs the built APK on the box (keeps data). First time only: make it the Home app
# (see android/build-and-install.sh for the full first-install steps).
. "$(dirname "$0")/common.sh"
a install -r "$ROOT/android/app/build/outputs/apk/release/app-release.apk"
