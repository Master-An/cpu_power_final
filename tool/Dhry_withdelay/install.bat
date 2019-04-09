adb wait-for-device
adb root
adb wait-for-device
adb remount
adb wait-for-device
adb push dhrystone /data/local/tmp/
adb shell "chmod 0777 /data/local/tmp/dhrystone" 

pause