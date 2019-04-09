# QUALCOMM POWERALL - power logging console
# 
# v1.32
# 1) support clk dump for MSM8998 and SDM660.
# 2) support MTK and KIRIN device.
# 3) support cycle and interval choose for top, clk and lpm dump.
# 4) change path to /data/local/tmp/powerall which can get logs on unroot mode.
# v1.33
# 1) fix a bug on lpm process.
# 2) change the ftrace function style to fix sometime miss ftrace issue.
# v1.40
# 1) support PTT automatic tool.
# 2) change the ftrace buffer size to support big size Ftrace log.
# 3) dump out bugreport and battery on basic process.
# 4) add duration and sampling time for most cases which can support long duration log catch.
# 5) change cpu load process to c execute app.
# 6) add min dump process, which used to capture clk/ldo/lpm/wake/dmesg/logcat together with same duration and sampling time.
# 7) change dmesg log capture way, which can support long time and APSS sleep/wakeup case.
# 8) support accurate fps and jank capture.
# 9) support su command to capture unrooted device’s data.
#10) add idlestat tool to get CPU idle/frequency/wakeup information from Ftrace.
# v1.41
# 1) Support no surface view case for Game FPS capture.
# 2) Support auto method to capture appointed logs.
# v1.42
# 1) Fix a bug for Android O FPS capture.
# v1.43
# 1) add new bmic clk node to support SDM845 and SDM670.
# 2) add l3_clk, l3_cluster0_vote_clk,l3_cluster1_vote_clk clk node for Napali.
# v1.44
# 1) add some nodes - pwrclk,perclk,cpubw,core_ctl_isolated and thermal cooling.
# 2) add new node to support sleep status capture for napali and sdm670.
# 3) update top and powertop to support android O.
# 4) fix print bug in cpu_logger
# 5) support ftrace capture for game and no game case.
# 6) add new HW IRQ mask on dmesg to support napali.
# v1.45
# 1) add new events for ftrace.
# v1.50
# 1) change log menu to support different application scenarios.
# 2) support systrace log.
# 3) remove some useless functions.
# 4) support BW/BIMC nodes for SDM855.
# 5) change some ftrace events.
# 6) change tool install manner, pack tool to a .exe file.
# v1.52
# 1) fix FPS issue for Android P.
# 2) support SM8150 BIMC node.
# 3) enable kernel prink log for unmask dmsg.
# 4) add some ftrace events
# 5) support latest GPU frequency and load for MTK device.
# 6) support to read out all cpu/bus governor and scheduler information.
# v1.53
# 1) support for talos related nodes.
# 2) fix version and back-light readout issue.
# 3) auto remove invalid path for external nodes.
# 4) change some ftrace events to support SM8150.
# 5) remove temperature information in cpu_logger.
# v1.54
# 1) fix a bug for ftrace capture.
# v1.55
# 1) adjust ftrace to four scenes: normal,game,sleep,camera.
# 2) fix ftrace overwrite issue and add process id for ftrace.
# 3) capture enabled clocks and regulators.
# 4) add camera ife and display mdp in cpu logger.
# 5) add externals node for mx/cx/snoc/cnoc related.
# v1.60
# 1) this version only changed cpu logger related.
# 2) change CPU Frequency/Load calculation.
# 3) change GPU/BIMC Frequency calculation.
# 4) change FPS/Jank calculation.
# 5) add chip vendor and rooted checking.
# 6) fix bugs for MTK/Hisilicon CPU/GPU frequency and load calculation.
# v1.61
# 1) fix one time FPS 0 issue.
# 2) change some column names.
# 3) fix cluster relative cpu name.
# 4) show HW FPS in file.
# 5) fix thread reopen issue.
# v1.62
# 1) remove BIMC node which will impact performance.
# 2) add gpubw in main list.
# 3) fix a bug for kirin chip scan.
# 5) add ftrace events bus_client_status and dump_clients event.
# v1.63
# 1) use high precision timer and do correction for FPS capture window.
# 2) remove some unnecessary nodes.
# 3) move CPULLCCBW/CPUDDRBW/GPUBW nodes to external files.

#/*delay time before capturing*/
delay_time=2
#/*define log path*/
log_path="/data/local/tmp/powerall"
#/*define tool path*/
tool_path="/data/local/tmp"
#/*product type*/
product_type=MSM
#/*Android Version*/
android_ver=6

