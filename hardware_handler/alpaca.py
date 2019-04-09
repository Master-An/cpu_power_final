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

from ptas_core.status import StatusResult
from ptas_core.ptasLogger import logger
from ptas_core.commonApplicationUtilities import CommonApplicationUtilities

from ptas_config.testCaseConfig import TestCaseConfig
from ptas_config.testSuiteConfig import TestSuiteConfig

from ptas_result.testCasePowerMetrics import TestCasePowerMetrics

from ptas_hardware_handler.alpacaApi.tac import Tac
from ptas_hardware_handler.alpacaApi.epm import Epm

from datetime import datetime
import os, time, shutil, pdb

class Alpaca:
    """
    #-------------------------------------------------------------------------------------------------------------------
    # Name: Alpaca
    # Description: Performs Operation on ALPACA card
    #     Wrapper class on TAC and EPM Python modules of ALPACA to provide power measurement, USB operations etc.
    #-------------------------------------------------------------------------------------------------------------------
    """

    tac = None
    """
    #-------------------------------------------------------------------------------------------------------------------
    # Name: tac
    # Description: Test Automation Controller (TAC)
    #    ALPACA has a TAC which can perform functionalities e.g. disconnecting power, connecting USB, etc.
    #-------------------------------------------------------------------------------------------------------------------
    """

    epm = None
    """
    #-------------------------------------------------------------------------------------------------------------------
    # Name: epm
    # Description: Embedded Power Measurement (EPM)
    #    ALPACA debug boards connect to the target device's MTP/RCM header and can measure the same power rails as Kratos
    #    using EPM.
    #-------------------------------------------------------------------------------------------------------------------
    """

    logsPath = None
    """
    #-------------------------------------------------------------------------------------------------------------------
    # Name: logsPath
    # Description: logs location to save logs on ALPACA PC
    #-------------------------------------------------------------------------------------------------------------------
    """

    udasDir = None
    """
    #-------------------------------------------------------------------------------------------------------------------
    # Name: udasDir
    # Description: UDAS location in reports path
    #-------------------------------------------------------------------------------------------------------------------
    """

    boardHasTac = False
    """
    #-------------------------------------------------------------------------------------------------------------------
    # Name: boardHasTac
    # Description: True if Alpaca board has a Test Automation Controller (TAC)
    #-------------------------------------------------------------------------------------------------------------------
    """

    boardHasEpm = False
    """
    #-------------------------------------------------------------------------------------------------------------------
    # Name: boardHasEpm
    # Description: True if Alpaca board has an Embedded Power Measurement (EPM)
    #-------------------------------------------------------------------------------------------------------------------
    """



    def __init__(self, setAcqConfig = True):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: __init__
        # Description: Initializes the object of class Tac and Epm, to establish connection with alpaca card
        #-------------------------------------------------------------------------------------------------------------------
        """
        logger.info("Hardware Type: " + str(TestSuiteConfig.HardwareType))
        #pdb.set_trace()
        if TestSuiteConfig.HardwareType == 'Alpaca Board' or TestSuiteConfig.HardwareType == 'Alpaca Dongle':
            self.boardHasTac = True

        if TestSuiteConfig.HardwareType == 'Alpaca Board' or TestSuiteConfig.HardwareType == 'Alpaca SPMv4.1':
            self.boardHasEpm = True

        logger.info("Board has TAC: " + str(self.boardHasTac) + " Board has EPM: " + str(self.boardHasEpm))
        logger.info( "Connecting to ALPACA port")

        if self.boardHasTac:
            try:
                self.tac = Tac()
                logger.info( "ALPACA version: " + self.tac.GetVersion() )
                logger.info( "ALPACA UUID: " + self.tac.GetUuid() )
            except Exception as e:
                logger.error(str(e))
                raise Exception(e)

        if self.boardHasEpm:
            try:
                self.epm = Epm()
            except Exception as e:
                logger.error(str(e))
                raise Exception(e)

            if  setAcqConfig:
                self.udasDir = TestCaseConfig.ReportsPath + '\\UDAS'


    def SetConfigurationFile(self, configFile):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: SetConfigurationFile
        # Input: Takes one argument
        #       configFile: json config filename for ALPACA
        # Description: Sets up configuration for ALPACA card
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """

        logger.info("Loading ALPACA Configuration : " + configFile)

        if not configFile.endswith('.json'):
            return StatusResult.Error('ALPACA : ', 'Incorrect Configuration file for ALPACA, JSON file needed')

        configFile = CommonApplicationUtilities._ResourcesConfigFilePath + '\\Alpaca\\' + configFile

        if self.boardHasEpm:
            if self.epm.getData:
                logger.warning('ALPACA : Measurement already running. Stopping previous measurement')

                result = self.StopMeasurement()
                if result.HasError():
                    logger.error('ALPACA : Error while stopping previous measurement')
                    return result

            if not os.path.exists(configFile):
                return StatusResult.Error('ALPACA : ', 'Configuration file not found')

        if self.boardHasEpm:
            try:
                self.epm.SetConfigFile(configFile)
            except Exception as e:
                logger.error(str(e))
                return StatusResult.Error('ALPACA : ', str(e))

        return StatusResult.Success()

    def SetDataCollectionPath(self):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: SetDataCollectionPath
        # Input: Takes no argument
        # Description: Sets up path to save UDAS waveform on automation PC
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """
        logger.info("Setting Logs Location for saving UDAS")

        if self.boardHasEpm:
            if self.epm.getData:
                logger.warning('ALPACA : Measurement already running. Stopping previous measurement')

                result = self.StopMeasurement()
                if result.HasError():
                    logger.error('ALPACA : Error stopping previous measurement')
                    return result

        self.logsPath = "C:\\Automation\\Logs\\" + str(datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))

        if self.boardHasEpm:
            try:
                logger.info('ALPACA : Log directory path : ' + self.logsPath)
                self.epm.SetLogDirectory(self.logsPath)
            except Exception as e:
                logger.error(str(e))
                return StatusResult.Error('ALPACA : ', str(e))

        return StatusResult.Success()

    def StopMeasurement(self):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: StopMeasurement
        # Input: Takes no argument
        # Description: Stops power measurement on ALPACA if power measurement in progress
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """
        #pdb.set_trace()
        logger.info('ALPACA : Stopping measurement')

        if self.boardHasEpm:
            if not self.epm.getData:
                logger.warning('ALPACA : Measurement not running')
                return StatusResult.Success()

            try:
                self.epm.StopMeasurement()
            except Exception as e:
                logger.error(str(e))
                return StatusResult.Error('ALPACA : ', str(e))

        return StatusResult.Success()

    def StartAcquisition(self):

        logger.debug('ALPACA : No action required')

        return StatusResult.Success()

    def StartMeasurement(self):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: StartMeasurement
        # Input: Takes no argument
        # Description: Starts power measurement on ALPACA
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """
        if self.boardHasEpm:
            if self.epm.getData:
                logger.warning('ALPACA : Measurement already running. Stopping previous measurement')

                result = self.StopMeasurement()
                if result.HasError():
                    logger.error('ALPACA : Error stopping previous measurement')
                    return result

            logger.info('ALPACA : Starting measurement')

            try:
                self.epm.StartMeasurement()
            except Exception as e:
                logger.error(str(e))
                return StatusResult.Error('ALPACA : ', str(e))

        return StatusResult.Success()

    def GetPlotStatistics(self):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: GetPlotStatistics
        # Input: Takes no argument
        # Description: Prints power number captured on different rails
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """
        #pdb.set_trace()
        if self.boardHasEpm:
            logger.info("Reading Measured Power Numbers")

            try:
                stats = self.epm.GetResults()
            except Exception as e:
                logger.error(str(e))
                return StatusResult.Error('ALPACA : ', str(e))

            measuredCurrent = None
            measuredVoltage = None

            for channel in sorted(stats):
                if stats[channel]["name"] == "VBAT_I" :
                    measuredCurrent = round(stats[channel]["avg"], 2)
                elif stats[channel]["name"] == "VBAT_V" :
                    measuredVoltage = round(float(stats[channel]["avg"])/1000, 2)

                logger.info("Channel  %3s %30s %4s %4s Average : %10s", str(channel), stats[channel]["name"], stats[channel]["type"], stats[channel]["units"], str(round(stats[channel]["avg"], 2)))

            f = open(''.join([self.logsPath,'\\PowerData.csv']),'w+')
            f.write("Channel#,channel_name,type,unit,avg,min,max,num samples\n")

            current_data = {}
            voltage_data = {}

            for channel in sorted(stats):
                power=-99.0
                f.write("%3d,%s,(%s),[%s],%8.2f,%8.2f,%8.2f,%d,\n" %
                    (channel,
                    stats[channel]["name"],
                    stats[channel]["type"],
                    stats[channel]["units"],
                    stats[channel]["avg"],
                    stats[channel]["min"],
                    stats[channel]["max"],
                    stats[channel]["numSamples"]))
                rail_name=stats[channel]["name"][0:-2]
                if stats[channel]["type"] == "I" or stats[channel]["type"] == "i" :
                    current_data[rail_name]=stats[channel]["avg"]
                    if rail_name in voltage_data.keys():
                        power=float(stats[channel]["avg"])*float(voltage_data[rail_name])/1000

                if stats[channel]["type"] == "V" or stats[channel]["type"] == "v" :
                    voltage_data[rail_name]=stats[channel]["avg"]
                    if rail_name in current_data.keys():
                        power=float(stats[channel]["avg"])*float(current_data[rail_name])/1000

                if power != -99 :
                    f.write("%3d,%s_P,(P),[mW],%8.2f\n" %
                        (channel,
                        rail_name,
                        power))

            f.write("%3d,Total_Time,(T),[S],%d\n" %
                        (channel+1,
                        int(TestCaseConfig.MeasurementDuration)))


        logger.info("Measured Current : " + str(measuredCurrent))
        logger.info("Measured Voltage : " + str(measuredVoltage))

        TestCasePowerMetrics.MeasuredCurrent = measuredCurrent
        TestCasePowerMetrics.AverageVoltage = measuredVoltage

        return StatusResult.Success()

    def UsbOn(self):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: UsbOn
        # Input: Takes no argument
        # Description: Enable USB on ALPACA
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """

        logger.info('ALPACA: USB ON')

        if self.boardHasTac:
            try:
                self.tac.ConnectUsb()

            except Exception as e:
                logger.error(str(e))
                return StatusResult.Error('ALPACA : ', str(e))

        logger.info('Waiting for 10 Seconds for USB to stabilise')
        time.sleep(10)

        return StatusResult.Success()

    def UsbOff(self):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: UsbOff
        # Input: Takes no argument
        # Description: Disable USB on ALPACA
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """

        logger.info('ALPACA: USB OFF')

        if self.boardHasTac:
            try:
                self.tac.DisconnectUsb()
            except Exception as e:
                logger.error(str(e))
                return StatusResult.Error('ALPACA : ', str(e))

        return StatusResult.Success()

    def PowerOn(self):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: PowerOn
        # Input: Takes no argument
        # Description: Power On ALPACA card
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """

        logger.info("ALPACA: Power ON");

        if self.boardHasTac:
            try:
                self.tac.On()
            except Exception as e:
                logger.error(str(e))
                return StatusResult.Error('ALPACA : ', str(e))

        return StatusResult.Success()

    def PowerOff(self):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: PowerOff
        # Input: Takes no argument
        # Description: Power Off ALPACA card
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """

        logger.info("ALPACA: Power OFF");

        if self.boardHasTac:
            try:
                self.tac.Off()
            except Exception as e:
                logger.error(str(e))
                return StatusResult.Error('ALPACA : ', str(e))


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


    def EdlSwitchOn(self):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: EdlSwitchOn
        # Input: Takes no argument
        # Description: Switch ON EDL on ALPACA card
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """

        logger.info('ALPACA: EDL switch on')

        if self.boardHasTac:
            try:
                self.tac._write('edl', 1)
            except Exception as e:
                logger.error(str(e))
                return StatusResult.Error('ALPACA : ', str(e))

        return StatusResult.Success()

    def EdlSwitchOff(self):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: EdlSwitchOff
        # Input: Takes no argument
        # Description: Switch OFF EDL on ALPACA card
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """

        logger.info('ALPACA: EDL switch off')

        if self.boardHasTac:
            try:
                self.tac._write('edl', 0)
            except Exception as e:
                logger.error(str(e))
                return StatusResult.Error('ALPACA : ', str(e))

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

        self.udasDir = TestCaseConfig.ReportsPath + '\\UDAS'
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
        # Description: Removes the waveforms from Default location
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """

        logger.info("Removing waveform Directory : " + self.logsPath)

        try:
            files = os.listdir(self.logsPath)
            for file in files:
                os.remove(os.path.join(self.logsPath, file))
        except Exception as e:
            return StatusResult.Error('Failed to remove waveform directory', str(e))

        logger.info("Removing waveform directory Completed")
        return StatusResult.Success()

    def ReleaseTacPort(self):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: ReleaseTacPort
        # Input: Takes no argument
        # Description: close TAC port
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """
        if self.boardHasTac and hasattr(self.tac, 'ser'):
            try:
                logger.debug('Releasing TAC port')
                self.tac.ser.close()
            except Exception as e:
                logger.error('Failed to close TAC port')
                logger.error(str(e))
                return StatusResult.Error('Failed to close TAC port : ', str(e))

        return StatusResult.Success()

if __name__ == "__main__":

    try:
        alpaca = Alpaca()
    except Exception as e:
        logger.error(str(e))
        exit()

    result = alpaca.SetConfigurationFile('C:\Automation\V3.0.3\Resources\ConfigFiles\Alpaca\qpat_alpaca_config.json')
    if result.HasError() :
        logger.error(result.ErrorMessage())

    result = alpaca.SetDataCollectionPath('C:\Automation\PTAS\Plasma\Engine\Reports')
    if result.HasError() :
        logger.error(result.ErrorMessage())

    result = alpaca.StartMeasurement()
    if result.HasError() :
        logger.error(result.ErrorMessage())
    time.sleep(10)

    result = alpaca.StopMeasurement()
    if result.HasError() :
        logger.error(result.ErrorMessage())

    #result = alpaca.GetSinglePlotStatistics()
    #if result.HasError() :
    #    logger.error(result.ErrorMessage())

