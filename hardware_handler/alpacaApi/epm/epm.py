#=============================================================================
# FILE:         epm.py
#
# OVERVIEW:     ALPACA Embedded Power Measurement (EPM) for Python
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
# $Header: //source/qcom/qct/core/hwengines/epm/scripts/python/alpaca/epm/epm.py#1 $$DateTime: 2017/09/05 18:48:19 $$Author: joresko $
#
# when        who  what, where, why
# ----------  ---  -----------------------------------------------------------
# 2017-02-16  jjo  Move thread to MicroEpm.
# 2017-01-20  jjo  Improved overflow handling.
# 2016-12-12  jjo  Clear buffer in GetData thread.
# 2016-12-07  jjo  Python 3.x compatibility.
# 2016-09-24  jjo  Initial revision.
#
#=============================================================================
#-----------------------------------------------------------------------------
#  Include Files
#-----------------------------------------------------------------------------
from .microepm import *
import json
import os
import sys

#-----------------------------------------------------------------------------
#  Types
#-----------------------------------------------------------------------------
Device = collections.namedtuple('Device', ['port', 'handle', 'name', 'serialNum', 'uuid'])

#-----------------------------------------------------------------------------
#  Global Variables
#-----------------------------------------------------------------------------
_connected = False
_devices = []
if sys.version_info > (3,):
   StandardError = Exception

#-----------------------------------------------------------------------------
#  Functions
#-----------------------------------------------------------------------------
## Function to get a list of port names for EPM devices. This will close
#  any open connections.
#
def ProbeForDevices():
   global _connected
   global _devices

   if not _connected:
      MicroEpmInit()
   else:
      # Force disconnect and reconnect to recheck for devices
      MicroEpmDeInit()
      MicroEpmInit()

   _connected = False
   _devices = []

   numTargets = MicroEpmConnect()
   if numTargets == 0:
      return _devices

   portIdx = 0
   for target in range(0, numTargets, 1):
      numModules = MicroEpmOpenTarget(target)
      if numModules > 1:
         # Must be SPMv3 - not supported
         continue
      h = MicroEpmGetModuleHandle(target, 0)
      targetInfo = MicroEpmGetTargetInfo(h)
      _devices.append(Device("EPM_PORT" + str(portIdx),
                             h,
                             targetInfo.szModelNumber,
                             targetInfo.szSerialNumber,
                             MicroEpmConvertUuidToString(targetInfo.epmBoardUuid)))
      portIdx += 1

   if portIdx > 0:
      _connected = True

   return _devices

