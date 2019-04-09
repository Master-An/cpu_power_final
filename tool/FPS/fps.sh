
#############################
#
#
#
#
##############################
echo FPS measure every ~1 second > /data/fps.txt

start_time=$(date +%Y-%m-%d%t%X)
echo FPS Start Time: $start_time >> /data/fps.txt

#initial 
t_start=${EPOCHREALTIME%.*}${EPOCHREALTIME#*.}
flip_str=`dumpsys SurfaceFlinger | grep flips`
flip_start=${flip_str#*flips=}
flip_start=${flip_start%, isS*}
# run 
while((0<1))
	do
	usleep 950000
	flip_str=`dumpsys SurfaceFlinger | grep flips`
	t_end=${EPOCHREALTIME%.*}${EPOCHREALTIME#*.}
	flip_str=${flip_str#*flips=}
    flip_cur=${flip_str%, isS*}
	frame=$(($flip_cur-$flip_start))
	flip_start=$flip_cur
	time_duration=$(($t_end-$t_start))
	t_start=$t_end
	fps=$((1000000*$frame/$time_duration))
	#echo "Elapsed_time="$time_duration, "Filps=" $frame, "FPS="$fps
	echo Elapsed Time:  $time_duration ms  FPS:  $fps >> /data/fps.txt
	done

	