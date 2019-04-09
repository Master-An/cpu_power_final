#=============================================================================
# FILE:         microepm.py
#
# OVERVIEW:     MicroEpm for Python
#
# DEPENDENCIES: libmicroepm
#
#               Copyright (c) 2016-2017 Qualcomm Technologies, Inc.
#               All Rights Reserved.
#               Qualcomm Technologies Proprietary and Confidential.
#=============================================================================
#=============================================================================
# EDIT HISTORY FOR MODULE
#
# This section contains comments describing changes made to the module.
# Notice that changes are listed in reverse chronological order.  Please
# use ISO format for dates.
#
# $Header: //source/qcom/qct/core/hwengines/epm/scripts/python/alpaca/epm/microepm.py#2 $$DateTime: 2017/09/15 16:02:01 $$Author: joresko $
#
# when        who  what, where, why
# ----------  ---  -----------------------------------------------------------
# 2017-03-06  jjo  Handle 32 vs 64-bit Python.
# 2017-02-16  jjo  Move thread to MicroEpm.
# 2016-12-07  jjo  Python 3.x compatibility.
# 2016-09-15  jjo  Initial revision.
#
#=============================================================================
#-----------------------------------------------------------------------------
#  Include Files
#-----------------------------------------------------------------------------
from ctypes import *
import collections
import sys
import os

#-----------------------------------------------------------------------------
#  Defines from MicroEpmAPI.h
#-----------------------------------------------------------------------------
MICRO_EPM_STRING_SIZE         = 32
MICRO_EPM_ROWDATA_STRING_SIZE = 16
MICRO_EPM_CH_STRING_SIZE      = 16
MICRO_EPM_STRING_MAX_SIZE     = MICRO_EPM_STRING_SIZE + 1
MICRO_EPM_CHANNEL_STRING_SIZE = MICRO_EPM_CH_STRING_SIZE + 1

#-----------------------------------------------------------------------------
#  Enums from MicroEpmAPI.h
#-----------------------------------------------------------------------------
MICRO_EPM_CHANNEL_TYPE_CURRENT = 0
MICRO_EPM_CHANNEL_TYPE_VOLTAGE = 1
MICRO_EPM_CHANNEL_TYPE_GPIO    = 2

MICRO_EPM_CHANNEL_DISABLE = 0
MICRO_EPM_CHANNEL_ENABLE  = 1

MICRO_EPM_GPIO_VALUE_LOW  = 0
MICRO_EPM_GPIO_VALUE_HIGH = 1

MICRO_EPM_GPIO_PIN_MARKER_1  = 0
MICRO_EPM_GPIO_PIN_MARKER_2  = 1
MICRO_EPM_GPIO_PIN_XO_OUT_EN = 2
MICRO_EPM_GPIO_PIN_EPM_INT   = 3
MICRO_EPM_GPIO_PIN_GPIO_4    = 4
MICRO_EPM_GPIO_PIN_GPIO_5    = 5

MICRO_EPM_GPIO_DIRECTION_INPUT  = 0
MICRO_EPM_GPIO_DIRECTION_OUTPUT = 1

MICRO_EPM_GPIO_DRIVE_STRONG                  = 0
MICRO_EPM_GPIO_DRIVE_OPEN_DRAIN_DRIVE_HIGH   = 1
MICRO_EPM_GPIO_DRIVE_OPEN_DRAIN_DRIVE_LOW    = 2
MICRO_EPM_GPIO_DRIVE_RESISTIVE_PULL_UP       = 3
MICRO_EPM_GPIO_DRIVE_RESISTIVE_PULL_DOWN     = 4
MICRO_EPM_GPIO_DRIVE_RESISTIVE_PULL_UP_DOWN  = 5
MICRO_EPM_GPIO_DRIVE_HIGH_IMPEDANCE_DIGITAL  = 6

