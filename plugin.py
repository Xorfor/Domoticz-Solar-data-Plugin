#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Space Weather
#
# Author: Xorfor
#
"""
<plugin key="xfr_spaceweather" name="Space Weather" author="Xorfor" version="1.0.0" wikilink="https://github.com/Xorfor/Domoticz-Space-Weather-Plugin">
    <params>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="False" value="Normal" default="true"/>
                <option label="True" value="Debug"/>
            </options>
        </param>
    </params>
</plugin>
"""
import Domoticz
import json
import subprocess


class BasePlugin:
    __DEBUG_NONE = 0
    __DEBUG_ALL = 1

    __HEARTBEATS2MIN = 6
    __MINUTES = 1  # or use a parameter

    # __API_URL = "https://api.openuv.io/api/v1/uv?lat={}&lng={}"
    __API_DOMAIN1 = "https://services.swpc.noaa.gov/products/summary/solar-wind-mag-field.json"
    __API_DOMAIN2 = "https://services.swpc.noaa.gov/products/summary/solar-wind-speed.json"
    __API_DOMAIN3 = "https://services.swpc.noaa.gov/products/summary/10cm-flux.json"
    __API_DOMAIN4 = "https://services.swpc.noaa.gov/products/noaa-scales.json"
    __API_VERSION = ""
    __API_PARAMETERS = ""
    __API_HEADER = ""

    # Device units
    __UNIT_BT = 1
    __UNIT_BZ = 2
    __UNIT_WINDSPEED = 3
    __UNIT_FLUX = 4
    __UNIT_R = 5
    __UNIT_S = 6
    __UNIT_G = 7

    __UNITS = [
        # Unit, Name, Type, Subtype, Options, Used
        # IMF: Interplanetary Magnetic Field
        # IMF Strength: BT nT
        [__UNIT_BT, "Bt", 243, 31, {"Custom": "0;nT"}, 1],
        # IMF Direction: Bz (south) nT
        [__UNIT_BZ, "Bz", 243, 31, {"Custom": "0;nT"}, 1],
        # Solar wind: Speed km/s
        [__UNIT_WINDSPEED, "Solar Wind Speed",
            243, 31, {"Custom": "0;km/s"}, 1],
        # Radio Flux
        [__UNIT_FLUX, "Flux", 243, 31, {"Custom": "0;sfu"}, 1],
        # Radio Blackouts
        [__UNIT_R, "Radio Blackouts", 243, 22, {}, 1],
        # Solar Radiation Storms
        [__UNIT_S, "Solar Radiation Storms", 243, 22, {}, 1],
        # Geomagnetic Storms
        [__UNIT_G, "Geomagnetic Storms", 243, 22, {}, 1],
    ]

    __SCALES = {
        0: "None",
        1: "Minor",
        2: "Moderate",
        3: "Strong",
        4: "Severe",
        5: "Extreme",
    }

    def __init__(self):
        self.__runAgain = 0
        return

    def onCommand(self, Unit, Command, Level, Color):
        Domoticz.Debug(
            "onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")

    def onDeviceAdded(self, Unit):
        Domoticz.Debug("onDeviceAdded called for Unit " + str(Unit))

    def onDeviceModified(self, Unit):
        Domoticz.Debug("onDeviceModified called for Unit " + str(Unit))

    def onDeviceRemoved(self, Unit):
        Domoticz.Debug("onDeviceRemoved called for Unit " + str(Unit))

    def onStart(self):
        Domoticz.Debug("onStart called")
        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(self.__DEBUG_ALL)
        else:
            Domoticz.Debugging(self.__DEBUG_NONE)
        # Images
        # Check if images are in database
        # if "xfr_spaceweather" not in Images:
        #     Domoticz.Image("xfr_spaceweather.zip").Create()
        # image = Images["xfr_spaceweather"].ID
        # Domoticz.Debug("Image created. ID: "+str(image))
        # Validate parameters
        # Create devices
        for unit in self.__UNITS:
            Domoticz.Device(Unit=unit[0],
                            Name=unit[1],
                            Type=unit[2],
                            Subtype=unit[3],
                            Options=unit[4],
                            Used=unit[5]).Create()
        # Log config
        DumpAllToLog()
        # Connection

    def onStop(self):
        Domoticz.Debug("onStop called")

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called")

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(
            Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called")
        self.__runAgain -= 1
        if self.__runAgain <= 0:
            self.__runAgain = self.__HEARTBEATS2MIN * self.__MINUTES
            Domoticz.Debug("Get data from: " + self.__API_DOMAIN1)
            values = getData(self.__API_DOMAIN1, self.__API_HEADER)
            if values is not None:
                value = values.get("Bt")
                Domoticz.Debug("value: " + str(value))
                UpdateDevice(self.__UNIT_BT,
                             int(value),
                             str(value),
                             TimedOut=0)
                value = values.get("Bz")
                Domoticz.Debug("value: " + str(value))
                UpdateDevice(self.__UNIT_BZ,
                             int(value),
                             str(value),
                             TimedOut=0)
            #
            Domoticz.Debug("Get data from: " + self.__API_DOMAIN2)
            values = getData(self.__API_DOMAIN2, self.__API_HEADER)
            if values is not None:
                value = values.get("WindSpeed")
                Domoticz.Debug("value: " + str(value))
                UpdateDevice(self.__UNIT_WINDSPEED,
                             int(value),
                             str(value),
                             TimedOut=0)
            #
            Domoticz.Debug("Get data from: " + self.__API_DOMAIN3)
            values = getData(self.__API_DOMAIN3, self.__API_HEADER)
            if values is not None:
                value = values.get("Flux")
                Domoticz.Debug("value: " + str(value))
                UpdateDevice(self.__UNIT_FLUX,
                             int(value),
                             str(value),
                             TimedOut=0)
            Domoticz.Debug("Get data from: " + self.__API_DOMAIN4)
            values = getData(self.__API_DOMAIN4, self.__API_HEADER)
            if values is not None:
                value = values.get("0")
                Domoticz.Debug("value: " + str(value))
                scale = int(value.get("G").get("Scale"))
                Domoticz.Debug("scale " + str(scale))
                Domoticz.Debug("G: {} - {}".format(scale, self.__SCALES[scale]))
                UpdateDevice(self.__UNIT_G,
                             max(0, scale - 1),
                             self.__SCALES[scale],
                             TimedOut=0)
                scale = int(value.get("R").get("Scale"))
                UpdateDevice(self.__UNIT_R,
                             max(0, scale - 1),
                             self.__SCALES[scale],
                             TimedOut=0)
                scale = int(value.get("S").get("Scale"))
                UpdateDevice(self.__UNIT_S,
                             max(0, scale - 1),
                             self.__SCALES[scale],
                             TimedOut=0)
        else:
            Domoticz.Debug("onHeartbeat called, run again in " +
                           str(self.__runAgain) + " heartbeats.")


global _plugin
_plugin = BasePlugin()


def onCommand(Unit, Command, Level, Color):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Color)


