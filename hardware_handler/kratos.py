'''***********************************************************************************************************************
**    Confidential and Proprietary – Qualcomm Technologies, Inc.
**
**    This technical data may be subject to U.S. and international export, re-export, or transfer
**    ("export") laws. Diversion contrary to U.S. and international law is strictly prohibited.
**
**    Restricted Distribution: Not to be distributed to anyone who is not an employee of either
**    Qualcomm or its subsidiaries without the express approval of Qualcomm’s Configuration
**    Management.
**
**    © 2013 Qualcomm Technologies, Inc
************************************************************************************************************************'''

from core.status import StatusResult
from core.ptasLogger import logger

from hardware_handler.kratosApi.kratosApi import KratosHandler
from hardware_handler.kratosApi.kratosRecovery import KratosRecovery
from hardware_handler.kratosApi.kratosConstants import KratosConstants

from conf.testSuiteConfig import TestSuiteConfig
from conf.testCaseConfig import TestCaseConfig

from lib.testCasePowerMetrics import TestCasePowerMetrics

from datetime import datetime
import os, shutil, time, socket

class Kratos:
    """
    #-------------------------------------------------------------------------------------------------------------------
    # Name: Kratos
    # Description: Performs Operation on KRATOS machine
    #     Wrapper class on kraosApi Python modules of KRATOS to provide power measurement, USB operations etc.
    #-------------------------------------------------------------------------------------------------------------------
    """

    kratosHandler = None
    """
    #-------------------------------------------------------------------------------------------------------------------
    # Name: kratosHandler
    # Description: kratosHandler object of KratosHandler class which can perform functionalities e.g. disconnecting power,
    #    connecting USB, etc. on KRATOS Machine
    #-------------------------------------------------------------------------------------------------------------------
    """

    logsPath = None
    """
    #-------------------------------------------------------------------------------------------------------------------
    # Name: logsPath
    # Description: logs location to save logs on KRATOS PC
    #-------------------------------------------------------------------------------------------------------------------
    """

    udasDir = None
    """
    #-------------------------------------------------------------------------------------------------------------------
    # Name: udasDir
    # Description: UDAS location in reports path
    #-------------------------------------------------------------------------------------------------------------------
    """

    def __init__(self, setAcqConfig = True):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: __init__
        # Description: Initializes KratosHandler class object, sets power supply parameters and Acquisition parameters
        #-------------------------------------------------------------------------------------------------------------------
        """

        self.retryOnErrorCount = 0
        if not TestSuiteConfig.KratosIpAddress :
            result = self.GetKratosIP(TestSuiteConfig.KratosPcName)
            if result.HasError():
                raise Exception(result.ErrorMessage())

        self.kratosHandler = KratosHandler(TestSuiteConfig.KratosIpAddress)

        if setAcqConfig:

            logger.info( "Connecting to KRATOS Machine")

            result = self.KratosSetup()
            if result.HasError():
                raise Exception(result.ErrorMessage())

            # SetPowerConfiguration function is used to configure the Voltage, Current & OVP values on KRATOS
            result = self.SetPowerConfiguration()
            if result.HasError():
                raise Exception(result.ErrorMessage())

            # SetAcquisitionConfiguration function is used to set Acquisition parameters on KRATOS.
            result = self.SetAcquisitionConfiguration()
            if result.HasError():
                raise Exception(result.ErrorMessage())

            result = self.SetDefaultOptions()
            if result.HasError():
                raise Exception(result.ErrorMessage())

            self.udasDir = TestCaseConfig.ReportsPath + '\\UDAS'


    def SetPowerConfiguration(self):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: SetPowerConfiguration
        # Input: Takes no argument
        # Description: Sets up power configuration parameters Voltage, Current, OVP
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """

        logger.info("Setting Voltage, Current & OVP : " + TestSuiteConfig.VoltageLevel + ", " + TestSuiteConfig.CurrentLimit + ", " + TestSuiteConfig.OVPLimit)

        # ConfigurePowerSupply function is used to configure the Voltage, Current & OVP values on KRATOS
        result =self.kratosHandler.ConfigurePowerSupply(TestSuiteConfig.VoltageLevel, TestSuiteConfig.CurrentLimit, TestSuiteConfig.OVPLimit)
        if result.HasError():
            logger.error("Error in Configuring Power Supply :  " + result.ErrorMessage())
            recoveryResult = self.KratosErrorHandler()
            return recoveryResult

        return StatusResult.Success()

    def SetAcquisitionConfiguration(self):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: SetAcquisitionConfiguration
        # Input: Takes no argument
        # Description: Sets up Acquisition configuration parameters AccuracyMode, SampleRate, MeasurementDuration, etc
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """
        samplingRate = TestCaseConfig.SampleRate if (TestCaseConfig.SampleRate != '') else TestSuiteConfig.SampleRate
        logger.info("Configuring Acquisition Parameters : " + TestSuiteConfig.AccuracyMode + ", " + samplingRate + ", " + str(TestCaseConfig.MeasurementDuration) + ", MANUAL")

        # SetAcquisitionParameters function is used to configure the parameters AccuracyMode, SampleRate, MeasurementDuration, etc on KRATOS
        result = self.kratosHandler.SetAcquisitionParameters(TestSuiteConfig.AccuracyMode, samplingRate, str(TestCaseConfig.MeasurementDuration), "MANUAL")
        if result.HasError():
            logger.error("Error in configuring Acquisition Parameters :  " + result.ErrorMessage())
            recoveryResult = self.KratosErrorHandler()
            return recoveryResult

        return StatusResult.Success()

    def SetConfigurationFile(self, configFile):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: SetConfigurationFile
        # Input: Takes one argument
        #       configFile: UDAS configuration file path for KRATOS
        # Description: Sets up channel configuration for KRATOS
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """

        logger.info("Loading KRATOS Channel Configuration : " + configFile)

        if not configFile.endswith('.udas'):
            return StatusResult.Error('KRATOS : ', 'Incorrect Configuration file for KRATOS, UDAS file needed')

        result =self.kratosHandler.LoadChannelConfiguration("C:\\rcm\\cfg\\"+ configFile)
        if result.HasError():
            logger.error("Error in Loading Channel Configuration :  " + result.ErrorMessage())
            recoveryResult = self.KratosErrorHandler()
            return recoveryResult

        return StatusResult.Success()

    def SetKratosInIdleState(self) :
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: KratosSetup
        # Input: Takes no argument
        # Description: Checks Kratos Acquisition State. Set Kratos State to Idle, if Kratos Acquisition state is not in idle.
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """
        if KratosConstants.ExtAcquisitionStatus['IDLE'] != self.kratosHandler.GetExtAcquisitionStatus():
            logger.warning("Already in Acquisition state")
            result = self.StopMeasurement()
            if result.HasError():
                return StatusResult.Error("Failed to stop Acquisition")

        return StatusResult.Success()


    def KratosSetup(self):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: KratosSetup
        # Input: Takes no argument
        # Description: Sets up KRATOS calibration
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """
        result = self.SetKratosInIdleState()
        if result.HasError() :
            logger.error("Error in Setting Kratos to IDLE State. " + result.ErrorMessage())
            return StatusResult.Error("Error in Setting Kratos to IDLE State. " + result.ErrorMessage())

        #Checking calibration on KRATOS
        calStatusList = []
        result = self.GetCalibrationStatus(calStatusList)
        if result.HasError():
            return result

        if 'False' in calStatusList[0]:

            logger.warning("Starting self calibration")

            result = self.UsbOff()
            if result.HasError():
                return result

            result = self.PowerOff()
            if result.HasError():
                return result

            result = self.kratosHandler.SelfCalibration()
            if result.HasError():
                return result

            result = self.WaitForIdle()
            if result.HasError():
                return result

            calStatusList = []
            result = self.GetCalibrationStatus(calStatusList)
            if result.HasError():
                return result

            if 'False' in calStatusList[0]:
                return StatusResult.Error('Failed to complete KRATOS self calibration')
            '''
            result = self.PowerOn()
            if result.HasError():
                return result
            '''
        return StatusResult.Success()

    def WaitForIdle(self) :
        """
        #-------------------------------------------------------------------------------------------------------------------
		# Name: WaitForIdle
		# Input: Takes No Arguments
		# Description: Waits 5 minutes for Kratos to go to IDLE state
		# Return: StatusResult() object
		#-------------------------------------------------------------------------------------------------------------------
		"""
        count = 0
        while(count < 30):

            busyStatus = self.kratosHandler.IsKratosBusy()
            if busyStatus is None:
                return StatusResult.Error('Failed to read Kratos status')
            if not busyStatus:
                return StatusResult.Success()
            time.sleep(10)
            count = count + 1

        logger.Error("KRATOS failed to return to IDLE state in 5 minutes")
        return StatusResult.Error("KRATOS failed to return to IDLE state in 5 minutes")

    def SetDefaultOptions(self) :
        """
        #-------------------------------------------------------------------------------------------------------------------
		# Name: SetDefaultOption
		# Input: Takes No Arguments
		# Description: Sets default of parameters :
		#     checkCal : False, ignoreSelfCal : false, ignoreExtCal : True, enforceMaxVBat : False, checkConnectors : True, autoSaveData : True
		# Return: StatusResult() object
		#-------------------------------------------------------------------------------------------------------------------
		"""
        result = self.kratosHandler.SetDefaultOptions()
        if result.HasError() :
            logger.Error("Error in setting Default Options on KRATOS. " + result.ErrorMessage())
            recoveryResult = self.KratosErrorHandler()
            return recoveryResult

        return StatusResult.Success()


    def SetDataCollectionPath(self):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: SetDataCollectionPath
        # Input: Takes no argument
        # Description: Sets up path to save UDAS waveform
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """
        # SetOutputDirectory function is used to set the Automation logs output directory location
        logger.info("Setting Logs Location for saving UDAS")

        dateTimeStrPath = "Automation\\Logs\\" + str(datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
        kratosPcLocalPath = "C:\\" + dateTimeStrPath

        self.logsPath = "\\\\" + TestSuiteConfig.KratosIpAddress + "\\C$\\" + dateTimeStrPath

        logger.info('KRATOS : Log directory path : ' + self.logsPath)
        result =self.kratosHandler.SetOutputDirectory(kratosPcLocalPath)
        if result.HasError():
            logger.error("Error in setting up UDAS logs location :  " + result.ErrorMessage())
            recoveryResult = self.KratosErrorHandler()
            return recoveryResult

        return StatusResult.Success()

    def GetCalibrationStatus(self, calStatusList):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: GetCalibrationStatus
        # Input: Takes one argument, calStatusList
        #        calStatusList : empty list, to return Calibration Status
        # Description: Stops power measurement on KRATOS
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """

        result = self.kratosHandler.CheckCalibrationStatus(calStatusList)
        if result.HasError() :
            logger.error("Error in checking KRATOS calibration status :  " + result.ErrorMessage())
            recoveryResult = self.KratosErrorHandler()
            return recoveryResult

        logger.info("Self Calibration : " + calStatusList[0])
        logger.info("DMM Calibration : " + calStatusList[1])
        logger.info("MUX Calibration : " + calStatusList[2])

        return StatusResult.Success()

    def StopMeasurement(self):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: StopMeasurement
        # Input: Takes no argument
        # Description: Stops power measurement on KRATOS
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """

        # StopAcquisition function is used to stop capturing waveforms on KRATOS while the test case runs on DUT
        logger.info('KRATOS : Stopping measurement')

        result = self.kratosHandler.StopAcquisition()
        if result.HasError():
            logger.error("Error in Stopping Acquisition :  " + result.ErrorMessage())
            recoveryResult = self.KratosErrorHandler()
            return recoveryResult

        return self.WaitForIdle()


    def StartAcquisition(self):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: StartAcquisition
        # Input: Takes no argument
        # Description: Makes KRATOS to start power measurement
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """

        # StartAcquisition function is used to start capturing waveforms on Kratos while the test case runs on DUT
        logger.info('KRATOS : Preparing to start measurement')

        result = self.kratosHandler.StartAcquisition()
        if result.HasError():
            logger.error("Error in Starting Acquisition :  " + result.ErrorMessage())
            recoveryResult = self.KratosErrorHandler()
            return recoveryResult

        return StatusResult.Success()


    def StartMeasurement(self):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: StartMeasurement
        # Input: Takes no argument
        # Description: Starts power measurement on KRATOS
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """
        logger.info('KRATOS : Starting measurement')

        # SendSwTrigger function is used to send Software trigger to DUT
        result = self.kratosHandler.SendSwTrigger()
        if result.HasError():
            logger.error("Error in Sending Software Trigger / Starting measurement :  " + result.ErrorMessage())
            recoveryResult = self.KratosErrorHandler()
            return recoveryResult

        return StatusResult.Success()

    def GetPlotStatistics(self):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: GetPlotStatistics
        # Input: Takes no argument
        # Description: Prints measured power number
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """

        logger.info("Reading Measured Power Numbers")

        statisticsList = [1,2]

        result = self.kratosHandler.GetSinglePlotStatistics(statisticsList)
        if result.HasError():
            logger.error("Error in Reading Power Numbers :  " + result.CmdResult.Output)
            recoveryResult = self.KratosErrorHandler()
            return recoveryResult

        logger.info("Measured Current : " + statisticsList[0])
        logger.info("Measured Voltage : " + statisticsList[1])

        TestCasePowerMetrics.MeasuredCurrent = str(statisticsList[0])
        TestCasePowerMetrics.AverageVoltage = str(statisticsList[1])

        return StatusResult.Success()

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
        logger.info('KRATOS: USB ON')

        result = self.kratosHandler.SetUsbConnection('true')
        if result.HasError():
            logger.error("Error in Turning ON USB :  " + result.ErrorMessage())
            recoveryResult = self.KratosErrorHandler()
            return recoveryResult

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
        logger.info('KRATOS: USB OFF')

        result = self.kratosHandler.SetUsbConnection('false')
        if result.HasError():
            logger.error("Error in Turning OFF USB :  " + result.ErrorMessage())
            recoveryResult = self.KratosErrorHandler()
            return recoveryResult

        return StatusResult.Success()

    def PowerOn(self):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: PowerOn
        # Input: Takes no argument
        # Description: Power On KRATOS
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """

        # SetPowerSupplyOutput function is used to turn on/off the power supply on device under test. True to turn on, False to turn off the device.
        # Powering On the device by passing argument - True
        logger.info('KRATOS: POWER ON')

        result =self.kratosHandler.SetPowerSupplyOutput('true')
        if result.HasError():
            logger.error("Error in Powering ON Device :  " + result.ErrorMessage())
            recoveryResult = self.KratosErrorHandler()
            return recoveryResult

        return StatusResult.Success()

    def PowerOff(self):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: PowerOff
        # Input: Takes no argument
        # Description: Power Off KRATOS card
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """

        # SetPowerSupplyOutput function is used to turn on/off the power supply on device under test. True to turn on, False to turn off the device.
        # Powering OFF the device by passing argument - false
        logger.info('KRATOS: POWER OFF')

        result =self.kratosHandler.SetPowerSupplyOutput('false')
        if result.HasError():
            logger.error("Error in Powering OFF Device :  " + result.ErrorMessage())
            recoveryResult = self.KratosErrorHandler()
            return recoveryResult

        return StatusResult.Success()


    def RebootDevice(self) :
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: RebootDevice
        # Input: Takes no argument
        # Description: Reboots Device by switching Power & USB
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """

        logger.info("Turning Off Device")
        result = self.PowerOff()
        if result.HasError():
            return result
        result = self.UsbOff()
        if result.HasError():
            return result

        time.sleep(2)

        logger.info("Booting up Device")
        result = self.PowerOn()
        if result.HasError():
            return result
        result = self.UsbOn()
        if result.HasError():
            return result

        return result

    def GetKratosIP(self, name):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: GetKratosIP
        # Input: Takes one argument
        #    name : KRATOS host name
        # Description: Gets KRATOS IP address from KRATOS host name
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """
        if (name is "") or ('kratos' not in name.lower()):
            return StatusResult.Error('KRATOS error: ', ' Incorrect KRATOS name')

        try:
            ipAddress = socket.gethostbyname(name)
        except Exception as e:
            logger.error('KRATOS : Failed to get KRATOS IP address')
            return StatusResult.Error(str(e))

        TestSuiteConfig.KratosIpAddress = str(ipAddress)
        logger.info('KRATOS : ' + 'Name - ' + name + ', IP address - ' + TestSuiteConfig.KratosIpAddress)

        return StatusResult.Success()

    def CopyUdasLogs(self):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: CopyUdasLogs
        # Input: Takes no argument
        # Description: Copy UDAS waveform from Default location to Logs location
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """

        logger.info("UDAS Directory : " + self.udasDir)

        logger.info("Copying UDAS waveform from Default location to Logs location")

        try :
            os.makedirs(self.udasDir)
        except OSError :
            if not os.path.exists(self.udasDir) :
                return StatusResult.Error("Error in creating UDAS Directory on Automation PC : " + self.udasDir)

        try:
            files = os.listdir(self.logsPath)
            for file in files:
                shutil.copy(os.path.join(self.logsPath, file), os.path.join(self.udasDir, file))
        except Exception as e:
            return StatusResult.Error('Failed to copy UDAS waveform : ', str(e))

        logger.info("Copying UDAS waveform Completed")

        return StatusResult.Success()

    def RemoveWaveforms(self):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: RemoveWaveforms
        # Input: Takes no argument
        # Description: Removes the UDAS waveform logs location within the Kratos PC
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """

        logger.info("Removing waveform Directory : " + self.logsPath + " from Kratos PC")

        try:
            files = os.listdir(self.logsPath)
            for file in files:
                os.remove(os.path.join(self.logsPath, file))
        except Exception as e:
            return StatusResult.Error('Failed to remove waveform directory from Kratos PC', str(e))

        logger.info("Removing waveform directory from Kratos PC Completed")
        return StatusResult.Success()

    def KratosErrorHandler(self):
        """
        -------------------------------------------------------------------------
        # Name: KratosErrorHandler
        # Input: Takes no argument
        # Description: Ping and restart Kratos Application for Recovery
        # Return: StatusResult.Error
        -------------------------------------------------------------------------
        """
        self.retryOnErrorCount = self.retryOnErrorCount + 1
        if self.retryOnErrorCount > 3 :
             return StatusResult.Error("Failled to Handle Error and Restart Kratos after Max Tries.")

        try:
            logger.info("Entered Kratos Error Handling")
            kratosRecovery  = KratosRecovery()
            result = kratosRecovery.PingKratos(TestSuiteConfig.KratosIpAddress, 3600)
            if result.HasError() :
                logger.error("Could Not Ping Kratos Machine in 60 Minutes.")
                return result
            result = kratosRecovery.RestartKratos(TestSuiteConfig.KratosIpAddress)
            logger.info("Rebooting Kratos Software and Test Device")
            if result.HasError():
                return result
            logger.info("Re-Configuring Kratos")
            result = self.KratosSetup()
            if result.HasError():
                return result

            # SetConfigurationFile function is used to recall the cfg file saved by user on Kratos
            configFile = TestCaseConfig.ChannelConfiguration if TestCaseConfig.ChannelConfiguration else TestSuiteConfig.ChannelConfiguration
            result = self.SetConfigurationFile(configFile)
            if result.HasError():
                raise Exception(result.ErrorMessage())

            # SetPowerConfiguration function is used to configure the Voltage, Current & OVP values on KRATOS
            result = self.SetPowerConfiguration()
            if result.HasError():
                raise Exception(result.ErrorMessage())

            # SetAcquisitionConfiguration function is used to set Acquisition parameters on KRATOS.
            result = self.SetAcquisitionConfiguration()
            if result.HasError():
                raise Exception(result.ErrorMessage())

            result = self.SetDefaultOptions()
            if result.HasError():
                raise Exception(result.ErrorMessage())

            logger.info("Booting up Device")
            result = self.PowerOn()
            if result.HasError():
                return result
            result = self.UsbOn()
            if result.HasError():
                return result
        except Exception as e:
            logger.error(str(e))
        return StatusResult.Error("Failing This Attempt To Retry Test After Kratos Restart")

if __name__ == "__main__":
    test = Kratos()
    test.GetKratosIP("QCT-KRATOS-634")