MICRO_EPM_AVERAGING_MODE_NONE         = 0
MICRO_EPM_AVERAGING_MODE_4_SAMPLES    = 1
MICRO_EPM_AVERAGING_MODE_16_SAMPLES   = 2
MICRO_EPM_AVERAGING_MODE_64_SAMPLES   = 3
MICRO_EPM_AVERAGING_MODE_128_SAMPLES  = 4
MICRO_EPM_AVERAGING_MODE_256_SAMPLES  = 5
MICRO_EPM_AVERAGING_MODE_512_SAMPLES  = 6
MICRO_EPM_AVERAGING_MODE_1024_SAMPLES = 7
_MICRO_EPM_AVERAGING_MODE_NUM         = 8

MICRO_EPM_ADC_MODE_CONTINIOUS = 0
MICRO_EPM_ADC_MODE_TRIGGERED  = 1
MICRO_EPM_ADC_MODE_OFF        = 2
_MICRO_EPM_ADC_MODE_NUM       = 3

MICRO_EPM_CONV_TIME_140_US  = 0
MICRO_EPM_CONV_TIME_204_US  = 1
MICRO_EPM_CONV_TIME_332_US  = 2
MICRO_EPM_CONV_TIME_588_US  = 3
MICRO_EPM_CONV_TIME_1100_US = 4
MICRO_EPM_CONV_TIME_2116_US = 5
MICRO_EPM_CONV_TIME_4156_US = 6
MICRO_EPM_CONV_TIME_8244_US = 7
_MICRO_EPM_CONV_TIME_NUM    = 8

MICRO_EPM_BOARD_ID_UNKNOWN      = 0
MICRO_EPM_BOARD_ID_SPMV4        = 1
MICRO_EPM_BOARD_ID_EPMV4        = 2
MICRO_EPM_BOARD_ID_ALPACA       = 3
MICRO_EPM_BOARD_ID_MICROEPM_TAC = 4
MICRO_EPM_BOARD_ID_ALPACA_V2    = 5
MICRO_EPM_BOARD_ID_ALPACA_V3    = 6
MICRO_EPM_BOARD_ID_SPMV3        = 0x7FFFFFFE

MICRO_EPM_PLATFORM_UNDEFINED  = 0
MICRO_EPM_PLATFORM_INTEGRATED = 1
MICRO_EPM_PLATFORM_SPM        = 2

MICRO_EPM_RECORDING_FORMAT_UDAS = 0

#-----------------------------------------------------------------------------
#  Structs from MicroEpmAPI.h
#-----------------------------------------------------------------------------
class MicroEpmChannelDataType(Structure):
      _fields_ = [("dbPhysical", c_double),
                  ("uTarget", c_uint),
                  ("uModule", c_uint),
                  ("uChannel", c_uint),
                  ("nRawCode", c_int),
                  ("uRawTimestamp", c_uint),
                  ("eChannelType", c_int)]

class MicroEpmVersionInfoType(Structure):
      _fields_ = [("EpmID", c_int),
                  ("uMaxSamplesPerPacket", c_ushort),
                  ("uMaxSamplesPerAveragePacket", c_ushort),
                  ("uMaxPackets", c_ushort),
                  ("uFirmwareVersion", c_ubyte * 4),
                  ("uFirmwareProtocolVersion", c_ubyte),
                  ("uFirmwareLowestCompatibleProtocolVersion", c_ubyte),
                  ("uHostProtocolVersion", c_ubyte),
                  ("uHostLowestCompatibleProtocolVersion", c_ubyte)]

class MicroEpmBoardUuidType(Structure):
      _fields_ = [("uPart1", c_uint),
                  ("usPart2", c_ushort),
                  ("usPart3", c_ushort),
                  ("usPart4", c_ushort),
                  ("aucPart5", c_ubyte * 6)]

