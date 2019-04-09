# coding=utf-8
from __future__ import division
from conf.testSuiteConfig import TestSuiteConfig
from conf.testCaseConfig import TestCaseConfig
from core.ptasLogger import logger
from core.status import StatusResult
from core.command import CommandLine
from lib.adbSettings import AdbSettings
from lib.adb import Adb
from lib.excelHandle import ExcelHandle
from lib.testCasePowerMetrics import TestCasePowerMetrics
from hardware_handler.qcusbswitch import QcUsbSwitch
from core.commonApplicationUtilities import CommonApplicationUtilities

from lib.qrd_setting import QRDSetting
from lib.ptt_power_tool_kratoslite import PTTKratoslite
from lib.ptt_power_tool_power_monitor import PTTPowerMonitor
from lib.ptt_power_tool_kratos import  PTTKratos
from lib.ptt_log_cpupower import PTT_LOG_CPUPower
from lib.qrd_cpu_setting import QRDCpuSetting
from lib.powermonitor_parser import PowerMonitorParser
from collections import Counter
from decimal import *

import os
import re
import csv

"""

CPU dhrystone power testing class

"""

class Dhry_Test_Para(object):
    """参数配置"""

    def __init__(self, CPU_power_f, CPU_perf_f, CPU_super_f, CPU_coremask, Dhry_loop, Dhry_thread, Dhry_delay, log_ctlog_time, log_power_time, flag):
        self.CPU_power_f = CPU_power_f
        self.CPU_perf_f = CPU_perf_f
        self.CPU_super_f = CPU_super_f
        self.CPU_coremask = CPU_coremask
        """case_name & TestCaseFolder"""
        self.work_path = os.getcwd()
        self.case_name = self.CPU_coremask + '_' + self.CPU_power_f + '_' + self.CPU_perf_f + '_' + self.CPU_super_f
        self.TestCaseFolder = os.path.join(TestSuiteConfig.ReportsPath, self.case_name)
        self.Dhry_loop = Dhry_loop
        self.Dhry_thread = Dhry_thread
        self.Dhry_delay = Dhry_delay
        self.log_ctlog_time = log_ctlog_time
        self.log_power_time = log_power_time
        self.flag = flag


        # # 各种类型核的个数
        # self.cpu_power_number = cpu_power_number
        # self.cpu_perf_number = cpu_perf_number
        # self.cpu_new_number = cpu_new_number

class CPUPOWER_QRD_KRATO_DB(QRDCpuSetting, PTT_LOG_CPUPower):
    """ Chind of QRD_CPU_SETTING + PTT_POWER_TOOL_KRATO
    
    CPU frequency sweeping test
    
    QRD_CPU setting + Krato + powerall, Dhry
    
    """
    Interation = 1
    
    def __init__(self):
        super(CPUPOWER_QRD_KRATO_DB, self).__init__()
        self.PowerHandler = None
        """get core , frequency information"""

    def cpu_power_path_search(self, search_name):
        for dirpath, dir_name, filenames in os.walk(os.getcwd()):
            # if dirpath.endswith(r'\QcUSBSwitchTool'):
            if dirpath.endswith(search_name):
                return dirpath
            
    def InitEnvironmnet(self):
        if 'KratosLite' in TestSuiteConfig.HardwareType:
            try:
                #self.PowerHandler = KratosLite()
                self.PowerHandler = PTTKratoslite()
                
                result = self.PowerHandler.SetConfigurationFile(TestSuiteConfig.ChannelConfiguration)
#                 if result.HasError():
#                     return result        
                result = self.PowerHandler.PowerOn()
                result = self.PowerHandler.UsbOn()
                result = Adb.IsDeviceDetected()
                if result.HasError():
                    logger.info("set usb on again")
                    QcUsbSwitch.SetUsbConnection('usb_on')
                    result = Adb.IsDeviceDetected()
                    logger.info("second time: " + str(result.IsSuccess()))
                else:
                    logger.info("first time: " + str(result.IsSuccess()))
                result = Adb.SetAdbRoot()
                if result.HasError():
                    return result
                result = Adb.SetAdbRemount()
                if result.HasError():
                    return result

            except Exception as e:
                return StatusResult.Error('Failed to initialize KRATOSLITE: ', str(e))
        elif 'Kratos' in TestSuiteConfig.HardwareType:
            logger.info("----------supply with Kratos--------------")
            try:
                #self.PowerHandler = Kratos()
                self.PowerHandler = PTTKratos()
                result = self.PowerHandler.SetConfigurationFile(TestSuiteConfig.ChannelConfiguration)
