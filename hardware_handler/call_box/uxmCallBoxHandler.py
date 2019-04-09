import os, re, shutil, glob, time, subprocess
from ptas_core.command import CommandLine
from ptas_core.status import StatusResult
from ptas_core.ptasLogger import logger
from ptas_config.testCaseConfig import TestCaseConfig
from ptas_config.testSuiteConfig import TestSuiteConfig
from ptas_core.commonApplicationUtilities import CommonApplicationUtilities
from ptas_utility.cptfLibraryInterface import CptfLibraryInterface

class UxmCallBoxHandler(object):
	"""
#-------------------------------------------------------------------------------------------------------------------
# Name: UxmCallBoxHandler
# Description: Performs Operation on UXM Call Box
# Sends Commands by passing method names to CPTF Library Interface which calls methods of the respective class.
# Performs operations like :
# DeRegisterUeFromIms, RecallAgilentUXMRegister, ActivateBSECell
#-------------------------------------------------------------------------------------------------------------------	
"""
	protocolType = "HiSlip"
	def __init__(self) :
		"""
	#-------------------------------------------------------------------------------------------------------------------
	# Name: __init__
	# Input: Takes argument :
	# 	None
	# Description: Constructor that sets QTF Parameters 
	#-------------------------------------------------------------------------------------------------------------------	
	"""
		self.address = TestSuiteConfig.CallBoxAddress


	def DeRegisterUeFromIms(self) :
			try :
					logger.info("De Registering UE From IMS")
					result = self.SendCommandAndGetResponse("-m DeRegisterUeFromIms-" + self.address + "," + UxmCallBoxHandler.protocolType)
					if result.Status.HasError() :
							return result
					'''
							Logic to check if the operation performed successfully
							It could be parsing the obtained console log
					'''
			except Exception as ex :
					return StatusResult.Error("Failed To De Register UE From IMS : " + str(ex))

			return StatusResult.Success()


	def RecallAgilentUXMRegister(self, register) :
			try :
					logger.info("Recalling Agilent UXM Register  : " + register)
					print("Recalling Agilent UXM Register  : " + register)
					result = self.SendCommandAndGetResponse("-m RecallAgilentUXMRegister-" + self.address + "," + register + "," + UxmCallBoxHandler.protocolType)
					if result.Status.HasError() :
							return result
					'''
							Logic to check if the operation performed is successfull
							It could be parsing the obtained console log
					'''					
			except Exception as ex :
					return StatusResult.Error("Failed To De Register UE From IMS : " + str(ex))

			return StatusResult.Success()


	def ActivateBSECell(self) :
			try :
					logger.info("Activating BSE Cell")
					result = self.SendCommandAndGetResponse("-m ActivateBSECell-" + self.address + "," + UxmCallBoxHandler.protocolType)
					if result.Status.HasError() :
							return result
					'''
							Logic to check if the operation performed is successfull
							It could be parsing the obtained console log
					'''
			except Exception as ex :
					return StatusResult.Error("Failed To De Register UE From IMS : " + str(ex))

			return StatusResult.Success()



	def SendCommandAndGetResponse(self, methodStrings, timeout = 30) :
			"""
	#-------------------------------------------------------------------------------------------------------------------
	# Name: SendCommandAndGetResponse
	# Input: Takes argument :
	# 	methodStrings: methods name followed by their parameters.
	#	For example : -m methodName-param1,param2
	# Description: check If it is Qualcomm Root Build
	# Return: StatusResult() object
	#-------------------------------------------------------------------------------------------------------------------	
	"""                
			#dllPath = CommonApplicationUtilities._ResourcesProgramPath + "CPTF_VISA_Dll\\Qualcomm.CPT.Automation.VISA.dll"
			dllPath = "C:\Automation\PTAS\Plasma\Engine\Resources\Programs\CPTF_VISA_Dll\Qualcomm.CPT.Automation.VISA.dll"
			className = 'Qualcomm.CPT.Automation.VISA.CallboxCommands'
			return CptfLibraryInterface.SendCommandAndGetResponse(dllPath,className,methodStrings)




if __name__ == "__main__" :
        #test = UxmCallBoxHandler("10.242.49.14")
        #test.RecallAgilentUXMRegister("sdm630_3gpp.xml")
        #test.ActivateBSECell()
        #test.DeRegisterUeFromIms()
        pass 
