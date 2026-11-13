#!/bin/bash
# enable-voice.sh: turns on the "Skins por voz" accessibility service, keeping any service already enabled.
. "$(dirname "$0")/common.sh"
a shell 'cur=$(settings get secure enabled_accessibility_services); case "$cur" in *SkinVoiceService*) ;; null|"") settings put secure enabled_accessibility_services '$PKG'/.SkinVoiceService ;; *) settings put secure enabled_accessibility_services "$cur:'$PKG'/.SkinVoiceService" ;; esac; settings put secure accessibility_enabled 1; settings get secure enabled_accessibility_services'