class MicroEpmTargetInfoType(Structure):
      _fields_ = [("szSerialNumber", c_char * 33),
                  ("szModelNumber", c_char * 33),
                  ("uTargetIdentifier", c_ushort),
                  ("ePlatformIdentifier", c_int),
                  ("eBoardOptionIdentifier", c_int),
                  ("eTargetIdentifier", c_int),
                  ("uTargetRevisionIdentifier", c_ushort),
                  ("uConfigurationIdentifier", c_ushort),
                  ("EepromProgrammedTime", c_ulonglong),
                  ("uEepromWriteCount", c_uint),
                  ("epmBoardUuid", MicroEpmBoardUuidType)]

class MicroEpmChannelStatType(Structure):
      _fields_ = [("dbAverage", c_double),
                  ("dbMin", c_double),
                  ("dbMax", c_double),
                  ("uNumSamples", c_uint)]

#-----------------------------------------------------------------------------
#  Global Variables
#-----------------------------------------------------------------------------
_microepm = 0
if sys.version_info > (3,):
   StandardError = Exception

#-----------------------------------------------------------------------------
#  Functions
#-----------------------------------------------------------------------------
def MicroEpmInit():
   global _microepm

   dllPath = os.path.dirname(os.path.realpath(__file__))
   if sys.maxsize > 2**32:
      dllPath += "\\x64"
   else:
      dllPath += "\\Win32"
   dllPath += "\\libmicroepm.dll"

   cdll.LoadLibrary(dllPath)
   _microepm = CDLL(dllPath)

   status = _microepm.MicroEpmInit()
   if status != 0:
      raise StandardError("MicroEpmInit failed with error: " + str(status))

def MicroEpmDeInit():
   status = _microepm.MicroEpmDeInit()
   if status != 0:
      raise StandardError("MicroEpmDeInit failed with error: " + str(status))

def MicroEpmConnect():
   uNumTargets = c_uint()

   status = _microepm.MicroEpmConnect(byref(uNumTargets))
   if status != 0:
      raise StandardError("MicroEpmConnect failed (make sure apps using EPM are closed) with error: " + str(status))
   return uNumTargets.value

def MicroEpmOpenTarget(target):
   uTarget = c_uint(target)
   uNumModules = c_uint()

   status = _microepm.MicroEpmOpenTarget(uTarget, byref(uNumModules))
   if status != 0:
      raise StandardError("MicroEpmOpenTarget failed with error: " + str(status))
   return uNumModules.value

def MicroEpmGetModuleHandle(target, module):
   uTarget = c_uint(target)
   uModule = c_uint(module)
   h = c_void_p()

   status = _microepm.MicroEpmGetModuleHandle(uTarget, uModule, byref(h))
   if status != 0:
      raise StandardError("MicroEpmGetModuleHandle failed with error: " + str(status))
   return h

def MicroEpmGetVersionInfo(h):
   versionInfo = MicroEpmVersionInfoType()

   status = _microepm.MicroEpmGetVersionInfo(h, byref(versionInfo))
   if status != 0:
      raise StandardError("MicroEpmVersionInfoType failed with error: " + str(status))
   return versionInfo

def MicroEpmPrintVersionInfo(versionInfo):
   print("EPM FW version: " +
      str(versionInfo.uFirmwareVersion[0]) + "." +
      str(versionInfo.uFirmwareVersion[1]) + "." +
      str(versionInfo.uFirmwareVersion[2]) + "." +
      str(versionInfo.uFirmwareVersion[3]) + "." +
      " HW version: " + str(versionInfo.EpmID))

def MicroEpmGetTimestamp(h):
   uRawTimestamp = c_uint()

   status = _microepm.MicroEpmGetTimestamp(h, byref(uRawTimestamp))
   if status != 0:
      raise StandardError("MicroEpmGetTimestamp failed with error: " + str(status))
   return uRawTimestamp.value

def MicroEpmSetTimestamp(h, timestamp):
   uRawTimestamp = c_uint(timestamp)

   status = _microepm.MicroEpmSetTimestamp(h, uRawTimestamp)
   if status != 0:
      raise StandardError("MicroEpmSetTimestamp failed with error: " + str(status))