#/*capture basic information, dmesg, logcat ... dump, save to data/powerall/basic_information_dump.txt and others*/
function basic_process()
{
	start_time=$(date +%s);
	echo "Start basic_process ...";
	
	rm -rf $log_path/printing.txt;
	rm -rf $log_path/basic_information_dump.txt;
	rm -rf $log_path/ps_dump.txt;
	rm -rf $log_path/dmesg_dump.txt;
	rm -rf $log_path/logcat_dump.txt
	rm -rf $log_path/dumpsys.txt
	rm -rf $log_path/LDO_consumers.txt
	rm -rf $log_path/bugreport.txt
	rm -rf $log_path/batterystats.txt
	rm -rf $log_path/SurfaceFlinger.txt
	rm -rf $log_path/thermal-engine.conf
	
	echo "Start basic_process ..." >> $log_path/printing.txt
	#/*Time*/
	echo Date Time: `date +%Y/%m/%d-%H:%M:%S` >> $log_path/basic_information_dump.txt
	#/*Build*/
	if [ -d /firmware/verinfo ]; then
		echo Build: `cat /firmware/verinfo/ver_info.txt` >> $log_path/basic_information_dump.txt
	else
		echo Build: `cat /vendor/firmware_mnt/verinfo/ver_info.txt` >> $log_path/basic_information_dump.txt
	fi
	#/*Linux version*/
	echo Linux version: `cat /proc/version` >> $log_path/basic_information_dump.txt
	#/*Serial number*/
	echo Serial number: `getprop ro.serialno` >> $log_path/basic_information_dump.txt
	#/*Hardware*/
	echo Hardware: `getprop ro.hardware` >> $log_path/basic_information_dump.txt
	#/*backlight*/
	if [ -d /sys/class/leds/wled ]; then
		echo lcd_brightness: `cat /sys/class/leds/wled/brightness` >> $log_path/basic_information_dump.txt
	fi
	#/*airplane*/
	echo airplane_mode: `settings get global airplane_mode_on` >> $log_path/basic_information_dump.txt
	#/*bt*/
	echo bluetooth_stat: `settings get global bluetooth_on` >> $log_path/basic_information_dump.txt
	#/*wifi/
	echo wifi_stat: `settings get global wifi_on` >> $log_path/basic_information_dump.txt
	#/*charging or not?*/
	echo charging?: `cat /sys/class/power_supply/battery/status` >> $log_path/basic_information_dump.txt
	#/*governor*/
	echo CPU0 governor : `cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>>$log_path/printing.txt` >> $log_path/basic_information_dump.txt
	echo CPU1 governor : `cat /sys/devices/system/cpu/cpu1/cpufreq/scaling_governor 2>>$log_path/printing.txt` >> $log_path/basic_information_dump.txt
	#/*rotation/
	echo portrait_stat: `settings get system accelerometer_rotation` >> $log_path/basic_information_dump.txt
	#/*wakelock/
	echo wake_lock : `cat /sys/power/wake_lock 2>>$log_path/printing.txt` >> $log_path/basic_information_dump.txt
	#/*cmdline*/
	echo cmdline : `cat /proc/cmdline` >> $log_path/basic_information_dump.txt

	#/* Scheduler parameters */
	cd /proc/sys/kernel/
	echo "" >> $log_path/basic_information_dump.txt
	echo \-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\- Scheduler \-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\- >> $log_path/basic_information_dump.txt
	for i in *; do if [[ $i == sched_* ]]; then echo $i \=\ `cat $i 2>>$log_path/printing.txt`; fi; done >> $log_path/basic_information_dump.txt
	cd /;

	#/* Governor parameters */
	echo "" >> $log_path/basic_information_dump.txt
	echo \-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\- Governor \-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\- >> $log_path/basic_information_dump.txt
	cd /sys/devices/system/cpu
	for i in 0 1 2 3 4 5 6 7 8 9; 
	do if [ -d cpu$i ]; then
		cd cpu$i
		for j in *; 
		do if [ -d $j ]; then
			cd $j
			for k in *; 
			do if [ -d $k ]; then
				cd $k
				for l in *; 
				do if [ ! -d $l ]; then echo cpu$i/$j/$k/$l \=\ `cat $l 2>>$log_path/printing.txt`; fi; done >> $log_path/basic_information_dump.txt
				cd ../
			else
				echo cpu$i/$j/$k \=\ `cat $k 2>>$log_path/printing.txt` >> $log_path/basic_information_dump.txt;
			fi
			done
			cd ../
		else
			echo cpu$i/$j \=\ `cat $j 2>>$log_path/printing.txt` >> $log_path/basic_information_dump.txt;
		fi
		done
		cd ../
	else
		cd /sys/devices/system/cpu
	fi
	done
	
	#/* Add for support MSM8917/8920 */
	if [ -d cpufreq/interactive ]; 
	then
	cd cpufreq/interactive;
	for j in *; do echo interactive/$j \=\ `cat $j 2>>$log_path/printing.txt`; done >> $log_path/basic_information_dump.txt;
	fi;
	cd /;
	
	#/* Add for support BW related node */
	echo "" >> $log_path/basic_information_dump.txt
	echo \-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\- BW related \-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\- >> $log_path/basic_information_dump.txt
	cd /sys/class/devfreq/
	for i in *; 
	do if [[ $i == soc* ]]; then
		cd $i
		for j in *; 
		do if [ -d $j ]; then
			cd $j
			for k in *;  
			do if [ ! -d $k ]; then echo $i/$j/$k \=\ `cat $k 2>>$log_path/printing.txt`; fi; done >> $log_path/basic_information_dump.txt
			cd ../
		else
			echo $i/$j \=\ `cat $j 2>>$log_path/printing.txt` >> $log_path/basic_information_dump.txt;
		fi
		done
		cd ../
	else
		cd /sys/class/devfreq/
	fi
	done
	
	cd /
	
	#/* GPU parameters */
	echo "" >> $log_path/basic_information_dump.txt
	echo \-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\- GPU Governor\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\- >> $log_path/basic_information_dump.txt
	
	if [[ $product_type == MSM ]]; then
		cd /sys/class/kgsl/kgsl-3d0/;
		for i in *;do if [[ $i == gpu* ]]; then echo $i \=\ `cat $i 2>>$log_path/printing.txt`; fi; done >> $log_path/basic_information_dump.txt
		cd devfreq;
		for j in *;do echo $j \=\ `cat $j 2>>$log_path/printing.txt`; done >> $log_path/basic_information_dump.txt
		cat trans_stat >> $log_path/basic_information_dump.txt
	elif [[ $product_type == KIRIN ]]; then
		cd /sys/devices/e8970000.mali/;
		for i in *;do if [[ $i == gpu* ]]; then echo $i \=\ `cat $i 2>>$log_path/printing.txt`; fi; done >> $log_path/basic_information_dump.txt
		cd devfreq/gpufreq;
		for j in *;do echo $j \=\ `cat $j 2>>$log_path/printing.txt`; done >> $log_path/basic_information_dump.txt
		cat trans_stat >> $log_path/basic_information_dump.txt
	elif [[ $product_type == MTK ]]; then
		cd /proc/mali
		for i in *;do echo `cat $i 2>>$log_path/printing.txt`; done >> $log_path/basic_information_dump.txt
		cd /
		cd /proc/gpufreq
		for i in *;do echo `cat $i 2>>$log_path/printing.txt`; done >> $log_path/basic_information_dump.txt
	else
		cd /;
	fi

	cd /;
	
	// add LDO consumers
	if [[ $product_type == MSM ]]; then
		cd /sys/kernel/debug/regulator
		for i in *
		do
		  #if [ "${i:0:2}"x = "pm"x ];  then
		  if [ -d $i ]; then
			if [ -e $i/enable ]; then
				if [ "$(cat $i/enable)" == "1" ]; then
					if [ -e $i/voltage ]; then 
						echo $i \=\> enable:`cat $i/enable` voltage:`cat $i/voltage`;
						echo consumers:`cat $i/consumers`;
					else 
						echo $i \=\> enable:`cat $i/enable` voltage: N\/A;
						echo consumers:`cat $i/consumers`; 
					fi;
				fi;
			fi;
		fi;
		done > $log_path/LDO_consumers.txt

		cd /
		
		#/* thermal engine config */
		thermal-engine -o > $log_path/thermal-engine-config.txt
		cp -rf /vendor/etc/thermal-engine.conf $log_path/thermal-engine.conf
	fi
	#/* ps */
	ps -A > $log_path/ps_dump.txt
	#/* dmesg */
	dmesg > $log_path/dmesg_dump.txt
	#/* logcat */
	#logcat -v time -b main > $log_path/main_dump.txt -d
	#logcat -v time -b system > $log_path/system_dump.txt -d 
	#logcat -v time -b radio > $log_path/radio_dump.txt -d 
	#logcat -v time -b events > $log_path/events_dump.txt -d 
	#logcat -v time -b crash > $log_path/crash_dump.txt -d 	
	logcat -v time -b all > $log_path/logcat_dump.txt -d 
	
	#/* dumpsys  */
	if [ "$1" =  "" ]; then
		#/* v1.34 add dumpsys and bugreport */
		#dumpsys > $log_path/dumpsys.txt
		bugreport > $log_path/bugreport.txt
	else
		#/* v1.50 add batterystats and SurfaceFlinger for quick dump */
		dumpsys batterystats > $log_path/batterystats.txt
		dumpsys SurfaceFlinger > $log_path/SurfaceFlinger.txt
	fi
	
	#/* procrank */
	#procrank > $log_path/procrank_dump.txt
  
	end_time=$(date +%s);
	echo "Finished basic_process spent $(($end_time - $start_time))s, log in $log_path";
	echo "Finished basic_process spent $(($end_time - $start_time))s, log in $log_path" >> $log_path/printing.txt
}

