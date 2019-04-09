import re
from ptas_core.command import CommandLine
from ptas_core.status import StatusResult
from ptas_core.ptasLogger import logger
from ptas_core.commonApplicationUtilities import CommonApplicationUtilities
from ptas_windows.widowsComPort import WindowsComPort

class ThermalControllerHandler:
    """
    #----------------------------------------------------------------------------------------------------------------------------------------
    # Name: ThermalControllerHandler
    # Description: Performs Operations on Thermal Controller
    # Sends Commands by passing method names to CPTF Library Interface which calls methdods of the respective class
    #-------------------------------------------------------------------------------------------------------------------
    """

    def __init__(self):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: __init__
        # Description: creates a Constructor
        #-------------------------------------------------------------------------------------------------------------------
        """
        logger.debug("ThermalController Constructor called")

    @staticmethod
    def GetTECComPort():
        """
        -------------------------------------------------------------------------------------------------------------------
         Name: GetTECComPort
         Input: Takes no argument
         Description: Get the COM port number for TEC
         Return: StatusResult() object
        -------------------------------------------------------------------------------------------------------------------
        """
        port = WindowsComPort.GetComPort('prolific usb-to-serial comm port')
        if not port:
            return StatusResult.Error('TEC not detected!')

        logger.info("The COM port of the TEC is " + port.device)
        return StatusResult.Success()


    def SetTemperature(self, temperature):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: SetTemperature
        # Input: Takes one argument
        #       argument1: Temperature in degree C
        # Description: Sets temperature on Thermal Controller
        #-------------------------------------------------------------------------------------------------------------------
        """
        logger.info("Setting temperature to " + str(temperature))
        methodString = "-m SetTemperature-" + str(temperature)
        result = self.SendCommandAndGetResponse(methodString)
        if result.Status.HasError():
            logger.error("Error in setting Temperature" + result.CmdResult.Output)
            return result.Status

        logger.debug("SetTemperatue function working fine")
        return StatusResult.Success()


    def ReadSVTemperature(self):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: ReadSVTemperature
        # Description: Reads SV temperature on Thermal Controller
        #-------------------------------------------------------------------------------------------------------------------
        """
        logger.info("Read SV temperature from Thermal Controller")
        methodString = "-m ReadSVTemperature-1"
        result = self.SendCommandAndGetResponse(methodString)
        logger.debug("Result contains: " + result)
        if result.Status.HasError():
            logger.error("Error in reading SV Temperature")
            return result.Status

        svTemp = "SVTemp : "
        match = re.findall(svTemp + '(.*?);', result.CmdResult.Output, re.DOTALL)
        if len(match) < 1 :
            return None

        svTemp = match[0]
        logger.debug("ReadSVTemperature function working fine")
        return svTemp


    def ReadPVTemperature(self):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: ReadPVTemperature
        # Description: Reads PV temperature on Thermal Controller
        #-------------------------------------------------------------------------------------------------------------------
        """
        logger.info("Read PV temperature from Thermal Controller")
        methodString = "-m ReadPVTemperature-1"
        result = self.SendCommandAndGetResponse(methodString)
        if result.Status.HasError():
            logger.error("Error in reading PV Temperature")
            return result.Status

        pvTemp = "PVTemp : "
        match = re.findall(pvTemp + '(.*?);', result.CmdResult.Output, re.DOTALL)
        if len(match) < 1 :
            return None

        pvTemp = match[0]
        logger.debug("ReadPVTemperature function working fine")
        return pvTemp


    def PIDControl(self, thermalZone, desiredTemperature, timeout, SVTemp = 25):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: PIDControl
        # Input: Takes 4 arguments
        #       argument1: thermal Zone
        #       argument2: desiredTemperature in degree C
        #       argument3: timeout in seconds.
        #       argument4: SVTemp Temperature in degree C, default value is 25.0C
        # Description: Sets RV temperature, reports device temperature
        #-------------------------------------------------------------------------------------------------------------------
        """
        msTimeout = timeout * 1000
        logger.info("Inside PIDControl function")
        methodString = "-m PIDControl-" + str(thermalZone) + "," + str(desiredTemperature) + "," + str(msTimeout) + "," + str(SVTemp)
        logger.info(methodString)
        result = self.SendCommandAndGetResponse(methodString ,timeout)
        logger.debug(result.CmdResult.Output)
        if result.Status.HasError():
            logger.error("Error in running PIDControl")
            return result.Status

        logger.debug("PIDControl function working fine")
        return StatusResult.Success()


    def ControlTemperature(self, thermalZone, desiredTemperature, timeout, SVTemp = 25):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: ControlTemperature
        # Input: Takes 4 argument
        #       argument1: thermalZone
        #       argument2: desiredTemperature
        #       argument3: timeout in seconds
        #       argument4: SVTemp
        # Description: Controls temperature on device
        #---------------------------------------------------------------------------------------------------
        """
        logger.info("Calling ControlTemperature function")
        methodString = "-m ControlTemperature-" + str(thermalZone) + "," + str(desiredTemperature) + "," + str(timeout*1000) + "," + str(SVTemp)
        #logger.debug(methodString)
        result = self.SendCommandAndGetResponse(methodString, timeout)
        logger.debug(result.CmdResult.Output)
        if result.Status.HasError():
            logger.error("Error in running ControlTemperature")
            return result.Status

        logger.debug("ControlTemperature function working fine")
        return StatusResult.Success()


    def CoolDevice(self, temperature, timeout):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: CoolDevice
        # Input: Takes 2 arguments
        #       argument1: Temperature
        #       argument2: Timeout
        # Description: Cools down temperature on device
        #---------------------------------------------------------------------------------------------------
        """
        logger.info("Calling CoolDevice function")
        methodString = "-m CoolDevice-" + str(temperature) + "," + str(timeout*1000)
        result = self.SendCommandAndGetResponse(methodString, timeout)
        if result.Status.HasError():
            logger.error("Error in running CoolDevice")
            return result.Status

        logger.debug("CoolDevice function working fine")
        return StatusResult.Success()


    def IsTemperatureStable(self, thermalZone):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: IsTemperatureStable
        # Input: Takes 1 argument
        #       argument1: thermalZone
        # Description: Checks temperature on device and reports when it's stable
        #---------------------------------------------------------------------------------------------------
        """
        logger.info("Calling IsTemperatureStable function")
        methodString = "-m IsTemperatureStable-" + str(thermalZone)
        result = self.SendCommandAndGetResponse(methodString)
        if result.Status.HasError():
            logger.error("Error in running IsTemperatureStable")
            return result.Status

        isStable = "isStable : "
        match = re.findall(isStable + '(.*?);', result.CmdResult.Output, re.DOTALL)
        if len(match) < 1 :
            return None

        isStable = match[0]
        logger.debug("IsTemperatureStable function working fine")
        return isStable


    def CheckTSens(self, thermalZone):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: CheckTSens
        # Input: Takes 1 argument
        #       argument1: thermalZone
        # Description: Checks temperature on device and reports when it's stable
        #---------------------------------------------------------------------------------------------------
        """
        logger.info("Calling CheckTSens function")
        methodString = "-m CheckTSens-" + str(thermalZone)
        result = self.SendCommandAndGetResponse(methodString)
        if result.Status.HasError():
            logger.error("Error in running CheckTSens")
            return result.Status

        tSens5Temperature = "TSens5Temperature : "
        match = re.findall(tSens5Temperature + '(.*?);', result.CmdResult.Output, re.DOTALL)
        if len(match) < 1 :
            return None

        tSens5Temperature = match[0]
        logger.debug("CheckTSens function working fine")
        return tSens5Temperature


    def SendCommandAndGetResponse(self, methodStrings, timeout = 30) :
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: SendCommandAndGetResponse
        # Input: Takes 2 arguments
        #       methodStrings: method names followed by their parameters
        #       timeout: default value is 30 seconds
        # Description: Sends execution command to TEC dll
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """
        cptfInterfaceExecutable = CommonApplicationUtilities._ResourcesProgramPath + "CPTF_LibraryInterface\\Qualcomm.CPTF.LibraryInterface.exe"
        dllPath = CommonApplicationUtilities._ResourcesProgramPath + "CPTF_LibraryInterface\\Qualcomm.CPT.Automation.TEC.dll"
        className = 'Qualcomm.CPT.Automation.TEC.ThermalController'

        executionString = cptfInterfaceExecutable + " -a " +  dllPath + " -c " +  className +  " " + " -s " + " " + methodStrings
        logger.debug("Executing Command :" +  executionString)
        result = CommandLine.RunCommand(executionString, timeout)
        logger.debug("Result contains: " + result.CmdResult.Output)
        if result.Status.HasError() :
            logger.error(result.CmdResult.Output)
            result.Status.AddError(result.CmdResult.Output)

        return result

if __name__ == "__main__":
    TECHandler = ThermalControllerHandler()
    result = TECHandler.ControlTemperature(11, 55, 900, 55)
    if result.HasError():
        logger.error(result.ErrorMessage())