def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)


def onDeviceAdded(Unit):
    global _plugin
    _plugin.onDeviceAdded(Unit)


def onDeviceModified(Unit):
    global _plugin
    _plugin.onDeviceModified(Unit)


def onDeviceRemoved(Unit):
    global _plugin
    _plugin.onDeviceRemoved(Unit)


def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)


def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()


def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)


def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status,
                           Priority, Sound, ImageFile)


def onStart():
    global _plugin
    _plugin.onStart()


def onStop():
    global _plugin
    _plugin.onStop()


################################################################################
# Get data
################################################################################
def getData(url, header):
    command = "curl -X GET "
    options = "'" + url + "' -H '" + header + "'"
    Domoticz.Debug(command + " " + options)
    p = subprocess.Popen(command + " " + options,
                         shell=True, stdout=subprocess.PIPE)
    p.wait()
    data, errors = p.communicate()
    if p.returncode != 0:
        Domoticz.Error("Request failed")
    values = json.loads(data.decode("utf-8", "ignore"))
    return values

################################################################################
# Generic helper functions
################################################################################


def DumpDevicesToLog():
    # Show devices
    Domoticz.Debug("Device count.........: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device...............: " +
                       str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device Idx...........: " + str(Devices[x].ID))
        Domoticz.Debug("Device Type..........: " +
                       str(Devices[x].Type) + " / " + str(Devices[x].SubType))
        Domoticz.Debug("Device Name..........: '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue........: " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue........: '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device Options.......: '" +
                       str(Devices[x].Options) + "'")
        Domoticz.Debug("Device Used..........: " + str(Devices[x].Used))
        Domoticz.Debug("Device ID............: '" +
                       str(Devices[x].DeviceID) + "'")
        Domoticz.Debug("Device LastLevel.....: " + str(Devices[x].LastLevel))
        Domoticz.Debug("Device Image.........: " + str(Devices[x].Image))


def DumpImagesToLog():
    # Show images
    Domoticz.Debug("Image count..........: " + str(len(Images)))
    for x in Images:
        Domoticz.Debug("Image '" + x + "...': '" + str(Images[x]) + "'")


def DumpParametersToLog():
    # Show parameters
    Domoticz.Debug("Parameters count.....: " + str(len(Parameters)))
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug("Parameter '" + x + "'...: '" +
                           str(Parameters[x]) + "'")


def DumpSettingsToLog():
    # Show settings
    Domoticz.Debug("Settings count.......: " + str(len(Settings)))
    for x in Settings:
        Domoticz.Debug("Setting '" + x + "'...: '" + str(Settings[x]) + "'")


def DumpAllToLog():
    DumpDevicesToLog()
    DumpImagesToLog()
    DumpParametersToLog()
    DumpSettingsToLog()


def DumpHTTPResponseToLog(httpDict):
    if isinstance(httpDict, dict):
        Domoticz.Debug("HTTP Details (" + str(len(httpDict)) + "):")
        for x in httpDict:
            if isinstance(httpDict[x], dict):
                Domoticz.Debug(
                    "....'" + x + " (" + str(len(httpDict[x])) + "):")
                for y in httpDict[x]:
                    Domoticz.Debug("........'" + y + "':'" +
                                   str(httpDict[x][y]) + "'")
            else:
                Domoticz.Debug("....'" + x + "':'" + str(httpDict[x]) + "'")


def UpdateDevice(Unit, nValue, sValue, TimedOut=0, AlwaysUpdate=False):
    if Unit in Devices:
        if Devices[Unit].nValue != nValue or Devices[Unit].sValue != sValue or Devices[
                Unit].TimedOut != TimedOut or AlwaysUpdate:
            Devices[Unit].Update(
                nValue=nValue, sValue=str(sValue), TimedOut=TimedOut)
            Domoticz.Debug(
                "Update " + Devices[Unit].Name + ": " + str(nValue) + " - '" + str(sValue) + "'")


def UpdateDeviceOptions(Unit, Options={}):
    if Unit in Devices:
        if Devices[Unit].Options != Options:
            Devices[Unit].Update(nValue=Devices[Unit].nValue,
                                 sValue=Devices[Unit].sValue, Options=Options)
            Domoticz.Debug("Device Options update: " +
                           Devices[Unit].Name + " = " + str(Options))


def UpdateDeviceImage(Unit, Image):
    if Unit in Devices and Image in Images:
        if Devices[Unit].Image != Images[Image].ID:
            Devices[Unit].Update(nValue=Devices[Unit].nValue,
                                 sValue=Devices[Unit].sValue, Image=Images[Image].ID)
            Domoticz.Debug("Device Image update: " +
                           Devices[Unit].Name + " = " + str(Images[Image].ID))
