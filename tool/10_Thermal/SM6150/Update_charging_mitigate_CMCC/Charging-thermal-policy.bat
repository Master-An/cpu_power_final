
adb wait-for-device root
adb wait-for-device remount

adb push Charging-thermal-policy.sh /data/local/tmp/
adb shell "chmod 777 /data/local/tmp/Charging-thermal-policy.sh"
adb shell ". /data/local/tmp/Charging-thermal-policy.sh"



pause