#/*capture top and powertop dump, save to data/powerall/dumptop.txt*/
function top_process()
{
    j=0
	start_time=$(date +%s);
	rm -rf $log_path/dumptop.txt;
	
    #powertop_file="/data/powertop"
    if [ ! -e "$tool_path/powertop" ]; then
      echo "no powertop in /data/ !!!, please copy one";
      echo "no powertop in /data/ !!!, please copy one" >> $log_path/printing.txt
      echo "Start top_process ...";
	  echo "Start top_process ..." >> $log_path/printing.txt
		while (($j<$1))
		  do
		    echo cycles $j: `date +%Y/%m/%d-%H:%M:%S`;
			echo \=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\= top \=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=;
		    top -d 1 -n 1
		    j=$(($j+1))
		done > $log_path/dumptop.txt
		end_time=$(date +%s);
      echo "Finished top_process spent $(($end_time - $start_time))s, log in $log_path";	
      echo "Finished top_process spent $(($end_time - $start_time))s, log in $log_path" >> $log_path/printing.txt	  
	else
		echo "Start top_process ...";
		echo "Start top_process ..." >> $log_path/printing.txt
		while (($j<$1))
		  do
			echo cycles $j: `date +%Y/%m/%d-%H:%M:%S`;
		    echo \=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\= top \=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=;
		    top -d 1 -n 1
		    echo \-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\- powertop \-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-;
		    $tool_path/powertop -r -d -t 5
			j=$(($j+1))
		done > $log_path/dumptop.txt
		end_time=$(date +%s);
		echo "Finished top_process spent $(($end_time - $start_time))s, log in $log_path";
		echo "Finished top_process spent $(($end_time - $start_time))s, log in $log_path" >> $log_path/printing.txt
	fi
}

#/*capture clock and LDO dump, save to $log_path/clk_ldo_dump.txt*/
function clk_ldo_process()
{
    j=0
	start_time=$(date +%s);
	rm -rf $log_path/clk_ldo_dump.txt;
	
	echo "clk_ldo_process Started ...";
	echo "clk_ldo_process Started ..." >> $log_path/printing.txt
	while(($j<$1))
	do
		echo cycles $j: `date +%Y/%m/%d-%H:%M:%S`;
        echo \=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\ clock =\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=;
		if [[ $product_type == MSM ]]; then
			if [ -e /d/clk/enabled_clocks ];then
				cat /d/clk/enabled_clocks
			else
				cat /d/clk/clk_enabled_list
			fi
		elif [[ $product_type == KIRIN ]]; then
			cat /d/clock/clock_tree
		elif [[ $product_type == MTK ]]; then
			cat /d/clk/enabled_clocks
		else
			cat /d/clk/enabled_clocks
		fi
		
		echo \=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\ clock lvl =\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=;
		cd /sys/kernel/debug/clk;
		for i in *;
		do if [ -d $i ];
			then if [ "$(cat $i/clk_enable_count)" != "0" ];
				then if [ -e $i/clk_rate ] && [ -e $i/clk_rate_max ] && [ "$(cat $i/clk_rate)" != "0" ];
					then echo $i \=\> clk_enable_count:`cat $i/clk_enable_count` rate:`cat $i/clk_rate`;
						 echo clk_rate_max:`cat $i/clk_rate_max`;
					elif [ -e $i/clk_rate ] && [ "$(cat $i/clk_rate)" != "0" ];
						then echo $i \=\> clk_enable_count:`cat $i/clk_enable_count` rate:`cat $i/clk_rate`;
					fi; 
				fi; 
			fi; 
		done;
		
        echo \-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\- LDO \-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-;
        cd /sys/class/regulator;
	    for i in *;
	    do if [ -d $i ];
    	   then if [ -e $i/state ];
		     then if [ "$(cat $i/state)" == "enabled" ];
			   then if [ -e $i/microvolts ];
			     then echo $i \=\> name:`cat $i/name` state:`cat $i/state` user:`cat $i/num_users` microvolt:`cat $i/microvolts`;
				 else echo $i \=\> name:`cat $i/name` state:`cat $i/state` user:`cat $i/num_users` microvolt: N\/A; 
				 fi; 
				fi;
			  fi; 
			fi; 
		done; 
    sleep $2;
	j=$(($j+1))
	done > $log_path/clk_ldo_dump.txt
	
	end_time=$(date +%s);
    echo "Finished clk_ldo_process spent $(($end_time - $start_time))s, log in $log_path";
	echo "Finished clk_ldo_process spent $(($end_time - $start_time))s, log in $log_path" >> $log_path/printing.txt
}

#/* capture wakelock,interrupt,wakeup_sources dump, save to data/powerall/wake_int_dump.txt */
function wake_process()
{
    j=0
	start_time=$(date +%s);
	rm -rf $log_path/wake_int_dump.txt;
	
	echo "wake_process Started ...";
	echo "wake_process Started ..." >> $log_path/printing.txt
	while (($j<$1))
	  do
	    echo cycles $j: `date +%Y/%m/%d-%H:%M:%S`;
		echo \=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\= wakeup_sources \=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=;
		#for example : cat wakeup_sources | grep msm_otg
		# msm_otg         6               6               0               0               52445
		# active_since = 52445 (52s) , msm_otg vote against system sleep 52s.
		cat /sys/kernel/debug/wakeup_sources
		echo \-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\- wakelocks \-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-;
		cat /sys/power/wake_lock
		echo \~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~ interrupts \~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~;
		cat /proc/interrupts
		sleep $2;
		j=$(($j+1))
	done > $log_path/wake_int_dump.txt
	
	end_time=$(date +%s);
	echo "finished wake_process spent $(($end_time - $start_time))s, log in $log_path";
	echo "finished wake_process spent $(($end_time - $start_time))s, log in $log_path" >> $log_path/printing.txt
}

