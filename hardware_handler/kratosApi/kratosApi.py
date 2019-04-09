from socket import *
import re, time, threading, datetime
from ptas_core.command import CommandLine
from ptas_core.status import StatusResult
from ptas_core.ptasLogger import logger
from ptas_core.commonApplicationUtilities import CommonApplicationUtilities
from ptas_hardware_handler.kratosApi.kratosConstants import KratosConstants

class KratosHandler :
	"""
	#-------------------------------------------------------------------------------------------------------------------
	# Name: KratosHandler
	# Description: Performs Operation on Kratos
	# Sends Commands by passing method names to CPTF Library Interface which calls methdods of the respective class
	#-------------------------------------------------------------------------------------------------------------------
	"""

	kratosPcIpAddress = 0
	socket = None
	defaultKratosPort = 6537
	bufferSize = 1024
	KratosSocketTimeout = 30
	LastApiResponse = None
	LastKratosResponse = None

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
		setOut = "ON" if (enable == 'true') else "OFF"
		commandToRun = "SetPowerSupplyOutput(1," + setOut + ")"
		return self.SendCommandAndGetResponse(commandToRun)

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
		commandToRun = "LoadChannelConfiguration(" + configurationFile + ")"
		return self.SendCommandAndGetResponse(commandToRun)

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
		commandToRun = "SetOptions(CHK_CAL=OFF,IGNORE_SELF_CAL=OFF,IGNORE_EXT_CAL=ON,ENFORCE_MAX_VBAT=OFF,CHK_CONNECTORS=ON,AUTOSAVE=ON)"
		return self.SendCommandAndGetResponse(commandToRun)


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
		setOut = "ON" if (enable == 'true') else "OFF"
		commandToRun = "SetUsbConnection(1," + setOut + ")"
		return self.SendCommandAndGetResponse(commandToRun, False)


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
		commandToRun = f"ConfigurePowerSupply(1,{voltage},{currentLimit},{ovp})"
		return self.SendCommandAndGetResponse(commandToRun)


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
		commandToRun = f"SetAcquisitionParameters({accuracyMode},{sampleRate},{acquisitionDurationInSeconds},{trigger})"
		return self.SendCommandAndGetResponse(commandToRun)


	def GetSinglePlotStatistics(self, statisticList) :
		logger.info( "Getting Single Plot Statistics ")

		for channel in ['CURRENT', 'VOLTAGE']:
			commandToRun = f"GetSinglePlotStatistics(0,{channel})"
			result = self.SendCommandAndGetResponse(commandToRun)
			if result.HasError() :
				logger.error(f"Error in reading battery {channel}")
				return result

			dataFields = None
			if self.LastApiResponse:
				dataFields = self.LastApiResponse.split(",")

			if (dataFields == None or len(dataFields) < 3):
				return StatusResult.Error(f"Kratos: Failed to parse response while reading battery {channel} value. Response: {self.LastApiResponse}")

			if channel == 'CURRENT':
				statisticList[0] = dataFields[2]
			else:
				statisticList[1] = dataFields[2]

		return StatusResult.Success()

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
		commandToRun = f"SetOutputDirectory({outputDirPath})"
		return self.SendCommandAndGetResponse(commandToRun)


	# Acquisition Operations
	def StartAcquisition(self) :
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: StartAcquisition
		# Description: Starts Acquisition on Kratos
		#-------------------------------------------------------------------------------------------------------------------
		"""
		logger.info("Starting Acquisition")
		commandToRun = "StartAcquisition()"
		result = self.SendCommandAndGetResponse(commandToRun, False)
		if (result.HasError()):
			return result

		status = KratosConstants.ExtAcquisitionStatus.UNKNOWN
		logger.info("Kratos: Waiting For Acquisition To Be Ready")
		# Wait for up to 60seconds for the waiting for trigger screen
		startTime = datetime.datetime.now()
		while (status != KratosConstants.ExtAcquisitionStatus.WAITING_FOR_TRIGGER and (datetime.datetime.now() - startTime).seconds < 60):
			time.sleep(2)
			status = self.GetExtAcquisitionStatus()

		if (status != KratosConstants.ExtAcquisitionStatus.WAITING_FOR_TRIGGER):
			return StatusResult.Error("Kratos: Acquisition Is Not Ready. Check That A Measurement Can Be Performed Manually")

		return StatusResult.Success()

	def SendSwTrigger(self) :
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: SendSwTrigger
		# Description: Send SW Trigger command to start measurement
		#-------------------------------------------------------------------------------------------------------------------
		"""
		logger.info("Sending Software Trigger")
		commandToRun = "SendSWTrigger()"
		result = self.SendCommandAndGetResponse(commandToRun, False)
		if result.HasError():
			return result

		result, isAcquiring = self.GetAcquisitionStatus()
		if result.HasError():
			return result

		if not isAcquiring:
			return StatusResult.Error("Kratos: Failed To Start Acquisition. Check To See If Measurements Can Be Performed Manually")

		return StatusResult.Success()

	def StopAcquisition(self) :
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: StopAcquisition
		# Description: Stops Acquisition if in progress
		#-------------------------------------------------------------------------------------------------------------------
		"""
		logger.info("Stopping Acquisition")
		commandToRun = "StopAcquisition()"
		result = self.SendCommandAndGetResponse(commandToRun, False)
		if result.HasError():
			return result

		status = KratosConstants.ExtAcquisitionStatus.UNKNOWN
		# Wait for up to 300 seconds for the waiting for trigger screen

		startTime = datetime.datetime.now()
		while (status != KratosConstants.ExtAcquisitionStatus.IDLE and (datetime.datetime.now() - startTime).seconds < 300):
			time.sleep(2)
			status = self.GetExtAcquisitionStatus()

		if (status != KratosConstants.ExtAcquisitionStatus.IDLE):
			return StatusResult.Error("Kratos: Could Not Stop Acquisition. Check That A Measurement Can Be Performed And Stopped Manually")

		time.sleep(5)
		# Use this command to force Kratos to wait until data is saved
		statisticsList = [1,2]
		result = self.GetSinglePlotStatistics(statisticsList)
		if result.HasError():
			logger.warning("Failed To Autodetect Kratos Save Duration. Waiting 10 Seconds...")
			time.sleep(10)

		return StatusResult.Success()

	def GetAcquisitionStatus(self) :
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: GetAcquisitionStatus
		# Description: This methods checks if Acquisition is in progress
		#-------------------------------------------------------------------------------------------------------------------
		"""
		# logger.info("Getting Acquisition Status")
		commandToRun = "GetAcquisitionStatus()"
		result = self.SendCommandAndGetResponse(commandToRun, False)
		if (result.HasError()):
			return (result, False)

		isAcquiring =  True if (self.LastApiResponse == "ACQUISITION IN PROGRESS") else False

		return (StatusResult.Success(), isAcquiring)


	def GetExtAcquisitionStatus(self) :
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: GetExtAcquisitionStatus
		# Description: This methods gets the Ext Acquisition
		#-------------------------------------------------------------------------------------------------------------------
		"""
		# logger.info("Getting Acquisition Status")
		extAcquisitionStatus = KratosConstants.ExtAcquisitionStatus.UNKNOWN
		commandToRun = "GetExtAcquisitionStatus()"
		result = self.SendCommandAndGetResponse(commandToRun, False)
		if result.HasError() :
			return extAcquisitionStatus

		extAcquisitionStatus = KratosConstants.ExtAcquisitionStatus[self.LastApiResponse.replace(' ', '_')]

		return extAcquisitionStatus


	def GetAcquisitionError(self) :
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: GetAcquisitionError
		# Description: Get Acquisition Error if encountered
		#-------------------------------------------------------------------------------------------------------------------
		"""
		logger.info("Getting Acquisition Error")
		commandToRun = "GetAcquisitionError()"
		result = self.SendCommandAndGetResponse(commandToRun, False)
		if result.HasError():
			return result

		outputs = None
		if self.LastApiResponse:
			outputs = self.LastApiResponse.split(",")

		if (outputs == None or len(outputs) == 0):
			return StatusResult.Error(f"Incorrect response from Kratos while checking for Acquisition errors. Response: {self.LastApiResponse}")

		if (outputs[0] != "NO ERROR"):
			return StatusResult.Error(f"Error response from Kratos while checking for Acquisition errors. Response: {self.LastApiResponse}")

		return StatusResult.Success()

	# end Acquisition Operations

	def IsKratosBusy(self):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: IsKratosBusy
		# Description: This method checks if Krtos is Busy
		#-------------------------------------------------------------------------------------------------------------------
		"""
		logger.info("Checking if Kratos is Busy")
		commandToRun = "GetHWState()"
		result = self.SendCommandAndGetResponse(commandToRun, False)
		if result.HasError() :
			return None

		isBusy = False if (self.LastApiResponse == "READY") else True
		return isBusy


	# Calibration Operations
	def SelfCalibration(self) :
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: SelfCalibration
		# Description: Performs Self Calibration
		#-------------------------------------------------------------------------------------------------------------------
		"""
		logger.info("Performing Self Calibration")
		commandToRun = "SelfCalibration()"
		return self.SendCommandAndGetResponse(commandToRun, False)

	def DmmMuxCalibration(self) :
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: DmmMuxCalibration
		# Description: Performs Dmm Mux Calibration on Kratos
		#-------------------------------------------------------------------------------------------------------------------
		"""
		logger.info("Performing Dmm Mux Calibration")
		commandToRun = "DmmMuxCalibration()"
		return self.SendCommandAndGetResponse(commandToRun, False)

	# Calibration Operations
	def CheckCalibrationStatus(self, calibrationStatusList) :
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: CheckCalibrationStatus
		# Description: Checks Status of Self Calibration, DMM Calibration & External Calibration
		#-------------------------------------------------------------------------------------------------------------------
		"""
		logger.info("Checking Calibration")
		commandToRun = "CheckCalibrationStatus()"
		result = self.SendCommandAndGetResponse(commandToRun)
		if result.HasError() :
			logger.error("Kratos: Error in sending command to check the calibration status")
			return result

		response = self.LastApiResponse.split(',')
		if (response == None or len(response) != 3):
			return StatusResult.Error(f"Incorrect response from Kratos while checking calibration status. Response: {self.LastApiResponse}")

		logger.debug(f"External Calibration Status : {response[0]}")
		logger.debug(f"Self     Calibration Status : {response[1]}")
		logger.debug(f"DMM      Calibration Status : {response[2]}")

		if "PASS" not in response[0]:
			logger.warning("External calibration is expired, please contact the IPS team to do the external calibration")

		selfCalibrationStatus = 'True' if ("PASS" in response[1]) else 'False'
		dmmCalibrationStatus = 'True' if ("PASS" in response[2]) else 'False'
		externalCalibrationStatus = 'True' if ("PASS" in response[0]) else 'False'

		calibrationStatusList.append(selfCalibrationStatus)
		calibrationStatusList.append(dmmCalibrationStatus)
		calibrationStatusList.append(externalCalibrationStatus)

		return result

	def SendCommandAndGetResponse(self, commandToRun, waitForIdle = True) :
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: SendCommandAndGetResponse
		# Input: Takes argument :
		# 	commandToRun: The UDAS API to be sent
		# Description: Wrapper Function that communicates with the UDAS s/w and then wait for UDAS to go IDLE
		# Return: StatusResult() object
		#-------------------------------------------------------------------------------------------------------------------
		"""
		result = self.SendApiAndGetResponse(commandToRun)
		if result.HasError():
			return result

		if waitForIdle:
			startTime = datetime.datetime.now()
			while ((datetime.datetime.now() - startTime).seconds < 60):
				result = self.SendApiAndGetResponse("GetHWState()", False)
				if result.HasError() :
					time.sleep(3)
					continue

				isBusy = False if (self.LastKratosResponse == "READY") else True
				if not isBusy:
					return StatusResult.Success()
				time.sleep(3)

			logger.error("KRATOS failed to return to IDLE state in 1 minute")

		return StatusResult.Success()


	def SendApiAndGetResponse(self, commandToRun, updateLastResponse = True) :
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: SendApiAndGetResponse
		# Input: Takes argument :
		# 	commandToRun: The UDAS API to be sent
		# Description: Function that sends the API to the UDAS socket of the intented Kratos and receives the response
		# Return: StatusResult() object
		#-------------------------------------------------------------------------------------------------------------------
		"""
		noRetryCommandList = ["SetUsbConnection(1,OFF)", "SendSWTrigger()"]
		noRetry = True if (commandToRun in noRetryCommandList) else False
		result = StatusResult.Success()
		retry = True
		retryCount = 0
		response = None
		self.LastKratosResponse = None
		if updateLastResponse:
			self.LastApiResponse = None
		while retry:
			try:
				retryCount += 1
				if result.HasError():
					logger.error(result.ErrorMessage())
					if (retryCount > 3):
						# if 3rd retry, then exit
						return result

				result = StatusResult.Success()
				response = None
				commandToRun += "\r\n"

				startTime = datetime.datetime.now()
				while True:
					try:
						self.socket = socket(AF_INET, SOCK_STREAM)          # Creating a TCP/IP socket
						self.socket.connect((self.kratosPcIpAddress, self.defaultKratosPort))
						self.socket.settimeout(self.KratosSocketTimeout)
					except Exception as e:
						if (noRetry or (datetime.datetime.now() - startTime).seconds > 120):
							retryCount = 3
							raise Exception(f"Couldn't connect To UDAS, Exception Occurred: \n{e}")
						else:
							logger.info('Trying to re-connect to UDAS socket, after a failed attempt')
							time.sleep(2)
					else:
						break

				try:
					totalsent = 0
					byteArray = bytearray()
					byteArray.extend(commandToRun.encode('utf-8'))
					while totalsent < len(byteArray):
						sent = self.socket.send(byteArray[totalsent:])
						if sent == 0:
							raise RuntimeError("socket connection broken")
						totalsent = totalsent + sent
				except Exception as e:
					raise Exception(f"Failed to send command to UDAS, Exception Occurred: \n{e}")

				try:
					chunks = []
					while True:
						chunk = self.socket.recv(self.bufferSize)
						data = chunk.decode("utf-8")
						chunks.append(data)
						if '\n' in data: break

					response = ''.join(chunks).strip()
					if (response == None):
						result = StatusResult.Error(f"Failed to send UDAS command.  Response Is null.  Command: {commandToRun}")
					elif ("ERROR" in response and "NO ERROR" not in response):
						result = StatusResult.Error(f"Failed to Send UDAS Command.  Command: {commandToRun}, UDAS Response: {response}")

				except Exception as e:
					raise Exception(f"Failed to connect to UDAS socket for command response, Command: {commandToRun}, Exception Occurred: {e}")
			except Exception as e:
				result = StatusResult.Error(str(e))
			else:
				#if we reached here, then all actions completed successfully
				retry = False
			finally:
				if noRetry:
					retryCount = 3
				if (self.socket != None):
					self.socket.shutdown(SHUT_RDWR)
					self.socket.close()
					self.socket = None

		self.LastKratosResponse = response
		if updateLastResponse:
			self.LastApiResponse = response

		return result

if __name__ == "__main__":
	pass
