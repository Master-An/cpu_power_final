import subprocess, sys
from core.status import StatusResult
from core.ptasLogger import logger
from datetime import datetime

class CommandLine(object):
	"""
	#-------------------------------------------------------------------------------------------------------------------
	# Name: CommandLine
	# Description: A simple wrapper for Python's subprocess module to achieve executing commands
	# 	An object oriented interface, used to execute commands with customizable defaults
	#-------------------------------------------------------------------------------------------------------------------
	"""
	def RunCommandWithOutput(command, working_directory = None, env = None):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: RunCommandWithOutput
		# Input: Takes max three argument
		# 	command : command to be executed
		#	working_directory : If not None, the current directory will be changed to working_directory before the child is executed
		#	env : If not None, it defines the environment variables for the new process
		# Description: Executes the command, prints output from the command to the logger and waits for command to finish
		# Return: Returns an Object of Status.Result() class, result. result have two attributes Status and CmdResult
		# 	storing objects of StatusResult and CommandLineResult respectively
		#-------------------------------------------------------------------------------------------------------------------
		"""
		command = 'cmd.exe /C ' + command		#Execute the command on command prompt
		CREATE_NO_WINDOW = 0x08000000			#To create a console application process that is being run without a console window.
		result  = Result()
		out = None
		try:
			process = subprocess.Popen(command, cwd = working_directory, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env = env, shell=True, universal_newlines = True, creationflags = CREATE_NO_WINDOW)
			while True:
				out = process.stdout.read(1)
				if out == '' and process.poll() != None:
					break
				if out != '':
					sys.stdout.write(out)
					sys.stdout.flush()
			return result
		except Exception as e:
			#If any error comes while executing command, add it to StatusResult() and return Result()
			result.CmdResult.AddResult('Exception Occurred @ ' + command + str(e))
			result.Status.AddError('Exception Occurred @ ' + command + str(e))
			return result

	def RunCommand(command, time_out_seconds = None, wait_for_exit = True, working_directory = None, env = None):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: RunCommand
		# Input: Takes max five argument
		# 	command : command to be executed
		#	time_out_seconds : if a time_out_seconds was specified and expires, returns an error
		#	wait_for_exit : if false, doesn't wait for command to exit, issues the command and returns
		#	working_directory : If not None, the current directory will be changed to working_directory before the child is executed
		#	env : If not None, it defines the environment variables for the new process
		# Description: Executes the command
		# Return: Returns an Object of Status.Result() class, result. result have two attributes Status and CmdResult
		# 	storing objects of StatusResult and CommandLineResult respectively
		#-------------------------------------------------------------------------------------------------------------------
		"""
		command = 'cmd.exe /C ' + command		#Execute the command on command prompt
		CREATE_NO_WINDOW = 0x08000000			#To create a console application process that is being run without a console window.
		result  = Result()
		out = None
		try:
			process = subprocess.Popen(command, cwd = working_directory, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env = env, universal_newlines = True, creationflags = CREATE_NO_WINDOW)
		except Exception as e:
			#If any error comes while executing command, add it to StatusResult() and return Result()
			result.CmdResult.AddResult('Exception Occurred @ ' + command + str(e))
			result.Status.AddError('Exception Occurred @ ' + command + str(e))
			return result
		try:
			if(wait_for_exit):
				out, err = process.communicate(timeout = time_out_seconds)
				out = out.strip()
				if process.returncode != 0:
					#If any error comes after executing command, add it to StatusResult() and return Result()
					result.CmdResult.AddResult('Exception Occurred @ ' + out )
					result.Status.AddError('Exception Occurred @ ' + out )
				else:
					result.CmdResult.AddResult(out)
				return result

		except subprocess.TimeoutExpired:
			#If timeout expires kill the process, add it to StatusResult() and return Result()
			process.kill()
			result.CmdResult.AddResult('Command TimeOut : ' + command)
			result.Status.AddError('Command TimeOut : ' + command)
			return result

		if out is None:
			result.CmdResult.AddResult('No output received')
			return result

	def RunCommandExe(command, time_out_seconds = None, wait_for_exit = True, working_directory = None, debug = False, env = None, passKeyword = "", failKeyword = "" ):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: RunCommandExe
		# Input: Takes max five argument
		# 	command : command to be executed
		#	time_out_seconds : if a time_out_seconds was specified and expires, returns an error
		#	wait_for_exit : if false, doesn't wait for command to exit, issues the command and returns
		#	working_directory : If not None, the current directory will be changed to working_directory before the child is executed
		#	debug : If False, write output in debug logs else info logs
		#	env : If not None, it defines the environment variables for the new process
		# Description: Executes the command
		# Return: Returns an Object of Status.Result() class, result. result have two attributes Status and CmdResult
		# 	storing objects of StatusResult and CommandLineResult respectively
		# Example : result = CommandLine.RunCommandExe('AtraceStartLogging.exe 1000 20 qtc', time_out_seconds = 20, wait_for_exit = True, working_directory = r'C:\Automation\PTAS\Plasma\Engine\Resources\Scripts\LoggingExecutables\Executables', debug = True)
		#           if result.Status.HasError():
		#               logger.error(result.CmdResult.Output)
		#-------------------------------------------------------------------------------------------------------------------
		"""
		CREATE_NO_WINDOW = 0x08000000			#To create a console application process that is being run without a console window.
		command = 'cmd.exe /C ' + command
		result  = Result()
		out = None
		try:
			startTime = datetime.now()
			process = subprocess.Popen(command, cwd = working_directory, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env = env, universal_newlines = True, creationflags = CREATE_NO_WINDOW)
		except Exception as e:
			#If any error comes while executing command, add it to StatusResult() and return Result()
			result.CmdResult.AddResult('Exception Occurred @ ' + command + str(e))
			result.Status.AddError('Exception Occurred @ ' + command + str(e))
			return result

		while wait_for_exit:
			if time_out_seconds is not None:
				currTime = datetime.now()
				if (currTime - startTime).seconds > time_out_seconds:
					result.Status.AddError('Command Timeout')
					result.CmdResult.AddResult('Command Timeout')
					return result

			out = process.stdout.readline().replace('\n','')
			if (passKeyword in out)  or (process.poll() is not None) :
				result.CmdResult.AddResult('Success')
				return result

			if  failKeyword and failKeyword in out :                                
				result.Status.AddError(out)
				result.CmdResult.AddResult("Failed")
				logger.error(out)
				return result
			
			if not debug:
				logger.info(out)
			else:
				logger.debug(out)

		return result

	def RunCommandsSequentially(command):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: RunCommandsSequentially
		# Input: Takes list as an argument
		# command : list of commands to be executed
		# Description: Executes the adb shell commands
		# Return: Returns an Object of Status.Result() class, result. result have two attributes Status and CmdResult
		# storing objects of StatusResult and CommandLineResult respectively
		#-------------------------------------------------------------------------------------------------------------------
		"""
		result  = Result()
		out = None
		try:
			procId = subprocess.Popen(command[0], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr = subprocess.STDOUT, encoding='utf8')
			cmd = command[1]
			for i in range(2,len(command)):
				cmd = cmd + '\n' + command[i]
			out, error = procId.communicate(cmd)
			'''
			executing commands sequentially in adb shell
			procId.communicate method will return tuple-(output,error)
			out variable will have output of executed commands
			error variable will have error message
			'''

			#If you want to display the output on screen then uncomment the following line
			logger.info("Command output : " + str(out))
		except Exception as e:
			#If any error comes while executing command, add it to StatusResult() and return Result()
			result.CmdResult.AddResult('Exception Occurred @ ' + str(command) + str(e))
			result.Status.AddError('Exception Occurred @ ' + str(command) + str(e))
			return result

		if out is None:
			#If no output is received then add result as no output received and return result object
			result.CmdResult.AddResult('No output received')
			return result

		else:
			#If result variable is not None then add that output in results and return result object
			result.CmdResult.AddResult(out)
			return result

	def Run(command):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: Run
		# Input: Takes one argument, command to be executed
		# Description: Run command and return its string output.
		# Return: Returns an Object of Status.Result() class, result. result have two attributes Status and CmdResult
		# 	storing objects of StatusResult and CommandLineResult respectively
		#-------------------------------------------------------------------------------------------------------------------
		"""
		result  = Result()
		try:
			out = subprocess.check_output(command, universal_newlines = True)
		except Exception as e:
			result.CmdResult.AddResult('Exception Occurred @ ' + command + str(e))
			result.Status.AddError('Exception Occurred @ ' + command + str(e))
			return result
		else:
			result.CmdResult.AddResult(out)
			return result

class CommandLineResult(object):
	"""
	#-------------------------------------------------------------------------------------------------------------------
	# Name: CommandLineResult
	# Description: Used to store output after executing command from CommandLine
	#	Can get error if any line of output contains it.
	#	Can print all output to console and logs file
	#-------------------------------------------------------------------------------------------------------------------
	"""

	Output = None
	"""
	#-------------------------------------------------------------------------------------------------------------------
	# Name: Output
	# Description: Stores output of executing command from CommandLine
	#-------------------------------------------------------------------------------------------------------------------
	"""

	OutputLines = None
	"""
	#-------------------------------------------------------------------------------------------------------------------
	# Name: OutputLines
	# Description: Stores list of string lines from Output
	#-------------------------------------------------------------------------------------------------------------------
	"""

	OutputToLower = None
	OutputLinesToLower = None

	def __init__(self, output):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: __init__
		# Input: Takes two argument, first calling object of CommandLineResult and output arguments takes output string of
		#	executing command from CommandLine
		# Description: Initializes a CommandLineResult object upon creation with OutputLines and Output
		# Return: A CommandLineResult object [self]
		#-------------------------------------------------------------------------------------------------------------------
		"""
		self.Output = output.replace('\n', '\n\t\t\t\t\t').replace('\r', '')
		self.OutputLines = output.split('\n')

	def AddResult(self, output):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: AddResult
		# Input: Takes two argument, first calling object of CommandLineResult and output arguments takes output string of
		#	executing command from CommandLine
		# Description: Adds another result string to CommandLineResult object's Output and OutputLines
		# Return: A CommandLineResult object [self]
		#-------------------------------------------------------------------------------------------------------------------
		"""
		self.Output += output.replace('\n', '\n').replace('\r', '')
		self.OutputLines += output.split('\n')

	def ContainsStringIgnoreCase(self, match_string):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: ContainsStringIgnoreCase
		# Input: Takes two argument, first calling object of CommandLineResult and a string to match with Output
		# Description: Checks if match_string is present in OutputToLower
		# Return: bool, True if match_string is present in OutputToLower
		#-------------------------------------------------------------------------------------------------------------------
		"""
		if self.OutputToLower is None:
			self.OutputToLower = self.Output.lower()
		return match_string in self.OutputToLower

	def GetError(self):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: GetError
		# Input: Takes one argument, calling object of CommandLineResult
		# Description: Checks if string 'error' is present in OutputLinesToLower
		# Return: line from OutputLinesToLower, if string 'error' is present in OutputLinesToLower
		#-------------------------------------------------------------------------------------------------------------------
		"""
		error = ''
		if self.OutputLinesToLower is None:
			self.OutputLinesToLower = []
			for line in self.OutputLines:
				self.OutputLinesToLower.append(line.lower())

		for line in self.OutputLinesToLower:
			if 'error' in line:
				error += line

		return error

	def OutPutAllreceivedInfo(self):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: OutPutAllreceivedInfo
		# Input: Takes one argument, calling object of CommandLineResult
		# Description: Prints all string lines from OutputLines on console
		#-------------------------------------------------------------------------------------------------------------------
		"""
		print("==========Here Are All Log Info (Head)==========")
		for line in self.OutputLines:
			print (line.strip(' \t\n\r'))
		print("==========Here Are All Log Info (End)==========")

	def OutPutAllreceivedInfo2Log(self):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: OutPutAllreceivedInfo
		# Input: Takes one argument, calling object of CommandLineResult
		# Description: Prints all string lines from OutputLines to logger output
		#-------------------------------------------------------------------------------------------------------------------
		"""
		logger.info("==========Here Are All Log Info (Head)==========")
		for line in self.OutputLines:
			logger.info(line.strip(' \t\n\r'))

		logger.info("==========Here Are All Log Info (End)==========")

class Result(object):
	"""
	#-------------------------------------------------------------------------------------------------------------------
	# Name: Result
	# Description: Wrapper to combine StatusResult and CommandLineResult classes, Used in CmdResult class to get result
	#-------------------------------------------------------------------------------------------------------------------
	"""
	Status = None
	"""
	#-------------------------------------------------------------------------------------------------------------------
	# Name: Status
	# Description: Stores object of StatusResult
	#-------------------------------------------------------------------------------------------------------------------
	"""

	CmdResult = None
	"""
	#-------------------------------------------------------------------------------------------------------------------
	# Name: CmdResult
	# Description: Stores object of CommandLineResult
	#-------------------------------------------------------------------------------------------------------------------
	"""

	def __init__(self):
		"""
		#-------------------------------------------------------------------------------------------------------------------
		# Name: __init__
		# Input: Takes two argument, calling object of Result
		# Description: Initializes a Result object upon creation with Status and CmdResult
		# Return: A Result object [self]
		#-------------------------------------------------------------------------------------------------------------------
		"""
		self.Status = StatusResult()
		self.CmdResult = CommandLineResult('')

if __name__ == '__main__':
	print(dir())
