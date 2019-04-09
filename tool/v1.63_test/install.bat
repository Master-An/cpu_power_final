pushd "%~dp0"
adb wait-for-device
adb root
adb remount

adb push powerall.bash /data/local/tmp/
adb push tool\powertop  /data/local/tmp/
adb push tool\idlestat  /data/local/tmp/
adb push tool\cpustatus  /data/local/tmp/
adb push tool\ctlogger  /data/local/tmp/
adb push tool\cplogger.conf /data/local/tmp/
adb push tool\atrace_userdebug.rc /system/etc/init/
adb shell chmod 777 /data/local/tmp/powerall.bash
adb shell chmod 777 /data/local/tmp/powertop
adb shell chmod 777 /data/local/tmp/idlestat
adb shell chmod 777 /data/local/tmp/cpustatus
adb shell chmod 777 /data/local/tmp/ctlogger
adb shell chmod 777 /data/local/tmp/cplogger.conf 

adb shell sync
adb shell sync

  