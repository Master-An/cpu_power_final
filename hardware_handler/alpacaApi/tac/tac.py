#=============================================================================
# FILE:         tac.py
#
# OVERVIEW:     ALPACA script for controlling TAC.
#
# DEPENDENCIES: PySerial
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
# $Header: //source/qcom/qct/core/hwengines/epm/scripts/python/alpaca/tac/tac.py#3 $$DateTime: 2017/09/12 17:05:32 $$Author: joresko $
#
# when        who  what, where, why
# ----------  ---  -----------------------------------------------------------
# 2017-08-18  jjo  Pull in fix for PySerial 2.7
# 2017-03-06  jjo  Add wrapper for read and write.
# 2017-03-01  jjo  Added new functions from HW controller & VID/PID support.
# 2016-03-31  jjo  Initial revision.
#
#===========================================================================*/
#-----------------------------------------------------------------------------
#  Include Files
#-----------------------------------------------------------------------------
import sys
from time import sleep
import re
try:
   import serial
   import serial.tools.list_ports
except Exception as x:
   print("\nPySerial is required. Please install this library.")
   sys.exit()

#-----------------------------------------------------------------------------
#  Global Variables
#-----------------------------------------------------------------------------
_alpaca_id = {'pid': 0x9302, 'vid': 0x05C6}
_spider_id = {'pid': 0x0483, 'vid': 0x16C0}
if sys.version_info > (3,):
   StandardError = Exception

#-----------------------------------------------------------------------------
#  Functions
#-----------------------------------------------------------------------------
## Function to get a list of port names for ALPACA devices
#
#  @return List of COM port names
def ProbeForDevices():
   identifiers = (_alpaca_id, _spider_id)

   return _get_comports_by_identifiers(identifiers)

## Gives a list of port names matching the identifiers passed in (borrowed from qhw's utils.py)
#
#  @param identifiers List of dictionaries where each dictionary contains
#                     one or more port identifier (key and value)
#                     e.g. given, ({'pid': 37634, 'vid': 1478}, {'description': 'Test Automation Controller (TAC) Device'})
#                     this will match all ports where the pid is 37634 and the vid is 1478
#                     OR where the description is 'Test Automation Controller (TAC) Device'
#  @return List of COM port names
def _get_comports_by_identifiers(identifiers):
   py_ser_ver_str = serial.VERSION.split(".")
   py_ser_ver = float(py_ser_ver_str[0]) + float(py_ser_ver_str[1]) / 10
   if py_ser_ver < 2.7:
      raise Exception("PySerial version 2.7 or greater is required. Your version is: " + serial.VERSION)

   matching_ports = []
   ports = serial.tools.list_ports.comports()
   if py_ser_ver >= 3.0:
      for port in ports:
         for identifier in identifiers:
            match = True
            for key, value in identifier.items():
               if key == 'description':
                  # Description include the COM port number appended at the end, ignore that whe looking for a match
                  if not port.description.startswith(value):
                     match = False
                     break
               elif getattr(port, key) != value:
                  match = False
                  break
            if match:
               matching_ports.append(port.device)
   else:
      vids_pids = []
      for identifier in identifiers:
         # Convert ids to strings of format <vid>:<pid>
         try:
            vids_pids.append(("%0.4X" % identifier['vid']).upper() + ':' + ("%0.4X" % identifier['pid']).upper())
         except KeyError:
            print("Error: get_comports_by_identifiers() requires vid & pid identifiers when using PySerial 2.x")
            continue
      for port in ports:
         for vid_pid in vids_pids:
            if vid_pid in port[2]:
               # The third item in the tuple will contain "<vid>:<pid>"
               matching_ports.append(port[0])

   return matching_ports

