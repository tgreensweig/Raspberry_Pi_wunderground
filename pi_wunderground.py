#!/usr/bin/python

import subprocess
import re
import sys
import time
from datetime import datetime
import httplib

# ===========================================================
# Configuration options
# ===========================================================

# Sensor information, see Adafruit driver documentation
sensor_type = "2302"
sensor_gpio = "4"
# Time between posting readings to wunderground
delay = 600
# Wunderground personal weather station ID/password
stationid = "your_station_ID_here"
password = "your_password_here"


# Loop to continously upload data (with delay)
while(True):
  # Run the DHT program to get the humidity and temperature readings, note 
  sensor_output = subprocess.check_output(["./Adafruit_DHT", sensor_type, sensor_gpio]);

  # search for temperature in sensor output
  matches = re.search("Temp =\s+([0-9.]+)", sensor_output)
  if (not matches): #in case reading the sensor fails
	time.sleep(3)
	continue
  temp = float(matches.group(1)) * 1.8 + 32
  
  # search for humidity in sensor output
  matches = re.search("Hum =\s+([0-9.]+)", sensor_output)
  if (not matches):
	time.sleep(3)
	continue
  humidity = float(matches.group(1))

  # upload data to Wunderground
  try:
        conn = httplib.HTTPConnection("rtupdate.wunderground.com")
        path = "/weatherstation/updateweatherstation.php?ID=" + stationid + "&PASSWORD=" + password + "&dateutc=" + str(datetime.utcnow()) + "&tempf=" + str(temp) + "&humidity=" + str(humidity) + "&softwaretype=RaspberryPi&action=updateraw"
        conn.request("GET", path)
        res = conn.getresponse()

        # checks whether there was a successful connection (HTTP code 200 and content of page contains "success")
        if ((int(res.status) == 200) & ("success" in res.read())):
                print "%s - Successful Upload\nTemp: %.1f F, Humidity: %.1f %%\nNext upload in %i seconds\n" % (str(datetime.now()), temp, humidity, delay)
        else:
                print "%s -- Upload not successful, check username, password, and formating.. Will try again in %i seconds" % (str(datetime.now()), delay)
  except IOError as e: #in case of any kind of socket error
        print "{0} -- I/O error({1}): {2} will try again in {3} seconds".format(datetime.now(), e.errno, e.strerror, delay)

  # Wait before re-uploading data
  time.sleep(delay)
