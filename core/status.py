
	
	
class StatusResult:
	"""
	#-------------------------------------------------------------------------------------------------------------------
	# Name: StatusResult
	# Description: Used to report errors from methods to be propagated up the call stack to the proper reporting call.
    # 	Is successful unless HasError is True.
	# 	Parameterless constructor creates a successful result.
	# 	Can add on errors as they are encountered.
    # 	Can absorb errors of other StatusResults.
	#-------------------------------------------------------------------------------------------------------------------
	"""
	
	Errors = None
	"""
	#-------------------------------------------------------------------------------------------------------------------
	# Name: Errors
	# Description: Support multiple errors for a single method result [error list]
	#-------------------------------------------------------------------------------------------------------------------
	"""
	
	def __init__(self, error = None, error_description = None):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: __init__
		# Input: Takes max three argument, first calling object of StatusResult and optional arguments 'error' takes error string
		# 	and 'error_description' for error description
		# Description: Initializes a StatusResult object upon creation either with 'SUCCESS' or with errors
		# Return: A StatusResult object either with 'SUCCESS' or with errors
		#-------------------------------------------------------------------------------------------------------------------
		"""
		self.Errors = []
		if error is not None:
			if type(error) is not type(''):
				raise Exception("Type Incompatibility : accepts string object")
			error = error.replace('\n', ' ; ')
			if error_description is not None:
				error_description = error_description.replace('\n', ' ; ')
			self.Errors.append(StatusError(Error(error, error_description)))
		
	
	def Success():
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: Success
		# Input: Takes no argument
		# Description: Creates a StatusResult object with 'SUCCESS', no errors
		# Return: A StatusResult object with Success, no errors
		#-------------------------------------------------------------------------------------------------------------------
		"""
		return StatusResult()
	
	
	def Error(error, error_description = None):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: Error
		# Input: Takes max two argument, 'error' takes error string. 'error_description' optional argument for error description
		# Description: Creates a StatusResult object with error message as 'error' and 'error_description'
		# Return: A StatusResult object with error
		#-------------------------------------------------------------------------------------------------------------------	
		"""
		if type(error) is not type(''):
			raise Exception("Type Incompatibility : accepts string object")
		error = error.replace('\n', ' ; ')
		if error_description is not None:
			error_description = error_description.replace('\n', ' ; ')
		return StatusResult(error, error_description)
	
	
	def ErrorMessage(self):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: ErrorMessage
		# Input: Takes one argument, calling object of StatusResult
		# Description: Creates a string of all errors in Errors list of StatusResult object
		# Return: String containing all errors, if no error, returns empty string
		#-------------------------------------------------------------------------------------------------------------------	
		"""
		string_message = ""
		if self.Errors is not None:
			for error in self.Errors:
				string_message += error.ToString() + "\r\n"
		return string_message
	
	def IsSuccess(self):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: IsSuccess
		# Input: Takes one argument, calling object of StatusResult
		# Description: To check if StatusResult object have no error
		# Return: bool value, true if no errors in StatusResult object, else false
		#-------------------------------------------------------------------------------------------------------------------	
		"""
		return not bool(self.ErrorMessage())
		
	
	def HasError(self):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: HasError
		# Input: Takes one argument, calling object of StatusResult
		# Description: To check if StatusResult object have any error
		# Return: bool value, false if no errors in StatusResult object, else true
		#-------------------------------------------------------------------------------------------------------------------	
		"""
		
		return bool(self.ErrorMessage())
	
	
	def ToString(self):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: ToString
		# Input: Takes one argument, calling object of StatusResult
		# Description: Creates a string of all errors in Errors list of StatusResult object
		# Return: String containing all errors, if no error, returns string 'SUCCESS'
		#-------------------------------------------------------------------------------------------------------------------	
		"""
		if len(self.Errors) == 0:
			return 'SUCCESS'
		
		string_message = 'ERROR(s) : '
		for error in self.Errors:
			string_message += error.ToString()
		return string_message
	
	def AddError(self, error, error_description = None):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: AddError
		# Input: Takes max three argument, calling object of StatusResult, 'error' takes error string and 
		# 	'error_description' optional argument for error description
		# Description: Adds an error to calling object of StatusResult
		#-------------------------------------------------------------------------------------------------------------------	
		"""
		if type(error) is not type(''):
				raise Exception("Type Incompatibility : accepts string object")
		error = error.replace('\n', ' ; ')
		if error_description is not None:
			error_description = error_description.replace('\n', ' ; ')		
		self.Errors.append(StatusError(Error(error, error_description)))
	
	
	def AddChildError(self, child_status_result):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: AddChildError
		# Input: Takes max two argument, calling object of StatusResult and another object of StatusResult
		# Description: Adds all error from child_status_result StatusResult object to calling object of StatusResult
		# Return: bool value, true if child_status_result have any error, else false
		#-------------------------------------------------------------------------------------------------------------------	
		"""
		
		if type(child_status_result) is not type(StatusResult()):
				raise Exception("Type Incompatibility : accepts StatusResult() object")
		
		if len(child_status_result.Errors) > 0:
			for child_error in child_status_result.Errors:
				self.Errors.append(child_error)
		
		return child_status_result.HasError()
	
	def InsertParentError(self, error, error_description = None):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: InsertParentError
		# Input: Takes max three argument, calling object of StatusResult, 'error' takes error string and 
		# 	'error_description' optional argument for error description
		# Description: Makes self StatusResult's errors the children errors of a newly specified error. Useful for wrapping several errors around a summary error
		# Return: Calling StatusResult object [self]
		#-------------------------------------------------------------------------------------------------------------------	
		"""
		if type(error) is not type(''):
				raise Exception("Type Incompatibility : accepts string object")
		error = error.replace('\n', ' ; ')
		if error_description is not None:
			error_description = error_description.replace('\n', ' ; ')
		child_errors = self.Errors
		self.Errors = []
		self.Errors.append(StatusError(Error(error, error_description), child_errors))
		return self
		
		