#/* capture lpm state, c-state, save to data/powerall/lpmstat.txt */
function lpm_process()
{
    j=0
	start_time=$(date +%s);
	rm -rf $log_path/lpmstat.txt;
	echo "lpm_process Started ..."

	#/*print */
	echo "lpm_process Started ..." >> $log_path/printing.txt
	echo \=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\= rpm_stats \- indicate XO and Vddmin \=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\= > $log_path/lpmstat.txt

	echo reset > /d/lpm_stats/stats;
	while (($j<$1))
	do
		sleep $2;
		j=$(($j+1))
		echo cycles $j: `date +%Y/%m/%d-%H:%M:%S`;
		echo \=\=\=\=\=\=\=\=\=\=\=\=\=\=\= APSS XO status \=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=;
		if [ -e /d/rpm_stats ];then
			cat /d/rpm_stats
			cat /d/rpm_master_stats
		else
			cat /sys/power/system_sleep/stats
			cat /sys/power/rpmh_stats/master_stats
		fi
		
		cat /d/lpm_stats/stats
	done >> $log_path/lpmstat.txt
	
	end_time=$(date +%s);
	echo "finished lpm_process spent $(($end_time - $start_time))s, log in $log_path/";
	echo "finished lpm_process spent $(($end_time - $start_time))s, log in $log_path/" >> $log_path/printing.txt
}

#/* v1.34 capture min dump process, include clk/ldo/lpm/wake/dmesg/logcat save to $log_path/clk_ldo_dump.txt*/
function min_dump_process()
{
    j=0
	start_time=$(date +%s);
	rm -rf $log_path/clk_ldo_dump.txt;
	rm -rf $log_path/clk_ldo_lvl_dump.txt;
	rm -rf $log_path/wake_int_dump.txt;
	rm -rf $log_path/lpmstat.txt;
	
	echo "min_dump_process Started ...";
	echo "min_dump_process Started ..." >> $log_path/printing.txt
	
	echo reset > /d/lpm_stats/stats;
		
	dmesg -c > $log_path/temp.txt ;
	rm -rf $log_path/temp.txt ;
	
	echo 1 > /sys/module/msm_show_resume_irq/parameters/debug_mask
	echo 0 >/sys/module/qpnp_rtc/parameters/poweron_alarm
	echo 1 > /sys/kernel/debug/clk/debug_suspend
	echo Y > /sys/module/printk/parameters/ignore_loglevel
	
	while(($j<$1))
	do
	    # clk&ldo dump.
        echo \=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\ clock =\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\= >> $log_path/clk_ldo_dump.txt
        echo cycles $j: `date +%Y/%m/%d-%H:%M:%S` >> $log_path/clk_ldo_dump.txt
		if [[ $product_type == MSM ]]; then
			if [ -e /d/clk/enabled_clocks ];then
				cat /d/clk/enabled_clocks >> $log_path/clk_ldo_dump.txt
			else
				cat /d/clk/clk_enabled_list >> $log_path/clk_ldo_dump.txt
			fi
		elif [[ $product_type == KIRIN ]]; then
			cat /d/clock/clock_tree >> $log_path/clk_ldo_dump.txt
		elif [[ $product_type == MTK ]]; then
			cat /d/clk/enabled_clocks >> $log_path/clk_ldo_dump.txt
		else
			cat /d/clk/enabled_clocks >> $log_path/clk_ldo_dump.txt
		fi
		
		echo cycles $j: `date +%Y/%m/%d-%H:%M:%S` >> $log_path/clk_ldo_lvl_dump.txt
		echo \-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\ clk_lvl -\-\-\-\-\-\-\-\-\-\-\ >> $log_path/clk_ldo_lvl_dump.txt
		cd /sys/kernel/debug/clk;
		for i in *;
		do if [ -d $i ];
			then if [ "$(cat $i/clk_enable_count)" != "0" ];
				then if [ -e $i/clk_rate ] && [ -e $i/clk_rate_max ] && [ "$(cat $i/clk_rate)" != "0" ];
					then echo $i \=\> clk_enable_count:`cat $i/clk_enable_count` rate:`cat $i/clk_rate`;
						 echo clk_rate_max:`cat $i/clk_rate_max`;
					elif [ -e $i/clk_rate ] && [ "$(cat $i/clk_rate)" != "0" ];
					then echo $i \=\> clk_enable_count:`cat $i/clk_enable_count` rate:`cat $i/clk_rate`;
				fi; 
			fi; 
		fi; 
		done >> $log_path/clk_ldo_lvl_dump.txt

        echo \-\-\-\-\-\-\-\-\-\-\-\-\- LDO \-\-\-\-\-\-\-\-\-\-\-\-\-\ >> $log_path/clk_ldo_dump.txt
        cd /sys/class/regulator;
	    for i in *;
	    do if [ -d $i ];
    	   then if [ -e $i/state ];
		     then if [ "$(cat $i/state)" == "enabled" ];
			   then if [ -e $i/microvolts ];
			     then echo $i \=\> name:`cat $i/name` state:`cat $i/state` microvolt:`cat $i/microvolts`;
				 else echo $i \=\> name:`cat $i/name` state:`cat $i/state` microvolt: N\/A; 
				 fi; 
				fi;
			  fi; 
			fi; 
		done >> $log_path/clk_ldo_dump.txt
		
		# wakeup/wakelock/interrupt dump
		echo cycles $j: `date +%Y/%m/%d-%H:%M:%S` >> $log_path/wake_int_dump.txt
		echo \=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\= wakeup_sources \=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\= >> $log_path/wake_int_dump.txt
		cat /sys/kernel/debug/wakeup_sources >> $log_path/wake_int_dump.txt
		echo \-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\- wakelocks \-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\- >> $log_path/wake_int_dump.txt
		cat /sys/power/wake_lock >> $log_path/wake_int_dump.txt
		echo \~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~ interrupts \~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~\~ >> $log_path/wake_int_dump.txt
		cat /proc/interrupts >> $log_path/wake_int_dump.txt
		
		sleep $2;
		j=$(($j+1))
		
		# lpm dump
		echo cycles $j: `date +%Y/%m/%d-%H:%M:%S` >> $log_path/lpmstat.txt
		echo \=\=\=\=\=\=\=\=\=\=\=\=\=\=\= APSS XO status \=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\= >> $log_path/lpmstat.txt
		
		if [ -e /d/rpm_stats ];then
			cat /d/rpm_stats >> $log_path/lpmstat.txt
			cat /d/rpm_master_stats >> $log_path/lpmstat.txt
		else
			cat /sys/power/system_sleep/stats >> $log_path/lpmstat.txt
			cat /sys/power/rpmh_stats/master_stats >> $log_path/lpmstat.txt
		fi 
		
		cat /d/lpm_stats/stats >> $log_path/lpmstat.txt
	done
	
	dmesg -r  > $log_path/unmask_irq_dmesg.txt
	
	echo 0 > /sys/module/msm_show_resume_irq/parameters/debug_mask
	echo 1 >/sys/module/qpnp_rtc/parameters/poweron_alarm
	echo 0 > /sys/kernel/debug/clk/debug_suspend
	echo N > /sys/module/printk/parameters/ignore_loglevel
	
	end_time=$(date +%s);
    echo "Finished min_dump_process spent $(($end_time - $start_time))s, log in $log_path";
	echo "Finished min_dump_process spent $(($end_time - $start_time))s, log in $log_path" >> $log_path/printing.txt
}

