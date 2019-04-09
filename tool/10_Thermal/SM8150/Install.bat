
adb root
adb wait-for-device
adb remount
adb wait-for-device
adb push ctlogger /data/local/tmp/
adb push ctlogger.conf /data/local/tmp/
adb shell chmod 777 /data/local/tmp/ctlogger
adb shell chmod 777 /data/local/tmp/ctlogger.conf

Pause

echo "Run via command"