class Error:
	"""
	#-------------------------------------------------------------------------------------------------------------------
	# Name: Error
	# Description: Represents an error message with ErrorMessage and Details. Base class to represent an error for 
	# 	StatusError and StatusResult
	#-------------------------------------------------------------------------------------------------------------------		
	"""
	
	ErrorMessage = None
	Details = None
	
	def __init__(self, error_message, details = None):
		self.ErrorMessage = error_message
		self.Details = details
		
		
	def ToString(self):
		string_message = self.ErrorMessage
		if self.Details is not None:
			string_message += " - " + self.Details
		
		return string_message
		
class StatusError:
	"""
	#-------------------------------------------------------------------------------------------------------------------
	# Name: StatusError
	# Description: Represents an error message. Can have child errors that are more detailed about the parent message.
	#-------------------------------------------------------------------------------------------------------------------		
	"""
	
	ChildErrors = None
	"""
	#-------------------------------------------------------------------------------------------------------------------
	# Name: ChildErrors
	# Description: Child errors that are more detailed about the parent message.
	#-------------------------------------------------------------------------------------------------------------------		
	"""
	
	Error = None
	"""
	#-------------------------------------------------------------------------------------------------------------------
	# Name: Error
	# Description: Error message for this Status Error (not including nested errors)
	#-------------------------------------------------------------------------------------------------------------------		
	"""
	
	def __init__(self, error, child_errors = None):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: __init__
		# Input: Takes max three argument, first calling object of StatusError and optional arguments 'error' takes object 
		# 	of Error() class and 'child_errors' also takes object of Error() class for detailed error description
		# Description: Initializes a StatusError object upon creation
		# Return: A StatusError object with errors
		#-------------------------------------------------------------------------------------------------------------------
		"""
		self.Error = error
		self.ChildErrors = child_errors
		

	def ContainsError(self, error):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: ContainsError
		# Input: Takes two argument, first calling object of StatusError and 'error' a string 
		# Description: Checks if 'error' string is present in calling StatusError object or not
		# Return: bool value, if 'error' string is present in calling StatusError object returns true else false
		#-------------------------------------------------------------------------------------------------------------------
		"""
		
		if self.Error.ErrorMessage is not error:
			return True
			
		if self.ChildErrors is not None:
			for err in self.ChildErrors:
				if (err.ContainsError(error)):
					return True
		return False

	def ToString(self):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: ToString
		# Input: Takes one argument, calling object of StatusError
		# Description: Creates a string of Error and nested ChildErrors StatusError object. Returns 
		# Return: String of this error and nested ChildErrors.
		#-------------------------------------------------------------------------------------------------------------------	
		"""
		string_message = ''
		string_message += self.Error.ToString()
		if self.ChildErrors is not None:
			for child_error in self.ChildErrors:
				string_message += child_error.ToString()
		
		return string_message