#/* capture irq unmask dmesg, save to data/powerall */
function dmesg_process()
{
	start_time=$(date +%s);
	rm -rf $log_path/unmask_irq_dmesg.txt;
	echo "dmesg_process Started ...";
	echo "dmesg_process Started ..." >> $log_path/printing.txt
	
	dmesg -c > $log_path/temp.txt ;
	rm -rf $log_path/temp.txt ;
	
	echo 1 > /sys/module/msm_show_resume_irq/parameters/debug_mask
	echo 0 >/sys/module/qpnp_rtc/parameters/poweron_alarm
	echo 1 > /sys/kernel/debug/clk/debug_suspend
	echo Y > /sys/module/printk/parameters/ignore_loglevel
	
	if [ "$1" =  "" ]; then
		sleep 10;
    else
		sleep $1;
	fi
	
	dmesg -r  > $log_path/unmask_irq_dmesg.txt
	echo 0 > /sys/module/msm_show_resume_irq/parameters/debug_mask
	echo 1 >/sys/module/qpnp_rtc/parameters/poweron_alarm
	echo 0 > /sys/kernel/debug/clk/debug_suspend
	echo N > /sys/module/printk/parameters/ignore_loglevel
	
	end_time=$(date +%s);
	echo "finished dmesg_process spent $(($end_time - $start_time))s, log in $log_path/"
	echo "finished dmesg_process spent $(($end_time - $start_time))s, log in $log_path/" >> $log_path/printing.txt
}

#/* capture camera unmask logcat, save to data/powerall */
function camera_logcat()
{
	start_time=$(date +%s);
	rm -rf $log_path/camera_logcat.txt;
	echo "camera_logcat Started ...";
	echo "camera_logcat Started ..." >> $log_path/printing.txt
	
	setprop persist.camera.sensor.debug 5
	setprop persist.camera.isp.debug 2
	setprop persist.camera.hal.debug 4
	setprop persist.camera.stats.debug.mask 5
	setprop persist.debug.sf.showfps 1
	if [ "$1" =  "" ]; then
		sleep 10;
    else
		sleep $1;
	fi
	logcat -f $log_path/camera_logcat.txt -d
	setprop persist.camera.sensor.debug 0
	setprop persist.camera.isp.debug 0
	setprop persist.camera.hal.debug 0
	setprop persist.camera.stats.debug.mask 0
	setprop persist.debug.sf.showfps 0
	end_time=$(date +%s);
	echo "finished camera_logcat spent $(($end_time - $start_time))s, log in $log_path/"
	echo "finished camera_logcat spent $(($end_time - $start_time))s, log in $log_path/" >> $log_path/printing.txt
}
#/* TCPIP dump, save to data/powerall */
function tcp_process()
{
	start_time=$(date +%s);
	echo "tcp_process Started ...";
	echo "tcp_process Started ..." >> $log_path/printing.txt
    rm -rf $log_path/tcpdump.pcap;
	
	tcpdump -nvs0 -i any -s 0 -w $log_path/tcpdump.pcap &
	#/*kill the above thread after 4s*/
	latest=$!; 
	echo $latest;
	#/*sleep arg1 s then kill the thread*/
	if [ "$1" =  "" ]; then
		sleep 10;
    else
		sleep $1;
	fi 
	
	kill -9 $latest
	end_time=$(date +%s);
	echo "finished tcp_process spent $(($end_time - $start_time))s, log in $log_path/"
	echo "finished tcp_process spent $(($end_time - $start_time))s, log in $log_path/" >> $log_path/printing.txt
}