#                 if result.HasError():
#                     return result        
                result = self.PowerHandler.PowerOn()
                result = self.PowerHandler.UsbOn()
            except Exception as e:
                logger.info(str(e))
                return StatusResult.Error('Failed to initialize KRATOS: ', str(e))
        elif 'Monitor' in TestSuiteConfig.HardwareType:
            try:
                self.PowerHandler = PTTPowerMonitor()
            except Exception as e:
                logger.info(str(e))
                return StatusResult.Error('Failed to initialize PowerMonitor: ', str(e))
        else:
            logger.error("Can't support hardware type, please check TestSuiteConfig.HardwareType")
            return
        logger.info(TestSuiteConfig.HardwareType + " : initialization successful.")  
        logger.info("Waiting for device ...")
        result = Adb.WaitForDevice(30)
        logger.info("wait for device ready...")
        result = AdbSettings.ReMountDevice()
        if result.HasError():
            logger.error("Unable to set root & remount privileges")
        self.Wakelock()  
        self.Discharging()
        logger.info("Disable charging & Enable wakelock")
    
    def GetDeviceCPUFreqList(self):
        self.core_status = self.get_core_status()
        self.power_core_avail_freq, self.perf_core_avail_freq, self.super_core_avail_freq = self.get_available_freq()
        
        logger.info("-------------------------------Basic checking-----------------------------------")
        # logger.info("Build info: %s", str(self.device_info()))
        logger.info("Online core : %s ", str(self.core_status))
        logger.info("Available power frequency : %s", str(self.power_core_avail_freq))
        logger.info("Available perf frequency : %s ", str(self.perf_core_avail_freq))
        logger.info("Available new frequency : %s ", str(self.super_core_avail_freq))
        logger.info("--------------------------------------------------------------------------------")

    
    
    def SingleCycleTest(self, para):
        """
        TODO
        :return: 
        """
        if para.CPU_power_f not in self.power_core_avail_freq or para.CPU_perf_f not in self.perf_core_avail_freq or para.CPU_super_f not in self.super_core_avail_freq:
            logger.info ("ERROR Frequency, please give new one:", para.CPU_power_f, para.CPU_perf_f, para.CPU_super_f,
                   para.CPU_coremask)
            exit()
        self.set_frequency_all(para.CPU_power_f, para.CPU_super_f, para.CPU_perf_f, para.CPU_coremask)
        self.set_core(para.CPU_coremask)
        if self.get_core_status() is not para.CPU_coremask:
            logger.info("setting online : "  + self.get_core_status() + "To : " + para.CPU_coremask)
        
        
        self.remove_log()
        self.run_log(para.log_ctlog_time)
        self.run_dhry(para.Dhry_loop,para.Dhry_thread,para.Dhry_delay,para)

        TestLogFolder = os.path.join(TestSuiteConfig.ReportsPath, "Interation" + str(para.flag))
        logger.info("Create test log folder %s" % TestLogFolder)
        if not os.path.exists(TestLogFolder):
            os.mkdir(TestLogFolder)

        para.TestCaseFolder = os.path.join(TestSuiteConfig.ReportsPath, "Interation" + str(para.flag), para.case_name)
        logger.info("Create test report folder %s" % para.TestCaseFolder)
        if not os.path.exists(para.TestCaseFolder):
            os.mkdir(para.TestCaseFolder)
        self.PowerHandler.start_measure(TestCaseConfig.MeasurementDuration, para.case_name, para.TestCaseFolder)
        self.collect_log(para.TestCaseFolder)
        self.target_dir = self.collect_log(para.TestCaseFolder)
        self.remove_log()
        
        
    def target_case_test(self, para):
        logger.info("-----------------Start %d st interation for dhrystone testing, current freq is %s------------------------" % (self.Interation, para.case_name))
        Maxretry = 3
        while(Maxretry):
            self.SingleCycleTest(para)
            if TestSuiteConfig.KratosErrorHandler == True:
                logger.warning("There is exception about kratos handler, will re-test this case!")
                logger.info("Current retry time is %d" % (4 - Maxretry))
                self.InitEnvironmnet()
                TestSuiteConfig.KratosErrorHandler = False
                Maxretry = Maxretry - 1
                continue
            else:
                break
        logger.info("-----------------End %d st interation for dhrystone testing, current freq is %s------------------------"  % (self.Interation, para.case_name))
        self.Interation = self.Interation + 1
        
    def target_case_test_all(self):
        self.InitEnvironmnet()
        self.GetDeviceCPUFreqList()
        logger.info(self.get_available_freq())
        logger.info("Create test report folder %s" % TestSuiteConfig.ReportsPath)
        # Test Case : Power core sweep , perf core offline
        # sweep_power_f = self.power_core_avail_freq[0]
        # sweep_perf_f = self.perf_core_avail_freq[0]

        """Excle Operation"""
        if not os.path.exists(os.path.join(TestSuiteConfig.ReportsPath, "CPUTestSummary.xls")):
            excelHandle = ExcelHandle(os.path.join(TestSuiteConfig.ReportsPath, "CPUTestSummary.xls"))
            excelHandle.GetSheetHandle("CPUTest")
            titleInfo = ["Test Case", "Average Current(mA)", "Average Voltage(V)", "Dhry Loop", "Dhry time", "Dhry thread", "Perf(DMIP)", "Thermal"]
            excelHandle.WriteRow(*titleInfo, beginColumn=0, style="head")
            excelHandle.SaveFile()
            excelHandle = None
        for loop in range(TestCaseConfig.Interation):
            logger.info('1st Loop is: ' + str(loop))

            """Test Case Settings"""
            """不同类型的核，频率设置"""
            sweep_power_f = self.power_core_avail_freq[-1]
            if self.perf_core_avail_freq == 'None':
                sweep_perf_f = 'None'
            else:
                sweep_perf_f = self.perf_core_avail_freq[-1]
            if self.super_core_avail_freq == 'None':
                sweep_super_f = 'None'
            else:
                sweep_super_f = self.super_core_avail_freq[-1]

            """thread number"""
            for sweep_core_online in TestCaseConfig.CoreOnline:
                logger.info('2nd Loop is: ' + str(loop))
                number = Counter(sweep_core_online)
                if number['1'] == 2:
                    logger.info(sweep_core_online)
                    thread_number = 2
                else:
                    thread_number = 1

                """sweep super core"""
                if self.super_core_avail_freq != 'None' and (sweep_core_online == '00000001' or sweep_core_online == '00001001'):
                    if sweep_core_online == '00001001':
                        sweep_perf_f = self.perf_core_avail_freq[0]
                    logger.info("Now test for super core")
                    Dhry_loop = 120
                    for sweep_super_f in self.super_core_avail_freq:
                        logger.info('3rd Loop is: ' + str(loop))
                        Dhry_loop = Dhry_loop + 2
                        para = Dhry_Test_Para(CPU_power_f=sweep_power_f, CPU_perf_f=sweep_perf_f, \
                                              CPU_coremask=sweep_core_online, Dhry_loop=Dhry_loop, \
                                              Dhry_delay=20, Dhry_thread=thread_number, log_ctlog_time=60, \
                                              log_power_time=60, CPU_super_f=sweep_super_f, flag = loop)
                        self.target_case_test(para)
                        self.WriteExcel(para, "apc1-max-step")
                elif self.super_core_avail_freq == 'None' and self.perf_core_avail_freq == 'None':
                    logger.info('test for only power core')
                    logger.info("Now online core is: " + str(sweep_core_online))
                    for index, item in enumerate(sweep_core_online):
                        Dhry_loop = 40
                        for sweep_power_f in self.power_core_avail_freq:
                            logger.info("power frequency for test: " + str(sweep_power_f))
                            Dhry_loop = Dhry_loop + 2
                            para = Dhry_Test_Para(CPU_power_f=sweep_power_f, CPU_perf_f=sweep_perf_f, \
                                                  CPU_coremask=sweep_core_online, Dhry_loop=Dhry_loop, \
                                                  Dhry_delay=20, Dhry_thread=thread_number, log_ctlog_time=60, \
                                                  log_power_time=60, CPU_super_f=sweep_super_f, flag=loop)
                            self.target_case_test(para)
                            self.WriteExcel(para, "cpuss0-max-step")
                        break
                else:
                    logger.info("Now online core is: " +str(sweep_core_online))
                    for index, item in enumerate(sweep_core_online):
                        if item != '0':
                            if index >= self.cpu_number_list[0]:
                                """sweep huge core"""
                                logger.info('Now test for huge core')
                                Dhry_loop = 80
                                for sweep_perf_f in self.perf_core_avail_freq:
                                    Dhry_loop = Dhry_loop + 2
                                    para = Dhry_Test_Para(CPU_power_f=sweep_power_f, CPU_perf_f=sweep_perf_f, \
                                                          CPU_coremask=sweep_core_online, Dhry_loop=Dhry_loop, \
                                                          Dhry_delay=20, Dhry_thread=thread_number, log_ctlog_time=60, \
                                                          log_power_time=60, CPU_super_f=sweep_super_f, flag = loop)
                                    self.target_case_test(para)
                                    self.WriteExcel(para, "apc1-max-step")
                                break
                            else:
                                """sweep small core"""
                                logger.info('Now test for small core')
                                Dhry_loop = 40
                                for sweep_power_f in self.power_core_avail_freq:
                                    logger.info("power frequency for test: " + str(sweep_power_f))
                                    Dhry_loop = Dhry_loop + 2
                                    para = Dhry_Test_Para(CPU_power_f=sweep_power_f, CPU_perf_f=sweep_perf_f, \
                                                          CPU_coremask=sweep_core_online, Dhry_loop=Dhry_loop, \
                                                          Dhry_delay=20, Dhry_thread=thread_number, log_ctlog_time=60, \
                                                          log_power_time=60, CPU_super_f = sweep_super_f, flag = loop)
                                    self.target_case_test(para)
                                    self.WriteExcel(para, "cpuss0-max-step")
                                break

        logger.info("Final Step")
        self.BreakDownPowerResult()

    def dhry_file_parser(self, parent, filename):
        time = ''
        score = ''
        loop = ''
        thread = ''
        f = open(os.path.join(parent, filename), 'r')
        for line in f.readlines():
            # print line
            # find_str = re.findall(r'for\s{0,4}\d{0,10} passes = \s{0,4}\d{0,4}.\d{0,4}', line)
            # print find_str
            # if len(find_str) != 0:
            #     temp = re.split(r' ', find_str[0])
            #     return temp[1],temp[4]
            find_str = re.findall(r'number of loops: \s{0,4}\d{0,10}', line)
            if len(find_str) != 0:
                temp = re.split(r' ', find_str[0])
                loop = temp[3]

            find_str = re.findall(r'Total dhrystone run time: \s{0,4}\d{0,10}.\d{0,10}', line)
            if len(find_str) != 0:
                temp1 = re.split(r' ', find_str[0])
                score = temp1[4]

            find_str = re.findall(r'number of threads: \s{0,4}\d{0,10}.\d{0,10}', line)
            if len(find_str) != 0:
                temp2 = re.split(r' ', find_str[0])
                thread = temp2[3]
        f.close()
        return loop, score, thread

    """截取波形中想要的时间段电流值（13-15s）"""
    def AnalyzingPowerResult(self, para):
        cmdResult = CommandLine.RunCommand(CommonApplicationUtilities._ToolsPath + "UDASDataAnalysis\\UDASDataAnalysis.exe VBAT 1 " +
            str(int(13 * 10 ** 9)) + "-" + str(int(15 * 10 ** 9))+ " " +os.path.join(para.TestCaseFolder.replace('/', '\\'), "UDAS"), 600, True)
        logger.info(cmdResult.CmdResult.Output)
        if "Error" in cmdResult.CmdResult.Output:
            logger.error("Fail to analyze power data: " + cmdResult.CmdResult.Output)
        else:
            cmdResult.CmdResult.OutputLines = [x for x in cmdResult.CmdResult.OutputLines if x != '']

            plane_current_avg = cmdResult.CmdResult.OutputLines[0].split('-')[0].split(',')[0]
            # plane_current_min = cmdResult.CmdResult.OutputLines[0].split('-')[0].split(',')[1]
            # plane_current_max = cmdResult.CmdResult.OutputLines[0].split('-')[0].split(',')[2]

            logger.info("I_Avg, I_Min, I_Max, V_Avg, V_Min, V_Max")
            logger.info(plane_current_avg)
        return plane_current_avg

    def WriteExcel(self, para, ThermalLogName):
        """write data"""
        if 'KratosLite' or 'Kratos' in TestSuiteConfig.HardwareType:
            avgCurrent = self.AnalyzingPowerResult(para)
            avgVoltage = self.GetAvgCurrentAndVoltage()

            """解析dhry.txt"""

            for parent, dirs, filenames in os.walk(self.target_dir):
                for filename in filenames:
                    if filename == 'dhry.txt':
                        [loop, time, thread] = self.dhry_file_parser(parent, filename)
            perf = int(loop)/float(time)/1757
            EndTime = Decimal(time)
            ThermalValue = self.GetThermalValue(para, 24, endRow = int(EndTime), target = ThermalLogName)
            logger.info("Appending test case data into Excel")
            logger.info("dhry dir: " + str(self.target_dir))
            excelHandle = ExcelHandle(os.path.join(TestSuiteConfig.ReportsPath, "CPUTestSummary.xls"))
            excelHandle.GetSheetHandle("CPUTest")
            tcInfo = [para.case_name, str(avgCurrent), str(avgVoltage), loop, time, thread, str(round(perf, 2)), str(ThermalValue)]
            logger.info(tcInfo)
            excelHandle.WriteRow(*tcInfo, beginColumn=0, style="body")
            excelHandle.SaveFile()
            excelHandle = None
        elif 'Monitor' in TestSuiteConfig.HardwareType:
            file_name = os.path.join(self.PowerHandler.collect_dir, self.PowerHandler.save_name + '.pt4')
            logger.info(file_name)
            st = 0
            et = 50
            avgCurrent = PowerMonitorParser().pt_csv(file_name, 'pt4', st, et)
            logger.info("Appending test case data into Excel")
            excelHandle = ExcelHandle(os.path.join(TestSuiteConfig.ReportsPath, "CPUTestSummary.xls"))
            excelHandle.GetSheetHandle("CPUTest")
            tcInfo = [para.case_name, para.GPU_power_f, str(round(avgCurrent, 2)), "4.0"]
            excelHandle.WriteRow(*tcInfo, beginColumn=0, style="body")
            excelHandle.SaveFile()
            excelHandle = None

    def GetAvgCurrentAndVoltage(self):
        return round(float(TestCasePowerMetrics.AverageVoltage),2)

    """获取Theral log"""
    def GetThermalValue(self, para, startRow=0, endRow=0, target = "cpuss0-max-step"):
        logger.info("Calculating Average Thermal Value")
        FPSColumn = -1
        totalFPS = 0
        countFPS = 0
        rowNumber = 0
        averageThermalValue = -1
        TsensLog = ""
        files = os.listdir(os.path.join(para.TestCaseFolder, "logs"))
        if len(files) == 0:
            logger.warning("There is no tsens logger")
            return averageThermalValue
        for file in files:
            fileFullPath = os.path.join(os.path.join(para.TestCaseFolder, "logs"), file)
            if os.path.splitext(file)[1].lower() == ".csv":
                TsensLog = fileFullPath
        if TsensLog == "":
            logger.warning("There is no tsens logger csv file")
            return averageThermalValue
        try:
            with open(TsensLog, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    if FPSColumn == -1:
                        i = 0
                        for item in row:
                            if item == target:
                                FPSColumn = i
                                break
                            i += 1
                    else:
                        if rowNumber >= startRow:
                            #logger.info(row)
                            if row == []:
                                break
                            if endRow == 0:
                                totalFPS += int(row[FPSColumn])
                                countFPS += 1
                            else:
                                if rowNumber <= endRow:
                                    totalFPS += int(row[FPSColumn])
                                    countFPS += 1
                                else:
                                    break
                        rowNumber += 1
                f.close()
            averageThermalValue = round((float(totalFPS) / float(countFPS) / 1000.0), 2)
        except Exception as e:
            logger.error("Error in calculating average FPS: " + str(e))
            averageThermalValue = -1
        logger.info("Average FPS: " + str(averageThermalValue))
        return averageThermalValue

    def BreakDownPowerResult(self):
        ToolsPath = os.path.join(os.getcwd(), "tool")
        cmdResult = CommandLine.RunCommand(ToolsPath + "\\DBBDDataParser.exe" + " - manual " + "-dir " + TestSuiteConfig.ReportsPath, 600, True)
        logger.info(cmdResult.CmdResult.Output)

if __name__ == '__main__':
    # test = PTT_LOG_CPUPower()
    # test.check_FPS()

    # qrd_cpu_setting = QRD_CPU_SETTING()
    # cpupower_qrd_krato_db = CPUPOWER_QRD_KRATO_DB()

    # qrd_cpu_setting.ATS_1440_2880_8150()
    # for i in (0,3):
    # qrd_cpu_setting.scroll()

    temp = QRDSetting()
    temp.__init__()

