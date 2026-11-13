#!/bin/bash
# skin.sh win98|xp|8bit: switches the skin (restarts the home screen).
. "$(dirname "$0")/common.sh"
case $1 in win98) A=SkinWin98;; xp) A=SkinXp;; 8bit) A=Skin8bit;; *) echo "usage: skin.sh win98|xp|8bit"; exit 2;; esac
a shell am start -n $PKG/.$A
