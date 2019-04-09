import logging
import colorlog, pathlib
from core.commonApplicationUtilities import CommonApplicationUtilities

global logger
"""
#-------------------------------------------------------------------------------------------------------------------
# Name: logger [global]
# Description: logger handler to be used across Plasma Engine
#-------------------------------------------------------------------------------------------------------------------
"""

def ConfigureLogger(logsFilePath = pathlib.Path(CommonApplicationUtilities._ReportPath), logFileName = 'logs.log', errorFileName = 'error.log'):
    """
    #-------------------------------------------------------------------------------------------------------------------
    # Name: ConfigureLogger
    # Input: Takes three optional argument
    #       argument1: directory path to create logs file
    #       argument2: All level logs file name
    #       argument3: Error logs file name
    # Description: Create logs handler for file logs and console logs, with a format and defined level
    # Return: StatusResult() object
    #-------------------------------------------------------------------------------------------------------------------
    """

    logPath = pathlib.Path(logsFilePath, logFileName)
    errorPath = pathlib.Path(logsFilePath, errorFileName)

    global logger   #Global logger handler to be used across Plasma Engine

    console_handler = logging.StreamHandler()   #Console handler, to show INFO level and above logs on windows console in colored format for
    console_handler.setLevel(logging.INFO)

    formatter = colorlog.ColoredFormatter(
        '%(bg_black)s %(asctime)s %(reset)s %(log_color)s%(levelname)-8s%(reset)s %(name)-11s %(module)-30s %(funcName)-30s %(lineno)-4d : %(reset)s %(log_color)s %(message)s',
        datefmt='%Y/%m/%d %H:%M:%S',
        reset=True,
        log_colors={
            'DEBUG':    'white,bold',
            'INFO':     'white,bold',
            'WARNING':  'yellow,bold',
            'ERROR':    'red,bold',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )
    console_handler.setFormatter(formatter)

    file_handler_log = logging.FileHandler(logPath)     #File handler, to show DEBUG level and above logs in a file
    file_handler_log.setLevel(logging.DEBUG)

    file_handler_log.setFormatter(logging.Formatter(
                    ' %(asctime)s %(levelname)-8s %(name)-11s %(module)-30s %(funcName)-30s %(lineno)-4d : %(message)s',
                    datefmt='%Y/%m/%d %H:%M:%S',
                    ))

    file_handler_error = logging.FileHandler(errorPath)     #File handler, to show ERROR level and above logs in a file
    file_handler_error.setLevel(logging.ERROR)

    file_handler_error.setFormatter(logging.Formatter(
                    ' %(asctime)s %(levelname)-8s %(name)-11s %(module)-30s %(funcName)-30s %(lineno)-4d : %(message)s',
                    datefmt='%Y/%m/%d %H:%M:%S',
                    ))


    logger = logging.getLogger('PTASLogger')
    logger.setLevel(logging.DEBUG)

    logger.handlers = []       # No duplicated handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler_log)
    logger.addHandler(file_handler_error)

ConfigureLogger()       #Load default logger on import module

class Log:
    """
	#-------------------------------------------------------------------------------------------------------------------
	# Name: Log
	# Description: A simple wrapper for logging package to create a logger object anbd write logs into files
	#-------------------------------------------------------------------------------------------------------------------
	"""

    def CreateLogger(self, name, level=logging.DEBUG, file='Logger.log'):
        logger = logging.getLogger(name)
        logger.setLevel(level)
    
        fh = logging.FileHandler(file)
        fh.setLevel(level)
        
        formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
        fh.setFormatter(formatter)
        
        logger.addHandler(fh)
        
        return logger
    
    def CreateLoggerForWebServer(self):
        pass
