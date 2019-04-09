"""
TBSLTEHandler provides functions which can control the Qualcomm LTE(4G) Test Base Station
by using TBSLTEUtil module.
"""

from ptas_hardware_handler.TBS.TBSLTEUtil import TBSLTEUtil
from ptas_config.testSuiteConfig import TestSuiteConfig
from ptas_core.status import StatusResult
from ptas_core.ptasLogger import logger
import json, sys

class TBSLTEHandler(object):
	"""
	#-------------------------------------------------------------------------------------------------------------------
	# Name: TBSLTEHandler
	# Description: TBSLTEHandler provides functions to control the Qualcomm LTE(4G) Test Base Station
	#   TBSLTEHandler implements functons that can be used to control the Qualcomm
	#   LTE(4G) Test Base Station. it uses TBSLTEUtil which is a wrapper class for the tbslte module
	#-------------------------------------------------------------------------------------------------------------------
	"""
	_tbslte_handle = None
	_host_id = None

	def initialize_handler(self):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: initialize_handler
		# Description: Create TBSLTEUtility handle and connect to Qualcomm LTE(4G) Test Base Station based on key tbslte_host_id
		# Input: Takes no argument
		# Return: StatusResult() object
		#-------------------------------------------------------------------------------------------------------------------
		"""
		self._host_id = TestSuiteConfig.TbsLteHostId
		if self._host_id is None:
			return StatusResult.Error("TbsLteHostId is not provisioned")

		logger.debug(f"TBSLTE Host ID {self._host_id} obtained from input XML key TbsLteHostId")
		return StatusResult.Success()

	def initialize_scenario(self):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: initialize_scenario
		# Description: Initialize instance variables for a single scenario
		# Input: Takes no argument
		# Return: StatusResult() object
		#-------------------------------------------------------------------------------------------------------------------
		"""
		if self._tbslte_handle is None:
			try:
				self._tbslte_handle = TBSLTEUtil(self._host_id)
			except Exception as e:
				logger.error('Failed to initialize TBS module. Please make sure your TBS is running on Octopus 96 or above')
				return StatusResult.Error(f'Failed to create TBSLTEUtil object. Error: {e}')
		return StatusResult.Success()

	def finalize_scenario(self):
		"""Finalize TBSLTE handler."""
		pass

	def finalize_handler(self):
		"""Cleanup TBSLTEHandler states at the end of a test suite or job."""
		pass

	def _get_tbslteutil_handle(self):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: _get_tbslteutil_handle
		# Description: Check whether TBSLTEUtil Handle is avaialble or not
		# Input: Takes no argument
		# Return:
		#   retVal (:class:`bool`): None
		#       1 : get TBSLTEUtil handle successful
		#       0 : get TBSLTEUtil handle failed
		#-------------------------------------------------------------------------------------------------------------------
		"""
		retVal = 0 if self._tbslte_handle is None else 1
		return retVal

	def configuretemplateonltetbs(self, **kwargs):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: configuretemplateonltetbs
		# Description: configure template for ltetbs
		# Input: Takes argument :
		#   template_path (:class:`str`): : Required: The TBS server accessible
		#       template file path. The template will be deployed to the system
		#       regardless of its current state
		# Examples:
		#   configuretemplateonltetbs({template_path: '/prj/qct/octopus/test/templates/Golden/LabOps/Wildcat_v27/BC01_EPN_4cell_20MHz_XOR_CAT11.xml'})
		#       It will configure and load /prj/qct/octopus/test/templates/Golden/LabOps/Wildcat_v27/BC01_EPN_4cell_20MHz_XOR_CAT11.xml
		#       in tbslte station template and run system, make sure system running
		# Return: StatusResult() object
		#-------------------------------------------------------------------------------------------------------------------
		"""
		if not self._get_tbslteutil_handle():
			return StatusResult.Error(f"TBSLTEUtil handle not initialized")

		try:
			template_path = kwargs.get('template_path')
			logger.debug(f"Deploying template {template_path} on TBSLTE station {self._host_id}")
			output = self._tbslte_handle.deploy_template(template_path)
		except Exception as e:
			return StatusResult.Error(f"TBSLTEUtil threw an exception while deploying the template: {e}")

		if not output:
			return StatusResult.Error(f"Failed to deploy template {template_path}")

		logger.info(f"Template {template_path} is deployed successful and LTETBS is running")
		return StatusResult.Success()

	def startsystem(self):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: startsystem
		# Description: Start the system with the previously deployed template
		# Input: Takes no argument
		# Examples:
		#   startsystem()
		#       It will start TBSLTE sytem with the previously deployed template
		#       and check if system is running at end
		# Return: StatusResult() object
		#-------------------------------------------------------------------------------------------------------------------
		"""
		if not self._get_tbslteutil_handle():
			return StatusResult.Error("TBSLTEUtil handle not initialized")

		try:
			output = self._tbslte_handle.start_system()
		except Exception as e:
			return StatusResult.Error(f"TBSLTEUtil threw an exception while starting the system: {e}")

		if output == 0:
			return StatusResult.Error("Failed to start the TBS system")
		elif output == 2:
			logger.debug("TBSLTE system was already running before calling the 'startsystem' function")

		logger.info("TBSLTE system is up and running")
		return StatusResult.Success()

	def stopsystem(self):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: stopsystem
		# Description: Stop the TBSLTE system and check system is in stopped mode at end
		# Input: Takes no argument
		# Examples:
		#   stopsystem()
		#       It will stop TBSLTE sytem
		# Return: StatusResult() object
		#-------------------------------------------------------------------------------------------------------------------
		"""
		if not self._get_tbslteutil_handle():
			return StatusResult.Error("TBSLTEUtil handle not initialized")

		try:
			output = self._tbslte_handle.stop_system()
		except Exception as e:
			return StatusResult.Error(f"TBSLTEUtil threw an exception while stopping the system: {e}")

		if output == 0:
			return StatusResult.Error("Failed to stop the TBS system")
		elif output == 2:
			logger.debug("TBSLTE system was already stopped before calling the 'stopsystem' function")

		logger.info("TBSLTE system is stopped successfully")
		return StatusResult.Success()

	def sendtestabilitycommandonltetbs(self, **kwargs):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: sendtestabilitycommandonltetbs
		# Description: Sends testability command to tbslte station
		# Input: Takes argument :
		#   command (:class:`str`): : Required: The testability command to execute
		# Example:
		#   sendtestabilitycommandonltetbs({command="MME COMMAND GET MME_QUERY_STATE"})
		#       Send testability command MME COMMAND GET MME_QUERY_STATE to
		#       the TBSLTE station
		# Return: StatusResult() object
		#-------------------------------------------------------------------------------------------------------------------
		"""
		if not self._get_tbslteutil_handle():
			return StatusResult.Error("TBSLTEUtil handle not initialized")

		try:
			command = kwargs.get('command')
			output = self._tbslte_handle.send_testability_command(command)
		except Exception as e:
			return StatusResult.Error(f"TBSLTEUtil threw an exception while sending testability command to tbslte station: {e}")

		if output is None:
			return StatusResult.Error('Sending testability command failed, returned None')

		else:
			# TBSLTE returns dict include request_status.
			result_hash = str(command).split(' ')[0] + '_STATUS'
			if (result_hash in output.keys() and 'REQUEST_STATUS' in output[result_hash].keys()
					and output[result_hash]['REQUEST_STATUS']['ERROR'] == 0
					and output[result_hash]['REQUEST_STATUS']['CAUSE'] == 'SUCCESS'):
				logger.info("Successful in sending testability command to TBSLTE system")
			else:
				return StatusResult.Error(f'Sending testability command failed, returned output: {json.dumps(output)}')

		return StatusResult.Success()

	def setpandaioronltetbs(self, **kwargs):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: setpandaioronltetbs
		# Description: Set panda ior on tbslte station all cells all transmitters all receivers
		# Input: Takes argument :
		#   ior (:class:`float`): : Required: PowerDbm value to set at a given
		#       tx/rx index for a given cell
		# Example:
		#   setpandaioronltetbs({ior=-25.5})
		#       Set panda all cells all transmitters all receivers ior to -25.5
		#   setpandaioronltetbs({ior=0.0})
		#       Set panda all cells all transmitters all receivers ior to 0
		# Return: StatusResult() object
		#-------------------------------------------------------------------------------------------------------------------
		"""
		if not self._get_tbslteutil_handle():
			return StatusResult.Error("TBSLTEUtil handle not initialized")

		try:
			ior = kwargs.get('ior')
			output = self._tbslte_handle.set_ior_on_cells(ior)
		except Exception as e:
			return StatusResult.Error(f"TBSLTEUtil threw an exception while setting Ior on cells: {e}")

		if not output:
			return StatusResult.Error(f"Setting Ior to {ior} failed on all cells for all transmitters, all receivers")

		logger.info(f"Setting Ior to {ior} successful on all cells for all transmitters, all receivers")
		return StatusResult.Success()

	def setadditionalcablelost(self, **kwargs):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: setadditionalcablelost
		# Description: Set additional cable loss value for either downlink or uplink
		# Input: Takes argument :
		#   link (:class:`str`): : Required: UPLINK or DOWNLINK
		#   lost (:class:`float`): : Required: Loss in db to write at given antenna indices
		#   antenna (:class:`int`): : Optional: Antenna at which the loss value is read
		#   cell (:class:`int`): 0: Optional: Index of cell of base station
		# Example:
		#   setadditionalcablelost({link:'downlink', lost: 25.0})
		#       Set downlink additional 25db cable lost on cell 0 all antenna
		#   setadditionalcablelost({link : 'uplink', lost: 20.0, antenna : 1, cell:1})
		#       Set uplink additional 20db cable lost on cell 1 antenna 1
		# Return: StatusResult() object
		#-------------------------------------------------------------------------------------------------------------------
		"""
		if not self._get_tbslteutil_handle():
			return StatusResult.Error("TBSLTEUtil handle not initialized")

		try:
			link = kwargs.get('link')
			lost = kwargs.get('lost')
			antenna = kwargs.get('antenna')
			cell = kwargs.get('cell')
			output = self._tbslte_handle.set_cable_loss(
				link, lost, antenna, cell)
		except Exception as e:
			return StatusResult.Error(f"TBSLTEUtil threw an exception while setting cable losses: {e}")

		if not output:
			return StatusResult.Error(f"Setting additional cable losses failed for the input: {json.dumps(kwargs)}")

		logger.info(f"Setting additional cable losses successful for the input: {json.dumps(kwargs)}")
		return StatusResult.Success()


	def sendtbslterawcommand(self, **kwargs):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: sendtbslterawcommand
		# Description: This function allow user access any tbslte module raw function directly
		# Input: Takes argument :
		#   method (:class:`str`) : : Required: An ltetbs function name
		#   inputs (:class:`list`) : : Required: tbslte input parameters
		# Example:
		#   sendtbslterawcommand({command: 'testability_command', inputs: ['MME COMMAND GET MME_QUERY_STATE']})
		#       Send testability_command input : MME COMMAND GET MME_QUERY_STATE' to tbslte station
		#   sendtbslterawcommand({command: 'start_system'})
		#       Send start_system input : None to tbslte station
		# Return: StatusResult() object
		#-------------------------------------------------------------------------------------------------------------------
		"""
		if not self._get_tbslteutil_handle():
			return StatusResult.Error("TBSLTEUtil handle not initialized")

		try:
			method = kwargs.get('method')
			inputs = kwargs.get('inputs')
			output = self._tbslte_handle.tbslte_dispatcher(method, inputs)
		except Exception as e:
			return StatusResult.Error(f"TBSLTEUtil threw an exception while trying to run the command {method} with input {inputs}: {e}")

		if not output:
			return StatusResult.Error(f"Failed to run sendtbslterawcommand for the input: {json.dumps(kwargs)}")

		logger.info(f"Successful in running sendtbslterawcommand for the input: {json.dumps(kwargs)}")
		return StatusResult.Success()


	def sendtbsltecomponentrawcommand(self, **kwargs):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: sendtbsltecomponentrawcommand
		# Description: This function allow user access any tbslte component module raw function directly
		# Input: Takes argument :
		#   component_name (:class:`str`): : Required: Component name
		#       tbslte.BMSC, tbslte.GW, tbslte.MME, tbslte.ENB, tbslte.CELL
		#   componet_index (:class:`str`): : Required: Value can be 'all'
		#       component or component index
		#   method (:class:`str`): None: Required:TBS raw API, please use
		#       go/tbsltedoc https://qct-artifactory.qualcomm.com/artifactory
		#       /tbs-content-browsing-local/sphinx_docs.zip!/sphinx_docs/index.html for API detail
		#   inputs (:class:`list`): : Required: TBS component raw API input
		#       parameters.  It supports multiple parameters
		# Example:
		#   sendtbsltecomponentrawcommand({component_name='CELL', componet_index='all', method='set_mimo_ior',inputs=-50 })
		#       Send set_mimo_ior input -50 in all Panda Cell
		#   sendtbsltecomponentrawcommand({component_name='CELL',componet_index= 'all', method= 'get_mimo_ior'})
		#       Send get_mimo_ior input None in all Panda Cell
		#   sendtbsltecomponentrawcommand({component_name='CELL',componet_index= '1',method= 'get_mimo_ior'})
		#       Send get_mimo_ior input None in all Panda Cell index 1
		# Return: StatusResult() object
		#-------------------------------------------------------------------------------------------------------------------
		"""
		if not self._get_tbslteutil_handle():
			return StatusResult.Error("TBSLTEUtil handle not initialized")

		try:
			component_name = kwargs.get('component_name')
			componet_index = kwargs.get('componet_index')
			method = kwargs.get('method')
			inputs = kwargs.get('inputs')
			output = self._tbslte_handle.tbslte_component_dispatcher(
				component_name, component_index, method, inputs)
		except Exception as e:
			return StatusResult.Error(f"TBSLTEUtil threw an exception during tbslte_component_dispatcher: {e}")

		if not output:
			return StatusResult.Error(f"Failed to run sendtbsltecomponentrawcommand for the input: {json.dumps(kwargs)}")

		logger.info(f"Successful in running sendtbsltecomponentrawcommand for the input: {json.dumps(kwargs)}")
		return StatusResult.Success()

if __name__ == '__main__':
	tbsltehandler = TBSLTEHandler()
	TestSuiteConfig.TbsLteHostId = sys.argv[1]

	result = tbsltehandler.initialize_handler()
	if result.HasError():
		logger.info(f'Error in initialize_handler: {result.ErrorMessage()}')
	result = tbsltehandler.initialize_scenario()
	if result.HasError():
		logger.info(f'Error in initialize_scenario: {result.ErrorMessage()}')
	result = tbsltehandler.stopsystem()
	if result.HasError():
		logger.info(f'Error in stopsystem: {result.ErrorMessage()}')
	result = tbsltehandler.configuretemplateonltetbs(template_path='/prj/qct/octopus/test/4power/Anirudh/LTE7e_band1.xml')
	if result.HasError():
		logger.info(f'Error in configuretemplateonltetbs: {result.ErrorMessage()}')
	result = tbsltehandler.startsystem()
	if result.HasError():
		logger.info(f'Error in startsystem: {result.ErrorMessage()}')

	result = tbsltehandler.sendtestabilitycommandonltetbs(command="MME COMMAND GET MME_QUERY_STATE")
	if result.HasError():
		logger.info(f'Error in sendtestabilitycommandonltetbs: {result.ErrorMessage()}')
	result = tbsltehandler.setpandaioronltetbs(ior=-51.0)
	if result.HasError():
		logger.info(f'Error in setpandaioronltetbs: {result.ErrorMessage()}')
	result = tbsltehandler.setadditionalcablelost(link='uplink', lost=20.0)
	if result.HasError():
		logger.info(f'Error in setadditionalcablelost: {result.ErrorMessage()}')
