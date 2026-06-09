#  Copyright (c) 2025 João Toppa <j213140@dac.unicamp.br>
 #  
 #   Redistribution and use in source and binary forms, with or without
 #   modification, are permitted provided that the following conditions
 #   are met:
 # 
 #   1. Redistributions of source code must retain the above Copyright
 #      notice, this list of conditions and the following disclaimer.
 #
 #   2. Redistributions in binary form must reproduce the above Copyright
 #      notice, this list of conditions and the following disclaimer in the
 #      documentation and/or other materials provided with the distribution.
 #
 #   3. Neither the name of the authors nor the names of its contributors
 #      may be used to endorse or promote products derived from this
 #      software without specific prior written permission.
 

# IMPORTS FOR PROBES

from RPi import GPIO
from board import SCL, SDA
import busio
import time
import adafruit_ccs811
import adafruit_bmp280
import adafruit_am2320
import configs
import sensors
import smbus
import board
import camera
import tables 

# IMPORTS FOR BEE DETECTION

import cv2
import numpy as np

# SETUP - PROBES

i2c1 = busio.I2C(SCL, SDA)
i2c0 = busio.I2C(board.D1, board.D0) 
bus = smbus.SMBus(0)
GPIO.setmode(GPIO.BCM)
try:
    ccs811_bus1 = adafruit_ccs811.CCS811(i2c1)
 
except Exception as e:
    ccs811_bus1 = None
    print(f"Warning: Failed to initialize CCS811: {e}")
 
am2320_bus1 = adafruit_am2320.AM2320(i2c1)

try:
    ccs811_bus0 = adafruit_ccs811.CCS811(i2c0)
except Exception as e:
    ccs811_bus0 = None
    print(f"Warning: Failed to initialize CCS811: {e}")

bmp280_bus0 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c0, 0x76)
mpu9250_bus0 = sensors.Accelerometer(configs.DEVICE_ADDRESS, configs.ACCEL_XOUT_H, configs.ACCEL_CONFIG, bus, configs.PWR_MGMT_1)
sensors.Accelerometer.initialize(mpu9250_bus0)
probe_bus0 = sensors.SensorProbe(ccs811=ccs811_bus0, mpu9250=mpu9250_bus0, climate_sensor=bmp280_bus0)
probe_bus1 = sensors.SensorProbe(ccs811=ccs811_bus1, mpu9250=None, climate_sensor=am2320_bus1)
last_update_time = time.time()
update_interval = 60


camera_feed_db = tables.SQLiteTables("camera_feed", 5)
station_db = tables.SQLiteTables("station_feed", 1)

camera_main = camera.Camera(camera_feed_db, probe_bus0, probe_bus1)

# MAIN LOOP

try:
    while True:
        current_time = time.time()
        if current_time - last_update_time >= update_interval:
            station_db.reading_and_writing_sensors([[0]], probe_bus0, probe_bus1, current_time)
            last_update_time = current_time

        camera_main.capture()

finally:
    GPIO.cleanup()
    cv2.destroyAllWindows()
