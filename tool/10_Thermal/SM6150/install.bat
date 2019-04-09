pushd "%~dp0"
adb wait-for-device root
adb wait-for-device remount
adb push ctlogger /data/local/tmp/
adb push ctlogger.conf /data/local/tmp/
adb shell chmod 777 /data/local/tmp/ctlogger
adb shell chmod 777 /data/local/tmp/ctlogger.conf
pause