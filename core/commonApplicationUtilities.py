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

'''

'''
import os
import sys

class CommonApplicationUtilities(object):
    
        def GetExeDirectory():
            '''Gets the path location which contains the test script code that is currently executing.'''
            path = os.path.realpath(sys.argv[0])            
            return os.path.dirname(path)


        # <summary>
        #  Path location which contains the test script
        # </summary>
        _ExePath = "C:\\Automation\\PTAS\\Plasma\\Engine"
        
        # <summary>
        #  Resource path for all resources
        # </summary>
        _ResourcesPath = _ExePath + "\\Resources\\"

        # <summary>
        #  Resource path for all APPS
        # </summary>
        _ResourcesAppPath = _ExePath + "\\Resources\Apps\\"

        # <summary>
        #  Resource path for all Media Files
        # </summary>
        _ResourcesMediaFilePath = _ExePath + "\\Resources\MediaFiles\\"

        # <summary>
        #  Resource path for all Configuration files e.g. camera XML
        # </summary>
        _ResourcesConfigFilePath = _ExePath + "\\Resources\ConfigFiles\\"

        # <summary>
        #  Resource path for all independent executables e.g. ShellExe.exe, iperf.exe
        # </summary>
        _ResourcesProgramPath = _ExePath + "\\Resources\Programs\\"

        # <summary>
        #  Resource path for all scripts e.g. ATS scripts
        # </summary>
        _ResourcesScriptsPath = _ExePath + "\\Resources\Scripts\\"

        # <summary>
        #  Resource path for Images
        # </summary>
        _ResourcesImagesPath = _ExePath + "\\Document\Images\\"

        # <summary>
        #  Resource path for Reports
        # </summary>
        _ReportPath = _ExePath + "\\Reports\\"

        # <summary>
        #  Tools path for all resources
        # </summary>
        _ToolsPath = _ExePath + "\\Tools\\"

        # <summary>
        #  Tools path for DBBD Parser Tools
        # </summary>
        _ToolsDBBDPath = _ExePath + "\\Tools\DBBDParser\\"

        # <summary>
        #  Tools path for FTrace Parser Tools
        # </summary>
        _ToolsFTracePath = _ExePath + "\\Tools\FTrace\\"

        # <summary>
        #  Tools path for LI2 Tools
        # </summary>
        _ToolsLI2Path = _ExePath + "\\Tools\LI2\\"

        # <summary>
        #  Tools path for PwrDB Tools
        # </summary>
        _ToolsPwrDBPath = _ExePath + "\\Tools\PwrDB\\"

        # <summary>
        #  Tools path for QTF Tools
        # </summary>
        _ToolsQTFPath = _ExePath + "\\Tools\QTF\\"
        

if __name__ == '__main__':
    print(CommonApplicationUtilities._ResourcesPath)
    print(CommonApplicationUtilities._ResourcesMediaFilePath)
    print(CommonApplicationUtilities._ToolsPath)
    print(CommonApplicationUtilities._ToolsDBBDPath)
    print(CommonApplicationUtilities._ToolsFTracePath)
    print(CommonApplicationUtilities._ToolsLI2Path)
    print(CommonApplicationUtilities._ToolsPwrDBPath)
    print(CommonApplicationUtilities._ToolsQTFPath)
    
    

