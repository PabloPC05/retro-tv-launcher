# Shared settings. TV = the Android TV box's adb address (adb over the network must be enabled on it).
#   export TV=192.168.1.50:5555
TV=${TV:?set TV to your box, e.g. export TV=192.168.1.50:5555}
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
PKG=com.gathin.tvhome
adb connect "$TV" >/dev/null 2>&1
a() { adb -s "$TV" "$@"; }
