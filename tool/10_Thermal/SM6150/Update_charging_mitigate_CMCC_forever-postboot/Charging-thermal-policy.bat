
adb wait-for-device root
adb wait-for-device disable-verity
adb wait-for-device remount

echo "push new limit config to device"
adb wait-for-device push init.qcom.post_boot.sh /vendor/bin/init.qcom.post_boot.sh
adb shell sync
echo "reboot device"
adb reboot

pause

