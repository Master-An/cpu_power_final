# -*- encoding: utf-8 -*-
from conf.testSuiteConfig import TestSuiteConfig
from conf.testCaseConfig import TestCaseConfig
from core import POWER_QRD_CPU as test
from core.ptasLogger import logger, ConfigureLogger

import os
import sys
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

CaseTime = time.strftime("%m_%d_%H_%M", time.localtime())
TestSuiteConfig.ChannelConfiguration = "Channel_Default.udas"

"""KratosLite"""
TestSuiteConfig.HardwareType = "KratosLite"
TestSuiteConfig.KratosID = "634"
TestSuiteConfig.KratosIpAddress = "127.0.0.1"
TestSuiteConfig.KratosPcName = "QCT-KRATOS-634"

"""Kratos"""
# TestSuiteConfig.HardwareType = "Kratos"
# TestSuiteConfig.KratosID = "1050"
# TestSuiteConfig.KratosIpAddress = "10.239.120.65"
# TestSuiteConfig.KratosPcName = "QCT-KRATOS-1050"

"""common part"""
TestSuiteConfig.CurrentLimit = "4.0"
TestSuiteConfig.VoltageLevel = "4.0"
TestSuiteConfig.OVPLimit = "4.2"
TestSuiteConfig.SampleRate = "2500"
TestSuiteConfig.BootupAndShutdownType = "NoReboot"
TestSuiteConfig.ReportsPath = os.path.join(r"C:\Dropbox\AutomationTestLog", "DhrystoneTest_" + CaseTime)
logger.info(TestSuiteConfig.ReportsPath)
TestCaseConfig.MeasurementDuration = '60'
# TestCaseConfig.CoreOnline = ['10100000', '10000000', '00000010', '00000011']
TestCaseConfig.CoreOnline = ['10100000', '10000000']



TestCaseConfig.Interation = 3
if not os.path.exists(TestSuiteConfig.ReportsPath):
    os.mkdir(TestSuiteConfig.ReportsPath)
ConfigureLogger(logsFilePath = os.path.join(TestSuiteConfig.ReportsPath), logFileName = 'logs.log', errorFileName = 'error.log')
test_db = test.CPUPOWER_QRD_KRATO_DB()
test_db.target_case_test_all()