def MicroEpmSetChannelEnable(h, channel, enable):
   uChannel = c_uint(channel)
   eEnable = c_int(enable)

   status = _microepm.MicroEpmSetChannelEnable(h, uChannel, eEnable)
   if status != 0:
      raise StandardError("MicroEpmSetChannelEnable failed with error: " + str(status))

def MicroEpmSetAveragingMode(h, voltageChan, currentChan, averagingMode):
   uVoltageChannel = c_uint(voltageChan)
   uCurrentChannel = c_uint(currentChan)
   eAveragingMode = c_int(averagingMode)

   status = _microepm.MicroEpmSetAveragingMode(h, uVoltageChannel, uCurrentChannel, eAveragingMode)
   if status != 0:
      raise StandardError("MicroEpmSetAveragingMode failed with error: " + str(status))

def MicroEpmSetAdcMode(h, adcMode):
   eAdcMode = c_int(adcMode)

   status = _microepm.MicroEpmSetAdcMode(h, eAdcMode)
   if status != 0:
      raise StandardError("MicroEpmSetAdcMode failed with error: " + str(status))

def MicroEpmSetSetPeriod(h, setPeriod):
   uSetPeriod = c_uint(setPeriod)

   status = _microepm.MicroEpmSetSetPeriod(h, uSetPeriod)
   if status != 0:
      raise StandardError("MicroEpmSetSetPeriod failed with error: " + str(status))

def MicroEpmSetConversionTime(h, channel, convTime):
   uChannel = c_uint(channel)
   eConvTime = c_int(convTime)

   status = _microepm.MicroEpmSetConversionTime(h, uChannel, eConvTime)
   if status != 0:
      raise StandardError("MicroEpmSetConversionTime failed with error: " + str(status))

def MicroEpmSetDataRateGovernor(h, maxDataRate):
   uMaxDataRate = c_uint(maxDataRate)

   status = _microepm.MicroEpmSetDataRateGovernor(h, uMaxDataRate)
   if status != 0:
      raise StandardError("MicroEpmSetSetPeriod failed with error: " + str(status))

def MicroEpmApplySettings(h):
   status = _microepm.MicroEpmApplySettings(h)
   if status != 0:
      raise StandardError("MicroEpmApplySettings failed with error: " + str(status))

def MicroEpmGetData(h, numPackets, dataArray):
   uNumPackets = c_uint(numPackets)
   uDataArrayLength = c_uint(len(dataArray))
   uNumSamples = c_uint()
   uNumOverflow = c_uint()
   uNumEmpty = c_uint()
   GetDataRet = collections.namedtuple('GetDataRet', ['uNumSamples', 'uNumOverflow', 'uNumEmpty'])

   status = _microepm.MicroEpmGetData(h, byref(dataArray), uDataArrayLength, byref(uNumSamples),
                                      uNumPackets, byref(uNumOverflow), byref(uNumEmpty))
   if status != 0:
      raise StandardError("MicroEpmGetData failed with error: " + str(status))
   retVal = GetDataRet(uNumSamples.value, uNumOverflow.value, uNumEmpty.value)
   return retVal

def MicroEpmClearBuffer(h):
   status = _microepm.MicroEpmClearBuffer(h)
   if status != 0:
      raise StandardError("MicroEpmClearBuffer failed with error: " + str(status))

def MicroEpmStartRecording(h, format, logFolder):
   eFormat = c_int(format)
   pszLogFolder = c_char_p(logFolder.encode('utf-8'))

   status = _microepm.MicroEpmStartRecording(h, eFormat, pszLogFolder)
   if status != 0:
      raise StandardError("MicroEpmStartRecording failed with error: " + str(status))

def MicroEpmStopRecording(h):
   status = _microepm.MicroEpmStopRecording(h)
   if status != 0:
      raise StandardError("MicroEpmStopRecording failed with error: " + str(status))

