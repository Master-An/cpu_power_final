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

'''***********************************************************************************************************************
**  USAGE INFORMATION:
**  Use the below parameters in your test case script to pass arguments to the functions in this class:
**  1. enbSystem = TestSuiteConfig.TbsLteHostId - Value to be provided is int - For Ex.: 8435
**  2. userName = TestSuiteConfig.TBSUserName
**  3. password = TestSuiteConfig.TBSPassword
**  4. port = TestSuiteConfig.TBSPort
**  5. throughput = TestCaseConfig.TBSThroughput
**  6. duration = TestSuiteConfig.TBSiPerfDuration
************************************************************************************************************************'''
from ptas_core.command import CommandLine
from ptas_core.status import StatusResult
from ptas_core.ptasLogger import logger
from ptas_core.commonApplicationUtilities import CommonApplicationUtilities
from threading import Thread
import os, os.path
import time, re


class TbsIPerfActions():
    """
    #-------------------------------------------------------------------------------------------------------------------
    # Name: TbsIPerfActions
    # Description: Python class to execute iPerf related commands on TBS
    #-------------------------------------------------------------------------------------------------------------------
    """

    plinkPath = CommonApplicationUtilities._ToolsPath + "\\Plink\\plink.exe"
    plinkstr = ""

    def SetupPlinkString(enbSystem, userName, password):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: SetupPlinkString
        # Input: Takes three arguments
        #       argument1: enbSystem
        #       argument2: userName
        #       argument3: password
        # Description: Function used to construct the SSH login command to TBS
        # Return: StatusResult result
        #-------------------------------------------------------------------------------------------------------------------
        """
        hostname = "qct-" + str(enbSystem) + "-enbu-0"
        TbsIPerfActions.plinkstr = TbsIPerfActions.plinkPath + " -ssh " + str(userName) + "@" + str(hostname) +" -pw " + str(password) + " "
        logger.info("Plinkstr is: " + str(TbsIPerfActions.plinkstr))
        logger.info("TBS: Connecting User " + str(userName) + " To TBS via SSH To " + str(hostname))

    def SetupServerIperf(port, throughput):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: SetupServerIperf
        # Input: Takes two arguments
        #       argument1: port
        #       argument2: throughput
        # Description: Function used start iPerf Server
        # Return: StatusResult result
        #-------------------------------------------------------------------------------------------------------------------
        """
        logger.info("Calling SetupServerIperf function")
        logger.info("TBS: Starting Iperf Server")
        command = TbsIPerfActions.plinkstr + "iperf -s -p " + str(port) + " -u -i2 -w " + str(throughput) + "M "
        logger.info("TBS: " + str(command))
        try:
            logger.info("Creating iPerfServer Thread")
            iPerfServerThread = Thread(target = CommandLine.RunCommand, args=[command,15])
            logger.info("Staring iPerfServer Thread")
            iPerfServerThread.start()
        except Exception as e:
            logger.error("Exception raised from SetupServerIperf function: " + str(e))
            return StatusResult.Error("Exception raised from SetupServerIperf function: " + str(e))

        time.sleep(10)
        logger.info("SetupServerIperf function worked fine")
        return StatusResult.Success()

    def StartClientIperf(port, throughput, duration):
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: StartClientIperf
        # Input: Takes five arguments
        #       argument1: port
        #       argument2: throughput
        #       argument3: duration - time in seconds to run iPerf
        # Description: Function used to start iPerf client
        # Return: StatusResult result
        #-------------------------------------------------------------------------------------------------------------------
        """
        logger.info("Calling StartClientIperf function")
        ueIpAddress = TbsIPerfActions.GetUeIpAddress()
        if ueIpAddress == "":
            logger.error("Error in getting UE IP Address")
            return logger.error("Failed to detect UE IP Address")

        logger.info("TBS: Starting Iperf Client")
        command = TbsIPerfActions.plinkstr + "miperf -c " + str(ueIpAddress) + " -p " + str(port) + " -u -b " + str(throughput) + "M -t " + str(duration) + " -i2 -w16M"
        logger.info("TBS: " + str(command))
        try:
            logger.info("Starting iPerfClientThread")
            iPerfClientThread = Thread(target = CommandLine.RunCommand, args=[command,15])
            iPerfClientThread.start()
        except Exception as e:
            logger.error("Exception raised from StartClientIperf function: " + str(e))
            return StatusResult.Error("Exception raised from StartClientIperf function: " + str(e))

        time.sleep(10)
        logger.info("SetupClientIperf function worked fine")
        return StatusResult.Success()

    def StopServerIperf():
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: StopServerIperf
        # Input: Takes no arguments
        # Description: Function used to Stop iPerf Server
        # Return: StatusResult result
        #-------------------------------------------------------------------------------------------------------------------
        """
        logger.info("Calling StopServerIperf function")
        logger.info("TBS: Stopping Iperf Server")
        command = TbsIPerfActions.plinkstr + "pkill iperf"
        logger.info("TBS: " + str(command))
        result = CommandLine.RunCommand(command, 20)
        if result.Status.HasError():
            logger.error("Unable to kill iperf")
            return StatusResult.Error("Unable to kill iperf")

        logger.info("StopServerIperf function worked fine")
        return StatusResult.Success()

    def StopClientIperf():
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: StopClientIperf
        # Input: Takes no arguments
        # Description: Function used to Stop iPerf Client
        # Return: StatusResult result
        #-------------------------------------------------------------------------------------------------------------------
        """
        logger.info("Calling StopClientIperf function")
        logger.info("TBS: Stopping Iperf Client")
        command = TbsIPerfActions.plinkstr + "pkill miperf"
        logger.info("TBS: " + str(command))
        result = CommandLine.RunCommand(command,10)
        if result.Status.HasError():
            logger.error("Unable to kill miperf")
            return StatusResult.Error("Unable to kill miperf")

        logger.info("StopClientIperf function worked fine")
        return StatusResult.Success()

    def GetUeIpAddress():
        """
        #-------------------------------------------------------------------------------------------------------------------
        # Name: GetUeIpAddress
        # Input: Takes no arguments
        # Description: Function used to get UE IP Address
        # Return: UE IP Address
        #-------------------------------------------------------------------------------------------------------------------
        """
        logger.info("Calling GetUeIpAddress function")
        logger.info("TBS: Detecting MME State")
        str1 = "/opt/lte/bin/appTestability.py -s localhost -p 15004 \\\"MME COMMAND GET MME_QUERY_STATE\\\""
        command = TbsTestabilityActions.plinkstr + "\""+ str1 + "\""
        logger.debug("Command is: " + str(command))
        result = CommandLine.RunCommand(command, 15)
        matched = 0
        OutputLines = str(result.CmdResult.OutputLines)
        OutputLines = OutputLines.split("\\n")
        logger.info("OutputLines: " + str(OutputLines) + "\n")

        for line in OutputLines:
            #logger.debug("Line contains: " + str(line))

            if matched == 1:
                if "IPV4_ADDRESS" in line:
                    match = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', line).group()
                    if "10.1.1" in match:
                        ipAddress = match
                        logger.info("TBS: UE IP Address: " + str(ipAddress))
                        return ipAddress

                        if ipAddress == "":
                            logger.error("Failed to detect UE IP Address")
                            return None
            else:
                match = re.search(r"\"IP_TYPE\" : \"IPV4\",",line)
                if match != None:
                    matched = 1
                    logger.debug("Line contains: " + str(line))


if __name__ == '__main__':
    result = TbsIPerfActions.SetupPlinkString("8435", "root", "0ctag0n5")

    #result = TbsIPerfActions.SetupServerIperf(9000, 90)
    #if result.HasError():
        #logger.error("Error in setting up server iperf")

    #result = TbsIPerfActions.GetUeIpAddress()
    #logger.info(result)
    #if result == None:
        #logger.error("Error in getting UE IP Address")

    #result = TbsIPerfActions.StartClientIperf(9000, 90, 60)
    #if result.HasError():
        #logger.error("Error in starting client iperf")

    #result = TbsIPerfActions.StopServerIperf()
    #if result.HasError():
        #logger.error("Error in stopping server iperf")

    #result = TbsIPerfActions.StopClientIperf()
    #if result.HasError():
        #logger.error("Error in stopping client iperf")
