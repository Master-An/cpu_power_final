class TestSuiteConfig:
    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description : The Class contains Test Suite specific Parameters, which will be common for all Test Cases
    #-------------------------------------------------------------------------------------------------------------------
    """

    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description : Set Test Suite Name
    #-------------------------------------------------------------------------------------------------------------------
    """
    TestSuiteName = "SampleTestSuite"

    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description : Power Handler Initialized by Framework based upon the "HardwareType" choosed
    #-------------------------------------------------------------------------------------------------------------------
    """
    PowerHandler = None

    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description : Time in seconds DUT takes to go in XO Shutdown
    #-------------------------------------------------------------------------------------------------------------------
    """
    XoShutdownTime = 30

    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description : Time in seconds DUT takes to Static Display State
    #-------------------------------------------------------------------------------------------------------------------
    """
    StaticDisplayDuration = 0

    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description : Time(in seconds) Device takes to boot up
    #-------------------------------------------------------------------------------------------------------------------
    """
    DeviceBootupTimeOut=60

    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description : Sets Measurement Style
    # Available Options : "EventBased" , "TimeBased"
    #-------------------------------------------------------------------------------------------------------------------
    """
    MeasurementStyle = 'TimeBased'


    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description : Sets Measurement Hardware Type
    # Available Options : "Kratos"
    #-------------------------------------------------------------------------------------------------------------------
    """
    HardwareType = 'Kratos'


    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description : Kratos Machine IP Address
    #-------------------------------------------------------------------------------------------------------------------
    """
    KratosIpAddress = None


    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description : Kratos PC Name
    #-------------------------------------------------------------------------------------------------------------------
    """
    KratosPcName = 'qct-kratos-xxx'


    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description : Kratos ID for Kratos-Lite
    #-------------------------------------------------------------------------------------------------------------------
    """
    KratosID = 'xyz'


    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description : Accuracy Mode to be set on Power Measuring System
    #-------------------------------------------------------------------------------------------------------------------
    """
    AccuracyMode = 'HIGH_ACCURACY'


    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description : Reboot Type to be performed before every iteration
    # Available Options :
    # HardReboot : Reboots DUT through Measurement Software by Powering OFF & Powering ON
    # NoReboot : Does not Reboots the DUT
    #-------------------------------------------------------------------------------------------------------------------
    """
    BootupAndShutdownType = 'HardReboot'


    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description : Sampling Rate for Kratos data collection
    # Default Value : 2500
    #-------------------------------------------------------------------------------------------------------------------
    """
    SampleRate = '2500'


    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description : Configuration file for the Measurement tool (Kratos/Alpaca)
    # Default Value : Channel_Default.udas
    #-------------------------------------------------------------------------------------------------------------------
    """
    ChannelConfiguration = 'Channel_Default.udas'


    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description : Current Limit to be set on Power Measuring System
    #-------------------------------------------------------------------------------------------------------------------
    """
    CurrentLimit = '4.0'


    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description : Voltage Limit to be set on Power Measuring System
    #-------------------------------------------------------------------------------------------------------------------
    """
    VoltageLevel = '3.7'


    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description : Voltage Tolerance which defines Measured Average Voltage Acceptable Range.
    #               Acceptable Measured Voltage Range = VoltageLevel +/- VoltageTolerance
    #-------------------------------------------------------------------------------------------------------------------
    """
    VoltageTolerance = 0.02


    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description : OVP Limit to be set on Power Measuring System
    #-------------------------------------------------------------------------------------------------------------------
    """
    OVPLimit = '4.2'

    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description : Maximum retries count for failure iterations of a test case
    #-------------------------------------------------------------------------------------------------------------------
    """
    MaxRetriesOnError = 3

    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description : HardReboot Target if test case fails after maximum retries
    #-------------------------------------------------------------------------------------------------------------------
    """
    ForceRebootAfterMaxRetries = 1

    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description : If enabled collect Crash Dumps if Device Crashes
    #-------------------------------------------------------------------------------------------------------------------
    """
    CollectCrashDumps = 1

    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description : DBBD Template Path for Generating Breakdown Output
    #-------------------------------------------------------------------------------------------------------------------
    """
    DBBDTemplatePath = "\\\\queen\\hyd_ast\\AST\\AST-Power\\DB_BD_Parser_Tool\\SDM630\\SDM630_Breakdown_Template.xlsx"

    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description : WIFI Server AP SSID
    #-------------------------------------------------------------------------------------------------------------------
    """
    SSID = ""

    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description : WIFI Server Password
    #-------------------------------------------------------------------------------------------------------------------
    """
    Password = ""

    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description : WeChat App username
    #-------------------------------------------------------------------------------------------------------------------
    """
    WeChatName = ""

    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description : WeChat App Password
    #-------------------------------------------------------------------------------------------------------------------
    """
    WeChatPassword = ""

    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description : Gmail username
    #-------------------------------------------------------------------------------------------------------------------
    """
    GmailUsername = ""

    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description : Gmail Password
    #-------------------------------------------------------------------------------------------------------------------
    """
    GmailPassword = ""

    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description : Facebook ID/Username
    #-------------------------------------------------------------------------------------------------------------------
    """
    FacebookID = ""

    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description : Facebook Password
    #-------------------------------------------------------------------------------------------------------------------
    """
    FacebookPassword = ""

    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description : TBS Host ID
    #-------------------------------------------------------------------------------------------------------------------
    """
    TbsLteHostId = ''

    Target = ''
    #Target Name e.g. SDM845

    MetaBuildPath = ''
    #Meta build location

    MetaBuildInfo = {}

    NonStandardImagesInfo = {}

    QcnFile = ""

    NvItemsXmlFile = ""

    T32ConfigFile = ''
    #Path upto T32 configuration XML file

    ChipsetName = ""

    QtfSettingsDirectory = ""

    QtfPwrDbSettingsDirectory = ""

    EnableQtf = 0

    EnableRebase = 0

    EnableQdssFtrace = 0

    SaveWorkspace = 1

    MultiIteration = 0

    GpioNumber = 0

    #ES Payload Parameters
    SaveWorkspace = 1
    Category = ""
    SerialNumber = ""
    EngineeringExperiment = False
    SoftwareID = ""

    #Build Loading Parameters
    CreateBuildCache = 0

    #Device Under Test (DUT) IP Address for Windows tasting (DB and HOBL)
    DutIP = ''

    #The absolute path within the Host machine where the MS HOBL scripts are kept (WIN HOBL)
    MicrosoftHOBL2Directory = 'C:/hobl/hobl'

    TestClockCmmScriptPath = ""

    BcmDumpCmmScriptPath = ""

    # Thermal KPI parameters
    AgilentDataLoggerAddress = "USBx::0xXXXX::0xXXXX::MYXXXXXXXX::0::INSTR"
    AgilentDataLoggerConfigFile = r"C:\Automation\PTAS\Plasma\Engine\Resources\ConfigFiles\AgilentDataLogger\data_logger_config.csv"
    ThermocoupleType = "K"
    NetBooterSerialPort = "COMxx"
    FanOutlet = 1
    FrontCameraLEDOutlet = 0
    RearCameraLEDOutlet = 0

    FrontCamera = "Front"
    FrontCameraURL = "http://xxx.xxx.xxx.xxx/"
    RearCamera = "Rear"
    RearCameraURL = "http://xxx.xxx.xxx.xxx/"

    # TBS iPerf parameters
    TBSUserName = "root"
    TBSPassword = ""
    TBSPort = 9000
    TBSiPerfDuration = 600
    
    SleepTestAPKList = []
    
    KratosErrorHandler = False
    
    WifiAdbIP = "10.91.222.47"
