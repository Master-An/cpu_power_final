import re
from core.command import CommandLine
from ptas_core.status import StatusResult
from core.ptasLogger import logger
from core.commonApplicationUtilities import CommonApplicationUtilities
from lib.adb import Adb

class QcUsbSwitch :
    """
    #-------------------------------------------------------------------------------------------------------------------
    # Name: QcUsbSwitch
    # Description: Performs Operation on USB switcher
    # Sends Commands by passing method names to CPTF Library Interface which calls methdods of the respective class
    #-------------------------------------------------------------------------------------------------------------------    
    """
    @staticmethod
    def SetUsbConnection(enable) :
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: SetUsbConnection
        # Input: Takes argument :
        #     enable: true / false
        # Description: Enables/Disables the USB Connection on Kratos
        #-------------------------------------------------------------------------------------------------------------------    
        """
        logger.info("Setting USB Connection to : " +  enable)
        methodString = enable
        while(True):
            result = QcUsbSwitch.SendCommandAndGetResponse(methodString)
            if not result.Status.HasError():
                break
        return result

    @staticmethod
    def SendCommandAndGetResponse(methodStrings, timeout = 30) :
        executionString = CommonApplicationUtilities._ToolsPath + "QcUSBSwitchTool\\QcUSBSwitchTool.exe " + methodStrings
 
        logger.debug("Executing Command :" +  executionString)
        result = CommandLine.RunCommand(executionString, timeout)
        if (result.Status.HasError() or (not 'Success' in result.CmdResult.Output)) :
            logger.error(result.CmdResult.Output)
            result.Status.AddError(result.CmdResult.Output)
                        
        return result

if __name__ == '__main__':
    for i in range(10):
        QcUsbSwitch.SetUsbConnection('usb_on')
        result = Adb.IsDeviceDetected()
        logger.info("first time: " + str(result.IsSuccess()))
        if result.HasError():
            logger.info("set usb on again")
            QcUsbSwitch.SetUsbConnection('usb_on')
            result = Adb.IsDeviceDetected()
            logger.info("second time: " + str(result.IsSuccess()))