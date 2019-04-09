cpustatus v0.1
========

CPU, Thermal Zones and KPI node logger for MSMs, MTK, Kirin

ctlogger is an upgrade to the perf_logging binary that has been used for years for thermal and performance debug. ctlogger incorporates many features like:
- auto detection of number of CPUs
- auto detection of number of nodes in thermal zone
- config file which allows to add more KPI nodes to log
- specify output file
- long duration logging
- easy launch
- proper csv formatting
- no need to recompile for new targets to add unaccounted nodes
- works great on customer devices with any QC target

```sh
usage: /data/ctlogger [OPTIONS]
        [OPTIONAL] -c, --config <logger config file path> default is /data/ctlogger.conf
        [OPTIONAL] -o, --out <output file path> default is /data/tsens_logger.csv
        [OPTIONAL] -d, --duration <total duration in minutes> default is 24*60
		[OPTIONAL] -s, --sampling <sampling time in ms>   default is 1000ms
		[OPTIONAL] -t, --disable thermal and cooling capture
		[OPTIONAL] -f, --input surface name at manual
        [OPTIONAL] -h, --help    prints usage
```        

config file example (see the ctlogger.conf)
```sh
PA_THERM0:/sys/bus/spmi/devices/qpnp-vadc-ee0023c0/pa_therm0
BATT_THERM:/sys/bus/spmi/devices/qpnp-vadc-ee0023c0/batt_therm
CPU 0 MAX FREQ:/sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq
CPU 1 MAX FREQ:/sys/devices/system/cpu/cpu4/cpufreq/scaling_max_freq
```
