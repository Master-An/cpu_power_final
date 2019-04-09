import re
from ptas_core.command import CommandLine
from ptas_core.status import StatusResult
from ptas_core.ptasLogger import logger
from ptas_core.commonApplicationUtilities import CommonApplicationUtilities

class KratosHandler :
	"""
	#-------------------------------------------------------------------------------------------------------------------
	# Name: KratosHandler
	# Description: Performs Operation on Kratos
	# Sends Commands by passing method names to CPTF Library Interface which calls methdods of the respective class
	#-------------------------------------------------------------------------------------------------------------------
	"""

	kratosPcIpAddress = 0

	def __init__(self, kratosPcIpAddress) :
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: __init__
		# Input: Takes argument :
		# 	kratosPcIpAddress: IP Address of the Kratos PC
		# Description: Constructor that sets Kratos IP Address
		#-------------------------------------------------------------------------------------------------------------------
		"""
		self.kratosPcIpAddress = kratosPcIpAddress


	def SetPowerSupplyOutput(self, enable) :
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: SetPowerSupplyOutput
		# Input: Takes argument :
		# 	enable: true/false to enable or disable Power
		# Description: Power ON/OFF Device by turning on Kratos Power ON/OFF
		#-------------------------------------------------------------------------------------------------------------------
		"""
		logger.info("Setting PowerSupply Output to " +  enable)
		methodString = "-m SetPowerSupplyOutput-" + enable
		result = self.SendCommandAndGetResponse(methodString)
		return result


	def LoadChannelConfiguration(self, configurationFile) :
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: LoadChannelConfiguration
		# Input: Takes argument :
		# 	configurationFile: Path of the cfg file to Load
		# Description: Loads the specified configuration file on Kratos
		#-------------------------------------------------------------------------------------------------------------------
		"""
		logger.info("Loading Channel Configuration : " +  configurationFile)
		methodString = "-m LoadChannelConfiguration-" + configurationFile
		return self.SendCommandAndGetResponse(methodString)

	def SetDefaultOptions(self) :
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: SetDefaultOption
		# Input: Takes No Arguments
		# Description: Sets default of parameters :
		# checkCal : False, ignoreSelfCal : false, ignoreExtCal : True, enforceMaxVBat : False, checkConnectors : True, autoSaveData : True
		#-------------------------------------------------------------------------------------------------------------------
		"""
		logger.info("Setting Default Options - checkCal : False, ignoreSelfCal : false, ignoreExtCal : True, enforceMaxVBat : False, checkConnectors : True, autoSaveData : True")
		methodString = "-m SetOption-false,false,true,false,true,true"
		return self.SendCommandAndGetResponse(methodString)



	def SetUsbConnection(self, enable) :
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: SetUsbConnection
		# Input: Takes argument :
		# 	enable: true / false
		# Description: Enables/Disables the USB Connection on Kratos
		#-------------------------------------------------------------------------------------------------------------------
		"""
		logger.info("Setting USB Connection to : " +  enable)
		methodString = "-m SetUsbConnection-" + enable
		return self.SendCommandAndGetResponse(methodString)


	def ConfigurePowerSupply(self, voltage, currentLimit, ovp) :
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: ConfigurePowerSupply
		# Input: Takes argument :
		# 	voltage: Voltage to be set on Kratos
		#	currentLimit: Current Limit to be set on Kratos
		#	ovp: OVP to be set
		# Description: Sets Voltage, Current & OVP on Kratos
		#-------------------------------------------------------------------------------------------------------------------
		"""
		logger.info( "Configuring Power Supply ")
		methodString = "-m ConfigurePowerSupply-" + voltage + "," + currentLimit + "," + ovp
		return self.SendCommandAndGetResponse(methodString)


	def SetAcquisitionParameters(self, accuracyMode, sampleRate, acquisitionDurationInSeconds, trigger) :
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: SetAcquisitionParameters
		# Input: Takes argument :
		# 	accuracyMode: HIGH_ACCURACY,
		#	sampleRate: sample rate to be set
		#	acquisitionDurationInSeconds: duration in seconds
		#	trigger: Manual, Intermediate,
		# Description: Sets Acquisition Parameters
		#-------------------------------------------------------------------------------------------------------------------
		"""
		logger.info("Setting Acquisition Parameters")
		methodString = "-m SetAcquisitionParameters-" +  accuracyMode + "," + sampleRate + "," + acquisitionDurationInSeconds + "," + trigger;
		return self.SendCommandAndGetResponse(methodString)


	def GetSinglePlotStatistics(self, statisticList) :
		logger.info( "Getting Single Plot Statistics ")
		methodString = "-m GetSinglePlotStatistics-1,1"
		result = self.SendCommandAndGetResponse(methodString)
		if result.Status.HasError() :
			logger.error("Error in Sending Command to get Single Point Statistics")
			return result

		current = "current : "
		voltage = "voltage : "
		match = re.findall ( current + '(.*?);', result.CmdResult.Output, re.DOTALL)
		if len(match) < 1 :
			return StatusResult.Error("Could not read Current Value")

		# logger.info("Current : " + match[0])
		current = match[0]

		match = re.findall ( voltage + '(.*?);', result.CmdResult.Output, re.DOTALL)
		if len(match) < 1 :
			return StatusResult.Error("Could not read Voltage Value")

		# logger.info("Voltage : " + match[0])
		voltage = match[0]

		statisticList[0] = current
		statisticList[1] = voltage

		return StatusResult.Success()

	def GetCurrent(self) :
		logger.info( "Fetching Measured Current")
		methodString = "-m GetSinglePlotStatistics-1,1"
		result = self.SendCommandAndGetResponse(methodString)
		if result.Status.HasError() :
			return None

		current = "current : "
		match = re.findall ( current + '(.*?);', result.CmdResult.Output, re.DOTALL)
		if len(match) < 1 :
			return None

		current = match[0]

		return current;

	def GetVoltage(self) :
		logger.info( "Fetching Measured Voltage")
		methodString = "-m GetSinglePlotStatistics-1,1"
		result = self.SendCommandAndGetResponse(methodString)
		if result.Status.HasError() :
			return None

		voltage = "voltage : "
		match = re.findall ( voltage + '(.*?);', result.CmdResult.Output, re.DOTALL)
		if len(match) < 1 :
			return None

		voltage = match[0]

		return voltage;

	def SetOutputDirectory(self, outputDirPath) :
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: SetOutputDirectory
		# Input: Takes argument :
		# 	outputDirPath: Absolute Logs Directory Path
		# Description: Sets Path on the Kratos PC to save UDAS Files
		#-------------------------------------------------------------------------------------------------------------------
		"""
		logger.info("Setting UDAS Output Directory to : " + outputDirPath)
		methodString = "-m SetOutputDirectory-" + outputDirPath
		return self.SendCommandAndGetResponse(methodString)


	# Acquisition Operations
	def StartAcquisition(self) :
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: StartAcquisition
		# Description: Starts Acquisition on Kratos
		#-------------------------------------------------------------------------------------------------------------------
		"""
		logger.info("Starting Acquisition")
		methodString = "-m StartAcquisition"
		return self.SendCommandAndGetResponse(methodString)


	def SendSwTrigger(self) :
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: SendSwTrigger
		# Description: Send SW Trigger command to start measurement
		#-------------------------------------------------------------------------------------------------------------------
		"""
		logger.info("Sending Software Trigger")
		methodString = "-m SendSwTrigger"
		return self.SendCommandAndGetResponse(methodString)


	def StopAcquisition(self) :
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: StopAcquisition
		# Description: Stops Acquisition if in progress
		#-------------------------------------------------------------------------------------------------------------------
		"""
		logger.info("Stopping Acquisition")
		methodString = "-m StopAcquisition"
		return self.SendCommandAndGetResponse(methodString)


	def GetAcquisitionStatus(self) :
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: GetAcquisitionStatus
		# Description: This methods checks if Acquisition is in progress
		#-------------------------------------------------------------------------------------------------------------------
		"""
		logger.info("Getting Acquisition Status")
		methodString = "-m GetAcquisitionStatus-False"
		result = self.SendCommandAndGetResponse(methodString)
		if result.Status.HasError() :
			return None

		acquisitionStatus = "isAcquiring : "
		match = re.findall ( acquisitionStatus + '(.*?);', result.CmdResult.Output, re.DOTALL)
		if len(match) < 1 :
			return None

		acquisitionStatus = match[0]
		return acquisitionStatus


	def GetExtAcquisitionStatus(self) :
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: GetExtAcquisitionStatus
		# Description: This methods gets the Ext Acquisition
		#-------------------------------------------------------------------------------------------------------------------
		"""
		logger.info("Getting Acquisition Status")
		methodString = "-m GetExtAcquisitionStatus-IDLE"
		result = self.SendCommandAndGetResponse(methodString)
		if result.Status.HasError() :
			return None

		extAcquisitionStatus = "extAcquisitionStatus : "
		match = re.findall ( extAcquisitionStatus + '(.*?);', result.CmdResult.Output, re.DOTALL)
		if len(match) < 1 :
			return None

		extAcquisitionStatus = match[0]
		return extAcquisitionStatus


	def GetAcquisitionError(self) :
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: GetAcquisitionError
		# Description: Get Acquisition Error if encountered
		#-------------------------------------------------------------------------------------------------------------------
		"""
		logger.info("Getting Acquisition Error")
		methodString = "-m GetAcquisitionError"
		return self.SendCommandAndGetResponse(methodString)

	# end Acquisition Operations

	def IsKratosBusy(self):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: IsKratosBusy
		# Description: This method checks if Krtos is Busy
		#-------------------------------------------------------------------------------------------------------------------
		"""
		logger.info("Checking if Kratos is Busy")
		methodString = "-m IsKratosBusy-false"
		result = self.SendCommandAndGetResponse(methodString)
		if result.Status.HasError() :
			return None

		kratosStatus = "isBusy : "
		match = re.findall ( kratosStatus + '(.*?);', result.CmdResult.Output, re.DOTALL)
		if len(match) < 1 :
			return None

		kratosStatus = match[0]
		return kratosStatus


	# Calibration Operations
	def SelfCalibration(self) :
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: SelfCalibration
		# Description: Performs Self Calibration
		#-------------------------------------------------------------------------------------------------------------------
		"""
		logger.info("Performing Self Calibration")
		methodString = "-m SelfCalibration"
		return self.SendCommandAndGetResponse(methodString)

	def DmmMuxCalibration(self) :
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: DmmMuxCalibration
		# Description: Performs Dmm Mux Calibration on Kratos
		#-------------------------------------------------------------------------------------------------------------------
		"""
		logger.info("Performing Dmm Mux Calibration")
		methodString = "-m DmmMuxCalibration"
		return self.SendCommandAndGetResponse(methodString)

	# Calibration Operations
	def CheckCalibrationStatus(self, calibrationStatusList) :
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: CheckCalibrationStatus
		# Description: Checks Status of Self Calibration, DMM Calibration & External Calibration
		#-------------------------------------------------------------------------------------------------------------------
		"""
		logger.info("Checking Calibration")
		methodString = "-m CheckCalibrationStatus-false,false,false"
		result = self.SendCommandAndGetResponse(methodString)
		if result.Status.HasError() :
			logger.error("Error in Sending Command to get Single Point Statistics")
			return result

		selfCalibrationStatus = "selfCalOk : "
		dmmCalibrationStatus = "dmmCalOk : "
		externalCalibrationStatus ="extCalOk : "

		match = re.findall ( selfCalibrationStatus + '(.*?);', result.CmdResult.Output, re.DOTALL)
		if len(match) < 1 :
			return StatusResult.Error("Could not read Self Calibration Status")
		selfCalibrationStatus = match[0]

		match = re.findall ( dmmCalibrationStatus + '(.*?);', result.CmdResult.Output, re.DOTALL)
		if len(match) < 1 :
			return StatusResult.Error("Could not read DMM Calibration Status")
		dmmCalibrationStatus = match[0]

		match = re.findall ( externalCalibrationStatus + '(.*?);', result.CmdResult.Output, re.DOTALL)
		if len(match) < 1 :
			return StatusResult.Error("Could not read External Calibration Status")
		externalCalibrationStatus = match[0]

		calibrationStatusList.append(selfCalibrationStatus)
		calibrationStatusList.append(dmmCalibrationStatus)
		calibrationStatusList.append(externalCalibrationStatus)

		return result

	def SendCommandAndGetResponse(self, methodStrings, timeout = 120) :
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
		#cptfInterfaceExecutable = 'C:\\Automation\\PTAS_Engine\\CPTF_Lib_Interface\\CPTF_LibraryInterface.exe'
		cptfInterfaceExecutable = CommonApplicationUtilities._ResourcesProgramPath + "CPTF_LibraryInterface\\Qualcomm.CPTF.LibraryInterface.exe"
		dllPath = CommonApplicationUtilities._ResourcesProgramPath + "CPTF_LibraryInterface\\Qualcomm.CPT.Automation.Plugins.HW.Kratos.dll"
		className = 'Qualcomm.CPT.Automation.Plugins.HW.Kratos.KratosApi'

		executionString = cptfInterfaceExecutable + " -a " +  dllPath + " -c " +  className + " -m SetupKratos-" + self.kratosPcIpAddress + " " +  methodStrings
		logger.debug("Executing Command :" +  executionString)
		result = CommandLine.RunCommand(executionString, timeout)
		if result.Status.HasError() or 'Error' in result.CmdResult.Output :
			logger.error(result.CmdResult.Output)
			result.Status.AddError(result.CmdResult.Output)

		return result