#-----------------------------------------------------------------------------
#  Classes
#-----------------------------------------------------------------------------
## Tac class to control the test automation controller.
#
class Tac:
   ## tac class constructor.
   #
   #  @param self
   #  @param timeout
   #  @param baud_rate
   def __init__(self, port=None, timeout=0.3, baud_rate=115200):
      if port is not None:
         self.port = port
         self.ser = serial.Serial(self.port, baud_rate, timeout=timeout)
         return
      else:
         ports = ProbeForDevices()
         if len(ports) == 0:
            raise StandardError("No TAC devices available")
         elif len(ports) > 1:
            raise StandardError("Multiple TAC devices available - port must be specified")
         else:
            self.port = ports[0]
            try:
               self.ser = serial.Serial(self.port, baud_rate, timeout=timeout)
            except Exception as x:
               print("Could not open " + self.port)

   ## Opens the port. By default, the port is open.
   #
   #  @param self
   # def open(self):
   #    self.ser.open()

   ## Closes the port.
   #
   #  @param self
   # def close(self):
   #    self.ser.close()

   ## Writes to the serial port.
   #
   #  @param cmd
   def _write_serial(self, cmd):
      write_str = cmd + "\r"
      self.ser.write(write_str.encode('ascii'))

   ## Reads from the serial port.
   #
   #  @param num_bytes
   def _read_serial(self, num_bytes):
      return self.ser.read(num_bytes).decode("utf-8")

   ## Reads from TAC.
   #
   #  The following items can be read from TAC:
   #  * "port_name"
   #     * Output is the port name, .e.g. "COM24"
   #  * "version"
   #     * Output is the version, .e.g. "EPM FW version: 1.4.6.0. HW version: 3 (ALPACA)"
   #  * "uuid"
   #     * Output is the UUID, .e.g. "06CF4E17-BDAE-4B8D-ABEC-BBD2E0239ECD"
   #  * GPIOs
   #    * '0' --> off
   #    * '1' --> on
   #    * Supported GPIOs:
   #      * "ready"
   #      * "monitor_1"
   #      * "monitor_2"
   #      * "monitor_3"
   #
   #  @param self
   #  @param item The item to read
   def _read(self, item):
      if item == "port_name":
         return self.port
      elif item == "version":
         cmd = "version"
      elif item == "uuid":
         cmd = "sys getFSUUID"
      elif item == "ready":
         cmd = "ttl inputBit 1"
      elif item == "monitor_1":
         cmd = "ttl inputBit 2"
      elif item == "monitor_2":
         cmd = "ttl inputBit 3"
      elif item == "monitor_3":
         cmd = "ttl inputBit 4"
      else:
         raise ValueError("Invalid read item")

      self._write_serial(cmd)
      text = self._read_serial(10000)
      text = text.splitlines()

      if text[2] != "ok":
         raise StandardError("Read error")

      return text[1]

   ## Writes a command to TAC.
   #
   #  The following items can be written to TAC:
   #  * UUID:
   #    * "uuid"
   #      * Value is a string with UUID standard format "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
   #  * GPIOs:
   #    * '0' --> off
   #    * '1' --> on
   #    * Supported GPIOs:
   #      * "power_key"
   #      * "power"
   #      * "edl"
   #      * "usb"
   #      * "volume_up"
   #      * "volume_down"
   #      * "focus"
   #      * "snap"
   #      * "control_1"
   #      * "control_2"
   #      * "control_3"
   #
   #  @param self
   #  @param item
   #  @param value
   def _write(self, item, value):
      if value == 0:
         value = '0'
      elif value == 1:
         value = '1'

      if item == "uuid":
         pattern = re.compile(r'([A-F]|[a-f]|[0-9]){8}-([A-F]|[a-f]|[0-9]){4}-([A-F]|[a-f]|[0-9]){4}-([A-F]|[a-f]|[0-9]){4}-([A-F]|[a-f]|[0-9]){12}$')
         if not pattern.match(value):
            raise ValueError("Invalid UUID format")
         cmd = "setid " + value
      elif item == "power_key":
         if value != '0' and value != '1':
            raise ValueError("Invalid value")
         cmd = "ttl outputBit 1 " + value
      elif item == "power":
         if value != '0' and value != '1':
            raise ValueError("Invalid value")
         cmd = "devicePower " + value
      elif item == "edl":
         if value != '0' and value != '1':
            raise ValueError("Invalid value")
         cmd = "ttl outputBit 4 " + value
      elif item == "usb":
         if value != '0' and value != '1':
            raise ValueError("Invalid value")
         cmd = "usbDevicePower " + value
      elif item == "volume_up":
         if value != '0' and value != '1':
            raise ValueError("Invalid value")
         cmd = "gpio volup " + value
      elif item == "volume_down":
         if value != '0' and value != '1':
            raise ValueError("Invalid value")
         cmd = "ttl outputBit 2 " + value
      elif item == "focus":
         if value != '0' and value != '1':
            raise ValueError("Invalid value")
         cmd = "gpio focus " + value
      elif item == "snap":
         if value != '0' and value != '1':
            raise ValueError("Invalid value")
         cmd = "gpio snap " + value
      elif item == "control_1":
         if value != '0' and value != '1':
            raise ValueError("Invalid value")
         cmd = "ttl outputBit 6 " + value
      elif item == "control_2":
         if value != '0' and value != '1':
            raise ValueError("Invalid value")
         cmd = "ttl outputBit 7 " + value
      elif item == "control_3":
         if value != '0' and value != '1':
            raise ValueError("Invalid value")
         cmd = "ttl outputBit 8 " + value
      else:
         raise ValueError("Invalid write item")

      self._write_serial(cmd)
      text = self._read_serial(100)
      text = text.splitlines()

      if text[1] != "ok":
         raise StandardError("Write error")

   ## Simulates pressing and releasing a button
   #
   #  The button is driven low (in case it was not previously off),
   #  on (for duration), and then off.
   #
   #  Supported buttons:
   #  * "power_key"
   #  * "volume_up"
   #  * "volume_down"
   #  * "focus"
   #  * "snap"
   #
   #  @param self
   #  @param button
   #  @param duration Duration key is pressed in seconds
   def _press_button(self, button, duration=0.1):
      supported_buttons = ["power_key", "volume_up", "volume_down", "focus", "snap"]
      if button not in supported_buttons:
         raise ValueError("Invalid button")

      self._write(button, '0')
      self._write(button, '1')
      sleep(duration)
      self._write(button, '0')

   ## Reads a register on an I2C peripheral
   #
   #  A single register is read and the value is returned as an int.
   #
   #  @param self
   #  @param i2c_address The I2C address of the GPIO expander, e.g. 0x71
   #  @param register The register, e.g. 0xe
   def _read_i2c_perph_reg(self, i2c_address, register):
      if i2c_address < 0 or i2c_address > 0xff:
         raise ValueError("Invalid I2C address")
      elif register < 0 or register > 0xff:
         raise ValueError("Invalid register")

      addr = hex(i2c_address)
      if len(addr) == 3:
         # Need to pad
         addr = "0x0" + addr[2]

      reg = hex(register)
      if len(reg) == 3:
         # Need to pad
         reg = "0x0" + reg[2]

      cmd = "i2c readRegisterBytes " + addr + " " + reg + " 1"
      self._write_serial(cmd)
      text = self._read_serial(100)
      text = text.splitlines()
      if text[1] != "ok":
         raise StandardError("Write error")

      cmd = "i2c receive"
      self._write_serial(cmd)
      text = self._read_serial(10000)
      text = text.splitlines()
      if text[2] != "ok":
         raise StandardError("Read error")

      return int(text[1], 16)

   ## Writes to a register on an I2C peripheral
   #
   #  @param self
   #  @param i2c_address The I2C address of the GPIO expander, e.g. 0x71
   #  @param register The register, e.g. 0xe
   #  @param value The value to write, e.g. 0x17
   def _write_i2c_perph_reg(self, i2c_address, register, value):
      if i2c_address < 0 or i2c_address > 0xff:
         raise ValueError("Invalid I2C address")
      elif register < 0 or register > 0xff:
         raise ValueError("Invalid register")
      elif value < 0 or value > 0xff:
         raise ValueError("Invalid value")

      addr = hex(i2c_address)
      if len(addr) == 3:
         # Need to pad
         addr = "0x0" + addr[2]

      reg = hex(register)
      if len(reg) == 3:
         # Need to pad
         reg = "0x0" + reg[2]

      val = hex(value)
      if len(val) == 3:
         # Need to pad
         val = "0x0" + val[2]

      cmd = "i2c writeByte " + addr + " " + reg + " " + val
      self._write_serial(cmd)
      text = self._read_serial(100)
      text = text.splitlines()
      if text[1] != "ok":
         raise StandardError("Write error")

   ## Read-modify-writes a register on an I2C peripheral
   #
   #  @param self
   #  @param i2c_address The I2C address of the GPIO expander, e.g. 0x71
   #  @param register The register, e.g. 0xe
   #  @param value The value to write, e.g. 0x17
   #  @param mask The mask to apply
   #  @param shift The shift to apply to the value
   def _read_modify_write_i2c_perph_reg(self, i2c_address, register, value, mask, shift):
      if mask < 0 or mask > 0xff:
         raise ValueError("Invalid mask")

      reg = self.read_i2c_perph_reg(i2c_address, register)

      reg = reg & ~mask
      reg = reg | ((value << shift) & mask)

      self.write_i2c_perph_reg(i2c_address, register, reg)

   ## Gets the UUID
   #
   #  @param self
   def GetUuid(self):
      return self._read("uuid")

   ## Gets the version
   #
   #  @param self
   def GetVersion(self):
      return self._read("version")

   ## Disconnects power from the device
   #
   #  @param self
   def Off(self):
      self._write('power', 0)
      self._write('usb', 0)
      sleep(2)

   ## Powers on the device
   #
   #  @param self
   def On(self):
      self._write('power', 1)
      sleep(0.1)
      self._write('usb', 1)
      self._press_button('power_key')

   ## Boots the device to EDL
   #
   #  @param self
   def BootToEdl(self):
      self.Off()
      self._write('edl', 1)
      sleep(0.5)
      self.On()
      sleep(2)
      self._write('edl', 0)

   ## Boots the device to HLOS
   #
   #  @param self
   def BootToHlos(self):
      self.Off()
      sleep(0.5)
      self.On()

   ## Disconnects USB
   #
   #  @param self
   def DisconnectUsb(self):
      self._write('usb', 0)

   ## Connects USB
   #
   #  @param self
   def ConnectUsb(self):
      self._write('usb', 1)