#/* Tracing dump, save to data/powerall */
function tracing_process()
{
	j=0
	start_time=$(date +%s);
	echo "tracing_process Started ...";
	echo "tracing_process Started ..." >> $log_path/printing.txt
	
	rm -rf $log_path/ftrace.txt
	
	type=`getprop ro.board.platform`
	
	cd /sys/kernel/debug/tracing
	echo 0 > tracing_on
	
	if [ -e options/overwrite ];then
		echo 0 > options/overwrite
	fi
	
	if [ -e options/record-tgid ];then
		echo 1 > options/record-tgid
	fi
	
	if [ -e options/print-tgid ];then
		echo 1 > options/print-tgid
	fi
	
	if [ "$1" =  "" ]; then
	 sleep_dur=10
	else
	 sleep_dur=$1
	fi
  
	if [ "$(cat /d/tracing/buffer_size_kb)" -lt "120000" ]; then
		for i in 10000 20000 30000 40000 50000 60000 70000 80000 90000 100000 110000 120000; 
		do while true
			do  
				echo $i > /d/tracing/buffer_size_kb
				if [ "$(cat /d/tracing/buffer_size_kb)" -lt "$i" ]; then
					echo $i > /d/tracing/buffer_size_kb
				else
					echo $i
					j=0
					break
				fi
				
				j=$(($j+1))	
				if [ $j -eq "10" ]; then
					echo "write Ftrace buffer error $j"
					echo "write Ftrace buffer error $j" >> $log_path/printing.txt
					j=0
					break
				fi
			done;
		done;
	fi
	

	echo "" > set_event
	echo "" > trace
	sync
	
	if [ "$2" =  "" ]; then
		echo power:cpu_idle power:cpu_frequency power:cpu_frequency_switch_start msm_bus:bus_update_request msm_low_power:* >> set_event
		if [ -d events/power/clock_set_rate ]; then
			echo power:clock_set_rate power:clock_enable power:clock_disable  >> set_event
		fi
		
		if [ -d events/cpufreq_interactive ]; then
			echo cpufreq_interactive:cpufreq_interactive_target cpufreq_interactive:cpufreq_interactive_setspeed >> set_event
		else
			echo power:sugov_next_freq power:sugov_util_update >> set_event
		fi
		
		echo power:wakeup_source_activate power:wakeup_source_deactivate >> set_event
		echo irq:* >> set_event
		#echo mdss:mdp_mixer_update mdss:mdp_sspp_change mdss:mdp_commit >> set_event
		echo workqueue:workqueue_execute_end workqueue:workqueue_execute_start workqueue:workqueue_activate_work workqueue:workqueue_queue_work >> set_event
		echo regulator:regulator_set_voltage_complete regulator:regulator_disable_complete regulator:regulator_enable_complete >> set_event
		echo kgsl:kgsl_pwrlevel kgsl:kgsl_buslevel kgsl:kgsl_pwr_set_state >> set_event
		#echo kgsl:kgsl_pwrlevel kgsl:kgsl_buslevel kgsl:kgsl_pwr_set_state >> set_event
		echo power:bw_hwmon_meas power:bw_hwmon_update power:memlat_dev_meas power:memlat_dev_update >> set_event
		#echo sched:* >> set_event
		echo sched:sched_switch sched:sched_wakeup sched:sched_wakeup_new sched:sched_enq_deq_task sched:sched_update_task_ravg sched:sched_cpu_util >> set_event
		echo clk:clk_set_rate clk:clk_enable clk:clk_disable >> set_event
		echo ipa:* >> set_event
		echo cpuhp:* >> set_event
	elif [[ "$2" -eq 1 ]]; then 
		echo 1 >  /sys/kernel/debug/perf_debug_tp/enabled
		echo perf_trace_counters:sched_switch_with_ctrs >> set_event
		echo sde:sde_perf_crtc_update >> set_event
		echo power:cpu_idle power:cpu_frequency power:cpu_frequency_switch_start msm_low_power:* >> set_event
		if [ -d events/power/clock_set_rate ]; then
			echo power:clock_set_rate power:clock_enable power:clock_disable  >> set_event
		fi
		echo sched:sched_switch sched:sched_wakeup sched:sched_wakeup_new sched:sched_enq_deq_task sched:sched_update_task_ravg sched:sched_cpu_util >> set_event
		if [ -d events/cpufreq_interactive ]; then
			echo cpufreq_interactive:cpufreq_interactive_target cpufreq_interactive:cpufreq_interactive_setspeed >> set_event
		else
			echo power:sugov_next_freq power:sugov_util_update >> set_event
		fi
		echo msm_bus:bus_update_request >> set_event
		echo power:bw_hwmon_meas power:bw_hwmon_update power:memlat_dev_meas power:memlat_dev_update >> set_event
		echo clk:clk_set_rate clk:clk_enable clk:clk_disable >> set_event
		#echo irq:* >> set_event
		#echo migrate:* >> set_event
		#echo cpuhp:* >> set_event
		#echo kgsl:kgsl_pwr_set_state kgsl:kgsl_pwrstats kgsl:kgsl_gpubusy kgsl:kgsl_buslevel kgsl:kgsl_powerlevel kgsl:kgsl_clk kgsl:kgsl_rail >> set_event
		echo kgsl:kgsl_pwrlevel kgsl:kgsl_buslevel kgsl:kgsl_pwr_set_state kgsl:kgsl_clk >> set_event
	elif [[ "$2" -eq 2 ]]; then
		echo power:wakeup_source_activate power:wakeup_source_deactivate >> set_event
		echo msm_low_power:* >> set_event
		echo irq:* >> set_event
		echo cpuhp:* >> set_event
		echo dfc:* >> set_event
		echo wda:* >> set_event
		if [ -d events/alarmtimer ]; then
			echo alarmtimer:* >> set_event
		fi
	else
		echo 1 >  /sys/kernel/debug/perf_debug_tp/enabled
		echo perf_trace_counters:sched_switch_with_ctrs >> set_event
		echo sde:sde_perf_crtc_update >> set_event
		#echo power:cpu_idle power:cpu_frequency power:cpu_frequency_switch_start msm_low_power:* >> set_event
		echo msm_bus:bus_update_request >> set_event
		echo power:bw_hwmon_meas power:bw_hwmon_update power:memlat_dev_meas power:memlat_dev_update >> set_event
		echo clk:clk_set_rate clk:clk_enable clk:clk_disable >> set_event
		echo kgsl:kgsl_pwrlevel kgsl:kgsl_buslevel kgsl:kgsl_pwr_set_state >> set_event
		echo camera:* >> set_event
	fi

	echo 0 > tracing_on && echo "" > trace && sleep 2 && echo 1 > tracing_on && echo 1 > /d/tracing/events/clk/clk_state/enable && cat /d/clk/trace_clocks && echo 1 > /d/tracing/events/msm_bus/bus_client_status/enable && cat /d/msm-bus-dbg/client-data/dump_clients && sleep $sleep_dur && echo 0 > tracing_on && cat trace > $log_path/ftrace.txt
	
	cd /
	
	if [ -e options/overwrite ];then	
		echo 1 > options/overwrite
	fi
	
	if [ -e options/record-tgid ];then
		echo 0 > options/record-tgid
	fi
	
	if [ -e options/print-tgid ];then
		echo 0 > options/print-tgid
	fi

	
	end_time=$(date +%s);
	echo "finished tracing_process spent $(($end_time - $start_time))s, log in $log_path/"
	echo "finished tracing_process spent $(($end_time - $start_time))s, log in $log_path/" >> $log_path/printing.txt
}

