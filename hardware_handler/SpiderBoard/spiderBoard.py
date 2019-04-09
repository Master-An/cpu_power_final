# ===========================================================================
#
#  Copyright (c) 2017 Qualcomm Technologies Incorporated.
#  All Rights Reserved.
#  Qualcomm Confidential and Proprietary
#
#  Export of this technology or software is regulated by the U.S. Government.
#  Diversion contrary to U.S. law prohibited.
#
#  All ideas, data and information contained in or disclosed by
#  this document are confidential and proprietary information of
#  Qualcomm Technologies Incorporated and all rights therein are expressly reserved.
#  By accepting this material the recipient agrees that this material
#  and the information contained therein are held in confidence and in
#  trust and will not be used, copied, reproduced in whole or in part,
#  nor its contents revealed in any manner to others without the express
#  written permission of Qualcomm Technologies Incorporated.
#
# ===========================================================================*/

from ptas_core.status import StatusResult
from ptas_core.ptasLogger import logger

from ptas_windows.widowsComPort import WindowsComPort
import serial
import serial.tools.list_ports

import time

class SpiderBoard():

    powerOn = "devicePower on"
    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description: enable the power going to the device and power out connectors.
    #-------------------------------------------------------------------------------------------------------------------
    """

    powerOff = "devicePower off"
    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description: disable the power going to the device and power out connectors.
    #-------------------------------------------------------------------------------------------------------------------
    """

    usbOn = "sync host"
    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description: connect usb device to host.
    #-------------------------------------------------------------------------------------------------------------------
    """

    usbOff = "sync none"
    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description: disconnect usb device from host.
    #-------------------------------------------------------------------------------------------------------------------
    """

    relay1On = "relay set 1 1";
    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description: Enable relay 1
    #-------------------------------------------------------------------------------------------------------------------
    """

    relay1Off = "relay set 1 0";
    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description: disable relay 1
    #-------------------------------------------------------------------------------------------------------------------
    """

    relay2On = "relay set 2 1";
    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description: Enable relay 2
    #-------------------------------------------------------------------------------------------------------------------
    """

    relay2Off = "relay set 2 0";
    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description: disable relay 2
    #-------------------------------------------------------------------------------------------------------------------
    """

    def __init__(self):
        self.portObj = None
        self.serObj = None


    def GetSpiderboardComPort(self):
        """
        -------------------------------------------------------------------------------------------------------------------
         Name: GetSpiderboardComPort
         Input: Takes no argument
         Description: Get the COM port number for the Spiderboard
         Return: StatusResult() object
        -------------------------------------------------------------------------------------------------------------------
        """

        self.portObj = WindowsComPort.GetComPort('teensy')
        if not self.portObj:
            self.portObj = WindowsComPort.GetComPort('spiderboard')
            if not self.portObj:
                self.portObj = WindowsComPort.GetComPort('usb serial')
                if not self.portObj:
                    logger.warning('Spiderboard not detected!')
                    return StatusResult.Error('Error getting Spiderboard COM port!')

        logger.info("The COM port of the Spiderboard is " + self.portObj.device)

        return StatusResult.Success()


    def OpenSpiderboardComPort(self):

        """
        -------------------------------------------------------------------------------------------------------------------
         Name: GetSpiderboardComPort
         Input: Takes no argument
         Description: Open the serial COM port connection to the Spiderboard
         Return: StatusResult() object
        -------------------------------------------------------------------------------------------------------------------
        """

        if not self.portObj:
            logger.error("COM port not specified!")
            return StatusResult.Error("COM port not specified!")

        logger.info('Opening spider board COM port')
        result, self.serObj = WindowsComPort.OpenComPort(self.portObj)
        if result.HasError():
            logger.error('Error in opening spider board COM port')
            logger.error(result.ErrorMessage())
            return result

        return StatusResult.Success()

    def CloseSpiderboardComPort(self):
        """
        -------------------------------------------------------------------------------------------------------------------
         Name: CloseSpiderboardComPort
         Input: Takes no argument
         Description: Close the COM port connection to the Spiderboard.
         Return: StatusResult() object
        -------------------------------------------------------------------------------------------------------------------
        """

        if self.serObj:
            result = WindowsComPort.CloseComPort(self.serObj)
            if result.HasError():
                logger.error('Failed to close Spiderboard COM port:')
                logger.error(result.ErrorMessage())
                return result

        return StatusResult.Success()

    def HandleComPort(self):
        """
        -------------------------------------------------------------------------------------------------------------------
         Name: HandleComPort
         Input: Takes no argument
         Description: Handle the serial COM port connection to the Spiderboard
         Return: StatusResult() object
        -------------------------------------------------------------------------------------------------------------------
        """

        #Search for the Spiderboard COM port
        result = self.GetSpiderboardComPort()
        if result.HasError():
            logger.error(result.ErrorMessage())
            return result

        if self.portObj:
            #Open the port and create the COM port object
            result = self.OpenSpiderboardComPort()
            if result.HasError():
                logger.error('Failed to open Spiderboard COM port')
                logger.error(result.ErrorMessage())
                return result

        return StatusResult.Success()

    def ExecuteCommand(self, command):
        """
        -------------------------------------------------------------------------------------------------------------------
         Name: ExecuteCommand
         Input: Takes one argument
            command : command or data to write on COM port
         Description: Handle the serial COM port connection to the Spiderboard, Writes data and read from COM port
         Return: StatusResult() object
        -------------------------------------------------------------------------------------------------------------------
        """

        logger.debug('Sending command : %s on spider board', command)
        #Make sure the COM port is up and running.
        result = self.HandleComPort()
        if result.HasError():
            logger.error(result.ErrorMessage())
            return result

        result, response = WindowsComPort.WriteReadOnComPort(self.serObj, command + '\r')
        if result.HasError():
            logger.error(result.ErrorMessage())
            return result

        if 'ok' not in response:
            return StatusResult.Error("Error in Spiderboard communication.");

        logger.debug('Recieved response from spider board')
        logger.debug(response)

        result = self.CloseSpiderboardComPort()
        if result.HasError():
            logger.error(result.ErrorMessage())
            return result

        return StatusResult.Success()

    def PowerOn(self):
        """
        -------------------------------------------------------------------------------------------------------------------
         Name: PowerOn
         Input: Takes no argument
         Description: Enables Power
         Return: StatusResult() object
        -------------------------------------------------------------------------------------------------------------------
        """
        logger.info("Spiderboard: Power On")
        result = self.ExecuteCommand(SpiderBoard.powerOn);
        if result.HasError():
            logger.error(result.ErrorMessage())
            return StatusResult.Error("Powering on with the Spiderboard failed!  " + result.ErrorMessage())

        return StatusResult.Success()

    def PowerOff(self):
        """
        -------------------------------------------------------------------------------------------------------------------
         Name: PowerOff
         Input: Takes no argument
         Description: Disables Power
         Return: StatusResult() object
        -------------------------------------------------------------------------------------------------------------------
        """
        logger.info("Spiderboard: Power OFF")
        result = self.ExecuteCommand(SpiderBoard.powerOff);
        if result.HasError():
            logger.error(result.ErrorMessage())
            return StatusResult.Error("Powering off with the Spiderboard failed!  " + result.ErrorMessage())

        return StatusResult.Success()

    def UsbOn(self):
        """
        -------------------------------------------------------------------------------------------------------------------
         Name: UsbOn
         Input: Takes no argument
         Description: Enables USB
         Return: StatusResult() object
        -------------------------------------------------------------------------------------------------------------------
        """
        logger.info("Spiderboard: USB On")
        result = self.ExecuteCommand(SpiderBoard.usbOn);
        if result.HasError():
            logger.error(result.ErrorMessage())
            return StatusResult.Error("USB on with the Spiderboard failed!  " + result.ErrorMessage())

        return StatusResult.Success()

    def UsbOff(self):
        """
        -------------------------------------------------------------------------------------------------------------------
         Name: UsbOff
         Input: Takes no argument
         Description: Disables USB
         Return: StatusResult() object
        -------------------------------------------------------------------------------------------------------------------
        """
        logger.info("Spiderboard: USB OFF")
        result = self.ExecuteCommand(SpiderBoard.usbOff);
        if result.HasError():
            logger.error(result.ErrorMessage())
            return StatusResult.Error("USB off with the Spiderboard failed!  " + result.ErrorMessage())

        return StatusResult.Success()


    def Relay1On(self):
        """
        -------------------------------------------------------------------------------------------------------------------
         Name: Relay1On
         Input: Takes no argument
         Description: Enables Relay1
         Return: StatusResult() object
        -------------------------------------------------------------------------------------------------------------------
        """
        logger.info("Spiderboard: Relay1 On")
        result = self.ExecuteCommand(SpiderBoard.relay1On);
        if result.HasError():
            logger.error(result.ErrorMessage())
            return StatusResult.Error("Relay1 on with the Spiderboard failed!  " + result.ErrorMessage())

        return StatusResult.Success()

    def Relay1Off(self):
        """
        -------------------------------------------------------------------------------------------------------------------
         Name: Relay1Off
         Input: Takes no argument
         Description: Disables Relay1
         Return: StatusResult() object
        -------------------------------------------------------------------------------------------------------------------
        """
        logger.info("Spiderboard: Relay1 Off")
        result = self.ExecuteCommand(SpiderBoard.relay1Off);
        if result.HasError():
            logger.error(result.ErrorMessage())
            return StatusResult.Error("Relay1 off with the Spiderboard failed!  " + result.ErrorMessage())

        return StatusResult.Success()

    def Relay2On(self):
        """
        -------------------------------------------------------------------------------------------------------------------
         Name: Relay2On
         Input: Takes no argument
         Description: Enables Relay2
         Return: StatusResult() object
        -------------------------------------------------------------------------------------------------------------------
        """
        logger.info("Spiderboard: Relay2 On")
        result = self.ExecuteCommand(SpiderBoard.relay2On);
        if result.HasError():
            logger.error(result.ErrorMessage())
            return StatusResult.Error("Relay2 on with the Spiderboard failed!  " + result.ErrorMessage())

        return StatusResult.Success()

    def Relay2Off(self):
        """
        -------------------------------------------------------------------------------------------------------------------
         Name: Relay2Off
         Input: Takes no argument
         Description: Disables Relay2
         Return: StatusResult() object
        -------------------------------------------------------------------------------------------------------------------
        """
        logger.info("Spiderboard: Relay2 Off")
        result = self.ExecuteCommand(SpiderBoard.relay2Off)
        if result.HasError():
            logger.error(result.ErrorMessage())
            return StatusResult.Error("Relay2 off with the Spiderboard failed!  " + result.ErrorMessage())

        return StatusResult.Success()

if __name__ == '__main__':
    spider = SpiderBoard()
    result = spider.PowerOff()
    if result.HasError():
        logger.error(result.ErrorMessage())

    time.sleep(10)

    result = spider.PowerOn()
    if result.HasError():
        logger.error(result.ErrorMessage())
