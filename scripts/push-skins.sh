#!/bin/bash
# push-skins.sh [win98 xp 8bit]: stores the skins from skins/ on the box (theme folder, skins/<name>/),
# through the launcher's theme provider. About a minute per skin.
. "$(dirname "$0")/common.sh"
for S in ${@:-win98 xp 8bit}; do
  a shell rm -rf /data/local/tmp/sk
  a push "$ROOT/skins/$S" /data/local/tmp/sk >/dev/null
  a shell "cd /data/local/tmp/sk && n=0; for f in \$(find . -type f | sed s,^./,,); do content write --uri content://$PKG.theme/skins/$S/\$f < \$f && n=\$((n+1)); done; cd /; rm -rf /data/local/tmp/sk; echo $S: \$n files"
done
