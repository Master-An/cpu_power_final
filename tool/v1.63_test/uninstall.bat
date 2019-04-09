adb wait-for-device
adb root
adb remount

adb shell rm /data/local/tmp/powerall.bash
adb shell rm /data/local/tmp/powertop
adb shell rm /data/local/tmp/idlestat
adb shell rm /data/local/tmp/cpustatus
adb shell rm /data/local/tmp/ctlogger
adb shell rm /data/local/tmp/cplogger.conf
adb shell rm -f -r /data/local/tmp/powerall

adb shell sync
adb shell sync

  