def MicroEpmSetChannelName(h, channel, name):
   uChannel = c_uint(channel)
   pszName = c_char_p(name.encode('utf-8'))

   status = _microepm.MicroEpmSetChannelName(h, uChannel, pszName)
   if status != 0:
      raise StandardError("MicroEpmSetChannelName failed with error: " + str(status))

def MicroEpmSetRsense(h, channel, rsenseMilliOhms):
   uChannel = c_uint(channel)
   dbRsenseMilliOhms = c_double(rsenseMilliOhms)

   status = _microepm.MicroEpmSetRsense(h, uChannel, dbRsenseMilliOhms)
   if status != 0:
      raise StandardError("MicroEpmSetRsense failed with error: " + str(status))

def MicroEpmSetRcmChannel(h, channel, rcmChannel):
   uChannel = c_uint(channel)
   uRcmChannel = c_uint(rcmChannel)

   status = _microepm.MicroEpmSetRcmChannel(h, uChannel, uRcmChannel)
   if status != 0:
      raise StandardError("MicroEpmSetRcmChannel failed with error: " + str(status))

def MicroEpmEepromRead(h, ignoreChecksum):
   bIgnoreChecksum = c_ubyte()

   if ignoreChecksum:
      bIgnoreChecksum = 1
   else:
      bIgnoreChecksum = 0

   status = _microepm.MicroEpmEepromRead(h, bIgnoreChecksum)
   if status != 0:
      raise StandardError("MicroEpmEepromRead failed with error: " + str(status))

def MicroEpmEepromWrite(h):
   status = _microepm.MicroEpmEepromWrite(h)
   if status != 0:
      raise StandardError("MicroEpmEepromWrite failed with error: " + str(status))

def MicroEpmEepromErase(h):
   status = _microepm.MicroEpmEepromErase(h)
   if status != 0:
      raise StandardError("MicroEpmEepromErase failed with error: " + str(status))

def MicroEpmGetTargetInfo(h):
   targetInfo = MicroEpmTargetInfoType()

   status = _microepm.MicroEpmGetTargetInfo(h, byref(targetInfo))
   if status != 0:
      raise StandardError("MicroEpmGetTargetInfo failed with error: " + str(status))
   return targetInfo

def MicroEpmSetTargetInfo(h, targetInfo):
   status = _microepm.MicroEpmSetTargetInfo(h, targetInfo)
   if status != 0:
      raise StandardError("MicroEpmSetTargetInfo failed with error: " + str(status))

def MicroEpmConvertUuidToString(uuid):
   return (format(uuid.uPart1, 'x').zfill(8) + "-" +
           format(uuid.usPart2, 'x').zfill(4) + "-" +
           format(uuid.usPart3, 'x').zfill(4) + "-" +
           format(uuid.usPart4, 'x').zfill(4) + "-" +
           format(uuid.aucPart5[0], 'x').zfill(2) +
           format(uuid.aucPart5[1], 'x').zfill(2) +
           format(uuid.aucPart5[2], 'x').zfill(2) +
           format(uuid.aucPart5[3], 'x').zfill(2) +
           format(uuid.aucPart5[4], 'x').zfill(2) +
           format(uuid.aucPart5[5], 'x').zfill(2))

def MicroEpmStartAcquisition(h):
   status = _microepm.MicroEpmStartAcquisition(h)
   if status != 0:
      raise StandardError("MicroEpmStartAcquisition failed with error: " + str(status))

def MicroEpmStopAcquisition(h):
   bOverflowed = c_ubyte()

   status = _microepm.MicroEpmStopAcquisition(h, byref(bOverflowed))
   if status != 0:
      raise StandardError("MicroEpmStopAcquisition failed with error: " + str(status))
   if bOverflowed:
      return True
   else:
      return False

def MicroEpmGetChannelStats(h, channel):
   uChannel = c_uint(channel)
   stats = MicroEpmChannelStatType()

   status = _microepm.MicroEpmGetChannelStats(h, uChannel, byref(stats))
   if status != 0:
      raise StandardError("MicroEpmGetChannelStats failed with error: " + str(status))
   return stats

