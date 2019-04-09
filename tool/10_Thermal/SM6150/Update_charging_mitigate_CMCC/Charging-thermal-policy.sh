#!/bin/bash  
  
cd /sys/devices/virtual/thermal


strQuiet="quiet-therm-step"

for i in $(seq 1 120) 
do   
	type=$(cat /sys/devices/virtual/thermal/thermal_zone$i/type) ;
	if  [[ $type == *$strQuiet* ]] 
	then
		echo "type is $type and need to update charging mitigate threshold"
		echo "disabled" > /sys/devices/virtual/thermal/thermal_zone$i/mode
		echo 32000 > /sys/devices/virtual/thermal/thermal_zone$i/trip_point_3_temp
		echo 33000 > /sys/devices/virtual/thermal/thermal_zone$i/trip_point_5_temp
		echo 34000 > /sys/devices/virtual/thermal/thermal_zone$i/trip_point_6_temp
		echo 35000 > /sys/devices/virtual/thermal/thermal_zone$i/trip_point_8_temp
		
		echo 4000 > /sys/devices/virtual/thermal/thermal_zone$i/trip_point_3_hyst
		echo 1000 > /sys/devices/virtual/thermal/thermal_zone$i/trip_point_5_hyst
		echo 1000 > /sys/devices/virtual/thermal/thermal_zone$i/trip_point_6_hyst
		echo 1000 > /sys/devices/virtual/thermal/thermal_zone$i/trip_point_8_hyst
		
		echo "enabled" > /sys/devices/virtual/thermal/thermal_zone$i/mode
		
		echo "Confirm mode and threshold"
		cat /sys/devices/virtual/thermal/thermal_zone$i/mode
		cat /sys/devices/virtual/thermal/thermal_zone$i/trip_point_3_temp
		cat /sys/devices/virtual/thermal/thermal_zone$i/trip_point_5_temp
		cat /sys/devices/virtual/thermal/thermal_zone$i/trip_point_6_temp
		cat /sys/devices/virtual/thermal/thermal_zone$i/trip_point_8_temp
		
	else 
		echo "No need to disable zone$i mode"
	fi
done 
