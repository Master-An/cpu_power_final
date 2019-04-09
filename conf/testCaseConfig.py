
class TestCaseConfig:
    """
    #-------------------------------------------------------------------------------------------------------------------
    # Description : The Class contains Test Case specific Parameters
    #-------------------------------------------------------------------------------------------------------------------
    """

    # Update Name param value.
    Name = "PTAS"

    # Update Module Name param value. Eg. MM, GDOU, Thermal, etc.
    ModuleName = "Thermal"

    # Update EnableDebugging param value. Takes boolean value.Default value - False
    EnableDebugging = 0

    # Update FTraceLogs param value. Takes boolean value. Default value - 0
    FTraceLogs = 0

    # SystraceLogging param value. Takes integer(0/1) value. Default value - 0
    SystraceLogging = 0

    # TcpdumpLogging param value. Takes integer(0/1) value. Default value - 0
    TcpdumpLogging = 0

    #InstantaneousFPS parameter value. Takes integer(0/1) value. Default value - 0
    InstantaneousFPS = 0

    # Below 2 param are for Thermal Test case only
    # Update LogTsensData param value. Takes boolean value. Default value - 0
    LogTsensData = 0

    # Update IsEncoding param value. Takes boolean value. Default value - 0.
    IsEncoding = 0

    # Update Power measurement interval param value in Seconds
    MeasurementInterval = '1'

    # Update Power measurement duration param value in Seconds
    MeasurementDuration = 30

    UsbDisconnectDuration = '30'

    # Update Delay after disconnecting USB to start measurement. Default value - 1 second
    DelayAfterUsbDisconnectBeforeMeasurement = 1

    # Update Kratos Sample Rate. Default value - 2500
    SampleRate = ''

    # Update ChannelString param value. Example: Channel_Default.udas
    #ChannelConfiguration = 'qpat_alpaca_config.json'
    ChannelConfiguration = ''

    # Update ReportsPath param value. Default value - C:\\Automation\\PTAS\\Plasma\\Engine\\Reports
    ReportsPath = ""

    # Update MediaFile param value. Example: Qtc88_91sec.mp4
    MediaFile = "Qtc88.mp4"

    # Update ShellScriptName param value. Example: qct88a.sh
    ShellScriptName = "qtc88a.sh"

    # Update Wifi param value. Takes boolean value 0 for False, 1 for True. Default value - 0
    Wifi = 0
    # Update BT param value. Takes boolean value 0 for False, 1 for True. Default value - 0
    BT = 0
    # Update AirplaneMode param value. Takes True or False as input. Default value - False
    AirplaneMode = 1
    #Update Sensor param value. Takes boolean value 0 for False, 1 for True. Default value - 0
    Sensor =  0
    # Update AutoRotate param value. Takes boolean value 0 for False, 1 for True. Default value - 0
    AutoRotate = 0
    # Disables Location Services.
    LocationServices = 0

    #Enable/Disable Landscape mode. Android MM Testbase Presetup Actions using it. Takes value 0 to Disable, 1 for Enable. Default value - 0
    LandscapeMode = 0

    # WIFI Server AP SSID
    SSID = "GDOU"
    #WIFI Server Password
    Password = "XXXX"

    # Below 5 values are DoU specific
    # These five below param values could be kept blank. Need to add the corresponding values in respective test cases that use ATS. Example: SubwaySurfer.py
    AtsToPush = []
    AtsSetupFileName = ""
    AtsRunFileName = ""
    ApkPackageName = ""
    AndroidApkName = ""

    ApkPackageNameList = '' #"package.Name.A,apkNameB.apk;package.Name.B,apkNameB.apk;""

    # Update LaunchCommand  param value. Used to launch the activity on device
    LaunchCommand = 'adb shell am broadcast -a net.kishonti.testfw.ACTION_RUN_TESTS -n com.glbenchmark.glbenchmark27.corporate/net.kishonti.benchui.corporate.CommandLineSession -e test_ids "gl_manhattan" --ei -single_frame 34500 --ef -fps_limit 15 --ei -fps_log_window 1'

    PostCommand = ''

    #Set this parameter to True (1) for PTAS framework to not setup Crash Monitoring, set to False (0) by default
    IgnoreCrashMonitoring = 0

    # Below parameters are for Thermal Test Cases Only
    # Update Thermal Zone param value. For Eg. CPU0 or GPU according to test case functionality
    ThermalZone = "CPU0"
    # Update Temperature param value. This is set on the TEC. Default value = 25 degree C
    Temperature = 25
    # Update TestTempeature param value. This value should be test scenario specific at which the measurement needs to be taken.
    TestTemperature = 55
    # Update ThermalTimeout param value. This value should be in Seconds. Default value = 600 seconds
    ThermalTimeout = 600
    # Update DisplayResoution param value. This value should be the desired display resolution required while running Graphics related test cases on DUT
    DisplayResoution = "1080x1920"

    EnableT32 = 0
    #Enable T32 dumps collection

    T32WillCrashDevice = 0
    #If T32 dumps collection will crash the device, This parameter needs to be set as True to skip adb commands, and USB logs collection

    T32Commands = ''
    #T32 commands separated by a semicolon (;)

    DelayBeforeCommands  = ''
    #Adding delay before execution any T32 command

    RunItemCore = ''
    #Item Core of T32


    #QTF Parameters
    QTFSettingsFile = "qtc88a.txt"

    EnableIntervalsBreakdown = 0

    EnablePowerDb = 0

    PowerDbXml = ""

    QdssBufferSize = None

    UsbDisconnectDuration = 30

    Li2TemplateFile = ""

    # Below 5 values are SVR Specific
    RunSetCPUCountScript = 1

    RunSetCPUClkScrip = 1

    SystraceLogs = 0

    RunSetGPUClkScript = 1

    RunSetBusBandwidthScript = 1

    CPUCount = 8

    CPUClkLow = 1324800

    CPUClkHigh = 1344000

    GPUClk = 414000000

    BUSBandwidth = 1000000

    # the following parameters were added for Windows Formal Dashboard Use Cases
    SleepAfterReboot = 60

    WindowsXOProcedure = 0

    UseHoblIni = 1

    RunDBBDParser = 0

    HOBLRemoteUser = 'HCKTest'

    HOBLRemotePassword = 'Password123'

    SleepAfterWindowsTestCase = 30

    HasTrainingMode = 0

    HOBLScenario = 'youtube'

    HOBLScriptIterations = 0

    CollectETL = 0

    FPSCollectionInterval = 60

    PowerIteration =  1

    DebugIteration = 0

    MeasurementDurationOverhead = 20

    MeasurementDurationPower = 30

    # Parameter to support Trace collection for longer than measurement duration
    TraceLogDurationOverhead = 0.0

    #Build Loading & Device Setup Parameters
    AppsPath = ''
    # Apps Path must be mentioned till the directory where images are present
    # For Example : \\diwali\NSID-HYD-01\LA.UM.6.3.c1-01702-sdm845.1-1\LINUX\android\out\target\product\sdm845

    LoadSecondaryImages = 1
    QcnFile = ""
    NvItemsXmlFile = ""
    EdlHardware = "spiderboard"

    #Force Device Crash
    ForceDeviceCrash = 0
    DelayBeforeDeviceCrash = 30

    # Wm density for 1080p (FHD) panel. Default value - 480
    WmDensity = 480

    # Test case XML for DDR AUX test cases, which have attributes for Clocks, frequency etc
    DdrAuxTestCaseXml = r'C:\Automation\PTAS\Plasma\Engine\Resources\Scripts\CMM\ddraux_testcase.xml'


    DeviceCrashedForcefully = False

    #Actions to be performed before doing any ADB settings
    BeforeSetupActionCommands  = ''

    #Actions to be performed after doing ADB settings and Before Launching ATS/Shell
    BeforeLaunchActionCommands = ''

    #Actions to be performed after measurement Completes and logs collected
    WrapupActionCommands = ''

    #Current Iteration of Test Case being executed
    CurrentIterationCount = 0

    #Max Iteration number present in Test Case Log Directory.
    #If two or more Test Case with same name are executed,
    CurrentMaxIterationInLogDirectory = 0

    CommandLineParameters = {}

    #RegMon Execution Parameteres
    #Path to Save Output of RegMon Summary Result
    OutputFolderPath=""
    #Path containing FTrace logs for Meta1
    InputResultPath1=""
    #Path containing FTRACE logs for Meta2
    InputResultPath2=""
    #MetaID of build1 for Ftrace log comparision
    MetaName1=""
    #MetaID of build2 for Ftrace log comparision
    MetaName2=""

    def ResetIterationConfig() :
        TestCaseConfig.DeviceCrashedForcefully = False


    def ResetTestCaseConfig() :
        TestCaseConfig.SSID = ""
        TestCaseConfig.Password = ""
    #Parameter supports to set GovernotPerfmode
    PerfMode = 1

    # Parameters for Thermal KPI
    AgilentMeasurementInterval = 1
    # Update FLIRIRCamera param value. Takes boolean value. Default value - 0
    FLIRIRCamera = 1
    FLIRIRCameraImageSamplingInterval = 30
    FLIRIRCameraTemperatureSamplingInterval = 1

    BackToBackRuns = 1
    TimeIntervalToAverageOver = 1
    DetectTargetAutomatically = 1

    # TBS iPerf parameter
    TBSThroughput = 25

    AI_Done = False
    
    MultiAPPTestSleepList = []

    Loop = 0
    Interation = 0
    TestScene = None
    CoreOnline = []