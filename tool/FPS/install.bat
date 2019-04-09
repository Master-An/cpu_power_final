adb wait-for-device
adb root
adb wait-for-device
adb remount
adb wait-for-device
adb push fps.sh /data/local/tmp/
adb shell "chmod 777 /data/local/tmp/fps.sh"