#/* Thermal dump, save to data/powerall */
function idlestat_process()
{
  start_time=$(date +%s);
  rm -rf $log_path/idlestat.csv
  
  #/* Thermal tsens data */
  echo "idlestat Started ...";
  echo "idlestat Started ..." >> $log_path/printing.txt
  #cat /sys/class/thermal/*/type >> $log_path/thermal_stat.txt
  #cat /sys/class/thermal/*/temp >> $log_path/thermal_stat.txt
  
  if [ "$1" =  "" ]; then
	 idle_dur=10
  else
	 idle_dur=$1
  fi
  echo $load_dur $load_sam
  cd /data/local/tmp
  ./idlestat --trace -c -p -w -C -f idles -t $idle_dur > $log_path/idlestat.csv &
  cd /
  
  #/*sleep arg1 s then kill the thread*/
  sleep $idle_dur
  
  end_time=$(date +%s);
  echo "finished idlestat spent $(($end_time - $start_time))s, log in $log_path/"
  echo "finished idlestat spent $(($end_time - $start_time))s, log in $log_path/" >> $log_path/printing.txt
}
#/* cpu/gpu/bmic frequency and load data dump, thermal data also dump */
function CPU_load_process()
{
  #sleep $delay_time;
  start_time=$(date +%s);
  rm -rf $log_path/cpu_logger.csv
  
  #/* Thermal tsens data */
  echo "CPU_load_process Started ...";
  echo "CPU_load_process Started ..." >> $log_path/printing.txt
  #cat /sys/class/thermal/*/type >> $log_path/thermal_stat.txt
  #cat /sys/class/thermal/*/temp >> $log_path/thermal_stat.txt
  
  if [ "$1" =  "" ]; then
	 load_dur=30
  else
	 load_dur=$1
	 if [ "$2" =  "" ]; then
		load_sam=1000
	 else
	    load_sam=$2
	 fi
  fi
  echo $load_dur $load_sam
  
  cd /data/local/tmp
  ./cpustatus -o $log_path/cpu_logger.csv -d $load_dur &
  cd /
  
  sleep $load_dur
  
  end_time=$(date +%s);
  echo "finished CPU_load_process spent $(($end_time - $start_time))s, log in $log_path/"
  echo "finished CPU_load_process spent $(($end_time - $start_time))s, log in $log_path/" >> $log_path/printing.txt
}

function rpm_status()
{
    j=0
	start_time=$(date +%s);
	echo "RPM Status Started ...";
	rm -rf $log_path/rpm_status.txt
	
	echo "RPM Status Started ..." >> $log_path/printing.txt
	while (($j<$1))
	do  
		echo cycles $j: `date +%Y/%m/%d-%H:%M:%S` >> $log_path/rpm_status.txt
		if [ -e /d/rpm_stats ];then
			cat /d/rpm_stats >> $log_path/rpm_status.txt
		else
			cat /sys/power/system_sleep/stats >> $log_path/rpm_status.txt
		fi	
		j=$(($j+1))
		sleep $2
	done;
	
	end_time=$(date +%s);
	echo "finished RPM Status spent $(($end_time - $start_time))s, log in $log_path";
	echo "finished RPM Status spent $(($end_time - $start_time))s, log in $log_path" >> $log_path/printing.txt
}

function systrace_process()
{
	start_time=$(date +%s);
	echo "systrace Started ...";
	rm -rf $log_path/systrace.atrace
	
	echo "systrace Started ..." >> $log_path/printing.txt
    
	if [ "$1" =  "" ]; then
		sleep_t=10
	else
		sleep_t=$1
	fi
	
	atrace --async_start -t $sleep_t -b 10000 gfx input view hal res dalvik sched freq idle mmc disk workq
	sleep $sleep_t
	atrace --async_stop -z -o $log_path/systrace.atrace
	
	end_time=$(date +%s);
	echo "finished systrace spent $(($end_time - $start_time))s, log in $log_path";
	echo "finished systrace spent $(($end_time - $start_time))s, log in $log_path" >> $log_path/printing.txt
}

function all_process()
{
    echo "Needs 120s";
	echo "Start after $delay_time s , you can remove USB";
	sleep $delay_time;
    basic_process;
	top_process 5;
	min_dump_process 5 1;
	if [[ $product_type == MSM ]]; then
		tracing_process 10;
		idlestat_process 10;
	fi
	tcp_process 10;
	
	CPU_load_process 30;

    echo "finished dump all";
}

function quick_all_process()
{
    echo "Needs 30s";
	echo "Start after $delay_time s , you can remove USB";
	sleep $delay_time;
	
	basic_process 1;
	top_process 2;
	min_dump_process 2 1;
	if [[ $product_type == MSM ]]; then
		tracing_process 5;
		idlestat_process 5;
	fi
	
	CPU_load_process 30;
    
    echo "finished quick dump all";
}

function camera_process()
{
	echo "Start after $delay_time s , you can remove USB";
	sleep $delay_time;
	
	min_dump_process 2 1;
	if [[ $product_type == MSM ]]; then
		tracing_process 5 3;
		camera_logcat 5;
	fi
	dumpsys SurfaceFlinger > $log_path/SurfaceFlinger.txt
	
	if [ "$1" =  "" ]; then
		sleep_t=30
	else
		sleep_t=$1
	fi
	
	CPU_load_process $sleep_t;
    
    echo "finished camera dump";
}

function game_process()
{
	echo "Start after $delay_time s , you can remove USB";
	sleep $delay_time;
	
	if [ "$1" =  "" ]; then
		sleep_t=60
	else
		sleep_t=$1
	fi
	
	CPU_load_process $sleep_t;
	
	dumpsys SurfaceFlinger > $log_path/SurfaceFlinger.txt
	logcat -v time -b all > $log_path/logcat_dump.txt -d 
	
	if [[ $product_type == MSM ]]; then
		tracing_process 5 1;
	fi
	
	systrace_process 10;
	
    echo "finished game dump";
}

#/*main process*/
cd /
rm -rf $log_path

if [ ! -d "$log_path" ]; then
mkdir "$log_path"
fi

android_ver=`getprop ro.build.version.release`
android_ver=${android_ver:0:1}
type=`getprop ro.board.platform`

if [[ $type == hi* ]]; then
	product_type=KIRIN
elif [[ $type == mt* ]]; then
	product_type=MTK
else
	product_type=MSM
fi

