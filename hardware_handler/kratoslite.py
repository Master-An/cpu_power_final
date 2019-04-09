'''***********************************************************************************************************************
**    Confidential and Proprietary Qualcomm Technologies, Inc.
**
**    This technical data may be subject to U.S. and international export, re-export, or transfer
**    ("export") laws. Diversion contrary to U.S. and international law is strictly prohibited.
**
**    Restricted Distribution: Not to be distributed to anyone who is not an employee of either
**    Qualcomm or its subsidiaries without the express approval of Qualcomm Configuration
**    Management.
**
**    2013 Qualcomm Technologies, Inc
************************************************************************************************************************'''

from core.status import StatusResult
from core.ptasLogger import logger

from hardware_handler.kratosApi.kratosApi import KratosHandler
from hardware_handler.qcusbswitch import QcUsbSwitch
from conf.testSuiteConfig import TestSuiteConfig
from conf.testCaseConfig import TestCaseConfig

from datetime import datetime
from hardware_handler.kratos import Kratos
import os, shutil, time, socket



class KratosLite(Kratos):

    def __init__(self, setAcqConfig = True):

        self.retryOnErrorCount = 0
        self.kratosHandler = KratosHandler(TestSuiteConfig.KratosIpAddress)

        logger.info( "Connecting to KRATOSLITE Machine, IP is:" + self.kratosHandler.kratosPcIpAddress + "Kratoslite PC name is: " + TestSuiteConfig.KratosPcName)

        result = self.KratosSetup()
        if result.HasError():
            raise Exception(result.ErrorMessage())

        # SetPowerConfiguration function is used to configure the Voltage, Current & OVP values on KRATOS
        result = self.SetPowerConfiguration()
        if result.HasError():
            raise Exception(result.ErrorMessage())

        if setAcqConfig:
            # SetAcquisitionConfiguration function is used to set Acquisition parameters on KRATOS.
            result = self.SetAcquisitionConfiguration()
            if result.HasError():
                raise Exception(result.ErrorMessage())

            result = self.SetDefaultOptions()
            if result.HasError():
                raise Exception(result.ErrorMessage())

            self.udasDir = TestCaseConfig.ReportsPath + '\\UDAS'



    def UsbOn(self):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: UsbOn
        # Input: Takes no argument
        # Description: Enable USB on KRATOS
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """

        # Connecting the USB by passing argument - True
        logger.info('KRATOSLITE: USB ON')

        result = QcUsbSwitch.SetUsbConnection('usb_on')
        if result.Status.HasError():
            logger.error("Error in Turning ON USB :  " + result.CmdResult.Output)
            return result.Status
        logger.info('Waiting for 10 Seconds for USB to stabilise')
        time.sleep(10)
        return StatusResult.Success()


    def UsbOff(self):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: UsbOff
        # Input: Takes no argument
        # Description: Disable USB on KRATOS
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """

        # Disconnecting the USB by passing argument - false
        logger.info('KRATOSLITE: USB OFF')

        result = QcUsbSwitch.SetUsbConnection('usb_off')
        if result.Status.HasError():
            logger.error("Error in Turning OFF USB :  " + result.CmdResult.Output)
            return result.Status

        return StatusResult.Success()


