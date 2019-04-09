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

from ptas_hardware_handler.kratosApi import KratosHandler

from ptas_core.command import CommandLine

from datetime import datetime
import os, shutil, time, socket
import subprocess
from ptas_core.commonApplicationUtilities import CommonApplicationUtilities

class KratosRecovery:
    """
    #-------------------------------------------------------------------------------------------------------------------
    # Name: KratosRecovery
    # Description: Performs recovery Operation on KRATOS machine
    #     Wrapper class on KratosRecovery to perform operations like RestartKratos, Ping Machine
    #-------------------------------------------------------------------------------------------------------------------
    """

    def __init__(self):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: __init__
        # Description: Initializes KratosRecovery class object
        #-------------------------------------------------------------------------------------------------------------------
        """
        pass

    def RestartKratos(self, IpAddress):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: RestartKratos
        # Input: Takes Argument: IpAddress of the KratosMachine
        # Description: Terminates the Kratos application on the kratosmachine. Batch file running on the machine will restart the kratos app.
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """

        logger.info("Restarting Kratos Application")
        methodString = " -m RestartKratos2-" + str(IpAddress)
        result = self.SendCommandAndGetResponse(methodString)
        if result.Status.HasError() :
            logger.error("Error in Sending Command to RestartKratos")
            return result.Status
        time.sleep(300)
        return StatusResult.Success()

    def PingStatus(self, IpAddress):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: PingStatus
        # Input: IpAddress
        # Description:Pings the machine (with IpAddress provided as an argument)
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """
        result = CommandLine.RunCommand('ping ' + IpAddress, 30)
        if result.Status.HasError() :
            logger.error("Error in pinging host {0} . {1}".format(IpAddress,result.CmdResult.Output))
            return StatusResult.Error("Error in pinging host {0} . {1}".format(IpAddress,result.CmdResult.Output))

        logger.info(result.CmdResult.Output)

        if ('unreachable.' in result.CmdResult.Output) :
            #No route from the local system. Packets sent were never put on the wire.
            return StatusResult.Error('IpAddress is unreacheable. ' + result.CmdResult.Output)

        elif ('Ping request could not find host' in result.CmdResult.Output) :
            return StatusResult.Error('host_not_found. ' + result.CmdResult.Output)

        elif ('Request timed out.' in result.CmdResult.Output) :
            return StatusResult.Error('Connection time out' + result.CmdResult.Output)

        return StatusResult.Success()

    def PingKratos(self, IpAddress, waitTime):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: PingKratos
        # Input: IpAddress, waitTime
        # Description: Try pinging IpAddress for timeout duration = waitTime
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """
        currentTime = time.time()
        timeout = time.time()+ waitTime
        while(currentTime < timeout):
            result = self.PingStatus(IpAddress)
            if not result.HasError() :
                return StatusResult.Success()
            logger.error("Error in pinging Kratos PC. " + result.ErrorMessage() + ". Pinging again..." )
            time.sleep(120)
            currentTime = time.time()
        return StatusResult.Error("Error in pinging Kratos PC : " + str(IpAddress))

    def SendCommandAndGetResponse(self, methodStrings, timeout = 120):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: SendCommandAndGetResponse
        # Input: Takes argument:
        #           methodStrings: methods name followed by their parameters.
        #           For example : -m methodName-param1,param2
        # Description: check If it is Qualcomm Root Build
        # Return: StatusResult() object
        #-------------------------------------------------------------------------------------------------------------------
        """

        cptfInterfaceExecutable = CommonApplicationUtilities._ResourcesProgramPath + "CPTF_LibraryInterface\\Qualcomm.CPTF.LibraryInterface.exe"
        dllPath = CommonApplicationUtilities._ResourcesProgramPath + "CPTF_LibraryInterface\\Qualcomm.CPT.Automation.Plugins.HW.Kratos.dll"
        className = 'Qualcomm.CPT.Automation.Plugins.HW.Kratos.KratosRecovery'
        executionString = cptfInterfaceExecutable + " -a " +  dllPath + " -c " +  className + methodStrings
        logger.debug("Executing Command :" +  executionString)
        result = CommandLine.RunCommand(executionString, timeout)
        return result

if __name__ == "__main__":
    pass