if [ $1 = "-s" ]; then
	if [ "$2" =  "" ]; then
		 all_process &
	else

		if [ $# -lt 13 ]; then
			echo parameter $# < 13	
			exit $? 
		fi
		
		echo "Start after $delay_time s , you can remove USB";
		sleep $delay_time;
	
		if [ -n "$2" ] && [ "$2" -gt 0 ]; then
			basic_process $2
		fi
		
		if [ -n "$3" ] && [ "$3" -gt 0 ]; then
			top_process $3
		fi
		
		if [ -n "$4" ] && [ "$4" -gt 0 ]; then
			clk_ldo_process $4 1
		fi
		
		if [ -n "$5" ] && [ "$5" -gt 0 ]; then
			wake_process $5 1
		fi
		
		if [ -n "$6" ] && [ "$6" -gt 0 ]; then
			lpm_process $6 1
		fi
		
		if [ -n "$7" ] && [ "$7" -gt 0 ]; then
			idlestat_process $7
		fi
		
		if [ -n "$8" ] && [ "$8" -gt 0 ]; then
			dmesg_process $8
		fi
		
		if [ -n "$9" ] && [ "$9" -gt 0 ]; then
			systrace_process $9
		fi
		
		if [ -n "${10}" ] && [ "${10}" -gt 0 ]; then
			tcp_process ${10}
		fi
		
		if [ -n "${11}" ] && [ "${11}" -gt 0 ]; then
			tracing_process ${11}
		fi
		
		if [ -n "${12}" ] && [ "${12}" -gt 0 ]; then
			tracing_process ${12} 1
		fi
		
		if [ -n "${13}" ] && [ "${13}" -gt 0 ]; then
			CPU_load_process ${13} 1
		fi
		
		echo "finished dump special all";
	fi
	exit 1;
fi


	
echo "#######################################################";
echo "#               QUALCOMM POWERALL v1.63               #";
echo "#               power logging console                 #";
echo "#                                                     #";
echo "#    please report issues to powerall.hotline         #";
echo "#######################################################";
echo "";
echo "0. Basic information dump"
echo "1. Top and powertop dump";
echo "2. Clock and LDO dump";
echo "3. Wakelock,interrupt,wakeup_sources dump";
echo "4. Lpm state, c-state and XO,Vddmin dump";
echo "5. CPU idlestat dump";
echo "6. irq unmask dmesg";
echo "7. systrace dump";
echo "8. TCPIP dump";
echo "9. Normal Ftrace dump";
echo "10. GPU Ftrace dump";
echo "11. CPU load dump";
echo "12. Game log dump";
echo "13. Camera power dump";
echo "14. Sleep Ftrace dump";
echo "a. Dump all";
echo "b. Quick Dump all";
echo "q. Quit";
echo "please enter a number :";	

if [ "$1" =  "" ]; then
	read -r number
else
    #echo "number import";
	number=$1;
	delay_time=$2;
	if [ -n "$3" ]; then
		cycles=$3;
	fi
	
	if [ -n "$4" ]; then
		inter_time=$4;
	fi
	#echo "parameter import $number, $delay_time, $cycles, $inter_time.";
fi

case $number in

0)
	echo "Need $(30))s";
	echo "Start after $delay_time s , you can remove USB";
	sleep $delay_time;
	basic_process &
	;;
1)	
	if [ "$cycles" =  "" ]; then
		echo "input cycles :";
		read -r cycles
	fi
	echo "Need $$((6*cycles+3))s";
	echo "Start after $delay_time s , you can remove USB";
	sleep $delay_time;
	top_process $cycles &
	;;
2)
	if [ "$cycles" =  "" ]; then
		echo "input cycles :";	
		read -r cycles
	fi
	
	if [ "$inter_time" =  "" ]; then
		echo "input interval time(S) :";
		read -r inter_time
	fi
	echo "Need $cycles";
	echo "Start after $delay_time s , you can remove USB";
	sleep $delay_time
	clk_ldo_process $cycles $inter_time &
	;;
3)
	if [ "$cycles" =  "" ]; then
		echo "input cycles :";	
		read -r cycles
	fi
	
	if [ "$inter_time" =  "" ]; then
		echo "input interval time(S) :";
		read -r inter_time
	fi
	echo "Need $cycles";
	echo "Start after $delay_time s , you can remove USB";
	sleep $delay_time;
    wake_process $cycles $inter_time &
	;;
4)
	if [ "$cycles" =  "" ]; then
		echo "input cycles :";	
		read -r cycles
	fi
	
	if [ "$inter_time" =  "" ]; then
		echo "input interval time(S) :";
		read -r inter_time
	fi
	echo "Need $cycles";
	echo "Start after $delay_time s , you can remove USB";
	sleep $delay_time;
    lpm_process $cycles $inter_time &
	;;
5)
	if [ "$cycles" =  "" ]; then
		echo "input cycles :";
		read -r cycles
	fi

	echo "Start after $delay_time s, you can remove USB";
	idlestat_process $cycles &
	;;
6)
	if [ "$cycles" =  "" ]; then
		echo "input cycles :";	
		read -r cycles 
	fi
	echo "Need $cycles";
	echo "Start after $delay_time s, you can remove USB";
	sleep $delay_time;
    dmesg_process $cycles &
	;;
7)
	if [ "$cycles" =  "" ]; then
		echo "input cycles :";	
		read -r cycles 
	fi
	echo "Need $cycles";
	echo "Start after $delay_time s, you can remove USB";
	sleep $delay_time;
	systrace_process $cycles &
	;;
8)
	if [ "$cycles" =  "" ]; then
		echo "input cycles :";	
		read -r cycles
	fi
	echo "Need $cycles";
	echo "Start after $delay_time s, you can remove USB";
	sleep $delay_time;
    tcp_process $cycles &
	;;
9)
	if [ "$cycles" =  "" ]; then
		echo "input cycles :";	
		read -r cycles
	fi
	echo "Need $cycles";
	echo "Start after $delay_time s, you can remove USB";
	sleep $delay_time
	tracing_process $cycles &
	;;
10)
	if [ "$cycles" =  "" ]; then
		echo "input cycles :";	
		read -r cycles
	fi
	echo "Need $cycles";
	echo "Start after $delay_time s, you can remove USB";
	sleep $delay_time;
	tracing_process $cycles 1 &
	;;
11)
	if [ "$cycles" =  "" ]; then
		echo "input cycles :";
		read -r cycles
	fi
	if [ "$inter_time" =  "" ]; then
		echo "input interval time(ms) :";
		read -r inter_time
	fi
	echo "Need $cycles";
	echo "Start after $delay_time s, you can remove USB";
	sleep $delay_time;
	
	CPU_load_process $cycles $inter_time &
	;;
12)
	if [ "$cycles" =  "" ]; then
		echo "input cycles :";	
		read -r cycles
	fi
	echo "Need $cycles";
	game_process $cycles &
	;;
13)
	if [ "$cycles" =  "" ]; then
		echo "input cycles :";	
		read -r cycles
	fi
	echo "Need $cycles";
	camera_process $cycles &
	;;		
14)
	if [ "$cycles" =  "" ]; then
		echo "input cycles :";	
		read -r cycles
	fi
	echo "Need $cycles";
	echo "Start after $delay_time s, you can remove USB";
	sleep $delay_time;
	tracing_process $cycles 2 &
	;;
a)
	echo "dump all";
    all_process &
	;;
b)
	echo "quick dump all";
    quick_all_process &
	;;
q)
	echo "q or invalid, exiting..."
	;;
esac