#-----------------------------------------------------------------------------
#  Classes
#-----------------------------------------------------------------------------
## EPM class to control SPM and TAC
#
class Epm:
   ## EPM class constructor.
   #
   #  @param self
   #  @param port
   def __init__(self, port=None):
      if not _connected:
         ProbeForDevices()

      if len(_devices) == 0:
         raise StandardError("No SPM devices connected")

      if port is not None:
         found = False
         for device in _devices:
            if device.port == port:
               self.h = device.handle
               found = True
               break
         if not found:
            raise StandardError("Device not found")
      else:
         if len(_devices) > 1:
            raise StandardError("Multiple EPM devices available - port must be specified")
         else:
            self.h = _devices[0].handle

      self.versionInfo = MicroEpmGetVersionInfo(self.h)
      self.targetInfo = MicroEpmGetTargetInfo(self.h)
      self.getData = False
      self.overflowed = False
      self.targetSet = False
      self.configSet = False
      self.logData = False

   def __set_target_file(self, targetPath, targetFile):
      if targetPath != '':
         targetFile = os.path.join(targetPath, targetFile)

      if self.targetSet:
         if self.configSet:
            for channel in self.enabledChannels:
               MicroEpmSetChannelEnable(self.h, channel["channel"], MICRO_EPM_CHANNEL_DISABLE)
            self.configSet = False
         self.targetSet = False

      with open(targetFile) as h:
         targetData = json.load(h)
         self.channels = targetData["channels"]
         for channel in self.channels:
            MicroEpmSetChannelName(self.h, channel["channel"], channel["name"])
            if channel["type"] == 'I':
               MicroEpmSetRsense(self.h, channel["channel"], channel["resistor"])
            if "rcm_channel" in channel:
               MicroEpmSetRcmChannel(self.h, channel["channel"], channel["rcm_channel"])

      # TODO: power on test?

      self.targetSet = True

   def SetConfigFile(self, configFile):
      if self.configSet:
         for channel in self.enabledChannels:
            MicroEpmSetChannelEnable(self.h, channel["channel"], MICRO_EPM_CHANNEL_DISABLE)
         self.configSet = False

      configFilePath, configFileName = os.path.split(configFile)

      with open(configFile) as h:
         configData = json.load(h)
         self.__set_target_file(configFilePath, configData["target_file"])
         self.enabledChannels = configData["enabled_channels"]
         self.enabledChannels = sorted(self.enabledChannels, key = lambda chan: chan["channel"])
         self.results = {}
         for channel in self.enabledChannels:
            chanIdx = channel["channel"]
            chanInfo = None
            for chan in self.channels:
               if chan["channel"] == chanIdx:
                  chanInfo = chan
                  break;
            if chanInfo is None:
               raise StandardError("Channel doesn't exist, ChanIdx=", chanIdx)
            if chanInfo["type"] == 'I':
               units = "mA"
            elif chanInfo["type"] == 'V':
               units = 'mV'
            else:
               units = 'mV'
            self.results[chanIdx] = {'channel': chanIdx,
                                     'name':    chanInfo["name"],
                                     'type':    chanInfo["type"],
                                     'units':   units,
                                     'numSamples': 0,
                                     'avg': 0,
                                     'min': 0,
                                     'max': 0}
      self.configSet = True

   def SetLogDirectory(self, logDirectoryPath, logFormat="UDAS"):
      if not os.path.exists(logDirectoryPath):
         os.makedirs(logDirectoryPath)
      self.logDirectoryPath = logDirectoryPath
      self.logData = True

   def StartMeasurement(self):
      if not self.configSet:
         raise StandardError("No configuration specified")

      if self.getData:
         raise StandardError("Tried to start measurement when already running")

      for channel in self.results:
         self.results[channel]["numSamples"] = 0
         self.results[channel]["avg"] = 0
         self.results[channel]["min"] = 0
         self.results[channel]["max"] = 0

      # Reset timestamp since timer overflows are not handled
      MicroEpmSetTimestamp(self.h, 0)

      for channel in self.enabledChannels:
         MicroEpmSetChannelEnable(self.h, channel["channel"], MICRO_EPM_CHANNEL_ENABLE)
      if self.logData:
         MicroEpmStartRecording(self.h, MICRO_EPM_RECORDING_FORMAT_UDAS, self.logDirectoryPath)
      MicroEpmApplySettings(self.h)
      self.getData = True
      self.overflowed = False
      MicroEpmStartAcquisition(self.h)

   def StopMeasurement(self):
      if not self.getData:
         return

      self.getData = False
      self.overflowed = MicroEpmStopAcquisition(self.h)
      if self.logData:
         MicroEpmStopRecording(self.h)
         self.logData = False

      for channel in self.enabledChannels:
         MicroEpmSetChannelEnable(self.h, channel["channel"], MICRO_EPM_CHANNEL_DISABLE)
      MicroEpmApplySettings(self.h)

      for channel in self.enabledChannels:
         chan = channel["channel"]
         stats = MicroEpmGetChannelStats(self.h, chan)
         self.results[chan]["numSamples"] = stats.uNumSamples
         self.results[chan]["avg"] = stats.dbAverage
         self.results[chan]["min"] = stats.dbMin
         self.results[chan]["max"] = stats.dbMax

      if self.overflowed:
         raise StandardError("PSoC data buffer overflowed. Some data samples were lost.")

   def GetResults(self):
      if self.getData:
         raise StandardError("Tried to get results while running")
      return self.results
