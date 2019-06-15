# Solar data
This Domoticz plugin retrieves data from https://www.swpc.noaa.gov/ 

## Devices
| Name                   | Description
| :---                   | :---
| Bt                     | Interplanetary Magnetic Field 
| Bz                     | Interplanetary Magnetic Field (North)
| Solar Wind Speed       | Speed of the solar wind in km/s
| Flux                   |
| Kp-index               |
| Radio Blackouts        | https://www.swpc.noaa.gov/noaa-scales-explanation
| Solar Radiation Storms | https://www.swpc.noaa.gov/noaa-scales-explanation
| Geomagnetic Storms     | https://www.swpc.noaa.gov/noaa-scales-explanation

## Installation

* Go in your Domoticz directory using a command line and open the plugins directory.
* Run: ```git clone git clone https://github.com/Xorfor/Domoticz-Space-Weather-Plugin.git```
* Restart Domoticz.
* make sure "add new devices" is active
* Go to Hardware and add Space Weather
* New sensors found under Utility
