#!/bin/bash
# build.sh: builds the launcher APK (needs the Android SDK: export ANDROID_HOME=...; JDK 17)
set -e
cd "$(dirname "$0")/../android"
./gradlew assembleRelease -q --console=plain
ls -la app/build/outputs/apk/release/
